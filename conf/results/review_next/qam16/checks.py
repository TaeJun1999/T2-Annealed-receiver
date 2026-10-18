"""E5 verification only: two authorized old QPSK chunks, or 16-QAM development blocks.

All outputs stay below this directory. BLER is not printed by the 16-QAM checks.
This is not an independent golden review or a locked measurement instrument.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, subprocess, sys
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'conf/code'))
import common as C
import numpy as np
import arms as A
import runner as R

def digest(p):
    with open(p, 'rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()
def save(name, data):
    with open(OUT / (name + '.json'), 'x') as f:
        json.dump(data, f, indent=2)
def source(tag):
    prior = 'S2' if tag == 'B16e4k' else 'UMi28'
    snr = '-3' if tag == 'B16e4k' else '12'
    path = next((ROOT / 'conf' / ('raw_' + tag)).glob(f'D2_C2_{prior}_*snr{snr}_skip0_n40.npz'))
    ref = np.load(path)
    ckpt = ROOT / 'conf/ckpt' / Path(str(ref['meta|stagec_ckpt'])).name
    return prior, path, ref, str(ckpt)
def route_raw(module, label):
    # Test harness isolates new chunks; production raw_file/tag rules are unchanged.
    directory = OUT / ('raw_' + label)
    directory.mkdir(exist_ok=True)
    module.d_raw = lambda: str(directory)
    return directory

def unit():
    from fractions import Fraction
    from t2_trellis import encode
    const, bits = C.qam_constellation(4)
    assert len(np.unique(const)) == 16
    h = bits[:, None, :] != bits[None, :, :]
    count = 0
    for axis in ('real', 'imag'):
        coordinate = getattr(const, axis)
        fixed = const.imag if axis == 'real' else const.real
        for level in np.unique(fixed):
            ix = np.flatnonzero(fixed == level)
            order = ix[np.argsort(coordinate[ix])]
            assert np.all(h[order[:-1], order[1:]].sum(1) == 1)
            count += len(order) - 1
    assert count == 24
    unscaled = np.rint(np.column_stack((const.real, const.imag)) * np.sqrt(10)).astype(int)
    exact_energy = sum((Fraction(int(x*x + y*y), 10) for x, y in unscaled), Fraction()) / 16
    assert exact_energy == 1
    floating = float(np.mean(np.abs(const)**2))
    assert abs(floating - 1) <= 2*np.finfo(float).eps
    index = bits @ (1 << np.arange(3, -1, -1))
    nearest = np.abs(const[index, None] - const).argmin(1)
    assert np.array_equal(bits[nearest], bits)
    code = C.QAMCode(C.GENS, C.NU, 4, 48)
    assert code.K == 90
    rng = np.random.default_rng(20261017)
    blocks = [np.zeros(90, int), np.ones(90, int), np.arange(90) % 2]
    blocks += [rng.integers(0, 2, 90) for _ in range(5)]
    for u in blocks:
        x = code.encode(u)
        # Independent convolutional encoding + integer label assembly verifies symbol mapping.
        coded = encode(u, code.st.nxt, code.st.out, C.NU).reshape(48, 4)
        assert np.array_equal(x, const[coded @ (1 << np.arange(3, -1, -1))])
        # No added noise. BCJR needs positive likelihood variance; exact zero is undefined.
        xb, v, lu = code.decode(x, np.full(48, 1e-6))
        assert np.array_equal((lu < 0).astype(int), u)
    for name, reason in A.QPSK_ONLY_ARMS.items():
        result = subprocess.run([sys.executable, '-B', str(ROOT/'conf/code/runner.py'),
                                 'run', '--mod', '16qam', '--arm', name, '--tag', 'E5_REFUSE'],
                                text=True, capture_output=True)
        assert result.returncode == 2 and reason in result.stderr
        assert not (ROOT/'conf/raw_E5_REFUSE').exists()
    # Direct callers must also be refused before attempting to open a checkpoint or a raw file.
    try:
        R.run_task(('D2', 'C2', 'S2', 9., 2560, 1, 160000, .7, 5, 16,
                    ['R3-bigamp'], None, '/missing.pt', False, False, None, False,
                    None, None, None, None, '16qam'))
    except ValueError as ex:
        assert 'BiG-AMP' in str(ex)
    else:
        raise AssertionError('direct run_task did not reject unsupported arm')
    result = dict(gray_axis_edges=count, exact_mean_energy=str(exact_energy),
                  float_mean_energy=floating, mapping_roundtrip=True, payload_bits=code.K,
                  noiseless_blocks=len(blocks), bcjr_likelihood_variance=1e-6,
                  rejected=list(A.QPSK_ONLY_ARMS), direct_task_rejection=True)
    save('unit', result)
    print('PASS unit:', result, flush=True)


def regression():
    spec = importlib.util.spec_from_file_location('e5_control_runner', OUT/'control_runner.py')
    old = importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
    result, all_pass = [], True
    for tag in ('B16e4k', 'U28B16e4'):
        prior, path, ref, ckpt = source(tag)
        old._init(tag)
        # HEAD runner before the patch: checks the current schema without extra test-set evaluation.
        control = old.build_point('D2', 'C2', prior, float(ref['run|snr']),
                                  ntrain=int(ref['meta|ntrain']), stagec_ckpt=ckpt)
        meta_control = {'meta|' + k for k in control['meta']}
        expected_arms = {k.split('|')[0] for k in ref.files if k.endswith('|' + C.KEYS_RAW[0])}
        assert set(control['arms']) == expected_arms
        del control
        historical = {k for k in ref.files if k.startswith('meta|')}
        for mode in ('omitted', 'explicit'):
            dest = route_raw(R, tag + '_' + mode)
            argv = ['run', '--testbed', 'D2', '--prior', prior, '--cell', 'C2',
                    '--snr', str(float(ref['run|snr'])), '--ntrain', str(int(ref['meta|ntrain'])),
                    '--stagec-ckpt', ckpt, '--tag', tag,
                    '--n', str(int(ref['run|n'])), '--chunk', str(int(ref['run|n'])),
                    '--skip0', str(int(ref['run|skip'])), '--beta', str(float(ref['run|beta'])),
                    '--tin', str(int(ref['run|t_in'])), '--iters', str(int(ref['run|iters'])),
                    '--seed', str(int(ref['run|seed']))]
            if mode == 'explicit': argv += ['--mod', 'qpsk']
            print('REGRESSION command:', sys.executable, '-B conf/code/runner.py', ' '.join(argv), flush=True)
            R.main(argv)
            got = np.load(next(dest.glob('*.npz')))
            actual_arms = {k.split('|')[0] for k in got.files if k.endswith('|' + C.KEYS_RAW[0])}
            bad = []
            for arm in sorted(expected_arms):
                for key in C.KEYS_RAW:
                    k = arm + '|' + key
                    x, y = ref[k], got[k]
                    if x.dtype != y.dtype or x.shape != y.shape or x.tobytes() != y.tobytes():
                        bad.append(dict(key=k, equal_nan=bool(np.array_equal(x,y,equal_nan=True)),
                                        max_abs=float(np.nanmax(np.abs(x-y)))))
            meta_actual = {k for k in got.files if k.startswith('meta|')}
            row = dict(tag=tag, mode=mode, reference=str(path), output=str(next(dest.glob('*.npz'))),
                       arms=len(expected_arms), keys_raw=len(C.KEYS_RAW),
                       arrays=len(expected_arms)*len(C.KEYS_RAW), mismatches=bad,
                       arm_set_equal=expected_arms == actual_arms,
                       meta_keys_equal_current_control=meta_actual == meta_control,
                       meta_added_since_historical=sorted(meta_actual-historical),
                       meta_missing_since_historical=sorted(historical-meta_actual), argv=argv)
            result.append(row)
            ok = not bad and expected_arms == actual_arms and meta_actual == meta_control
            all_pass &= ok
            print(('PASS' if ok else 'FAIL'), 'REGRESSION', tag, mode,
                  'arrays=', row['arrays'], 'mismatches=', len(bad),
                  'current schema unchanged=', row['meta_keys_equal_current_control'],
                  'historical added=', row['meta_added_since_historical'], flush=True)
        omitted = np.load(next((OUT/('raw_'+tag+'_omitted')).glob('*.npz')))
        explicit = np.load(next((OUT/('raw_'+tag+'_explicit')).glob('*.npz')))
        assert omitted.files == explicit.files
        assert all(omitted[k].tobytes() == explicit[k].tobytes() for k in omitted.files)
        print('PASS omitted vs explicit: every saved field bit-identical', tag, flush=True)
    save('regression', dict(passed=all_pass, comparisons=result))
    assert all_pass


def smoke():
    result = []
    for tag in ('U28B16e4', 'B16e4k'):
        prior, path, ref, ckpt = source(tag)
        manifest = json.loads((ROOT/'conf/results/review_next'/('run_manifest_'+tag+'.json')).read_text())
        sha = digest(ckpt)
        assert sha.startswith(manifest['stagec_checkpoint']['sha256_16'])
        R._init(tag)
        p = R.build_point('D2', 'C2', prior, 9., ntrain=160000, stagec_ckpt=ckpt,
                          pilot_arms=True, mod='16qam')
        supported = ['M-ours-dscore-C-V1','M-ours-bstar','R2-ours-G','R5-genie','V1-pilot']
        assert all(k in p['arms'] for k in supported)
        assert not set(A.QPSK_ONLY_ARMS) & p['arms'].keys()
        assert all(rx.code is p['code'] and rx.code.m == 4 for rx in p['arms'].values())
        assert p['code'].K == 90
        assert p['meta']['bstar'] == str(ref['meta|bstar'])
        assert p['meta']['kron_K'] == int(ref['meta|kron_K'])
        for k in ref.files:
            if k.startswith('meta|ll_val|'):
                assert p['meta'][k[5:]] == float(ref[k])
        seed = {}
        channels = {}
        for mod in ('qpsk', '16qam'):
            rng = C.trial_rng('D2',prior,8,16,4,9.)
            gen = C.make_gen('D2',prior,8,4)
            code = C.QAMCode(C.GENS,C.NU,C.MOD_BITS[mod],48)
            rx = A.route_a(8,4,16,4,10**(-.9),p['arms']['R2-ours-G'].prior,code,p['Xp'],'gaussian')
            channels[mod] = {}
            for tr in range(2564):
                H = gen.sample(rng)
                if tr in (0,1,2560,2561,2562,2563):
                    channels[mod][tr] = hashlib.sha256(H.tobytes()).hexdigest()
                u = rng.integers(0,2,code.K); perm = rng.permutation(48)
                _, Y = rx.transmit(u,perm,H,rng)  # skipped trials are generated, never decoded
                if mod == '16qam' and tr == 2560:
                    v1_trace = p['arms']['M-ours-dscore-C-V1'].run(Y,H,u,perm,C.N_ITER)
                    np.savez_compressed(OUT/('v1_trace_'+tag+'.npz'), **v1_trace)
        seed['channel_hashes'] = channels
        seed['same_channel_at_trial'] = {tr: channels['qpsk'][tr] == channels['16qam'][tr] for tr in channels['qpsk']}
        assert seed['same_channel_at_trial'][0]
        # Actual runner path and metadata, no patched receiver math.
        dest = route_raw(R, tag + '_16qam_dev')
        argv = ['run','--testbed','D2','--prior',prior,'--cell','C2','--snr','9',
                '--ntrain','160000','--stagec-ckpt',ckpt,'--pilot-arms','--mod','16qam',
                '--skip0','2560','--n','4','--chunk','4','--tag',tag,'--arm'] + supported
        print('SMOKE command:', sys.executable, '-B conf/code/runner.py', ' '.join(argv), flush=True)
        R.main(argv)
        raw = next(dest.glob('*.npz')); d = np.load(raw)
        assert str(d['meta|modulation']) == '16qam' and int(d['meta|payload_bits']) == 90
        assert str(d['meta|protocol']) == 'E5-qam16-v1'
        assert json.loads(str(d['meta|unsupported_arms'])) == A.QPSK_ONLY_ARMS
        for arm in supported:
            assert arm+'|failed' not in d.files
            for key in C.KEYS_RAW:
                assert d[arm+'|'+key].shape == (4,16)
            if arm == 'R5-genie':
                assert np.isnan(d[arm+'|nmse']).all()  # no channel estimator in genie mode, by design
            else:
                assert np.isfinite(d[arm+'|nmse']).all()
            for key in C.KEYS_RAW:
                if key != 'nmse':
                    assert np.isfinite(d[arm+'|'+key]).all()
        diag = OUT / ('coverage_'+tag+'.npz')
        subprocess.run([sys.executable,'-B',str(ROOT/'conf/code/diag_sigma_coverage.py'),
                        '--mod','16qam','--prior',prior,'--stagec-ckpt',ckpt,'--tag',tag,
                        '--cell','C2','--snr','9','--n','1','--skip0','2560','--out',str(diag)],check=True)
        dd = np.load(diag)
        assert dd['9|nu_q'].shape == (1,16)
        assert np.array_equal(dd['9|nu_q'][0],v1_trace['nu_q'])
        for key in C.KEYS_RAW:
            assert d['M-ours-dscore-C-V1|'+key][0].tobytes() == np.asarray(v1_trace[key]).tobytes()
        result.append(dict(tag=tag, prior=prior, output=str(raw), arms=supported, n=4, skip=2560,
                           snr=9, payload_bits=90, no_arm_exceptions=True, checkpoint_sha256=sha,
                           bstar=str(d['meta|bstar']), kron_K=int(d['meta|kron_K']),
                           frozen_ll_vals_matched=True, seed=seed, argv=argv,
                           diagnostic_matches_v1_query=True))
        print('PASS 16qam dev smoke',tag,'4 blocks x 5 arms x 16 iterations; coverage matches V1',flush=True)
    save('smoke',result)

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('check',choices=['unit','regression','smoke'])
    globals()[ap.parse_args().check]()
