"""conf/code/pair_mismatch.py -- table B for a TRAIN/TEST channel-model mismatch tag against its test prior's matched base raw
(NEXT_EXPERIMENTS_MISMATCH16e4 §1).

The mismatch tag ran V1 (M-ours-dscore-C-V1), b* (M-ours-bstar), R2-ours-G and R5-genie on the TEST prior's trials with the
TRAIN prior's checkpoint, GMM fits and sample covariance (fits dir = renamed links, runner --train-prior).  Trial streams
are fixed by (testbed, test prior, Nr, T, Tp, SNR), so the tag pairs trial by trial with the test prior's base raw (matched
arms).  Its arms are renamed V1-mis / bstar-mis / R2-mis and merged; analysis.decision_points / paired / gain are reused.
Integrity (any failure -> exit 1 BEFORE any label): the same point set as the base = the cell's SNR grid, no load_raw
warning, R5-genie identical (4 keys, every trial and iteration; genie uses only H and sigma2, so this proves the SAME
trials, not the priors), the tag's fits ARE the train prior's -- meta em_sec and every meta ll_val|<arm> equal the TRAIN
prior's base raw (ll_val|gmm32 fingerprints the npz that also holds Chat) -- and the mismatch really applied: bstar-mis and
R2-mis nmse differ from the matched arms' over the trials where neither raised.
    python code/pair_mismatch.py --base raw_D3B16e4 --mis raw_MMs2s2c --train-base raw_B16e4k --train-prior S2 --cell C2 --prior S2c
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np
from analysis import load_raw, decision_points, paired, gain, sign_p, MIN_DISC
from pair_cross import same, failed

REN = {"M-ours-dscore-C-V1": "V1-mis", "M-ours-bstar": "bstar-mis", "R2-ours-G": "R2-mis"}
PAIRS = (("bstar-mis", "V1-mis", "MM: mismatched b* -> mismatched V1"),
         ("V1-mis", "M-ours-dscore-C-V1", "report: mismatched V1 -> matched V1"),
         ("bstar-mis", "M-ours-bstar", "report: mismatched b* -> matched b*"),
         ("M-ours-bstar", "V1-mis", "report: matched b* -> mismatched V1"),
         ("R2-mis", "V1-mis", "report: mismatched Gaussian R2 -> mismatched V1"),
         ("R2-mis", "R2-ours-G", "report: mismatched Gaussian R2 -> matched R2"))
SHOW = ("R2-mis", "bstar-mis", "V1-mis", "R2-ours-G", "M-ours-bstar", "M-ours-dscore-C-V1", "R5-genie")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--mis", required=True)
    ap.add_argument("--train-base", required=True); ap.add_argument("--train-prior", required=True)
    ap.add_argument("--cell", required=True); ap.add_argument("--prior", required=True)
    a = ap.parse_args()
    b, _, wb = load_raw("D2", root=os.path.join(C.CONF, a.base))
    m, mm, wm = load_raw("D2", root=os.path.join(C.CONF, a.mis))
    _, tm, _ = load_raw("D2", root=os.path.join(C.CONF, a.train_base))
    sel = lambda d: sorted((k for k in d if k[:2] == (a.cell, a.prior)), key=lambda k: k[2])
    keys = sel(m)
    head = subprocess.run(["git", "-C", C.CONF, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    bad = []
    if [k[2] for k in keys] != [k[2] for k in sel(b)] or [k[2] for k in keys] != [float(s) for s in C.CELLS[a.cell]["snrs"]]:
        bad.append(f"point set {[k[2] for k in keys]} != base {[k[2] for k in sel(b)]} / grid {list(C.CELLS[a.cell]['snrs'])}")
    bad += [f"load_raw warning: {w.strip()}" for w in wb + wm]
    mt, tt = mm.get((a.cell, a.prior), {}), tm.get((a.cell, a.train_prior), {})
    fk = ["em_sec"] + sorted(k for k in tt if k.startswith("ll_val|"))
    if len(fk) < 2 or any(str(mt.get(k)) != str(tt.get(k)) for k in fk):
        bad.append("fits fingerprint (em_sec, ll_val|*) differs from the train base: "
                   + "; ".join(f"{k} {mt.get(k)} vs {tt.get(k)}" for k in fk if str(mt.get(k)) != str(tt.get(k)))[:300])
    for k in keys if not bad else []:
        for q in ("blk_err", "ber", "tauL_gmean", "alphaD"):
            if not same(b[k]["R5-genie"][q], m[k]["R5-genie"][q]):
                bad.append(f"{k[2]:+.0f} dB R5-genie|{q} differs")
        for arm in ("M-ours-bstar", "R2-ours-G"):
            ok = ~(failed(b[k], arm) | failed(m[k], arm))
            if same(np.asarray(b[k][arm]["nmse"])[ok], np.asarray(m[k][arm]["nmse"])[ok]):
                bad.append(f"{k[2]:+.0f} dB {arm} nmse identical to the matched arm (mismatch not applied)")
    raised = {REN[arm]: int(sum(failed(m[k], arm).sum() for k in keys)) for arm in REN} if not bad else {}
    n = len(m[keys[0]]["R5-genie"]["blk_err"]) if keys else 0
    print(f"# pair_mismatch {a.mis} x {a.base}, cell {a.cell}, test prior {a.prior}, n={n} per SNR, git {head}; raised trials "
          f"{raised}; integrity (point set, genie identical, train-fits fingerprint, mismatch applied): " + ("OK" if not bad else "FAILED: " + "; ".join(bad[:10])))
    if bad:
        sys.exit(1)                                     # an invalid pair gets no label (registration §1)
    data = {k: {**b[k], **{REN[arm]: m[k][arm] for arm in REN}} for k in keys}
    snrs = [k[2] for k in keys]
    for x, y, name in PAIRS:                            # same rule as analysis.table_B / pair_cross
        cand = decision_points(data, a.cell, a.prior, snrs, x)            # anchor = the first member
        res = [paired(data[(a.cell, a.prior, s)], x, y) for s in cand]
        A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
        powered = len(cand) == 3 and sum(1 for r in res if r[0] + r[1] >= MIN_DISC) >= 2
        wy = sum(1 for r in res if r[0] > r[1] and r[2] < 0.05); wx = sum(1 for r in res if r[1] > r[0] and r[2] < 0.05)
        lab = ("(iv) UNDECIDED" if not powered else "(i) second arm fewer" if wy >= 2 else "(ii) first arm fewer" if wx >= 2
               else "(iii) no direction")
        print(f"{name}: {x} -> {y}  [anchor {x}]  decision SNRs {[f'{s:+.0f}' for s in cand]}")
        print("    sign test @16: " + "  ".join(f"{s:+.0f} dB {r[0]}:{r[1]} p={r[2]:.2g}" for s, r in zip(cand, res))
              + f"   pooled {A}:{Bn} p={sign_p(A, Bn):.2g}")
        print(f"    POWERED={powered}  second arm fewer at {wy}/{len(cand)}, first arm fewer at {wx}/{len(cand)}  -> {lab}")
        print(f"    SNR@0.1 gap ({x} minus {y}): {gain(data, a.cell, a.prior, snrs, x, y)['text']}")
    g1, g0 = (gain(data, a.cell, a.prior, snrs, x, y)["est"] for x, y in (("bstar-mis", "V1-mis"), ("M-ours-bstar", "M-ours-dscore-C-V1")))
    print(f"report-only, gap retention = gap(bstar-mis - V1-mis) / gap(b* - V1, matched) = {g1:+.2f} / {g0:+.2f}"
          + (f" = {g1 / g0:.2f}" if g1 is not None and g0 and np.isfinite(g1) and np.isfinite(g0) else " (n/a)"))
    print("BLER@16 failures / n per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in SHOW:
        print(f"    {arm:<20}" + " ".join(f"{int(np.nan_to_num(np.asarray(data[k][arm]['blk_err'])[:, -1], nan=1).sum()):5d}"
                                         for k in keys))
    print("report-only, median NMSE@16 of the channel estimate per SNR " + " ".join(f"{s:+.0f}" for s in snrs) + " dB:")
    for arm in SHOW[:-1]:
        print(f"    {arm:<20}" + " ".join(f"{np.nanmedian(np.asarray(data[k][arm]['nmse'])[:, -1]):.2e}" for k in keys))


if __name__ == "__main__":
    main()
