"""(F3) Module H divergence guard -- the report 10_SPEC_stageC §3 asked for.

§3 registered this guard UNCONDITIONALLY, on the R3 precedent (code/bigamp.py DIVERGE_NMSE = 10.0),
and it was not implemented until the 2026-09-21 18:20 adversarial audit found it missing.  Without it
a run whose channel estimate ran away was filed under the catch-all "other" failure class, and the
`<arm>|diverged` column read n/a for every RouteA arm -- so a reader could not tell the guard was
ABSENT rather than never triggered.

The guard fires on a trial when the channel-estimate NMSE exceeds DIVERGE_NMSE, or is non-finite, at
ANY iteration.  It is DETECTION AND CLASSIFICATION ONLY: no trajectory changes, so every number
already recorded stays valid and all arms stay comparable.  Because it is a pure function of the
saved `<arm>|nmse`, it applies retroactively to raw files written before it existed -- including the
pre-registered raw/, which is READ ONLY here and is not rewritten.
"""
import argparse, glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C, bigamp


def scan(raw_dir, testbed):
    hits, skipped = {}, set()
    for f in sorted(glob.glob(os.path.join(raw_dir, f"{testbed}_*.npz"))):
        d = np.load(f, allow_pickle=True)
        cell = re.search(r"_(C\d)_", os.path.basename(f)).group(1)
        snr = float(d["run|snr"])
        for k in d.keys():
            if not k.endswith("|nmse"):
                continue
            arm = k.rsplit("|", 1)[0]
            nm = d[k]
            if nm.ndim != 2 or not nm.size:
                continue
            # An arm that never forms a channel ESTIMATE has an all-non-finite nmse by construction
            # (R5-genie is handed the true H).  Such an arm has no Module H path, so §3's guard does
            # not apply to it -- flagging it would be a pure false positive.  An arm with SOME
            # non-finite entries is a genuine blow-up and IS flagged.
            if not np.isfinite(nm).any():
                skipped.add(arm)
                continue
            with np.errstate(invalid="ignore"):
                bad = ~np.isfinite(nm) | (nm > bigamp.DIVERGE_NMSE)
            fired = bad.any(axis=1)
            a, b, c = hits.get((cell, snr, arm), (0, 0, 0.0))
            worst = np.nanmax(nm[np.isfinite(nm)]) if np.isfinite(nm).any() else np.inf
            hits[(cell, snr, arm)] = (a + int(fired.sum()), b + len(fired), max(c, float(worst)))
    return hits, skipped


def main(a):
    hits, skipped = scan(a.raw, a.testbed)
    print(C.header(a.testbed, extra=[
        f"content     : (F3) Module H divergence guard firings, DIVERGE_NMSE = {bigamp.DIVERGE_NMSE} "
        f"(reused from code/bigamp.py, NOT re-chosen)",
        f"raw         : {a.raw}",
        "rule        : a trial fires the guard if NMSE > 10.0 or non-finite at ANY of the 16 iterations.",
        "status      : DETECTION AND CLASSIFICATION ONLY -- no arm's trajectory is altered, so every",
        "              number recorded before this guard existed remains valid.",
        "read-only   : the raw files are not rewritten.",
    ]))
    print()
    rows = sorted((k for k, v in hits.items() if v[0]), key=lambda k: (k[0], k[1], k[2]))
    if not rows:
        print("NO GUARD FIRINGS in this raw set.  Every arm kept NMSE <= 10.0 and finite at every "
              "iteration of every trial.")
    else:
        print(f"{'cell':<5} {'SNR':>5} {'arm':<24} {'fired':>7} {'of':>6} {'rate':>7}  worst NMSE seen")
        print("-" * 78)
        for cell, snr, arm in rows:
            n, tot, worst = hits[(cell, snr, arm)]
            print(f"{cell:<5} {snr:>+5.0f} {arm:<24} {n:>7} {tot:>6} {n/tot:>7.3f}  {worst:.4g}")
    clean = sorted({k[2] for k in hits} - {k[2] for k in rows})
    print(f"\narms that NEVER fired the guard anywhere in this raw set ({len(clean)}): {', '.join(clean)}")
    if skipped:
        print(f"not applicable -- no channel estimate, so no Module H path ({len(skipped)}): "
              f"{', '.join(sorted(skipped))}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--raw", default=os.path.join(C.CONF, "raw_C"))
    p.add_argument("--testbed", default="D1", choices=["D1", "D2"])
    main(p.parse_args())
