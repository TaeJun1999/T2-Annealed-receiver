"""conf/code/diag_prior_swap.py -- receiver runs with swapped Module H priors for the K1 / K2 follow-ups of P4-LO (user
decision 2026-09-25 00:2x CDT).  New file only; the production runner / arms / score code is untouched.

Arms (the name is the raw key; every one is an existing route_a() call with only the prior object chosen here):
  M-ours-dscore-C-V1   V1 exactly as production: runner.score_prior(..., psd_project=True, ntrain) -> route_a(.., "score", clip="eta")
  V1-clamp / V1-edge   prior_variants.ScorePriorOOG(oog="clamp"/"edge") in the same wiring; identical to V1 on in-grid queries
  BR-S                 prior_variants.BayesGPrior (Bayes-G reference) in V1's wiring
  M-ours-bstar         b* .view("eta"), gmm_site                      (arms.build_our_arms)
  M-ours-bstar-scalar  b* raw, "score", clip="eta", hsite="scalar"    (arms.build_our_arms, bstar_scalar)
  gmmB-scorew-eta      b* raw in V1's exact wiring                    (arms.build_our_arms, mean_arms)
  R5-genie, R2-ours-G  arms.build_baseline_arms
Trial stream: runner.run_task's, replayed exactly.  Raw per point in <out>/ with runner's key format (KEYS_RAW, failed,
guardH) plus per-trial query counters (<arm>|n_oog, BR-S|mc_disagree).

  run:    python conf/code/diag_prior_swap.py run --cell C1 --snr -3 --skip0 S --n N --arms V1-edge M-ours-bstar ... --out raw_X
  check:  python conf/code/diag_prior_swap.py check --out raw_X --ref raw_review_next_A2 --cell C2 --snr -3
          (every arm present in both: all KEYS_RAW fields bit-identical at every shared trial -- construction identity)
  report: python conf/code/diag_prior_swap.py report --out raw_X --cell C1 --snr -3 --skip0 S --n N --chunk 10 --pairs ...
          (fail-closed acceptance first: exact chunk set, run meta, one arm set, one edge_kw/bg_kw/ckpt per point)
  check-cavity: ... --out raw_X --cell C1 --snr -3   (blk_err@16 vs the p1_cavity <arm>|fail record at shared trials)
CPU only (receiver rule).
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
PAT = re.compile(r"D2_(C\d)_S2_Nr(\d+)_T(\d+)_Tp(\d+)_\w+?_snr(-?\d+)_skip(\d+)_n(\d+)\.npz")
ALL_ARMS = ("M-ours-dscore-C-V1", "V1-clamp", "V1-edge", "BR-S", "M-ours-bstar", "M-ours-bstar-scalar", "gmmB-scorew-eta",
            "R5-genie", "R2-ours-G")


def build(cell, snr, arms_wanted, fits_tag, ntrain, ckpt, edge_kw, bg_kw):
    import prior_variants as PV
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    runner._init(fits_tag)
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    pil, Xp = C.make_pilots("D2", PRIOR, Nt, Tp, Nr)
    gen = C.make_gen("D2", PRIOR, Nr, Nt)
    a = (Nr, Nt, T, Tp, sigma2)
    base, _, _, fits = A.build_baseline_arms("D2", PRIOR, *a, code, Xp, ntrain=ntrain)
    Chat = fits[("full", 32)]["Chat"]
    hp, _, _, bstar, kron_K = A.module_h_priors("D2", PRIOR, Nr, Nt, ntrain)
    out = {}
    for k in arms_wanted:
        if k in ("R5-genie", "R2-ours-G"):
            out[k] = base[k]
        elif k == "M-ours-dscore-C-V1":
            sp, why = runner.score_prior("D2", PRIOR, Nr, Nt, ckpt, psd_project=True, ntrain=ntrain)
            assert sp is not None, why
            out[k] = A.route_a(*a, sp, code, Xp, "score", clip="eta")
        elif k in ("V1-clamp", "V1-edge"):
            sp = PV.ScorePriorOOG(ckpt, Nr, Nt, Chat, oog=k.split("-")[1], device="cpu",
                                  **(edge_kw if k == "V1-edge" else {}))
            out[k] = A.route_a(*a, sp, code, Xp, "score", clip="eta")
        elif k == "BR-S":
            out[k] = A.route_a(*a, PV.BayesGPrior(Nr, Nt, Chat, **bg_kw), code, Xp, "score", clip="eta")
        elif k == "M-ours-bstar":
            out[k] = A.route_a(*a, hp[bstar].view("eta"), code, Xp, "gmm_site")
        elif k == "M-ours-bstar-scalar":
            out[k] = A.route_a(*a, hp[bstar], code, Xp, "score", clip="eta", hsite="scalar")
        elif k == "gmmB-scorew-eta":
            out[k] = A.route_a(*a, hp[bstar], code, Xp, "score", clip="eta")
            assert not out[k].exact_prior
        else:
            raise SystemExit(f"unknown arm {k}")
    return out, base["R5-genie"], code, gen, pil, dict(bstar=bstar, kron_K=kron_K)


def run_task(t):
    cell, snr, skip, n, iters, arms_wanted, fits_tag, ntrain, ckpt, edge_kw, bg_kw, out_dir = t
    c = C.CELLS[cell]
    Nr, T, Tp = c["Nr"], c["T"], c["Tp"]
    t0 = time.time()
    rxs, first, code, gen, pil, meta = build(cell, snr, arms_wanted, fits_tag, ntrain, ckpt, edge_kw, bg_kw)
    out = os.path.join(out_dir, f"D2_{cell}_{PRIOR}_Nr{Nr}_T{T}_Tp{Tp}_{pil}_snr{snr:g}_skip{skip}_n{n}.npz")
    if os.path.exists(out):
        return f"exists  {os.path.basename(out)}"
    logs = {k: [] for k in rxs}; failed = {k: [] for k in rxs}; cnt = {k: [] for k in rxs}; mcd = []
    rng = C.trial_rng("D2", PRIOR, Nr, T, Tp, snr)
    for tr in range(skip + n):
        H = gen.sample(rng)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        if tr < skip:
            continue
        for k, rx in rxs.items():
            n0 = getattr(rx.prior, "n_oog", 0); m0 = len(getattr(rx.prior, "mc_disagree", []))
            if hasattr(rx, "reset_stats"):
                rx.reset_stats()
            try:
                logs[k].append(rx.run(Y, H, u, perm, iters)); failed[k].append(0.0)
            except Exception:                                      # classified, never dropped (01_RULES §4)
                logs[k].append({q: np.full(iters, np.nan) for q in C.KEYS_LOG}); failed[k].append(1.0)
            cnt[k].append(getattr(rx.prior, "n_oog", 0) - n0)
            if k == "BR-S":
                d = rx.prior.mc_disagree[m0:]
                mcd.append(float(np.median(d)) if d else np.nan)
    import bigamp
    flat = {f"{k}|{q}": np.array([l[q] for l in L_]) for k, L_ in logs.items() for q in C.KEYS_RAW + ("nu_q",)}
    flat.update({f"{k}|failed": np.array(v) for k, v in failed.items()})
    for k in rxs:
        nm = flat[f"{k}|nmse"]
        if k == "R5-genie":
            flat[f"{k}|guardH"] = np.full(len(nm), np.nan); continue
        with np.errstate(invalid="ignore"):
            flat[f"{k}|guardH"] = (~np.isfinite(nm) | (nm > bigamp.DIVERGE_NMSE)).any(axis=1).astype(float)
        if k in ("V1-clamp", "V1-edge"):
            flat[f"{k}|n_oog"] = np.array(cnt[k], float)
    if mcd:
        flat["BR-S|mc_disagree"] = np.array(mcd)
    import score as S
    import prior_variants as PV
    ekw = dict(M=16, burn=100, keep=100, n_jac=16, eps_frac=0.05); ekw.update(edge_kw)          # class defaults + CLI
    bkw = dict(chains=4, burn=25, keep=75, n_th=96, n_ph=48); bkw.update(bg_kw)
    flat.update({"meta|bstar": meta["bstar"], "meta|kron_K": float(meta["kron_K"] if meta["kron_K"] is not None else -1),
                 "meta|fits_tag": fits_tag, "meta|ntrain": float(ntrain), "meta|ckpt": ckpt,
                 "meta|ckpt_sha": S.ckpt_identity(ckpt)["sha256_16"], "meta|arms": " ".join(rxs),
                 "meta|edge_kw": repr(sorted(ekw.items())), "meta|bg_kw": repr(sorted(bkw.items())),
                 "run|iters": iters, "run|skip": skip, "run|n": n, "run|snr": snr, "run|seed": C.SEED})
    os.makedirs(out_dir, exist_ok=True)
    tmp = out + ".tmp.npz"
    np.savez_compressed(tmp, **flat); os.replace(tmp, out)
    return f"done    {os.path.basename(out)}  ({time.time() - t0:.0f} s)"


def cmd_run(a):
    out_dir = os.path.join(C.CONF, a.out)
    old = glob.glob(os.path.join(out_dir, f"D2_{a.cell}_*_snr{a.snr:g}_skip*_n*.npz"))
    if old and not a.resume:
        sys.exit(f"[swap] {len(old)} raw file(s) for {a.cell} {a.snr:g} dB already in {out_dir} -- run once into an empty "
                 f"--out, or --resume to finish an interrupted run of the SAME arguments")
    edge_kw = dict(M=a.edge_M, burn=a.edge_burn, keep=a.edge_keep, n_jac=a.edge_njac)
    bg_kw = dict(chains=a.bg_chains)
    tasks = [(a.cell, a.snr, s, min(a.chunk, a.skip0 + a.n - s), a.iters, tuple(a.arms), a.fits_tag, a.ntrain, a.ckpt,
              edge_kw, bg_kw, out_dir) for s in range(a.skip0, a.skip0 + a.n, a.chunk)]
    jobs = min(a.jobs or os.cpu_count(), len(tasks))
    print(f"[swap] {a.cell} {a.snr:g} dB trials {a.skip0}..{a.skip0 + a.n - 1}: {len(tasks)} tasks on {jobs} workers, "
          f"arms {a.arms}, iters {a.iters}, edge {edge_kw}, bayes-g {bg_kw}, ckpt {a.ckpt}, fits {a.fits_tag} -> {out_dir}", flush=True)
    t0 = time.time()
    with mp.get_context("fork").Pool(jobs) as pool:
        for i, msg in enumerate(pool.imap_unordered(run_task, tasks), 1):
            print(f"{i}/{len(tasks)} {msg}", flush=True)
    print(f"[swap] finished in {(time.time() - t0) / 60:.1f} min", flush=True)


def load(rawdir, cell, snr):
    """{trial: {arm|field: row}} for one point."""
    rows = {}
    for f in glob.glob(os.path.join(C.CONF, rawdir, f"D2_{cell}_*_snr{snr:g}_skip*_n*.npz")):
        s = int(PAT.search(os.path.basename(f)).group(6))
        d = np.load(f, allow_pickle=True)
        keys = [k for k in d.files if "|" in k and not k.startswith(("meta|", "run|"))]
        n = int(d["run|n"])
        for i in range(n):
            rows.setdefault(s + i, {}).update({k: d[k][i] for k in keys})
    return rows


def cmd_check(a):
    X, R = load(a.out, a.cell, a.snr), load(a.ref, a.cell, a.snr)
    shared = sorted(set(X) & set(R))
    arms = sorted({k.split("|")[0] for t in shared for k in X[t]} & {k.split("|")[0] for t in shared for k in R[t]})
    worst = {}
    for t in shared:
        for k in X[t]:
            if k in R[t] and k.split("|")[1] in C.KEYS_RAW:
                x, y = np.asarray(X[t][k], float), np.asarray(R[t][k], float)[: len(np.asarray(X[t][k]))]
                d = np.abs(np.nan_to_num(x, nan=1e300) - np.nan_to_num(y, nan=1e300))
                worst[k.split("|")[0]] = max(worst.get(k.split("|")[0], 0.0), float(d.max()))
    ok = bool(shared) and all(v == 0.0 for v in worst.values())
    print(f"[check] {a.out} vs {a.ref} {a.cell} {a.snr:g} dB: shared trials {len(shared)}, arms {arms}, "
          f"max |diff| per arm {worst} -> {'PASS (bit-identical)' if ok else 'FAIL'}")
    return 0 if ok else 1


def accept(out, cell, snr, skip0, n, chunk, iters=16, fits_tag="B16e4k", ntrain=160000, ckpt_sha=None):
    """Registered acceptance of one point (fail-closed): the raw chunk set is EXACTLY {(skip0 + chunk*k, chunk)}, every chunk
    carries run|iters / meta|fits_tag / meta|ntrain (/ meta|ckpt_sha) as registered, the SAME arm set and the SAME
    edge_kw / bg_kw, and every registered trial is present exactly once.  -> (ok, problems, meta_summary)"""
    want = {(s, min(chunk, skip0 + n - s)) for s in range(skip0, skip0 + n, chunk)}
    have, prob, arms_seen, kws = {}, [], set(), set()
    for f in glob.glob(os.path.join(C.CONF, out, f"D2_{cell}_*_snr{snr:g}_skip*_n*.npz")):
        m = PAT.search(os.path.basename(f)); have[(int(m.group(6)), int(m.group(7)))] = f
    if set(have) != want:
        prob.append(f"chunk set differs from the registered {len(want)}: extra/missing {sorted(set(have) ^ want)}")
    for (s, k), f in sorted(have.items()):
        d = np.load(f, allow_pickle=True)
        g = lambda key: str(d[key].item() if d[key].shape == () else d[key])
        if int(d["run|iters"]) != iters or g("meta|fits_tag") != fits_tag or int(float(g("meta|ntrain"))) != ntrain:
            prob.append(f"{os.path.basename(f)}: iters/fits/ntrain {int(d['run|iters'])}/{g('meta|fits_tag')}/{g('meta|ntrain')}")
        if ckpt_sha and g("meta|ckpt_sha") != ckpt_sha:
            prob.append(f"{os.path.basename(f)}: ckpt sha {g('meta|ckpt_sha')} != {ckpt_sha}")
        arms_seen.add(g("meta|arms")); kws.add((g("meta|edge_kw"), g("meta|bg_kw"), g("meta|ckpt_sha"), g("meta|bstar"), g("meta|kron_K")))
        if int(d["run|n"]) != k:
            prob.append(f"{os.path.basename(f)}: run|n {int(d['run|n'])} != {k}")
    if len(arms_seen) > 1:
        prob.append(f"arm set differs between chunks: {arms_seen}")
    if len(kws) > 1:
        prob.append(f"edge_kw/bg_kw/ckpt/bstar differ between chunks: {kws}")
    return (not prob), prob, (sorted(arms_seen), sorted(kws))


def cmd_report(a):
    from analysis import sign_p
    ok, prob, ms = accept(a.out, a.cell, a.snr, a.skip0, a.n, a.chunk, a.iters, a.fits_tag, a.ntrain, a.ckpt_sha)
    head = (f"== {a.out} {a.cell} {a.snr:g} dB, registered trials {a.skip0}..{a.skip0 + a.n - 1} (chunk {a.chunk}) ==\n"
            f"   acceptance: {'PASS' if ok else 'FAIL -- nothing below is read: ' + '; '.join(prob)}\n"
            f"   arms {ms[0]}  meta(edge_kw, bg_kw, ckpt_sha, bstar, kron_K) {ms[1]}")
    if not ok:
        print(head)
        if a.save:
            open(os.path.join(C.CONF, "results", "review_next", a.save), "a").write(head + "\n")
        return 1
    X = load(a.out, a.cell, a.snr)
    trials = sorted(X)
    arms = sorted({k.split("|")[0] for t in trials for k in X[t]})
    it = a.it - 1
    be = {k: np.array([1.0 if not np.isfinite(X[t][f"{k}|blk_err"][it]) else float(X[t][f"{k}|blk_err"][it]) for t in trials])
          for k in arms if all(f"{k}|blk_err" in X[t] for t in trials)}
    L = [head, f"   @{a.it}, n={len(trials)}"]
    g = be.get("M-ours-bstar"); r = be.get("R5-genie")
    for k, v in be.items():
        extra = ""
        if f"{k}|n_oog" in X[trials[0]]:
            extra += f"  out-of-grid queries/block {np.mean([X[t][f'{k}|n_oog'] for t in trials]):.2f}"
        gd = [X[t].get(f"{k}|guardH", np.nan) for t in trials]
        extra += f"  F3 guard {np.nansum(gd):.0f}  exceptions {int(sum(X[t].get(f'{k}|failed', 0.0) for t in trials))}"
        if f"{k}|nu_q" in X[trials[0]]:                             # above-grid queries per iteration (nu_q > nu_hi)
            oog = np.array([np.asarray(X[t][f"{k}|nu_q"], float) > 1.4285757304853552 for t in trials])
            extra += f"  above-grid it1 {oog[:, 0].mean():.2f} it2-16 {oog[:, 1:].mean():.3f}"
        pos = f"  gap position {(g.sum() - v.sum()) / (g.sum() - r.sum()):+.3f}" if g is not None and r is not None and g.sum() != r.sum() else ""
        L.append(f"   {k:<22} {int(v.sum()):>5} ({v.mean():.4f}){pos}{extra}")
    if "BR-S" in be:
        md = [X[t].get("BR-S|mc_disagree", np.nan) for t in trials]
        L.append(f"   BR-S chain spread per block (median over queries): median {np.nanmedian(md):.2e}, p90 {np.nanquantile(md, .9):.2e}")
    for pr in a.pairs:
        x, y = pr.split(">")
        if x in be and y in be:
            p, q = int(np.sum((be[x] == 1) & (be[y] == 0))), int(np.sum((be[x] == 0) & (be[y] == 1)))
            L.append(f"   {x:>22} -> {y:<22} {p:>4}:{q:<4} p={sign_p(p, q):.2g}" + ("  UNDECIDED (n_d < 6)" if p + q < 6 else ""))
    txt = "\n".join(L)
    print(txt)
    if a.save:
        open(os.path.join(C.CONF, "results", "review_next", a.save), "a").write(txt + "\n")
    return 0


def cmd_check_cavity(a):
    """Pre-check (a): the driver's blk_err@16 (non-finite -> 1) of every arm also present in the p1_cavity record must equal
    the record's <arm>|fail (> 0) at every shared trial."""
    X = load(a.out, a.cell, a.snr)
    ref = {}
    for f in glob.glob(os.path.join(C.CONF, "results", "review_next", "p1_cavity", f"p1_cavity_D2_{a.cell}_*_snr{a.snr:g}_skip*_n*.npz")):
        s = int(PAT.search(os.path.basename(f)).group(6)); d = np.load(f, allow_pickle=True)
        for k in d.files:
            if k.endswith("|fail"):
                for i, v in enumerate(d[k]):
                    ref.setdefault(s + i, {})[k.split("|")[0]] = 1.0 if v > 0 else 0.0
    shared = sorted(set(X) & set(ref)); bad = {}
    for t in shared:
        for arm in ref[t]:
            if f"{arm}|blk_err" in X[t]:
                v = X[t][f"{arm}|blk_err"][15]; x = 1.0 if not np.isfinite(v) else float(v)
                bad[arm] = bad.get(arm, 0) + int(x != ref[t][arm])
    ok = bool(shared) and bad and all(v == 0 for v in bad.values())
    print(f"[check-cavity] {a.out} vs p1_cavity {a.cell} {a.snr:g} dB: shared trials {len(shared)}, mismatches per arm {bad} -> "
          f"{'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--cell", required=True); r.add_argument("--snr", type=float, required=True)
    r.add_argument("--skip0", type=int, required=True); r.add_argument("--n", type=int, required=True)
    r.add_argument("--chunk", type=int, default=20); r.add_argument("--iters", type=int, default=16)
    r.add_argument("--arms", nargs="+", required=True, choices=ALL_ARMS)
    r.add_argument("--fits-tag", default="B16e4k"); r.add_argument("--ntrain", type=int, default=160000)
    r.add_argument("--ckpt", default=os.path.join(C.CONF, "ckpt", "d2sx_N160000_a1.pt"))
    r.add_argument("--edge-M", type=int, default=16); r.add_argument("--edge-burn", type=int, default=100)
    r.add_argument("--edge-keep", type=int, default=100); r.add_argument("--edge-njac", type=int, default=16)
    r.add_argument("--bg-chains", type=int, default=4)
    r.add_argument("--out", required=True); r.add_argument("--jobs", type=int, default=None)
    r.add_argument("--resume", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("--out", required=True); c.add_argument("--ref", required=True)
    c.add_argument("--cell", required=True); c.add_argument("--snr", type=float, required=True)
    p = sub.add_parser("report")
    p.add_argument("--out", required=True); p.add_argument("--cell", required=True); p.add_argument("--snr", type=float, required=True)
    p.add_argument("--skip0", type=int, required=True); p.add_argument("--n", type=int, required=True)
    p.add_argument("--chunk", type=int, default=10); p.add_argument("--iters", type=int, default=16)
    p.add_argument("--fits-tag", default="B16e4k"); p.add_argument("--ntrain", type=int, default=160000)
    p.add_argument("--ckpt-sha", default=None)
    p.add_argument("--it", type=int, default=16); p.add_argument("--pairs", nargs="*", default=[])
    p.add_argument("--save", default=None)
    cc = sub.add_parser("check-cavity")
    cc.add_argument("--out", required=True); cc.add_argument("--cell", required=True); cc.add_argument("--snr", type=float, required=True)
    a = ap.parse_args()
    return {"run": cmd_run, "check": cmd_check, "report": cmd_report, "check-cavity": cmd_check_cavity}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
