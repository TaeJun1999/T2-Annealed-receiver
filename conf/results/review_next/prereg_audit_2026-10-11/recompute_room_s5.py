"""recompute_room_s5.py -- RECORD AUDIT of NEXT_EXPERIMENTS_ROOM16e4.md §5 (prior SRB; DMI withdrawn) and the timeline / acceptance
facts of §6.  Reads results/gmm_fits_D2_SRBB16e4/*.npz (ll_val, n_iter, it_best, n_reseed, kappa, restart, candidates, the stored ll
trajectory, pi, covs, Chat), their mtimes vs the freeze commit b737fd55, logs/tb2_post_SRB.{log,sel}, logs/tb2.log (SRB job lines),
the sigma grid, the manifests, the run logs' timing lines, the training log, the git commit times and diffs, the banner strings.
Answers: (1) is the evaluated b* (full K = 1024) a CONVERGED EM fit (which stopping rule fired, ll trajectory, model structure);
(2) does arms.gmm_selection return now what the hand-rewritten tb2_post_SRB.sel says; (3) is there any DMI BLER anywhere under conf/.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_room_s5.py > results/review_next/prereg_audit_2026-10-11/recompute_room_s5.out
"""
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np

CONF = "/home/HTJ/t2/conf"
FITS = os.path.join(CONF, "results/gmm_fits_D2_SRBB16e4")
KST = dt.timezone(dt.timedelta(hours=9))
FREEZE = dt.datetime(2026, 10, 12, 1, 23, 26, tzinfo=KST)        # b737fd55, = 10-11 11:23:26 CDT
TOL, PATIENCE, VAL_EVERY = 1e-6, 40, 10                           # gmm_em_gpu.fit_gmm_em_gpu defaults (fit_gpu passes neither)

# §5 fits table as transcribed (family, K): (ll_val 3 dp or full, restart, n_iter, it_best, reseed, kappa)
EXP_FULL = {16: (30.445, 0, 361, 340, 0, 0), 32: (41.698, 2, 179, 150, 354, 0), 64: (55.912, 2, 190, 180, 188, 0),
            128: (68.085, 1, 388, 370, 4632, 0), 256: (79.119, 0, 244, 240, 8953, 0), 512: (89.214, 1, 188, 180, 15243, 0),
            1024: (97.00871495382869, 0, 182, 180, 44081, 0)}
EXP_KRON = {16: (25.940, 1, 121, 80, 0, 0), 32: (34.173, 2, 164, 140, 164, 0), 64: (41.133, 2, 196, 160, 970, 0),
            128: (46.060, 2, 161, 120, 3657, 0), 256: (51.939, 1, 123, 90, 6171, 0), 512: (56.836, 1, 147, 140, 15658, 0),
            1024: (61.1622399385799, 0, 181, 140, 43670, 0), 2048: (64.84831463937753, 0, 215, 200, 124714, 0)}
EXP_CAND = {1024: [(61.162, 181, 140, 43670), (61.064, 162, 160, 40157), (61.028, 121, 80, 29268)],
            2048: [(64.848, 215, 200, 124714), (64.754, 151, 110, 91621), (64.745, 186, 170, 115696)],
            4096: [(67.634, 215, 180, 343246), (67.807, 164, 140, 254447), (67.584, 173, 170, 269847)]}
EXP_MERGE_MTIME = {1024: "04:07:49", 2048: "04:07:55"}            # KST (= 14:07:xx CDT)
EXP_FULL1024_MTIME = "04:49:46"                                   # KST (= 14:49:46 CDT)
EXP_SEL_MTIME = "04:50"                                           # KST (= 14:50 CDT, hand-rewritten)
EXP_SIGMA = (3.272627191797374e-02, 8.548070100767116e-01, 20)

OUT, NCHECK = [], [0, 0]


def p(*a):
    s = " ".join(str(x) for x in a)
    OUT.append(s)
    print(s)


def chk(label, got, exp, tol=0):
    NCHECK[0] += 1
    ok = (abs(got - exp) <= tol) if isinstance(exp, (int, float)) and not isinstance(exp, bool) else got == exp
    if not ok:
        NCHECK[1] += 1
        p(f"    DIFF  {label}: recomputed {got!r}  record {exp!r}")
    return ok


def mt(path):
    return dt.datetime.fromtimestamp(os.path.getmtime(path), KST)


def main():
    p("# recompute_room_s5.py -- §5 fits table / selection / timeline / stop-rule analysis / DMI absence (prior SRB)")
    p("\n## 1. fits table vs the npz files (final files; candidates for kron K >= 1024; the extra full 1024)")
    files = sorted(glob.glob(os.path.join(FITS, "*.npz")))
    chk("24 fit files (7 full + 6 kron + 9 kron candidates + 2 merged kron; kron 4096 NOT merged)", len(files), 24)
    chk("no merged kron 4096 file (rule: merge only if b* = kron 2048)", os.path.exists(os.path.join(FITS, "fit_SRB_Nr8_kronK4096_n160000.npz")), False)
    chk("no full 2048 file (STOP after full 1024)", os.path.exists(os.path.join(FITS, "fit_SRB_Nr8_fullK2048_n160000.npz")), False)
    maxit = 0
    stop_rows = []
    for fam, exp in (("full", EXP_FULL), ("kron", EXP_KRON)):
        for K, e in exp.items():
            f = os.path.join(FITS, f"fit_SRB_Nr8_{fam}K{K}_n160000.npz")
            z = np.load(f, allow_pickle=True)
            got = (float(z["ll_val"]), int(z["restart"]), int(z["n_iter"]), int(z["it_best"]), int(z["n_reseed"]), int(z["kappa"]))
            p(f"  {fam} {K:5d}: ll_val {got[0]:.6f} r{got[1]} n_iter {got[2]} it_best {got[3]} reseed {got[4]} kappa {got[5]}  mtime {mt(f).strftime('%m-%d %H:%M:%S KST')}")
            chk(f"{fam} {K} ll_val", round(got[0], 3) if (fam == "kron" and K < 1024) or (fam == "full" and K < 1024) else got[0], e[0], 0 if (K >= 1024) else 0.0006)
            chk(f"{fam} {K} (restart, n_iter, it_best, reseed, kappa)", got[1:], e[1:])
            chk(f"{fam} {K} file mtime after the freeze (01:23:26 KST)", mt(f) > FREEZE, True)
            maxit = max(maxit, got[2])
            ll = np.asarray(z["ll"], float)
            last = len(ll) - 1
            tol_rule = last >= 20 and (ll[-1] - ll[-2] < TOL * abs(ll[-1]))
            pat_rule = (last % VAL_EVERY == 0) and (last - int(z["it_best"]) >= PATIENCE)
            stop_rows.append((fam, K, last, int(z["it_best"]), tol_rule, pat_rule, ll[0], ll[1] if len(ll) > 1 else np.nan, ll[-2], ll[-1], ll.max(), int(np.argmax(ll))))
            if fam == "kron" and K >= 1024:
                cands = []
                for r in range(3):
                    zc = np.load(os.path.join(FITS, f"fit_SRB_Nr8_kronK{K}_n160000.k0r{r}.npz"), allow_pickle=True)
                    cands.append((round(float(zc["ll_val"]), 3), int(zc["n_iter"]), int(zc["it_best"]), int(zc["n_reseed"])))
                chk(f"kron {K} candidates (ll_val 3 dp, n_iter, it_best, reseed)", cands, EXP_CAND[K])
                chk(f"kron {K} merged cand_ll_val == candidates", [round(float(v), 3) for v in z["cand_ll_val"]], [c[0] for c in EXP_CAND[K]])
                chk(f"kron {K} selected = argmax cand_ll_val", int(np.argmax(z["cand_ll_val"])), int(z["restart"]))
                chk(f"kron {K} merged mtime (KST)", mt(f).strftime("%H:%M:%S"), EXP_MERGE_MTIME[K])
            if fam == "full" and K == 1024:
                chk("full 1024 file mtime 04:49:46 KST (= 14:49:46 CDT)", mt(f).strftime("%H:%M:%S"), EXP_FULL1024_MTIME)
                chk("full 1024: 12 (kappa, restart) EM runs (same protocol as the base grid: kappa grid x 3 restarts)", int(z["cand"].shape[0]), 12)
                p(f"  full 1024 candidates (kappa, restart) -> ll_val: {[(int(a), int(b), round(float(v), 3)) for (a, b), v in zip(z['cand'], z['cand_ll_val'])]}")
                chk("full 1024 selected candidate = argmax cand_ll_val", int(np.argmax(z["cand_ll_val"])), int(np.flatnonzero((z["cand"][:, 0] == int(z["kappa"])) & (z["cand"][:, 1] == int(z["restart"])))[0]))
    cands4096 = []
    for r in range(3):
        zc = np.load(os.path.join(FITS, f"fit_SRB_Nr8_kronK4096_n160000.k0r{r}.npz"), allow_pickle=True)
        cands4096.append((round(float(zc["ll_val"]), 3), int(zc["n_iter"]), int(zc["it_best"]), int(zc["n_reseed"])))
    chk("kron 4096 candidates (unmerged) ll_val / n_iter / it_best / reseed", cands4096, EXP_CAND[4096])
    chk("§5 '후보 ll_val 67.634 / 67.807 / 67.584'", [c[0] for c in cands4096], [67.634, 67.807, 67.584])
    chk("max n_iter over all files = 388 ('상한 500 정지 없음')", maxit, 388)
    chk("every n_iter < 500", maxit < 500, True)
    chk("first selection: full 512 is the base-grid full maximum and beats every kron (89.214 > 64.848)", (max(k for k in EXP_FULL if k <= 512), EXP_FULL[512][0] > EXP_KRON[2048][0]), (512, True))
    chk("§5 '512 대비 +7.795 nat'", round(EXP_FULL[1024][0] - 89.21392313986264, 3), 7.795)
    chk("full 1024 > full 512 > kron 2048 (b* = full 1024 by argmax)", EXP_FULL[1024][0] > 89.21392313986264 > EXP_KRON[2048][0], True)
    chk("full 1024 is 'still rising' (ll_val increased from 512 to 1024)", EXP_FULL[1024][0] > EXP_FULL[512][0], True)
    for f in files:
        chk(f"mtime after freeze: {os.path.basename(f)}", mt(f) > FREEZE, True)
    pre = [os.path.basename(f) for f in files if mt(f) < FREEZE]
    p(f"  files with mtime before the freeze: {pre if pre else 'none'} (the 3 kron-1024 candidates ENDED before the freeze per tb2.log but their mtimes are: "
      + ", ".join(mt(os.path.join(FITS, f'fit_SRB_Nr8_kronK1024_n160000.k0r{r}.npz')).strftime('%H:%M:%S') for r in range(3)) + " KST)")
    sel = open(os.path.join(CONF, "logs/tb2_post_SRB.sel")).read().strip()
    chk("tb2_post_SRB.sel", sel, "gmm1024 - 97.00871495382869")
    chk(".sel mtime 04:50 KST (after the full-1024 file; hand-rewritten)", mt(os.path.join(CONF, "logs/tb2_post_SRB.sel")).strftime("%H:%M"), EXP_SEL_MTIME)
    chk(".sel mtime after the full 1024 file", mt(os.path.join(CONF, "logs/tb2_post_SRB.sel")) > mt(os.path.join(FITS, "fit_SRB_Nr8_fullK1024_n160000.npz")), True)
    chk("gmm_fits_D2_SRBB16e4last is a symlink to gmm_fits_D2_SRBB16e4", os.readlink(os.path.join(CONF, "results/gmm_fits_D2_SRBB16e4last")), "gmm_fits_D2_SRBB16e4")

    p("\n## 1b. arms.gmm_selection NOW (the runner's selection code) vs the hand-rewritten .sel")
    sys.path.insert(0, os.path.join(CONF, "code"))
    import arms as A  # noqa: E402
    import runner  # noqa: E402
    runner._init("SRBB16e4")
    fits, llv, b, kK = A.gmm_selection("D2", "SRB", 8, 160000)
    p(f"  gmm_selection -> b* = {b}, kron_K = {kK}, ll_val by arm = {{{', '.join(f'{k}: {v:.4f}' for k, v in llv.items())}}}; fits loaded: {sorted(fits)}")
    chk("gmm_selection b* == gmm1024", b, "gmm1024")
    chk("gmm_selection ll_val == .sel == §5", repr(llv[b]), "97.00871495382869")
    chk("gmm_selection kron_K = 2048 (informational; matches raw meta|kron_K)", kK, 2048)
    chk("gmm_selection loads 7 full + 8 kron merged files (no 4096, no full 2048)", (sorted(K for f, K in fits if f == "full"), sorted(K for f, K in fits if f == "kron")),
        ([16, 32, 64, 128, 256, 512, 1024], [16, 32, 64, 128, 256, 512, 1024, 2048]))
    chk(".sel line == f'{b} - {ll_val!r}' as the post-select script would write it for a full family", sel, f"{b} - {llv[b]!r}")

    p("\n## 2. which stopping rule fired (gmm_em_gpu: val every 10 it, patience 40 on it_best; train-ll tol rule from it >= 20)")
    p("  fam  K      last_it it_best  tol_rule  patience_rule   ll[0]      ll[1]      ll[-2]     ll[-1]     max(ll) @it")
    n_tol = n_pat = 0
    for fam, K, last, ib, tr, pr, l0, l1, lm2, lm1, lmax, imax in stop_rows:
        p(f"  {fam:4s} {K:5d}  {last:5d}   {ib:3d}     {str(tr):5s}     {str(pr):5s}       {l0:9.3f}  {l1:9.3f}  {lm2:9.3f}  {lm1:9.3f}  {lmax:9.3f} @{imax}")
        n_tol += tr; n_pat += pr
    p(f"  -> stopped by the train-ll tolerance rule: {n_tol} of {len(stop_rows)}; by validation patience: {n_pat}")
    chk("every final fit has it_best >= 80 (EM improved the validation likelihood; no fit is the seed initialisation)", all(ib >= 80 for _, _, _, ib, *_ in stop_rows), True)
    chk("train ll at the LAST iteration is within 1e-3 nat of the trajectory maximum in every fit (EM converged, no collapse)",
        all(lmax - lm1 < 1e-3 for *_, lm1, lmax, _ in stop_rows), True)
    chk("train ll rose from it 0 to the end in every fit (ll[-1] > ll[0] + 10 nat)", all(lm1 > l0 + 10 for *_, l0, _, _, lm1, _, _ in stop_rows), True)

    p("\n## 3. what the selected b* (full K = 1024) is: pi, covs structure, trajectory")
    z = np.load(os.path.join(FITS, "fit_SRB_Nr8_fullK1024_n160000.npz"), allow_pickle=True)
    pi, covs, Chat = z["pi"], z["covs"], z["Chat"]
    ll = np.asarray(z["ll"], float)
    p(f"  pi: min {pi.min():.2e} max {pi.max():.2e} median {np.median(pi):.2e} (uniform would be {1 / 1024:.2e}); sum {pi.sum():.6f}; #pi < 1e-5: {int((pi < 1e-5).sum())}")
    chk("pi NOT uniform (max/min > 3)", float(pi.max() / pi.min()) > 3, True)
    chk("pi sums to 1", abs(float(pi.sum()) - 1) < 1e-9, True)
    rng = np.random.default_rng(0)
    rk1, herm, psd = [], True, True
    for k in rng.choice(1024, 64, replace=False):
        D = covs[k] - 0.5 * Chat
        s = np.linalg.svd(D, compute_uv=False); rk1.append(s[1] / s[0])
        herm &= bool(np.allclose(covs[k], covs[k].conj().T, atol=1e-10))
        psd &= bool(np.linalg.eigvalsh(covs[k]).min() > -1e-10)
    p(f"  64 random components: min/median/max s2/s1 of (cov_k - 0.5 Chat) = {min(rk1):.3f} / {np.median(rk1):.3f} / {max(rk1):.3f} (rank-1 ~ 1e-16 would mean the seed initialisation); Hermitian {herm}, PSD {psd}")
    chk("cov_k - 0.5 Chat is NOT rank-1 in any sampled component (the fit moved away from the seed initialisation)", min(rk1) > 1e-3, True)
    chk("covs Hermitian PSD", (herm, psd), (True, True))
    ev = np.array([np.linalg.eigvalsh(covs[k]) for k in range(1024)])
    p(f"  component covariance eigenvalues (32 each): median of (max/min) {np.median(ev[:, -1] / ev[:, 0]):.2e}; median of min eig {np.median(ev[:, 0]):.2e}; floor 1e-4 hit in {int((ev[:, 0] < 1.01e-4).sum())} components")
    p(f"  train ll trajectory: it0 {ll[0]:.3f}, it1 {ll[1]:.3f}, it10 {ll[10]:.3f}, it100 {ll[100]:.3f}, it180 {ll[180]:.3f}, it181 {ll[181]:.3f}; max {ll.max():.3f} @{int(np.argmax(ll))}; "
      f"monotone non-decreasing steps: {int((np.diff(ll) >= -1e-9).sum())} of {len(ll) - 1}; ll_train stored {float(z['ll_train']):.4f} (= ll[it_best]); ll_val {float(z['ll_val']):.4f}; ll_test {float(z['ll_test']):.4f}; gauss_val {float(z['gauss_val']):.4f}")
    chk("stored ll_train == ll[it_best]", abs(float(z["ll_train"]) - ll[int(z["it_best"])]) < 1e-9, True)
    chk("full 1024: it_best 180 = the last validation iteration before the stop at it 181 -> validation ll was still (weakly) improving at the end", int(z["it_best"]), 180)
    chk("full 1024: last step |ll[-1]-ll[-2]| < tol*|ll| (train-ll tolerance stop at it 181)", bool(ll[-1] - ll[-2] < TOL * abs(ll[-1])), True)
    chk("full 1024 train-val gap (ll_train - ll_val) < 5 nat (no gross overfit)", float(z["ll_train"]) - float(z["ll_val"]) < 5, True)
    chk("full 1024: ll_val - gauss_val > 100 nat (the mixture explains far more than the Gaussian prior)", float(z["ll_val"]) - float(z["gauss_val"]) > 100, True)
    st_ = z["sparse_tol"].astype(float)
    chk("sparse_tol unset (nan or 0) / kron_batched 0 for the full family (exact path)", (bool(np.all(np.isnan(st_) | (st_ == 0))), float(z["kron_batched"].max())), (True, 0.0))

    p("\n## 4. sigma grid, manifests, commit times, run-log timing lines, training log, tb2 / post / sparse logs, git diffs, banners")
    sg = np.load(os.path.join(CONF, "results/sigma_grid_D2_SRB.npz"))
    chk("sigma grid 20 points, endpoints", (float(sg["sigma"].min()), float(sg["sigma"].max()), int(sg["sigma"].size)), EXP_SIGMA)
    for tag, egit, ecfg in (("SRBB16e4", "9ad4caa0", "6b12b56f55a3319e"), ("SRBB16e4last", "9ad4caa0", "6b12b56f55a3319e"),
                            ("PILSRB", "7d524638", "f5a83cbf01b47958"), ("ALDSRB", "7d524638", "f5a83cbf01b47958"), ("SPSRB", "7d524638", "f5a83cbf01b47958")):
        m = json.load(open(os.path.join(CONF, f"results/review_next/run_manifest_{tag}.json")))
        p(f"  manifest {tag}: git {m['git_commit']} config_hash {m['config_hash']} n_raw {m['n_raw_files']} written {m.get('written')} Demo {m['code_hashes'] if isinstance(m['code_hashes'], str) else m['code_hashes'].get('Demo')}")
        chk(f"manifest {tag} git", m["git_commit"], egit)
        chk(f"manifest {tag} n_raw_files", m["n_raw_files"], 448)
        chk(f"manifest {tag} config_hash", m["config_hash"], ecfg)
    mb, ml = (json.load(open(os.path.join(CONF, f"results/review_next/run_manifest_{t}.json"))) for t in ("SRBB16e4", "SRBB16e4last"))
    chk("both main manifests: identical Demo hashes", mb["code_hashes"].get("Demo") if isinstance(mb["code_hashes"], dict) else mb["code_hashes"], ml["code_hashes"].get("Demo") if isinstance(ml["code_hashes"], dict) else ml["code_hashes"])
    git = subprocess.run(["git", "show", "-s", "--format=%h %ci", "b737fd55", "9ad4caa0", "7d524638", "f183160d", "99039ef5"], cwd=CONF, capture_output=True, text=True).stdout.split("\n")
    p("  commits: " + " | ".join(g for g in git if g))
    t = {g.split()[0]: dt.datetime.strptime(" ".join(g.split()[1:3]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST) for g in git if g}
    chk("freeze commit time == 10-11 11:23:26 CDT", t["b737fd55"], FREEZE)
    chk("§5 commit 9ad4caa0 == 15:06:43 CDT ('갱신 15:06 CDT')", t["9ad4caa0"], dt.datetime(2026, 10, 12, 5, 6, 43, tzinfo=KST))
    chk("§6 commit f183160d == 16:35:37 CDT ('기록 16:35 CDT')", t["f183160d"], dt.datetime(2026, 10, 12, 6, 35, 37, tzinfo=KST))
    first_best = min(mt(f) for f in glob.glob(os.path.join(CONF, "raw_SRBB16e4/*.npz")))
    last_last = max(mt(f) for f in glob.glob(os.path.join(CONF, "raw_SRBB16e4last/*.npz")))
    first_pil = min(mt(f) for f in glob.glob(os.path.join(CONF, "raw_PILSRB/*.npz")))
    last_sp = max(mt(f) for f in glob.glob(os.path.join(CONF, "raw_SPSRB/*.npz")))
    p(f"  first raw_SRBB16e4 chunk {first_best.strftime('%H:%M:%S KST')} (run commit 9ad4caa0 at {t['9ad4caa0'].strftime('%H:%M:%S KST')}); last raw_SRBB16e4last chunk {last_last.strftime('%H:%M:%S KST')}; "
      f"first raw_PILSRB chunk {first_pil.strftime('%H:%M:%S KST')} (commit 7d524638 at {t['7d524638'].strftime('%H:%M:%S KST')}); last raw_SPSRB chunk {last_sp.strftime('%H:%M:%S KST')}")
    chk("main run raws written after the run commit 9ad4caa0", first_best > t["9ad4caa0"], True)
    chk("no main commit during the main run: 7d524638 is after the last SRBB16e4last chunk", t["7d524638"] > last_last, True)
    chk("baseline raws written after the commit 7d524638", first_pil > t["7d524638"], True)
    chk("commit 7d524638 after PRIOR_EVAL_DONE (16:17 CDT = 06:17 KST) and before the baseline start line (06:18 KST)", dt.datetime(2026, 10, 12, 6, 17, 0, tzinfo=KST) < t["7d524638"] < dt.datetime(2026, 10, 12, 6, 19, 0, tzinfo=KST), True)
    chk("§6 commit f183160d after the last baseline raw", t["f183160d"] > last_sp, True)
    for tag, emin in (("SRBB16e4", 28.3), ("SRBB16e4last", 24.8), ("PILSRB", 1.4), ("ALDSRB", 0.4), ("SPSRB", 10.4)):
        log = open(os.path.join(CONF, f"logs/run_D2_{tag}.log")).read()
        done = len(re.findall(r"^\s*\d+/448 done", log, re.M)); exists = log.count("exists")
        fin = re.search(r"finished in ([\d.]+) min", log)
        chk(f"run_D2_{tag}.log: 448 done lines, no 'exists', finished in {emin} min", (done, exists, float(fin.group(1)) if fin else None), (448, 0, emin))
        chk(f"run_D2_{tag}.log: '448 tasks on 192 workers' once", log.count("448 tasks on 192 workers"), 1)
    pe = open(os.path.join(CONF, "logs/run_prior_eval_SRBB16e4.log")).read()
    chk("prior_eval log: start 15:22 (git 9ad4caa0, bstar=gmm1024 kron_K=-), measurement done 15:50, last done 16:15, decision SNRs -3 +0 +3, acceptance rc=0 16:16, PRIOR_EVAL_DONE 16:17 (CDT)",
        all(s in pe for s in ("10-11 15:22 CDT] start (git 9ad4caa0) prior=SRB bstar=gmm1024 kron_K=- ll_val=97.00871495382869 best=ed437f21af15c305 last=b5f74923f2bd2920 ckpt=d2sx_SRB_N160000_a1",
                              "10-11 15:50 CDT] run SRBB16e4 (measurement) done", "10-11 16:15 CDT] SRBB16e4last done", "decision SNRs (anchor b*, tag SRBB16e4): -3 +0 +3",
                              "10-11 16:16 CDT] acceptance rc=0 (ACCEPT: OK -- SRBB16e4, SRBB16e4last)", "10-11 16:17 CDT] recovery diff rc=0", "10-11 16:17 CDT] PRIOR_EVAL_DONE")), True)
    chk("prior_eval log: exactly one start line (ran once)", pe.count("] start (git"), 1)
    sb = open(os.path.join(CONF, "logs/run_srb_base.log")).read()
    chk("srb_base log: one start line, 16:18 CDT, git 7d524638, pick / ald_tune shas", (sb.count("] start (git"), "[srb_base 10-11 16:18 CDT] start (git 7d524638) ckpt=d2sx_SRB_N160000_a1 best=ed437f21af15c305 pick=4c6da315c701b9d4 ald_tune=e0adb06cce792093" in sb), (1, True))
    chk("srb_base log: PIL 16:19 / ALD 16:21 / SP 16:31 ACCEPT OK, pair_baselines rc=0, SRB_BASE_DONE rc=0 16:32, rule-reproduced, memory line, ALD on GPU 1, no DEFER line",
        all(s in sb for s in ("16:19 CDT] PIL acceptance (ACCEPT: OK -- PILSRB)", "16:21 CDT] ALD acceptance (ACCEPT: OK -- ALDSRB)", "16:31 CDT] SP acceptance (ACCEPT: OK -- SPSRB)",
                              "16:32 CDT] pair_baselines rc=0", "16:32 CDT] SRB_BASE_DONE rc=0", "rule-reproduced=True", "memory need ~264 GB, available 1028 GB", "16:20 CDT] ALD estimate on GPU 1 done",
                              "ald_PILSRB.npz sha256[:16]=a3d249188f9c061a" if "a3d249188f9c061a" in sb else "16:20 CDT")) and "deferred" not in sb, True)
    chk("srb_base log: pair_cross integrity OK raised 0/0; pair_ald integrity OK; meta|sparse 0 mismatching; raised SP 0/0/0",
        all(s in sb for s in ("raised trials {'V1-pilot': 0, 'bstar-pilot': 0}", "no raised ALD trial", "meta|sparse check raw_SPSRB: 0 mismatching chunks", "{'SBL-loop': 0, 'SBL-pilot': 0, 'OMP-pilot': 0}")), True)
    tb = open(os.path.join(CONF, "logs/tb2.log")).read()
    starts = re.findall(r"\[tb2 10-11 (\d\d:\d\d) CDT\] GPU (\d) start: code/fit_gpu(?:_batched)?\.py 8 \w+ \d+ 160000 SRBB16e4", tb)
    dones = re.findall(r"\[tb2 10-11 (\d\d:\d\d) CDT\] GPU (\d) done rc=(\d+): code/fit_gpu(?:_batched)?\.py 8 \w+ \d+ 160000 SRBB16e4", tb)
    chk("tb2.log: 21 SRB fit jobs, first start 11:03, last done 14:07 CDT, all rc=0, GPUs {0,1,2}", (len(starts), len(dones), starts[0][0], max(d[0] for d in dones), all(d[2] == "0" for d in dones), sorted({g for _, g in starts})), (21, 21, "11:03", "14:07", True, ["0", "1", "2"]))
    pre_done = [(tm, m) for tm, g, rc in dones for m in [re.search(rf"\[tb2 10-11 {tm} CDT\] GPU {g} done rc=0: (code/\S+ 8 \w+ \d+)", tb).group(1)] if tm < "11:23"]
    chk("tb2.log: exactly 3 SRB fit jobs ended before the freeze 11:23 CDT (the kron 1024 candidates)", (len(pre_done), all("kron 1024" in m for _, m in pre_done)), (3, True))
    chk("tb2.log: SRB training 11:03 start (GPU 1), patience stop 13:27 CDT", ("10-11 11:03 CDT] GPU 1 start: @train SRB SRBB16e4" in tb and "10-11 13:27 CDT] train SRB fallback 1: stopped_by=patience" in tb), True)
    chk("tb2.log: stop-file NOTE lines 11:45 / 11:52 / 13:13 / 13:23, SRP-at-head 12:11, DMI withdrawal 13:49, queue empty 14:07 (§5 '실행 사실' (1))",
        all(s in tb for s in ("[tb2 10-11 11:45 CDT] NOTE: stop file set", "[tb2 10-11 11:52 CDT] NOTE: stop file removed", "[tb2 10-11 12:11 CDT] NOTE: 22 SRP jobs", "[tb2 10-11 13:13 CDT] NOTE: stop file set",
                              "[tb2 10-11 13:23 CDT] NOTE: stop file removed", "[tb2 10-11 13:49 CDT] NOTE: the 21 DMI fit jobs are removed from the queue by user decision", "[tb2 10-11 14:07 CDT] NOTE: queue empty")), True)
    chk("tb2.log: no DMI fit job ever started", len(re.findall(r"start: code/fit_gpu(?:_batched)?\.py 8 \w+ \d+ 160000 DMIB16e4", tb)), 0)
    chk("tb2.log: DMI training ended by patience 12:44 CDT (checkpoint kept)", "10-11 12:44 CDT] train DMI fallback 1: stopped_by=patience (ckpt/d2sx_DMI_N160000_a1.pt)" in tb, True)
    ps = open(os.path.join(CONF, "logs/tb2_post_SRB.log")).read()
    chk("tb2_post_SRB.log: freeze check 14:07, first SELECT gmm512 (kron_K 2048), edge rule 14:08 full 1024 ONCE on GPU 2, full 1024 rc=0 14:49, 14:50 SELECT gmm1024, STOP (no full 2048), ALD 14:07 -> 14:19 rc=0, GB' 16:33 on GPU 1",
        all(s in ps for s in ("14:07 CDT] freeze b737fd55 (10-11 11:23:26 CDT) done; 21 fit files present", "SELECT b* = gmm512 kron_K = 2048 ll_val = 89.21392313986264",
                              "14:08 CDT] b* = full 512 = full-family grid edge -> registered rule: full 1024 ONCE on GPU 2 (git 99039ef5)", "14:49 CDT] full 1024 rc=0; FULL1024_DONE",
                              "14:50 CDT] after full 1024 (registered edge rule, once): SELECT b* = gmm1024 ll_val = 97.00871495382869 (gmm512 89.21392313986264; kron best K 2048 64.8483)", "STOP (no full 2048); POST_SELECT_DONE",
                              "14:07 CDT] ALD dev regen (CPU) + tune on GPU 0 (ckpt d2sx_SRB_N160000_a1, git 99039ef5)", "14:19 CDT] ALD tune rc=0; POST_ALD_DONE", "16:33 CDT] GB' resume on GPU 1 (ckpt d2sx_SRB_N160000_a1, git 7d524638)")), True)
    chk("tb2_post_SRB.log: the script's own final line said gmm512 (first pass) -- the .sel was then rewritten by hand (record discloses this)", "final b* (family kron_K ll_val) = gmm512 - 89.21392313986264" in ps, True)
    chk("tb2_post_SRB.log: the merged kron files were not re-merged after full 1024 (one MERGE line each)", (ps.count("kronK1024_n160000.npz  MERGE"), ps.count("kronK2048_n160000.npz  MERGE")), (1, 1))
    chk("pick_SRB_C2.json mtime 02:49 KST (= 12:49 CDT), tune_PILSRB.json 04:19 KST (= 14:19 CDT), both after the freeze",
        (mt(os.path.join(CONF, "results/sparse/pick_SRB_C2.json")).strftime("%H:%M"), mt(os.path.join(CONF, "results/ald/tune_PILSRB.json")).strftime("%H:%M"),
         mt(os.path.join(CONF, "results/sparse/pick_SRB_C2.json")) > FREEZE), ("02:49", "04:19", True))
    chk("pick written after the judged tag? NO -- pick 02:49 KST is before the main run (15:22 CDT = 05:22 KST); it was read only by the baseline runner (16:18 CDT)", mt(os.path.join(CONF, "results/sparse/pick_SRB_C2.json")) < dt.datetime(2026, 10, 12, 5, 22, tzinfo=KST), True)
    chk("ckpt mtimes best 03:25 / last 03:27 KST (11:03 -> 13:27 CDT training)", (mt(os.path.join(CONF, "ckpt/d2sx_SRB_N160000_a1_best.pt")).strftime("%H:%M"), mt(os.path.join(CONF, "ckpt/d2sx_SRB_N160000_a1.pt")).strftime("%H:%M")), ("03:25", "03:27"))
    chk("tb2_train_state_SRB.txt = '1 patience'", open(os.path.join(CONF, "logs/tb2_train_state_SRB.txt")).read().strip(), "1 patience")
    tl = open(os.path.join(CONF, "logs/train_d2sx_SRB_N160000_a1.log")).read()
    chk("training log: one real run (01:03:36 KST header; done 1680 epochs patience best 2.476990e-01 @1660 wall 8627.0 s 5.135 s/epoch) + one no-op resume header (06:33:23 KST, GB' lane, 'no epoch trained ... left untouched')",
        (tl.count("# ====="), "# done        : 1680 epochs, stopped_by=patience, aborted=False, best val 2.476990e-01 @ epoch 1660, wall 8627.0 s, 5.135 s/epoch" in tl,
         "2026-10-12 06:33:23 KST" in tl and "# resume      : checkpoint already meets stopped_by=patience at epoch 1680 -- no epoch trained" in tl), (2, True, True))
    chk("training log: n_train=144000 n_val=16000 split_hash=c009329584978bd9 (9:1 of 160000)", "n_train=144000 n_val=16000 split_hash=c009329584978bd9" in tl, True)
    chk("training log: 1680 'epoch' lines", len(re.findall(r"^epoch\s+\d+ \|", tl, re.M)), 1680)
    chk("run_tb2.sh pins GPU 1 training to taskset -c 21,117", "taskset -c $([ $g -le 3 ] && echo $((20 + g)),$((116 + g))" in open(os.path.join(CONF, "code/run_tb2.sh")).read(), True)
    d1 = subprocess.run(["git", "diff", "--stat", "b737fd55", "9ad4caa0", "--", "conf/code", "Demo"], cwd="/home/HTJ/t2", capture_output=True, text=True).stdout
    d2 = subprocess.run(["git", "diff", "--stat", "9ad4caa0", "7d524638", "--", "conf/code", "Demo"], cwd="/home/HTJ/t2", capture_output=True, text=True).stdout
    d3 = subprocess.run(["git", "diff", "--stat", "b737fd55", "9ad4caa0", "--", "Demo"], cwd="/home/HTJ/t2", capture_output=True, text=True).stdout
    p(f"  git diff --stat b737fd55..9ad4caa0 -- conf/code Demo:\n{d1}")
    chk("git diff 9ad4caa0..7d524638 -- conf/code Demo is EMPTY (record)", d2.strip(), "")
    chk("git diff b737fd55..9ad4caa0 -- Demo is EMPTY", d3.strip(), "")
    chk("git diff b737fd55..9ad4caa0 -- conf/code: 17 files, all SRP additions / SRP branches / run_srb_eval.sh args (no receiver module: no route_a / arms / gmm_em / runner.py / score / dmimo pool-read change)",
        ("17 files changed" in d1) and not any(x in d1 for x in ("route_a", "arms.py", "gmm_em", "runner.py", "score.py", "bigamp", "scvamp", "sparse.py", "ald.py")), True)
    d4 = subprocess.run(["git", "diff", "b737fd55", "9ad4caa0", "--", "conf/code/dmimo.py", "conf/code/common.py", "conf/code/analysis.py"], cwd="/home/HTJ/t2", capture_output=True, text=True).stdout
    chk("dmimo.py / common.py / analysis.py diffs touch only SRP entries (every changed line mentions SRP / srp)", all(("SRP" in l or "srp" in l) for l in d4.splitlines() if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---"))), True)
    chk("record §1-§3 unchanged since the freeze (git diff b737fd55..f183160d of the record starts at line 138, §4 onward)",
        re.findall(r"^@@ -(\d+)", subprocess.run(["git", "diff", "b737fd55", "f183160d", "--", "conf/results/review_next/NEXT_EXPERIMENTS_ROOM16e4.md"], cwd="/home/HTJ/t2", capture_output=True, text=True).stdout, re.M), ["138"])
    for tag in ("SRBB16e4", "SRBB16e4last"):
        tt = open(os.path.join(CONF, f"results/tables_D2_{tag}.txt")).read()
        chk(f"tables_D2_{tag}: banner once, 'metal walls as shipped' present, sparse-specular banner absent, no 'FIVE'", (tt.count("SITE-SPECIFIC RAY-TRACED TESTBED (prior SRB)"), "metal walls" in tt, tt.count("CLAIM TESTBED -- sparse specular"), "FIVE" in tt), (1, True, 0, False))
        chk(f"tables_D2_{tag}: git 9ad4caa0, prior SRB, N_train=160000 lines >= 12, b*=gmm1024, stagec_ckpt_id", ("# git commit  : 9ad4caa0" in tt and "prior SRB" in tt and tt.count("N_train=160000") >= 12 and "b*=gmm1024" in tt and ("ed437f21af15c305" if tag == "SRBB16e4" else "b5f74923f2bd2920") in tt), True)
    for tag in ("SRBB16e4", "PILSRB", "ALDSRB", "SPSRB"):
        a = open(os.path.join(CONF, f"results/review_next/{tag}_accept.txt")).read().strip()
        chk(f"{tag}_accept.txt first line", a.split("\n")[0], f"ACCEPT: OK -- {tag}" + (", SRBB16e4last" if tag == "SRBB16e4" else ""))

    p("\n## 5. DMI: no BLER anywhere under conf/ (raw dirs, tables, manifests, accept, pair files, logs)")
    dmi_raw = sorted(glob.glob(os.path.join(CONF, "raw_*DMI*/*.npz")))
    dmi_files = sorted(os.path.relpath(f, CONF) for pat in ("results/tables_D2_*DMI*", "results/guard_D2_*DMI*", "results/review_next/*DMI*", "results/gmm_fits_D2_*DMI*", "logs/run_D2_*DMI*", "logs/run_prior_eval_*DMI*", "logs/analysis_*DMI*", "results/ald/*DMI*", "results/d2_gbprime_DMI*") for f in glob.glob(os.path.join(CONF, pat)))
    p(f"  raw_*DMI* npz files: {len(dmi_raw)}; raw_DMI dir exists (empty, mtime {mt(os.path.join(CONF, 'raw_DMI')).strftime('%m-%d %H:%M KST') if os.path.isdir(os.path.join(CONF, 'raw_DMI')) else '-'}; from the sigma-grid measurement, like raw_SRB): {os.path.isdir(os.path.join(CONF, 'raw_DMI'))}; other DMI result files: {dmi_files}")
    chk("no DMI raw npz anywhere under conf/raw_*", len(dmi_raw), 0)
    chk("no DMI tables / guard / review_next / fits dir / run logs / ALD / GB' files", dmi_files, [])
    chk("raw_DMI and raw_SRB are both empty directories (sigma-grid artefacts, 00:42 / 00:47 KST = before the registration)", (os.listdir(os.path.join(CONF, "raw_DMI")), os.listdir(os.path.join(CONF, "raw_SRB"))), ([], []))
    chk("DMI checkpoints kept on disk (record)", (os.path.exists(os.path.join(CONF, "ckpt/d2sx_DMI_N160000_a1.pt")), os.path.exists(os.path.join(CONF, "ckpt/d2sx_DMI_N160000_a1_best.pt"))), (True, True))
    dl = open(os.path.join(CONF, "logs/train_d2sx_DMI_N160000_a1.log")).read()
    chk("DMI training log: 1162 epochs, patience, best @1142 (record 'epoch 1162')", "# done        : 1162 epochs, stopped_by=patience, aborted=False, best val 2.152151e-01 @ epoch 1142" in dl, True)
    chk("DMI sparse tune files exist (12:49 CDT) but no DMI pick was ever consumed (no raw_SPDMI)", (os.path.exists(os.path.join(CONF, "results/sparse/pick_DMI_C2.json")), os.path.isdir(os.path.join(CONF, "raw_SPDMI"))), (True, False))
    chk("no DMI ALD tune file", os.path.exists(os.path.join(CONF, "results/ald/tune_PILDMI.json")), False)
    dec = open(os.path.join(CONF, "DECISIONS.md")).read()
    chk("DECISIONS.md: freeze line (01:23 KST) states SRB epoch 229 / DMI 221 at the freeze (prediction 9 lower bound still scorable: < 300)", "학습 SRB epoch 229 · DMI epoch 221" in dec, True)
    chk("DECISIONS.md: DMI withdrawal line with the user's words and 13:49 CDT", "'Deepmimo 포기하고 sionna에 올인해'" in dec and "큐에서 DMI 적합 21 작업 제거 (13:49 CDT; 시작한 적합 없음)" in dec, True)
    gb = os.path.join(CONF, "results/d2_gbprime_SRB.csv")
    p(f"  GB' (pending in the record): d2_gbprime_SRB.csv exists {os.path.exists(gb)}" + (f", mtime {mt(gb).strftime('%m-%d %H:%M KST')} (after the §6 commit 06:35 KST: {mt(gb) > t['f183160d']}); content: {open(gb).read().strip().splitlines()[-1]}" if os.path.exists(gb) else ""))
    rec = open(os.path.join(CONF, "results/review_next/NEXT_EXPERIMENTS_ROOM16e4.md")).read()
    s6 = rec[rec.index("## 6. 결과"):]
    chk("record §6 claims no GB' number (every GB' mention says 계산 중 / 보류 / 추가)", all(("계산 중" in l or "보류" in l or "추가" in l or "pending" in l) for l in s6.splitlines() if "GB′" in l or "GB'" in l), True)
    chk("record §6 has no equivalence / generalisation wording (동치, 일반화 only in the negated sentences)", all(("않" in l or "없" in l) for l in s6.splitlines() if "동치" in l or "일반화" in l), True)

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
