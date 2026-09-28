"""Independent re-derivation of every number quoted in NEXT_EXPERIMENTS_{ALD16e4,DOP16e4,ROT16e4,ROTMIX16e4,S2V16e4}.md §6
(+ ROTMIX / S2V §5), the matching docs/EXPERIMENTS.md rows and DECISIONS entries (record audit 2026-09-29, Fable 5.1; precedent
prereg_audit_2026-09-26/recompute.py).  A first run of this file (sections G/0/1-4, at HEAD 22370276, cut off by an API limit)
is kept as recompute_partial_22370276.out.prev; this version adds section 5 (S2V), the S2V/HEAD git checks and fixes one
false FAILED of the first run (ROTMIX meta|train_prior is a descriptive string starting with 'S2d', not the bare token).

Reads ONLY raw npz chunks, checkpoints, fit files, results/ald/*, GB' csv/npz, logs and git.  The raw reader, the sign test
(scipy exact binomial), decision points, SNR@0.1 gap (paired bootstrap, seed 20260925), genie-gap recovery R_X, the ROTMIX
difference-in-differences DD (paired bootstrap, seed 20260926, six arms resampled on the same trial indices) and the S2V
unpaired ΔR (two raws resampled independently, frontier_ci draw order) are re-implemented from the registrations' written
definitions -- pair_*.py / analysis.py / recovery_ci.py / frontier_ci.py are NOT called.  analysis.load_raw is imported ONLY
to cross-check this file's own reader on one raw set (section 0); every statistic below comes from the own reader.

    OMP_NUM_THREADS=2 CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python \
        results/review_next/prereg_audit_2026-09-28/recompute.py > .../recompute.out 2> .../recompute.err
"""
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
from scipy.stats import binomtest

CONF = "/home/HTJ/t2/conf"
T2 = "/home/HTJ/t2"
V1, BSTAR, GENIE, R2, SCALAR, R3 = "M-ours-dscore-C-V1", "M-ours-bstar", "R5-genie", "R2-ours-G", "M-ours-bstar-scalar", "R3-bigamp"
KEYS_RAW = ("blk_err", "ber", "nmse", "tauL_gmean", "alphaD", "tauL_clip_frac", "alphaD_clip")
KEYS4 = ("blk_err", "ber", "tauL_gmean", "alphaD")
GRID = (-3.0, 0.0, 3.0, 6.0, 9.0, 12.0, 15.0)
B = 2000
PAT = re.compile(r"^D2_(C\d)_([A-Za-z0-9]+)_Nr(\d+)_T(\d+)_Tp(\d+)_(dft|eig)_snr(-?\d+)_skip(\d+)_n(\d+)\.npz$")
BASELINES = ("M-ours-bstar-scalar", "M-ours-gmm32", "R0-pilot", "R1-turbo", "R2-ours-G", "R3-bigamp", "R4-llr", "R4-scvamp",
             "bstar-pilot", "V1-pilot", "ALD-pilot", "ALDv-pilot")
# name, cell, prior, base raw, PIL raw, ALD raw, ALD estimate tag, DOP/ROT suffix
DS = (("D2C2", "C2", "S2", "B16e4k", "PILB16e4k", "ALDB16e4k", "PILB16e4k", "B16e4k"),
      ("D2C6", "C6", "S2", "NR16B16e4", "PILNR16", "ALDNR16", "PILNR16", "NR16"),
      ("D3", "C2", "S2c", "D3B16e4", "PILD3", "ALDD3", "PILD3", "D3"),
      ("SV8e", "C2", "SV8e", "SVB16e4", "PILSV", "ALDSV", "PILSV", "SV"),
      ("UMi28", "C2", "UMi28", "U28B16e4", "PILU28", "ALDU28", "PILU28", "U28"),
      ("MIX3", "C2", "MIX3", "MXB16e4", "PILMX", "ALDMX", "PILMX", "MX"))


def P(*a):
    print(*a, flush=True)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def git(*a):
    return subprocess.run(["git", "-C", T2] + list(a), capture_output=True, text=True).stdout.strip()


def same(x, y):
    x, y = np.asarray(x), np.asarray(y)
    return x.shape == y.shape and np.array_equal(np.nan_to_num(x, nan=1e300), np.nan_to_num(y, nan=1e300))


# ----------------------------------------------------------------------------------------------- own raw reader
class Raw:
    """data[(cell, prior, snr)][arm][field]; meta[(cell, prior)] from the first chunk; per-chunk scalars in .scal[key] = set of
    str values over every chunk of the raw set (run|git, meta|rotation, meta|doppler, meta|train_prior, meta|stagec_ckpt_id,
    meta|em_sec); .holes = chunk-sequence problems; .fill = fields absent from some chunk (filled with NaN, announced)."""

    def __init__(self, tag):
        self.tag = tag
        root = os.path.join(CONF, f"raw_{tag}")
        pts = {}
        for f in sorted(glob.glob(os.path.join(root, "D2_*.npz"))):
            m = PAT.match(os.path.basename(f))
            if m:
                pts.setdefault((m[1], m[2], float(m[7])), []).append((int(m[8]), int(m[9]), f))
        self.nfiles = sum(len(v) for v in pts.values())
        self.data, self.meta, self.scal, self.holes, self.fill = {}, {}, {}, [], []
        for key, chunks in sorted(pts.items()):
            chunks.sort()
            pos = chunks[0][0] if chunks[0][0] in (0, 2560) else 0
            for s, n, _ in chunks:
                if s != pos:
                    self.holes.append((key, s, pos))
                pos = s + n
            zs = [np.load(f) for _, _, f in chunks]
            ns = [n for _, n, _ in chunks]
            keys = sorted({k for z in zs for k in z.files})
            d = {}
            for k in keys:
                a0 = next(z[k] for z in zs if k in z.files)
                if k.startswith("meta|") or k.startswith("run|"):
                    v = a0.item() if a0.shape == () else a0
                    self.meta.setdefault(key[:2], {}).setdefault(k, v)
                    if k in ("run|git", "meta|rotation", "meta|doppler", "meta|train_prior", "meta|stagec_ckpt_id", "meta|em_sec", "run|iters"):
                        for z in zs:
                            self.scal.setdefault(k, set()).add(str(z[k].item() if k in z.files and z[k].shape == () else (z[k] if k in z.files else "(none)")))
                    continue
                if "|" not in k or a0.ndim == 0:
                    continue
                arm, q = k.split("|", 1)
                parts = []
                for z, nz in zip(zs, ns):
                    if k in z.files:
                        parts.append(z[k])
                    elif q == "failed":
                        parts.append(np.zeros((nz,) + a0.shape[1:]))
                    else:
                        parts.append(np.full((nz,) + a0.shape[1:], np.nan)); self.fill.append((key, k, nz))
                d.setdefault(arm, {})[q] = np.concatenate(parts)
            for z in zs:
                z.close()
            self.data[key] = d
        # every raw set here holds one (cell, prior)
        self.cp = sorted({k[:2] for k in self.data})
        for k in ("run|git", "meta|rotation", "meta|doppler", "meta|train_prior"):
            self.scal.setdefault(k, {"(none)"})

    def snrs(self, cp):
        return sorted(k[2] for k in self.data if k[:2] == cp)

    def arms(self, cp):
        return sorted(self.data[(cp[0], cp[1], self.snrs(cp)[0])])

    def d(self, cp, s):
        return self.data[(cp[0], cp[1], float(s))]

    def m(self, cp):
        return self.meta.get(cp, {})


def fails(d, arm, it=-1):
    v = np.asarray(d[arm]["blk_err"])[:, it]
    return np.where(np.isfinite(v), v, 1.0)                       # a raised block is a block error (01_RULES §4)


def raised(d, arm):
    return np.asarray(d[arm]["failed"]) > 0 if "failed" in d[arm] else np.zeros(len(d[arm]["blk_err"]), bool)


def n_raised(raw, cp, arm):
    return int(sum(raised(raw.d(cp, s), arm).sum() for s in raw.snrs(cp)))


def sign_p(a, b):
    n = a + b
    return 1.0 if n == 0 else float(binomtest(min(a, b), n, 0.5, alternative="two-sided").pvalue)


def merged(cp, *srcs):
    """srcs = (Raw, {raw arm: new name}) ...; -> {snr: {new arm: fields}} on the common grid."""
    snrs = srcs[0][0].snrs(cp)
    out = {s: {} for s in snrs}
    for raw, ren in srcs:
        for s in snrs:
            for arm, new in ren.items():
                out[s][new] = raw.d(cp, s)[arm]
    return out


def dpoints(D, anchor):
    snrs = sorted(D)
    n = len(D[snrs[0]][anchor]["blk_err"])
    bl = {s: max(fails(D[s], anchor).mean(), 0.5 / n) for s in snrs}
    return sorted(sorted((s for s in snrs if 0.005 <= bl[s] <= 0.9), key=lambda s: abs(np.log10(bl[s] / 0.1)))[:3])


def table_b(D, x, y, it=-1):
    """08_SPEC §2 table B: anchor = first member; a = only-first-fails, b = only-second-fails; POWERED = 3 points and >= 6 discordant
    at >= 2 of them; (i) second fewer at >= 2 points (p < .05), (ii) first fewer, (iii) neither, (iv) not powered."""
    cand = dpoints(D, x)
    res = []
    for s in cand:
        fx, fy = fails(D[s], x, it), fails(D[s], y, it)
        a = int(((fx > 0) & (fy == 0)).sum()); b = int(((fx == 0) & (fy > 0)).sum())
        res.append((a, b, sign_p(a, b)))
    A = sum(r[0] for r in res); Bn = sum(r[1] for r in res)
    powered = len(cand) == 3 and sum(1 for a, b, _ in res if a + b >= 6) >= 2
    wy = sum(1 for a, b, p in res if a > b and p < 0.05); wx = sum(1 for a, b, p in res if b > a and p < 0.05)
    lab = "(iv)" if not powered else "(i)" if wy >= 2 else "(ii)" if wx >= 2 else "(iii)"
    return dict(cand=cand, res=res, A=A, B=Bn, pp=sign_p(A, Bn), powered=powered, wx=wx, wy=wy, lab=lab)


def fmt_b(t):
    k = f" {t['wy']}/3" if t["lab"] == "(i)" else f" {t['wx']}/3" if t["lab"] == "(ii)" else f" {t['wy']}/{len(t['cand'])}" if t["lab"] == "(iii)" else f" (POWERED=False, {len(t['cand'])} pts)"
    return (f"decision {[f'{s:+.0f}' for s in t['cand']]} a:b " + " · ".join(f"{a}:{b} (p {p:.2g})" for a, b, p in t["res"])
            + f" pooled {t['A']}:{t['B']} (p {t['pp']:.2g}) -> {t['lab']}{k}")


def snr_at(snrs, bl, n, target=0.1):
    lb = np.log10(np.maximum(np.asarray(bl, float), 0.5 / n)); lt = np.log10(target)
    if lb[0] <= lt:
        return snrs[0], "lo"
    for i in range(len(snrs) - 1):
        if lb[i] > lt >= lb[i + 1]:
            return snrs[i] + (lb[i] - lt) / (lb[i] - lb[i + 1]) * (snrs[i + 1] - snrs[i]), "ok"
    return snrs[-1], "hi"


def gap(D, x, y, seed=20260925):
    """exp_0925 gain: SNR@0.1(x) - SNR@0.1(y); paired bootstrap, the same resampled indices for both arms at every SNR."""
    snrs = sorted(D); ex = [fails(D[s], x) for s in snrs]; ey = [fails(D[s], y) for s in snrs]; n = min(len(e) for e in ex)
    (vx, fx), (vy, fy) = snr_at(snrs, [e.mean() for e in ex], n), snr_at(snrs, [e.mean() for e in ey], n)
    if fx == "hi" and fy == "ok":
        return dict(text=f">= {vx - vy:+.2f} ({x} never reaches 0.1)", est=vx - vy)
    if fx == "ok" and fy == "lo":
        return dict(text=f">= {vx - vy:+.2f} ({y} already < 0.1 at lowest SNR)", est=vx - vy)
    if fx != "ok" or fy != "ok":
        return dict(text=f"n/a ({vx:.2f} {fx} vs {vy:.2f} {fy})", est=np.nan)
    rng = np.random.default_rng(seed); g = []
    for _ in range(B):
        bx, by = [], []
        for a, b in zip(ex, ey):
            i = rng.integers(len(a), size=len(a)); bx.append(a[i].mean()); by.append(b[i].mean())
        (ux, gx), (uy, gy) = snr_at(snrs, bx, n), snr_at(snrs, by, n); g.append(ux - uy if gx == gy == "ok" else np.nan)
    g = np.array(g); cens = np.mean(~np.isfinite(g)); lo, hi = np.nanpercentile(g, [5, 95])
    return dict(text=f"{vx - vy:+.2f} [{lo:+.2f}, {hi:+.2f}]" + (f" censored {100 * cens:.0f}%" if cens > 0.005 else ""), est=vx - vy, lo=lo, hi=hi)


def recovery(cols, seed=20260926):
    """R_X = (F_X - F_V1)/(F_X - F_genie) on pooled failure counts; paired bootstrap of trial indices, the arms resampled together."""
    X, V, G = (sum(c[i].sum() for c in cols) for i in range(3))
    rng = np.random.default_rng(seed); n = len(cols[0][0]); out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n)
        xs, vs, gs = (sum(c[j][idx].sum() for c in cols) for j in range(3))
        out[i] = (xs - vs) / (xs - gs) if xs - gs > 0 else np.nan
    ok = np.isfinite(out); lo, hi = np.percentile(out[ok], [5, 95]) if ok.sum() else (np.nan, np.nan)
    return ((X - V) / (X - G) if X - G > 0 else np.nan), lo, hi, int((~ok).sum()), (int(X), int(V), int(G))


def dd_boot(s2d, sta, seed=20260926):
    """ROTMIX §1 DD: R(S2d side) - R(static side); one trial-index resample per replicate applied to every SNR column and BOTH sides."""
    def R(cols, idx=None):
        b, v, g = (sum((c[i] if idx is None else c[i][idx]).sum() for c in cols) for i in range(3))
        return (b - v) / (b - g) if b - g > 0 else np.nan
    d0 = R(s2d) - R(sta); rng = np.random.default_rng(seed); n = len(s2d[0][0]); out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n); out[i] = R(s2d, idx) - R(sta, idx)
    ok = np.isfinite(out); lo, hi = np.percentile(out[ok], [5, 95])
    return R(s2d), R(sta), d0, lo, hi, int((~ok).sum())


def fails_row(D, arms, s=-3.0):
    return " · ".join(f"{int(fails(D[s], a).sum())}" if a in D[s] else "-" for a in arms)


def fingerprint(raw, base, cp):
    """pair_dop/pair_rot: em_sec, stagec_ckpt_id (when the base has it), every ll_val|* of the base."""
    bm, mm = base.m(cp), raw.m(cp)
    fk = ["meta|em_sec"] + (["meta|stagec_ckpt_id"] if bm.get("meta|stagec_ckpt_id") is not None else []) + sorted(k for k in bm if k.startswith("meta|ll_val|"))
    return [k for k in fk if str(mm.get(k)) != str(bm.get(k))]


def control_check(ctl, base, cp):
    """0-control: every arm x KEYS_RAW of the control chunk (trials 0..39) bit-identical to the base raw at the same trials."""
    s = -3.0; dc, db = ctl.d(cp, s), base.d(cp, s); diff, arms = [], sorted(dc)
    for arm in arms:
        for q in KEYS_RAW:
            if q in dc[arm] and q in db.get(arm, {}):
                x = np.asarray(dc[arm][q]); y = np.asarray(db[arm][q])[:len(x)]
                if not same(x, y):
                    diff.append((arm, q))
    return len(arms), len(dc[arms[0]]["blk_err"]), diff


# ----------------------------------------------------------------------------------------------- sections
def sec0_reader_check():
    P("\n## 0. own reader vs analysis.load_raw (one raw set) + a hand count from the chunk files with no reader at all")
    sys.path.insert(0, os.path.join(CONF, "code"))
    from analysis import load_raw                   # cross-check only
    raw = Raw("ROTaB16e4k"); d2, _, w = load_raw("D2", root=os.path.join(CONF, "raw_ROTaB16e4k"))
    bad = 0
    for k in raw.data:
        for arm in raw.data[k]:
            for q in raw.data[k][arm]:
                x = raw.data[k][arm][q]; y = d2[k][arm].get(q)
                if y is None or not same(np.nan_to_num(x, nan=1.0) if q == "blk_err" else x, y):
                    bad += 1
    P(f"  ROTaB16e4k: {raw.nfiles} files, points {sorted((k[0], k[2]) for k in raw.data)}, load_raw warnings {len(w)}, fields disagreeing {bad}")
    # hand count: b* -> V1 at C2 -3 dB straight from the 64 chunk files
    a = b = 0
    for f in sorted(glob.glob(os.path.join(CONF, "raw_ROTaB16e4k", "D2_C2_*_snr-3_skip*_n40.npz")), key=lambda f: int(PAT.match(os.path.basename(f))[8])):
        with np.load(f) as z:
            bx = np.nan_to_num(z[f"{BSTAR}|blk_err"][:, -1], nan=1.0); by = np.nan_to_num(z[f"{V1}|blk_err"][:, -1], nan=1.0)
            a += int(((bx == 1) & (by == 0)).sum()); b += int(((bx == 0) & (by == 1)).sum())
    P(f"  hand count ROTaB16e4k C2 -3 dB b*->V1 a:b = {a}:{b}  (exact two-sided binomial p = {sign_p(a, b):.3g}; house sign_p = "
      f"{min(1.0, 2 * sum(__import__('math').comb(a + b, i) for i in range(min(a, b) + 1)) / 2 ** (a + b)):.3g})")
    cp = raw.cp[0]; D = merged(cp, (raw, {BSTAR: "bstar-rot", V1: "V1-rot"}))
    P("  table_b (own) same point: " + fmt_b(table_b(D, "bstar-rot", "V1-rot")))
    return raw


def sec_git():
    P("\n## G. git / documents / logs")
    P("  HEAD", git("rev-parse", "--short", "HEAD"), "| dirty conf/code Demo:", repr(git("status", "--porcelain", "conf/code", "Demo")),
      "| dirty docs/records:", repr(git("status", "--porcelain", "conf/results/review_next/NEXT_EXPERIMENTS_ALD16e4.md", "conf/results/review_next/NEXT_EXPERIMENTS_DOP16e4.md",
                                        "conf/results/review_next/NEXT_EXPERIMENTS_ROT16e4.md", "conf/results/review_next/NEXT_EXPERIMENTS_ROTMIX16e4.md",
                                        "conf/results/review_next/NEXT_EXPERIMENTS_S2V16e4.md", "docs/EXPERIMENTS.md", "conf/DECISIONS.md")))
    for name, fz in (("ALD16e4", "7e64f5cc"), ("DOP16e4", "063f3bcb"), ("ROT16e4", "9c0ca1f4"), ("ROTMIX16e4", "389e23f4"), ("S2V16e4", "389e23f4")):
        f = f"conf/results/review_next/NEXT_EXPERIMENTS_{name}.md"
        dl = git("diff", fz, "HEAD", "--", f).splitlines()
        hunks = [l for l in dl if l.startswith("@@")]
        removed = [l for l in dl if l.startswith("-") and not l.startswith("---")]
        P(f"  {name} vs freeze {fz} (-> HEAD): hunks {hunks}; removed lines {len(removed)}: {[l[:70] for l in removed]}")
        hh = [l for l in git("diff", "HEAD", "--", f).splitlines() if l.startswith("@@")]
        rh = [l[:70] for l in git("diff", "HEAD", "--", f).splitlines() if l.startswith("-") and not l.startswith("---")]
        P(f"      working tree vs HEAD: hunks {hh}; removed {rh}")
        # section boundaries at the freeze (a hunk whose first line is >= the '## 4.' line touches only §4-§6)
        txt = git("show", f"{fz}:{f}").splitlines()
        P("      section lines at freeze: " + ", ".join(f"{l[:6]}@{i + 1}" for i, l in enumerate(txt) if l.startswith("## ")))
    # HANDOFF_2026-09-27c incident (an overnight cp glob overwrote the working copies of the DOP/ROT docs, restored from HEAD):
    for name, ref, what in (("DOP16e4", "cf9eb419", "expected identical"), ("ALD16e4", "1be29323", "expected identical"),
                            ("ROT16e4", "a4cbd184", "expected: one hunk, only '+' lines, all after '## 6.'"),
                            ("ROTMIX16e4", "22370276", "expected: §5 merge cells + §6.1 only"), ("S2V16e4", "22370276", "expected: §4/§5 cells + §6.1 only")):
        f = f"conf/results/review_next/NEXT_EXPERIMENTS_{name}.md"
        dl = git("diff", ref, "HEAD", "--", f).splitlines()
        hunks = [l for l in dl if l.startswith("@@")]; minus = [l[:80] for l in dl if l.startswith("-") and not l.startswith("---")]
        plus = [l for l in dl if l.startswith("+") and not l.startswith("+++")]
        sec6 = next((i + 1 for i, l in enumerate(git("show", f"{ref}:{f}").splitlines()) if l.startswith("## 6.")), None)
        P(f"  {name} vs {ref} ({what}): hunks {hunks}; '-' lines {minus}; '+' lines {len(plus)}, first '+' {plus[0][:60] if plus else None!r}; '## 6.' at line {sec6} of {ref}")
    P("  b356079d:", git("log", "-1", "--format=%h %p %ad %s", "--date=format-local:%Y-%m-%d %H:%M:%S KST", "b356079d")[:160])
    P("  files in b356079d:", len(git("show", "--stat", "--format=", "b356079d").splitlines()) - 1, "|",
      [l.split("|")[0].strip()[-45:] for l in git("show", "--stat=200", "--format=", "b356079d").splitlines() if "NEXT_EXPERIMENTS" in l or "EXPERIMENTS.md" in l or "DECISIONS" in l])
    P("  server boot (who -b):", subprocess.run(["who", "-b"], capture_output=True, text=True).stdout.strip(), "KST | resume_after_reboot.log ROT lines:",
      [l.rstrip()[:90] for l in open(os.path.join(CONF, "logs/resume_after_reboot.log")) if "ROT" in l])
    P("  diff 389e23f4..22370276 --stat -- conf/code Demo:\n    " + git("diff", "389e23f4", "22370276", "--stat", "--", "conf/code", "Demo").replace("\n", "\n    "))
    P("  diff 9c0ca1f4..602f8971 -- conf/code Demo:", repr(git("diff", "9c0ca1f4", "602f8971", "--stat", "--", "conf/code", "Demo")))
    P("  diff 9c0ca1f4..a4cbd184 -- conf/code Demo:", repr(git("diff", "9c0ca1f4", "a4cbd184", "--stat", "--", "conf/code", "Demo")))
    P("  diff 22370276..HEAD -- conf/code Demo:", repr(git("diff", "22370276", "HEAD", "--stat", "--", "conf/code", "Demo")))
    P("  22370276 parents:", git("log", "-1", "--format=%p", "22370276"), "| a4cbd184 parent:", git("log", "-1", "--format=%p", "a4cbd184"), "| merge-base main/c-rotmix:", git("merge-base", "dac312b0", "bcc80d3b")[:8])
    for h in ("7e64f5cc", "1be29323", "063f3bcb", "cf9eb419", "9c0ca1f4", "602f8971", "a4cbd184", "389e23f4", "e2ed3445", "b233c3a2", "dac312b0", "22370276"):
        P(f"  {h}: {git('log', '-1', '--format=%ad %s', '--date=format-local:%Y-%m-%d %H:%M:%S KST', h)[:110]}")
    P("  DECISIONS.md in merge 22370276: lines added vs main parent dac312b0:",
      [l[:60] for l in git("diff", "dac312b0", "22370276", "--", "conf/DECISIONS.md").splitlines() if l.startswith("+") and not l.startswith("+++") and l.strip("+ ")])
    P("    lines added vs branch parent bcc80d3b:",
      [l[:60] for l in git("diff", "bcc80d3b", "22370276", "--", "conf/DECISIONS.md").splitlines() if l.startswith("+") and not l.startswith("+++") and l.strip("+ ")])
    P("  after_rot_chain.log merge lines:")
    for l in open(os.path.join(CONF, "results/review_next/after_rot_chain.log")):
        if "CONFLICT" in l or "conflict" in l or "merge commit" in l or "main commit" in l or "ROT done" in l or "B' " in l or "C " in l or "CHAIN" in l or "moved" in l:
            P("    " + l.rstrip()[:160])
    for lg, pat in (("logs/run_ald16e4.log", "start|ALD_EVAL_DONE|estimate|stage"), ("logs/run_dop16e4.log", "start|DOP_EVAL_DONE"),
                    ("logs/run_rot16e4.log", "start|ROT_EVAL_DONE|resume|control|D2C2 deg=|D2C6 deg=15 pair"), ("logs/run_rotmix16e4.log", "start|ROTMIX_EVAL_DONE|phase|acceptance"),
                    ("logs/run_s2v16e4_eval.log", "start|S2V_EVAL_DONE|phase|acceptance|rc=|decision")):
        P(f"  {lg}:")
        for l in open(os.path.join(CONF, lg)):
            if re.search(pat, l):
                P("    " + l.rstrip()[:150])
    fz = int(git("log", "-1", "--format=%ct", "389e23f4"))
    P(f"  pair_ROT*.txt mtimes vs ROTMIX design freeze 389e23f4 ({git('log', '-1', '--format=%ad', '--date=format-local:%m-%d %H:%M:%S KST', '389e23f4')}):")
    for f in sorted(glob.glob(os.path.join(CONF, "results/review_next/pair_ROT*.txt")), key=os.path.getmtime):
        t = os.path.getmtime(f); P(f"    {os.path.basename(f):<22} {subprocess.run(['date', '-d', f'@{int(t)}', '+%m-%d %H:%M:%S KST'], capture_output=True, text=True).stdout.strip()} {'BEFORE' if t < fz else 'after'} freeze")
    for f in sorted(glob.glob(os.path.join(CONF, "results/review_next/run_manifest_R*.json"))):
        j = json.load(open(f)); P(f"  {os.path.basename(f):<32} git {j.get('git_commit')} n_raw_files {j.get('n_raw_files')} config_hash {j.get('config_hash')} arms {len(j.get('arms', []))}")
    for f in sorted(glob.glob(os.path.join(CONF, "results/review_next/run_manifest_ALD*.json")) + glob.glob(os.path.join(CONF, "results/review_next/run_manifest_DOP*.json"))
                    + glob.glob(os.path.join(CONF, "results/review_next/run_manifest_S2v*.json"))):
        j = json.load(open(f)); P(f"  {os.path.basename(f):<32} git {j.get('git_commit')} n_raw_files {j.get('n_raw_files')} config_hash {j.get('config_hash')} arms {len(j.get('arms', []))}")
    P("  link dirs (count, all resolve to fit_S2d_Nr8_*, dir mtime CDT):")
    for t in ("RMX0", "RMX0PIL", "RMX0ALD", "RMX0last", "RMX0k1", "RMX15", "RMX15PIL", "RMX15ALD", "RMX15last", "RMX15k1", "RMX30", "RMX30PIL", "RMX30ALD", "RMX30last", "RMX30k1"):
        d = os.path.join(CONF, "results", f"gmm_fits_D2_{t}"); fs = sorted(glob.glob(os.path.join(d, "*.npz")))
        ok = all(os.path.basename(os.path.realpath(f)).startswith("fit_S2d_Nr8_") and os.path.exists(f) for f in fs)
        mt = subprocess.run(["date", "-d", f"@{int(os.path.getmtime(d))}", "+%m-%d %H:%M:%S"], capture_output=True, text=True, env={"TZ": "America/Chicago"}).stdout.strip()
        P(f"    {t:<10} {len(fs)} links ok={ok} k0r={len(glob.glob(os.path.join(d, '*k0r*')))} mtime {mt} CDT")


def sec_ald():
    P("\n## 1. ALD16e4 -- 6 datasets (A1 ALDv->V1, A2 ALD->V1, A3 ALDv->V1-pilot; report pairs; -3 dB failures; test NMSE)")
    PAIRS = (("ALDv-pilot", V1, "A1"), ("ALD-pilot", V1, "A2"), ("ALDv-pilot", "V1-pilot", "A3"),
             ("ALDv-pilot", BSTAR, "rep ALDv->b*"), ("bstar-pilot", "ALDv-pilot", "rep bstar-pilot->ALDv"), ("ALD-pilot", "ALDv-pilot", "rep ALD->ALDv"))
    SHOW = ("R0-pilot", "bstar-pilot", "ALD-pilot", "ALDv-pilot", "V1-pilot", BSTAR, V1, GENIE)
    for name, cell, prior, bt, pt, at, est_tag, _ in DS:
        base, pil, ald = Raw(bt), Raw(pt), Raw(at); cp = (cell, prior)
        P(f"\n  [{name}] base raw_{bt} ({base.nfiles} files) PIL raw_{pt} ({pil.nfiles}) ALD raw_{at} ({ald.nfiles})")
        bad = [f"{r.tag}: grid {r.snrs(cp)}" for r in (base, pil, ald) if tuple(r.snrs(cp)) != GRID]
        bad += [f"{r.tag}: holes {r.holes}" for r in (base, pil, ald) if r.holes] + [f"{r.tag}: NaN-filled {r.fill[:3]}" for r in (base, pil, ald) if r.fill]
        for s in GRID:
            for q in KEYS4:
                for r in (ald, pil):
                    if not same(base.d(cp, s)[GENIE][q], r.d(cp, s)[GENIE][q]):
                        bad.append(f"{s:+.0f} genie|{q} differs {r.tag}")
            for r in (base, pil, ald):
                if any(len(r.d(cp, s)[a]["blk_err"]) != 2560 for a in r.d(cp, s)):
                    bad.append(f"{s:+.0f} {r.tag}: n != 2560")
        est = np.load(os.path.join(CONF, "results/ald", f"ald_{est_tag}.npz"), allow_pickle=True)
        pilf = np.load(os.path.join(CONF, "results/ald", f"pilots_{est_tag}_test.npz"), allow_pickle=True)
        nm_test = []
        for j, s in enumerate(est["snrs"]):
            H, hh = pilf["H"][j], est["hhat"][j]
            ref = np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1); nm_test.append(10 * np.log10(ref.mean()))
            if not (len(H) == len(hh) == 2560):
                bad.append(f"{s:+.0f}: est/pilot trials {len(H)}/{len(hh)}")
            for arm in ("ALD-pilot", "ALDv-pilot"):
                d = ald.d(cp, float(s)); nm = np.asarray(d[arm]["nmse"])
                if raised(d, arm).any():
                    bad.append(f"{s:+.0f} {arm}: raised {int(raised(d, arm).sum())}")
                elif not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)) or not np.allclose(nm[:, 0], ref, rtol=1e-9, atol=0):
                    bad.append(f"{s:+.0f} {arm}: estimate not fixed / not the precomputed one")
        est_nm_file = [10 * np.log10(x) for x in est["nmse"]]
        prov = str(est["prov"]) if "prov" in est.files else ""
        bid = str(base.m(cp).get("meta|stagec_ckpt_id", "")); aid = str(ald.m(cp).get("meta|stagec_ckpt_id", ""))
        tune = json.load(open(os.path.join(CONF, "results/ald", f"tune_{est_tag}.json")))
        dev = [float(tune["dev_nmse_db"][k]) if isinstance(tune["dev_nmse_db"], dict) else float(v) for k, v in (tune["dev_nmse_db"].items() if isinstance(tune["dev_nmse_db"], dict) else enumerate(tune["dev_nmse_db"]))]
        P(f"    integrity (grid, holes, genie == base in ALD & PIL, n = 2560, ALD raised 0, estimate fixed == precomputed): {'OK' if not bad else 'FAILED ' + '; '.join(bad[:6])}")
        P(f"    est file sha256[:16] {sha16(os.path.join(CONF, 'results/ald', f'ald_{est_tag}.npz'))}; prov {prov[:150]!r}")
        P(f"    base ckpt id {bid[:60]!r}; ALD raw ckpt id same as base: {aid == bid}; ALD raw run|git {sorted(ald.scal['run|git'])}; base run|git {sorted(base.scal['run|git'])}")
        P(f"    ALD raw meta|ald_file: {str(ald.m(cp).get('meta|ald_file', '(none)'))[-40:]}; em_sec ALD==base: {str(ald.m(cp).get('meta|em_sec')) == str(base.m(cp).get('meta|em_sec'))}")
        P(f"    test ALD NMSE dB (recomputed from hhat/H): {' '.join(f'{v:.2f}' for v in nm_test)}; est['nmse'] field: {' '.join(f'{v:.2f}' for v in est_nm_file)}")
        P(f"    dev NMSE dB (tune json): {' '.join(f'{v:.1f}' for v in dev)}; max |test - dev| = {max(abs(a - b) for a, b in zip(nm_test, dev)):.2f} dB; tune c={tune['c']} beta={tune['beta']} stop={list(tune['stop'].values())}")
        D = merged(cp, (base, {a: a for a in base.arms(cp)}), (pil, {"V1-pilot": "V1-pilot", "bstar-pilot": "bstar-pilot"}), (ald, {"ALD-pilot": "ALD-pilot", "ALDv-pilot": "ALDv-pilot"}))
        for x, y, nm in PAIRS:
            t = table_b(D, x, y); P(f"    {nm:<24} {x} -> {y}: {fmt_b(t)}; gap {gap(D, x, y)['text']}")
        P(f"    -3 dB failures ({' · '.join(a.replace('M-ours-', '') for a in SHOW)}): {fails_row(D, SHOW)}")
        P(f"    -3 dB failures R0-pilot@1 (house 08_SPEC reading of R0-pilot): {int(fails(D[-3.0], 'R0-pilot', 0).sum())}")
        del base, pil, ald, D


def sec_shift(kind):
    """kind = 'DOP' (nu 0.005 / 0.01, meta|doppler) or 'ROT' (15 / 30 deg, meta|rotation)."""
    P(f"\n## {'2. DOP16e4' if kind == 'DOP' else '3. ROT16e4'} -- 6 datasets x 2 levels + 6 zero-controls")
    lv = (("a", "0.005"), ("b", "0.01")) if kind == "DOP" else (("a", "15"), ("b", "30"))
    suf = "dop" if kind == "DOP" else "rot"; mkey = "meta|doppler" if kind == "DOP" else "meta|rotation"
    REN = {V1: f"V1-{suf}", BSTAR: f"bstar-{suf}", R2: f"R2-{suf}", GENIE: f"genie-{suf}"}
    PAIRS = ((f"bstar-{suf}", f"V1-{suf}", "MAIN"), (f"V1-{suf}", V1, "rep V1-x->V1"), (f"bstar-{suf}", BSTAR, "rep b*-x->b*"),
             (BSTAR, f"V1-{suf}", "rep b*->V1-x"), (f"R2-{suf}", f"V1-{suf}", "rep R2-x->V1-x"), (f"genie-{suf}", GENIE, "rep genie-x->genie"))
    for name, cell, prior, bt, _, _, _, sx in DS:
        base = Raw(bt); cp = (cell, prior)
        ctl = Raw(f"{kind}0{sx}")
        na, nt, diff = control_check(ctl, base, cp)
        P(f"\n  [{name}] control {kind}0{sx}: {ctl.nfiles} file, {na} arms x KEYS_RAW over {nt} trials vs raw_{bt}: differing {diff}; "
          f"run|git {sorted(ctl.scal['run|git'])}; {mkey} {sorted(v[:12] for v in ctl.scal[mkey])}")
        P(f"    static -3 dB failures (R2 · b* · V1 · genie): {fails_row({-3.0: base.d(cp, -3.0)}, (R2, BSTAR, V1, GENIE))}")
        for L, val in lv:
            tag = f"{kind}{L}{sx}"; raw = Raw(tag)
            bad = [f"grid {raw.snrs(cp)}"] if tuple(raw.snrs(cp)) != GRID else []
            bad += [f"holes {raw.holes}"] if raw.holes else []
            bad += [f"NaN-filled {raw.fill[:3]}"] if raw.fill else []
            mv = raw.scal[mkey]
            if len(mv) != 1 or not (next(iter(mv)).startswith(f"deg={float(val)!r}:") if kind == "ROT" else next(iter(mv)).startswith(f"nu={float(val)!r}") or next(iter(mv)) == str(float(val))):
                bad.append(f"{mkey} {sorted(v[:30] for v in mv)}")
            g = raw.scal["run|git"]
            if len(g) != 1 or any(x.endswith("+dirty") or x == "(none)" for x in g):
                bad.append(f"run|git {sorted(g)}")
            fp = fingerprint(raw, base, cp)
            if fp:
                bad.append(f"fingerprint differs {fp}")
            for s in GRID:
                if any(len(raw.d(cp, s)[a]["blk_err"]) != 2560 for a in REN):
                    bad.append(f"{s:+.0f} n != 2560")
                if same(base.d(cp, s)[GENIE]["tauL_gmean"], raw.d(cp, s)[GENIE]["tauL_gmean"]):
                    bad.append(f"{s:+.0f} genie tauL_gmean identical to static ({kind} not applied)")
            rz = {REN[a]: n_raised(raw, cp, a) for a in REN}
            P(f"    [{tag}] {raw.nfiles} files; run|git {sorted(g)}; {mkey} {sorted(v[:14] for v in mv)}; ckpt id == base {str(raw.m(cp).get('meta|stagec_ckpt_id')) == str(base.m(cp).get('meta|stagec_ckpt_id'))}; "
              f"raised {rz}; integrity (grid, meta, one clean commit, fingerprint, n, applied): {'OK' if not bad else 'FAILED ' + '; '.join(bad[:5])}")
            D = merged(cp, (base, {a: a for a in (V1, BSTAR, R2, GENIE)}), (raw, REN))
            for x, y, nm in PAIRS:
                t = table_b(D, x, y); P(f"      {nm:<20} {x} -> {y}: {fmt_b(t)}; gap {gap(D, x, y)['text']}")
            g1, g0 = gap(D, f"bstar-{suf}", f"V1-{suf}")["est"], gap(D, BSTAR, V1)["est"]
            P(f"      gap retention = {g1:+.2f} / {g0:+.2f} = {g1 / g0 if np.isfinite(g1) and np.isfinite(g0) and g0 else float('nan'):.2f}")
            P(f"      -3 dB failures (R2-{suf} · bstar-{suf} · V1-{suf} · genie-{suf}): {fails_row(D, (f'R2-{suf}', f'bstar-{suf}', f'V1-{suf}', f'genie-{suf}'))}")
            del raw, D
        del base, ctl


def sec_rotmix():
    P("\n## 4. ROTMIX16e4 (B') -- 3 angles x 5 tags: RB, 13 baselines + R_X + X*, DT, DD, integrity (a)-(g), §5 artifacts")
    FITS = os.path.join(CONF, "results/gmm_fits_D2_S2dB16e4")
    P("  §5 fits (merged ll_val, n_iter, it_best, n_reseed | candidates r0/r1/r2):")
    ll = {}
    for fam, Ks in (("full", (16, 32, 64, 128, 256, 512)), ("kron", (16, 32, 64, 128, 256, 512, 1024, 2048, 4096))):
        for K in Ks:
            f = os.path.join(FITS, f"fit_S2d_Nr8_{fam}K{K}_n160000.npz")
            with np.load(f, allow_pickle=True) as z:
                ll[(fam, K)] = (float(z["ll_val"]), float(z["sec"]))
                info = f"ll_val {float(z['ll_val'])!r} n_iter {int(z['n_iter']) if 'n_iter' in z.files else '?'} it_best {int(z['it_best']) if 'it_best' in z.files else '?'} n_reseed {int(z['n_reseed']) if 'n_reseed' in z.files else '?'} restart {int(z['restart']) if 'restart' in z.files else '?'} sec {float(z['sec']):.1f}"
            cands = []
            for c in sorted(glob.glob(f[:-4] + ".k0r*.npz")):
                with np.load(c, allow_pickle=True) as z:
                    cands.append(f"{os.path.basename(c)[-8:-4]} {float(z['ll_val']):.4f} {int(z['n_iter']) if 'n_iter' in z.files else '?'}/{int(z['n_reseed']) if 'n_reseed' in z.files else '?'}")
            if K >= 256:
                P(f"    {fam} K={K}: {info}" + (f" | {cands}" if cands else ""))
    sec15 = sum(v[1] for v in ll.values()); sec13 = sec15 - ll[("kron", 2048)][1] - ll[("kron", 4096)][1]
    P(f"    sec sum 15 files {sec15:.1f}; 13 files (<= kron 1024) {sec13:.1f}; kron 4096 sec {ll[('kron', 4096)][1]:.1f}; +2048-1024 {ll[('kron', 2048)][0] - ll[('kron', 1024)][0]:+.2f} +4096-2048 {ll[('kron', 4096)][0] - ll[('kron', 2048)][0]:+.2f} nat")
    for f in ("d2sx_S2d_N160000_a1_best.pt", "d2sx_S2d_N160000_a1.pt"):
        p = os.path.join(CONF, "ckpt", f)
        try:
            import torch
            ck = torch.load(p, map_location="cpu", weights_only=False)
            keys = {k: ck[k] for k in ck if k in ("epoch", "best_epoch", "prior", "sigma_tag", "stopped_by", "aborted", "fallback", "best_val", "val_loss")}
            extra = {k: ck[k] for k in ck if isinstance(ck[k], (int, float, str, bool)) and k not in keys}
            P(f"    ckpt {f}: sha256[:16] {sha16(p)} {keys} {str(extra)[:200]}")
        except Exception as e:                                          # noqa: BLE001
            P(f"    ckpt {f}: sha256[:16] {sha16(p)} (torch load failed: {e})")
    z = np.load(os.path.join(CONF, "results/d2_gbprime_S2d_N160000_a1.npz"), allow_pickle=True)
    r = z["nmse_model"] / z["nmse_gmm"] if "nmse_model" in z.files else None
    if r is not None:
        P(f"    GB' npz ratio min {r.min():.4f} max {r.max():.4f} median {np.median(r):.4f} n {len(r)}; csv: {open(os.path.join(CONF, 'results/d2_gbprime_S2d.csv')).read().strip().splitlines()[-1]}")
    else:
        P(f"    GB' npz keys {z.files}; csv: {open(os.path.join(CONF, 'results/d2_gbprime_S2d.csv')).read().strip().splitlines()[-1]}")
    P("    sigma grid header: " + " | ".join(l.strip() for l in open(os.path.join(CONF, "results/sigma_grid_D2_S2d.txt")).readlines()[:2]))
    for d in (0, 15, 30):
        t = json.load(open(os.path.join(CONF, "results/ald", f"tune_RMX{d}ALD.json")))
        dv = t["dev_nmse_db"]; vv = t["v"]
        P(f"    tune_RMX{d}ALD.json sha {sha16(os.path.join(CONF, 'results/ald', f'tune_RMX{d}ALD.json'))}: c {t['c']} beta {t['beta']} stop {list(t['stop'].values())} dev dB {[round(float(x), 1) for x in (dv.values() if isinstance(dv, dict) else dv)]} "
          f"v {[round(float(x), 4) for x in (vv.values() if isinstance(vv, dict) else vv)]} edge {t.get('optimum_at_edge_after_extension')} ext {t.get('extended')} ckpt {t.get('ckpt_sha')} ald.py {t.get('ald_py_sha')} git {t.get('git')} rule {t.get('selection_rule')[:60]!r}")
    REF = {0: "B16e4k", 15: "ROTaB16e4k", 30: "ROTbB16e4k"}; cp = ("C2", "S2")
    for d in (0, 15, 30):
        ref, rmx, pil, ald, last, k1 = (Raw(t) for t in (REF[d], f"RMX{d}", f"RMX{d}PIL", f"RMX{d}ALD", f"RMX{d}last", f"RMX{d}k1"))
        raws = dict(ref=ref, rmx=rmx, pil=pil, ald=ald, last=last, k1=k1)
        P(f"\n  [delta = {d} deg] ref raw_{REF[d]}; files " + ", ".join(f"{n} {r.nfiles}" for n, r in raws.items()))
        bad = [f"{n}: grid {r.snrs(cp)}" for n, r in raws.items() if tuple(r.snrs(cp)) != GRID]
        bad += [f"{n}: holes/NaN {r.holes[:2]} {r.fill[:2]}" for n, r in raws.items() if r.holes or r.fill]
        gits = set().union(*(r.scal["run|git"] for n, r in raws.items() if n != "ref"))
        if len(gits) != 1 or any(g.endswith("+dirty") or g == "(none)" for g in gits):
            bad.append(f"run|git {sorted(gits)}")
        for n, r in raws.items():
            if n != "ref" and (len(r.scal["meta|rotation"]) != 1 or not next(iter(r.scal["meta|rotation"])).startswith(f"deg={float(d)!r}:")):
                bad.append(f"{n}: meta|rotation {sorted(v[:20] for v in r.scal['meta|rotation'])}")
            if n != "ref" and (len(r.scal["meta|train_prior"]) != 1 or not next(iter(r.scal["meta|train_prior"])).startswith("S2d")):
                bad.append(f"{n}: meta|train_prior {sorted(r.scal['meta|train_prior'])}")
        P(f"    ref raw meta: kron_K {ref.m(cp).get('meta|kron_K')} bstar {ref.m(cp).get('meta|bstar')} ll_val|kron {ref.m(cp).get('meta|ll_val|kron')} ckpt id {str(ref.m(cp).get('meta|stagec_ckpt_id', '(none)'))[:45]!r}")
        # (c) fit fingerprint
        for n, kk, sec in (("rmx", 4096, sec15), ("pil", 4096, sec15), ("ald", 4096, sec15), ("last", 4096, sec15), ("k1", 1024, sec13)):
            m = raws[n].m(cp)
            want = {f"meta|ll_val|gmm{K}": ll[("full", K)][0] for K in (16, 32, 64, 128, 256, 512)} | {"meta|ll_val|kron": ll[("kron", kk)][0], "meta|kron_K": float(kk), "meta|em_sec": sec}
            diff = [f"{q} {m.get(q)} != {v}" for q, v in want.items() if m.get(q) is None or abs(float(m.get(q)) - v) > 1e-9 * max(1, abs(v))]
            if diff:
                bad.append(f"{n}: fit fingerprint " + "; ".join(diff[:3]))
        for n, sha, role in (("rmx", "ceec0222e0912a1c", "best"), ("pil", "ceec0222e0912a1c", "best"), ("ald", "ceec0222e0912a1c", "best"), ("last", "98bc88f7333f19ee", "last"), ("k1", "ceec0222e0912a1c", "best")):
            cid = str(raws[n].m(cp).get("meta|stagec_ckpt_id", ""))
            if f"sha256[:16]={sha}" not in cid or f"role={role}" not in cid:
                bad.append(f"{n}: ckpt id {cid[:50]!r}")
        # (e) genie identical to the ref raw, 15 tags; R3 identical at 0 deg; (d) b*/R2 nmse NOT identical at 0 deg
        for s in GRID:
            for n, r in raws.items():
                if n == "ref":
                    continue
                if any(not same(ref.d(cp, s)[GENIE][q], r.d(cp, s)[GENIE][q]) for q in KEYS4):
                    bad.append(f"{s:+.0f} {n}: genie != ref")
                if any(len(r.d(cp, s)[a]["blk_err"]) != 2560 for a in r.d(cp, s)):
                    bad.append(f"{s:+.0f} {n}: n != 2560")
            if d == 0:
                r3 = rmx.d(cp, s).get(R3, {})
                if not r3 or any(not same(r3[q], ref.d(cp, s)[R3][q]) for q in r3 if q in ref.d(cp, s)[R3]):
                    bad.append(f"{s:+.0f}: R3-bigamp != ref")
                for arm in (BSTAR, R2):
                    ok = ~(raised(rmx.d(cp, s), arm) | raised(ref.d(cp, s), arm))
                    if same(np.asarray(rmx.d(cp, s)[arm]["nmse"])[ok], np.asarray(ref.d(cp, s)[arm]["nmse"])[ok]):
                        bad.append(f"{s:+.0f}: {arm} nmse identical to ref (S2d fits not applied)")
            # (g) PIL / ALD
            for arm, r in (("V1-pilot", pil), ("bstar-pilot", pil), ("ALD-pilot", ald), ("ALDv-pilot", ald)):
                if raised(r.d(cp, s), arm).any():
                    bad.append(f"{s:+.0f} {arm}: raised {int(raised(r.d(cp, s), arm).sum())}")
            for x, y in (("V1-pilot", V1), ("bstar-pilot", BSTAR)):
                ok = ~(raised(pil.d(cp, s), x) | raised(rmx.d(cp, s), y))
                if not same(np.asarray(pil.d(cp, s)[x]["nmse"])[ok, 0], np.asarray(rmx.d(cp, s)[y]["nmse"])[ok, 0]):
                    bad.append(f"{s:+.0f} {x}@1 != {y}@1")
        est = np.load(os.path.join(CONF, "results/ald", f"ald_RMX{d}ALD.npz"), allow_pickle=True)
        pilf = np.load(os.path.join(CONF, "results/ald", f"pilots_RMX{d}ALD_test.npz"), allow_pickle=True)
        prov = str(est["prov"]) if "prov" in est.files else ""
        erot = float(pilf["rotation"]) if "rotation" in pilf.files else -1.0
        if "ceec0222e0912a1c" not in prov + (str(est["ckpt_sha"]) if "ckpt_sha" in est.files else ""):
            bad.append("ALD estimate ckpt != _best")
        if erot != float(d):
            bad.append(f"ALD pilots rotation {erot} != {d}")
        for j, s in enumerate(est["snrs"]):
            H, hh = pilf["H"][j], est["hhat"][j]; refe = np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1)
            for arm in ("ALD-pilot", "ALDv-pilot"):
                nm = np.asarray(ald.d(cp, float(s))[arm]["nmse"])
                if not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)) or not np.allclose(nm[:, 0], refe, rtol=1e-9, atol=0):
                    bad.append(f"{s:+.0f} {arm}: estimate not fixed / not precomputed")
        P(f"    run|git {sorted(gits)}; meta|rotation {sorted(v[:8] for v in rmx.scal['meta|rotation'])}; meta|train_prior " + str({n: sorted(r.scal['meta|train_prior']) for n, r in raws.items()}))
        P(f"    est ald_RMX{d}ALD.npz sha {sha16(os.path.join(CONF, 'results/ald', f'ald_RMX{d}ALD.npz'))}; prov {prov[:120]!r}; pilots rotation {erot}; "
          f"test NMSE dB {' '.join(f'{10 * np.log10(x):.2f}' for x in est['nmse'])}")
        P(f"    ckpt ids: " + "; ".join(f"{n} {str(r.m(cp).get('meta|stagec_ckpt_id', ''))[:45]}" for n, r in raws.items() if n != "ref"))
        P(f"    rmx arms ({len(rmx.arms(cp))}): {rmx.arms(cp)}")
        P(f"    integrity (a)-(g) + one clean commit + train_prior: {'OK' if not bad else 'FAILED ' + '; '.join(bad[:8])}")
        # ---- pairB: X -> V1 (S2d _best), R_X, X*
        D = merged(cp, (rmx, {a: a for a in rmx.arms(cp)}), (pil, {"V1-pilot": "V1-pilot", "bstar-pilot": "bstar-pilot"}), (ald, {"ALD-pilot": "ALD-pilot", "ALDv-pilot": "ALDv-pilot"}))
        labs, rows = {}, []
        P(f"    pairB: X -> V1 (13 registered baselines), R_X -3 dB primary [90%] | secondary (decision points):")
        for x in (BSTAR,) + BASELINES:
            t = table_b(D, x, V1); labs[x] = t["lab"]
            fx, fv, fg = (fails(D[-3.0], a) for a in (x, V1, GENIE)); bl = fx.mean()
            if not (0.005 <= bl <= 0.9) or fx.sum() <= fg.sum():
                r1 = f"undefined (BLER {bl:.4f}, F_X {int(fx.sum())}, F_genie {int(fg.sum())})"; Rv = (np.nan, np.nan)
            else:
                R, lo, hi, nn, _ = recovery([(fx, fv, fg)]); r1 = f"{R:.3f} [{lo:.3f}, {hi:.3f}]" + (f" ({nn} undef)" if nn else ""); Rv = (lo, R)
            if t["cand"]:
                R2v, lo2, hi2, nn2, _ = recovery([tuple(fails(D[s], a) for a in (x, V1, GENIE)) for s in t["cand"]]); r2 = f"{R2v:.3f} [{lo2:.3f}, {hi2:.3f}] ({len(t['cand'])} pts)"
            else:
                r2 = "undefined"
            P(f"      {x:<20} {fmt_b(t)}; gap {gap(D, x, V1)['text']}; R_X {r1} | {r2}")
            rows.append((x, int(fx.sum()), t["lab"], Rv))
        # R0-pilot at the house reading (@1)
        D1 = {s: dict(D[s]) for s in D}
        for s in D1:
            D1[s]["R0-pilot@1"] = {"blk_err": np.asarray(D[s]["R0-pilot"]["blk_err"])[:, :1]}
        t = table_b(D1, "R0-pilot@1", V1); fx = fails(D1[-3.0], "R0-pilot@1"); fv, fg = fails(D[-3.0], V1), fails(D[-3.0], GENIE)
        R, lo, hi, nn, _ = recovery([(fx, fv, fg)])
        P(f"      R0-pilot@1 (house 08_SPEC reading; NOT what pair_baselines used): {fmt_b(t)}; F -3 dB {int(fx.sum())}; R_X {R:.3f} [{lo:.3f}, {hi:.3f}]")
        k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)")
        xs = min(rows, key=lambda r: (r[1], r[0]))
        P(f"    SUMMARY 13 baselines: (i) {k}, (ii) {mm}, undecided {13 - k - mm}; X* = {xs[0]} (F {xs[1]}; runner-up {sorted(rows, key=lambda r: (r[1], r[0]))[1][:2]}); "
          f"R_X* {xs[3][1]:.3f} lower {xs[3][0]:.3f}; sentence condition (k=13, (ii)=0, lower > 0): {'MET' if k == 13 and mm == 0 and xs[3][0] > 0 else 'NOT met'}")
        # ---- pair_rotmix: DT, report pairs, DD
        E = merged(cp, (ref, {V1: "V1-static", BSTAR: "bstar-static", GENIE: "genie", R2: "R2-static"}), (rmx, {V1: "V1-drift-best", BSTAR: "bstar-drift-4096", R2: "R2-drift"}),
                   (last, {V1: "V1-drift-last"}), (k1, {BSTAR: "bstar-drift-1024"}))
        for x, y, nm in (("V1-static", "V1-drift-last", "DT-V1"), ("bstar-static", "bstar-drift-1024", "DT-b*"), ("V1-drift-best", "V1-drift-last", "rep best->last"),
                         ("bstar-drift-1024", "bstar-drift-4096", "rep 1024->4096"), ("V1-static", "V1-drift-best", "rep V1 static->best"), ("bstar-static", "bstar-drift-4096", "rep b* 1024->S2d 4096"),
                         ("R2-static", "R2-drift", "rep R2")):
            t = table_b(E, x, y); P(f"    {nm:<22} {x} -> {y}: {fmt_b(t)}; gap {gap(E, x, y)['text']}")
        f3 = {a: fails(E[-3.0], a) for a in E[-3.0]}
        for nm, bd in (("DD registered (S2d b* 4096 + V1 last)", "bstar-drift-4096"), ("DD same-K report (S2d b* 1024 + V1 last)", "bstar-drift-1024")):
            s2d = (f3[bd], f3["V1-drift-last"], f3["genie"]); sta = (f3["bstar-static"], f3["V1-static"], f3["genie"])
            guard = all(0.005 <= x.mean() <= 0.9 and x.sum() > f3["genie"].sum() for x in (f3[bd], f3["bstar-static"]))
            Rs, Rt, d0, lo, hi, nn = dd_boot([s2d], [sta])
            P(f"    {nm}: guard {'OK' if guard else 'FIRED'} (b* BLER {f3[bd].mean():.3f}/{f3['bstar-static'].mean():.3f}); R_S2d {Rs:.3f} - R_static {Rt:.3f} = {d0:+.3f} [{lo:+.3f}, {hi:+.3f}]" + (f" ({nn} undef)" if nn else "")
              + (" -> CI > 0" if lo > 0 else " -> CI < 0" if hi < 0 else " -> contains 0"))
            cand = dpoints(E, bd)
            cs = [tuple(fails(E[s], a) for a in (bd, "V1-drift-last", "genie")) for s in cand]; ct = [tuple(fails(E[s], a) for a in ("bstar-static", "V1-static", "genie")) for s in cand]
            _, _, d2, lo2, hi2, _ = dd_boot(cs, ct)
            P(f"      secondary (decision points of {bd} {[f'{s:+.0f}' for s in cand]}, pooled): {d2:+.3f} [{lo2:+.3f}, {hi2:+.3f}]")
        P(f"    -3 dB failures (genie · V1 S2d best · V1 S2d last · b* S2d 4096 · b* S2d 1024 · V1 static · b* static 1024 · R2 S2d · R2 static): "
          f"{fails_row(E, ('genie', 'V1-drift-best', 'V1-drift-last', 'bstar-drift-4096', 'bstar-drift-1024', 'V1-static', 'bstar-static', 'R2-drift', 'R2-static'))}")
        del raws, ref, rmx, pil, ald, last, k1, D, E


def unpaired_dR(cols_a, cols_b, seed=20260926):
    """frontier_ci --recovery: per replicate ONE index draw per (raw, SNR point) in first-use order (raw A's points, then raw B's),
    the three arms of a point resampled together; R_A - R_B on the finite replicates, percentiles 5/95."""
    rng = np.random.default_rng(seed); out = np.full((B, 2), np.nan)
    for i in range(B):
        for j, cols in enumerate((cols_a, cols_b)):
            b = v = g = 0
            for fb, fv, fg in cols:
                idx = rng.integers(0, len(fb), len(fb)); b += fb[idx].sum(); v += fv[idx].sum(); g += fg[idx].sum()
            out[i, j] = (b - v) / (b - g) if b - g > 0 else np.nan
    d = out[:, 0] - out[:, 1]
    pc = lambda v: np.percentile(v[np.isfinite(v)], [5, 95])
    return pc(out[:, 0]), pc(out[:, 1]), pc(d), int((~np.isfinite(d)).sum())


def sec_s2v():
    P("\n## 5. S2V16e4 (C) -- C6 S2v N'=1.6e5: §5 artifacts, 4-tag integrity, 판정 1, 판정 2 (13 baselines) + X*, R_b*, ΔR (unpaired vs raw_NR16B16e4), report-only")
    FITS = os.path.join(CONF, "results/gmm_fits_D2_S2vB16e4"); cp = ("C6", "S2v")
    P("  §5 grid (merged: ll_val, restart, n_iter/it_best, n_reseed, sec | candidates .k0r{0,1,2}: ll_val n_iter/it_best n_reseed):")
    ll = {}
    for fam, Ks in (("full", (16, 32, 64, 128, 256, 512)), ("kron", (16, 32, 64, 128, 256, 512, 1024, 2048, 4096))):
        for K in Ks:
            f = os.path.join(FITS, f"fit_S2v_Nr16_{fam}K{K}_n160000.npz")
            with np.load(f, allow_pickle=True) as z:
                g = lambda k: int(z[k]) if k in z.files else "?"
                ll[(fam, K)] = (float(z["ll_val"]), float(z["sec"]))
                info = f"{float(z['ll_val'])!r} r{g('restart')} {g('n_iter')}/{g('it_best')} reseed {g('n_reseed')} kappa {g('kappa')} sec {float(z['sec']):.0f}"
            cands = []
            for c in sorted(glob.glob(f[:-4] + ".k0r*.npz")):
                with np.load(c, allow_pickle=True) as z:
                    cands.append(f"{os.path.basename(c)[-8:-4]} {float(z['ll_val']):.3f} {int(z['n_iter']) if 'n_iter' in z.files else '?'}/{int(z['it_best']) if 'it_best' in z.files else '?'} {int(z['n_reseed']) if 'n_reseed' in z.files else '?'}")
            P(f"    {fam} K={K}: {info}" + (f" | {cands}" if cands else ""))
    bs = max(ll, key=lambda k: ll[k][0]); fbest = max((k for k in ll if k[0] == "full"), key=lambda k: ll[k][0])
    P(f"    argmax ll_val = {bs} ({ll[bs][0]!r}); kron 4096 - 2048 = {ll[('kron', 4096)][0] - ll[('kron', 2048)][0]:+.3f} nat; full best {fbest} ({ll[fbest][0]:.3f}, b* - full best = {ll[bs][0] - ll[fbest][0]:.1f} nat); sec sum 15 files {sum(v[1] for v in ll.values()):.1f}; "
      f"candidate files: K>=1024 {[len(glob.glob(os.path.join(FITS, f'fit_S2v_Nr16_kronK{K}_n160000.k0r*.npz'))) for K in (1024, 2048, 4096)]}, K=512 {len(glob.glob(os.path.join(FITS, 'fit_S2v_Nr16_kronK512_n160000.k0r*.npz')))}; files in dir {len(os.listdir(FITS))}")
    import torch
    for f in ("d2sx_S2vNR16_N160000_a1_best.pt", "d2sx_S2vNR16_N160000_a1.pt"):
        p = os.path.join(CONF, "ckpt", f); ck = torch.load(p, map_location="cpu", weights_only=False)
        keys = {k: ck[k] for k in ck if k in ("epoch", "best_epoch", "prior", "sigma_tag", "stopped_by", "aborted", "fallback", "best_val", "grad_clip", "attempt", "split_hash", "rung")}
        P(f"    ckpt {f}: sha256[:16] {sha16(p)} {keys}")
    z = np.load(os.path.join(CONF, "results/d2_gbprime_S2vNR16_N160000_a1.npz"), allow_pickle=True); r = z["nmse_model"] / z["nmse_gmm"]
    P(f"    GB' npz ratio min {r.min():.4f} max {r.max():.4f} median {np.median(r):.4f} n {len(r)}; sigma grid in npz [{z['sigma'].min():.4e}, {z['sigma'].max():.4e}]; s2v_gb.log last: {open(os.path.join(CONF, 'logs/s2v_gb.log')).read().strip().splitlines()[-1][:150]}")
    sg = open(os.path.join(CONF, "results/sigma_grid_D2_S2vNR16.txt")).read().splitlines()
    P("    sigma grid header: " + " | ".join(l.strip() for l in sg[:2]) + f"; data rows {sum(1 for l in sg if l.strip() and not l.startswith('#'))}")
    t = json.load(open(os.path.join(CONF, "results/ald/tune_S2vALD.json"))); dv = t["dev_nmse_db"]; vv = t["v"]
    P(f"    tune_S2vALD.json sha {sha16(os.path.join(CONF, 'results/ald/tune_S2vALD.json'))}: c {t['c']} beta {t['beta']} stop {list(t['stop'].values())} dev dB {[round(float(x), 1) for x in dv.values()]} v {[round(float(x), 4) for x in vv.values()]} "
      f"edge {t.get('optimum_at_edge_after_extension')} ext {t.get('extended')} ckpt {t.get('ckpt_sha')} ald.py {t.get('ald_py_sha')} git {t.get('git')} seed {t.get('seed')} dev_skip {t.get('dev_skip')} n_dev {t.get('n_dev')} smin/smax {t.get('smin'):.5f}/{t.get('smax'):.5f} rule {t.get('selection_rule')!r}")
    # ---- raws
    best, last, pil, ald = (Raw(t) for t in ("S2vB16e4", "S2vB16e4last", "S2vPIL", "S2vALD")); raws = dict(best=best, last=last, pil=pil, ald=ald)
    P(f"  raws: " + ", ".join(f"{n} {r.nfiles} files" for n, r in raws.items()) + f"; best arms ({len(best.arms(cp))}): {best.arms(cp)}; pil {pil.arms(cp)}; ald {ald.arms(cp)}")
    bad = [f"{n}: grid {r.snrs(cp)}" for n, r in raws.items() if tuple(r.snrs(cp)) != GRID]
    bad += [f"{n}: holes/NaN {r.holes[:2]} {r.fill[:2]}" for n, r in raws.items() if r.holes or r.fill]
    gits = set().union(*(r.scal["run|git"] for r in raws.values()))
    if len(gits) != 1 or any(g.endswith("+dirty") or g == "(none)" for g in gits):
        bad.append(f"run|git {sorted(gits)}")
    for n, r in raws.items():
        m = r.m(cp)
        want = {"meta|ntrain": 160000, "meta|bstar": "kron", "meta|kron_K": 4096}
        for k, v in want.items():
            if str(m.get(k)) not in (str(v), str(float(v)) if isinstance(v, int) else str(v)):
                bad.append(f"{n}: {k} {m.get(k)!r}")
        if abs(float(m.get("meta|ll_val|kron", np.nan)) - ll[("kron", 4096)][0]) > 1e-9:
            bad.append(f"{n}: ll_val|kron {m.get('meta|ll_val|kron')}")
    for n, sha, role, ep in (("best", "fef34e13133004fc", "best", 2463), ("last", "9940812e5f7ab689", "last", 2483), ("pil", "fef34e13133004fc", "best", 2463), ("ald", "fef34e13133004fc", "best", 2463)):
        cid = str(raws[n].m(cp).get("meta|stagec_ckpt_id", ""))
        if f"sha256[:16]={sha}" not in cid or f"role={role}" not in cid or f"epoch={ep}" not in cid or "best_epoch=2463" not in cid:
            bad.append(f"{n}: ckpt id {cid[:70]!r}")
    em = {n: str(raws[n].m(cp).get("meta|em_sec")) for n in raws}
    if em["best"] != em["last"]:
        bad.append(f"em_sec best {em['best']} != last {em['last']}")
    diff_arms = set()
    for s in GRID:
        db = best.d(cp, s)
        for n in ("last", "pil", "ald"):
            if any(not same(db[GENIE][q], raws[n].d(cp, s)[GENIE][q]) for q in KEYS4):
                bad.append(f"{s:+.0f} {n}: genie != best")
        if any(len(r.d(cp, s)[a]["blk_err"]) != 2560 for r in raws.values() for a in r.d(cp, s)):
            bad.append(f"{s:+.0f}: n != 2560")
        dl = last.d(cp, s)
        for a in db:
            if any(not same(db[a][q], dl[a][q]) for q in KEYS_RAW if q in db[a] and q in dl[a]):
                diff_arms.add(a)
        for arm, r in (("V1-pilot", pil), ("bstar-pilot", pil), ("ALD-pilot", ald), ("ALDv-pilot", ald)):
            if raised(r.d(cp, s), arm).any():
                bad.append(f"{s:+.0f} {arm}: raised {int(raised(r.d(cp, s), arm).sum())}")
        for x, y in (("V1-pilot", V1), ("bstar-pilot", BSTAR)):
            ok = ~(raised(pil.d(cp, s), x) | raised(db, y))
            if not same(np.asarray(pil.d(cp, s)[x]["nmse"])[ok, 0], np.asarray(db[y]["nmse"])[ok, 0]):
                bad.append(f"{s:+.0f} {x}@1 != {y}@1")
    if diff_arms != {"M-ours-dscore-C-V0", "M-ours-dscore-C-V1", "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b"}:
        bad.append(f"last vs best differing arms {sorted(diff_arms)}")
    est = np.load(os.path.join(CONF, "results/ald/ald_S2vALD.npz"), allow_pickle=True); pilf = np.load(os.path.join(CONF, "results/ald/pilots_S2vALD_test.npz"), allow_pickle=True)
    prov = str(est["prov"]) if "prov" in est.files else ""
    if "fef34e13133004fc" not in prov:
        bad.append("ALD estimate ckpt != _best")
    nm_test = []
    for j, s in enumerate(est["snrs"]):
        H, hh = pilf["H"][j], est["hhat"][j]; refe = np.sum(np.abs(hh - H) ** 2, -1) / np.sum(np.abs(H) ** 2, -1); nm_test.append(10 * np.log10(refe.mean()))
        if not (len(H) == len(hh) == 2560):
            bad.append(f"{s:+.0f}: est/pilot trials {len(H)}/{len(hh)}")
        for arm in ("ALD-pilot", "ALDv-pilot"):
            nm = np.asarray(ald.d(cp, float(s))[arm]["nmse"])
            if not same(nm, np.repeat(nm[:, :1], nm.shape[1], axis=1)) or not np.allclose(nm[:, 0], refe, rtol=1e-9, atol=0):
                bad.append(f"{s:+.0f} {arm}: estimate not fixed / not precomputed")
    P(f"    run|git {sorted(gits)}; meta best: ntrain {best.m(cp).get('meta|ntrain')} bstar {best.m(cp).get('meta|bstar')} kron_K {best.m(cp).get('meta|kron_K')} ll_val|kron {best.m(cp).get('meta|ll_val|kron')!r} em_sec {em}; "
      f"ckpt ids: " + "; ".join(f"{n} {str(r.m(cp).get('meta|stagec_ckpt_id', ''))[:60]}" for n, r in raws.items()))
    P(f"    last vs best (every arm x KEYS_RAW, 7 SNR): differing arms {sorted(diff_arms)}; est ald_S2vALD.npz sha {sha16(os.path.join(CONF, 'results/ald/ald_S2vALD.npz'))} prov {prov[:130]!r}; pilots rotation {pilf['rotation'] if 'rotation' in pilf.files else '(none)'}")
    P(f"    test ALD NMSE dB (hhat/H): {' '.join(f'{v:.2f}' for v in nm_test)}; est['nmse']: {' '.join(f'{10 * np.log10(x):.2f}' for x in est['nmse'])}; dev (tune): {' '.join(f'{float(v):.1f}' for v in dv.values())}; max |test - dev| {max(abs(a - float(b)) for a, b in zip(nm_test, dv.values())):.2f} dB")
    P(f"    integrity (grid, holes, one clean commit, meta, ckpt ids, em_sec, genie ②③④ == ①, n = 2560, non-Stage-C 10 arms ② == ①, PIL/ALD raised 0, pilot@1 == loop@1, ALD estimate fixed == precomputed, ALD ckpt): {'OK' if not bad else 'FAILED ' + '; '.join(bad[:8])}")
    # ---- 판정 1 + report pairs (best), last
    D = merged(cp, (best, {a: a for a in best.arms(cp)}), (pil, {"V1-pilot": "V1-pilot", "bstar-pilot": "bstar-pilot"}), (ald, {"ALD-pilot": "ALD-pilot", "ALDv-pilot": "ALDv-pilot"}))
    DL = merged(cp, (last, {a: a for a in last.arms(cp)}))
    for x, y, nm, DD in ((BSTAR, V1, "판정 1 b*->V1 (best)", D), (BSTAR, V1, "report b*->V1 (last)", DL), (BSTAR, SCALAR, "control b*->b*-scalar", D),
                         (BSTAR, "M-ours-dscore-C-V4", "report b*->V4", D), (BSTAR, "M-ours-dscore-C-V4b", "report b*->V4b", D), (BSTAR, "M-ours-dscore-C-V0", "report b*->V0", D)):
        t = table_b(DD, x, y); P(f"    {nm:<28} {x} -> {y}: {fmt_b(t)}; gap {gap(DD, x, y)['text']}")
    cand = dpoints(D, BSTAR)
    res = []
    for s in cand:
        fb, fl = fails(D[s], V1), fails(DL[s], V1); a = int(((fb > 0) & (fl == 0)).sum()); b = int(((fb == 0) & (fl > 0)).sum()); res.append((a, b, sign_p(a, b)))
    A, Bn = sum(r[0] for r in res), sum(r[1] for r in res)
    P(f"    best vs last V1 paired sign (a = best fails, last succeeds) at b* decision points {[f'{s:+.0f}' for s in cand]}: " + " · ".join(f"{a}:{b} (p {p:.2g})" for a, b, p in res) + f" pooled {A}:{Bn} (p {sign_p(A, Bn):.2g})")
    # ---- 판정 2: 13 baselines
    labs, rows = {}, []
    P("    pairB: X -> V1 (b* + 𝔅 12), R_X -3 dB primary [90%] | secondary (decision points):")
    for x in (BSTAR,) + BASELINES:
        t = table_b(D, x, V1); labs[x] = t["lab"]
        fx, fv, fg = (fails(D[-3.0], a) for a in (x, V1, GENIE)); bl = fx.mean()
        if not (0.005 <= bl <= 0.9) or fx.sum() <= fg.sum():
            r1 = f"undefined (BLER {bl:.4f}, F_X {int(fx.sum())}, F_genie {int(fg.sum())})"; Rv = (np.nan, np.nan)
        else:
            R, lo, hi, nn, _ = recovery([(fx, fv, fg)]); r1 = f"{R:.3f} [{lo:.3f}, {hi:.3f}]" + (f" ({nn} undef)" if nn else ""); Rv = (lo, R)
        if t["cand"]:
            R2v, lo2, hi2, nn2, _ = recovery([tuple(fails(D[s], a) for a in (x, V1, GENIE)) for s in t["cand"]]); r2 = f"{R2v:.3f} [{lo2:.3f}, {hi2:.3f}] ({len(t['cand'])} pts)"
        else:
            r2 = "undefined"
        P(f"      {x:<20} {fmt_b(t)}; gap {gap(D, x, V1)['text']}; R_X {r1} | {r2}")
        rows.append((x, int(fx.sum()), t["lab"], Rv))
    D1 = {s: dict(D[s]) for s in D}
    for s in D1:
        D1[s]["R0-pilot@1"] = {"blk_err": np.asarray(D[s]["R0-pilot"]["blk_err"])[:, :1]}
    t = table_b(D1, "R0-pilot@1", V1); fx = fails(D1[-3.0], "R0-pilot@1"); fv, fg = fails(D[-3.0], V1), fails(D[-3.0], GENIE); R, lo, hi, nn, _ = recovery([(fx, fv, fg)])
    P(f"      R0-pilot@1 (house 08_SPEC 1-pass reading; NOT what pair_baselines used): {fmt_b(t)}; F -3 dB {int(fx.sum())}; R_X {R:.3f} [{lo:.3f}, {hi:.3f}]")
    k = sum(1 for x in labs if labs[x] == "(i)"); mm = sum(1 for x in labs if labs[x] == "(ii)"); xs = min(rows, key=lambda r: (r[1], r[0]))
    P(f"    SUMMARY 13 baselines: (i) {k}, (ii) {mm}, undecided {13 - k - mm}; X* = {xs[0]} (F {xs[1]}; runner-up {sorted(rows, key=lambda r: (r[1], r[0]))[1][:2]}); "
      f"R_X* {xs[3][1]:.3f} lower {xs[3][0]:.3f}; sentence condition (k=13, (ii)=0, lower > 0): {'MET' if k == 13 and mm == 0 and xs[3][0] > 0 else 'NOT met'}")
    # ---- R_b* (best / last), ΔR unpaired vs raw_NR16B16e4
    nr = Raw("NR16B16e4"); cpn = ("C6", "S2")
    for nm, DD in (("best", D), ("last", DL)):
        c3 = [tuple(fails(DD[-3.0], a) for a in (BSTAR, V1, GENIE))]; R, lo, hi, nn, F = recovery(c3)
        cd = dpoints(DD, BSTAR); cs = [tuple(fails(DD[s], a) for a in (BSTAR, V1, GENIE)) for s in cd]; R2v, lo2, hi2, nn2, F2 = recovery(cs)
        P(f"    R_b* ({nm}): -3 dB {R:.3f} [{lo:.3f}, {hi:.3f}] (F {F}); decision points {[f'{s:+.0f}' for s in cd]} {R2v:.3f} [{lo2:.3f}, {hi2:.3f}] (F {F2}); per point: "
          + " · ".join(f"{s:+.0f} {recovery([c])[0]:.3f} [{recovery([c])[1]:.3f}, {recovery([c])[2]:.3f}]" for s, c in zip(cd, cs)))
        cn = [tuple(fails(nr.d(cpn, -3.0), a) for a in (BSTAR, V1, GENIE))]; Rn, lon, hin, _, Fn = recovery(cn)
        (l1, h1), (l2, h2), (ld, hd), nu = unpaired_dR(c3, cn)
        P(f"    ΔR ({nm}) = R_S2v {R:.3f} - R_NR16B16e4 {Rn:.3f} (F {Fn}; paired CI [{lon:.3f}, {hin:.3f}]) = {R - Rn:+.3f} [90% unpaired {ld:+.3f}, {hd:+.3f}] undefined {nu}; "
          f"frontier-style own CIs R1 [{l1:.3f}, {h1:.3f}] R2 [{l2:.3f}, {h2:.3f}] -> {'CI < 0' if hd < 0 else 'CI > 0' if ld > 0 else 'contains 0'}")
    # ---- report-only: -3 dB failures, F3 guard
    arms = (GENIE, V1, "M-ours-dscore-C-V4", "M-ours-dscore-C-V4b", "M-ours-dscore-C-V0", BSTAR, SCALAR, "M-ours-gmm32", "R0-pilot", "R1-turbo", R2, R3, "R4-llr", "R4-scvamp", "bstar-pilot", "V1-pilot", "ALD-pilot", "ALDv-pilot")
    P(f"    -3 dB failures ({' · '.join(a.replace('M-ours-', '').replace('dscore-C-', '') for a in arms)}): {fails_row(D, arms)}; last V1 {int(fails(DL[-3.0], V1).sum())}; R0-pilot@1 {int(fails(D[-3.0], 'R0-pilot', 0).sum())}")
    fired = {}
    for s in GRID:
        for a in best.d(cp, s):
            if a == GENIE:
                continue
            nm = np.asarray(best.d(cp, s)[a]["nmse"]); f = (~np.isfinite(nm) | (nm > 10.0)).any(axis=1); fired.setdefault(a, []).append((int(f.sum()), len(f)))
    P("    F3 guard (nmse > 10 or non-finite at any iteration): V0 rates " + " ".join(f"{a / b:.3f}" for a, b in fired["M-ours-dscore-C-V0"]) + "; arms with any firing: " + str(sorted(a for a in fired if any(x for x, _ in fired[a]))))
    P("    SNR-wise failures (best): " + "; ".join(f"{a.replace('M-ours-', '')} {[int(fails(D[s], a).sum()) for s in GRID]}" for a in (GENIE, V1, BSTAR, "V1-pilot", "ALDv-pilot")))
    del best, last, pil, ald, nr, D, DL


def main():
    P("# recompute.py -- record audit ALD/DOP/ROT/ROTMIX/S2V (Fable 5.1, 2026-09-29); raw/ckpt/fits/ald/csv/logs/git only; git HEAD", git("rev-parse", "--short", "HEAD"))
    sec_git()
    sec0_reader_check()
    sec_ald()
    sec_shift("DOP")
    sec_shift("ROT")
    sec_rotmix()
    sec_s2v()
    P("\n# done")


if __name__ == "__main__":
    main()
