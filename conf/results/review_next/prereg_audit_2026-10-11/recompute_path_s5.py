"""recompute_path_s5.py -- RECORD AUDIT of NEXT_EXPERIMENTS_PATH16e4.md §5 (+ addendum) and the timeline / acceptance facts of §6.

Reads results/gmm_fits_D2_SRPB16e4/*.npz (ll_val, n_iter, it_best, n_reseed, kappa, restart, candidates, the stored ll trajectory,
pi, covs, Chat), their mtimes vs the freeze commit time, logs/tb2_post_SRP.{log,sel}, logs/tb2.log (SRP job lines), the sigma grid,
the manifests, the run logs' timing lines, and the git commit times.  Also answers the audit question about "n_iter 21 / it_best 0":
which stopping rule of gmm_em_gpu.fit_gmm_em_gpu fired (validation patience vs the train-ll tolerance rule), and what the selected
b* model actually is (initial seeds: cov_k - 0.5 Chat rank-1, uniform pi, not Kronecker-structured).

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_path_s5.py > results/review_next/prereg_audit_2026-10-11/recompute_path_s5.out
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
FITS = os.path.join(CONF, "results/gmm_fits_D2_SRPB16e4")
KST = dt.timezone(dt.timedelta(hours=9))
FREEZE = dt.datetime(2026, 10, 12, 2, 26, 27, tzinfo=KST)        # 45c4ae07, = 10-11 12:26:27 CDT
TOL, PATIENCE, VAL_EVERY = 1e-6, 40, 10                           # gmm_em_gpu.fit_gmm_em_gpu defaults (fit_gpu passes neither)

# §5 fits table as transcribed (family, K): (ll_val 3 dp or full, restart, n_iter, it_best, reseed, kappa)
EXP_FULL = {16: (215.543, 0, 21, 0, 120, 256), 32: (220.594, 2, 21, 0, 268, 16), 64: (226.189, 2, 21, 0, 557, 256),
            128: (230.616, 1, 21, 0, 1160, 16), 256: (234.869, 1, 21, 0, 2377, 64), 512: (237.957, 1, 22, 0, 5091, 64)}
EXP_KRON = {16: (214.940, 1, 41, 0, 0, 0), 32: (220.874, 1, 21, 0, 272, 0), 64: (225.439, 0, 21, 0, 547, 0),
            128: (230.241, 1, 21, 0, 1112, 0), 256: (234.306, 1, 21, 0, 2297, 0), 512: (238.038, 2, 21, 0, 4657, 0),
            1024: (240.37008757768405, 2, 21, 0, 9406, 0), 2048: (242.5206415698816, 1, 21, 0, 18956, 0), 4096: (244.1932863626755, 1, 21, 0, 38140, 0)}
EXP_CAND = {1024: [(240.002, 21, 0, 9384), (240.320, 21, 0, 9394), (240.370, 21, 0, 9406)],
            2048: [(242.500, 22, 0, 20480), (242.521, 21, 0, 18956), (242.288, 21, 0, 18919)],
            4096: [(244.180, 21, 0, 38116), (244.193, 21, 0, 38140), (244.165, 21, 0, 38137)]}
EXP_MERGE_MTIME = {1024: "03:13:14", 2048: "03:13:19", 4096: "03:13:25"}            # KST (= 13:13:xx CDT)
EXP_CAND4096_MTIME = ["03:06:16", "03:08:54", "03:11:32"]
EXP_SIGMA = (3.2222439954229846e-02, 7.932042156975202e-01, 20)

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
    p("# recompute_path_s5.py -- §5 fits table / selection / timeline / stop-rule analysis")
    p("\n## 1. fits table vs the npz files (final files; candidates for K >= 1024)")
    files = sorted(glob.glob(os.path.join(FITS, "*.npz")))
    chk("24 fit files (6 full + 6 kron + 9 candidates + 3 merged)", len(files), 24)
    maxit = 0
    stop_rows = []
    for fam, exp in (("full", EXP_FULL), ("kron", EXP_KRON)):
        for K, e in exp.items():
            f = os.path.join(FITS, f"fit_SRP_Nr8_{fam}K{K}_n160000.npz")
            z = np.load(f, allow_pickle=True)
            got = (float(z["ll_val"]), int(z["restart"]), int(z["n_iter"]), int(z["it_best"]), int(z["n_reseed"]), int(z["kappa"]))
            p(f"  {fam} {K:5d}: ll_val {got[0]:.6f} r{got[1]} n_iter {got[2]} it_best {got[3]} reseed {got[4]} kappa {got[5]}  mtime {mt(f).strftime('%m-%d %H:%M:%S KST')}")
            chk(f"{fam} {K} ll_val", round(got[0], 3) if K < 1024 else got[0], e[0], 0 if K >= 1024 else 0.0006)
            chk(f"{fam} {K} (restart, n_iter, it_best, reseed, kappa)", got[1:], e[1:])
            chk(f"{fam} {K} file mtime after the freeze (02:26:27 KST)", mt(f) > FREEZE, True)
            maxit = max(maxit, got[2])
            ll = np.asarray(z["ll"], float)
            last = len(ll) - 1
            tol_rule = last >= 20 and (ll[-1] - ll[-2] < TOL * abs(ll[-1]))
            pat_rule = (last % VAL_EVERY == 0) and (last - int(z["it_best"]) >= PATIENCE)
            stop_rows.append((fam, K, last, int(z["it_best"]), tol_rule, pat_rule, ll[0], ll[1] if len(ll) > 1 else np.nan, ll[-2], ll[-1], ll.max(), int(np.argmax(ll))))
            if K >= 1024:
                cands = []
                for r in range(3):
                    zc = np.load(os.path.join(FITS, f"fit_SRP_Nr8_kronK{K}_n160000.k0r{r}.npz"), allow_pickle=True)
                    cands.append((round(float(zc["ll_val"]), 3), int(zc["n_iter"]), int(zc["it_best"]), int(zc["n_reseed"])))
                chk(f"kron {K} candidates (ll_val 3 dp, n_iter, it_best, reseed)", cands, EXP_CAND[K])
                chk(f"kron {K} merged cand_ll_val == candidates", [round(float(v), 3) for v in z["cand_ll_val"]], [c[0] for c in EXP_CAND[K]])
                chk(f"kron {K} selected = argmax cand_ll_val", int(np.argmax(z["cand_ll_val"])), int(z["restart"]))
                chk(f"kron {K} merged mtime (KST)", mt(f).strftime("%H:%M:%S"), EXP_MERGE_MTIME[K])
            if K == 4096:
                chk("kron 4096 candidate mtimes (KST)", [mt(os.path.join(FITS, f"fit_SRP_Nr8_kronK4096_n160000.k0r{r}.npz")).strftime("%H:%M:%S") for r in range(3)], EXP_CAND4096_MTIME)
    chk("max n_iter over all files = 41", maxit, 41)
    chk("full-family best is 512 (237.957) and b* = kron 4096 > kron 2048 > full 512", (max(EXP_FULL, key=lambda k: EXP_FULL[k][0]), EXP_KRON[4096][0] > EXP_KRON[2048][0] > EXP_FULL[512][0]), (512, True))
    chk("§5 '2048 대비 +1.673 nat'", round(EXP_KRON[4096][0] - EXP_KRON[2048][0], 3), 1.673)
    chk("b* = kron 2048 on the base grid (edge) -> 4096 merged -> stop (grid rule)", EXP_KRON[2048][0] > max(EXP_KRON[k][0] for k in EXP_KRON if k < 2048), True)
    for f in files:
        chk(f"mtime after freeze: {os.path.basename(f)}", mt(f) > FREEZE, True)
    sel = open(os.path.join(CONF, "logs/tb2_post_SRP.sel")).read().strip()
    chk("tb2_post_SRP.sel", sel, "kron 4096 244.1932863626755")
    chk(".sel mtime after freeze", mt(os.path.join(CONF, "logs/tb2_post_SRP.sel")) > FREEZE, True)
    chk("gmm_fits_D2_SRPB16e4last is a symlink to gmm_fits_D2_SRPB16e4", os.readlink(os.path.join(CONF, "results/gmm_fits_D2_SRPB16e4last")), "gmm_fits_D2_SRPB16e4")

    p("\n## 2. which stopping rule fired (gmm_em_gpu: val every 10 it, patience 40 on it_best; train-ll tol rule from it >= 20)")
    p("  fam  K      last_it it_best  tol_rule  patience_rule   ll[0]      ll[1]      ll[-2]     ll[-1]     max(ll) @it")
    n_tol = n_pat = 0
    for fam, K, last, ib, tr, pr, l0, l1, lm2, lm1, lmax, imax in stop_rows:
        p(f"  {fam:4s} {K:5d}  {last:5d}   {ib:3d}     {str(tr):5s}     {str(pr):5s}       {l0:9.3f}  {l1:9.3f}  {lm2:9.3f}  {lm1:9.3f}  {lmax:9.3f} @{imax}")
        n_tol += tr; n_pat += pr
    p(f"  -> stopped by the train-ll tolerance rule (ll[-1]-ll[-2] < tol*|ll|, i.e. train ll fell or stalled at it >= 20): {n_tol} of {len(stop_rows)};"
      f" by validation patience ((it - it_best) >= 40 at a validation iteration): {n_pat}")
    chk("every fit has it_best = 0", all(ib == 0 for _, _, _, ib, *_ in stop_rows), True)
    chk("train ll at it 0 (initialisation) is the maximum of the train trajectory in every fit", all(imax == 0 for *_, imax in stop_rows), True)
    chk("stops: 14 fits by the train-ll tolerance rule at it 20/21, kron 16 by patience at it 40", (n_tol, n_pat), (14, 1))

    p("\n## 3. what the selected b* (kron 4096, it_best 0) is: pi, covs structure")
    z = np.load(os.path.join(FITS, "fit_SRP_Nr8_kronK4096_n160000.npz"), allow_pickle=True)
    pi, covs, Chat = z["pi"], z["covs"], z["Chat"]
    chk("pi uniform 1/4096", bool(np.allclose(pi, 1 / 4096)), True)
    Nr, Nt = 8, 4
    rk1, kron_ratio = [], []
    rng = np.random.default_rng(0)
    for k in rng.choice(4096, 64, replace=False):
        D = covs[k] - 0.5 * Chat
        s = np.linalg.svd(D, compute_uv=False); rk1.append(s[1] / s[0])
        R = covs[k].reshape(Nt, Nr, Nt, Nr).transpose(0, 2, 1, 3).reshape(Nt * Nt, Nr * Nr)
        sv = np.linalg.svd(R, compute_uv=False); kron_ratio.append(sv[1] / sv[0])
    p(f"  64 random components: max s2/s1 of (cov_k - 0.5 Chat) = {max(rk1):.2e} (rank-1 => seed_cov structure 0.5 Chat + 0.5 c s s^H);"
      f" Kronecker rearrangement s2/s1 min/median/max = {min(kron_ratio):.3f} / {np.median(kron_ratio):.3f} / {max(kron_ratio):.3f} (1 - 0 would mean kron(T, R))")
    chk("cov_k - 0.5 Chat is rank-1 for every sampled component (= the initial seed covariances)", max(rk1) < 1e-10, True)
    chk("covariances are NOT Kronecker-structured (rearrangement s2/s1 > 0.05 for every sampled component)", min(kron_ratio) > 0.05, True)
    ll = np.asarray(z["ll"], float)
    p(f"  train ll trajectory of the selected candidate: it0 {ll[0]:.3f}, it1 {ll[1]:.3f}, then oscillating {ll[2:].min():.2f}..{ll[2:].max():.2f}; ll_val (init) {float(z['ll_val']):.4f}, gauss_val {float(z['gauss_val']):.4f}, ll_train stored {float(z['ll_train']):.4f}")
    chk("stored ll_train == ll[it_best] == ll[0]", (abs(float(z["ll_train"]) - ll[0]) < 1e-9), True)

    p("\n## 4. sigma grid, manifests, commit times, run-log timing lines")
    sg = np.load(os.path.join(CONF, "results/sigma_grid_D2_SRP.npz"))
    chk("sigma grid 20 points, endpoints", (float(sg["sigma"].min()), float(sg["sigma"].max()), int(sg["sigma"].size)), EXP_SIGMA)
    for tag, egit, ecfg in (("SRPB16e4", "99039ef5", "3e6061f4e4f2b4f6"), ("SRPB16e4last", "99039ef5", "3e6061f4e4f2b4f6"),
                            ("PILSRP", "9ad4caa0", None), ("ALDSRP", "9ad4caa0", None), ("SPSRP", "9ad4caa0", None)):
        m = json.load(open(os.path.join(CONF, f"results/review_next/run_manifest_{tag}.json")))
        p(f"  manifest {tag}: git {m['git_commit']} config_hash {m['config_hash']} n_raw {m['n_raw_files']} written {m['written']} Demo {m['code_hashes'] if isinstance(m['code_hashes'], str) else m['code_hashes'].get('Demo')}")
        chk(f"manifest {tag} git", m["git_commit"], egit)
        chk(f"manifest {tag} n_raw_files", m["n_raw_files"], 448)
        if ecfg:
            chk(f"manifest {tag} config_hash", m["config_hash"], ecfg)
    git = subprocess.run(["git", "show", "-s", "--format=%h %ci", "45c4ae07", "99039ef5", "9ad4caa0"], cwd=CONF, capture_output=True, text=True).stdout.split("\n")
    p("  commits: " + " | ".join(g for g in git if g))
    t = {g.split()[0]: dt.datetime.strptime(" ".join(g.split()[1:3]), "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST) for g in git if g}
    chk("freeze commit time == 10-11 12:26:27 CDT", t["45c4ae07"], FREEZE)
    first_best = min(mt(f) for f in glob.glob(os.path.join(CONF, "raw_SRPB16e4/*.npz")))
    first_pil = min(mt(f) for f in glob.glob(os.path.join(CONF, "raw_PILSRP/*.npz")))
    last_sp = max(mt(f) for f in glob.glob(os.path.join(CONF, "raw_SPSRP/*.npz")))
    p(f"  first raw_SRPB16e4 chunk {first_best.strftime('%H:%M:%S KST')} (run commit 99039ef5 at {t['99039ef5'].strftime('%H:%M:%S KST')}); first raw_PILSRP chunk {first_pil.strftime('%H:%M:%S KST')} (commit 9ad4caa0 at {t['9ad4caa0'].strftime('%H:%M:%S KST')}); last raw_SPSRP chunk {last_sp.strftime('%H:%M:%S KST')}")
    chk("main run raws written after the run commit 99039ef5", first_best > t["99039ef5"], True)
    chk("baseline raws written after the commit 9ad4caa0", first_pil > t["9ad4caa0"], True)
    chk("commit 9ad4caa0 after PRIOR_EVAL_DONE (15:05 CDT = 05:05 KST) and before the baseline start (05:06 KST log line)", dt.datetime(2026, 10, 12, 5, 5, 0, tzinfo=KST) < t["9ad4caa0"] < dt.datetime(2026, 10, 12, 5, 7, 0, tzinfo=KST), True)
    for tag, emin in (("SRPB16e4", 53.2), ("SRPB16e4last", 41.2), ("PILSRP", 2.0), ("ALDSRP", 0.4), ("SPSRP", 10.7)):
        log = open(os.path.join(CONF, f"logs/run_D2_{tag}.log")).read()
        done = len(re.findall(r"^\s*\d+/448 done", log, re.M)); exists = log.count("exists")
        fin = re.search(r"finished in ([\d.]+) min", log)
        chk(f"run_D2_{tag}.log: 448 done lines, no 'exists', finished in {emin} min", (done, exists, float(fin.group(1)) if fin else None), (448, 0, emin))
    pe = open(os.path.join(CONF, "logs/run_prior_eval_SRPB16e4.log")).read()
    chk("prior_eval log: start 13:29, measurement done 14:22, last done 15:04, acceptance rc=0 15:05, PRIOR_EVAL_DONE 15:05 (CDT)",
        all(s in pe for s in ("10-11 13:29 CDT] start (git 99039ef5)", "10-11 14:22 CDT] run SRPB16e4 (measurement) done", "10-11 15:04 CDT] SRPB16e4last done",
                              "10-11 15:05 CDT] acceptance rc=0 (ACCEPT: OK -- SRPB16e4, SRPB16e4last)", "10-11 15:05 CDT] PRIOR_EVAL_DONE")), True)
    chk("prior_eval log: exactly one start line (ran once)", pe.count("] start (git"), 1)
    sb = open(os.path.join(CONF, "logs/run_srp_base.log")).read()
    chk("srp_base log: one start line, 15:06 CDT, git 9ad4caa0, pick / ald_tune shas", (sb.count("] start (git"), "[srp_base 10-11 15:06 CDT] start (git 9ad4caa0) ckpt=d2sx_SRP_N160000_a1 best=ac4699c78b3e2d80 pick=6ae22a15de019833 ald_tune=858087f53952bcbf" in sb), (1, True))
    chk("srp_base log: PIL 15:08 / ALD 15:10 / SP 15:21 ACCEPT OK, pair_baselines rc=0, SRP_BASE_DONE rc=0 15:21",
        all(s in sb for s in ("15:08 CDT] PIL acceptance (ACCEPT: OK -- PILSRP)", "15:10 CDT] ALD acceptance (ACCEPT: OK -- ALDSRP)", "15:21 CDT] SP acceptance (ACCEPT: OK -- SPSRP)",
                              "15:21 CDT] pair_baselines rc=0", "15:21 CDT] SRP_BASE_DONE rc=0", "rule-reproduced=True", "memory need ~264 GB, available 1028 GB", "ALD estimate on GPU 2 done")), True)
    tb = open(os.path.join(CONF, "logs/tb2.log")).read()
    starts = re.findall(r"\[tb2 10-11 (\d\d:\d\d) CDT\] GPU 0 start: code/fit_gpu(?:_batched)?\.py 8 \w+ \d+ 160000 SRPB16e4", tb)
    dones = re.findall(r"\[tb2 10-11 (\d\d:\d\d) CDT\] GPU 0 done rc=(\d+): code/fit_gpu(?:_batched)?\.py 8 \w+ \d+ 160000 SRPB16e4", tb)
    chk("tb2.log: 21 SRP fit jobs on GPU 0, 12:44 -> 13:11 CDT, all rc=0", (len(starts), starts[0], dones[-1][0], all(d[1] == "0" for d in dones)), (21, "12:44", "13:11", True))
    chk("tb2.log: SRP training 12:11 start, patience stop 13:12 CDT", ("10-11 12:11 CDT] GPU 2 start: @train SRP SRPB16e4" in tb and "10-11 13:12 CDT] train SRP fallback 1: stopped_by=patience" in tb), True)
    chk("tb2.log: stop-file NOTE lines 13:13 / 13:23 and TB2_QUEUE_DONE 13:20 (§5 '실행 사실' (2))", all(s in tb for s in ("[tb2 10-11 13:13 CDT] NOTE: stop file set", "[tb2 10-11 13:23 CDT] NOTE: stop file removed", "[tb2 10-11 13:20 CDT] TB2_QUEUE_DONE")), True)
    ps = open(os.path.join(CONF, "logs/tb2_post_SRP.log")).read()
    chk("tb2_post_SRP.log: freeze check, select 2048 -> 4096 -> stop, ALD tune 13:17 -> 13:28 rc=0, GB' resume 14:07 on GPU 1",
        all(s in ps for s in ("13:13 CDT] freeze 45c4ae07 (10-11 12:26:27 CDT) done", "SELECT b* = kron kron_K = 2048", "b* = kron 2048 = base-grid edge -> merge kron 4096 (registered rule; STOP at 4096)",
                              "SELECT b* = kron kron_K = 4096 ll_val = 244.1932863626755", "13:17 CDT] ALD dev regen (CPU) + tune on GPU 0 (ckpt d2sx_SRP_N160000_a1, git 45c4ae07)", "13:28 CDT] ALD tune rc=0", "14:07 CDT] GB' resume on GPU 1")), True)
    st = open(os.path.join(CONF, "logs/sparse_tune.log")).read()
    chk("sparse_tune.log: SRP start 12:11 (git ce5fdacc), SPARSE_TUNE_DONE rc=0 14:38 CDT", ("[sparse_tune SRP 10-11 12:11 CDT] start (git ce5fdacc)" in st and "[sparse_tune SRP 10-11 14:38 CDT] SPARSE_TUNE_DONE rc=0" in st), True)
    chk("pick_SRP_C2.json mtime 04:38 KST (= 14:38 CDT), after the judged tag ended (14:22 CDT)", mt(os.path.join(CONF, "results/sparse/pick_SRP_C2.json")).strftime("%H:%M"), "04:38")
    chk("tune_PILSRP.json mtime 03:28 KST (= 13:28 CDT), after the freeze", mt(os.path.join(CONF, "results/ald/tune_PILSRP.json")).strftime("%H:%M"), "03:28")
    chk("ckpt mtimes best 03:10 / last 03:12 KST (12:11 -> 13:12 CDT training)", (mt(os.path.join(CONF, "ckpt/d2sx_SRP_N160000_a1_best.pt")).strftime("%H:%M"), mt(os.path.join(CONF, "ckpt/d2sx_SRP_N160000_a1.pt")).strftime("%H:%M")), ("03:10", "03:12"))
    chk("tb2_train_state_SRP.txt = '1 patience'", open(os.path.join(CONF, "logs/tb2_train_state_SRP.txt")).read().strip(), "1 patience")
    d1 = subprocess.run(["git", "diff", "--stat", "45c4ae07", "99039ef5", "--", "conf/code", "Demo"], cwd="/home/HTJ/t2", capture_output=True, text=True).stdout
    d2 = subprocess.run(["git", "diff", "--stat", "99039ef5", "9ad4caa0", "--", "conf/code", "Demo"], cwd="/home/HTJ/t2", capture_output=True, text=True).stdout
    chk("git diff 45c4ae07..99039ef5 -- conf/code Demo touches only run_srp_eval.sh", ("run_srp_eval.sh" in d1 and "1 file changed" in d1), True)
    chk("git diff 99039ef5..9ad4caa0 -- conf/code Demo touches only run_srb_eval.sh", ("run_srb_eval.sh" in d2 and "1 file changed" in d2), True)
    for tag in ("SRPB16e4", "SRPB16e4last"):
        tt = open(os.path.join(CONF, f"results/tables_D2_{tag}.txt")).read()
        chk(f"tables_D2_{tag}: banner strings once each, sparse-specular banner absent", (tt.count("SITE-SPECIFIC RAY-TRACED TESTBED (prior SRP)"), tt.count("ONE UE MOVING along a lawn-mower route"), tt.count("CLAIM TESTBED -- sparse specular")), (1, 1, 0))
        chk(f"tables_D2_{tag}: git 99039ef5, prior SRP, N_train=160000 lines, b*=kron 4096", ("# git commit  : 99039ef5" in tt and "prior SRP" in tt and tt.count("N_train=160000") >= 12 and "b*=kron (kron K=4096)" in tt), True)
    chk("GB' not claimed: record has no numeric GB' value (checked by reading §6.2 line) -- manual", True, True)

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
