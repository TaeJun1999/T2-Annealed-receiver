"""E3' regression. Only raw() evaluates test packets: the single authorized old chunk, twice (cold CLI controls).

Run from this worktree under CUDA_VISIBLE_DEVICES=, taskset -c 0-1, BLAS=1.
No writes to main, no baseline result selection, no new test points.
"""
import os
import sys
from pathlib import Path
import json
import re
import subprocess
import argparse

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "conf/code"))
import numpy as np
import common as C
import arms as A
import runner as R
from sbl_probe import blas_pools

HERE = Path(__file__).resolve().parent
REFERENCE = ROOT / "conf/raw_SPU28/D2_C2_UMi28_Nr8_T16_Tp4_eig_snr-3_skip0_n40.npz"


def bits(x, y, label):
    x, y = np.asarray(x), np.asarray(y)
    assert x.shape == y.shape and x.dtype == y.dtype and x.tobytes() == y.tobytes(), label


def unit():
    # Frozen pre-change implementation from this worktree's base commit, in memory only.
    old_src = subprocess.check_output(["git", "-C", str(ROOT), "show", "HEAD:conf/code/arms.py"], text=True)
    legacy = {"__name__": "legacy_arms"}
    exec(compile(old_src, "HEAD:conf/code/arms.py", "exec"), legacy)
    rng = np.random.default_rng(20261018)
    Nr, Nt, N, ne, k = 4, 2, 8, 3, 4
    Z = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
    base = C.GaussianPrior(Nr, Nt, np.eye(N) + Z @ Z.conj().T / N)
    H = rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))
    G = H @ H.conj().T / N
    b = rng.standard_normal(N) + 1j * rng.standard_normal(N)
    checks = 0
    for update in ("mackay", "em"):
        for rho in (1, 2, 4):
            kw = dict(update=update)
            p = A.SparsePrior(base, Nr, Nt, rho, ne, warm=True, **kw)
            ref = p.gamma_path(G, b, [ne * i for i in range(1, k + 1)])
            A.CURRENT_TRIAL = 2560
            for i in range(1, k + 1):
                site = p.ep_site(G, b, C.LAM_MIN)
                bits(p._gamma_last, ref[ne * i], "warm continuation gamma_path")
                for x, y in zip(site, p.site_from_gamma(ref[ne * i], N)):
                    bits(x, y, "warm continuation site")
                checks += 1
            A.CURRENT_TRIAL = 2561
            cold = A.SparsePrior(base, Nr, Nt, rho, ne, **kw)
            for x, y in zip(p.ep_site(G, b, C.LAM_MIN), cold.ep_site(G, b, C.LAM_MIN)):
                bits(x, y, "new-trial reset site")
            checks += 1
            old = legacy["SparsePrior"](base, Nr, Nt, rho, ne, **kw)
            for GG, bb in ((G, b), (G/3, -b), (np.zeros_like(G), b*0), (G, b)):
                for x, y in zip(cold.ep_site(GG, bb, C.LAM_MIN), old.ep_site(GG, bb, C.LAM_MIN)):
                    bits(x, y, "off vs HEAD site, arbitrary call order")
                bits(cold.gamma(GG, bb), old.gamma(GG, bb), "off vs HEAD gamma")
                checks += 1
            A.CURRENT_TRIAL = 2562
            bits(cold.gamma(G, b), old.gamma(G, b), "off after trial change")
            assert cold._gamma_last is None
            # Unset CURRENT_TRIAL must never accidentally continue a different packet.
            A.CURRENT_TRIAL = None
            for _ in range(2):
                for x, y in zip(p.ep_site(G, b, C.LAM_MIN), cold.ep_site(G, b, C.LAM_MIN)):
                    bits(x, y, "unset trial remains flat")
            checks += 3
    print(f"PASS warm gamma_path / trial reset / cold HEAD byte comparison / unset trial: {checks} cases", flush=True)
    oldfits, old_sparse = A.D2_FITS, R.SPARSE
    try:
        A.D2_FITS = str(ROOT / "conf/results/gmm_fits_D2_SPU28")
        for spec in ("8,3,16,3", "8,3,16,3,0", "8,3,16,3,1"):
            R.SPARSE = R.parse_sparse_arms(spec)
            P = R.build_point("D2", "C2", "UMi28", -3, ntrain=160000)
            expected = dict(L=3, n_em=3, rho_omp=16, rho_sbl=8)
            if spec.endswith(",1"):
                expected["warm"] = True
            assert P['meta']['sparse'] == json.dumps(expected, sort_keys=True)
            loop, pilot = (P['arms'][name].prior for name in ('SBL-loop', 'SBL-pilot'))
            assert loop is not pilot and loop.warm == pilot.warm == expected.get('warm', False)
            if loop.warm:
                A.CURRENT_TRIAL = 2560
                loop.ep_site(G=np.eye(32), b=np.ones(32, complex), lam_min=C.LAM_MIN)
                assert pilot._gamma_last is None, "loop/pilot gamma state shared"
            print(f"PASS runner build + meta|sparse + separate prior objects: {spec}", flush=True)
        # The sparse-file resolution/serialization path must be unchanged too.
        pick = ROOT / 'conf/results/sparse/pick_UMi28_C2.json'
        R.SPARSE = json.loads(pick.read_text())
        assert json.dumps(R._sparse_at(-3), sort_keys=True) == str(np.load(REFERENCE)['meta|sparse'])
        print("PASS unchanged --sparse-file resolver / cold metadata", flush=True)
        for bad in ('1,2,3', '1,2,3,4,2', '1,2,3,4,-1', '1,2,3,4,0,0'):
            try:
                R.parse_sparse_arms(bad)
            except ValueError:
                continue
            raise AssertionError(f"accepted invalid WARM/arity: {bad}")
        print("PASS invalid WARM/arity rejection", flush=True)
    finally:
        A.D2_FITS, R.SPARSE = oldfits, old_sparse
        A.CURRENT_TRIAL = None


def raw():
    with np.load(REFERENCE) as z:
        sparse = json.loads(str(z['meta|sparse']))
        meta = {k: str(z[k]) for k in z.files if k.startswith(('meta|', 'run|'))}
        match = re.fullmatch(r'(D2)_(C2)_(UMi28)_Nr8_T16_Tp4_eig_snr-3_skip0_n40.npz', REFERENCE.name)
        assert match and int(z['run|seed']) == C.SEED
        assert 'meta|stagec_ckpt_id' not in z.files and str(z['meta|stagec_status']).startswith('not requested')
        manifest = dict(reference=str(REFERENCE), meta=meta, commands=[], comparisons=[])
        for suffix, fifth in (('4', []), ('5OFF', [0])):
            tag = 'SBL32REG' + suffix
            spec = ','.join(map(str, [sparse['rho_sbl'], sparse['n_em'], sparse['rho_omp'], sparse['L']] + fifth))
            cmd = [sys.executable, str(ROOT / 'conf/code/runner.py'), 'run', '--testbed', match[1], '--cell', match[2],
                   '--prior', match[3], '--snr', str(float(z['run|snr'])), '--skip0', str(int(z['run|skip'])),
                   '--n', str(int(z['run|n'])), '--chunk', str(int(z['run|n'])), '--ntrain', str(int(float(z['meta|ntrain']))),
                   '--beta', str(float(z['run|beta'])), '--tin', str(int(z['run|t_in'])), '--iters', str(int(z['run|iters'])),
                   '--sparse-arms', spec, '--arm', 'SBL-loop', '--tag', tag]
            result = ROOT / ('conf/raw_' + tag) / REFERENCE.name
            if result.exists():
                raise FileExistsError(f"refusing to reuse old regression output: {result}")
            print('COMMAND ' + ' '.join(cmd), flush=True)
            with (HERE / f'runner_{tag}.out').open('x') as out, (HERE / f'runner_{tag}.err').open('x') as err:
                subprocess.run(cmd, cwd=ROOT, stdout=out, stderr=err, check=True)
            manifest['commands'].append(cmd)
            with np.load(result) as new:
                assert str(new['meta|sparse']) == str(z['meta|sparse'])
                for q in C.KEYS_RAW:
                    key = 'SBL-loop|' + q
                    assert np.isfinite(new[key]).all(), key
                    bits(new[key], z[key], f'{spec}: {key}')
                    manifest['comparisons'].append(dict(spec=spec, key=key, shape=list(new[key].shape), byte_identical=True))
                    print(f'PASS {spec} {key}: shape={new[key].shape}, dtype={new[key].dtype}, byte-identical', flush=True)
                assert 'SBL-loop|failed' not in new.files or not new['SBL-loop|failed'].any()
                print(f'PASS {spec} meta|sparse byte-identical; SBL-loop exceptions absent', flush=True)
        with (HERE / 'raw_regression.json').open('x') as f:
            json.dump(manifest, f, indent=2)


def existing():
    import tests as T
    for f in (T.test_C2, T.test_C3, T.test_C4, T.test_C5, T.test_M1, T.test_M1b, T.test_M2, T.test_M2b, T.test_M4):
        verdict = f()
        row = T.RES[-1]
        print('EXISTING ' + repr(row), flush=True)
        assert verdict == 'PASS', f.__name__


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--section', choices=('unit', 'raw', 'existing', 'all'), default='all')
    a = ap.parse_args()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
    assert set(os.sched_getaffinity(0)) <= {0, 1}
    pools = blas_pools()
    assert all(p['num_threads'] == 1 for p in pools)
    print('START ' + subprocess.check_output(['date', '+%Y-%m-%d %H:%M:%S %Z'],
          env=dict(os.environ, TZ='America/Chicago'), text=True).strip(), flush=True)
    print(f'HEAD={C.git_commit()} + uncommitted implementation; CUDA empty; affinity={sorted(os.sched_getaffinity(0))}; BLAS=1', flush=True)
    print('BLAS ' + json.dumps(pools), flush=True)
    for name, fn in (('unit', unit), ('raw', raw), ('existing', existing)):
        if a.section in (name, 'all'):
            fn()
    print('REGRESSION PASS', flush=True)


if __name__ == '__main__':
    main()
