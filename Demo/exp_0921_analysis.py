"""exp_0921 analysis (measurement convention M-1).  usage: python exp_0921_analysis.py [A|B|all]   -> stdout + exp_0921_results.txt (append per set)
Reads exp_0921_raw/*.npz, concatenates the chunks of each point in skip order (warns if the chunk sequence has holes).
Iteration indices: '@8' = trajectory index 7, '@16' = index 15 (same run).
Failure classes of blocks that fail at @16, from the BER trajectory of iterations 11..16 (operational definition, exp_0921):
  stuck = BER constant over the last 4 iterations (wrong fixed point);  cyc2 = the last 5 BER increments are non-zero with alternating sign
  (period-2 limit cycle, F3);  other = neither (still drifting / irregular)."""
import os, re, sys, glob
from math import comb, sqrt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RAW = os.path.join(HERE, "exp_0921_raw")
T, NT = 28, 4
PAT = re.compile(r"(A|B)_Nr(\d+)_rho([\d.]+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
_out = []


def P(*a):
    s = " ".join(str(x) for x in a); print(s); _out.append(s)


def load(sname):
    pts = {}
    for f in glob.glob(os.path.join(RAW, f"{sname}_*.npz")):
        m = PAT.search(os.path.basename(f))
        if m: pts.setdefault((int(m[2]), float(m[3]), int(m[4]), m[5], int(m[6])), []).append((int(m[7]), int(m[8]), f))
    data = {}
    for key, chunks in pts.items():
        chunks.sort(); pos = 0; ok = True
        for skip, n, _ in chunks: ok &= skip == pos; pos = skip + n
        if not ok: P(f"  WARNING {key}: chunk sequence has holes/overlaps: {[(s, n) for s, n, _ in chunks]}")
        zs = [np.load(f) for _, _, f in chunks]; d = {}
        for k in zs[0].files:
            v, q = k.split("|"); d.setdefault(v, {})[q] = np.concatenate([z[k] for z in zs])
        data[key] = d
    return data


def wilson(k, n, z=1.96):
    if n == 0: return (np.nan, np.nan)
    p = k / n; c = p + z * z / (2 * n); h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)); den = 1 + z * z / n
    return ((c - h) / den, (c + h) / den)


def sign_p(a, b):
    n = a + b
    return 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def paired(d, x, y, it=-1):
    ex, ey = d[x]["blk_err"][:, it], d[y]["blk_err"][:, it]; a = int(np.sum((ex == 1) & (ey == 0))); b = int(np.sum((ex == 0) & (ey == 1)))
    return a, b, sign_p(a, b)


def fail_classes(v):
    be, ber = v["blk_err"], v["ber"]; f = be[:, -1] == 1; n = len(be)
    if not f.any(): return 0.0, 0.0, 0.0
    tail = ber[f][:, -6:]; dif = np.diff(tail, axis=1)
    stuck = np.ptp(tail[:, -4:], axis=1) < 1e-12
    cyc = np.all(dif != 0, 1) & np.all(dif[:, 1:] * dif[:, :-1] < 0, 1) & ~stuck
    return stuck.sum() / n, cyc.sum() / n, (f.sum() - stuck.sum() - cyc.sum()) / n


def row(name, v):
    be, nm = v["blk_err"], v["nmse"]; n = len(be); ok = be[:, -1] == 0; lo, hi = wilson(int(be[:, -1].sum()), n)
    st, cy, ot = fail_classes(v)
    nm_ok = np.median(nm[ok, -1]) if ok.any() and np.isfinite(nm[ok, -1]).any() else np.nan
    return (f"  {name:<20} n={n:<4} BLER@1/@2/@8/@16 = {be[:, 0].mean():.3f} {be[:, 1].mean():.3f} {be[:, 7].mean():.3f} {be[:, -1].mean():.3f} [{lo:.3f},{hi:.3f}]"
            f"  BER@16={v['ber'][:, -1].mean():.2e}  NMSE med@1/@16={np.nanmedian(nm[:, 0]):.4f}/{np.nanmedian(nm[:, -1]):.4f} ok={nm_ok:.4f}"
            f"  resc/lost(2->16)={int(np.sum((be[:, 1] == 1) & ok))}/{int(np.sum((be[:, 1] == 0) & ~ok))}"
            f"  tauL@1={np.median(v['tauL_gmean'][:, 0]):.3f}  fail% stuck/cyc2/other={100 * st:.1f}/{100 * cy:.1f}/{100 * ot:.1f}")


PAIRS_A = [("col_ext_b1", "col_post_b1"), ("col_ext_b0.7", "col_post_b0.7"), ("col_post_b1", "col_post_b0.7"), ("col_post_b0.7", "col_post_b0.7_fbd"),
           ("col_post_b0.7", "col_postnoloo_b0.7"), ("v0_ext_b1", "v0_post_b1"), ("v0_ext_b0.7", "v0_post_b0.7"), ("bel_ext_b0.7", "bel_post_b0.7"),
           ("bel_post_b0.7", "col_post_b0.7"), ("pilot_b1", "pilot_b0.7"), ("pilot_b0.7", "col_ext_b0.7"), ("pilot_b0.7", "col_post_b0.7")]


def analyse_A():
    data = load("A"); P("=" * 30, "exp_0921 A — D-15 baseline table (Gaussian Kronecker rho=0.7, 4x4, QPSK, seed 20260921+100+SNR)", "=" * 30)
    for key in sorted(data, key=lambda k: (-k[2], k[4])):
        Nr, rho, Tp, pil, snr = key; d = data[key]
        P(f"\n--- Tp={Tp} SNR={snr} dB ({Nr}x{NT}, rho={rho}, {pil})")
        for name, v in d.items(): P(row(name, v))
        for x, y in PAIRS_A:
            if x in d and y in d:
                a8, b8, p8 = paired(d, x, y, 7); a, b, p = paired(d, x, y)
                P(f"    paired {x} vs {y}: @16 only-first-fails {a}, only-second-fails {b}, p={p:.2g}   (@8: {a8}:{b8}, p={p8:.2g})")


def snr_at(snrs, bler, n, target=0.1):
    lb = np.log10(np.maximum(bler, 0.5 / n)); lt = np.log10(target)
    if lb[0] <= lt: return f"<={snrs[0]:.0f}"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]: return f"{snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]):.1f}"
    return f">{snrs[-1]:.0f}"


def analyse_B():
    data = load("B"); P("=" * 30, "exp_0921 B — Q-20 regime scan (Gaussian Kronecker, QPSK, 16 it, seed 20260921+100+SNR)", "=" * 30)
    cfgs = sorted({k[:4] for k in data}, key=lambda c: (c[0], c[1], -c[2], c[3])); summary = {}
    for cfg in cfgs:
        Nr, rho, Tp, pil = cfg; snrs = sorted(k[4] for k in data if k[:4] == cfg); K = NT * (T - Tp) - 6
        ns = [len(next(iter(data[cfg + (s,)].values()))["blk_err"]) for s in snrs]
        P(f"\n--- {Nr}x{NT} rho={rho} Tp={Tp} pilots={pil}  (K={K}, n per SNR: {ns})")
        P(f"  {'SNR [dB]':<26}" + " ".join(f"{s:>6.0f}" for s in snrs))
        for name in data[cfg + (snrs[0],)]:
            for tag, it in (("@8", 7), ("@16", -1)):
                bl = np.array([data[cfg + (s,)][name]["blk_err"][:, it].mean() for s in snrs])
                if tag == "@16" or name.startswith("col"): P(f"  BLER{tag:<4}{name:<18}" + " ".join(f"{x:6.3f}" for x in bl))
            summary[cfg + (name,)] = (np.array(snrs), bl, min(ns), K)
        for name in ("col_ext_b0.7", "col_post_b0.7"):
            P(f"  NMSEok@16 {name:<16}" + " ".join(f"{(lambda v: np.median(v['nmse'][v['blk_err'][:, -1] == 0, -1]) if (v['blk_err'][:, -1] == 0).any() else np.nan)(data[cfg + (s,)][name]):6.4f}" for s in snrs))
        P(f"  tauL@1    {'col_post_b0.7':<16}" + " ".join(f"{np.median(data[cfg + (s,)]['col_post_b0.7']['tauL_gmean'][:, 0]):6.3f}" for s in snrs))
        for x, y in (("pilot_b0.7", "col_post_b0.7"), ("col_ext_b0.7", "col_post_b0.7")):
            P(f"  paired {x} vs {y} (first:second, p): " + "  ".join("{}:{} {:.1g}".format(*paired(data[cfg + (s,)], x, y)) for s in snrs))
    P("\n--- summary: SNR [dB] at BLER@16 = 0.1 (log-linear interpolation; '>x' = not reached) and goodput K(1-BLER)/T [bit per channel use of the 4-antenna block]")
    for (Nr, rho) in sorted({c[:2] for c in cfgs}):
        P(f"  {Nr}x{NT} rho={rho}")
        for cfg in [c for c in cfgs if c[:2] == (Nr, rho)]:
            for name in ("pilot_b1", "pilot_b0.7", "col_ext_b0.7", "col_post_b0.7", "genie_b1"):
                if cfg + (name,) not in summary: continue
                snrs, bl, n, K = summary[cfg + (name,)]
                P(f"    Tp={cfg[2]} {cfg[3]} {name:<15} SNR@0.1 = {snr_at(snrs, bl, n):>6}   goodput: " + " ".join(f"{s:.0f}dB:{K * (1 - b) / T:.2f}" for s, b in zip(snrs, bl)))
        P("    regime check (same Tp, pilots, SNR): pilot-only fails (best-of-beta BLER >= 0.5) while col_post_b0.7 BLER <= 0.1:")
        hit = False
        for cfg in [c for c in cfgs if c[:2] == (Nr, rho)]:
            if cfg + ("col_post_b0.7",) not in summary: continue
            snrs, bj, _, _ = summary[cfg + ("col_post_b0.7",)]; bp = np.minimum(summary[cfg + ("pilot_b1",)][1], summary[cfg + ("pilot_b0.7",)][1])
            for s, a, b in zip(snrs, bp, bj):
                if a >= 0.5 and b <= 0.1: P(f"      Tp={cfg[2]} {cfg[3]} {s:.0f} dB: pilot {a:.3f} vs joint {b:.3f}"); hit = True
        if not hit: P("      none")


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("A", "all"): analyse_A()
    if which in ("B", "all"): analyse_B()
    with open(os.path.join(HERE, "exp_0921_results.txt"), "a") as f: f.write("\n".join(_out) + "\n")
