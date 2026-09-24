"""(review_next P4-LO, user decision 2026-09-24 17:45 CDT 무렵 "P4-LO 오라클 참조") Latent-oracle REFERENCE receiver on D2.

Question: at the SAME receiver loop, would a prior that knows each block's propagation geometry get closer to R5-genie
than V1 does?  I.e. is the V1 -> genie gap prior-limited or loop-limited?  (DECISIONS: the prior-side intervention
experiment was missing.)  REPORT-ONLY.  The arm is a REFERENCE, never a bound: it knows more than any learnable prior.

Latent oracle (LO) prior of one block.  D2 (d2.D2Gen) draws per block L ~ Unif{3..8}, angles (theta_l, phi_l),
|alpha_l| = sqrt(p_l) FIXED and phases psi_l ~ Unif[0, 2pi).  Given (L, theta, phi) the channel vec(H) = V alpha with
V[:, l] = scale * kron(conj(a_t(phi_l)), a_r(theta_l)) (column-major vec, as H.reshape(-1, order="F")), and
E[alpha alpha^H | geometry] = diag(p), so the exact conditional second moment is C_z = V diag(p) V^H (rank L).
The LO prior is GaussianPrior(C_z + delta * (tr C_z / N) * I) -- second-moment exact given the geometry, NOT the
conditional law (fixed |alpha| makes it non-Gaussian), hence 'reference'.  delta (relative ridge; C_z is singular)
takes the values in --deltas.
Two wirings, each the route_a() call of an existing arm with only the prior object swapped:
  LO-G-d<delta>  = R2-ours-G's call  route_a(..., prior, code, Xp, "gaussian")        (exact Gaussian EP site)
  LO-S-d<delta>  = V1's call         route_a(..., prior, code, Xp, "score", clip="eta") (V1's score/matrix wiring)
LO-S vs V1 = prior quality at identical wiring; LO-G vs LO-S = the wiring at identical (oracle) prior.
In-script controls: R2-ours-G (Chat of --fits-tag full K=32, as build_baseline_arms) and R5-genie.  V1 and b* are NOT
re-run: they are read from the existing raw sets at the same trials (P3ref @16, P3 @32).

Trial stream: runner.run_task's, replayed exactly (gen.sample == gen._draw + gen._channels; then u, perm, transmit).
Acceptance (in `report`): R5-genie blk_err / nmse of the first 16 iterations must be bit-identical to the reference raw
set at every shared trial -- else the replay is broken and nothing is read.

  run:    python conf/code/diag_latent_oracle.py run --cell C2 --snr -3 --skip0 3200 --n 1280 [--chunk 20]
  report: python conf/code/diag_latent_oracle.py report
  smoke:  ... run --cell C2 --snr -3 --skip0 6400 --n 2 --chunk 2 --out raw_review_next_LOsmoke   (fresh trials)
CPU only (receiver rule), multiprocessing over chunks.  Writes raw_<out>/ and results/review_next/LO_report.txt.
"""
import argparse
import glob
import multiprocessing as mp
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                          # FIRST: sets OMP/OPENBLAS/MKL_NUM_THREADS=1 (runner.py:51)
import numpy as np
import arms as A
import runner

PRIOR = "S2"
DELTAS = (1e-3, 1e-2)
REF16, REF32 = "raw_review_next_P3ref", "raw_review_next_P3"      # V1 / b* / genie @16, V1 / b* @32 (same trials)
PAT = re.compile(r"D2_(C\d)_S2_Nr(\d+)_T(\d+)_Tp(\d+)_\w+?_snr(-?\d+)_skip(\d+)_n(\d+)\.npz")


def lo_names(deltas):
    return [f"LO-{w}-d{d:g}" for d in deltas for w in ("G", "S")]


def oracle_cov(gen, th, ph, al):
    """C_z = V diag(|alpha|^2) V^H for ONE block (th, ph, al of shape (L_MAX,), zero amplitude beyond L)."""
    ar = np.exp(1j * np.pi * np.sin(th)[:, None] * np.arange(gen.Nr)) / np.sqrt(gen.Nr)
    at = np.exp(1j * np.pi * np.sin(ph)[:, None] * np.arange(gen.Nt)) / np.sqrt(gen.Nt)
    V = gen.scale * (at.conj()[:, :, None] * ar[:, None, :]).reshape(len(th), -1).T    # col l = kron(conj(a_t), a_r)
    return (V * np.abs(al) ** 2) @ V.conj().T, V


def run_task(t):
    cell, snr, skip, n, iters, deltas, fits_tag, ntrain, out_dir, controls_only = t
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    pil, Xp = C.make_pilots("D2", PRIOR, Nt, Tp, Nr)
    out = os.path.join(out_dir, f"D2_{cell}_{PRIOR}_Nr{Nr}_T{T}_Tp{Tp}_{pil}_snr{snr:g}_skip{skip}_n{n}.npz")
    if os.path.exists(out):
        return f"exists  {os.path.basename(out)}"
    t0 = time.time()
    runner._init(fits_tag)                                         # A.D2_FITS -> results/gmm_fits_D2_<fits_tag>
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    gen = C.make_gen("D2", PRIOR, Nr, Nt)
    a = (Nr, Nt, T, Tp, sigma2)
    base, _, _, _ = A.build_baseline_arms("D2", PRIOR, *a, code, Xp, ntrain=ntrain)
    ctrl = {k: base[k] for k in ("R2-ours-G", "R5-genie")}
    names = list(ctrl) + ([] if controls_only else lo_names(deltas))
    logs = {k: [] for k in names}
    failed = {k: [] for k in names}
    Ls, vchk = [], 0.0
    rng = C.trial_rng("D2", PRIOR, Nr, T, Tp, snr)
    for tr in range(skip + n):
        th, ph, al, L = gen._draw(rng, 1)                          # == gen.sample(rng), keeping the latents
        H = gen._channels(th, ph, al)[0]
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        X, Y = ctrl["R5-genie"].transmit(u, perm, H, rng)
        if tr < skip:
            continue
        Ls.append(int(L[0]))
        rxs = dict(ctrl)
        if not controls_only:
            Cz, V = oracle_cov(gen, th[0], ph[0], al[0])
            h = H.reshape(-1, order="F")
            vchk = max(vchk, float(np.linalg.norm(V @ al[0] - h) / np.linalg.norm(h)))   # V reproduces the channel
            cb = np.trace(Cz).real / gen.N
            for d in deltas:
                pr = A.GaussianPrior(Nr, Nt, Cz + d * cb * np.eye(gen.N))
                rxs[f"LO-G-d{d:g}"] = A.route_a(*a, pr, code, Xp, "gaussian")
                rxs[f"LO-S-d{d:g}"] = A.route_a(*a, pr, code, Xp, "score", clip="eta")
        for k in names:
            try:
                logs[k].append(rxs[k].run(Y, H, u, perm, iters))
                failed[k].append(0.0)
            except Exception:                                      # classified, never dropped (01_RULES §4)
                logs[k].append({q: np.full(iters, np.nan) for q in C.KEYS_LOG})
                failed[k].append(1.0)
    if vchk > 1e-12:
        raise RuntimeError(f"oracle V does not reproduce the channel: rel err {vchk:.2e}")
    flat = {f"{k}|{q}": np.array([l[q] for l in L_]) for k, L_ in logs.items() for q in C.KEYS_RAW}
    flat.update({f"{k}|failed": np.array(v) for k, v in failed.items()})
    flat.update({"L": np.array(Ls), "meta|deltas": np.array(deltas), "meta|fits_tag": fits_tag,
                 "meta|ntrain": float(ntrain), "meta|V_relerr_max": vchk,
                 "meta|definition": "LO prior = GaussianPrior(C_z + delta*tr(C_z)/N*I), C_z = V diag(|alpha|^2) V^H",
                 "run|iters": iters, "run|skip": skip, "run|n": n, "run|snr": snr, "run|seed": C.SEED})
    os.makedirs(out_dir, exist_ok=True)
    tmp = out + ".tmp.npz"
    np.savez_compressed(tmp, **flat)
    os.replace(tmp, out)
    return f"done    {os.path.basename(out)}  ({time.time() - t0:.0f} s)"


def cmd_run(a):
    out_dir = os.path.join(C.CONF, a.out)
    tasks = [(a.cell, a.snr, s, min(a.chunk, a.skip0 + a.n - s), a.iters, tuple(a.deltas), a.fits_tag, a.ntrain, out_dir,
              a.controls_only) for s in range(a.skip0, a.skip0 + a.n, a.chunk)]
    jobs = min(a.jobs or os.cpu_count(), len(tasks))
    print(f"[LO] {a.cell} {a.snr:g} dB trials {a.skip0}..{a.skip0 + a.n - 1}: {len(tasks)} tasks on {jobs} workers, "
          f"iters {a.iters}, deltas {a.deltas}, controls_only {a.controls_only} -> {out_dir}", flush=True)
    t0 = time.time()
    with mp.get_context("fork").Pool(jobs) as pool:
        for i, msg in enumerate(pool.imap_unordered(run_task, tasks), 1):
            print(f"{i}/{len(tasks)} {msg}", flush=True)
    print(f"[LO] finished in {(time.time() - t0) / 60:.1f} min", flush=True)


# ----------------------------------------------------------------------------- report
def per_trial(rawdir, cell, snr, arms, it):
    """{arm: {trial: (blk_err@it, nmse@it)}} from every chunk of (cell, snr) in rawdir."""
    out = {k: {} for k in arms}
    for f in glob.glob(os.path.join(C.CONF, rawdir, f"D2_{cell}_*_snr{snr:g}_skip*_n*.npz")):
        m = PAT.search(os.path.basename(f))
        skip = int(m.group(6))
        d = np.load(f, allow_pickle=True)
        for k in arms:
            if f"{k}|blk_err" in d.files and d[f"{k}|blk_err"].shape[1] > it:
                be, nm = d[f"{k}|blk_err"][:, it], d[f"{k}|nmse"][:, it]
                for i in range(len(be)):
                    out[k][skip + i] = (1.0 if not np.isfinite(be[i]) else float(be[i]), float(nm[i]))
    return out


def genie_identity(lo_dir, cell, snr):
    """R5-genie blk_err and nmse, iterations 1..16, LO run vs REF16 at every shared trial: max abs difference."""
    worst, shared = 0.0, 0
    ref = {}
    for f in glob.glob(os.path.join(C.CONF, REF16, f"D2_{cell}_*_snr{snr:g}_skip*_n*.npz")):
        d = np.load(f, allow_pickle=True); s = int(PAT.search(os.path.basename(f)).group(6))
        for i in range(d["R5-genie|blk_err"].shape[0]):
            ref[s + i] = (d["R5-genie|blk_err"][i, :16], d["R5-genie|nmse"][i, :16])
    for f in glob.glob(os.path.join(C.CONF, lo_dir, f"D2_{cell}_*_snr{snr:g}_skip*_n*.npz")):
        d = np.load(f, allow_pickle=True); s = int(PAT.search(os.path.basename(f)).group(6))
        for i in range(d["R5-genie|blk_err"].shape[0]):
            if s + i in ref:
                shared += 1
                for x, y in zip((d["R5-genie|blk_err"][i, :16], d["R5-genie|nmse"][i, :16]), ref[s + i]):
                    diff = np.abs(np.nan_to_num(x, nan=1e300) - np.nan_to_num(y, nan=1e300))
                    worst = max(worst, float(np.max(diff)))
    return shared, worst


def cmd_report(a):
    from analysis import sign_p
    L = [C.header("D2", extra=["content     : review_next P4-LO latent-oracle REFERENCE receiver (report-only; a reference, "
                               "not a bound) -- " + os.path.basename(__file__)])]
    lo = lo_names(a.deltas)
    for cell, snr in ((c.split(":")[0], float(c.split(":")[1])) for c in a.points):
        shared, worst = genie_identity(a.out, cell, snr)
        ok = shared > 0 and worst == 0.0
        L += ["", f"== {cell} {snr:g} dB ==",
              f"   acceptance: R5-genie @1..16 vs {REF16} at {shared} shared trials, max |diff| {worst:.3g} -> "
              f"{'PASS (replay bit-identical)' if ok else 'FAIL -- nothing below is read'}"]
        if not ok:
            continue
        for it, ref in ((15, REF16), (31, REF32)):
            X = per_trial(a.out, cell, snr, lo + ["R2-ours-G", "R5-genie"], it)
            X.update(per_trial(ref, cell, snr, ["M-ours-bstar", "M-ours-dscore-C-V1"], it))
            if it == 31:
                X["R5-genie"] = per_trial(a.out, cell, snr, ["R5-genie"], 31)["R5-genie"]
            tr = sorted(set.intersection(*(set(v) for v in X.values() if v)))
            if not tr:
                L.append(f"   @{it + 1}: no shared trials"); continue
            be = {k: np.array([X[k][t][0] for t in tr]) for k in X if X[k]}
            nm = {k: np.array([X[k][t][1] for t in tr]) for k in X if X[k]}
            g, gn = be["M-ours-bstar"].sum(), be["R5-genie"].sum()
            L.append(f"   @{it + 1}  n={len(tr)} (trials {tr[0]}..{tr[-1]})   failures (BLER)   median NMSE   "
                     f"gap position (b* - X)/(b* - genie)")
            for k in ["M-ours-bstar", "M-ours-dscore-C-V1", "R2-ours-G"] + lo + ["R5-genie"]:
                if k in be:
                    L.append(f"     {k:<22} {int(be[k].sum()):>5} ({be[k].mean():.4f})   {np.nanmedian(nm[k]):.4e}   "
                             f"{(g - be[k].sum()) / (g - gn) if g != gn else float('nan'):+.3f}")
            L.append("     paired sign tests (a = first fails & second ok, b = reverse), house test p (n_d < 6 -> UNDECIDED):")
            for x, y in [("M-ours-dscore-C-V1", k) for k in lo] + [(k, "R5-genie") for k in lo] + \
                        [("M-ours-bstar", k) for k in lo] + [(f"LO-G-d{d:g}", f"LO-S-d{d:g}") for d in a.deltas]:
                if x in be and y in be:
                    p, q = int(np.sum((be[x] == 1) & (be[y] == 0))), int(np.sum((be[x] == 0) & (be[y] == 1)))
                    L.append(f"     {x:>20} -> {y:<16} {p:>4}:{q:<4} p={sign_p(p, q):.2g}"
                             + ("  UNDECIDED (n_d < 6)" if p + q < 6 else ""))
    txt = "\n".join(L) + "\n"
    out = os.path.join(C.CONF, "results", "review_next", a.report_name)
    open(out, "w").write(txt)
    print(txt, flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cell", required=True)
    r.add_argument("--snr", type=float, required=True)
    r.add_argument("--skip0", type=int, required=True)
    r.add_argument("--n", type=int, required=True)
    r.add_argument("--chunk", type=int, default=20)
    r.add_argument("--iters", type=int, default=32)
    r.add_argument("--deltas", type=float, nargs="+", default=list(DELTAS))
    r.add_argument("--fits-tag", default="B16e4k")
    r.add_argument("--ntrain", type=int, default=160000)
    r.add_argument("--out", default="raw_review_next_LO")
    r.add_argument("--jobs", type=int, default=None)
    r.add_argument("--controls-only", action="store_true", help="R2-ours-G and R5-genie only (replay check)")
    p = sub.add_parser("report")
    p.add_argument("--out", default="raw_review_next_LO")
    p.add_argument("--deltas", type=float, nargs="+", default=list(DELTAS))
    p.add_argument("--points", nargs="+", default=["C2:-3", "C2:6", "C5:-3"])
    p.add_argument("--report-name", default="LO_report.txt")
    a = ap.parse_args()
    return cmd_run(a) if a.cmd == "run" else cmd_report(a)


if __name__ == "__main__":
    sys.exit(main())
