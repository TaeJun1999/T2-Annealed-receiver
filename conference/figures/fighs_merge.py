"""conference/figures/fighs_merge.py -- the FIGHS16e4 merge shared by the paper BLER-vs-SNR scripts (paper_f16 (a), f17 (a)(b),
f20 (b), f21, f22, f24 (c)(d), f31 (b)); registration conf/results/review_next/NEXT_EXPERIMENTS_FIGHS16e4.md (§0.1 sources, §1
figure rule; REPORT-ONLY).

A drawn curve keeps its original raw (test trials 0..2559, n = 2560) at -3/0/+3 dB and takes +6/+9/+12/+15 dB from the n = 20480
raw of the new trials 10000..30479: raw_FH<original tag> (§1a), or the HISNR raw where §0.2 reuses it (hs_tag).  One point = one
raw (never pooled); BLER@16 = k/n with the point's own n, a raised block counted as a failure; every merged k/n is asserted against
the tag's count table (results/review_next/fighs_<TAG>.txt, which code/run_fighs16e4.sh writes only after acceptance; HISNR:
hisnr_<TAG>.txt).  A missing raw / count table / arm / SNR, a hole in the chunks or n != 20480 stops the script (SystemExit);
with FIGHS_ALLOW_MISSING=1 that curve keeps its original +6..+15 dB points and a WARNING goes to stderr (testing only -- never a
paper figure).  FIGHS_N2560="<TAG> ..." declares tags the run left invalid / unrun (logs/run_fighs16e4.log INVALID / SKIP /
ABORT): their curves keep the original n = 2560 points at every SNR, stated in the record text (§1 v2, S-4: the caption must say
so too); an accepted tag in that list stops the script.  FIG_OUTDIR=<dir> redirects every saved figure of the scripts (test
renders never overwrite the committed ones).  Self-check (mapping + count-table parser): python -B fighs_merge.py
"""
import os
import re
import sys

import numpy as np
from scipy.stats import fisher_exact

CONF = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "conf"))
RV = os.path.join(CONF, "results", "review_next")
FIG = os.environ.get("FIG_OUTDIR") or os.path.dirname(os.path.abspath(__file__))
os.makedirs(FIG, exist_ok=True)
ALLOW = os.environ.get("FIGHS_ALLOW_MISSING") == "1"
N2560 = set(os.environ.get("FIGHS_N2560", "").replace(",", " ").split())   # §1 S-4: invalid / unrun tags, declared
HS, N_HS = (6.0, 9.0, 12.0, 15.0), 20480
HISNR = {"B16e4k": "HSB16e4k", "NR16B16e4": "HSNR16"}     # §0.2: reused raws (V1 b* R2 R1 R3 genie; R0-pilot is not in them)
HEAD = ("FIGHS16e4 merge (REPORT-ONLY, NEXT_EXPERIMENTS_FIGHS16e4 §1): the record above is the original raws' (n = 2560, unchanged; "
        "its zero-failure / 'not drawn' notes refer to those points).  Drawn: -3/0/+3 dB = those counts, +6/+9/+12/+15 dB = the "
        "counts below (new trials 10000..30479, n = 20480 per SNR; one point = one raw, never pooled).  'rising' = a cell of the "
        "drawn curve where BLER rises with SNR, with its one-sided Fisher p (independent trials per SNR; the +3 -> +6 dB cell "
        "compares the two trial sets; §1: reported, no smoothing / re-run / dropped point):")
_raws = {}


def hs_tag(orig, arm):
    """§0.1: the +6..+15 dB source of curve `arm` drawn from raw_<orig> = the §1a row FH<orig> (the rotation XL raws -> FHROT..),
    except the D2 C2 / C6 base raws, whose arms come from the HISNR raws (§0.2) -- all but R0-pilot (its own row FHB16e4k / FHNR16B16e4)."""
    return HISNR[orig] if orig in HISNR and arm != "R0-pilot" else "FH" + orig.replace("XLROT", "ROT")


def parse(lines):
    """count-table lines -> {(snr, arm): (k, n)}: run_fighs16e4.sh `counts` ('SNR +6  <arm> <k> / <n>  BLER ...') or hisnr_report
    ('SNR +6 dB, n = 20480:' then '    <arm> <k> / <n>  BLER ...')."""
    out, s = {}, None
    for line in lines:
        h = re.match(r"SNR ([+-]\d+) dB, n = \d+:", line)
        m = re.match(r"(?:SNR ([+-]\d+))?\s+(\S+)\s+(\d+) / (\d+)\s+BLER", line)
        if h:
            s = float(h[1])
        elif m:
            s = float(m[1]) if m[1] else s
            out[(s, m[2])] = (int(m[3]), int(m[4]))
    return out


def _table(tag):
    """path of the tag's count table (exists only for an accepted tag), else None."""
    return next((p for p in (os.path.join(RV, f"fighs_{tag}.txt"), os.path.join(RV, f"hisnr_{tag}.txt")) if os.path.exists(p)), None)


def _load(tag):
    """raw_<tag> and its count table, once per tag -> ((data, table), None) or (None, why not usable)."""
    if tag not in _raws:
        root, tab = os.path.join(CONF, f"raw_{tag}"), _table(tag)
        if not os.path.isdir(root):
            _raws[tag] = None, f"raw_{tag} does not exist"
        elif tab is None:
            _raws[tag] = None, f"no count table results/review_next/fighs_{tag}.txt (tag not accepted)"
        else:
            from analysis import load_raw                    # conf/code is on sys.path in every caller
            d, _, w = load_raw("D2", root=root)
            bad = [x.strip() for x in w if "WARNING" in x]   # NOTE lines = raised blocks, kept as failures
            with open(tab, encoding="utf-8") as f:
                _raws[tag] = (None, f"raw_{tag}: {bad[0]}") if bad else ((d, parse(f)), None)
    return _raws[tag]


def merge(snrs, k, n, orig, cell, prior, arm):
    """One drawn curve, BLER@16: failures k / trials n per SNR of `snrs` from raw_<orig> -> (k, n, record line) with the +6/+9/+12/+15 dB
    entries from raw_<hs_tag(orig, arm)> (all four or none); missing data -> SystemExit, or FIGHS_ALLOW_MISSING=1 -> unchanged + WARNING;
    a tag declared in FIGHS_N2560 -> unchanged at every SNR, stated (§1 S-4)."""
    snrs, k = [float(s) for s in snrs], np.array(k, dtype=int)
    n = np.array(np.broadcast_to(n, k.shape), dtype=int)
    tag = hs_tag(orig, arm)
    if tag in N2560:
        if _table(tag):
            raise SystemExit(f"FIGHS16e4: {tag} is in FIGHS_N2560 but was accepted (its count table exists); the list is only for "
                             "tags the run left invalid / unrun (§1)")
        print(f"NOTE FIGHS16e4: curve {arm} ({cell} {prior}) keeps raw_{orig} (n = 2560) at every SNR: {tag} declared invalid / "
              "unrun (FIGHS_N2560) -- the caption must say so (§1)", file=sys.stderr)
        src = f"raw_{orig} at every SNR -- this curve is n = 2560 over the whole range: {tag} invalid / unrun (§1)"
    else:
        got, why = _load(tag)
        new = []
        for s in HS if got else ():
            d, tab = got
            e = d.get((cell, prior, s), {}).get(arm, {}).get("blk_err")
            if e is None:
                why = f"raw_{tag} has no {arm} at {cell} {prior} {s:+.0f} dB"
                break
            e = np.asarray(e, float)[:, -1]
            kk, nn = int(np.where(np.isfinite(e), e, 1.0).sum()), len(e)
            if nn != N_HS:
                why = f"raw_{tag} {arm} {s:+.0f} dB has n = {nn}, not {N_HS} (run incomplete?)"
                break
            assert tab.get((s, arm)) == (kk, nn), (tag, arm, s, (kk, nn), tab.get((s, arm)))   # §1: raw == count table
            new.append((snrs.index(s), kk, nn))
        if why:
            msg = f"FIGHS16e4: curve {arm} ({cell} {prior}, original raw_{orig}) takes +6..+15 dB from raw_{tag}, but {why}"
            if not ALLOW:
                raise SystemExit(msg + ".  Regenerate after the FIGHS16e4 run has finished and been accepted (a tag the run left "
                                 "invalid / unrun: FIGHS_N2560=<TAG>, §1; FIGHS_ALLOW_MISSING=1 FIG_OUTDIR=<scratch dir> renders a "
                                 "test figure with the original points).")
            print(f"WARNING {msg} -> kept the original raw_{orig} points (n = 2560) at +6..+15 dB (FIGHS_ALLOW_MISSING=1: test "
                  "render only, not a paper figure)", file=sys.stderr)
            src = f"FALLBACK to the original raw_{orig}: {why} -- TEST RENDER ONLY"
        else:
            for i, kk, nn in new:
                k[i], n[i] = kk, nn
            src = f"raw_{tag}"
    up = [f"{snrs[i]:+.0f}->{snrs[i + 1]:+.0f} dB p={fisher_exact([[k[i + 1], n[i + 1] - k[i + 1]], [k[i], n[i] - k[i]]], alternative='greater').pvalue:.2g}"
          for i in range(len(k) - 1) if k[i + 1] * n[i] > k[i] * n[i + 1]]          # BLER(i+1) > BLER(i), exact in integers
    return k, n, (f"    {arm:<20}@16  " + " ".join(f"{a}/{b}" for s, a, b in zip(snrs, k, n) if s in HS) + f"   ({src})"
                  + (f"   rising: {'; '.join(up)}" if up else ""))


def block(lines):
    """the record block a script appends after its unchanged original record text."""
    return ["", HEAD] + lines if lines else []


def zero_arrows(ax, xs, ns, color, w=0.3):
    """Zero-failure points (0/n blocks) cannot sit on a log axis: a short cap at the 95% Wilson upper bound z^2/(n + z^2) of the
    point's own n (2560 -> 1.50e-3, 20480 -> 1.87e-4) and a downward arrow (the F17 convention), never a made-up value; the curve
    itself breaks there (NaN)."""
    for s, n in zip(xs, np.broadcast_to(ns, np.shape(xs))):
        hi = 1.96 ** 2 / (n + 1.96 ** 2)
        ax.plot([s - w, s + w], [hi, hi], color=color, lw=1.0, zorder=6)
        ax.annotate("", xy=(s, hi / 1.7), xytext=(s, hi), zorder=6,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=0.9, mutation_scale=6.5, shrinkA=0, shrinkB=0))


if __name__ == "__main__":
    assert [hs_tag(o, a) for o, a in (("B16e4k", "R5-genie"), ("B16e4k", "R0-pilot"), ("NR16B16e4", "M-ours-bstar"),
                                      ("NR16B16e4", "R0-pilot"), ("SPB16e4k", "SBL-loop"), ("PILMX", "V1-pilot"), ("D3B16e4", "R5-genie"),
                                      ("XLROTbB16e4k", "R1-turbo"), ("ROTaB16e4k", "R5-genie"), ("XAROTaB16e4k", "ALD-pilot"))] == \
        ["HSB16e4k", "FHB16e4k", "HSNR16", "FHNR16B16e4", "FHSPB16e4k", "FHPILMX", "FHD3B16e4", "FHROTbB16e4k", "FHROTaB16e4k",
         "FHXAROTaB16e4k"]
    fighs = [f"SNR {s:+.0f}  {a:<20} {k:6d} / {N_HS}  BLER {k / N_HS:.2e}  95% [0, 1]" for s, a, k in ((6.0, "R5-genie", 66), (15.0, "R0-pilot", 3))]
    assert parse(["# run_fighs16e4 git x raw_FHB16e4k C2: ...", "SNR +6  R0-pilot@1   218 / 20480  BLER", *fighs]) == \
        {(6.0, "R5-genie"): (66, N_HS), (15.0, "R0-pilot"): (3, N_HS), (6.0, "R0-pilot@1"): (218, N_HS)}
    with open(os.path.join(RV, "hisnr_HSNR16.txt"), encoding="utf-8") as f:
        t = parse(f)
    assert [t[(s, "R5-genie")] for s in HS] == [(17, N_HS), (16, N_HS), (7, N_HS), (7, N_HS)], t
    # the 'rising' convention = DECISIONS 2026-10-07 06:59 KST (Doppler genie 9 -> 15 dB, 22 -> 41 of 2560: one-sided p 0.011)
    assert f"{fisher_exact([[41, 2560 - 41], [22, 2560 - 22]], alternative='greater').pvalue:.2g}" == "0.011"
    print("fighs_merge self-check OK")
