"""fit_gpu.py -- run the D2 GMM re-fit for ONE (Nr, fam, K) configuration on ONE GPU, with exactly the
protocol of runner.cmd_fit: same kappa grid, same restarts, same iteration cap, same validation-based
early stopping, same selection rule (validation log-likelihood ONLY), same fields in the same
arms.fit_path() file.  The EM itself is code/gmm_em_gpu.py (float64 port of the READ-ONLY
Demo/t2_gmm.py :: fit_gmm_em).

  CUDA_VISIBLE_DEVICES=k python code/fit_gpu.py <Nr> <fam> <K> <ntrain> <tag>

<tag> is runner's --tag and is REQUIRED, not optional: it routes the OUTPUT DIRECTORY.  runner._init
sets arms.D2_FITS = d_fits_d2() = results/gmm_fits_D2_<tag>/; without it arms.D2_FITS keeps its
import-time default results/gmm_fits_D2/, which is the directory of the ORIGINAL n=1e4 fits (and the
target of the results/gmm_fits_D2_B1e4 symlink).  A fit written there is invisible to the tagged
pipeline and visible to an untagged reader -- i.e. it silently mixes fitting codes.  That is the bug
this argument exists to prevent; the assert below is the guard.

Never overwrites an existing fit file (the CPU run owns those).  Writes atomically.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
import arms as A
from runner import _sets, ref_task, FAM, KAPPAS, N_VAL, RESTARTS, FIT_ITERS, d_fits_d2, _init
from gmm_em_gpu import fit_gmm_em_gpu

# NEXT_EXPERIMENTS_B32e4 speed-up (opt-in, user decision 2026-09-24): FIT_SPARSE_TOL=<tol> in the environment turns on
# gmm_em_gpu's sparse kron M-step for THIS process; unset = the exact path (every earlier fit).  The value used and the
# largest dropped responsibility mass are written into every candidate / final file (sparse_tol, sparse_max_dropped).
SPARSE_TOL = float(os.environ["FIT_SPARSE_TOL"]) if os.environ.get("FIT_SPARSE_TOL") else None
# FIT_KRON_BATCHED=1 (opt-in, 2026-09-24): gmm_em_gpu's batched exact kron M-step (scatter matrices); recorded as kron_batched.
KRON_BATCHED = os.environ.get("FIT_KRON_BATCHED") == "1"


def _fit_one(X, Xv, Xt, prior, Nr, Nt, fam, K, kap, r):
    """ONE (kappa, restart) EM run -- exactly runner.cmd_fit's per-task unit, same seed tuple."""
    rng = np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID[prior], Nr, FAM[fam], K, kap, r])
    t = time.time()
    f = fit_gmm_em_gpu(X, K, rng, n_iter=FIT_ITERS, kappa=float(kap), struct=fam,
                       dims=(Nr, Nt), Xval=Xv, sparse_tol=SPARSE_TOL, batched=KRON_BATCHED)
    f["kron_batched"] = float(KRON_BATCHED)
    f["ll_test"] = float(C.GMMPriorB(Nr, Nt, f["covs"], f["pi"]).log_pdf(Xt).mean())
    f["ll_train"] = float(f["ll"][f["it_best"]])
    f["sec"] = time.time() - t
    print(f"  ('{prior}', {Nr}, {Nt}, '{fam}', {K}, {kap}, {r}): iters {f['n_iter']} "
          f"best@{f['it_best']} reseeds {f['n_reseed']} ll_train {f['ll_train']:.3f} "
          f"ll_val {f['ll_val']:.3f} ({f['sec']:.0f} s)"
          + (f"  sparse_tol {SPARSE_TOL:g} max dropped mass {f['sparse_max_dropped']:.2e}" if SPARSE_TOL else "")
          + ("  kron_batched" if KRON_BATCHED else ""),
          flush=True)
    return f


def _write_final(out, rs, ref, ntrain, t0, prior, Nr, fam, K):
    """Select by validation log-likelihood ONLY and write the arms.fit_path() file (same fields as
    runner.cmd_fit).  Shared by the all-in-one path and the --merge path."""
    kb = max(rs, key=lambda k: rs[k]["ll_val"])
    f, cand = rs[kb], sorted(rs)
    tmp = out + f".tmp{os.getpid()}.npz"
    np.savez_compressed(tmp, pi=f["pi"], covs=f["covs"], Chat=f["Chat"], ll=f["ll"],
                        kappa=kb[0], restart=kb[1], it_best=f["it_best"], n_iter=f["n_iter"],
                        n_reseed=f["n_reseed"], ll_train=f["ll_train"], ll_val=f["ll_val"],
                        ll_test=f["ll_test"], gauss_val=ref["gauss_val"], gauss_test=ref["gauss_test"],
                        sec=sum(rs[c]["sec"] for c in cand), sec_best=f["sec"],
                        cand=np.array(cand), cand_ll_val=np.array([rs[c]["ll_val"] for c in cand]),
                        cand_ll_test=np.array([rs[c]["ll_test"] for c in cand]),
                        ntrain=ntrain, n_val=N_VAL,
                        sparse_tol=np.array([float(rs[c].get("sparse_tol", np.nan)) for c in cand]),
                        sparse_max_dropped=np.array([float(rs[c].get("sparse_max_dropped", np.nan)) for c in cand]),
                        kron_batched=np.array([float(rs[c].get("kron_batched", 0.0)) for c in cand]))
    if os.path.exists(out):                              # CPU won the race while we were fitting
        os.remove(tmp); print(f"[gpu-fit] {out} appeared meanwhile -- kept the CPU file", flush=True)
        return 0
    os.replace(tmp, out)
    print(f"[gpu-fit] {prior} Nr={Nr} {fam:<4} K={K:<3}: kappa {kb[0]:>3} restart {kb[1]} "
          f"best@{f['it_best']:<3} train-val gap {f['ll_train'] - f['ll_val']:6.3f}  "
          f"ll_test - ll_test(Gaussian) = {f['ll_test'] - ref['gauss_test']:6.3f} nat  "
          f"pi_min {f['pi'].min():.4f}  ({(time.time() - t0) / 60:.1f} min GPU over {len(cand)} EM runs) "
          f"-> {out}", flush=True)
    return 0


def _cand_path(out, kap, r):
    return out[:-4] + f".k{kap}r{r}.npz"


def main(Nr, fam, K, ntrain, tag, restart=None, merge=False):
    """restart=None, merge=False : the original all-in-one path (every kappa x every restart, then select).
    restart=r                   : run ONLY restart r (for every kappa) and save a per-restart CANDIDATE
                                  file beside the target -- the original protocol treats each (kappa, r)
                                  as an independent pool task with its own seed, so restarts may be
                                  spread over GPUs without changing a single RNG draw (2026-09-22 15:15).
    merge=True                  : combine the candidate files (all of them must exist) into the final
                                  file with exactly the fields and selection rule of the all-in-one path."""
    _init(tag)                                           # routes arms.D2_FITS, exactly as cmd_fit does
    prior, Nt = C.PRIOR_OF["D2"], C.NT
    out = A.fit_path("D2", prior, Nr, fam, K, ntrain)
    assert os.path.dirname(out) == d_fits_d2(), (out, d_fits_d2())
    print(f"[gpu-fit] tag={tag!r}  out={out}" + (f"  restart={restart}" if restart is not None else "")
          + ("  MERGE" if merge else ""), flush=True)
    if os.path.exists(out):
        print(f"[gpu-fit] {out} exists -- CPU run owns it, skipping", flush=True)
        return 0
    os.makedirs(d_fits_d2(), exist_ok=True)
    kaps = KAPPAS if fam == "full" else (0,)
    t0 = time.time()
    if merge:
        gen, (X, Xv, Xt) = _sets(prior, Nr, Nt, ntrain)
        ref = ref_task((prior, Nr, Nt, ntrain))[1]
        rs = {}
        for kap in kaps:
            for r in range(RESTARTS):
                cp = _cand_path(out, kap, r)
                if not os.path.exists(cp):
                    sys.exit(f"[gpu-fit] MERGE refused: candidate missing {cp}")
                d = np.load(cp)
                rs[(kap, r)] = {k: (d[k] if d[k].shape else d[k].item()) for k in d.files}
        return _write_final(out, rs, ref, ntrain, t0, prior, Nr, fam, K)
    gen, (X, Xv, Xt) = _sets(prior, Nr, Nt, ntrain)
    ref = ref_task((prior, Nr, Nt, ntrain))[1]
    if restart is not None:
        for kap in kaps:
            f = _fit_one(X, Xv, Xt, prior, Nr, Nt, fam, K, kap, restart)
            cp = _cand_path(out, kap, restart)
            np.savez_compressed(cp + ".tmp.npz", pi=f["pi"], covs=f["covs"], Chat=f["Chat"], ll=f["ll"],
                                it_best=f["it_best"], n_iter=f["n_iter"], n_reseed=f["n_reseed"],
                                ll_train=f["ll_train"], ll_val=f["ll_val"], ll_test=f["ll_test"],
                                sec=f["sec"], sparse_tol=f["sparse_tol"], sparse_max_dropped=f["sparse_max_dropped"],
                                kron_batched=f["kron_batched"])
            os.replace(cp + ".tmp.npz", cp)
            print(f"[gpu-fit] candidate (kappa {kap}, restart {restart}) -> {cp}  ll_val {f['ll_val']:.3f}",
                  flush=True)
        return 0
    rs = {}
    for kap in kaps:
        for r in range(RESTARTS):
            rs[(kap, r)] = _fit_one(X, Xv, Xt, prior, Nr, Nt, fam, K, kap, r)
    return _write_final(out, rs, ref, ntrain, t0, prior, Nr, fam, K)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 5 or len(a) > 7:
        sys.exit("usage: CUDA_VISIBLE_DEVICES=k fit_gpu.py <Nr> <fam> <K> <ntrain> <tag> [--restart r | --merge]"
                 "   (tag routes the output dir -- see the module docstring)")
    restart, merge = None, False
    if len(a) == 7 and a[5] == "--restart":
        restart = int(a[6])
    elif len(a) == 6 and a[5] == "--merge":
        merge = True
    elif len(a) != 5:
        sys.exit("bad trailing arguments: expected '--restart r' or '--merge'")
    sys.exit(main(int(a[0]), a[1], int(a[2]), int(a[3]), a[4], restart=restart, merge=merge))
