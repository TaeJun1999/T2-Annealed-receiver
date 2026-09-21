"""conf/code/analysis.py -- result tables (conf/08_SPEC_analysis.md).

                    *** THIS SCRIPT PRINTS NUMBERS. IT NEVER PRINTS A READING. ***
08_SPEC §5: no "significant / there is a gain / our method is better" sentences, no conclusion drawn
under insufficient power, no mean computed after dropping failed or diverged blocks (when a drop is
made, BOTH versions are printed side by side), no paper prose, and D1 and D2 are NEVER merged --
they have different arm sets (06_SPEC §1) and go to different files.  The human reads the tables.

What is here, section by section (08_SPEC section -> function):
  §1   table_A   per-cell arm comparison: BLER (95% Wilson CI) / BER / NMSE_H@16 per SNR point,
                 + SNR@BLER 0.1 (log-linear interpolation) with 90% paired bootstrap CI,
                 + failure classes stuck / cyc2 / other / diverged / raised, + clip firing rates,
                 + fit/training cost (GMM EM wall-clock s) -- never blank, "n/a" when none.
  §2   table_B   the NINE listed paired comparisons only (all-pairs = multiple-comparison problem),
                 each with the paired sign test and the SNR@0.1 gap, behind the R6/R7 power guard.
                 The decision SNRs of a pair are anchored on its BASELINE member (exp_0925's
                 pre-registered rule anchored on the GMM/baseline arm, never on one of ours), and the
                 anchor arm is printed on every row.
  §3   table_C   cross-Tp goodput envelope over C1 (Tp=2) and C2 (Tp=4).
  §3.5 table_D   training quality independent of BLER: gate_D1 / gate_D2 / gmm_fit_D2, verbatim.
  §0   headers   common.header + common.D1_WARNING / D2_WARNING + common.ARM_NOTES, on every file.

Computation routines are REUSED, not re-derived (08_SPEC preamble):
    exp_0921_analysis : wilson, sign_p, paired, row, fail_classes
    exp_0925_analysis : snr_at, fmt_at, gain, MIN_DISC
Demo/ is imported, never written (01_RULES §2).

Raw layout this module reads (06_SPEC §5, written by the runner):
    conf/raw/<testbed>_<cell>_<prior>_Nr<Nr>_T<T>_Tp<Tp>_<pil>_snr<snr>_skip<skip>_n<n>.npz
    keys "<arm>|<field>" for field in common.KEYS_RAW, each of shape (n_trials, N_ITER)   [exact]
         "<arm>|diverged" for the arms that carry one (R3-bigamp, R4-*)                   [optional]
         "meta|<k>" scalars for the point, "comp" = true mixture component per trial (D1).
Chunks of one point are concatenated in skip order and holes/overlaps WARN (exp_0925_analysis.load).

Two arm-specific reporting rules fixed by the task spec:
  * R0-pilot is the 1-PASS arm -> it is read at iteration index 0 and labelled "R0-pilot (@1)";
    the @16 trajectory of the SAME receiver is printed on its own line as "pilot_C (@16)" for context.
    (Same raw arm, two reading indices -- not two runs.)
  * R3-bigamp / R4-* carry a per-trial diverged flag.  The diverged fraction is surfaced and the
    diverged blocks STAY in every aggregate above it (08_SPEC §5 forbids dropping them).
  * "<arm>|failed" (the arm RAISED on that trial) is its OWN failure class, "raised", beside
    stuck / cyc2 / other / diverged -- otherwise an arm that threw is indistinguishable from an arm
    that converged to a wrong fixed point.  A raised block still counts as a block error and still
    stays in every aggregate.
"""
import os, re, glob, sys, warnings
import numpy as np

import common as C
from common import (ARM_NOTES, CELLS, D1_WARNING, D2_WARNING, N_ITER, NT, PRIOR_OF, header)

from exp_0921_analysis import wilson, sign_p, paired, row, fail_classes          # noqa: F401
from exp_0925_analysis import snr_at, fmt_at, gain, MIN_DISC

RESULTS = os.path.join(C.CONF, "results")
RAW = os.path.join(C.CONF, "raw")

PAT = re.compile(r"^(D1|D2)_(C\d)_([A-Z]\d?)_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")

# ----------------------------------------------------------------------------- arm sets (06_SPEC §1)
# D2 has NO R6-exactEP (no exact EP site for the true prior) and NO M-ours-score (no exact score).
# M-ours-G is the M2 equivalence-test arm only and is deliberately absent from every table.
ARMS = {
    "D1": ("R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp",
           "M-ours-gmm32", "M-ours-bstar", "M-ours-score", "M-ours-dscore", "R6-exactEP", "R5-genie"),
    "D2": ("R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp",
           "M-ours-gmm32", "M-ours-bstar", "M-ours-dscore", "R5-genie"),
}
M_ARMS = ("M-ours-gmm32", "M-ours-bstar", "M-ours-score", "M-ours-dscore")

# Stage C (10_SPEC §3b / §3c).  These arms exist only in a run launched with --stagec-ckpt, so they are NOT
# part of ARMS: _pool() appends them and _present() then keeps only the ones actually in the raw files.  A
# pre-registered run therefore produces a byte-identical table -- none of these names can appear in it.
STAGEC_ARMS = ("M-ours-dscore-C-V0", "M-ours-dscore-C-V1", "M-ours-dscore-C-V4",
               "M-ours-dscore-C-V4b", "M-ours-bstar-scalar")
STAGEC_NOTES = {
    "M-ours-dscore-C-V0": "Stage C V0 (PRIMARY) -- learned prior at N', D-14 MATRIX site, pre-registered score wiring, unchanged",
    "M-ours-dscore-C-V1": "Stage C V1 -- V0 + (F1) symmetric-PSD projection of the D-14 site (ScorePrior(psd_project=True))",
    "M-ours-dscore-C-V4": "Stage C V4 -- D-14 matrix site REPLACED by the D-13 belief scalarisation (hsite=scalar, scal=belief); "
                          "POST-HOC registered, observed in the H4 diagnostic BEFORE registration (10_SPEC §3c)",
    "M-ours-bstar-scalar": "Stage C CONTROL (10_SPEC §3c, MANDATORY) -- the b* GMM through V4's EXACT wiring: if scalarisation "
                           "also helps the GMM, the gain belongs to the SITE, not to the learned prior",
}


def _pool(testbed):
    """Arm order of the tables: the pre-registered set with the Stage C arms slotted in just above the
    bound arm (R6-exactEP / R5-genie), which stays last."""
    p = list(ARMS[testbed])
    return p[:-1] + list(STAGEC_ARMS) + p[-1:]


PILOT1 = "R0-pilot@1"          # alias injected by load_raw: R0-pilot read at iteration index 0
REF = "R2-ours-G"              # the "our model" baseline; table A quotes every gain against it


def _p(out, *a):
    s = " ".join(str(x) for x in a)
    out.append(s)
    return s


# ----------------------------------------------------------------------------- loading
def load_raw(testbed, root=None):
    """Mirror of exp_0925_analysis.load for the conf/ naming.
    -> data[(cell, prior, snr)][arm][field], meta[(cell, prior)], warns (a list of strings).

    data is keyed by (cell, prior, snr) TUPLES ONLY and meta by (cell, prior) tuples ONLY -- neither
    ever carries a book-keeping key, so a consumer may write `for (cell, prior, snr) in data`.  The
    warnings are a THIRD return value for exactly that reason; they used to be injected as
    data["__warn__"] and broke every such unpacking loop with a ValueError.

    Chunks of a point are concatenated in skip order; a gap or an overlap in the (skip, n) sequence
    WARNS and is printed, never silently repaired."""
    root = root or RAW
    pts, warns = {}, []
    for f in sorted(glob.glob(os.path.join(root, f"{testbed}_*.npz"))):
        m = PAT.match(os.path.basename(f))
        if m:
            pts.setdefault((m[2], m[3], float(m[8])), []).append((int(m[9]), int(m[10]), f))
    data, meta = {}, {}
    for key, chunks in sorted(pts.items()):
        chunks.sort()
        pos, ok = 0, True
        for skip, n, _ in chunks:
            ok &= skip == pos
            pos = skip + n
        if not ok:
            warns.append(f"  WARNING {key}: chunk sequence has holes/overlaps: {[(s, n) for s, n, _ in chunks]}")
        zs = [np.load(f) for _, _, f in chunks]
        ns = [n for _, n, _ in chunks]
        # UNION of the chunks' key sets, not chunk 0's: runner.py writes "<arm>|failed" ONLY in a chunk
        # where some trial raised, so the key set is legitimately ragged across chunks of one point.
        d = {}
        for k in sorted({k for z in zs for k in z.files}):
            a0 = next(z[k] for z in zs if k in z.files)
            if k.startswith("meta|"):
                meta.setdefault(key[:2], {})[k[5:]] = a0.item()
                continue
            if "|" not in k:
                continue                                   # "comp" (true component index) -- not used by the tables
            v, q = k.split("|", 1)
            # "run|<param>" holds the point's run parameters (beta, T_in, seed, iters, dtype ...) as 0-d
            # entries, not per-trial arrays: take them from the first chunk instead of concatenating.
            if a0.ndim == 0:
                d.setdefault(v, {})[q] = a0
                continue
            parts = []
            for z, nz in zip(zs, ns):
                if k in z.files:
                    parts.append(z[k])
                    continue
                # absent "failed" == no trial of that chunk raised (runner.py's encoding) -> zeros [exact].
                # anything else absent is UNKNOWN -> NaN, and it is announced; never silently dropped.
                parts.append(np.zeros((nz,) + a0.shape[1:]) if q == "failed"
                             else np.full((nz,) + a0.shape[1:], np.nan))
                if q != "failed":
                    warns.append(f"  WARNING {key}: '{k}' is missing from a chunk (n={nz})"
                                 f" -> filled with NaN, not dropped")
            d.setdefault(v, {})[q] = np.concatenate(parts)
        # 01_RULES §4 / 08_SPEC §5: a block whose arm RAISED is stored as an all-NaN row (runner.py, key
        # "<arm>|failed").  Such a block is CLASSIFIED as a block error and kept.  Left as NaN it would
        # (i) make wilson(int(be.sum()), n) raise and (ii) disappear from exp_0921.paired's discordant
        # counts -- both routines predate the flag, and (ii) is exactly the silent drop §5 forbids.
        for a, vv in d.items():
            be = vv.get("blk_err")
            if getattr(be, "ndim", 0) != 2:
                continue
            bad = ~np.isfinite(be)
            if bad.any():
                vv["blk_err"] = np.where(bad, 1.0, be)
                warns.append(f"  NOTE {key} {a}: {int(bad[:, -1].sum())}/{len(be)} blocks carry a non-finite "
                             f"blk_err@16 (the arm raised) -> KEPT and counted as block errors, never dropped")
        # alias: the 1-PASS reading of R0-pilot.  gain()/paired() index the LAST column, so the alias
        # carries the trajectory truncated at iteration 1 -- same trials, same blocks, different index.
        if "R0-pilot" in d:
            d[PILOT1] = {q: a[:, :1] for q, a in d["R0-pilot"].items() if getattr(a, "ndim", 0) == 2}
        data[key] = d
    return data, meta, warns


def _points(data, cell, prior):
    return sorted(k[2] for k in data if k[:2] == (cell, prior))


def _groups(data):
    return sorted({k[:2] for k in data},
                  key=lambda t: (list(CELLS).index(t[0]) if t[0] in CELLS else 99, t[1]))


def _present(data, cell, prior, testbed):
    """Arms usable for this (cell, prior): present at EVERY SNR point of the grid.  An arm missing from
    one point cannot be paired or interpolated across the grid, so it is listed as absent instead of
    being silently averaged over a shorter grid (01_RULES §6: its slot stays FAILED-VERIFICATION)."""
    ss = _points(data, cell, prior)
    return [a for a in _pool(testbed) if all(a in data[(cell, prior, s)] for s in ss)]


def _rows(present):
    """(raw arm, iteration index, printed label).  R0-pilot appears twice: @1 (its own 1-pass result)
    and @16 (the same receiver's trajectory, for context) -- task spec, 08_SPEC §1."""
    out = []
    for a in present:
        if a == "R0-pilot":
            out += [("R0-pilot", 0, "R0-pilot (@1)"), ("R0-pilot", -1, "pilot_C (@16)")]
        else:
            out.append((a, -1, a))
    return out


def _gkey(arm, it):
    return PILOT1 if (arm == "R0-pilot" and it == 0) else arm


def fit_cost(m, arm):
    """GMM EM wall-clock seconds for an arm, from the point's meta.  08_SPEC §1: this column is NEVER
    blank -- an arm that fits nothing prints n/a (01_RULES §5: the fit cost is not hidden)."""
    # the point-level "em_sec" fallback belongs ONLY to the arms that actually run EM.  R6-exactEP and
    # M-ours-score take the TRUE prior (arms.py build_baseline_arms / build_our_arms) and fit nothing:
    # quoting the GMM EM wall-clock against them invents a training cost for an oracle baseline.
    for k in (f"em_sec|{arm}", f"fit_sec|{arm}", "em_sec" if arm.startswith(("M-ours-gmm", "M-ours-bstar")) else None):
        if k and k in m:
            return f"{float(m[k]):9.1f}"
    return "      n/a"


def diverged_frac(v):
    """Fraction of blocks the arm itself flagged as diverged.  These blocks are KEPT everywhere above
    (08_SPEC §5); this line only makes their weight visible."""
    if "diverged" not in v:
        return None
    return float(np.asarray(v["diverged"])[:, -1].mean())


def raised_frac(v):
    """Fraction of blocks on which the arm itself RAISED (runner.py writes "<arm>|failed", (n,), 1.0 per
    such trial, and writes the key only when at least one trial of the chunk raised -> key absent means
    zero, exactly).  Convention, unchanged: the block counts as a block error (load_raw turns its
    non-finite blk_err into 1.0) and STAYS in every aggregate above.  Reporting it separately only stops
    it being attributed to 'other', where a thrown exception looks like a wrong fixed point."""
    return float(np.mean(np.asarray(v["failed"]))) if "failed" in v else 0.0


# ----------------------------------------------------------------------------- table A (08_SPEC §1)
def _cellfield(v, it, n):
    be = v["blk_err"][:, it]
    lo, hi = wilson(int(be.sum()), len(be))
    nm = np.nanmedian(v["nmse"][:, it]) if np.isfinite(v["nmse"][:, it]).any() else np.nan
    return f"{be.mean():.3f}({lo:.3f},{hi:.3f}) {v['ber'][:, it].mean():.1e} {nm:.2e}"


def table_A(data, meta, testbed, out):
    """Rows = arms, columns = SNR points, one table per cell.  Cell = BLER (95% Wilson CI) / BER /
    NMSE_H@16 (median over ALL blocks, failed and diverged included)."""
    _p(out, "\n" + "=" * 30, "TABLE A -- per-cell arm comparison (08_SPEC §1)", "=" * 30)
    _p(out, "cell entry = BLER (95% Wilson CI) / BER / NMSE_H  at the arm's reporting iteration")
    _p(out, "reporting iteration: @16 for every arm except R0-pilot, which is the 1-PASS arm and is read @1;")
    _p(out, "'pilot_C (@16)' is the SAME receiver's 16-iteration trajectory, printed for context only.")
    for cell, prior in _groups(data):
        snrs = _points(data, cell, prior)
        cfg = CELLS.get(cell, {})
        Nr, T, Tp = cfg.get("Nr", "?"), cfg.get("T", "?"), cfg.get("Tp", "?")
        K = NT * (T - Tp) - 6 if isinstance(T, int) else "?"
        pres = _present(data, cell, prior, testbed)
        # Arm-label column width.  16 is the PRE-REGISTERED width and stays 16 for every pre-registered
        # arm set (longest label "M-ours-dscore" / "pilot_C (@16)" = 13), so tables_D1/D2.txt regenerate
        # byte-identically; only the 18-19 char Stage C names widen it, instead of running 2-3 columns
        # ragged and mis-aligning every number under the SNR headers.
        W = max(16, max((len(x) for x in list(pres) + [l for _, _, l in _rows(pres)]), default=0))
        if not pres:
            _p(out, f"\n--- cell {cell}  prior {prior}: no arm of the {testbed} set is present at every SNR point -> no table")
            continue
        ns = [len(data[(cell, prior, s)][pres[0]]["blk_err"]) for s in snrs]
        m = meta.get((cell, prior), {})
        _p(out, f"\n--- cell {cell} ({Nr}x{NT}, T={T}, Tp={Tp}, K={K})  prior {prior}  testbed {testbed}"
                f"   n per SNR: {ns}   b* = {m.get('bstar', 'n/a')}")
        # Once a run ASKED for Stage C (meta|stagec_ckpt is present) a Stage C arm that is not in the raw
        # files is an absence that must be traced, not an arm that was never requested (01_RULES §6).  In a
        # pre-registered run the key is absent and this list is exactly ARMS[testbed], as before.
        want = list(ARMS[testbed]) + (list(STAGEC_ARMS) if "stagec_ckpt" in m else [])
        missing = [a for a in want if a not in pres]
        if missing:
            _p(out, f"  arms absent from the raw files (see 01_RULES §6 -- BLOCKED / FAILED-VERIFICATION): {missing}")
        _p(out, f"  {'arm':<{W}}" + "".join(("SNR %+.0f dB" % s).center(37) for s in snrs))
        for arm, it, lab in _rows(pres):
            _p(out, f"  {lab:<{W}}" + "".join(f"{_cellfield(data[(cell, prior, s)][arm], it, ns[i]):^37}"
                                             for i, s in enumerate(snrs)))

        # -- per-point detail rows, exp_0921_analysis.row verbatim (full BLER trajectory + fail classes)
        _p(out, "\n  per-point detail rows (exp_0921 convention M-1: BLER@1/@2/@8/@16, BER@16, NMSE median all / success-only,"
                " rescued/lost 2->16, tauL@1, failure-class %):")
        for s in snrs:
            _p(out, f"   SNR {s:+.0f} dB")
            for a in pres:
                _p(out, "  " + row(a, data[(cell, prior, s)][a]))

        # -- SNR@BLER 0.1 and the 90% PAIRED bootstrap CI of each arm's gain over the REF arm
        nmin = min(ns)
        _p(out, f"\n  SNR@BLER 0.1 (log-linear interpolation; '<=x' already below at the lowest grid point, '>x' never reached)")
        _p(out, f"  and the SNR@0.1 gain over {REF} with a 90% PAIRED bootstrap CI (same resampled trials for both arms).")
        _p(out, f"  SIGN CONVENTION (spelled out the same way as table B, so it cannot be read inverted): the number is")
        _p(out, f"  SNR@0.1(this arm) MINUS SNR@0.1({REF}).  + dB = this arm needs MORE SNR than {REF} to reach")
        _p(out, f"  BLER 0.1;  - dB = it needs LESS.")
        _p(out, f"    {'arm':<{W}} {'SNR@0.1':>8}   SNR@0.1 gap (this arm minus {REF})")
        for arm, it, lab in _rows(pres):
            gk = _gkey(arm, it)
            bl = [data[(cell, prior, s)][gk]["blk_err"][:, -1].mean() for s in snrs]
            at = fmt_at(*snr_at(snrs, bl, nmin))
            if gk == REF or len(snrs) < 2:
                g = "-- (reference)" if gk == REF else "n/a (needs >= 2 SNR points)"
            else:
                g = gain(data, cell, prior, snrs, gk, REF)["text"]
            _p(out, f"    {lab:<{W}} {at:>8}   {g}")

        # -- failure classes.  exp_0921 fail_classes splits the @16 failures into stuck / cyc2 / other;
        #    'diverged' is the arm's OWN flag and is reported beside them (it is not carved out of them).
        _p(out, "\n  failure classes at @16, as a fraction of ALL blocks (exp_0921 operational definition;"
                " diverged = the arm's own flag, raised = the arm threw on that block (runner.py '<arm>|failed');"
                " diverged AND raised blocks are KEPT in every mean above, a raised block counting as a block error):")
        _p(out, f"    {'arm  [stuck/cyc2/other/diverged/raised]':<40}" + "".join(("%+.0f dB" % s).center(32) for s in snrs))
        for arm, it, lab in _rows(pres):
            if it == 0:
                _p(out, f"    {lab:<40}" + "".join("n/a".center(32) for _ in snrs) + "  (1-pass arm: no trajectory to classify)")
                continue
            cells_ = []
            for s in snrs:
                v = data[(cell, prior, s)][arm]
                st, cy, ot = fail_classes(v)
                dv = diverged_frac(v)
                cells_.append(f"{st:.3f}/{cy:.3f}/{ot:.3f}/" + (f"{dv:.3f}" if dv is not None else "n/a  ")
                              + f"/{raised_frac(v):.3f}")
            _p(out, f"    {lab:<40}" + "".join(c.center(32) for c in cells_))

        # -- clip firing rates
        _p(out, "\n  clip firing rates, mean over trials x iterations "
                "(tauL = variance-floor clip of the detector site, alphaD = alpha^D clip to [eps, 1-eps]):")
        _p(out, f"    {'arm':<{W}}" + "".join(f"{('%+.0f dB' % s):>18}" for s in snrs))
        for a in pres:
            cells_ = []
            for s in snrs:
                v = data[(cell, prior, s)][a]
                t = float(np.mean(v["tauL_clip_frac"])) if "tauL_clip_frac" in v else np.nan
                al = float(np.mean(v["alphaD_clip"])) if "alphaD_clip" in v else np.nan
                cells_.append(f"{t:8.4f}/{al:<8.4f}")
            _p(out, f"    {a:<{W}}" + "".join(f"{c:>18}" for c in cells_))

        # -- 08_SPEC §5: a mean over a subset is only printed NEXT TO the mean over everything
        _p(out, "\n  NMSE_H@16 median, WITH and WITHOUT the failed blocks (08_SPEC §5: both versions, never only one):")
        _p(out, f"    {'arm':<{W}}" + "".join(f"{('%+.0f dB' % s):>24}" for s in snrs) + "     [all blocks / success-only]")
        for a in pres:
            cells_ = []
            for s in snrs:
                v = data[(cell, prior, s)][a]
                ok = v["blk_err"][:, -1] == 0
                allm = np.nanmedian(v["nmse"][:, -1]) if np.isfinite(v["nmse"][:, -1]).any() else np.nan
                okm = np.nanmedian(v["nmse"][ok, -1]) if (ok.any() and np.isfinite(v["nmse"][ok, -1]).any()) else np.nan
                cells_.append(f"{allm:.3e}/{okm:.3e}")
            _p(out, f"    {a:<{W}}" + "".join(f"{c:>24}" for c in cells_))

        # -- fit / training cost, never blank
        _p(out, "\n  fit / training cost (GMM EM wall-clock, seconds; 01_RULES §5 -- not hidden, 'n/a' where there is no fit):")
        for a in pres:
            _p(out, f"    {a:<{W}} {fit_cost(m, a)} s")
    return "\n".join(out)


# ----------------------------------------------------------------------------- table B (08_SPEC §2)
def pair_list(testbed, present):
    """ONLY the pairs listed in 08_SPEC §2.  All-pairs is deliberately not done (multiple comparisons).
    -> (x, y, anchor): the pair, plus the arm whose BLER fixes its decision SNRs.

    The anchor is the BASELINE member of the pair, never one of ours.  exp_0925's pre-registered rule
    anchored the decision points on the GMM / baseline arm; picking them off one of our arms would let
    our own arm choose where the comparison is evaluated.  So:
      R2-ours-G -> M-ours-*            anchor R2-ours-G          (the baseline of the comparison)
      M-ours-bstar <-> M-ours-dscore   anchor M-ours-bstar       (the GMM arm, and the pre-registered b*)
      M-ours-*     -> R6-exactEP/R5-genie  anchor the BOUND      (the non-ours member)
    """
    P = [("R1-turbo", "R2-ours-G", "R1-turbo"),
         (REF, "M-ours-gmm32", REF), (REF, "M-ours-bstar", REF), (REF, "M-ours-dscore", REF),
         ("M-ours-bstar", "M-ours-dscore", "M-ours-bstar")]
    if testbed == "D1":
        P.append((REF, "M-ours-score", REF))
    P += [(REF, "R4-scvamp", REF), ("R4-llr", "R4-scvamp", "R4-llr"), (REF, "R3-bigamp", REF)]
    top = "R6-exactEP" if testbed == "D1" else "R5-genie"          # headroom: D1 = exact EP, D2 = genie only
    P += [(a, top, top) for a in M_ARMS]
    # Stage C, pre-registered in 10_SPEC §6 (comparisons 1-3) and §3c ("1차 비교").  Same anchoring rule:
    # the BASELINE member of the pair fixes the decision SNRs.  Filtered out below when the arms are absent,
    # so a pre-registered run's table B is unchanged.
    P += [(REF, a, REF) for a in STAGEC_ARMS]
    P += [("M-ours-bstar", a, "M-ours-bstar") for a in STAGEC_ARMS]   # incl. the site-effect control pair
    P += [(a, top, top) for a in STAGEC_ARMS]
    return [(x, y, z) for x, y, z in P if x in present and y in present]


def decision_points(data, cell, prior, snrs, ref):
    """The (up to) 3 grid SNRs whose REF-arm BLER@16 is closest to 0.1 in |log10|, among the points with
    BLER in [0.005, 0.9].  Identical rule to exp_0925_analysis.k2_eval, with the pair's ANCHOR arm (its
    baseline member, see pair_list) as the reference instead of the hard-wired Hgmm-K32 (k2_eval cannot
    be called directly for that reason)."""
    n = len(data[(cell, prior, snrs[0])][ref]["blk_err"])
    bl = {s: max(data[(cell, prior, s)][ref]["blk_err"][:, -1].mean(), 0.5 / n) for s in snrs}
    cand = sorted((s for s in snrs if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3]
    return sorted(cand)


def table_B(data, meta, testbed, out):
    """Paired sign test + SNR@0.1 gap for the listed pairs, behind the pre-registered R6/R7 power guard:
    a call is printed ONLY with >= 3 decision points on the grid and >= MIN_DISC discordant pairs at
    >= 2 of them (MIN_DISC = 6: a two-sided sign test cannot reach p < .05 below that).  Otherwise the
    line reads UNDECIDED and NO call is made (08_SPEC §2, §5)."""
    _p(out, "\n" + "=" * 30, "TABLE B -- paired comparisons (08_SPEC §2)", "=" * 30)
    _p(out, "Only the pairs listed in 08_SPEC §2 are computed; all-pairs is not done (multiple-comparison problem).")
    _p(out, f"Sign test is paired per block (same channel/noise realisation, 06_SPEC §2). 'a:b' = only-first-fails : only-second-fails.")
    _p(out, f"POWER GUARD (R6/R7, pre-registered): >= 3 decision points AND >= {MIN_DISC} discordant pairs at >= 2 of them,")
    _p(out, "otherwise UNDECIDED is printed and no significance call is made.")
    _p(out, "The decision SNRs of a pair are anchored on its BASELINE member (exp_0925's pre-registered rule; never on one")
    _p(out, "of our arms, which would let our own arm choose where it is evaluated). The anchor arm is printed on every row.")
    for cell, prior in _groups(data):
        snrs = _points(data, cell, prior)
        pres = _present(data, cell, prior, testbed)
        _p(out, f"\n--- cell {cell}  prior {prior}  testbed {testbed}   SNR grid {[f'{s:+.0f}' for s in snrs]}")
        for x, y, anc in pair_list(testbed, pres):
            cand = decision_points(data, cell, prior, snrs, anc)
            res = [paired(data[(cell, prior, s)], x, y) for s in cand]
            A = sum(r[0] for r in res)
            B = sum(r[1] for r in res)
            powered = len(cand) == 3 and sum(1 for a, b, _ in res if a + b >= MIN_DISC) >= 2
            wy = sum(1 for a, b, p in res if a > b and p < 0.05)      # second arm fails less often
            wx = sum(1 for a, b, p in res if b > a and p < 0.05)
            _p(out, f"  {x} -> {y}        [decision-point anchor arm: {anc}"
                    + ("" if anc in (x, y) else " (NOT a member of this pair)") + "]")
            _p(out, f"    decision SNRs {[f'{s:+.0f}' for s in cand]} (anchor {anc}: "
                    f"|log10(BLER@16 of {anc} / 0.1)| smallest, BLER in [0.005, 0.9])")
            _p(out, "    sign test @16: " + ("  ".join(f"{s:+.0f} dB {a}:{b} p={p:.2g}" for (a, b, p), s in zip(res, cand)) or "none")
                    + f"   pooled {A}:{B} p={sign_p(A, B):.2g}")
            nd = [a + b for a, b, _ in res]
            if powered:
                _p(out, f"    power guard: {len(cand)} decision points, {sum(1 for d in nd if d >= MIN_DISC)} with >= {MIN_DISC} discordant pairs -> POWERED")
                _p(out, f"    two-sided sign test at p < .05: second arm fewer failures at {wy}/{len(cand)} points, "
                        f"first arm fewer failures at {wx}/{len(cand)} points -> "
                        + ("significant" if max(wx, wy) >= 2 else "not significant"))
            else:
                _p(out, f"    power guard: {len(cand)} decision points (needs 3), discordant-pair counts {nd} (needs >= {MIN_DISC} at >= 2) -> UNDECIDED")
                _p(out, "    UNDECIDED -- no significance call is made (08_SPEC §2). Raise n or extend the SNR grid.")
            _p(out, f"    SNR@0.1 gap ({x} minus {y}): "
                    + (gain(data, cell, prior, snrs, x, y)["text"] if len(snrs) >= 2 else "n/a (needs >= 2 SNR points)"))
    return "\n".join(out)


# ----------------------------------------------------------------------------- table C (08_SPEC §3)
def table_C(data, meta, testbed, out):
    """goodput = K (1 - BLER@16) / T with K = Nt (T - Tp) - 6, over the SNR points C1 and C2 share.
    Envelope = the better Tp per SNR.  The second-moment envelope (the comparison base) is the best of
    R2-ours-G @16, R0-pilot @1 and the same receiver @16 -- the base is given its best reading, never
    its worst (01_RULES §5: no baseline is handicapped)."""
    _p(out, "\n" + "=" * 30, "TABLE C -- cross-Tp goodput envelope (08_SPEC §3)", "=" * 30)
    pairs = [(a, b) for a in ("C1",) for b in ("C2",)]
    for c1, c2 in pairs:
        priors = sorted({k[1] for k in data if isinstance(k, tuple) and k[0] in (c1, c2)})
        for prior in priors:
            s1, s2 = _points(data, c1, prior), _points(data, c2, prior)
            if not s1 or not s2:
                _p(out, f"\n--- prior {prior}: cells {c1} and {c2} are not both present "
                        f"({c1}: {len(s1)} points, {c2}: {len(s2)} points) -> envelope not computed")
                continue
            snrs = [s for s in s1 if s in s2]
            T = CELLS[c1]["T"]
            Ks = {c: NT * (T - CELLS[c]["Tp"]) - 6 for c in (c1, c2)}
            _p(out, f"\n--- prior {prior}  testbed {testbed}   T={T}   "
                    f"upper bounds K/T: {c1} (Tp={CELLS[c1]['Tp']}) {Ks[c1] / T:.3f}, {c2} (Tp={CELLS[c2]['Tp']}) {Ks[c2] / T:.3f}")
            _p(out, "  " + "arm  (goodput; SNR [dB])".ljust(26) + " ".join(f"{s:>+8.0f}" for s in snrs))
            pres = [a for a in _present(data, c1, prior, testbed) if a in _present(data, c2, prior, testbed)]
            env = {}
            for arm, it, lab in _rows(pres):
                gk = _gkey(arm, it)
                g = {}
                for c in (c1, c2):
                    g[c] = np.array([Ks[c] * (1 - data[(c, prior, s)][arm]["blk_err"][:, it].mean()) / T for s in snrs])
                    _p(out, f"  {lab:<20} Tp={CELLS[c]['Tp']}  " + " ".join(f"{x:8.3f}" for x in g[c]))
                env[lab] = np.maximum(g[c1], g[c2])
            base_rows = [l for l in ("R2-ours-G", "R0-pilot (@1)", "pilot_C (@16)") if l in env]
            if not base_rows:
                _p(out, "  second-moment envelope base (R2-ours-G / R0-pilot) absent -> envelope gains not computed")
                continue
            base = np.max([env[l] for l in base_rows], axis=0)
            _p(out, f"  second-moment envelope base = best of {base_rows} over both Tp:")
            _p(out, f"  {'base':<26}" + " ".join(f"{x:8.3f}" for x in base))
            _p(out, "  envelope gain over the second-moment envelope [%]:")
            for lab in env:
                r = 100 * (env[lab] / np.maximum(base, 1e-9) - 1)
                _p(out, f"    {lab:<24}" + " ".join(f"{x:+7.1f}%" for x in r))
    return "\n".join(out)


# ----------------------------------------------------------------------------- table D (08_SPEC §3.5)
def _echo(out, path, what):
    _p(out, f"\n  [{what}]  source: {path}")
    if not os.path.exists(path):
        _p(out, "    NOT PRESENT -- this file is produced by `runner.py gate` / `runner.py fit`. No numbers to report yet.")
        return
    with open(path) as f:
        txt = f.read().rstrip("\n")
    _p(out, "\n".join("    " + l for l in txt.split("\n")))


def table_D(testbed, out, results_dir=None):
    """Training quality, independent of BLER.  The gate files are echoed VERBATIM: they already hold the
    per-rung GA-GD numbers (passing AND failing rungs), the GB' held-out denoising NMSE of the GMM prior
    vs the diffusion prior on the same sigma_t grid, and the K-by-K GMM fit table with the degradation
    relative to D1.  Nothing is re-derived or filtered here -- filtering a rung out would be exactly the
    'drop the failures' that 01_RULES §5 forbids."""
    R = results_dir or RESULTS
    _p(out, "\n" + "=" * 30, "TABLE D -- training quality, independent of BLER (08_SPEC §3.5)", "=" * 30)
    if testbed == "D1":
        _p(out, "D1: per-rung GA-GD numbers of the score ladder. Rungs that FAILED a gate are shown together with"
                " the rungs that passed (01_RULES §5: every attempt stays on the record, LADDER.md).")
        _p(out, "  GA: GA guards an INCONSISTENCY between the score path and the x0 path; it cannot catch an error"
                " shared by both.")
        _p(out, "      GA is identically zero by construction for every parameterisation (ve / vp / rf), so a passing"
                " GA is NOT evidence that the conversion was validated on the trained model.")
        _p(out, "  GD: the gate is the FULL Wirtinger matrix -- max over the sigma grid of the relative Frobenius"
                " error of J (per_sigma 'J_rel_fro'), tolerance 0.20. GD_trace (relative error of tr(J)/N) is")
        _p(out, "      reported beside it but is NOT the gate (conf/DECISIONS.md).")
        _echo(out, os.path.join(R, "gate_D1.txt"), "GA-GD per ladder rung")
    else:
        _p(out, "D2: GB' = held-out denoising NMSE of the GMM prior vs the diffusion prior on the SAME sigma_t grid."
                " This is a comparison one stage BEFORE BLER and stands on its own.")
        _echo(out, os.path.join(R, "gate_D2.txt"), "GB' held-out denoising NMSE, GMM vs diffusion")
        _p(out, "\n  GMM fit table on D2, including the DEGRADATION RELATIVE TO D1 -- the second piece of evidence"
                " that the testbed actually broke conditional Gaussianity (08_SPEC §3.5):")
        _echo(out, os.path.join(R, "gmm_fit_D2.txt"), "GMM fits on D2, per K, vs D1")
    return "\n".join(out)


# ----------------------------------------------------------------------------- filename contract self-test
NO_RAW_MARKER = "!!! NO RAW FILES"          # emitted into main()'s text; runner.py can test `in txt`


def selftest_filename():
    """PAT here and runner.raw_file there are two independent spellings of ONE filename, written by two
    different agents.  Build a name with runner's own spelling and require PAT to match it and to recover
    EVERY field.  Raises AssertionError the moment either spelling drifts."""
    import runner
    cell, prior, pil, skip, n = "C1", "S", "eig", 40, 80
    c = CELLS[cell]
    for testbed in ("D1", "D2"):
        for snr in (-3.0, 0.0, 15.0):
            f = os.path.basename(runner.raw_file(testbed, cell, prior, pil, snr, skip, n))
            m = PAT.match(f)
            assert m, f"PAT does not match runner.raw_file output: {f!r}"
            got = (m[1], m[2], m[3], int(m[4]), int(m[5]), int(m[6]), m[7], float(m[8]), int(m[9]), int(m[10]))
            want = (testbed, cell, prior, c["Nr"], c["T"], c["Tp"], pil, snr, skip, n)
            assert got == want, f"PAT recovers {got} from {f!r}, runner.raw_file encoded {want}"
    return f"selftest_filename OK -- analysis.PAT and runner.raw_file agree (6 names, D1/D2 x snr -3/0/+15)"


# ----------------------------------------------------------------------------- driver
def _head(testbed, data, meta):
    extra = ["arm list with per-arm notes (06_SPEC §5):"]
    for a in ARMS[testbed]:
        note = ARM_NOTES.get(a)
        extra += [f"  {a:<14}: {note}"] if note else []
    extra += [
        "  R0-pilot      : 1-PASS arm -- reported at iteration index 0 ('R0-pilot (@1)'); 'pilot_C (@16)' is the",
        "                  SAME receiver's 16-iteration trajectory, printed for context only.",
        "  M-ours-*      : differ from R2-ours-G in Module H and nothing else (test M2); Module H, K and the clip",
        "                  rule are in the run header of conf/results/ and in the raw meta of each point.",
        "fit/training cost (GMM EM wall-clock) is a column of table A and is never left blank.",
        "aggregates KEEP failed and diverged blocks; where a subset mean is printed, the full-set mean is beside it.",
    ]
    seen_arms = {k[7:] for m in meta.values() for k in m if k.startswith("budget|")}
    stagec = [a for a in STAGEC_ARMS if a in seen_arms]
    if stagec:
        extra.append("Stage C arms present in this run (10_SPEC §3b / §3c) -- the pre-registered Stage A/B verdicts are")
        extra.append("UNCHANGED by this file and M-ours-dscore stays BLOCKED in the pre-registered table:")
        extra += [f"  {a:<20}: {STAGEC_NOTES[a]}" for a in stagec]
    # 10_SPEC A3: the training budget of EVERY arm, printed, because the GMM re-fit at N'=1.6e5 may not be
    # finished and then some comparisons below are NOT equal-budget and must be readable as such.
    bud, note = {}, ""
    for m in meta.values():
        note = str(m.get("budget_note", note))
        for k, v in m.items():
            if k.startswith("budget|"):
                bud.setdefault(k[7:], set()).add(str(v))
    if bud:
        extra += ["", note, "per-arm training budget (arms absent from the raw files are simply not listed):"]
        for a in _pool(testbed):
            for v in sorted(bud.get(a, ())):
                extra.append(f"  {a:<20}: {v}")
        for k in ("dscore_ckpt", "dscore_status", "stagec_ckpt", "stagec_gate", "stagec_status"):
            for v in sorted({str(m[k]) for m in meta.values() if k in m}):
                extra.append(f"  {k:<20}: {v}")
    for cell, prior in _groups(data):
        snrs = _points(data, cell, prior)
        c = CELLS.get(cell, {})
        pres = _present(data, cell, prior, testbed)
        n = len(data[(cell, prior, snrs[0])][pres[0]]["blk_err"]) if pres else 0
        extra.append(f"cell {cell}: {c.get('Nr', '?')}x{NT} T={c.get('T', '?')} Tp={c.get('Tp', '?')} prior {prior}"
                     f"  SNR grid {[f'{s:+.0f}' for s in snrs]} dB  n={n} per point  outer iterations={N_ITER}"
                     f"  b*={meta.get((cell, prior), {}).get('bstar', 'n/a')}")
        # the beta / T_in / seed / dtype the runner ACTUALLY used, read back from "run|*" (06_SPEC §5):
        r = data[(cell, prior, snrs[0])].get("run", {})
        if r:
            extra.append("  run params as recorded in the raw file: "
                         + "  ".join(f"{k}={np.asarray(v).item()}" for k, v in sorted(r.items())))
    return header(testbed, extra)


def main(testbed, tag="", root=None, out_dir=None, results_dir=None):
    """Write conf/results/tables_<testbed>.txt and return its text.  D1 and D2 go to SEPARATE files and
    are never merged (08_SPEC §0): their arm sets are different (06_SPEC §1).

    If no raw file is found the returned text CONTAINS NO_RAW_MARKER: a caller (runner.py cmd_analysis,
    the __main__ block below) tests `NO_RAW_MARKER in txt` and exits non-zero instead of letting an empty
    table pass for a result."""
    sfx = f"_{tag}" if tag else ""
    root = root or (RAW + sfx)
    data, meta, warns = load_raw(testbed, root)
    out = []
    _p(out, _head(testbed, data, meta))
    _p(out, D1_WARNING if testbed == "D1" else D2_WARNING)
    for w in warns:
        _p(out, w)
    if not _groups(data):
        _p(out, "\n" + "!" * 110)
        _p(out, f"{NO_RAW_MARKER} for testbed {testbed} under {root} -- tables A/B/C have NO INPUT.")
        _p(out, "!!! Nothing below is a result. Check the --raw / --tag path and that `runner.py run` actually wrote chunks.")
        _p(out, "!" * 110)
    else:
        table_A(data, meta, testbed, out)
        table_B(data, meta, testbed, out)
        table_C(data, meta, testbed, out)
    table_D(testbed, out, results_dir)
    txt = "\n".join(out) + "\n"
    d = out_dir or RESULTS
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, f"tables_{testbed}{sfx}.txt"), "w") as f:
        f.write(txt)
    return txt


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--testbed", default="D1", choices=("D1", "D2"))
    ap.add_argument("--tag", default="")
    ap.add_argument("--raw", default=None)
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--results-dir", default=None)
    a = ap.parse_args()
    print("# " + selftest_filename())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)          # genie: NMSE is all-NaN by construction
        txt = main(a.testbed, a.tag, a.raw, a.out_dir, a.results_dir)
    print(txt)
    sys.exit(2 if NO_RAW_MARKER in txt else 0)
