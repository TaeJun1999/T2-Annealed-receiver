"""conf/code/eval_accept.py -- generalisation of b32e4_accept.py (NEXT_EXPERIMENTS_C6B16e4 §1 수용 검사): acceptance check
of evaluation tags against the values frozen in the pre-registration's §5.  Read-only; prints OK or the failures (exit 1).

  --tag TAG:ROLE:SHA:CELLS   (repeatable)  e.g. --tag NR16B16e4:best:0123456789abcdef:C6 --tag NR16B16e4last:last:...:C6
  --ntrain N  --kron-K K  --ll-val LL     the frozen b* (kron) and its validation log-likelihood (|diff| <= 1e-9)
  --iters 16  --chunk 40  --n 2560         the registered chunk plan {(chunk*k, chunk)}
  --ref-raw raw_NR16run2                    R5-genie replay check: blk_err / ber / tauL_gmean / alphaD @1..iters must be
                                            bit-identical to this raw set at EVERY shared trial of every point (NaN == NaN)
  --fits-dir results/gmm_fits_D2_NR16B16e4 --grid "full:16,32,64,128,256,512 kron:16,...,4096"
                                            grid completeness: every merged file exists; K >= 1024 has 3 candidate files
  --cand-dir DIR                            where the kron K >= 1024 candidate files live when not in --fits-dir
                                            (headline B16e4k: results/gmm_fits_D2_K1024n160000)
  --points C2:-6                            (repeatable) the expected SNR set of that cell instead of C.CELLS[c]["snrs"]
                                            (Pareto tag: C2 holds the single -6 dB point)
  --ref-cells C2                            restrict the genie replay check to these cells (others have no reference raw)
  --ref-arms all                            replay check over EVERY arm x common.KEYS_RAW instead of R5-genie x 4 keys
                                            (receiver regression check: a re-run of already-observed trials under the
                                            current code must reproduce every arm bit for bit; NEXT_EXPERIMENTS_PARETO §1)
  --bstar gmm256                            a full-family b*; then --kron-K may be omitted (meta|kron_K is not checked)
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
    ap.add_argument("--kron-K", type=int, default=None, help="required when --bstar kron")
    ap.add_argument("--ll-val", type=float, required=True)
    ap.add_argument("--iters", type=int, default=16)
    ap.add_argument("--chunk", type=int, default=40)
    ap.add_argument("--n", type=int, default=2560)
    ap.add_argument("--ref-raw", default=None)
    ap.add_argument("--fits-dir", default=None)
    ap.add_argument("--grid", default=None)
    ap.add_argument("--cand-dir", default=None, help="kron K >= 1024 candidate files location (default: --fits-dir)")
    ap.add_argument("--nr", type=int, default=8, help="Nr in the fit file names checked by --grid (B16e4k also holds Nr4 files)")
    ap.add_argument("--points", action="append", default=[], help="CELL:s1,s2,... expected SNR set override (repeatable)")
    ap.add_argument("--ref-cells", nargs="+", default=None, help="cells checked against --ref-raw (default: all)")
    ap.add_argument("--ref-arms", default="R5-genie", help="'R5-genie' (default: 4 keys) or 'all' (every arm x KEYS_RAW)")
    ap.add_argument("--prior", default="S2", help="prior in the fit file names (D3: S2c, SV: SV8e, 38.901: UMi28 / MIX3)")
    ap.add_argument("--bstar", default="kron", help="expected meta|bstar: 'kron' (default, every earlier tag) or a full-K name such as gmm256")
    a = ap.parse_args()
    if a.bstar == "kron" and a.kron_K is None:
        ap.error("--kron-K is required when --bstar kron")
    points = {p.split(":")[0]: tuple(int(s) for s in p.split(":")[1].split(",")) for p in a.points}
    plan = [(a.chunk * k, a.chunk) for k in range(a.n // a.chunk)]
    bad, common_meta = [], {}
    ref = load_points(os.path.join(C.CONF, a.ref_raw)) if a.ref_raw else None
    for spec in a.tag:
        tag, role, sha, cells = spec.split(":")
        cells = cells.split(",")
        pts = load_points(os.path.join(C.CONF, f"raw_{tag}"))
        want = {(c, s) for c in cells for s in points.get(c, C.CELLS[c]["snrs"])}
        if set(pts) != want:
            bad.append(f"{tag}: points {sorted(set(pts) ^ want)} missing/extra")
        for key, ch in sorted(pts.items()):
            ch.sort()
            if [(s, n) for s, n, _ in ch] != plan:
                bad.append(f"{tag} {key}: chunk plan differs from {{({a.chunk}k, {a.chunk})}}")
            for _, _, f in ch[:1] + ch[-1:]:
                with np.load(f) as z:
                    g = lambda k: str(z[k].item() if z[k].shape == () else z[k])
                    if (int(float(g("meta|ntrain"))) != a.ntrain or g("meta|bstar") != a.bstar
                            or (a.bstar == "kron" and int(float(g("meta|kron_K"))) != a.kron_K)):
                        bad.append(f"{os.path.basename(f)}: ntrain/bstar/kron_K = {g('meta|ntrain')}/{g('meta|bstar')}/{g('meta|kron_K')}")
                    if abs(float(g(f"meta|ll_val|{a.bstar}")) - a.ll_val) > 1e-9:
                        bad.append(f"{os.path.basename(f)}: ll_val|{a.bstar} {g(f'meta|ll_val|{a.bstar}')} != {a.ll_val}")
                    ids = g("meta|stagec_ckpt_id") if "meta|stagec_ckpt_id" in z.files else "(key absent: pre-P0-1 raw)"
                    if f"sha256[:16]={sha}" not in ids or f"role={role}" not in ids:
                        bad.append(f"{os.path.basename(f)}: ckpt id {ids[:80]} != sha {sha} role {role}")
                    if int(z["run|iters"]) != a.iters:
                        bad.append(f"{os.path.basename(f)}: run|iters {int(z['run|iters'])}")
                    common_meta.setdefault((g("meta|bstar"), g("meta|kron_K"), g("meta|em_sec")), set()).add(tag)
            if ref is not None and (a.ref_cells is None or key[0] in a.ref_cells):   # replay check, every chunk, every trial
                if key not in ref:
                    bad.append(f"{tag} {key}: no reference point in {a.ref_raw}"); continue
                with np.load(ref[key][0][2]) as z0:
                    if a.ref_arms == "all":                     # every "<arm>|<key>" of the reference with a KEYS_RAW key
                        rk = sorted(k for k in z0.files if "|" in k and k.split("|", 1)[1] in C.KEYS_RAW
                                    and not k.startswith(("meta|", "run|")))
                    else:
                        rk = [f"R5-genie|{q}" for q in REF_KEYS]
                cut = lambda v, i: v[i, :a.iters] if v.ndim == 2 else v[i]
                rows = {}
                for s, n, f in ref[key]:
                    with np.load(f) as z:
                        for i in range(n):
                            rows[s + i] = {k: cut(z[k], i) for k in rk}
                worst, shared, missing = {}, 0, set()
                for s, n, f in ch:
                    with np.load(f) as z:
                        for i in range(n):
                            if s + i not in rows:
                                bad.append(f"{tag} {key}: trial {s + i} absent from {a.ref_raw}"); continue
                            shared += 1
                            for k in rk:
                                if k not in z.files:
                                    missing.add(k); continue
                                x, y = cut(z[k], i), rows[s + i][k]
                                d = float(np.max(np.abs(np.nan_to_num(x, nan=1e300) - np.nan_to_num(y, nan=1e300))))
                                if d != 0.0:
                                    worst[k.split("|")[0]] = max(worst.get(k.split("|")[0], 0.0), d)
                if worst or missing or shared != a.n:
                    bad.append(f"{tag} {key}: replay vs {a.ref_raw} ({a.ref_arms}): shared {shared}/{a.n}"
                               + (f", arms differing {sorted(worst)} (max |diff| {max(worst.values()):.3g})" if worst else "")
                               + (f", keys missing in tag {sorted(missing)[:5]}" if missing else ""))
    if len(common_meta) != 1:
        bad.append(f"tags disagree on (bstar, kron_K, em_sec): {common_meta}")
    if a.fits_dir and a.grid:
        d = os.path.join(C.CONF, a.fits_dir)
        for fam_spec in a.grid.split():
            fam, ks = fam_spec.split(":")
            for K in (int(k) for k in ks.split(",")):
                pat = os.path.join(d, f"fit_{a.prior}_Nr{a.nr}_{fam}K{K}_n{a.ntrain}.npz")
                if not glob.glob(pat):
                    bad.append(f"grid: {fam} K={K} merged file missing ({pat})")
                if fam == "kron" and K >= 1024:
                    cpat = os.path.join(os.path.join(C.CONF, a.cand_dir) if a.cand_dir else d, os.path.basename(pat))
                    c = glob.glob(cpat[:-4] + ".k0r*.npz")
                    if len(c) != 3:
                        bad.append(f"grid: kron K={K} has {len(c)} candidate files, expected 3")
    names = [s.split(":")[0] for s in a.tag]
    print("ACCEPT: OK -- " + ", ".join(names) if not bad else "ACCEPT: FAILED\n  " + "\n  ".join(bad[:30]))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
