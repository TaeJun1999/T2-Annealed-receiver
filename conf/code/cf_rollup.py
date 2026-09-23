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
    # NOTE (2026-09-23, review_next G-1.2): the SCOPE line below is shorthand.  The sweep's checkpoint,
    # ckpt/d2sx_N10000_a1.pt, has no D2 gate row (GA-GD are measurable on D1 only; results/tables_D2_B1e4.txt:45);
    # GC 0.243 is its D1 sibling at N_train=1e4 (results/samplecx_D1.txt:28), which FAILS.  Output left unchanged
    # (results/jacpsd_counterfactual_SUMMARY_n256.txt is not regenerated); at the next regeneration read
    # "... on ckpt/d2sx_N10000_a1.pt, which has no D2 gate record; its D1 sibling at N_train=1e4 FAILS GC 0.243 vs 0.15".
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

    # ---- the §6h prediction, scored against its LITERAL wording first (2026-09-22 14:55 correction).
    # 10_SPEC_stageC §6h (commit 7ec3d37) says, verbatim: "dscore|psd1e-2(부호 교정)가 7 SNR 전부에서
    # C2 BLER 을 V1 대역(절대 0.02 이내)으로 회복시키고, dscore|abs1e-2(크기만 바닥치고 부호 유지)는
    # 회복시키지 못한다".  The reference band is the V1 ARM (equal budget N=1e4, n=2560, raw_B1e4), NOT
    # dscore|belsc.  The first version of this roll-up scored against belsc; an independent figure
    # verification (wf_49dc79b9-4cf, item 6) caught the substituted reference.  Both scorings are kept.
    v1 = {}
    for s in SNRS:
        snr_int = int(s)
        vals = []
        for f in glob.glob(os.path.join(C.CONF, "raw_B1e4", f"D2_C2_*snr{snr_int}_*.npz")):
            b = np.load(f, allow_pickle=True)["M-ours-dscore-C-V1|blk_err"][:, 15]
            vals.append(np.where(np.isfinite(b), b, 1.0))          # analysis.py rule: raised = block error
        v1[s] = float(np.concatenate(vals).mean()) if vals else float("nan")
    w("===== §6h prediction, scored against the LITERAL pre-registered reference: the V1 ARM =====")
    w("§6h verbatim: psd1e-2 restores C2 BLER@16 to within 0.02 absolute of the V1 BAND at ALL SEVEN")
    w("SNRs, and abs1e-2 (magnitude floor, SIGN KEPT) does not.  V1 = M-ours-dscore-C-V1 from")
    w("raw_B1e4 (equal budget N=1e4, n=2560; this probe is n=256, so 0.02 is ~1 sigma at BLER 0.15).")
    w("  V1 BLER@16 : " + " ".join(f"{v1[s]:.4f}" for s in SNRS))
    for cand in ("dscore|psd1e-2", "dscore|abs1e-2", "dscore|mean", "dscore|belsc", "dscore|eta"):
        if f"{cand}|blk_err" not in loaded[SNRS[0]].files:
            continue
        gaps = [float(np.mean(loaded[s][f"{cand}|blk_err"][:, 15])) - v1[s] for s in SNRS]
        ok = sum(abs(g) <= 0.02 for g in gaps)
        w(f"  {cand:<20} vs V1 arm : within 0.02 at {ok}/7 SNRs   gaps " +
          " ".join(f"{g:+.3f}" for g in gaps))
    w("")
    w("===== the same prediction as this roll-up FIRST scored it (belsc reference -- NOT the §6h wording) =====")
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
    w("Read BOTH blocks against the prediction; the V1-referenced block is the one §6h wrote.")

    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
