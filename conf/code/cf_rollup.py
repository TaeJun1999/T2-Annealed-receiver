"""(10_SPEC_stageC §6h) Roll up the do()-counterfactual sweep that has been sitting unread on disk.

The seven results/diag/jacpsd-counterfactual_D2_C2_snr*_n256.npz were written 2026-09-21 16:23-17:13.
The SUMMARY.txt beside them is dated 14:56 -- it PREDATES the sweep and has never seen it.
This writes a NEW file; the 14:56 one is left untouched as the record of what was known when.

Report-only.  Detection/aggregation of already-saved arrays; nothing is re-run, nothing is selected.
"""
import glob
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import common as C  # noqa: E402

DIAG = os.path.join(C.CONF, "results", "diag")
OUT = os.path.join(C.CONF, "results", "jacpsd_counterfactual_SUMMARY_n256.txt")
DIVERGE_NMSE = 10.0                      # same constant the F3 guard uses (bigamp.DIVERGE_NMSE)
SNRS = ["-3", "+0", "+3", "+6", "+9", "+12", "+15"]


def arm_keys(d):
    return sorted({"|".join(k.split("|")[:2]) for k in d.files
                   if "|" in k and k.split("|")[0] != "run"})


def main():
    files = {s: os.path.join(DIAG, f"jacpsd-counterfactual_D2_C2_snr{s}_n256.npz") for s in SNRS}
    missing = [s for s, p in files.items() if not os.path.exists(p)]
    if missing:
        sys.exit(f"missing SNR points: {missing} -- refusing to write a partial table (§6h: no SNR is dropped)")

    loaded = {s: np.load(p, allow_pickle=True) for s, p in files.items()}
    arms = arm_keys(loaded[SNRS[0]])

    lines = []
    w = lines.append
    w("# (10_SPEC_stageC §6h) do() counterfactual sweep -- C2, n=256/point, 7 SNRs, ROLL-UP ONLY")
    w(f"# generated : {C.now_kst()}" if hasattr(C, "now_kst") else "# generated : (see git commit)")
    w("# source    : results/diag/jacpsd-counterfactual_D2_C2_snr{-3,+0,+3,+6,+9,+12,+15}_n256.npz")
    w("#             written 2026-09-21 16:23-17:13 KST.  The SUMMARY.txt beside them is dated 14:56,")
    w("#             i.e. it predates the sweep and never read it.  That file is left unmodified.")
    w("# SCOPE     : diagnostic probe on the N=1e4 checkpoint, which FAILED the pre-registered gate")
    w("#             (GC 0.243 vs 0.15).  These are NOT arms and appear in no BLER table.")
    w(f"# guard     : 'div' = fraction of trials with NMSE@16 > {DIVERGE_NMSE} (same constant as F3)")
    w("")
    for meta_key in ("run|json", "meta|json"):
        if meta_key in loaded[SNRS[0]].files:
            try:
                m = json.loads(str(loaded[SNRS[0]][meta_key]))
                w("# run meta  : " + json.dumps({k: m[k] for k in list(m)[:12]}))
            except Exception:
                pass
            break
    w("")

    for metric, fmt in (("blk_err", "BLER@16"), ("nmse", "NMSE@16 (median)")):
        w(f"===== {fmt} =====")
        w(f"{'arm|intervention':<26}" + "".join(f"{s+' dB':>11}" for s in SNRS))
        for a in arms:
            row = f"{a:<26}"
            for s in SNRS:
                d = loaded[s]
                k = f"{a}|{metric}"
                if k not in d.files:
                    row += f"{'--':>11}"
                    continue
                x = d[k][:, 15]
                row += f"{np.mean(x):>11.4f}" if metric == "blk_err" else f"{np.median(x):>11.4g}"
            w(row)
        w("")

    w("===== divergence fraction (NMSE@16 > %g) =====" % DIVERGE_NMSE)
    w(f"{'arm|intervention':<26}" + "".join(f"{s+' dB':>11}" for s in SNRS))
    for a in arms:
        row = f"{a:<26}"
        for s in SNRS:
            d = loaded[s]
            k = f"{a}|nmse"
            row += f"{np.mean(d[k][:, 15] > DIVERGE_NMSE):>11.3f}" if k in d.files else f"{'--':>11}"
        w(row)
    w("")

    # the §6h prediction, scored here so the scoring cannot drift later
    w("===== §6h prediction, scored =====")
    w("prediction (committed before this file was written): dscore|psd1e-2 (sign repair) restores C2")
    w("BLER@16 to within 0.02 absolute of dscore|belsc at ALL SEVEN SNRs, and dscore|abs1e-2")
    w("(magnitude floor, SIGN KEPT) does not.  i.e. the defect is the SIGN, not the conditioning.")
    ref = "dscore|belsc"
    for cand in ("dscore|psd1e-2", "dscore|abs1e-2", "dscore|mean", "dscore|eta"):
        if f"{cand}|blk_err" not in loaded[SNRS[0]].files:
            continue
        gaps = [float(np.mean(loaded[s][f"{cand}|blk_err"][:, 15])
                      - np.mean(loaded[s][f"{ref}|blk_err"][:, 15])) for s in SNRS]
        ok = sum(abs(g) <= 0.02 for g in gaps)
        w(f"  {cand:<20} vs {ref}: within 0.02 at {ok}/7 SNRs   gaps " +
          " ".join(f"{g:+.3f}" for g in gaps))
    w("")
    w("Read the two lines above against the prediction; do not restate them selectively.")

    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
