"""select_grid.py -- NEXT_EXPERIMENTS_E5QAM16 §1.2: the 7-point SNR grid of one cell from b*'s development BLER only
(committed before any development BLER).

Reads raw_<tag>/ (worktree conf/), arm M-ours-bstar at outer iteration 16, trials 5120..5439 (32 chunks of 10 per SNR):
  BLER(s) = F(s) / 320,  F(s) = sum of [blk_err@16 != 0 or non-finite (a raised trial, 01_RULES §4)].
Integrity (any failure -> exit 1): exactly the 32 chunks per SNR, every array (10, 16), run|iters 16, run|n 10, one run|git,
meta modulation 16qam / payload_bits 90 / protocol E5-qam16-v1.
Rule: G0 = 3..21 dB step 3.  Inside = BLER(3) > 0.1 and BLER(21) < 0.1 -> G0.  Else ONE shift: BLER(3) <= 0.1 -> down (0..18),
BLER(21) >= 0.1 -> up (6..24); the shifted grid's new point must be in the raw ('need' printed otherwise) and is used whatever
it shows (no second shift; a still-broken inside condition is reported).  Both broken at once cannot happen (BLER(3) <= 0.1 and
BLER(21) >= 0.1) unless b* is non-monotone -- then the grid stays G0 and the fact is reported.
    cd ~/t2_wtE5/conf && python results/review_next/qam16/select_grid.py <tag>
"""
import glob
import re
import sys

import numpy as np

G0 = [3, 6, 9, 12, 15, 18, 21]
SKIP0, N, CH, BS = 5120, 320, 10, "M-ours-bstar"
BSTAR = {"U28QAM16g": (4096, 5.797910431000217), "D2QAM16g": (1024, -11.459169831224418)}   # §1.1: kron K, ll_val|kron (repr)


def bler(tag, s):
    fs = sorted(glob.glob(f"raw_{tag}/D2_C2_*_snr{s}_skip*_n{CH}.npz"), key=lambda f: int(re.search(r"_skip(\d+)_", f)[1]))
    if not fs:
        return None
    skips = [int(re.search(r"_skip(\d+)_", f)[1]) for f in fs]
    if skips != list(range(SKIP0, SKIP0 + N, CH)):
        raise SystemExit(f"{tag} {s:+d} dB: {len(fs)} chunks (skips {skips[:3]}..) != 32 chunks covering {SKIP0}..{SKIP0 + N - 1}")
    F, raised, git = 0, 0, set()
    for f in fs:
        z = np.load(f)
        meta = (str(z["meta|modulation"]), int(z["meta|payload_bits"]), str(z["meta|protocol"]))
        bstar = (str(z["meta|bstar"]), int(z["meta|kron_K"]), float(z["meta|ll_val|kron"]))
        sk = int(re.search(r"_skip(\d+)_", f)[1])
        if (z[f"{BS}|blk_err"].shape != (CH, 16) or int(z["run|iters"]) != 16 or int(z["run|n"]) != CH
                or int(z["run|skip"]) != sk or float(z["run|snr"]) != s or meta != ("16qam", 90, "E5-qam16-v1")
                or bstar != ("kron",) + BSTAR[tag]):
            raise SystemExit(f"{f}: shape {z[f'{BS}|blk_err'].shape} iters {z['run|iters']} n {z['run|n']} skip {z['run|skip']} "
                             f"snr {z['run|snr']} meta {meta} bstar {bstar} (want kron {BSTAR[tag]})")
        v = z[f"{BS}|blk_err"][:, -1]
        F += int(np.sum(np.where(np.isfinite(v), v != 0, True))); raised += int(np.sum(~np.isfinite(v))); git.add(str(z["run|git"]))
    return F, raised, git


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in BSTAR:
        raise SystemExit(f"usage: select_grid.py {'|'.join(BSTAR)}")
    tag = sys.argv[1]
    b = {s: bler(tag, s) for s in G0 + [0, 24]}
    gits = set().union(*(v[2] for v in b.values() if v is not None))
    if len(gits) != 1:
        raise SystemExit(f"{tag}: run|git {sorted(gits)} -- one code version over all SNRs required")
    if b[0] is not None and b[24] is not None:
        print(f"WARNING {tag}: both shift points (0 and 24 dB) are present -- only the one the rule asks for is used")
    for s in G0:
        if b[s] is None:
            raise SystemExit(f"{tag}: G0 point {s:+d} dB missing")
    for s in sorted(k for k in b if b[k] is not None):
        F, r, _ = b[s]
        print(f"{tag} b* {s:+3d} dB: F {F!r} / {N}  BLER {F / N!r}  raised {r!r}  git {next(iter(gits))}")
    lo, hi = b[3][0] / N, b[21][0] / N
    if lo > 0.1 and hi < 0.1:
        print(f"GRID {G0} (G0; inside: BLER(+3) {lo!r} > 0.1, BLER(+21) {hi!r} < 0.1)"); return
    if lo <= 0.1 and hi >= 0.1:
        print(f"GRID {G0} (G0; b* non-monotone: BLER(+3) {lo!r} <= 0.1 and BLER(+21) {hi!r} >= 0.1 -- reported, no shift)"); return
    new, grid = (0, [s - 3 for s in G0]) if lo <= 0.1 else (24, [s + 3 for s in G0])
    if b[new] is None:
        print(f"NEED {new:+d} dB (shift {'down' if new == 0 else 'up'} once: run b* at {new:+d} dB on the same trials)"); return
    nlo, nhi = b[grid[0]][0] / N, b[grid[-1]][0] / N
    ok = nlo > 0.1 and nhi < 0.1
    print(f"GRID {grid} (shifted {'down' if new == 0 else 'up'} once; inside after the shift: {ok} -- BLER({grid[0]:+d}) {nlo!r}, "
          f"BLER({grid[-1]:+d}) {nhi!r}{'' if ok else '; still broken, reported, no second shift'})")


if __name__ == "__main__":
    main()
