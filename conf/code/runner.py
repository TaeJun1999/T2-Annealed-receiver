"""conf/code/runner.py -- the single entry point for every stage of the conference run (conf/06_SPEC_runner.md §4).

  python runner.py tests    --testbed D1                     07_SPEC: B/S/C + M + L (+ D/T once their artefacts exist)
  python runner.py smoke    --testbed D1 --cell C1           n = 2, every arm of that testbed, numbers discarded
  python runner.py run      --testbed D1 --n 640 --chunk 40  the real grid -> conf/raw/*.npz   (finished chunks skipped)
  python runner.py lemma                                     A3  -> conf/results/lemma.txt + conf/figs/F2_lemma.png
  python runner.py sigma    --testbed D1                     A4/B3 -> conf/results/sigma_grid[_D2].txt
  python runner.py train    --rung L1 --attempt 1            A5/B3 -> conf/ckpt/ + a row in conf/LADDER.md
  python runner.py gate     --testbed D1 --rung L1           A5  -> conf/results/gate_D1.txt   (D2: GB' -> gate_D2.txt)
  python runner.py testbed                                   B1  -> conf/results/testbed_D2.txt (T2a..T2e)
  python runner.py fit      --testbed D2                     B2  -> conf/results/gmm_fits_D2/*.npz + gmm_fit_D2.txt
  python runner.py analysis --testbed D1                     08_SPEC tables

Structure (chunked tasks, resume by skipping finished chunks, one rng stream per point, mp.Pool, flushed
progress) follows Demo/exp_0925_run.py, which is the proven runner of this project; only the naming, the
arm sets and the testbed switch differ.  There is deliberately NO --jobs flag (01_RULES §4: the default is
all cores).  --tag X routes EVERY output -- raw/, the D2 fits, ckpt/, LADDER.md, the sigma grid, the gate
files, tests.txt and the lemma artefacts -- into suffixed paths, so a smoke run can never overwrite the real
one (01_RULES §7).  On top of that the FROZEN A4 grid conf/results/sigma_grid_<testbed>.npz, which every
GA-GD gate and every score arm reads, is refused outright unless --force-regrid is passed.  ANY departure
from the frozen configuration (seed, iterations, beta, T_in, arm subset, ntrain, EM restarts, EM iterations)
is refused unless --tag is given (01_RULES §5: same data, same budget, for the GMM and the diffusion arm).

device [01_RULES §9]: the receiver is CPU / complex128 / float64 for EVERY arm -- `run` and `tests` refuse
anything else, because a per-arm precision difference invalidates the paired comparison of table B.  Only
`train` and `gate` default to cuda (§9.5); they touch no receiver number.

Raw file (the contract conf/code/analysis.py is written against):
    conf/raw[_tag]/<testbed>_<cell>_<prior>_Nr<Nr>_T<T>_Tp<Tp>_<pil>_snr<int(snr)>_skip<skip>_n<n>.npz
    "<arm>|<field>"  (n, n_iter) for every field of common.KEYS_RAW
    "<arm>|diverged", "<arm>|stop_hits"   where the arm provides them
    "<arm>|clip"     (n, 2) = (clipped site fraction, mean relative shift) where the arm counts them
    "<arm>|failed"   (n,)   1.0 for a trial whose arm raised -- the row stays, filled with NaN
    "meta|<k>"       b* / kron_K / validation log-likelihoods from arms.build_our_arms
    "meta|dscore_status"   "built from <ckpt>" or "ABSENT -- <reason>".  M-ours-dscore is NEVER silently
                     missing: analysis.py prints its slot as BLOCKED / FAILED-VERIFICATION (01_RULES §6)
    "meta|em_sec", "meta|em_sec|<arm>", "meta|em_sec_note", "meta|fit_sec|M-ours-dscore"
                     the fit / training-cost column of table A -- never hidden, never blank (01_RULES §5)
    "comp"           true mixture component per trial, D1 only (absent on D2)
    "run|<k>"        beta, T_in, seed, iterations, dtype actually used (06_SPEC §5)
FAILED, DIVERGED AND NON-CONVERGED BLOCKS ARE NEVER DROPPED (01_RULES §5); they are flagged, never removed.
"""
import argparse
import glob
import multiprocessing as mp
import os
import re
import sys
import time

import common as C                          # FIRST: common.py sets OMP/OPENBLAS/MKL_NUM_THREADS=1, and the
import numpy as np                          # BLAS reads those only at ITS import, which common.py triggers
import arms as A

TAG = ""                                   # set by _init in the parent AND in every worker
N_VAL = 5000                               # validation / test set size, exp_0925 convention [exact]
KAPPAS = (0, 16, 64, 256)                  # MAP shrinkage grid, full covariance only (05_SPEC §4)
FAM = {"full": 0, "kron": 1}
D2_KS = A.D2_KS                            # (16, 32, 64, 128) -- 05_SPEC §4 asks for the full range
SIGMA_GRID = os.path.join(C.CONF, "results", "sigma_grid.txt")
RESTARTS, FIT_ITERS = 3, 500               # `fit` defaults; the frozen-config guard in main() reads THESE

# D1 reuses Demo/exp_0925_fits/ verbatim (see DECISIONS).  Those .npz carry no per-fit wall-clock, so the
# only honest number is the DOCUMENTED aggregate of the whole exp_0925 fit stage, labelled as such.
# 01_RULES §5: the fit cost is a column of the result table -- an empty column is not an option.
EM_SEC_D1 = 205.0
EM_SEC_D1_NOTE = ("exp_0925 fit-stage AGGREGATE (3 min 25 s = 205 s for 36 fits / 270 EM runs: prior U/S/P "
                  "x Nr 4/8 x {full,kron} x K{16,32,64} x kappa x 3 restarts, 192 CPU cores; "
                  "docs/EXPERIMENTS.md row 2026-09-18 13:35).  Demo/exp_0925_fits/*.npz store no per-fit "
                  "time, so NO per-arm split of this number exists -- it is an upper bound for any one arm.")

# Used when conf/code/score.py does not export GA_NOTE itself.  04_SPEC §5 keeps GA at 1e-6, unchanged;
# this note exists so that "GA 1e-17 PASS" is never read as evidence that the conversion was validated.
GA_NOTE = (
    "GA is identically zero BY CONSTRUCTION for every parameterisation of this model family:\n"
    "  ve:  x + s^2 * (-eps/s) = x - s*eps = the native denoiser;\n"
    "  vp:  sqrt(abar)/sqrt(1-abar) = 1/sigma, so the score reduces to -eps/sigma -> same expression;\n"
    "  rf:  (1-t)^2/t = 1/(sigma(1+sigma)), so x + s^2*score = x(1-t) - t*v = the native denoiser.\n"
    "GA guards an INCONSISTENCY between the score path and the x0 path; it cannot catch an error shared by\n"
    "both.  A GA of 1e-17 is therefore NOT evidence that the score->denoiser conversion was validated on\n"
    "the trained model: GB, GC and GD carry the whole gate.  Tolerance 1e-6 unchanged (04_SPEC §5); see\n"
    "conf/DECISIONS.md 2026-09-20 12:35.")


# ----------------------------------------------------------------------------- tag routing / worker setup
def d_raw():
    return os.path.join(C.CONF, "raw" + (f"_{TAG}" if TAG else ""))


def d_fits_d2():
    return os.path.join(C.CONF, "results", "gmm_fits_D2" + (f"_{TAG}" if TAG else ""))


def d_ckpt():
    return os.path.join(C.CONF, "ckpt" + (f"_{TAG}" if TAG else ""))


def tagged(path):
    """conf/results/x.txt -> conf/results/x_<TAG>.txt.  --tag routes EVERY output, not just raw/."""
    r, e = os.path.splitext(path)
    return r + (f"_{TAG}" if TAG else "") + e


def _init(tag):
    """Worker initialiser (also called once in the parent).  Robust to fork / spawn / forkserver."""
    global TAG
    TAG = tag
    A.D2_FITS = d_fits_d2()                # arms.fit_path reads this module global at call time
    t = sys.modules.get("torch")           # do NOT import torch here: 192 workers would each pay for it
    if t is not None:
        t.set_num_threads(1)               # one BLAS/torch thread per worker (common.py did the env vars)


def raw_file(testbed, cell, prior, pil, snr, skip, n):
    c = C.CELLS[cell]
    return os.path.join(d_raw(), f"{testbed}_{cell}_{prior}_Nr{c['Nr']}_T{c['T']}_Tp{c['Tp']}_{pil}"
                                 f"_snr{int(snr)}_skip{skip}_n{n}.npz")


# ----------------------------------------------------------------------------- arm construction at one point
def stats_obj(rx):
    """The object that counts EP-site clips for this arm: RouteAClip itself for the score arms, the GMM
    prior object for the exact-mixture-site arms, None otherwise (same rule as exp_0925_run.stats_obj)."""
    if isinstance(rx, C.RouteAClip):
        return rx
    p = getattr(rx, "prior", None)
    return p if (getattr(rx, "exact_prior", False) and hasattr(p, "reset_stats")) else None


def score_prior(testbed, prior, Nr, Nt, ckpt=None, psd_project=False, ntrain=None):
    """Module H of M-ours-dscore.  score.py is authoritative; its signature is

        score.load_prior(testbed, prior, Nr, Nt, rung=None, attempt=None, ckpt=None, device="cpu",
                         psd_project=False, ntrain=None)
            -> a ScorePrior, or None when no GATE-PASSING checkpoint exists.

    device is always "cpu": the receiver is CPU/complex128 for EVERY arm (01_RULES §9.3).  rung/attempt are
    left None on purpose -- picking a ladder attempt by hand for the headline run would be choosing the arm
    after the fact (01_RULES §5); load_prior applies the gate itself.

    Returns (obj, status).  A MISSING load_prior is reported as its own failure, not folded into "no
    checkpoint": swallowing it silently drops M-ours-dscore from both testbeds with no trace (FIX 1)."""
    try:
        import score
    except Exception as ex:
        return None, f"ABSENT -- conf/code/score.py not importable ({type(ex).__name__}: {ex})"
    fn = getattr(score, "load_prior", None)
    if fn is None:
        return None, ("ABSENT -- score.load_prior does not exist; the 06_SPEC §1 contract "
                      "(M-ours-dscore = the gate-passing checkpoint) cannot be honoured")
    try:
        kw = dict(psd_project=True) if psd_project else {}      # Stage C V1 / (F1); default path unchanged
        if ntrain is not None and ntrain != C.N_TRAIN:
            kw["ntrain"] = ntrain          # equal budget: Chat from the SAME fits the GMM arms use (10_SPEC A3)
        p = fn(testbed, prior, Nr, Nt, rung=None, attempt=None, ckpt=ckpt, device="cpu", **kw)
    except Exception as ex:
        return None, f"ABSENT -- score.load_prior raised ({type(ex).__name__}: {ex})"
    why = str(getattr(score, "last_reason", "") or "")          # score.py's own account of the decision
    if p is None:
        return None, ("ABSENT -- no GATE-PASSING checkpoint (04_SPEC §5 gates GA-GD): "
                      + (why or "score.load_prior gave no reason"))
    return p, "built from " + (why or str(getattr(p, "ckpt", None) or ckpt or "the checkpoint"))


NO_SCORE = "n/a (no score model for this array size)"


def fit_cost_meta(testbed, fits):
    """The fit/training-cost column of table A (01_RULES §5: "학습·적합 비용을 숨기지 않는다").
    analysis.fit_cost reads meta|em_sec|<arm>, meta|fit_sec|<arm> or meta|em_sec, in that order.

    D2: the wall-clock cmd_fit stored in each conf/results/gmm_fits_D2/*.npz ("sec" = every EM run of that
        (family, K), including the restarts and the kappa grid).  M-ours-gmm32 is specified a priori, so it
        carries the K=32 fit alone; M-ours-bstar is SELECTED by validation likelihood and that selection
        consumed the whole grid, so it carries the total -- the larger, less flattering number (01_RULES §1).
    D1: the fits are reused and carry no per-fit time -> the documented aggregate, labelled."""
    if testbed == "D1":
        return {"em_sec": float(EM_SEC_D1), "em_sec_note": EM_SEC_D1_NOTE}
    sec = {k: float(z["sec"]) for k, z in fits.items() if "sec" in getattr(z, "files", ())}
    if not sec:
        return {"em_sec_note": "the D2 fits carry no 'sec' field -- re-run `runner.py fit --testbed D2`"}
    tot = sum(sec.values())
    out = {"em_sec": tot, "em_sec|M-ours-bstar": tot,
           "em_sec_note": f"sum of 'sec' over {len(sec)} fit files in {A.D2_FITS} (every EM run: "
                          f"{len(sec)} (family, K) combinations x kappa grid x restarts)"}
    if ("full", 32) in sec:
        out["em_sec|M-ours-gmm32"] = sec[("full", 32)]
    return out


# ----------------------------------------------------------------------------- per-arm training budget (10_SPEC A3)
# "학습 prior 의 예산을 N' 로 올리면 GMM 도 같은 N' 로 재적합한다" -- and while that re-fit is still running,
# a table can hold arms at DIFFERENT budgets.  10_SPEC A3 therefore requires the budget of every arm to be
# readable in the header, so a not-equal-budget comparison cannot be mistaken for an equal-budget one.
BUDGET_NOTE = ("training budget (N_train, channel samples) of EVERY arm -- 10_SPEC A3.  The GMM arms and the "
               "learned arms are only equal-budget when their N_train below are EQUAL; read the numbers, not "
               "the arm names.  The GMM re-fit at N'=1.6e5 may not have finished when this table was written.")
GMM_BUDGET_ARMS = ("R0-pilot", "R1-turbo", "R2-ours-G", "R4-scvamp", "R4-llr", "M-ours-G",
                   "M-ours-gmm32", "M-ours-bstar", "M-ours-bstar-scalar")
EXACT_BUDGET_ARMS = ("M-ours-score", "R6-exactEP")


def gate_verdict(ckpt):
    """The RECORDED gate verdict of a checkpoint, quoted verbatim from conf/results/gate_*.txt and
    conf/LADDER*.md.  Nothing is re-measured and no threshold is touched here: this only surfaces what the
    gate stage already wrote, so a table row naming a learned arm also names its gate row (10_SPEC §5).
    A checkpoint no gate file mentions is reported as UNVERIFIED -- never as silently fine."""
    base = os.path.basename(str(ckpt or ""))
    if not base:
        return "n/a (no checkpoint)"
    hits = []
    for p in sorted(glob.glob(os.path.join(C.CONF, "results", "gate_*.txt"))
                    + glob.glob(os.path.join(C.CONF, "LADDER*.md"))):
        try:
            with open(p, errors="replace") as f:
                for line in f:
                    # DIVERGED is in the list because 10_SPEC §3d makes it a COMPLETED attempt with
                    # a recorded verdict (LADDER_C.md already carries three).  Without it a diverged
                    # checkpoint reads back as "NO GATE RECORD ... UNVERIFIED", i.e. as an unknown
                    # rather than as the known-bad thing the ladder already says it is.
                    if base in line and re.search(r"\b(PASS|FAIL|ABORTED|DIVERGED)\b", line):
                        hits.append(f"[{os.path.basename(p)}] " + " ".join(line.split())[:220])
        except OSError:
            continue
    return " || ".join(hits[:3]) if hits else (
        f"NO GATE RECORD mentions {base} -- UNVERIFIED here.  (GA-GD are measurable on D1 only, 10_SPEC §5: "
        f"a D2 re-train is qualified by its D1 sibling's gate row, which this string cannot prove.)")


def learned_budget(sp, ckpt):
    """N_train of a LEARNED arm, taken from the checkpoint's own 'rung' tag (score.train writes e.g.
    'D2SX10000' / 'SX160000'), plus the checkpoint path and its recorded gate verdict.  When the tag
    carries no sample count the string says UNKNOWN -- it never guesses a budget."""
    st = getattr(sp, "st", None) or {}
    rung = str(st.get("rung", "?"))
    m = re.search(r"(\d{3,})", rung)
    n = m.group(1) if m else f"UNKNOWN (checkpoint rung tag {rung!r} carries no sample count)"
    p = str(getattr(sp, "ckpt", None) or ckpt or "?")
    return f"N_train={n}  rung={rung}  ckpt={p}  gate: {gate_verdict(p)}"


def budget_meta(arm_names, ntrain, learned):
    """meta|budget|<arm> for every arm at this point (analysis.py prints them in the table header)."""
    out = {"budget_note": BUDGET_NOTE}
    for k in arm_names:
        if k in learned:
            out[f"budget|{k}"] = learned[k]
        elif k in GMM_BUDGET_ARMS:
            out[f"budget|{k}"] = f"N_train={ntrain} -- the ONE channel set (GMM EM fit / its sample covariance Chat)"
        elif k in EXACT_BUDGET_ARMS:
            out[f"budget|{k}"] = "N_train=n/a -- EXACT / TRUE prior, fits nothing (oracle)"
        elif k == "R3-bigamp":
            out[f"budget|{k}"] = "N_train=0 -- i.i.d. CN(0,1/Nr) prior, fits nothing"
        elif k == "R5-genie":
            out[f"budget|{k}"] = "N_train=n/a -- genie: the true H is given"
        else:
            out[f"budget|{k}"] = f"N_train={ntrain} -- unclassified arm, quoting the point's channel-set size"
    return out


def build_point(testbed, cell, prior, snr, ntrain=C.N_TRAIN, beta=C.BETA, t_in=C.T_IN, ckpt=None,
                stagec_ckpt=None):
    """Every arm of `testbed` at one (cell, prior, SNR) point, all sharing one pilot matrix (06_SPEC §2).

    D1: R0 R1 R2 R3 R4-scvamp R4-llr R5-genie R6-exactEP + M-ours-{gmm32,bstar,score,dscore}
    D2: the same MINUS R6-exactEP and M-ours-score -- there is no exact prior score there (06_SPEC §1).

    M-ours-score is the ORACLE arm: the EXACT score of the true prior, in closed form from GMMPriorB.
    It needs NO trained network, so it exists on EVERY D1 cell including the 4x4 ones.
    Only M-ours-dscore is tied to the array size, because its network input is 2*Nr*Nt and the ladder was
    trained for 8x4 (conf/DECISIONS.md); on 4x4 it is reported as NO_SCORE, never silently omitted."""
    c = C.CELLS[cell]
    Nr, Nt, T, Tp = c["Nr"], c["Nt"], c["T"], c["Tp"]
    sigma2 = 10 ** (-snr / 10)
    code = C.QAMCode(C.GENS, C.NU, C.M_QAM, Nt * (T - Tp))
    pil, Xp = C.make_pilots(testbed, prior, Nt, Tp, Nr)
    gen = C.make_gen(testbed, prior, Nr, Nt)
    true = getattr(gen, "prior", None) if testbed == "D1" else None     # exact prior: D1 only
    a = (testbed, prior, Nr, Nt, T, Tp, sigma2, code, Xp)

    arms, cfgs, Cs, fits = A.build_baseline_arms(*a, ntrain=ntrain, true_prior=true)
    if beta != C.BETA or t_in != C.T_IN:            # 01_RULES §4: beta 0.7 -> 0.5 -> 0.3 is BiG-AMP's knob
        arms["R3-bigamp"] = A.R3BiGAMP(Nr, Nt, T, Tp, sigma2, code, Xp, beta=beta, t_in=t_in)
        cfgs["R3-bigamp"] = dict(arms["R3-bigamp"].cfg_dump, arm="R3-bigamp")

    sp, why = (score_prior(testbed, prior, Nr, Nt, ckpt, ntrain=ntrain) if Nr == 8
               else (None, "ABSENT -- M-ours-dscore only: " + NO_SCORE))
    # Stage C (10_SPEC §3b/§3c).  STRICTLY OPT-IN: with stagec_ckpt=None nothing below is built and the arm
    # set of this point is exactly the pre-registered one.  --stagec-ckpt is a SEPARATE flag from --ckpt, so
    # turning Stage C on never changes what M-ours-dscore is (its pre-registered judgement stays untouched).
    spc = spc1 = None
    sc_why = "not requested (--stagec-ckpt not given) -- arm set is the pre-registered one"
    if stagec_ckpt:
        if Nr != 8:
            sc_why = "ABSENT -- M-ours-dscore-C-* only: " + NO_SCORE
        else:
            spc, sc_why = score_prior(testbed, prior, Nr, Nt, stagec_ckpt, ntrain=ntrain)
            spc1, w1 = score_prior(testbed, prior, Nr, Nt, stagec_ckpt, psd_project=True, ntrain=ntrain)
            sc_why += " | V1 (psd_project=True): " + w1
    # `true` (not `true if Nr == 8`): the oracle score arm is closed-form and array-size independent.
    our, ocfg, meta, hp, _ = A.build_our_arms(*a, ntrain=ntrain, true_prior=true, score_prior=sp,
                                              score_prior_c=spc, score_prior_v1=spc1,
                                              bstar_scalar=bool(stagec_ckpt))
    arms.update(our)
    cfgs.update(ocfg)
    # An arm that is not built must leave a trace with the REASON, or the analysis sees a missing row and
    # cannot tell "not built" from "dropped" (01_RULES §6, 06_SPEC §1).
    meta["dscore_status"] = why
    meta["stagec_status"] = sc_why
    meta["ntrain"] = float(ntrain)
    meta.update(fit_cost_meta(testbed, fits))
    if stagec_ckpt:
        meta["stagec_ckpt"] = str(stagec_ckpt)
        meta["stagec_gate"] = gate_verdict(stagec_ckpt)
    learned = {}
    if sp is not None:
        meta["dscore_ckpt"] = str(getattr(sp, "ckpt", None) or ckpt or "?")
        learned["M-ours-dscore"] = learned_budget(sp, ckpt)
    for k, o, cp in (("M-ours-dscore-C-V0", spc, stagec_ckpt), ("M-ours-dscore-C-V4", spc, stagec_ckpt),
                     ("M-ours-dscore-C-V1", spc1, stagec_ckpt)):
        if o is not None:
            learned[k] = learned_budget(o, cp)
    for k, o in (("M-ours-dscore", sp), ("M-ours-dscore-C-V0", spc), ("M-ours-dscore-C-V4", spc),
                 ("M-ours-dscore-C-V1", spc1)):
        st = getattr(o, "st", None) or {}
        if "wall_sec" in st:            # score.train's wall-clock = the TRAINING cost of the learned arm
            meta[f"fit_sec|{k}"] = float(st["wall_sec"])
    meta.update(budget_meta(arms, ntrain, learned))
    return dict(arms=arms, cfgs=cfgs, meta=meta, gen=gen, code=code, pil=pil, Xp=Xp, fits=fits,
                Nr=Nr, Nt=Nt, T=T, Tp=Tp, sigma2=sigma2, dscore=why, stagec=sc_why)


# ----------------------------------------------------------------------------- run: the real grid
def run_task(task):
    """One (point, skip, chunk).  The trials that a previous chunk consumed are REGENERATED from the same
    common.trial_rng stream and then dropped, so chunks concatenate and every arm at a point sees the same
    (H, u, perm, Y) -- paired inside a cell (01_RULES §5, test C4)."""
    testbed, cell, prior, snr, skip, n, ntrain, beta, t_in, iters, arm_sel, ckpt, stagec_ckpt = task
    c = C.CELLS[cell]
    pil = C.make_pilots(testbed, prior, c["Nt"], c["Tp"], c["Nr"])[0]   # cheap; the build is not
    out = raw_file(testbed, cell, prior, pil, snr, skip, n)
    if os.path.exists(out):
        return f"exists  {os.path.basename(out)}"                      # FINISHED CHUNKS ARE SKIPPED
    t0 = time.time()
    P = build_point(testbed, cell, prior, snr, ntrain, beta, t_in, ckpt, stagec_ckpt)
    code, gen = P["code"], P["gen"]
    first = P["arms"]["R5-genie"]                       # transmit() is arm-independent; use one object
    arms = {k: v for k, v in P["arms"].items() if (not arm_sel or k in arm_sel)}
    logs = {k: [] for k in arms}
    clip = {k: [] for k in arms if stats_obj(arms[k]) is not None}
    failed = {k: [] for k in arms}
    comp = []
    rng = C.trial_rng(testbed, prior, P["Nr"], P["T"], P["Tp"], snr)
    for tr in range(skip + n):
        H = gen.sample(rng)
        k_true = getattr(getattr(gen, "prior", None), "last_k", None)
        u = rng.integers(0, 2, code.K)
        perm = rng.permutation(code.Ns)
        X, Y = first.transmit(u, perm, H, rng)
        if tr < skip:
            continue
        if k_true is not None:
            comp.append(k_true)
        for name, rx in arms.items():
            so = stats_obj(rx)
            if so is not None:
                so.reset_stats()
            try:
                logs[name].append(rx.run(Y, H, u, perm, iters))
                failed[name].append(0.0)
            except Exception:                           # 01_RULES §4: the block is CLASSIFIED, never dropped
                logs[name].append({q: np.full(iters, np.nan) for q in C.KEYS_LOG})
                failed[name].append(1.0)
            if so is not None:
                clip[name].append((so.n_clip / max(so.n_site, 1), so.shift / max(so.n_clip, 1)))

    flat = {f"{k}|{q}": np.array([l[q] for l in L]) for k, L in logs.items() for q in C.KEYS_RAW}
    for k, L in logs.items():
        for q in ("diverged", "stop_hits", "beta_used"):   # beta_used: 01_RULES §4 requires the damping actually used to be recorded
            # NOT `q in L[0]`: the substitute dict of a trial whose arm RAISED carries only KEYS_LOG, so
            # keying off trial 0 either raises KeyError (trial 0 fine, a later one raised -> the whole
            # CHUNK dies, defeating the try/except above) or drops the flag for the entire arm (trial 0
            # raised).  A missing entry stays NaN -- never 0, which would read as "did not diverge"
            # (01_RULES §4: classify, never silently zero).
            if any(q in l for l in L):
                flat[f"{k}|{q}"] = np.array([l[q] if q in l else np.full(iters, np.nan) for l in L])
        if any(failed[k]):
            flat[f"{k}|failed"] = np.array(failed[k])
    flat.update({f"{k}|clip": np.array(v) for k, v in clip.items()})
    if comp:
        flat["comp"] = np.array(comp)                   # D1 only: the true mixture component per trial
    flat.update({f"meta|{k}": np.array(v) for k, v in P["meta"].items()})
    flat.update({"run|beta": beta, "run|t_in": t_in, "run|seed": C.SEED, "run|iters": iters,
                 "run|n": n, "run|skip": skip, "run|snr": snr, "run|dtype": "complex128/float64"})
    os.makedirs(d_raw(), exist_ok=True)
    np.savez_compressed(out, **flat)

    show = [k for k in ("R2-ours-G", "R3-bigamp", "R4-scvamp", "M-ours-gmm32", "M-ours-score", "R5-genie")
            if k in logs]
    bl = " ".join(f"{k}={np.nanmean([l['blk_err'][-1] for l in logs[k]]):.2f}" for k in show)
    nf = sum(int(sum(v)) for v in failed.values())
    return (f"done    {os.path.basename(out)}  ({time.time() - t0:.0f} s)  BLER{iters}: {bl}"
            + (f"  [{nf} arm-trial exceptions recorded]" if nf else ""))


def cmd_run(a):
    testbed = a.testbed
    prior = a.prior or C.PRIOR_OF[testbed]
    cells = a.cell or list(C.CELLS)
    pts = [(cell, prior, float(s)) for cell in cells for s in (a.snr or C.CELLS[cell]["snrs"])]
    for cell, p, _ in pts:                              # fail early if a GMM fit is missing
        A.load_fits(testbed, p, C.CELLS[cell]["Nr"], a.ntrain)
    for cell in cells:
        if C.CELLS[cell]["Nr"] != 8:
            print(f"[run] {cell}: M-ours-dscore -> {NO_SCORE}  (M-ours-score is the closed-form ORACLE and DOES run here)", flush=True)
    _, why = score_prior(testbed, prior, 8, C.NT, a.ckpt, ntrain=a.ntrain)
    print(f"[run] M-ours-dscore: {why}", flush=True)
    if why.startswith("ABSENT"):
        print("[run] M-ours-dscore is NOT in this run.  The reason is written to every raw file as "
              "'meta|dscore_status', so analysis.py reports its slot as BLOCKED / FAILED-VERIFICATION "
              "instead of quietly printing a table without it (01_RULES §6).", flush=True)

    if a.stagec_ckpt:
        print(f"[run] Stage C arms ON (10_SPEC §3b/§3c): M-ours-dscore-C-{{V0,V1,V4}} + the mandatory GMM "
              f"control M-ours-bstar-scalar, from {a.stagec_ckpt}", flush=True)
        print(f"[run] Stage C gate record: {gate_verdict(a.stagec_ckpt)}", flush=True)
    tasks = [pt + (s, min(a.chunk, a.n - s), a.ntrain, a.beta, a.tin, a.iters, a.arm, a.ckpt, a.stagec_ckpt)
             for pt in pts for s in range(0, a.n, a.chunk)]
    tasks = [(testbed,) + t for t in tasks]
    tasks.sort(key=lambda t: (t[4], -C.CELLS[t[1]]["Nr"]))   # first chunks of every point early; 8x4 first
    jobs = min(os.cpu_count(), len(tasks))
    print(f"[run] {testbed} {len(pts)} points x n={a.n} -> {len(tasks)} tasks on {jobs} workers "
          f"(prior {prior}, cells {cells}, chunk {a.chunk}) -> {d_raw()}", flush=True)
    t0 = time.time()
    if jobs <= 1:
        for i, t in enumerate(tasks):
            print(f"{i + 1}/{len(tasks)} {run_task(t)}", flush=True)
    else:
        with mp.Pool(jobs, initializer=_init, initargs=(TAG,)) as pool:
            for i, msg in enumerate(pool.imap_unordered(run_task, tasks)):
                print(f"{i + 1}/{len(tasks)} {msg}", flush=True)
    print(f"[run] finished in {(time.time() - t0) / 60:.1f} min -> "
          f"python runner.py analysis --testbed {testbed}" + (f" --tag {TAG}" if TAG else ""), flush=True)


# ----------------------------------------------------------------------------- smoke
def cmd_smoke(a):
    """n = 2, every arm, numbers discarded: exceptions and the key/shape signature only (test C1's rule)."""
    testbed = a.testbed
    prior = a.prior or C.PRIOR_OF[testbed]
    bad, ref = [], None
    for cell in (a.cell or ["C1"]):
        snr = float((a.snr or [C.CELLS[cell]["snrs"][-1]])[0])
        t0 = time.time()
        P = build_point(testbed, cell, prior, snr, a.ntrain, a.beta, a.tin, a.ckpt, a.stagec_ckpt)
        print(f"[smoke] {cell}: Stage C: {P['stagec']}", flush=True)
        print(f"[smoke] {testbed} {cell} prior={prior} snr={snr:g} pilots={P['pil']} "
              f"({P['Nr']}x{P['Nt']}, T={P['T']}, Tp={P['Tp']}): {len(P['arms'])} arms "
              f"{sorted(P['arms'])}  build {time.time() - t0:.1f} s", flush=True)
        if P["Nr"] != 8:
            print(f"[smoke] {cell}: M-ours-dscore -> {NO_SCORE}  (M-ours-score is the closed-form ORACLE and DOES run here)", flush=True)
        else:
            print(f"[smoke] {cell}: M-ours-dscore: {P['dscore']}", flush=True)
        rng = C.trial_rng(testbed, prior, P["Nr"], P["T"], P["Tp"], snr)
        for tr in range(2):
            H = P["gen"].sample(rng)
            u = rng.integers(0, 2, P["code"].K)
            perm = rng.permutation(P["code"].Ns)
            X, Y = P["arms"]["R5-genie"].transmit(u, perm, H, rng)
            for k, rx in P["arms"].items():
                t1 = time.time()
                try:
                    o = rx.run(Y, H, u, perm, a.iters)
                except Exception as ex:
                    bad.append(f"{cell}/{k}: EXCEPTION {type(ex).__name__}: {ex}")
                    continue
                sig = {q: np.asarray(o[q]).shape for q in C.KEYS_LOG}
                if ref is None:
                    ref = sig
                elif sig != ref:
                    bad.append(f"{cell}/{k}: shape signature {sig} != {ref}")
                if tr == 0:
                    print(f"  {cell} {k:<14} {time.time() - t1:6.2f} s/run  "
                          f"finite={bool(np.all(np.isfinite(o['nmse'])))}", flush=True)
    print(f"[smoke] {'OK: no exceptions, identical key/shape signature across arms' if not bad else 'PROBLEMS:'}",
          flush=True)
    for b in bad:
        print("  " + b, flush=True)
    return 1 if bad else 0


# ----------------------------------------------------------------------------- tests (07_SPEC)
def cmd_tests(a):
    import tests as TS
    which, ran, skipped = [], [], []
    for name, group, have, why in (
            ("B/S/C", TS.BSC, True, ""),
            ("M", TS.M_TESTS, True, ""),
            ("L", TS.L_TESTS, True, ""),
            ("D", getattr(TS, "D_TESTS", None), os.path.exists(SIGMA_GRID),
             "conf/results/sigma_grid.txt absent (A4 not run)"),
            ("T", getattr(TS, "T_TESTS", None), os.path.exists(os.path.join(C.CONF, "code", "d2.py")),
             "conf/code/d2.py absent (B1 not built)")):
        if not group:
            skipped.append(f"{name}-tests: tests.py defines no {name}_TESTS yet"
                           + ("  (T2a..T2e live in d2.tests_T2 -- `runner.py testbed`)" if name == "T" else ""))
        elif not have:
            skipped.append(f"{name}-tests: {why}")
        else:
            which += list(group)
            ran.append(f"{name}({len(group)})")
    rows = TS.run(which)
    txt = TS.fmt(rows)
    out = tagged(os.path.join(C.CONF, "results", "tests.txt"))
    with open(out, "w") as f:
        f.write(C.header(a.testbed, extra=[f"content     : conf/07_SPEC_tests.md -- groups run: {' '.join(ran)}"]
                         + [f"NOT RUN     : {s}" for s in skipped]) + "\n\n" + txt + "\n")
    for s in skipped:
        print("[tests] NOT RUN -- " + s, flush=True)
    print(txt.splitlines()[-1], flush=True)
    print(f"[tests] -> {out}", flush=True)
    return 1 if any(v == "FAIL" for _, v, *_ in rows) else 0


# ----------------------------------------------------------------------------- lemma / sigma (A3, A4/B3)
def cmd_lemma(a):
    import lemma as LM
    if TAG:                       # lemma.py keeps its output paths as module constants and is not ours to
        LM.OUT, LM.FIG = tagged(LM.OUT), tagged(LM.FIG)      # edit -- redirect them here instead
    txt, err, sha = LM.run_unmodified(log=tagged(os.path.join(C.CONF, "logs", "lemma.log")))
    t, tw, lc4, lc2 = LM.write_results(txt)
    e1, e2 = LM.figure()
    print(f"[lemma] {os.path.relpath(LM.SRC, C.REPO)} (sha {sha}) run unmodified: "
          f"max|tanh-E| = {t:.3e} (<= 1e-14), Tweedie FD = {tw:.3e} (<= 1e-9); "
          f"Lc=4 err {lc4:.3e} / Lc=2 err {lc2:.3e}", flush=True)
    print(f"[lemma] -> {LM.OUT}  {LM.FIG} (figure max err {e1:.1e} / {e2:.1e})", flush=True)
    if err.strip():
        print("[lemma] script stderr:\n" + err, flush=True)
    return 0


def cmd_sigma(a):
    """04_SPEC §3.  The grid is FROZEN once measured: training, GA-GD and GB' all read
    conf/results/sigma_grid_<testbed>.npz, so re-measuring it silently would move the ruler under every
    number already taken with it.  --tag X writes a separate grid; replacing the frozen one needs an
    explicit --force-regrid."""
    import sigma as SG
    frozen = os.path.join(C.CONF, "results", f"sigma_grid_{a.testbed}.npz")
    if a.force_regrid and TAG:
        sys.exit("--force-regrid applies only to the untagged frozen grid; --tag X already writes elsewhere")
    if not TAG and os.path.exists(frozen) and not a.force_regrid:
        sys.exit(f"refusing to overwrite {frozen}: the sigma grid is FROZEN (04_SPEC §3) and every GA-GD "
                 f"gate and every score arm reads it.  Use --tag X for a separate grid, or --force-regrid "
                 f"to replace the frozen one deliberately.")
    cells = a.cell or [c for c in C.CELLS if C.CELLS[c]["Nr"] == 8]     # the array the score net is for
    n = a.n if a.n != 640 else SG.N_MEAS                                # --n's default is the RUN default
    res, prior = SG.measure(a.testbed, cells, prior=a.prior, n=n)
    nu, sig, out = SG.write(a.testbed, res, prior, tag=TAG)
    print(f"[sigma] {a.testbed} prior={prior} cells={cells}: grid of {len(nu)} points, "
          f"nu_q in [{nu[0]:.3e}, {nu[-1]:.3e}], sigma_t in [{sig[0]:.3e}, {sig[-1]:.3e}] -> {out}", flush=True)
    return 0


# ----------------------------------------------------------------------------- train / gate (A5, B3)
LADDER = os.path.join(C.CONF, "LADDER.md")


def _need(name, why):
    try:
        return __import__(name)
    except ImportError:
        sys.exit(f"conf/code/{name}.py is not available yet -- {why}")


def _array(a):
    """The (Nr, Nt) the score model is trained and gated for.  DECISIONS 2026-09-20 01:55: the ladder is
    run for 8x4 (cells C1/C2) only; --cell asks for another geometry explicitly."""
    return (C.CELLS[a.cell[0]]["Nr"], C.CELLS[a.cell[0]]["Nt"]) if a.cell else (8, C.NT)


def _ckpts(score, testbed, rung=None, attempt=None, ckpt=None):
    """Every ladder checkpoint of this testbed, --rung / --attempt narrowing it, --ckpt overriding it."""
    if ckpt:
        return [ckpt]
    out = []
    for r in ([rung] if rung else list(score.RUNGS)):
        for at in ([attempt] if attempt else range(1, score.MAX_ATTEMPTS + 1)):
            p = score.ckpt_path(r, at, testbed, d_ckpt())
            if os.path.exists(p):
                out.append(p)
    return out


def cmd_train(a):
    """One ladder attempt.  score.py owns the trainer AND conf/LADDER.md: the runner calls score.train and
    hands the result straight to score.ladder_append, so there is exactly ONE row format and ONE writer
    (04_SPEC §4).  Append-only, ABORTED attempts included (01_RULES §5).

    The verdict of a freshly trained attempt is UNGATED: GA-GD are measured by `runner.py gate`, and
    calling an untested attempt PASS or FAIL here would put a judgement in the log that nothing measured."""
    score = _need("score", "it is the score-ladder trainer (04_SPEC §4)")
    rung, attempt = a.rung or "L1", a.attempt or 1
    prior = a.prior or C.PRIOR_OF[a.testbed]
    Nr, Nt = _array(a)
    os.makedirs(d_ckpt(), exist_ok=True)
    cpath = a.ckpt or score.ckpt_path(rung, attempt, a.testbed, d_ckpt())
    lpath = tagged(os.path.join(C.CONF, "logs", f"train_{rung}_a{attempt}_{a.testbed}.log"))
    res = score.train(rung, attempt, a.testbed, prior, Nr, Nt, device=a.device, ckpt=cpath, log_path=lpath)
    res.setdefault("verdict", "ABORTED" if res.get("aborted") else "UNGATED")
    row = score.ladder_append(res, path=tagged(LADDER))
    print(f"[train] {rung} a{attempt} {a.testbed}/{prior} {Nr}x{Nt} -> {cpath}", flush=True)
    print(f"[train] {tagged(LADDER)} += {row.rstrip()}", flush=True)
    print(f"[train] verdict stays UNGATED until `runner.py gate --testbed {a.testbed}"
          + (f" --tag {TAG}" if TAG else "") + "` measures GA-GD.", flush=True)
    return 0


def _gd_row(r):
    """(GD, GD_trace) at ONE sigma grid point.

    GD (04_SPEC §5) is "the relative error of the Jacobian/divergence estimate that D-14 uses".  D-14 is
    RouteAClip._matrix_site: it builds SigH = nu*J, symmetrises it and INVERTS it, so what it consumes is
    the FULL Wirtinger matrix, not tr(J)/N.  GD is therefore the relative Frobenius error of J; the old
    scalar is kept and reported as GD_trace, and is NOT the gate (conf/DECISIONS.md 2026-09-20 12:35;
    01_RULES §1 -- of two readings take the one unfavourable to our claim, and the full matrix is strictly
    harder to pass).  Tolerance 0.20 unchanged.  A non-finite entry is propagated, never replaced."""
    if "J_rel_fro" in r:
        return float(r["J_rel_fro"]), float(r.get("GD_trace", r.get("GD", float("nan"))))
    return float(r.get("GD", float("nan"))), float(r.get("GD_trace", float("nan")))


def _gd(G):
    """(GD, GD_trace) over the whole grid.  np.max, not the builtin: a NaN grid point must propagate and
    fail the gate (01_RULES §4 -- classify, never silently drop)."""
    rows = G.get("per_sigma") or []
    if rows:
        p = [_gd_row(r) for r in rows]
        return float(np.max([x[0] for x in p])), float(np.max([x[1] for x in p]))
    return float(G.get("GD", float("nan"))), float(G.get("GD_trace", float("nan")))


GATE_COLS = ("nu", "sigma", "GA", "GB", "GC", "GD", "GD_trace", "herm_res",
             "nmse_hat", "nmse_star", "alpha_hat", "alpha_star")


def _block_D1(score, ckpt, Nr, Nt, prior, a):
    G = score.gates_D1(ckpt, Nr, Nt, prior=prior, device=a.device)
    gd, gdt = _gd(G)
    tol = G.get("tol") or score.GATE_TOL
    val = dict(GA=float(G["GA"]), GB=float(G["GB"]), GC=float(G["GC"]), GD=gd)
    ok = {k: bool(val[k] <= tol[k]) for k in val}          # NaN <= tol is False -> FAIL, by design
    L = [f"=== {G.get('rung', '?')} attempt {G.get('attempt', '?')}   {ckpt}",
         f"    hp          {G.get('hp', {})}",
         f"    evaluated on n_eval={G.get('n_eval', '?')} held-out samples (common.train_rng stream 10), "
         f"n_jac={G.get('n_jac', '?')}, {G.get('Nr', Nr)}x{G.get('Nt', Nt)}, prior {G.get('prior', prior)}"]
    for k in ("GA", "GB", "GC", "GD"):
        L.append(f"    {k:<9} {val[k]:13.5e}   <= {tol[k]:<9g}  {'PASS' if ok[k] else 'FAIL'}")
    L += [f"    {'GD_trace':<9} {gdt:13.5e}   relative error of tr(J)/N -- REPORTED, NOT the gate",
          f"    VERDICT   {'PASS' if all(ok.values()) else 'FAIL'}   "
          f"(PASS = GA and GB and GC and GD, 04_SPEC §5)",
          "",
          "    per sigma grid point (the grid is the FROZEN A4 measurement; GD = full-matrix J_rel_fro)",
          "    " + f"{'k':>3} " + " ".join(f"{c:>13}" for c in GATE_COLS) + f" {'n_jac':>6}"]
    for r in G.get("per_sigma") or []:
        g, t = _gd_row(r)
        d = dict(r, GD=g, GD_trace=t)
        L.append(f"    {int(d.get('k', -1)):>3} "
                 + " ".join(f"{float(d.get(c, float('nan'))):13.5e}" for c in GATE_COLS)
                 + f" {int(d.get('n_jac', 0)):>6}")
    # 04_SPEC §4's ladder row carries GA|GB|GC|GD, but the row written at TRAIN time cannot: nothing has
    # measured them yet.  So the gate appends its own row (LADDER.md is append-only -- the UNGATED row is
    # never rewritten).  This is what makes the ladder log self-contained evidence.
    try:
        score.ladder_append(dict(G, rung=G.get("rung"), attempt=G.get("attempt"),
                                 GD_trace=gdt, verdict="PASS" if all(ok.values()) else "FAIL",
                                 note=f"GATED from {os.path.basename(str(ckpt))}; GD = full-matrix J_rel_fro "
                                      f"(GD_trace {gdt:.4g} reported, not gated); "
                                      f"n_eval={G.get('n_eval','?')} n_jac={G.get('n_jac','?')}"),
                            path=tagged(LADDER))
    except Exception as ex:                       # a logging failure must never lose the measured numbers
        L.append(f"    [warn] could not append the gate row to LADDER.md: {type(ex).__name__}: {ex}")
    return L + [""]


def _block_D2(score, ckpt, Nr, Nt, prior, a):
    hp, _, llv, bstar, _ = A.module_h_priors(a.testbed, prior, Nr, Nt)
    G = score.gb_prime(ckpt, hp[bstar], a.testbed, Nr, Nt, prior=prior, device=a.device)
    rows = G.get("per_sigma") or []
    cols = [c for c in ("nu", "sigma", "nmse_gmm", "nmse_model", "nmse_exact", "excess")
            if rows and c in rows[0]]
    L = [f"=== {ckpt or 'NO CHECKPOINT -- the GMM reference alone'}",
         f"    GMM prior = b* = {bstar} (validation log-likelihood {llv.get(bstar, float('nan')):.4f}): the "
         f"GMM arm is compared at its OWN best configuration, never a weakened one (01_RULES §5).",
         f"    worst excess (diffusion vs GMM) = {float(G.get('worst_excess', float('nan'))):+.4%}",
         f"    {G.get('note', '')}",
         "",
         "    " + f"{'k':>3} " + " ".join(f"{c:>13}" for c in cols)]
    for r in rows:
        L.append(f"    {int(r.get('k', -1)):>3} "
                 + " ".join(f"{float(r.get(c, float('nan'))):13.5e}" for c in cols))
    return L + ["",
                "    GA-GD do not exist on D2: there is no exact score to compare against (04_SPEC §6).",
                "    GB' is REPORT-ONLY -- the arm set was fixed by the D1 gates before any D2 number.",
                ""]


def cmd_gate(a):
    """D1: the pre-registered quality gates GA-GD (04_SPEC §5) -> conf/results/gate_D1.txt.
    D2: GB' only -- there is no exact score there, and GB' is REPORTED, never used to select (04_SPEC §6).

    The file is WRITTEN, not merely printed: 00_GOAL §4 lists gate_D<x>.txt with per-rung NUMBERS (not
    PASS/FAIL letters) as the evidence that the ladder was judged by the gates and not by a BLER."""
    score = _need("score", "it evaluates the pre-registered gates (04_SPEC §5)")
    prior = a.prior or C.PRIOR_OF[a.testbed]
    Nr, Nt = _array(a)
    out = tagged(os.path.join(C.CONF, "results", f"gate_{a.testbed}.txt"))
    cps = _ckpts(score, a.testbed, a.rung, a.attempt, a.ckpt)
    filt = " (filter: " + " ".join(f"{k}={v}" for k, v in (("rung", a.rung), ("attempt", a.attempt),
                                                           ("ckpt", a.ckpt)) if v) + ")" \
        if (a.rung or a.attempt or a.ckpt) else ""
    L = [C.header(a.testbed, extra=[
        "content     : conf/04_SPEC_diffusion.md " + ("§5 -- the pre-registered quality gates GA-GD, on "
                                                      "every ladder checkpoint" if a.testbed == "D1" else
                                                      "§6 -- GB', the REPORT-ONLY comparison"),
        f"checkpoints : {len(cps)} found under {d_ckpt()}{filt}",
        f"device      : {a.device} for the gate only; the receiver stays CPU/complex128 for every arm",
        "judgement   : the ladder is judged by THESE numbers and never by a BLER (01_RULES §5).",
    ]), C.D1_WARNING if a.testbed == "D1" else C.D2_WARNING, ""]
    if a.testbed == "D1":
        L += ["GA -- STRUCTURAL ZERO.  READ THIS BEFORE READING ANY GA NUMBER BELOW.",
              "-" * 110, getattr(score, "GA_NOTE", GA_NOTE), "-" * 110, "",
              "GD -- the FULL Wirtinger matrix (relative Frobenius error of J), tolerance 0.20 unchanged.",
              "     GD_trace (relative error of tr(J)/N) is reported beside it and is NOT the gate.",
              "     conf/DECISIONS.md 2026-09-20 12:35; fixed before any checkpoint was gated.", ""]
    if not cps:
        L += ["!" * 110,
              f"NO CHECKPOINT FOUND under {d_ckpt()} -- no ladder attempt has produced one.",
              "M-ours-dscore is therefore ABSENT from the result tables.  Its slot stays",
              "BLOCKED / FAILED-VERIFICATION; it is never quietly dropped (01_RULES §6).",
              "!" * 110, ""]
    blk = _block_D1 if a.testbed == "D1" else _block_D2
    for p in cps:
        L += blk(score, p, Nr, Nt, prior, a)
    if a.testbed == "D2" and not cps:
        L += _block_D2(score, None, Nr, Nt, prior, a)       # GB' still reports the GMM reference
    txt = "\n".join(L) + "\n"
    with open(out, "w") as f:
        f.write(txt)
    print(txt, flush=True)
    print(f"[gate] {a.testbed}: {len(cps)} checkpoint(s) -> {out}", flush=True)
    return 0


# ----------------------------------------------------------------------------- testbed D2 verification (B1)
def cmd_testbed(a):
    """d2.tests_T2(prior, Nr, Nt, Tp) -> rows shaped exactly like conf/code/tests.py's, so tests.fmt prints
    both in one table.  T2d is the gate: if it FAILs, Stage B does not start (00_GOAL §3, 01_RULES §4) --
    the runner says so and exits non-zero rather than letting the pipeline continue."""
    d2 = _need("d2", "it is the D2 generator and its T2a..T2e verification (05_SPEC §2)")
    import tests as TS
    prior = a.prior or C.PRIOR_OF["D2"]
    cells = a.cell or ["C1"]                                   # C1 = 8x4, Tp=2, the headline geometry
    rows = []
    for cell in cells:
        c = C.CELLS[cell]
        r = d2.tests_T2(prior, c["Nr"], c["Nt"], c["Tp"])
        rows += [((f"{cell}:{t[0]}" if len(cells) > 1 else t[0]),) + tuple(t[1:]) for t in r]
    txt = TS.fmt(rows)
    out = os.path.join(C.CONF, "results", "testbed_D2" + (f"_{TAG}" if TAG else "") + ".txt")
    with open(out, "w") as f:
        f.write(C.header("D2", extra=[
            f"content     : conf/05_SPEC_testbed_D2.md §2 -- T2a..T2e on the D2 generator (prior {prior}, "
            f"cells {cells})",
            "gate        : T2d FAIL => Stage B does not start; an unverified testbed's numbers are unusable.",
        ]) + "\n\n" + txt + "\n")
    print(txt, flush=True)
    print(f"[testbed] -> {out}", flush=True)
    bad = [t for t, v, *_ in rows if v == "FAIL"]
    if any("T2d" in t for t in bad):
        print("[testbed] T2d FAILED -- conditional Gaussianity is NOT broken by this generator. "
              "Stage B is BLOCKED (00_GOAL §3); record it in conf/BLOCKERS.md and wait for the user.",
              flush=True)
    return 1 if bad else 0


# ----------------------------------------------------------------------------- fit: the D2 GMM re-fits (B2)
def _sets(prior, Nr, Nt, ntrain):
    """The ONE training set (stream 7) that the GMM and the diffusion model share, plus validation (8)
    and a held-out test set (10) -- exactly the exp_0925 split, on the D2 streams (common.train_rng)."""
    gen = C.make_gen("D2", prior, Nr, Nt)
    return gen, tuple(gen.sample_vecs(C.train_rng("D2", prior, Nr, w), m)
                      for w, m in ((7, ntrain), (8, N_VAL), (10, N_VAL)))


def fit_task(task):
    from t2_gmm import fit_gmm_em
    prior, Nr, Nt, fam, K, kappa, r, ntrain, iters = task
    t0 = time.time()
    gen, (X, Xv, Xt) = _sets(prior, Nr, Nt, ntrain)
    f = fit_gmm_em(X, K, np.random.default_rng([C.SEED, C.TBID["D2"], 9, C.PID[prior], Nr, FAM[fam], K, kappa, r]),
                   n_iter=iters, kappa=float(kappa), struct=fam, dims=(Nr, Nt), Xval=Xv)
    f["ll_test"] = float(C.GMMPriorB(Nr, Nt, f["covs"], f["pi"]).log_pdf(Xt).mean())
    f["ll_train"] = float(f["ll"][f["it_best"]])
    f["sec"] = time.time() - t0
    return task[:7], f                                   # (prior, Nr, Nt, fam, K) + (kappa, restart)


def ref_task(task):
    """Reference log-likelihoods: the Gaussian sample-covariance prior (K = 1) on the same held-out sets,
    and the TRUE density where it exists (D1 only -- D2 has no closed-form prior density)."""
    prior, Nr, Nt, ntrain = task
    gen, (X, Xv, Xt) = _sets(prior, Nr, Nt, ntrain)
    g = C.GMMPriorB(Nr, Nt, (X.T @ X.conj() / len(X))[None])
    out = dict(gauss_val=float(g.log_pdf(Xv).mean()), gauss_test=float(g.log_pdf(Xt).mean()))
    lp = getattr(getattr(gen, "prior", None), "log_pdf", None)
    if lp is not None:
        out.update(true_val=float(lp(Xv).mean()), true_test=float(lp(Xt).mean()))
    return (prior, Nr), out


def cmd_fit(a):
    """05_SPEC §4 / 06_SPEC: K in {16,32,64,128} x {full, kron} x MAP shrinkage kappa x restarts, selection
    BY VALIDATION LOG-LIKELIHOOD ONLY -- BLER is never consulted (01_RULES §5).  Mirrors exp_0925_run.cmd_fit
    so that the D2 fits are produced by the same procedure that produced the D1 fits (no weakening of the
    GMM arm).  Writes the per-K table, the fit wall-clock and the degradation relative to D1."""
    if a.testbed != "D2":
        sys.exit("fit is the D2 re-fit (05_SPEC §4); D1 reuses Demo/exp_0925_fits/ verbatim (see DECISIONS)")
    prior = a.prior or C.PRIOR_OF["D2"]
    cells = a.cell or list(C.CELLS)
    Nrs = sorted({C.CELLS[c]["Nr"] for c in cells})
    os.makedirs(d_fits_d2(), exist_ok=True)
    todo = [(prior, Nr, C.NT, fam, K) for Nr in Nrs for fam in FAM for K in D2_KS
            if not os.path.exists(A.fit_path("D2", prior, Nr, fam, K, a.ntrain))]
    tasks = [t + (kap, r, a.ntrain, a.fit_iters) for t in todo
             for kap in (KAPPAS if t[3] == "full" else (0,)) for r in range(a.restarts)]
    tasks.sort(key=lambda t: -t[1] * t[4])                     # the expensive (large Nr, large K) fits first
    print(f"[fit] D2 prior={prior}: {len(todo)} fits -> {len(tasks)} EM runs on "
          f"{min(os.cpu_count(), max(len(tasks), 1))} workers (ntrain={a.ntrain}, n_val=n_test={N_VAL}, "
          f"kappa {KAPPAS}, restarts {a.restarts}, K {D2_KS}) -> {d_fits_d2()}", flush=True)
    t0 = time.time()
    res = {}
    with mp.Pool(min(os.cpu_count(), max(len(tasks), 1)), initializer=_init, initargs=(TAG,)) as pool:
        refs = dict(pool.map(ref_task, sorted({(t[0], t[1], t[2], a.ntrain) for t in todo})))
        for i, (key, f) in enumerate(pool.imap_unordered(fit_task, tasks)):
            res.setdefault(key[:5], {})[key[5:]] = f
            print(f"  {i + 1}/{len(tasks)} {key}: iters {f['n_iter']} best@{f['it_best']} "
                  f"reseeds {f['n_reseed']} ll_train {f['ll_train']:.3f} ll_val {f['ll_val']:.3f} "
                  f"({f['sec']:.0f} s)", flush=True)
    for (p, Nr, Nt, fam, K), rs in sorted(res.items()):
        kb = max(rs, key=lambda k: rs[k]["ll_val"])            # selection: validation log-likelihood ONLY
        f, ref, cand = rs[kb], refs[(p, Nr)], sorted(rs)
        np.savez_compressed(A.fit_path("D2", p, Nr, fam, K, a.ntrain),
                            pi=f["pi"], covs=f["covs"], Chat=f["Chat"], ll=f["ll"], kappa=kb[0], restart=kb[1],
                            it_best=f["it_best"], n_iter=f["n_iter"], n_reseed=f["n_reseed"],
                            ll_train=f["ll_train"], ll_val=f["ll_val"], ll_test=f["ll_test"],
                            gauss_val=ref["gauss_val"], gauss_test=ref["gauss_test"],
                            sec=sum(rs[c]["sec"] for c in cand), sec_best=f["sec"],
                            cand=np.array(cand), cand_ll_val=np.array([rs[c]["ll_val"] for c in cand]),
                            cand_ll_test=np.array([rs[c]["ll_test"] for c in cand]),
                            ntrain=a.ntrain, n_val=N_VAL)
        print(f"[fit] {p} Nr={Nr} {fam:<4} K={K:<3}: kappa {kb[0]:>3} restart {kb[1]} best@{f['it_best']:<3} "
              f"train-val gap {f['ll_train'] - f['ll_val']:6.3f}  ll_test - ll_test(Gaussian) = "
              f"{f['ll_test'] - ref['gauss_test']:6.3f} nat  pi_min {f['pi'].min():.4f}  "
              f"({sum(rs[c]['sec'] for c in cand) / 60:.1f} min over {len(cand)} EM runs)", flush=True)
    write_fit_table(prior, Nrs, a.ntrain)
    print(f"[fit] finished in {(time.time() - t0) / 60:.1f} min", flush=True)
    return 0


def write_fit_table(prior, Nrs, ntrain):
    """conf/results/gmm_fit_D2.txt -- per-K train/val likelihood, over-fit gap, wall-clock, and the
    DEGRADATION RELATIVE TO THE D1 FITS (05_SPEC §4: the second piece of evidence that the testbed really
    broke conditional Gaussianity).  Numbers only; the reading is the user's (08_SPEC §5)."""
    out = os.path.join(C.CONF, "results", "gmm_fit_D2" + (f"_{TAG}" if TAG else "") + ".txt")
    d1p = C.PRIOR_OF["D1"]
    with open(out, "w") as f:
        f.write(C.header("D2", extra=[
            f"content     : conf/05_SPEC_testbed_D2.md §4 -- GMM re-fit on D2 (prior {prior}), "
            f"K {D2_KS} x {{full, kron}} x kappa {KAPPAS} x restarts, ntrain {ntrain}, n_val = n_test = {N_VAL}",
            "selection   : VALIDATION log-likelihood only.  BLER is never consulted (01_RULES §5).",
            f"D1 fits     : {A.D1_FITS} (prior {d1p}, K {A.D1_KS}) -- reused verbatim, see DECISIONS",
        ]) + "\n" + C.D2_WARNING + "\n\n")
        for Nr in Nrs:
            f.write(f"Nr = {Nr} x Nt = {C.NT}\n")
            f.write(f"  {'fam':<5} {'K':>4} {'kappa':>6} {'ll_train':>10} {'ll_val':>10} {'gap':>8} "
                    f"{'ll_test':>10} {'-gauss':>8} {'reseed':>7} {'EM min':>8}\n")
            d2f = {}
            for fam in FAM:
                for K in D2_KS:
                    p = A.fit_path("D2", prior, Nr, fam, K, ntrain)
                    if not os.path.exists(p):
                        continue
                    z = np.load(p)
                    d2f[(fam, K)] = z
                    f.write(f"  {fam:<5} {K:>4} {int(z['kappa']):>6} {float(z['ll_train']):>10.3f} "
                            f"{float(z['ll_val']):>10.3f} {float(z['ll_train']) - float(z['ll_val']):>8.3f} "
                            f"{float(z['ll_test']):>10.3f} "
                            f"{float(z['ll_test']) - float(z['gauss_test']):>8.3f} "
                            f"{int(z['n_reseed']):>7} {float(z['sec']) / 60:>8.1f}\n")
            if d2f:
                best = max(d2f, key=lambda k: float(d2f[k]["ll_val"]))
                f.write(f"  b* (validation log-likelihood) = {best[0]} K={best[1]}   "
                        f"ll_val {float(d2f[best]['ll_val']):.3f}\n")
            f.write("\n  degradation relative to D1 (05_SPEC §4)\n")
            f.write("  Absolute log-likelihoods of two DIFFERENT distributions are not comparable, so the\n"
                    "  comparable quantity is what the mixture buys over the Gaussian sample-covariance prior\n"
                    "  on the same held-out set:  G := ll_test(GMM) - ll_test(Gaussian)  [nat/sample].\n")
            f.write(f"  {'fam':<5} {'K':>4} {'G(D2)':>9} {'G(D1)':>9} {'D2-D1':>9} {'gap(D2)':>9} {'gap(D1)':>9}"
                    f" {'KL(D1)':>9}\n")
            for fam in FAM:
                for K in D2_KS:
                    z2 = d2f.get((fam, K))
                    p1 = A.fit_path("D1", d1p, Nr, fam, K, ntrain)
                    z1 = np.load(p1) if os.path.exists(p1) else None
                    if z2 is None and z1 is None:
                        continue
                    g2 = (float(z2["ll_test"]) - float(z2["gauss_test"])) if z2 is not None else np.nan
                    # D1 fits store KL(true||fit) and KL(true||Gaussian); their difference is the same G.
                    g1 = (float(z1["kl_test_gauss"]) - float(z1["kl_test"])) if z1 is not None else np.nan
                    gp2 = (float(z2["ll_train"]) - float(z2["ll_val"])) if z2 is not None else np.nan
                    gp1 = (float(z1["ll_train"]) - float(z1["ll_val"])) if z1 is not None else np.nan
                    kl1 = float(z1["kl_test"]) if z1 is not None else np.nan
                    f.write(f"  {fam:<5} {K:>4} {g2:>9.3f} {g1:>9.3f} {g2 - g1:>9.3f} "
                            f"{gp2:>9.3f} {gp1:>9.3f} {kl1:>9.3f}\n")
            f.write("  KL(D1) = KL(true || fit) on the D1 test set [nat/sample]; D2 has no closed-form true\n"
                    "  density, so no KL column exists there (05_SPEC §3).\n\n")
    print(f"[fit] -> {out}", flush=True)


# ----------------------------------------------------------------------------- analysis (08_SPEC)
def cmd_analysis(a):
    """analysis.main(testbed, tag) reads conf/raw[_tag]/ and writes conf/results/tables_<testbed>[_tag].txt."""
    import warnings
    analysis = _need("analysis", "it builds the 08_SPEC tables")
    with warnings.catch_warnings():
        # NARROW: only numpy's all-NaN aggregation warning, which the genie arm triggers by construction
        # (its NMSE is NaN for every block).  A real divide-by-zero or invalid value in the aggregation
        # stays visible -- silencing RuntimeWarning wholesale would hide it (08_SPEC §5).
        for msg in ("All-NaN slice encountered", "All-NaN axis encountered", "Mean of empty slice"):
            warnings.filterwarnings("ignore", message=msg, category=RuntimeWarning)
        print(analysis.main(a.testbed, TAG), flush=True)
    return 0


# ----------------------------------------------------------------------------- CLI
CMDS = dict(tests=cmd_tests, smoke=cmd_smoke, run=cmd_run, lemma=cmd_lemma, sigma=cmd_sigma,
            train=cmd_train, gate=cmd_gate, testbed=cmd_testbed, fit=cmd_fit, analysis=cmd_analysis)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="runner.py", formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__.split("Structure (")[0].rstrip(),
        epilog="No --jobs flag by design (01_RULES §4: the default is all cores).")
    ap.add_argument("cmd", choices=list(CMDS))
    ap.add_argument("--testbed", default="D1", choices=list(C.TBID), help="D1 = grid GMM (instrument), D2 = sparse specular (claim)")
    ap.add_argument("--cell", nargs="+", choices=list(C.CELLS), default=None, help="default: every cell (smoke: C1)")
    ap.add_argument("--snr", nargs="+", type=float, default=None, help="default: the cell's SNR grid")
    ap.add_argument("--prior", default=None, choices=list(C.PID), help="default: S on D1, S2 on D2")
    ap.add_argument("--n", type=int, default=640, help="trials per point (01_RULES: never below 640 for a real run)")
    ap.add_argument("--chunk", type=int, default=40, help="trials per resumable task")
    ap.add_argument("--arm", nargs="+", default=None, help="subset of arms to run (requires --tag)")
    ap.add_argument("--iters", type=int, default=C.N_ITER, help="outer iterations, 16 for every arm")
    ap.add_argument("--beta", type=float, default=C.BETA, help="BiG-AMP damping (01_RULES §4: 0.7 -> 0.5 -> 0.3)")
    ap.add_argument("--tin", type=int, default=C.T_IN, help="BiG-AMP inner iterations")
    ap.add_argument("--seed", type=int, default=C.SEED)
    ap.add_argument("--ntrain", type=int, default=C.N_TRAIN)
    ap.add_argument("--restarts", type=int, default=RESTARTS, help="fit: EM restarts per (family, K, kappa)")
    ap.add_argument("--fit-iters", type=int, default=FIT_ITERS, help="fit: maximum EM iterations")
    ap.add_argument("--device", default=None, help="cpu (default for run/tests) or cuda (default for train/gate)")
    ap.add_argument("--dtype", default="complex128", help="receiver dtype -- complex128 only (01_RULES §9.3)")
    ap.add_argument("--rung", default=None, help="score ladder rung L1..L6 (04_SPEC §4); train: default L1, "
                                                 "gate: default = every rung with a checkpoint")
    ap.add_argument("--attempt", type=int, default=None, help="attempt inside a rung (max 3); train: default 1, "
                                                             "gate: default = every attempt present")
    ap.add_argument("--ckpt", default=None, help="explicit checkpoint path for train/gate/run")
    ap.add_argument("--stagec-ckpt", default=None,
                    help="Stage C (10_SPEC §3b/§3c), run/smoke: ADD M-ours-dscore-C-V0 (D-14 matrix site), "
                         "-C-V1 (psd_project=True), -C-V4 (hsite=scalar, scal=belief) built from THIS "
                         "checkpoint, plus the mandatory GMM control M-ours-bstar-scalar.  OPT-IN: without "
                         "it the arm set is exactly the pre-registered one, and --ckpt / M-ours-dscore are "
                         "untouched either way.  Requires --tag (Stage C writes raw_C/, tables_D2_C.txt).")
    ap.add_argument("--tag", default="", help="route EVERY output (raw/, ckpt/, LADDER, gates, sigma grid, "
                                              "tests, lemma, D2 fits) to suffixed paths")
    ap.add_argument("--force-regrid", action="store_true",
                    help="sigma: deliberately replace the FROZEN conf/results/sigma_grid_<testbed>.npz")
    a = ap.parse_args(argv)

    a.device = a.device or ("cuda" if a.cmd in ("train", "gate") else "cpu")
    if a.cmd in ("run", "tests", "smoke", "sigma", "fit", "analysis") and a.device != "cpu":
        sys.exit(f"--device {a.device} refused for `{a.cmd}`: the receiver is CPU/complex128 for EVERY arm "
                 "(01_RULES §9.1, §9.3) -- a per-arm precision difference invalidates table B")
    if a.dtype != "complex128":
        sys.exit(f"--dtype {a.dtype} refused: there is no complex64 receiver path; 01_RULES §9.3 requires "
                 "identical precision for every arm and G1/G2 before any reduction")
    if a.n < 640 and a.cmd == "run" and not a.tag:
        sys.exit("n < 640 is forbidden for a real run (00_GOAL §4) -- use --tag X for a smoke run")
    if a.seed != C.SEED:
        sys.exit("--seed cannot be overridden: every stream comes from common.trial_rng / common.train_rng "
                 "or the fixed constants in score.py, and no other seeding scheme exists (01_RULES §4)")
    # 01_RULES §5, equal budget: --ntrain / --restarts / --fit-iters change how much data and how much EM
    # the GMM arm gets, so a reduced-budget re-fit must never land in the pre-registered
    # conf/results/gmm_fits_D2/ that the headline B4 run reads.
    changed = [f"--{k}" for k, v in (("iters", a.iters != C.N_ITER),
                                     ("beta", a.beta != C.BETA), ("tin", a.tin != C.T_IN),
                                     ("arm", a.arm is not None), ("ntrain", a.ntrain != C.N_TRAIN),
                                     ("restarts", a.restarts != RESTARTS),
                                     ("fit-iters", a.fit_iters != FIT_ITERS),
                                     # --stagec-ckpt ADDS arms to the point, so it changes the frozen arm
                                     # set: it may never write the pre-registered raw/ or tables_D2.txt.
                                     ("stagec-ckpt", a.stagec_ckpt is not None)) if v]
    if changed and a.cmd in ("run", "fit") and not a.tag:
        sys.exit(f"refusing to write the pre-registered output with {', '.join(changed)} -- pass --tag X "
                 "(01_RULES §5: the configuration is frozen before the run and not changed afterwards, and "
                 "the diffusion arm gets no more data or budget than the GMM arm)")
    if a.stagec_ckpt:
        # 10_SPEC A5: the confirmatory BLER runs ONCE.  score.load_prior reports a bad path as "ABSENT"
        # and the run would then quietly produce a table with V0/V1/V4 missing -- and there is no second
        # run to notice it in.  Resolve the path against conf/ and refuse a missing file here instead.
        p = a.stagec_ckpt if os.path.exists(a.stagec_ckpt) else os.path.join(C.CONF, a.stagec_ckpt)
        if not os.path.isfile(p):
            sys.exit(f"--stagec-ckpt {a.stagec_ckpt}: no such file (tried it as given and under {C.CONF}). "
                     "Refusing: the Stage C score arms would be silently ABSENT from the whole run.")
        a.stagec_ckpt = os.path.abspath(p)
    _init(a.tag)
    for d in ("results", "raw", "logs", "figs", "ckpt"):
        os.makedirs(os.path.join(C.CONF, d), exist_ok=True)
    os.makedirs(d_raw(), exist_ok=True)
    return CMDS[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
