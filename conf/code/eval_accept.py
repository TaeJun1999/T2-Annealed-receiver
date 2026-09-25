"""conf/code/eval_accept.py -- generalisation of b32e4_accept.py (NEXT_EXPERIMENTS_C6B16e4 §1 수용 검사): acceptance check
of evaluation tags against the values frozen in the pre-registration's §5.  Read-only; prints OK or the failures (exit 1).

  --tag TAG:ROLE:SHA:CELLS   (repeatable)  e.g. --tag NR16B16e4:best:0123456789abcdef:C6 --tag NR16B16e4last:last:...:C6
  --ntrain N  --kron-K K  --ll-val LL     the frozen b* (kron) and its validation log-likelihood (|diff| <= 1e-9)
  --iters 16  --chunk 40  --n 2560         the registered chunk plan {(chunk*k, chunk)}
  --ref-raw raw_NR16run2                    R5-genie replay check: blk_err / ber / tauL_gmean / alphaD @1..iters must be
                                            bit-identical to this raw set at EVERY shared trial of every point (NaN == NaN)
  --fits-dir results/gmm_fits_D2_NR16B16e4 --grid "full:16,32,64,128,256,512 kron:16,...,4096"
                                            grid completeness: every merged file exists; K >= 1024 has 3 candidate files
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np

REF_KEYS = ("blk_err", "ber", "tauL_gmean", "alphaD")
PAT = re.compile(r"D2_(C\d)_.*_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")


def load_points(raw_dir):
    pts = {}
    for f in glob.glob(os.path.join(raw_dir, "D2_*.npz")):
        m = PAT.search(f)
        pts.setdefault((m[1], int(m[2])), []).append((int(m[3]), int(m[4]), f))
    return pts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", action="append", required=True)
    ap.add_argument("--ntrain", type=int, required=True)
    ap.add_argument("--kron-K", type=int, required=True)
    ap.add_argument("--ll-val", type=float, required=True)
    ap.add_argument("--iters", type=int, default=16)
    ap.add_argument("--chunk", type=int, default=40)
    ap.add_argument("--n", type=int, default=2560)
    ap.add_argument("--ref-raw", default=None)
    ap.add_argument("--fits-dir", default=None)
    ap.add_argument("--grid", default=None)
    a = ap.parse_args()
    plan = [(a.chunk * k, a.chunk) for k in range(a.n // a.chunk)]
    bad, common_meta = [], {}
    ref = load_points(os.path.join(C.CONF, a.ref_raw)) if a.ref_raw else None
    for spec in a.tag:
        tag, role, sha, cells = spec.split(":")
        cells = cells.split(",")
        pts = load_points(os.path.join(C.CONF, f"raw_{tag}"))
        want = {(c, s) for c in cells for s in C.CELLS[c]["snrs"]}
        if set(pts) != want:
            bad.append(f"{tag}: points {sorted(set(pts) ^ want)} missing/extra")
        for key, ch in sorted(pts.items()):
            ch.sort()
            if [(s, n) for s, n, _ in ch] != plan:
                bad.append(f"{tag} {key}: chunk plan differs from {{({a.chunk}k, {a.chunk})}}")
            for _, _, f in ch[:1] + ch[-1:]:
                with np.load(f) as z:
                    g = lambda k: str(z[k].item() if z[k].shape == () else z[k])
                    if (int(float(g("meta|ntrain"))) != a.ntrain or g("meta|bstar") != "kron"
                            or int(float(g("meta|kron_K"))) != a.kron_K):
                        bad.append(f"{os.path.basename(f)}: ntrain/bstar/kron_K = {g('meta|ntrain')}/{g('meta|bstar')}/{g('meta|kron_K')}")
                    if abs(float(g("meta|ll_val|kron")) - a.ll_val) > 1e-9:
                        bad.append(f"{os.path.basename(f)}: ll_val|kron {g('meta|ll_val|kron')} != {a.ll_val}")
                    ids = g("meta|stagec_ckpt_id")
                    if f"sha256[:16]={sha}" not in ids or f"role={role}" not in ids:
                        bad.append(f"{os.path.basename(f)}: ckpt id {ids[:80]} != sha {sha} role {role}")
                    if int(z["run|iters"]) != a.iters:
                        bad.append(f"{os.path.basename(f)}: run|iters {int(z['run|iters'])}")
                    common_meta.setdefault((g("meta|bstar"), g("meta|kron_K"), g("meta|em_sec")), set()).add(tag)
            if ref is not None:                                     # genie replay check, every chunk, every trial
                if key not in ref:
                    bad.append(f"{tag} {key}: no reference point in {a.ref_raw}"); continue
                rows = {}
                for s, n, f in ref[key]:
                    with np.load(f) as z:
                        for i in range(n):
                            rows[s + i] = {q: z[f"R5-genie|{q}"][i, :a.iters] for q in REF_KEYS}
                worst, shared = 0.0, 0
                for s, n, f in ch:
                    with np.load(f) as z:
                        for i in range(n):
                            if s + i not in rows:
                                bad.append(f"{tag} {key}: trial {s + i} absent from {a.ref_raw}"); continue
                            shared += 1
                            for q in REF_KEYS:
                                x, y = z[f"R5-genie|{q}"][i, :a.iters], rows[s + i][q]
                                worst = max(worst, float(np.max(np.abs(np.nan_to_num(x, nan=1e300) - np.nan_to_num(y, nan=1e300)))))
                if worst != 0.0 or shared != a.n:
                    bad.append(f"{tag} {key}: R5-genie replay vs {a.ref_raw}: shared {shared}/{a.n}, max |diff| {worst:.3g}")
    if len(common_meta) != 1:
        bad.append(f"tags disagree on (bstar, kron_K, em_sec): {common_meta}")
    if a.fits_dir and a.grid:
        d = os.path.join(C.CONF, a.fits_dir)
        for fam_spec in a.grid.split():
            fam, ks = fam_spec.split(":")
            for K in (int(k) for k in ks.split(",")):
                pat = os.path.join(d, f"fit_S2_Nr*_{fam}K{K}_n{a.ntrain}.npz")
                if not glob.glob(pat):
                    bad.append(f"grid: {fam} K={K} merged file missing ({pat})")
                if fam == "kron" and K >= 1024:
                    c = glob.glob(pat[:-4] + ".k0r*.npz")
                    if len(c) != 3:
                        bad.append(f"grid: kron K={K} has {len(c)} candidate files, expected 3")
    names = [s.split(":")[0] for s in a.tag]
    print("ACCEPT: OK -- " + ", ".join(names) if not bad else "ACCEPT: FAILED\n  " + "\n  ".join(bad[:30]))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
