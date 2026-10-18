"""E5 fix1 checks. QPSK uses saved arrays only; receiver calls are dev-only.

Run sequentially with run_checks.sh. Each output is created exclusively and retained.
The harness redirects raw output and instruments calls, without changing receiver math.
"""
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import importlib.util
import io
import json
import os
import shlex
import subprocess
import sys

ROOT = Path('/home/HTJ/t2_wtE5')
OUT = Path(__file__).resolve().parent
QAM = OUT.parent
sys.path.insert(0, str(ROOT / 'conf/code'))
import runner as R
import common as C
import numpy as np
import torch

torch.set_num_threads(1)
torch.set_num_interop_threads(1)
assert set(os.sched_getaffinity(0)) <= {64, 65}
assert os.environ['CUDA_VISIBLE_DEVICES'] == ''
assert torch.get_num_threads() == torch.get_num_interop_threads() == 1

ARMS = ['M-ours-dscore-C-V1', 'M-ours-bstar', 'R2-ours-G', 'R5-genie', 'V1-pilot']
SPECS = {
    'B16e4k': ('S2', 'd2sx_N160000_a1.pt'),
    'U28B16e4': ('UMi28', 'd2sx_UMi28_N160000_a1_best.pt'),
}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(name, data):
    with (OUT / f'{name}.json').open('x') as stream:
        json.dump(data, stream, indent=2)


def save_npz(path, arrays):
    assert path.resolve().is_relative_to(OUT)
    with path.open('xb') as stream:
        np.savez_compressed(stream, **arrays)


def load_control(path):
    spec = importlib.util.spec_from_file_location('control_' + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def task(cell='C2'):
    return ('D2', cell, 'S2', 9., 2560, 4, 160000, .7, 5, 16,
            ['R5-genie'], None, None, False, False, None, False, None, None, None, None)


def resume(module, path, args):
    before = sha(path)
    with patch.object(module, 'raw_file', return_value=str(path)), \
            patch.object(module, 'build_point', side_effect=AssertionError('resume built receivers')) as build:
        try:
            message = module.run_task(args)
            rejected = False
        except ValueError as exc:
            message, rejected = str(exc), True
    assert build.call_count == 0 and sha(path) == before
    return {'rejected': rejected, 'message': message, 'raw_sha256': before,
            'raw_preserved': True, 'build_point_calls': build.call_count}


def smoke_args(arm, mod='16qam'):
    return SimpleNamespace(testbed='D2', prior='S2', cell=['C2'], snr=[9.], ntrain=160000,
                           beta=.7, tin=5, ckpt=None,
                           stagec_ckpt=str(ROOT / 'conf/ckpt' / SPECS['B16e4k'][1]),
                           mean_arms=False, p3_arms=False, pilot_arms=False, ald_file=None,
                           mod=mod, skip0=2560, iters=16, arm=arm)


def smoke_rejection(module, point, args):
    output = io.StringIO()
    with ExitStack() as stack:
        calls = [stack.enter_context(patch.object(rx, 'run', side_effect=AssertionError('unexpected run')))
                 for rx in point['arms'].values()]
        stack.enter_context(patch.object(module, 'build_point', return_value=point))
        rng = stack.enter_context(patch.object(C, 'trial_rng', wraps=C.trial_rng))
        with redirect_stdout(output):
            rc = module.cmd_smoke(args)
    result = {'returncode': rc, 'receiver_run_calls': sum(call.call_count for call in calls),
              'trial_rng_calls': rng.call_count, 'stdout': output.getvalue()}
    print(result['stdout'], end='', flush=True)
    return result


def defects():
    old = load_control(OUT / 'runner_before.py')
    raw = next((QAM / 'raw_B16e4k_16qam_dev').glob('*.npz'))
    rows = []
    for mode, args in [('omitted_21_fields', task()), ('explicit_qpsk_22_fields', task() + ('qpsk',))]:
        before, after = resume(old, raw, args), resume(R, raw, args)
        assert not before['rejected'] and before['message'].startswith('exists')
        assert after['rejected'] and 'modulation' in after['message'] and "saved='16qam'" in after['message']
        rows.append({'case': mode, 'before': before, 'after': after})
        print('PASS defect1', mode, after['message'], flush=True)

    fixtures = OUT / 'resume_fixtures'
    fixtures.mkdir(exist_ok=True)
    qpsk = {'meta|modulation': 'qpsk', 'meta|payload_bits': 42, 'meta|protocol': ''}
    qam = {'meta|modulation': '16qam', 'meta|payload_bits': 90, 'meta|protocol': 'E5-qam16-v1'}
    cases = [('legacy_qpsk_C2', {}, 'C2', 'qpsk', False),
             ('legacy_qpsk_C7', {}, 'C7', 'qpsk', False),
             ('explicit_qpsk', qpsk, 'C2', 'qpsk', False),
             ('matching_16qam', qam, 'C2', '16qam', False),
             ('legacy_to_16qam', {}, 'C2', '16qam', True),
             ('qpsk_to_16qam', qpsk, 'C2', '16qam', True),
             ('bad_qpsk_payload', {**qpsk, 'meta|payload_bits': 90}, 'C2', 'qpsk', True),
             ('bad_qpsk_protocol', {**qpsk, 'meta|protocol': 'E5-qam16-v1'}, 'C2', 'qpsk', True),
             ('bad_16qam_payload', {**qam, 'meta|payload_bits': 42}, 'C2', '16qam', True),
             ('bad_16qam_protocol', {**qam, 'meta|protocol': 'other'}, 'C2', '16qam', True),
             ('missing_16qam_payload', {k: v for k, v in qam.items() if k != 'meta|payload_bits'}, 'C2', '16qam', True),
             ('missing_16qam_protocol', {k: v for k, v in qam.items() if k != 'meta|protocol'}, 'C2', '16qam', True)]
    matrix = []
    for name, meta, cell, mod, rejected in cases:
        path = fixtures / f'{name}.npz'
        save_npz(path, meta)
        result = resume(R, path, task(cell) + (mod,))
        assert result['rejected'] == rejected, (name, result)
        matrix.append({'case': name, **result})
    print('PASS resume metadata matrix:', len(matrix), 'cases; all files preserved', flush=True)

    R._init('B16e4k')
    args = smoke_args(['V1-pilot'])
    point = R.build_point('D2', 'C2', 'S2', 9., ntrain=160000, stagec_ckpt=args.stagec_ckpt, mod='16qam')
    assert 'V1-pilot' not in point['arms']
    before = smoke_rejection(old, point, args)
    after = smoke_rejection(R, point, args)
    assert before['returncode'] == 0 and before['receiver_run_calls'] == 0
    assert after['returncode'] == 1 and after['receiver_run_calls'] == after['trial_rng_calls'] == 0
    assert 'V1-pilot' in after['stdout'] and 'not built' in after['stdout'] and 'no arms executed' in after['stdout']
    partial = smoke_rejection(R, point, smoke_args(['R5-genie', 'V1-pilot']))
    assert partial['returncode'] == 1 and partial['receiver_run_calls'] == partial['trial_rng_calls'] == 0
    empty = smoke_rejection(R, {**point, 'arms': {}}, smoke_args(None))
    assert empty['returncode'] == 1 and empty['receiver_run_calls'] == empty['trial_rng_calls'] == 0
    assert 'no arms executed' in empty['stdout']
    save('defects', {'resume_review_reproductions': rows, 'resume_matrix': matrix,
                     'missing_pilot_before': before, 'missing_pilot_after': after,
                     'partially_missing_after': partial, 'empty_arms_after': empty})
    print('PASS defect2: missing/partly missing/empty arms fail; receiver_run_calls=0', flush=True)


def compare_arrays(left, right, keys):
    return [k for k in keys if left[k].dtype != right[k].dtype or left[k].shape != right[k].shape
            or left[k].tobytes() != right[k].tobytes()]


def regression():
    old = load_control(OUT / 'runner_before.py')
    legacy = load_control(QAM / 'control_runner.py')
    prior_rows = json.loads((QAM / 'regression.json').read_text())['comparisons']
    schema, rows = {}, []
    for tag, (prior, ckpt_name) in SPECS.items():
        snr = -3. if tag == 'B16e4k' else 12.
        built = []
        for module in (legacy, old, R):
            module._init(tag)
            # Construct metadata only: no channel stream or receiver evaluation.
            with patch.object(C, 'trial_rng', side_effect=AssertionError('test stream requested')):
                point = module.build_point('D2', 'C2', prior, snr, ntrain=160000,
                                           stagec_ckpt=str(ROOT / 'conf/ckpt' / ckpt_name))
            built.append((sorted('meta|' + k for k in point['meta']), sorted(point['arms'])))
        assert built[0] == built[1] == built[2]
        schema[tag] = built[2]

    for row in prior_rows:
        reference, output = Path(row['reference']), Path(row['output'])
        before = {str(p): sha(p) for p in (reference, output)}
        transcript = io.StringIO()
        # If a test chunk is absent, fail before construction or sampling. Never re-evaluate test trials.
        with patch.object(R, 'd_raw', return_value=str(output.parent)), \
                patch.object(R, 'build_point', side_effect=AssertionError('test receiver rebuild forbidden')) as build, \
                patch.object(C, 'trial_rng', side_effect=AssertionError('test stream evaluation forbidden')) as rng, \
                redirect_stdout(transcript):
            rc = R.main(row['argv'])
        assert rc == 0 and '1/1 exists' in transcript.getvalue()
        assert build.call_count == rng.call_count == 0
        print('COMMAND:', shlex.join([sys.executable, '-B', 'conf/code/runner.py', *row['argv']]), flush=True)
        print(transcript.getvalue(), end='', flush=True)
        with np.load(reference) as ref, np.load(output) as got:
            arms = sorted({k.split('|')[0] for k in ref.files if k.endswith('|' + C.KEYS_RAW[0])})
            keys = [arm + '|' + key for arm in arms for key in C.KEYS_RAW]
            mismatches = compare_arrays(ref, got, keys)
            assert not mismatches
            assert schema[row['tag']][0] == sorted(k for k in got.files if k.startswith('meta|'))
            assert schema[row['tag']][1] == arms
            assert 'meta|modulation' not in got.files and 'meta|modulation' not in ref.files
        # Historical QPSK raw itself must also skip for both tuple layouts.
        args = ('D2', 'C2', SPECS[row['tag']][0], -3. if row['tag'] == 'B16e4k' else 12.,
                0, 40, 160000, .7, 5, 16, None, None, None, False, False, None, False, None, None, None, None)
        original_resume = resume(R, reference, args + (('qpsk',) if row['mode'] == 'explicit' else ()))
        assert not original_resume['rejected'] and original_resume['message'].startswith('exists')
        assert before == {str(p): sha(p) for p in (reference, output)}
        rows.append({'tag': row['tag'], 'mode': row['mode'], 'argv': row['argv'],
                     'reference': str(reference), 'output': str(output), 'sha256': before,
                     'arrays': len(keys), 'mismatches': mismatches, 'meta_keys': schema[row['tag']][0],
                     'schema_equal_pre_fix_and_legacy': True, 'resume_stdout': transcript.getvalue(),
                     'original_resume': original_resume, 'build_point_calls_on_resume': build.call_count,
                     'trial_rng_calls_on_resume': rng.call_count, 'raw_preserved': True})
        print('PASS QPSK', row['tag'], row['mode'], f'arrays={len(keys)} mismatches=0',
              f'meta_keys={len(schema[row["tag"]][0])} unchanged; resume=exists; evaluations=0', flush=True)
    for tag in SPECS:
        paths = [Path(row['output']) for row in prior_rows if row['tag'] == tag]
        with np.load(paths[0]) as omitted, np.load(paths[1]) as explicit:
            assert omitted.files == explicit.files
            assert not compare_arrays(omitted, explicit, omitted.files)
    save('regression', {'comparisons': rows, 'total_arrays': sum(row['arrays'] for row in rows),
                        'test_receiver_evaluations': 0, 'omitted_explicit_all_fields_equal': True})
    print('PASS QPSK saved-array comparison: 392 arrays, mismatches=0; no test receiver evaluation', flush=True)


def smoke(tag):
    prior, ckpt_name = SPECS[tag]
    ckpt = ROOT / 'conf/ckpt' / ckpt_name
    reference = next((QAM / f'raw_{tag}_16qam_dev').glob('*.npz'))
    reference_sha = sha(reference)
    original_build = R.build_point
    records, metas, counts = {}, [], {}
    commands = []

    def instrument(*args, **kwargs):
        point = original_build(*args, **kwargs)
        assert set(ARMS) <= point['arms'].keys() and point['code'].K == 90
        metas.append(point['meta'])
        trial = [-1]
        transmitter = point['arms']['R5-genie']
        original_transmit = transmitter.transmit

        def transmit(*a, **kw):
            trial[0] += 1
            return original_transmit(*a, **kw)

        transmitter.transmit = transmit
        for name, rx in point['arms'].items():
            original_run = rx.run

            def run(*a, _name=name, _run=original_run, **kw):
                assert _name in ARMS and 2560 <= trial[0] <= 2563, (_name, trial[0])
                key = (_name, trial[0])
                assert key not in records, key
                counts[_name] = counts.get(_name, 0) + 1
                result = _run(*a, **kw)
                records[key] = {k: np.asarray(result[k]).copy() for k in C.KEYS_RAW}
                return result

            rx.run = run
        return point

    raw_dir = OUT / f'raw_route_{tag}'
    raw_dir.mkdir(exist_ok=True)
    # cmd_smoke is fixed at n=2; these two calls cover exactly dev 2560..2563, once per arm.
    for skip in (2560, 2562):
        argv = ['smoke', '--testbed', 'D2', '--prior', prior, '--cell', 'C2', '--snr', '9',
                '--ntrain', '160000', '--stagec-ckpt', str(ckpt), '--pilot-arms', '--mod', '16qam',
                '--skip0', str(skip), '--iters', '16', '--tag', tag, '--arm', *ARMS]
        commands.append(argv)
        print('COMMAND:', shlex.join([sys.executable, '-B', 'conf/code/runner.py', *argv]), flush=True)
        with patch.object(R, 'build_point', side_effect=instrument), \
                patch.object(R, 'd_raw', return_value=str(raw_dir)):
            assert R.main(argv) == 0
    assert counts == {arm: 4 for arm in ARMS}, counts
    arrays = {f'{arm}|{key}': np.array([records[arm, tr][key] for tr in range(2560, 2564)])
              for arm in ARMS for key in C.KEYS_RAW}
    with np.load(reference) as ref:
        mismatches = compare_arrays(ref, arrays, arrays)
        assert not mismatches, mismatches
        assert set(metas[0]) == set(metas[1]) == {k[5:] for k in ref.files if k.startswith('meta|')}
    for arm in ARMS:
        for key in C.KEYS_RAW:
            value = arrays[arm + '|' + key]
            assert value.shape == (4, 16)
            if arm == 'R5-genie' and key == 'nmse':
                assert np.isnan(value).all()  # Genie does not estimate H: intentional existing convention.
            else:
                assert np.isfinite(value).all()
    arrays.update({f'meta|{k}': np.array(v) for k, v in metas[0].items()})
    arrays.update({'check|trial_ids': np.arange(2560, 2564), 'check|seed': C.SEED,
                   'check|source': 'instrumented cmd_smoke return values; not run_task raw',
                   'check|runner_sha256': sha(ROOT / 'conf/code/runner.py')})
    output = OUT / f'smoke_{tag}.npz'
    save_npz(output, arrays)
    assert sha(reference) == reference_sha

    # Full CLI parser/dispatch: missing --pilot-arms must return nonzero without receiver work.
    missing = [v for v in commands[0][:commands[0].index('--arm')] if v != '--pilot-arms'] + ['--arm', 'V1-pilot']
    with patch.object(R, 'd_raw', return_value=str(raw_dir)), \
            patch.object(C, 'trial_rng', side_effect=AssertionError('missing arm must fail before sampling')) as rng:
        rc = R.main(missing)
    assert rc == 1 and rng.call_count == 0
    save(f'smoke_{tag}', {'tag': tag, 'prior': prior, 'argv': commands, 'seed': C.SEED,
                          'trials': list(range(2560, 2564)), 'receiver_run_calls': counts,
                          'arrays': len(ARMS) * len(C.KEYS_RAW), 'mismatches': mismatches,
                          'reference': str(reference), 'reference_sha256': reference_sha,
                          'output': str(output), 'output_sha256': sha(output),
                          'checkpoint_sha256': sha(ckpt), 'meta_keys_unchanged': True,
                          'missing_pilot_argv': missing, 'missing_pilot_returncode': rc,
                          'missing_pilot_trial_rng_calls': rng.call_count})
    print('PASS 16qam', tag, 'dev=2560..2563 arms=5 iterations=16 arrays=35 bit-identical;',
          'missing --pilot-arms exit=1', flush=True)


if __name__ == '__main__':
    mode = sys.argv[1]
    print('ENV', json.dumps({'pid': os.getpid(), 'affinity': sorted(os.sched_getaffinity(0)),
                            'torch_threads': torch.get_num_threads(),
                            'torch_interop_threads': torch.get_num_interop_threads(),
                            'CUDA_VISIBLE_DEVICES': os.environ['CUDA_VISIBLE_DEVICES'],
                            'seed': C.SEED, 'mode': mode}), flush=True)
    if mode == 'defects':
        defects()
    elif mode == 'regression':
        regression()
    elif mode in SPECS:
        smoke(mode)
    else:
        raise ValueError(mode)
