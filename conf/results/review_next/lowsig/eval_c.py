"""eval_c.py -- WORK_QUEUE 13 variant (C): the retrained V1 (same rung / seed / data / recipe, training sigma grid extended downward:
HSU / UMi28HSU) on the SAME development trials and points as run_screen2.sh (SELECTION_RULE.md), built exactly like V1
(runner.build_point(..., stagec_ckpt=<C checkpoint>) -> arm M-ours-dscore-C-V1, psd projection on, out-of-grid queries extrapolated).
Development only.
    cd ~/t2/conf && CUDA_VISIBLE_DEVICES= nice -n 10 taskset -c <cpu> python results/review_next/lowsig/eval_c.py <U28|D2> <qpsk|16qam> <skip0> <n> <snr>
Output: screenC_<cell>_<mod>_<skip0>_<n>_snr<snr>.{txt,npz} next to this file (refuses to overwrite)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, "code")
import numpy as np
import common as C
import runner as R
import diag_lowsig as DL

CKS = {"": {"U28": "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_sgUMi28HSU_best.pt",      # role best, as the registered UMi28 V1
            "D2": "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1_sgHSU.pt"},                       # role last, as the registered D2 V1
       # SELECTION_RULE.md addendum (Fable M1): C re-trained on the grids re-measured on DEVELOPMENT trials 2560..2623
       "d": {"U28": "/home/HTJ/t2/conf/ckpt/d2sx_UMi28_N160000_a1_sgUMi28HSUd_best.pt",
             "D2": "/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1_sgHSUd.pt"}}


def main(cell, mod, skip0, n, snr, cset=""):
    assert skip0 >= C.DEV_SKIP0, "development trials only"
    CK = CKS[cset]
    path = os.path.join(DL.OUT, f"screenC{cset}_{cell}_{mod}_{skip0}_{n}_snr{snr:g}")
    if os.path.exists(path + ".npz"):
        sys.exit(f"{path}.npz exists -- refusing")
    prior, tag, _ = DL.CELLS[cell]
    R._init(tag)
    p = R.build_point("D2", "C2", prior, snr, ntrain=160000, stagec_ckpt=CK[cell], mod=mod)
    rx = p["arms"][DL.V1]
    s_lo, s_hi = rx.prior.s_lo, rx.prior.s_hi
    rng = C.trial_rng("D2", prior, p["Nr"], p["T"], p["Tp"], snr)
    be, nm = [], []
    for tr in range(skip0 + n):
        H = p["gen"].sample(rng); u = rng.integers(0, 2, p["code"].K); perm = rng.permutation(p["code"].Ns)
        _, Y = rx.transmit(u, perm, H, rng)
        if tr < skip0:
            continue
        lg = rx.run(Y, H, u, perm, C.N_ITER); be.append(lg["blk_err"]); nm.append(lg["nmse"])
    be, nm = np.asarray(be, float), np.asarray(nm, float)
    f = lambda i: int((be[:, i] != 0).sum())
    txt = (f"# eval_c {cell} {mod}: checkpoint {CK[cell]} (grid [{s_lo:.4e}, {s_hi:.4e}]), development trials {skip0}..{skip0 + n - 1}\n"
           f"{snr:+3.0f} dB {mod:5s} V1-C      failures @1 {f(0):4d} @2 {f(1):4d} @4 {f(3):4d} @16 {f(15):4d} / {n}   "
           f"median NMSE @1 {np.nanmedian(nm[:, 0]):.2e} @16 {np.nanmedian(nm[:, 15]):.2e}   out-of-grid queries "
           f"{rx.prior.n_out_of_grid}/{rx.prior.n_query}\n")
    np.savez_compressed(path + ".npz", blk_err=be, nmse=nm, grid=np.array([s_lo, s_hi]))
    open(path + ".txt", "w").write(txt)
    print(txt, flush=True)


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0], a[1], int(a[2]), int(a[3]), float(a[4]), a[5] if len(a) > 5 else "")
