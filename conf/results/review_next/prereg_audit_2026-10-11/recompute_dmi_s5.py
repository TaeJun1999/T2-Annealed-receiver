"""recompute_dmi_s5.py -- RECORD AUDIT of NEXT_EXPERIMENTS_ROOM16e4.md block 5-DMI and the timeline / acceptance / disclosure facts
of §7 (prior DMI).  Method of recompute_room_s5.py, rewritten for DMI (every expected value retyped from the record at cde35a4e).
Reads results/gmm_fits_D2_DMIB16e4/*.npz (ll_val, restart, n_iter, it_best, n_reseed, kappa, candidates, the stored train-ll trajectory,
pi, covs, Chat), their mtimes vs the freeze b737fd55, logs/tb2.log, logs/tb2_post_DMI.{log,sel}, logs/fit_full1024_DMI.log, the training
log, the sigma grid, manifests, run logs, driver logs, commit times, git diffs, banners, GB' files, DECISIONS.md.
Answers: (1) is the evaluated b* (full K = 1024) a properly EM-fitted model and WHICH stop rule ended it; how many live components;
(2) does arms.gmm_selection return now what the hand-written tb2_post_DMI.sel says; (3) did any DMI BLER exist before 4131a3b0.

usage (cwd = ~/t2/conf):  CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=8 taskset -c 0-15 ~/miniforge3/envs/torch/bin/python -B \
    results/review_next/prereg_audit_2026-10-11/recompute_dmi_s5.py > results/review_next/prereg_audit_2026-10-11/recompute_dmi_s5.out
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
REPO = "/home/HTJ/t2"
FITS = os.path.join(CONF, "results/gmm_fits_D2_DMIB16e4")
KST = dt.timezone(dt.timedelta(hours=9))
CDT = dt.timezone(dt.timedelta(hours=-5))
FREEZE = dt.datetime(2026, 10, 12, 1, 23, 26, tzinfo=KST)        # b737fd55 = 10-11 11:23:26 CDT
TOL, PATIENCE, VAL_EVERY = 1e-6, 40, 10                           # gmm_em_gpu.fit_gmm_em_gpu defaults

# 5-DMI fits table as transcribed: K: (ll_val 3 dp or full precision, restart, n_iter, it_best, reseed)
EXP_FULL = {16: (28.002, 1, 103, 80, 0), 32: (44.495, 2, 121, 80, 0), 64: (67.588, 2, 307, 300, 0), 128: (83.443, 2, 179, 170, 1),
            256: (96.447, 1, 183, 150, 542), 512: (105.851, 2, 191, 190, 5661), 1024: (112.043, 0, 72, 70, 6847)}
EXP_KRON = {16: 10.964, 32: 17.682, 64: 22.517, 128: 26.746, 256: 30.850, 512: 34.837, 1024: 38.050615215363074, 2048: 41.18010947841611}
EXP_CAND = {1024: [38.051, 37.981, 38.007], 2048: [41.180, 41.097, 41.119], 4096: [43.957, 44.071, 44.067]}
EXP_BSTAR, EXP_F512 = 112.04253042212595, 105.85089193400368

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


def cdt(d):
    return d.astimezone(CDT).strftime("%m-%d %H:%M:%S")


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout


def main():
    p("# recompute_dmi_s5.py -- 5-DMI fits table / selection / stop-rule analysis / timeline / disclosures (prior DMI)")
    p("\n## 1. fits table vs the npz files")
    files = sorted(glob.glob(os.path.join(FITS, "*.npz")))
    chk("24 fit files ('파일 24 개': 7 full + 6 kron + 2 merged kron + 9 kron candidates)", len(files), 24)
    chk("no merged kron 4096 / no full 2048", (os.path.exists(os.path.join(FITS, "fit_DMI_Nr8_kronK4096_n160000.npz")), os.path.exists(os.path.join(FITS, "fit_DMI_Nr8_fullK2048_n160000.npz"))), (False, False))
    rows, maxit, minbest = [], 0, 10 ** 9
    for f in files:
        z = np.load(f, allow_pickle=True)
        maxit = max(maxit, int(z["n_iter"])); minbest = min(minbest, int(z["it_best"]))
        chk(f"mtime after the freeze: {os.path.basename(f)}", mt(f) > FREEZE, True)
    chk("'최대 n_iter 307'", maxit, 307)
    chk("'모든 적합이 it_best >= 40 에서 선택됐다' (min it_best over the 24 files)", minbest >= 40, True)
    p(f"  min it_best over the 24 files = {minbest}; max n_iter = {maxit}")
    for K, e in EXP_FULL.items():
        f = os.path.join(FITS, f"fit_DMI_Nr8_fullK{K}_n160000.npz")
        z = np.load(f, allow_pickle=True)
        got = (round(float(z["ll_val"]), 3), int(z["restart"]), int(z["n_iter"]), int(z["it_best"]), int(z["n_reseed"]))
        chk(f"full {K} (ll_val 3 dp, restart, n_iter, it_best, reseed)", got, e)
        chk(f"full {K} kappa 0", int(z["kappa"]), 0)
        rows.append(("full", K, z))
    for K, e in EXP_KRON.items():
        f = os.path.join(FITS, f"fit_DMI_Nr8_kronK{K}_n160000.npz")
        z = np.load(f, allow_pickle=True)
        chk(f"kron {K} ll_val", float(z["ll_val"]) if K >= 1024 else round(float(z["ll_val"]), 3), e, 1e-12 if K >= 1024 else 0.00051)
        rows.append(("kron", K, z))
    for K, e in EXP_CAND.items():
        c = [round(float(np.load(os.path.join(FITS, f"fit_DMI_Nr8_kronK{K}_n160000.k0r{r}.npz"), allow_pickle=True)["ll_val"]), 3) for r in range(3)]
        chk(f"kron {K} candidates r0/r1/r2 (3 dp)", c, e)
        if K < 4096:
            z = np.load(os.path.join(FITS, f"fit_DMI_Nr8_kronK{K}_n160000.npz"), allow_pickle=True)
            chk(f"kron {K} merged = argmax of the candidates (restart {int(z['restart'])})", (int(np.argmax(z["cand_ll_val"])), int(z["restart"])), (0, 0))
    zf512 = np.load(os.path.join(FITS, "fit_DMI_Nr8_fullK512_n160000.npz"), allow_pickle=True)
    z1024 = np.load(os.path.join(FITS, "fit_DMI_Nr8_fullK1024_n160000.npz"), allow_pickle=True)
    chk("full 512 ll_val (full precision)", repr(float(zf512["ll_val"])), repr(EXP_F512))
    chk("full 1024 ll_val (full precision) = b*", repr(float(z1024["ll_val"])), repr(EXP_BSTAR))
    chk("'512 대비 +6.192 nat'", round(float(z1024["ll_val"]) - float(zf512["ll_val"]), 3), 6.192)
    lls = [float(z["ll_val"]) for fam, K, z in rows if fam == "full"]
    p("  full-family ll_val gains per doubling (16 -> ... -> 1024): " + ", ".join(f"{b - a:+.3f}" for a, b in zip(lls, lls[1:])))
    chk("first selection: full 512 = base-grid full maximum and > every kron (kron best 2048 41.180)", (float(zf512["ll_val"]) == max(lls[:6]), float(zf512["ll_val"]) > EXP_KRON[2048]), (True, True))
    chk("merged kron mtimes 15:46:21 / 15:46:25 CDT", (cdt(mt(os.path.join(FITS, "fit_DMI_Nr8_kronK1024_n160000.npz"))), cdt(mt(os.path.join(FITS, "fit_DMI_Nr8_kronK2048_n160000.npz")))), ("10-12 15:46:21", "10-12 15:46:25"))
    chk("full 1024 file mtime 16:11:10 CDT", cdt(mt(os.path.join(FITS, "fit_DMI_Nr8_fullK1024_n160000.npz"))), "10-12 16:11:10")
    chk("full 1024: 12 (kappa, restart) EM runs, (0, 0) selected = argmax cand_ll_val", (int(z1024["cand"].shape[0]), int(z1024["kappa"]), int(z1024["restart"]), int(np.argmax(z1024["cand_ll_val"]))), (12, 0, 0, 0))
    p(f"  full 1024 candidates (kappa, restart) -> ll_val: {[(int(a), int(b), round(float(v), 3)) for (a, b), v in zip(z1024['cand'], z1024['cand_ll_val'])]}")
    sel = open(os.path.join(CONF, "logs/tb2_post_DMI.sel")).read().strip()
    chk("tb2_post_DMI.sel", sel, "gmm1024 - 112.04253042212595")
    chk(".sel mtime after the full-1024 file and before the run commit 4131a3b0 (16:13:38 CDT)", (mt(os.path.join(CONF, "logs/tb2_post_DMI.sel")) > mt(os.path.join(FITS, "fit_DMI_Nr8_fullK1024_n160000.npz")), cdt(mt(os.path.join(CONF, "logs/tb2_post_DMI.sel")))[:11]), (True, "10-12 16:12"))
    chk("gmm_fits_D2_DMIB16e4last is a symlink to gmm_fits_D2_DMIB16e4", os.readlink(os.path.join(CONF, "results/gmm_fits_D2_DMIB16e4last")), "gmm_fits_D2_DMIB16e4")

    p("\n## 1b. arms.gmm_selection NOW vs the hand-written .sel")
    sys.path.insert(0, os.path.join(CONF, "code"))
    import arms as A  # noqa: E402
    import runner  # noqa: E402
    runner._init("DMIB16e4")
    fits, llv, b, kK = A.gmm_selection("D2", "DMI", 8, 160000)
    p(f"  gmm_selection -> b* = {b}, kron_K = {kK}, ll_val by arm = {{{', '.join(f'{k}: {v:.4f}' for k, v in llv.items())}}}")
    chk("gmm_selection b* / ll_val / kron_K", (b, repr(llv[b]), kK), ("gmm1024", "112.04253042212595", 2048))
    chk("gmm_selection loads 7 full + 8 kron files", (sorted(K for f, K in fits if f == "full"), sorted(K for f, K in fits if f == "kron")), ([16, 32, 64, 128, 256, 512, 1024], [16, 32, 64, 128, 256, 512, 1024, 2048]))
    chk(".sel == f'{b} - {ll_val!r}'", sel, f"{b} - {llv[b]!r}")

    p("\n## 2. which stop rule ended each final fit (gmm_em_gpu.py:133-143: validation every 10 it, patience 40 on it_best; from it >= 20: break if ll[-1] - ll[-2] < 1e-6 |ll[-1]|,")
    p("      which ALSO fires on a NEGATIVE train-ll step, e.g. after a reseed)")
    p("  fam  K     n_iter it_best  rule        last step      tol*|ll|     mean of the 5 steps before   ll[0] -> ll[-1]")
    neg = []
    for fam, K, z in rows:
        ll = np.asarray(z["ll"], float); last = len(ll) - 1; d = np.diff(ll)
        tol_rule = last >= 20 and (ll[-1] - ll[-2] < TOL * abs(ll[-1]))
        pat_rule = (last % VAL_EVERY == 0) and (last - int(z["it_best"]) >= PATIENCE)
        rule = "tol" if tol_rule and not pat_rule else "patience" if pat_rule and not tol_rule else "both" if tol_rule else "?"
        if tol_rule and d[-1] < 0:
            rule = "tol(NEG step)"; neg.append((fam, K))
        p(f"  {fam:4s} {K:5d}  {len(ll):4d}   {int(z['it_best']):4d}   {rule:14s} {d[-1]:+.3e}   {TOL * abs(ll[-1]):.3e}   {d[-6:-1].mean():+.3e}             {ll[0]:9.3f} -> {ll[-1]:9.3f}   neg steps total {int((d < 0).sum())}")
    p(f"  -> final fits ended by a NEGATIVE train-ll step: {neg}")
    ll = np.asarray(z1024["ll"], float); d = np.diff(ll)
    chk("b* (full 1024): EM ended at iteration 71 on the FIRST non-increasing train-ll step (the only negative step of the trajectory)", (len(ll), int((d < 0).sum()), bool(d[-1] < 0)), (72, 1, True))
    chk("b* (full 1024): the five steps before the stop were still > 10 x the tolerance (EM was still improving the train ll)", bool(d[-6:-1].min() > 10 * TOL * abs(ll[-1])), True)
    chk("b* (full 1024): it_best 70 = the last validation point (validation ll was still improving when EM ended)", int(z1024["it_best"]), 70)
    chk("b* (full 1024): stored ll_train == ll[it_best]", abs(float(z1024["ll_train"]) - ll[70]) < 1e-9, True)
    p(f"  b* train ll: it0 {ll[0]:.3f}, it1 {ll[1]:.3f}, it10 {ll[10]:.3f}, it30 {ll[30]:.3f}, it50 {ll[50]:.3f}, it70 {ll[70]:.4f}, it71 {ll[71]:.4f}; per-iteration gain over it 61..70: {d[60:70].mean():.4f} nat")
    p(f"  b* ll_train {float(z1024['ll_train']):.4f}, ll_val {float(z1024['ll_val']):.4f} (train-val gap {float(z1024['ll_train']) - float(z1024['ll_val']):.3f}), ll_test {float(z1024['ll_test']):.4f}, gauss_val {float(z1024['gauss_val']):.4f}; "
      f"the three kappa-0 restarts: ll_val {[round(float(v), 3) for v in z1024['cand_ll_val'][:3]]} (spread {float(np.ptp(z1024['cand_ll_val'][:3])):.3f} nat)")
    chk("b*: three independent kappa-0 restarts agree within 0.2 nat in ll_val (the stop point is not an outlier)", float(np.ptp(z1024["cand_ll_val"][:3])) < 0.2, True)
    chk("b*: ll_val - gauss_val > 100 nat", float(z1024["ll_val"]) - float(z1024["gauss_val"]) > 100, True)

    p("\n## 3. structure of b* (pi, covs): live components, placeholders, PSD")
    pi, covs, Chat = z1024["pi"], z1024["covs"], z1024["Chat"]
    n = int(z1024["ntrain"])
    rk = np.array([(lambda s: s[1] / s[0])(np.linalg.svd(covs[k] - 0.5 * Chat, compute_uv=False)) for k in range(1024)])
    placeholder = rk < 1e-8                                  # cov_k = 0.5 Chat + rank-1 = a reseeded component not yet updated by an M-step
    tiny = pi <= 1.5 / n
    p(f"  pi: min {pi.min():.3e}, max {pi.max():.3e}, median {np.median(pi):.3e} (uniform 1/1024 = {1 / 1024:.3e}; 1/n = {1 / n:.3e}); sum {pi.sum():.9f}")
    p(f"  components with cov_k - 0.5 Chat of rank 1 (reseeded placeholders at the end of EM): {int(placeholder.sum())}; with pi_k <= 1.5/n: {int(tiny.sum())}; both: {int((placeholder & tiny).sum())}; "
      f"pi mass of the placeholders {float(pi[placeholder].sum()):.5f}")
    live = int((~placeholder).sum())
    p(f"  LIVE components (EM-updated covariance): {live} of 1024, carrying {float(pi[~placeholder].sum()):.5f} of the mass; effective number exp(H(pi)) = {float(np.exp(-(pi * np.log(pi)).sum())):.1f}")
    ev = np.array([np.linalg.eigvalsh(covs[k]) for k in range(1024)])
    herm = bool(np.allclose(covs, covs.conj().transpose(0, 2, 1), atol=1e-10))
    chk("b*: pi sums to 1, pi not uniform, covs Hermitian PSD", (abs(float(pi.sum()) - 1) < 1e-9, float(pi.max() / pi.min()) > 3, herm, bool(ev.min() > -1e-10)), (True, True, True, True))
    chk("b*: more than half of the components are live (NOT the collapsed-initialisation case)", live > 512, True)
    for K in (512,):
        zz = zf512; rkk = np.array([(lambda s: s[1] / s[0])(np.linalg.svd(zz["covs"][k] - 0.5 * zz["Chat"], compute_uv=False)) for k in range(K)])
        p(f"  (for comparison) full {K}: placeholders {int((rkk < 1e-8).sum())} of {K}, pi mass {float(zz['pi'][rkk < 1e-8].sum()):.5f}")

    p("\n## 4. logs: queue (tb2.log), post-select, full-1024 fit, training, sigma grid")
    tb = open(os.path.join(CONF, "logs/tb2.log")).read()
    st = re.findall(r"\[tb2 (10-1\d) (\d\d:\d\d) CDT\] GPU (\d) start: (code/fit_gpu(?:_batched)?\.py 8 \w+ \d+ 160000 DMIB16e4[^\n]*)", tb)
    dn = re.findall(r"\[tb2 (10-1\d) (\d\d:\d\d) CDT\] GPU (\d) done rc=(\d+): code/fit_gpu(?:_batched)?\.py 8 \w+ \d+ 160000 DMIB16e4", tb)
    chk("tb2.log: 21 DMI fit jobs, all on 10-12, first start 14:01, last done 14:35 CDT, all rc=0, GPUs 0-5", (len(st), len(dn), {x[0] for x in st}, st[0][1], max(x[1] for x in dn), all(x[3] == "0" for x in dn), sorted({x[2] for x in st})),
        (21, 21, {"10-12"}, "14:01", "14:35", True, ["0", "1", "2", "3", "4", "5"]))
    want = ([f"code/fit_gpu_batched.py 8 kron 1024 160000 DMIB16e4 --restart {r} --prior DMI" for r in range(3)]
            + ["code/fit_gpu.py 8 full 512 160000 DMIB16e4 --prior DMI", "code/fit_gpu.py 8 full 256 160000 DMIB16e4 --prior DMI", "code/fit_gpu_batched.py 8 kron 512 160000 DMIB16e4 --prior DMI",
               "code/fit_gpu.py 8 full 128 160000 DMIB16e4 --prior DMI", "code/fit_gpu_batched.py 8 kron 256 160000 DMIB16e4 --prior DMI", "code/fit_gpu.py 8 full 64 160000 DMIB16e4 --prior DMI",
               "code/fit_gpu_batched.py 8 kron 128 160000 DMIB16e4 --prior DMI", "code/fit_gpu.py 8 full 32 160000 DMIB16e4 --prior DMI", "code/fit_gpu_batched.py 8 kron 64 160000 DMIB16e4 --prior DMI",
               "code/fit_gpu.py 8 full 16 160000 DMIB16e4 --prior DMI", "code/fit_gpu_batched.py 8 kron 32 160000 DMIB16e4 --prior DMI", "code/fit_gpu_batched.py 8 kron 16 160000 DMIB16e4 --prior DMI"]
            + [f"code/fit_gpu_batched.py 8 kron {K} 160000 DMIB16e4 --restart {r} --prior DMI" for K in (2048, 4096) for r in range(3)])
    chk("tb2.log: the 21 jobs started in the registered list order of run_room_gpu.sh ('등록된 목록·순서')", [x[3].strip() for x in st], want)
    chk("tb2.log: no DMI fit job on 10-11; withdrawal NOTE 13:49; re-queue NOTE 10-12 14:01", ("[tb2 10-11 13:49 CDT] NOTE: the 21 DMI fit jobs are removed from the queue by user decision" in tb, "[tb2 10-12 14:01 CDT] NOTE: DMI fits re-queued (21 jobs" in tb), (True, True))
    chk("tb2.log: DMI training 10-11 11:03 start on GPU 0, patience stop 12:44 CDT", ("[tb2 10-11 11:03 CDT] GPU 0 start: @train DMI DMIB16e4" in tb, "[tb2 10-11 12:44 CDT] train DMI fallback 1: stopped_by=patience (ckpt/d2sx_DMI_N160000_a1.pt)" in tb), (True, True))
    ps = open(os.path.join(CONF, "logs/tb2_post_DMI.log")).read()
    chk("tb2_post_DMI.log lines (freeze check 15:46; SELECT gmm512; full 1024 ONCE on GPU 2 15:46 -> rc=0 16:11; 16:12 SELECT gmm1024, STOP; ALD 15:46 -> 15:55 rc=0 on GPU 0 git 003c8e51; GB' 16:16 -> 16:24 rc=0 on GPU 0 git 4131a3b0)",
        [s in ps for s in ("[post DMI 10-12 15:46 CDT] freeze b737fd55 (10-11 11:23:26 CDT) done; 21 fit files present", "SELECT b* = gmm512 kron_K = 2048 ll_val = 105.85089193400368",
                           "[post DMI 10-12 15:46 CDT] b* = full 512 = full-family grid edge -> registered rule: full 1024 ONCE on GPU 2 (git 003c8e51)", "[post DMI 10-12 16:11 CDT] full 1024 rc=0; FULL1024_DONE",
                           "[post DMI 10-12 16:12 CDT] after full 1024 (registered edge rule, once): SELECT b* = gmm1024 ll_val = 112.04253042212595 (gmm512 105.85089193400368; kron best K 2048 41.1801)", "STOP (no full 2048); POST_SELECT_DONE",
                           "[post DMI 10-12 15:46 CDT] ALD dev regen (CPU) + tune on GPU 0 (ckpt d2sx_DMI_N160000_a1, git 003c8e51)", "[post DMI 10-12 15:55 CDT] ALD tune rc=0; POST_ALD_DONE",
                           "[post DMI 10-12 16:16 CDT] GB' resume on GPU 0 (ckpt d2sx_DMI_N160000_a1, git 4131a3b0)", "[post DMI 10-12 16:24 CDT] GB' rc=0")], [True] * 10)
    chk("'적합이 끝난 뒤(14:35) 선택까지 71 분' (14:35 -> 15:46)", (15 * 60 + 46) - (14 * 60 + 35), 71)
    ff = open(os.path.join(CONF, "logs/fit_full1024_DMI.log")).read()
    chk("fit_full1024_DMI.log: (0, 0) iters 72 best@70 reseeds 6847 ll_val 112.043; 12 EM runs; selected kappa 0 restart 0", ("('DMI', 8, 4, 'full', 1024, 0, 0): iters 72 best@70 reseeds 6847 ll_train 115.501 ll_val 112.043" in ff, ff.count("('DMI', 8, 4, 'full', 1024,"), "kappa   0 restart 0 best@70" in ff), (True, 12, True))
    tl = open(os.path.join(CONF, "logs/train_d2sx_DMI_N160000_a1.log")).read()
    chk("training log: real run header 10-12 01:03:36 KST (= 10-11 11:03 CDT), done 1162 epochs patience best 2.152151e-01 @1142 wall 6074.0 s 5.227 s/epoch; 1162 epoch lines; n_train 144000 / n_val 16000 / split_hash",
        ("# ===== 2026-10-12 01:03:36 KST  D2SXDMI160000 attempt 1" in tl, "# done        : 1162 epochs, stopped_by=patience, aborted=False, best val 2.152151e-01 @ epoch 1142, wall 6074.0 s, 5.227 s/epoch" in tl,
         len(re.findall(r"^epoch\s+\d+ \|", tl, re.M)), "n_train=144000 n_val=16000 split_hash=fecf46b30175b5c8" in tl), (True, True, 1162, True))
    chk("training log: ONE no-op resume header (10-13 06:16:37 KST = 10-12 16:16 CDT, the GB' lane): 'no epoch trained ... left untouched'", (tl.count("# ====="), "# ===== 2026-10-13 06:16:37 KST" in tl, "# resume      : checkpoint already meets stopped_by=patience at epoch 1162 -- no epoch trained" in tl), (2, True, True))
    chk("training log sigma range [3.2882e-02, 8.4773e-01] (5-DMI: sigma_t [3.288e-02, 8.477e-01])", "20 points, log-uniform draw over [3.2882e-02, 8.4773e-01]" in tl, True)
    chk("tb2_train_state_DMI.txt = '1 patience'", open(os.path.join(CONF, "logs/tb2_train_state_DMI.txt")).read().strip(), "1 patience")
    chk("ckpt mtimes: best 10-11 12:43 CDT, last 12:44 CDT (unchanged by the GB' lane on 10-12)", (cdt(mt(os.path.join(CONF, "ckpt/d2sx_DMI_N160000_a1_best.pt")))[:11], cdt(mt(os.path.join(CONF, "ckpt/d2sx_DMI_N160000_a1.pt")))[:11]), ("10-11 12:43", "10-11 12:44"))
    chk("run_tb2.sh pins the GPU-0 training to taskset -c 20,116", "taskset -c $([ $g -le 3 ] && echo $((20 + g)),$((116 + g))" in open(os.path.join(CONF, "code/run_tb2.sh")).read(), True)
    sg = np.load(os.path.join(CONF, "results/sigma_grid_D2_DMI.npz"))
    p(f"  sigma_grid_D2_DMI.npz keys {sg.files}")
    chk("sigma grid: 20 points, sigma_t endpoints (4 sf) [3.288e-02, 8.477e-01]", (int(sg["sigma"].size), f"{float(sg['sigma'].min()):.3e}", f"{float(sg['sigma'].max()):.3e}"), (20, "3.288e-02", "8.477e-01"))
    nu = [sg[k] for k in sg.files if k in ("nu", "nuq", "nu_q", "nu_grid")]
    if nu:
        chk("sigma grid nu endpoints (4 sf) [2.162e-03, 1.437e+00]", (f"{float(nu[0].min()):.3e}", f"{float(nu[0].max()):.3e}"), ("2.162e-03", "1.437e+00"))
    else:
        tg = open(os.path.join(CONF, "results/sigma_grid_D2_DMI.txt")).read()
        chk("sigma grid txt mentions nu endpoints 2.162e-03 / 1.437e+00", ("2.162e-03" in tg, "1.437e+00" in tg), (True, True))
    chk("pick / sparse tune mtime 10-11 12:49 CDT; ALD tune 10-12 15:55 CDT (all before the run commit, after the freeze)", (cdt(mt(os.path.join(CONF, "results/sparse/pick_DMI_C2.json")))[:11], cdt(mt(os.path.join(CONF, "results/ald/tune_PILDMI.json")))[:11]), ("10-11 12:49", "10-12 15:55"))

    p("\n## 5. commits, raw mtimes, manifests, runner / driver logs (§7 header, 7.3 header, 7.7)")
    t = {}
    for h in ("b737fd55", "003c8e51", "4131a3b0", "29cf411d", "cde35a4e"):
        t[h] = dt.datetime.fromisoformat(git("show", "-s", "--format=%cI", h).strip())
    p("  commits (CDT): " + " | ".join(f"{h} {cdt(v)}" for h, v in t.items()))
    chk("commit times: freeze 10-11 11:23:26; 5-DMI 4131a3b0 10-12 16:13:38 ('기록 16:13'); 29cf411d 17:56:07; §7 cde35a4e 18:21:13 ('기록 18:19' <= commit)",
        tuple(cdt(t[h]) for h in ("b737fd55", "4131a3b0", "29cf411d", "cde35a4e")), ("10-11 11:23:26", "10-12 16:13:38", "10-12 17:56:07", "10-12 18:21:13"))
    rawt = {r: sorted(mt(f) for f in glob.glob(os.path.join(CONF, r, "*.npz"))) for r in ("raw_DMIB16e4", "raw_DMIB16e4last", "raw_PILDMI", "raw_ALDDMI", "raw_SPDMI")}
    for r, v in rawt.items():
        p(f"  {r}: {len(v)} chunks, first {cdt(v[0])}, last {cdt(v[-1])} CDT")
    chk("448 chunks per raw", [len(v) for v in rawt.values()], [448] * 5)
    chk("every main raw chunk written after the run commit 4131a3b0 and before 29cf411d (no main commit during the main run)", (rawt["raw_DMIB16e4"][0] > t["4131a3b0"], rawt["raw_DMIB16e4last"][-1] < t["29cf411d"]), (True, True))
    chk("every baseline raw chunk written after 29cf411d and before cde35a4e (no main commit during the baseline run)", (min(rawt[r][0] for r in ("raw_PILDMI", "raw_ALDDMI", "raw_SPDMI")) > t["29cf411d"], rawt["raw_SPDMI"][-1] < t["cde35a4e"]), (True, True))
    between = [l for l in git("log", "--format=%h %cI", "003c8e51..cde35a4e").split("\n") if l]
    chk("commits in 003c8e51..cde35a4e are exactly 4131a3b0, 29cf411d, cde35a4e", [l.split()[0] for l in between][::-1], ["4131a3b0", "29cf411d", "cde35a4e"])
    pe = open(os.path.join(CONF, "logs/run_prior_eval_DMIB16e4.log")).read()
    chk("prior_eval log: ONE start line 16:15 (git 4131a3b0, args of 5-DMI); measurement done 17:02; last done 17:53; decision SNRs -3 +0 +3; acceptance rc=0 17:53; PRIOR_EVAL_DONE 17:54",
        (pe.count("] start (git"),) + tuple(s in pe for s in ("10-12 16:15 CDT] start (git 4131a3b0) prior=DMI bstar=gmm1024 kron_K=- ll_val=112.04253042212595 best=dc784649f1e9b890 last=20d28bf06e317ca5 ckpt=d2sx_DMI_N160000_a1",
                                                              "10-12 17:02 CDT] run DMIB16e4 (measurement) done", "10-12 17:53 CDT] DMIB16e4last done", "decision SNRs (anchor b*, tag DMIB16e4): -3 +0 +3",
                                                              "10-12 17:53 CDT] acceptance rc=0 (ACCEPT: OK -- DMIB16e4, DMIB16e4last)", "10-12 17:54 CDT] PRIOR_EVAL_DONE")), (1, True, True, True, True, True, True))
    chk("PRIOR_EVAL_DONE (log mtime 17:54:16 CDT) is before the commit 29cf411d (17:56:07) and before the baseline start", mt(os.path.join(CONF, "logs/run_prior_eval_DMIB16e4.log")) < t["29cf411d"], True)
    sb = open(os.path.join(CONF, "logs/run_dmi_base.log")).read()
    chk("dmi_base log: ONE start line 17:56 (git 29cf411d, shas of 5-DMI); PIL 17:58 / ALD 17:59 / SP 18:15 ACCEPT OK; ALD estimate on GPU 0 17:59; rule-reproduced, 264 / 1040 GB; meta|sparse 0 mismatching; raised 0; pair_baselines rc=0; DMI_BASE_DONE rc=0 18:15; no DEFER line",
        (sb.count("] start (git"),) + tuple(s in sb for s in ("[dmi_base 10-12 17:56 CDT] start (git 29cf411d) ckpt=d2sx_DMI_N160000_a1 best=dc784649f1e9b890 pick=8f72c113efb91b0b ald_tune=1e7824c1bae10376",
                                                              "17:58 CDT] PIL acceptance (ACCEPT: OK -- PILDMI)", "17:59 CDT] ALD acceptance (ACCEPT: OK -- ALDDMI)", "18:15 CDT] SP acceptance (ACCEPT: OK -- SPDMI)",
                                                              "17:59 CDT] ALD estimate on GPU 0 done", "rule-reproduced=True (rho, per-SNR n_em / L) memory need ~264 GB, available 1040 GB",
                                                              "meta|sparse check raw_SPDMI: 0 mismatching chunks", "{'SBL-loop': 0, 'SBL-pilot': 0, 'OMP-pilot': 0}", "raised trials {'V1-pilot': 0, 'bstar-pilot': 0}", "no raised ALD trial",
                                                              "18:15 CDT] pair_baselines rc=0", "18:15 CDT] DMI_BASE_DONE rc=0")) + ("deferred" in sb,), (1,) + (True,) * 12 + (False,))
    chk("baseline start after the commit 29cf411d: first PIL chunk after it", rawt["raw_PILDMI"][0] > t["29cf411d"], True)
    for tag, emin in (("DMIB16e4", 46.6), ("DMIB16e4last", 49.9), ("PILDMI", 1.6), ("ALDDMI", 0.6), ("SPDMI", 14.9)):
        log = open(os.path.join(CONF, f"logs/run_D2_{tag}.log")).read()
        fin = re.search(r"finished in ([\d.]+) min", log)
        chk(f"run_D2_{tag}.log: 448 done lines, no 'exists', finished in {emin} min, '448 tasks on 192 workers' once",
            (len(re.findall(r"^\s*\d+/448 done", log, re.M)), log.count("exists"), float(fin.group(1)) if fin else None, log.count("448 tasks on 192 workers")), (448, 0, emin, 1))
    for tag, egit, ecfg in (("DMIB16e4", "4131a3b0", "76399fb1c7f57517"), ("DMIB16e4last", "4131a3b0", "76399fb1c7f57517"), ("PILDMI", "29cf411d", None), ("ALDDMI", "29cf411d", None), ("SPDMI", "29cf411d", None)):
        m = json.load(open(os.path.join(CONF, f"results/review_next/run_manifest_{tag}.json")))
        p(f"  manifest {tag}: git {m['git_commit']} config_hash {m['config_hash']} n_raw {m['n_raw_files']}")
        chk(f"manifest {tag} git / n_raw_files", (m["git_commit"], m["n_raw_files"]), (egit, 448))
        if ecfg:
            chk(f"manifest {tag} config_hash", m["config_hash"], ecfg)
    mb, ml = (json.load(open(os.path.join(CONF, f"results/review_next/run_manifest_{x}.json"))) for x in ("DMIB16e4", "DMIB16e4last"))
    chk("both main manifests: identical code hashes (incl. Demo)", mb["code_hashes"], ml["code_hashes"])
    pb = open(os.path.join(CONF, "results/review_next/pairB_SPDMI.txt")).read()
    chk("pairB_SPDMI.txt header: run_dmi_base git 29cf411d 18:15 CDT; provenance line 'git base=4131a3b0 extra0=29cf411d pil=29cf411d ald=29cf411d; integrity: OK'", ("# run_dmi_base git 29cf411d 2026-10-12 18:15 CDT" in pb, "git base=4131a3b0 extra0=29cf411d pil=29cf411d ald=29cf411d; integrity: OK" in pb), (True, True))
    chk("pairB_SPDMI.txt SUMMARY / condition / X* lines as quoted in 7.3", all(s in pb for s in ("SUMMARY-B (baselines without b*, 15): (i) 15, (ii) 0, not decided 0; b* -> V1 (i)", "SUMMARY registered baselines 16 (b* + 𝔅 15): (i) 16, (ii) 0, not decided 0",
                                                                                 "condition (k = 16, (ii) = 0, R_X* CI lower > 0): MET", "X* (fewest -3 dB failures, ties by name) = M-ours-bstar (F=885); R_X* -3 dB = 0.099 [90% 0.050, 0.146]")), True)

    p("\n## 6. git diffs (7.3 header, 7.7) and banners / acceptance files")
    chk("git diff 4131a3b0 29cf411d -- conf/code Demo is EMPTY", git("diff", "--stat", "4131a3b0", "29cf411d", "--", "conf/code", "Demo").strip(), "")
    d1 = git("diff", "--stat", "b737fd55", "4131a3b0", "--", "conf/code", "Demo")
    names = sorted(l.split("|")[0].strip().replace("conf/code/", "") for l in d1.split("\n") if "|" in l)
    new = sorted(l.split("\t")[1].replace("conf/code/", "") for l in git("diff", "--name-status", "b737fd55", "4131a3b0", "--", "conf/code", "Demo").split("\n") if l.startswith("A"))
    chk("git diff --stat b737fd55 4131a3b0 -- conf/code Demo: 23 files, none under Demo", (len(names), "23 files changed" in d1, any("Demo" in x for x in names)), (23, True, False))
    chk("7.7 new files (11)", new, sorted(["srp_build.py", "path_strata.py", "run_srp_base.sh", "run_srp_eval.sh", "run_srp_post_gpu.sh", "run_srp_post_select.sh", "run_srp_sparse_tune.sh",
                                             "run_fighsroom16e4.sh", "run_fighspath16e4.sh", "run_fighsx16e4.sh", "run_seedsroom16e4.sh"]))
    chk("7.7 modified files (12)", sorted(set(names) - set(new)), sorted(["ald.py", "analysis.py", "common.py", "dmimo.py", "em_batched_check_nr.py", "run_d2_sx.py", "run_manifest.py", "run_prior_eval.sh", "sigma.py", "testbed_dm.py",
                                                                         "run_srb_eval.sh", "run_dmi_eval.sh"]))
    d4 = git("diff", "b737fd55", "4131a3b0", "--", "conf/code/dmimo.py", "conf/code/common.py", "conf/code/analysis.py", "conf/code/sigma.py", "conf/code/run_d2_sx.py", "conf/code/run_manifest.py",
             "conf/code/run_prior_eval.sh", "conf/code/testbed_dm.py", "conf/code/em_batched_check_nr.py")
    ch = [l for l in d4.splitlines() if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---"))]
    non = [l[:150] for l in ch if not ("SRP" in l or "srp" in l)]
    p(f"  changed lines in the 9 shared modules: {len(ch)}; lines NOT mentioning SRP/srp: {len(non)}")
    for l in non:
        p("     ", l)
    removed = [l[:160] for l in ch if l.startswith("-")]
    p(f"  removed lines ({len(removed)}) -- each is re-added with an SRP entry appended:")
    for l in removed:
        p("     ", l)
    da = git("diff", "b737fd55", "4131a3b0", "--", "conf/code/ald.py")
    cha = [l for l in da.splitlines() if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---"))]
    chk("ald.py diff: every changed line concerns the regen sets (hisnr / hisnr4) only", all("hisnr" in l for l in cha), True)
    untouched = ["arms.py", "runner.py", "gmm_em_gpu.py", "fit_gpu.py", "fit_gpu_batched.py", "score.py", "bigamp.py", "sparse_tune.py", "eval_accept.py", "pair_baselines.py", "pair_cross.py", "pair_ald.py",
                 "recovery_ci.py", "frontier_ci.py", "guard_report.py", "dmi_build.py", "run_dmi_base.sh", "run_dmi_post_gpu.sh", "run_dmi_post_select.sh", "dmc_leak_strata.py", "rank_strata.py"]
    chk("receiver / fit / judge modules (21 existing files of conf/code) NOT in the diff b737fd55..4131a3b0", ([x for x in untouched if x in names], all(os.path.isfile(os.path.join(CONF, "code", x)) for x in untouched), len(untouched)), ([], True, 21))
    import common as C  # noqa: E402
    import dmimo  # noqa: E402
    chk("PID['DMI'] = 14, dmimo.POOL_SHA / P_RAW / TRAIN_SHA of DMI = §0", (C.PID["DMI"], dmimo.POOL_SHA[("DMI", 8)], repr(dmimo.P_RAW[("DMI", 8, 4)]), dmimo.TRAIN_SHA[("DMI", 8, 4)]),
        (14, ("dec5e7a1ea1e4605", "f0f716718f1c15d1"), "0.0019453481377247777", "3380177f4c38cf57"))
    old_common = git("show", "b737fd55:conf/code/common.py"); new_common = open(os.path.join(CONF, "code/common.py")).read()
    grab = lambda s: s[s.index("DMI_WARNING = ("):s.index("DM_WARNINGS") if "SRP_WARNING" not in s else s.index("SRP_WARNING = (")]
    chk("common.DMI_WARNING (the banner text) byte-identical to the freeze", grab(old_common), grab(new_common))
    for tag, sha in (("DMIB16e4", "dc784649f1e9b890"), ("DMIB16e4last", "20d28bf06e317ca5")):
        tt = open(os.path.join(CONF, f"results/tables_D2_{tag}.txt")).read()
        chk(f"tables_D2_{tag}: banner counts (SITE-SPECIFIC ... (prior DMI) 1, 'FIVE frozen UE yaws per position' 1, sparse-specular 0, 'FIVE fixed' 0)",
            (tt.count("SITE-SPECIFIC RAY-TRACED TESTBED (prior DMI)"), tt.count("FIVE frozen UE yaws per position"), tt.count("CLAIM TESTBED -- sparse specular"), tt.count("FIVE fixed")), (1, 1, 0, 0))
        chk(f"tables_D2_{tag}: git 4131a3b0, N_train=160000 lines >= 12, b*=gmm1024, ckpt sha", ("# git commit  : 4131a3b0" in tt, tt.count("N_train=160000") >= 12, "b*=gmm1024" in tt, sha in tt), (True, True, True, True))
    for tag in ("DMIB16e4", "PILDMI", "ALDDMI", "SPDMI"):
        a = open(os.path.join(CONF, f"results/review_next/{tag}_accept.txt")).read().strip()
        chk(f"{tag}_accept.txt first line", a.split("\n")[0], f"ACCEPT: OK -- {tag}" + (", DMIB16e4last" if tag == "DMIB16e4" else ""))

    p("\n## 7. GB' (7.2) and acceptance (e)")
    gl = open(os.path.join(CONF, "logs/gbprime_DMIB16e4.log")).read()
    chk("gbprime log: 'GMM b* = gmm1024 (full K=1024) @N=160000 | diff/gmm min 0.7272 max 1.0217 median 0.8038 | equal_budget=True'; 'trained 1162 ep'; stopped_by=patience",
        ("[d2sx] GMM b* = gmm1024 (full K=1024) @N=160000 | diff/gmm min 0.7272 max 1.0217 median 0.8038 | equal_budget=True" in gl, "[d2sx] trained 1162 ep" in gl, "stopped_by=patience aborted=False best_epoch=1142" in gl), (True, True, True))
    gz = np.load(os.path.join(CONF, "results/d2_gbprime_DMI_N160000_a1.npz"), allow_pickle=True)
    p(f"  d2_gbprime_DMI_N160000_a1.npz keys: {gz.files}")
    for k in gz.files:
        a = gz[k]
        p(f"    {k}: {a if a.size <= 20 else a.shape}")
    csv = open(os.path.join(CONF, "results/d2_gbprime_DMI.csv")).read().strip().split("\n")
    row = dict(zip(csv[0].split(","), csv[-1].split(",")))
    chk("d2_gbprime_DMI.csv: one data row; gmm_bstar gmm1024, K 1024, equal_budget True, epochs 1162, ratio min/max/median = 0.7272 / 1.0217 / 0.8038 (4 dp)",
        (len(csv), row["gmm_bstar"], row["gmm_K"], row["equal_budget"], row["epochs"], round(float(row["ratio_min"]), 4), round(float(row["ratio_max"]), 4), round(float(row["ratio_median"]), 4)), (2, "gmm1024", "1024", "True", "1162", 0.7272, 1.0217, 0.8038))
    chk("acceptance (e): npz mtime 16:24:17 CDT > full-1024 fit 16:11:10 CDT (and > the merged kron files)", (cdt(mt(os.path.join(CONF, "results/d2_gbprime_DMI_N160000_a1.npz"))), mt(os.path.join(CONF, "results/d2_gbprime_DMI_N160000_a1.npz")) > mt(os.path.join(FITS, "fit_DMI_Nr8_fullK1024_n160000.npz"))), ("10-12 16:24:17", True))
    chk("prediction 8: GB' median <= 0.90 -> hit", float(row["ratio_median"]) <= 0.90, True)

    p("\n## 8. no DMI BLER before 4131a3b0; DECISIONS.md lines")
    dirs = sorted(os.path.basename(d) for d in glob.glob(os.path.join(CONF, "raw_*")) if "DMI" in os.path.basename(d))
    later = [d for d in dirs if d.startswith("raw_FH")]      # the follow-up registration FIGHSDMI16e4 (started 10-12 18:43 CDT, after cde35a4e): OUT OF SCOPE
    if later:
        firsts = {d: min([mt(x) for x in glob.glob(os.path.join(CONF, d, "*.npz"))] or [mt(os.path.join(CONF, d))]) for d in later}
        p(f"  out of scope (follow-up FIGHSDMI16e4, appeared DURING this audit): {[(d, cdt(v)) for d, v in firsts.items()]}")
        chk("the raw_FH* directories of the follow-up registration hold nothing older than the audited commit cde35a4e", all(v > t["cde35a4e"] for v in firsts.values()), True)
    chk("raw directories with DMI in the name (follow-up raw_FH* excluded)", [d for d in dirs if d not in later], ["raw_ALDDMI", "raw_DMI", "raw_DMIB16e4", "raw_DMIB16e4last", "raw_PILDMI", "raw_SPDMI"])
    chk("raw_DMI is an EMPTY directory (sigma-grid artefact, mtime 10-11 10:42 CDT, before the registration)", (os.listdir(os.path.join(CONF, "raw_DMI")), cdt(mt(os.path.join(CONF, "raw_DMI")))[:11]), ([], "10-11 10:42"))
    others = [f for f in glob.glob(os.path.join(CONF, "raw*", "*_DMI_*.npz")) if os.path.basename(os.path.dirname(f)) not in dirs]
    chk("no prior-DMI raw chunk in any other raw directory", len(others), 0)
    earliest = min(v[0] for v in rawt.values())
    chk("earliest DMI raw chunk on disk is after the run commit 4131a3b0", earliest > t["4131a3b0"], True)
    early_files = [os.path.relpath(f, CONF) for pat in ("results/tables_D2_*DMI*", "results/guard_D2_*DMI*", "results/review_next/*DMI*", "logs/run_D2_*DMI*", "logs/analysis_*DMI*", "logs/run_prior_eval_*DMI*", "logs/run_dmi_base.log")
                   for f in glob.glob(os.path.join(CONF, pat)) if mt(f) < t["4131a3b0"]]
    chk("no DMI tables / guard / review_next / run-log file older than the run commit", early_files, [])
    hist = [l for l in git("log", "--format=%h", "b737fd55..003c8e51", "--", "conf/results/tables_D2_DMIB16e4.txt", "conf/results/review_next/pairB_SPDMI.txt", "conf/results/review_next/DMIB16e4_accept.txt").split("\n") if l]
    chk("git history b737fd55..003c8e51 never contained DMI result files", hist, [])
    dec = open(os.path.join(CONF, "DECISIONS.md")).read()
    chk("DECISIONS.md: freeze line 'SRB epoch 229 · DMI epoch 221' (prediction 9 lower bound scorable: < 300)", "학습 SRB epoch 229 · DMI epoch 221" in dec, True)
    chk("DECISIONS.md: 10-13 04:02 KST line (withdrawal reverted, user 'Deepmimo 지금 못하나?') and the 06:13 KST 5-DMI line", ("[2026-10-13 04:02 KST] DeepMIMO 실내 풀 (prior DMI) 의 철회를 되돌림" in dec and "'Deepmimo 지금 못하나?'" in dec, "[2026-10-13 06:13 KST] ROOM16e4 — DMI 의 평가 전 고정 기록 (5-DMI)" in dec), (True, True))
    rec = open(os.path.join(CONF, "results/review_next/NEXT_EXPERIMENTS_ROOM16e4.md")).read()
    s7 = rec[rec.index("## 7. 결과"):]
    chk("record §7: 동치 / 일반화 only inside negated sentences", all(("않" in l or "없" in l) for l in s7.splitlines() if "동치" in l or "일반화" in l), True)
    chk("run_dmi_eval.sh == the 5-DMI command", "CUDA_VISIBLE_DEVICES= bash code/run_prior_eval.sh DMI DMIB16e4 d2sx_DMI_N160000_a1 gmm1024 - 112.04253042212595 \\\n  dc784649f1e9b890 20d28bf06e317ca5 \"full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048\"" in open(os.path.join(CONF, "code/run_dmi_eval.sh")).read(), True)

    p(f"\n## SUMMARY: {NCHECK[0]} values checked, {NCHECK[1]} differ from the record")
    return 0 if NCHECK[1] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
