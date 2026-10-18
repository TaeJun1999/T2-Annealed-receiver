"""Verify probe wiring and trial-2560 packet against runner; never call any receiver's run()."""
import sys
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'conf/code'))
import numpy as np
import common as C
import arms as A
import runner as R
from sbl_probe import FIT, packet, runtime, date_now


def main():
    env = runtime()
    A.D2_FITS = str(FIT.parent)
    R.SPARSE = dict(rho_sbl=4, n_em=3, rho_omp=1, L=1)
    P = R.build_point('D2', 'C9', 'UMi28', 0, ntrain=160000)
    actual = P['arms']['SBL-loop']
    with np.load(FIT) as z:
        prior = A.SparsePrior(C.GaussianPrior(32, 4, z['Chat']), 32, 4, 4, 3)
    direct = A.route_a(32, 4, 16, 4, 1.0, prior, P['code'], P['Xp'], 'gmm_site')
    assert type(direct) is type(actual)
    assert type(direct.prior) is type(actual.prior) is A.SparsePrior
    for key in direct.cfg_dump:
        a, b = direct.cfg_dump[key], actual.cfg_dump[key]
        assert np.array_equal(a, b) if isinstance(a, np.ndarray) else a == b, key
    for key in ('A', 'C', 'Cinv', 'eh2_prior', 'cbar'):
        x, y = np.asarray(getattr(prior, key)), np.asarray(getattr(actual.prior, key))
        assert x.dtype == y.dtype and x.shape == y.shape and x.tobytes() == y.tobytes(), key
    # Literal runner.run_task generation loop and its actual R5-genie transmitter.
    rng = C.trial_rng('D2', 'UMi28', P['Nr'], P['T'], P['Tp'], 0)
    for tr in range(2561):
        A.CURRENT_TRIAL = tr
        H = P['gen'].sample(rng)
        u = rng.integers(0, 2, P['code'].K)
        perm = rng.permutation(P['code'].Ns)
        _, Y = P['arms']['R5-genie'].transmit(u, perm, H, rng)
    ref = (H, u, perm, Y)
    observed = packet(direct)
    hashes = {}
    for key, x, y in zip(('H', 'u', 'perm', 'Y'), ref, observed):
        assert x.dtype == y.dtype and x.shape == y.shape and x.tobytes() == y.tobytes(), key
        hashes[key] = hashlib.sha256(y.tobytes()).hexdigest()
    env = runtime()  # include libraries loaded lazily by the real channel generator
    env['torch_num_threads'] = sys.modules['torch'].get_num_threads()
    env['torch_cuda_initialized'] = sys.modules['torch'].cuda.is_initialized()
    assert env['torch_num_threads'] == 1 and not env['torch_cuda_initialized']
    doc = dict(date=date_now(), runtime=env, trial=2560, snr=0, receiver_wiring_identical=True,
               packet_byte_identical=True, packet_sha256=hashes,
               statement='No receiver.run call; no decoder outputs or BLER evaluated.')
    with Path(__file__).with_suffix('.json').open('x') as f:
        json.dump(doc, f, indent=2)
    print('PASS direct probe wiring == runner.build_point sparse SBL-loop', flush=True)
    print('PASS development trial 2560 H,u,perm,Y byte-identical to runner.run_task stream', flush=True)
    print(json.dumps(doc, indent=2), flush=True)


if __name__ == '__main__':
    main()
