"""select_dev.py -- NEXT_EXPERIMENTS_U28NR32SBL §1.2: the development selection of SBL-loop (committed before any development BLER).

Reads raw_U28NR32SBLd_r<rho>e<n_em>[w]/ (worktree conf/), arm SBL-loop at outer iteration 16:
  F(c, s) = sum over trials 3840..4159 of [blk_err@16 != 0 or non-finite (a raised trial, 01_RULES §4)]  -- pair_baselines.fails.
Integrity (any failure -> exit 1 before a selection): every SNR in {-3, 0, +3} holds exactly 32 chunks of 10 covering 3840..4159,
run|git one value per candidate, R5-genie blk_err / nmse identical across candidates (same trials), meta|sparse = the candidate.
Rule: metric = (F(-3) + F(0) + F(+3)) / 960, smaller better; tie -> shorter probe block time (cold value of the same (rho, n_em) for
a warm variant), then cold before warm.  'cold': the 8 cold candidates -> top two.  'final': cold 8 + warm 2 -> the pick and its
range-edge flag (rho in {4, 16} or n_em in {3, 25} or (rho 16, n_em 10) = the rho 16 column's surveyed maximum).
    cd ~/t2_wtE3/conf && python results/review_next/sbl32/select_dev.py cold|final [--allow-missing c,...]
Output: repr values to stdout (the caller tees results/review_next/sbl32/select_dev_<phase>.out).
"""
import glob
import json
import os
import re
import sys

import numpy as np

SEC = {(4, 3): 4.765, (4, 10): 12.398, (4, 25): 39.051, (8, 3): 33.897, (8, 10): 43.338, (8, 25): 122.003,
       (16, 3): 124.065, (16, 10): 295.339}                    # probe.out (1 thread, s / block); (16, 25) excluded by time
SNRS, SKIP0, N, CH = (-3, 0, 3), 3840, 320, 10


def load(tag):
    out, git, sparse = {}, set(), set()
    for s in SNRS:
        fs = sorted(glob.glob(f"raw_{tag}/D2_C9_UMi28_Nr32_T16_Tp4_eig_snr{s}_skip*_n{CH}.npz"),
                    key=lambda f: int(re.search(r"_skip(\d+)_", f)[1]))
        skips = [int(re.search(r"_skip(\d+)_", f)[1]) for f in fs]
        if skips != list(range(SKIP0, SKIP0 + N, CH)):
            raise SystemExit(f"{tag} {s:+d} dB: chunks {len(fs)} (skips {skips[:3]}..) != 32 chunks covering {SKIP0}..{SKIP0 + N - 1}")
        zs = [np.load(f) for f in fs]
        for f, z in zip(fs, zs):                               # BLER@16 over exactly 10 trials per chunk (= 320 per SNR)
            bad = [(k, z[k].shape) for k in ("SBL-loop|blk_err", "R5-genie|blk_err", "R5-genie|nmse") if z[k].shape != (CH, 16)]
            if bad or int(z["run|iters"]) != 16 or int(z["run|n"]) != CH:
                raise SystemExit(f"{f}: shapes {bad} run|iters {z['run|iters']} run|n {z['run|n']} -- not 10 trials x 16 iterations")
        git |= {str(z["run|git"]) for z in zs}; sparse |= {str(z["meta|sparse"]) for z in zs}
        v = np.concatenate([z["SBL-loop|blk_err"][:, -1] for z in zs])
        out[s] = dict(F=int(np.sum(np.where(np.isfinite(v), v != 0, True))), raised=int(np.sum(~np.isfinite(v))),
                      genie=np.concatenate([np.r_[z["R5-genie|blk_err"].ravel(), z["R5-genie|nmse"].ravel()] for z in zs]))
    return out, git, sparse


def main():
    phase = sys.argv[1]; allow = set(sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[2] == "--allow-missing" else set()
    cands = [(r, e, False) for r, e in SEC]
    if phase == "final":
        cands += [(int(m[1]), int(m[2]), True) for m in (re.fullmatch(r"raw_U28NR32SBLd_r(\d+)e(\d+)w", d) for d in os.listdir(".")) if m]
        assert sum(w for *_, w in cands) == 2, "final needs exactly two warm variants"
    rows, genie = [], None
    for r, e, w in cands:
        tag = f"U28NR32SBLd_r{r}e{e}" + ("w" if w else "")
        if f"r{r}e{e}" + ("w" if w else "") in allow:          # §1.2 3: incomplete by the deadline -> excluded, files kept, never read
            n = len(glob.glob(f"raw_{tag}/*.npz")) if os.path.isdir(f"raw_{tag}") else 0
            if n < len(SNRS) * N // CH:
                print(f"EXCLUDED {tag}: incomplete ({n} of {len(SNRS) * N // CH} chunks; not BLER) -- --allow-missing"); continue
        d, git, sparse = load(tag)
        want = json.dumps(dict(rho_sbl=r, n_em=e, rho_omp=1, L=1, **({"warm": True} if w else {})), sort_keys=True)
        assert len(git) == 1 and sparse == {want}, (tag, git, sparse, want)
        g = np.concatenate([d[s]["genie"] for s in SNRS])
        assert genie is None or np.array_equal(g, genie, equal_nan=True), f"{tag}: R5-genie differs -> not the same trials"   # genie nmse is NaN by convention
        genie = g
        F = [d[s]["F"] for s in SNRS]
        rows.append(dict(tag=tag, rho=r, n_em=e, warm=w, F=F, Fsum=sum(F), metric=sum(F) / (len(SNRS) * N),
                         raised=[d[s]["raised"] for s in SNRS], sec=SEC[(r, e)], git=git.pop()))
    key = lambda x: (x["Fsum"], x["sec"], x["warm"])
    rows.sort(key=key)
    top2 = [(x["rho"], x["n_em"]) for x in sorted((x for x in rows if not x["warm"]), key=key)[:2]]
    warm = sorted((x["rho"], x["n_em"]) for x in rows if x["warm"])
    if phase == "final" and warm != sorted(top2):
        raise SystemExit(f"warm variants {warm} != the cold top two {top2} (§1.2 4)")
    for x in rows:
        print(f"{x['tag']:<22} F(-3,0,+3) {x['F']!r} sum {x['Fsum']!r} metric {x['metric']!r} raised {x['raised']!r} "
              f"probe_sec {x['sec']!r} git {x['git']}")
    if phase == "cold":
        print("TOP2 (cold, warm variants to run):", " ".join(f"{x['rho']},{x['n_em']}" for x in rows[:2]))
    else:
        p = rows[0]
        edge = [ax for ax, hit in (("rho", p["rho"] in (4, 16)), ("n_em", p["n_em"] in (3, 25)),
                                    ("rho16-column max n_em (time screen)", (p["rho"], p["n_em"]) == (16, 10))) if hit]
        print(f"PICK {p['tag']} rho {p['rho']} n_em {p['n_em']} warm {p['warm']} metric {p['metric']!r}"
              f" range_edge {edge if edge else 'none'}")


if __name__ == "__main__":
    main()
