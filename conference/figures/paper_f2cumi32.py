"""conference/figures/paper_f2cumi32.py -- panel (c) of Fig. 2 of the ICC manuscript as BLER vs SNR on 3GPP UMi 28 GHz, 32x4 (cell C9,
prior UMi28, N' = 1.6e5; user's decision 2026-10-20 17:2x CDT, web chat: the strongest comparisons of the 10/16 campaign -- the GMM
prior with K = 8192 and SBL tuned on loop BLER -- with 3GPP and 32 antennas in one panel; the ray-traced room stays as a row of Table I):

  F2c_umi32.{pdf,png}  2.00 x 2.00 in  = the place of F2c_room_sel; 7 curves = the 8 entries of the legend band F2legend_sel without
                       OMP (pilot-only), which was not run at 32x4; -12 .. +6 dB, n = 2560 per point (test trials 0..2559, the same
                       blocks for every curve); points with line and marker only, no bar
No legend, no panel label and no title in the file (the legend band F2legend_sel is used as it is; subfig writes (c)).  F2c_room*,
F2c_scale and every other figure file stay as they are.

The points are counted from raw the way of paper_f30.py (d) -- frontier_ci.points / fails: the last iteration, a raised block is a
failure -- with analysis.load_raw under the rules of paper_f16deep.raw (a load_raw WARNING stops the script, a NOTE is listed);
Pilot-only LMMSE is the alias R0-pilot@1 of analysis.load_raw, read after the first iteration (the rule of (a)).  The raws are the
ones the records name: the header line of results/review_next/pairB_U28NR32SBL.txt (base, PIL, ALD and SBL raws, with the commit of
each) and results/review_next/run_manifest_U28NR32GCAPe.json (the GMM prior with K = 8192).  The curve shapes are those of the
curves of the same name in F2a_snr (= F2a_snr_nb = F2a_snr_sel): paper_f16deep.main() runs in a fresh interpreter with
Figure.savefig disabled (paper_f2sub.ref, as paper_f2nb.py does) and its artists give colour, marker, line style, fill, edge, line
width, marker size, edge width and zorder.  Asserted, else the script stops before anything is saved:
  - the reference record text = records/paper_f16deep.txt byte for byte;
  - every raw: path and run|git = the record's, the grid C9 / UMi28 at -12 .. +6 dB, test trials 0..2559 in contiguous chunks, no
    load_raw WARNING; the same blocks: the Perfect CSI error arrays of the five raws are identical; K of the GMM prior from the
    meta of the raw (8192 in raw_U28NR32GCAPe, 4096 in the base raw, which is not drawn);
  - counted = recorded, every drawn curve against two records or more: the values of the task prompt (REC; it lists none for
    Pilot-only LMMSE) and the record files pairB_U28NR32B16e4.txt (the SCALE16e4 record, R0-pilot read at @1), pairB_U28NR32SBL.txt,
    conference_plot/F30_scale_trend.txt (d), gcap/compare_U28NR32GCAP.txt; Pilot-only LMMSE also = the 'R0-pilot (@1)' row of
    results/tables_D2_U28NR32B16e4.txt (Table A, BLER to three decimals); R0-pilot after 16 iterations (not drawn) = its rows in
    both pairB records and Table A; the K = 4096 / 8192 failures over the decision points -3 / 0 / +3 dB = 958 / 942;
  - drawn = counted (x, y rtol 1e-12) with the shape of F2a_snr's curve of the same name; no bar artist (no container, no
    collection, 7 lines); no legend, panel label or title;
  - 2.00 x 2.00 in; axes bottom 0.36 in / top 1.95 in = F2a_snr and F2b_budget (the axes table of records/paper_f2sub.txt); right
    end <= 1.96 in; left end by the rule of paper_f2croom.py; y range: the largest lower limit of YLO that keeps every marker inside
    the axes box; x tick labels clear of each other (else labels at -12 / -6 / 0 / +6 only); every artist inside the canvas; every
    visible text >= 7 pt; the rendered PNG 600 x 600 px and PDF 144 x 144 pt with TrueType and no Type 3 font (checked on the
    rendered bytes in memory; the two files are written only after that).
Output next to this script, or in $FIG_OUTDIR.
Run (CPU, about 3 minutes):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= taskset -c 0-15 ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f2cumi32.py \\
      > ~/t2/conference/figures/records/paper_f2cumi32.txt
"""
import concurrent.futures
import glob
import hashlib
import io
import json
import math
import multiprocessing
import os
import re
import struct
import sys

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
import paper_f2croom as C                                      # record(); the (c) margins and the left-end rule; SHAPE
import paper_f2sub as S                                        # ref(), grab(), draw(); the sizes and margins of the Fig. 2 panels

HERE = os.path.dirname(os.path.abspath(__file__))
RV = os.path.normpath(os.path.join(HERE, "..", "..", "conf", "results", "review_next"))
NAME, W, H = "F2c_umi32", 2.00, 2.00                           # the size of F2c_room_sel / F2c_scale
CELL, PRIOR, SNRS, N = "C9", "UMi28", (-12.0, -9.0, -6.0, -3.0, 0.0, 3.0, 6.0), 2560
XLIM, YHI, YLO = (-13, 7), 1.2, (1e-3, 5e-4, 2e-4, 1e-4)       # YLO: candidate lower y limits, largest first
X4 = (-12.0, -6.0, 0.0, 6.0)                                   # x tick labels kept if the seven overlap (the seven tick lines stay)
DP, DP_SUM = (-3.0, 0.0, 3.0), {4096: 958, 8192: 942}          # GMM anchor decision points; failures summed over them (task prompt)
# drawn arm -> raw role (OMP (pilot-only) of F2legend_sel was not run at 32x4); R0-pilot sits in the base raw (asserted)
ROLE = {"M-ours-dscore-C-V1": "base", "ALD-pilot": "ald", "M-ours-bstar": "gcap", "R2-ours-G": "base", "R0-pilot@1": "base",
        "SBL-loop": "sbl", "R5-genie": "base"}
# failures / 2560 at -12 .. +6 dB as the task prompt lists them (a second anchor next to the record files read in main())
REC = {"M-ours-dscore-C-V1": (2219, 1068, 595, 349, 180, 70, 27), "M-ours-bstar": (2277, 1196, 746, 505, 294, 143, 61),
       "R5-genie": (846, 423, 227, 88, 30, 9, 3), "R2-ours-G": (2460, 1468, 919, 676, 436, 238, 102),
       "SBL-loop": (2522, 1772, 979, 671, 386, 174, 83), "ALD-pilot": (2545, 1822, 863, 537, 282, 124, 40)}
R0_AT16 = (2560, 2073, 1096, 747, 468, 254, 123)               # R0-pilot after 16 iterations (pairB_U28NR32SBL.txt) -- not drawn
NOTES = []


def sources():
    """{role: (raw path, commit)} from the records that name the raws"""
    with open(os.path.join(RV, "pairB_U28NR32SBL.txt"), encoding="utf-8") as f:
        head = f.readline()
    m = re.match(r"# pair_baselines (\S+) \+ (\S+) \+ (\S+) \+ (\S+), cell C9, prior UMi28, .* git base=(\w+) extra0=(\w+) pil=(\w+) "
                 r"ald=(\w+); integrity: OK$", head.strip())
    assert m, head
    with open(os.path.join(RV, "run_manifest_U28NR32GCAPe.json"), encoding="utf-8") as f:
        man = json.load(f)
    assert man["result_tag"] == "U28NR32GCAPe" and man["cells"][CELL]["Nr"] == 32 and man["points"] and all(
        v == N for v in man["points"].values()), man["cells"]
    return {"base": (m[1], m[5]), "pil": (m[2], m[7]), "ald": (m[3], m[8]), "sbl": (m[4], m[6]),
            "gcap": (man["raw_dir"], man["git_commit"])}


def load(path, git):
    """one raw: analysis.load_raw with the rules of paper_f16deep.raw, plus the test-trial range and the commit -> (data, meta, digest)"""
    from analysis import PAT, load_raw
    d, meta, w = load_raw("D2", root=path)
    assert not [x for x in w if "WARNING" in x], (path, w)
    NOTES.extend(f"{os.path.basename(path)}: {x.strip()}" for x in w if "NOTE" in x)
    assert sorted(d) == [(CELL, PRIOR, s) for s in SNRS] and list(meta) == [(CELL, PRIOR)], (path, sorted(d))
    chunks = {}                                                    # test trials 0..2559 per point, in contiguous chunks
    for f in sorted(glob.glob(os.path.join(path, "D2_*.npz"))):
        p = PAT.match(os.path.basename(f))
        chunks.setdefault(float(p[8]), []).append((int(p[9]), int(p[10])))
    for s, c in chunks.items():
        c.sort()
        assert c[0][0] == 0 and all(a + n == b for (a, n), (b, _) in zip(c, c[1:])) and c[-1][0] + c[-1][1] == N, (path, s, c)
    assert sorted(chunks) == list(SNRS), (path, sorted(chunks))
    assert {str(d[k]["run"]["git"]) for k in d} == {git}, (path, {str(d[k]["run"]["git"]) for k in d}, git)
    h = hashlib.sha256()                                           # content digest: name and sha256 of every file, sorted
    files = sorted(os.listdir(path))
    for f in files:
        with open(os.path.join(path, f), "rb") as g:
            h.update(f"{f} {hashlib.sha256(g.read()).hexdigest()}\n".encode())
    return d, meta[(CELL, PRIOR)], (len(files), h.hexdigest())


def rec_rows(path, start, n_int=7):
    """{arm: [counts]} from the rows after the first line starting with `start` (the row form of the pairB / F30 record files)"""
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    i = next(j for j, l in enumerate(lines) if l.startswith(start))
    out = {}
    for l in lines[i + 1:]:
        m = re.match(r"\s+(\S+)((?:\s+\d+){%d})\s*$" % n_int, l)
        if not m:
            break
        out[m[1]] = tuple(int(x) for x in m[2].split())
    return out


def rec_gcap():
    """the '[new b*]' line of gcap/compare_U28NR32GCAP.txt -> {arm: failures per SNR} for b* (K = 8192), V1, genie"""
    with open(os.path.join(RV, "gcap", "compare_U28NR32GCAP.txt"), encoding="utf-8") as f:
        line = next(l for l in f if l.startswith("[new b*] failures / n per SNR (b*, V1, genie):"))
    pts = re.findall(r"(-?\+?\d+): (\d+)/(\d+)/(\d+) of 2560", line)
    assert [float(p[0]) for p in pts] == list(SNRS), pts
    return {a: tuple(int(p[i]) for p in pts) for i, a in ((1, "M-ours-bstar"), (2, "M-ours-dscore-C-V1"), (3, "R5-genie"))}


def table_a_r0():
    """the 'R0-pilot (@1)' and 'pilot_C (@16)' rows of the cell C9 / UMi28 block of conf/results/tables_D2_U28NR32B16e4.txt (TABLE A)
    -> {'@1': [BLER to three decimals per SNR], '@16': [...]}"""
    with open(os.path.join(RV, "..", "tables_D2_U28NR32B16e4.txt"), encoding="utf-8") as f:
        lines = f.read().split("\n")
    i = next(j for j, l in enumerate(lines) if l.startswith("--- cell C9 (") and " prior UMi28 " in l)
    out = {}
    for l in lines[i + 1:]:
        if not l.strip():
            break
        if l.startswith("  arm "):
            assert re.findall(r"SNR ([-+]?\d+) dB", l) == ["-12", "-9", "-6", "-3", "+0", "+3", "+6"], l
        m = re.match(r"  (R0-pilot \(@1\)|pilot_C \(@16\)) ", l)
        if m:
            out["@1" if m[1].startswith("R0") else "@16"] = re.findall(r"(\d\.\d{3})\(\d\.\d{3},\d\.\d{3}\)", l)
    assert set(out) == {"@1", "@16"} and all(len(v) == len(SNRS) for v in out.values()), out
    return out


def png_size(b):
    assert b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR", b[:16]
    return struct.unpack(">II", b[16:24])


def main():
    # ---------------- reference: paper_f16deep.main() in a fresh interpreter (the curves of F2a_snr) ----------------
    with concurrent.futures.ProcessPoolExecutor(1, mp_context=multiprocessing.get_context("spawn")) as ex:
        f16 = ex.submit(S.ref, "paper_f16deep").result()
    sha16 = C.record("paper_f16deep.txt", f16[0])
    (A, _), (order,), RC = f16[1:]                                 # F16deep_wide (a) = the curves of F2a_snr (paper_f2sub asserts it)
    with open(os.path.join(HERE, "records", "paper_f2sub.txt"), encoding="utf-8") as f:   # the axes table of the Fig. 2 panels [in]
        f2 = {m[1]: tuple(float(v) for v in m[2].split(", ")) for m in re.finditer(r"^  (F2\w+) +\[([\d., ]+)\]$", f.read(), re.M)}
    assert all(f2[n][1] == S.BOTTOM and f2[n][3] == H - S.TOP for n in ("F2a_snr", "F2b_budget")), f2
    assert (W, H) == S.SIZE["F2c_scale"] and W - C.RIGHT <= C.RIGHT_MAX + 1e-12

    import matplotlib.pyplot as plt
    import numpy as np
    import paper_f16deep as D                                      # the arm -> figure name table, coincide(), the checks (Q), the output folder
    import frontier_ci as F                                        # points(), fails(): the counting of paper_f30.py (d)
    Q, FIG = D.Q, D.FIG
    plt.rcParams.update(RC)                                        # the style F16deep_wide / F2a_snr is drawn with
    arms = [a for a in D.SHOW if a in ROLE]                        # legend order of F16deep_wide
    names = [D.BY[a].label for a in arms]
    assert len(arms) == len(ROLE) == 7 and sorted(A["curves"]) == sorted(D.BY[a].label for a in D.SHOW) == sorted(x for x in order if x)
    assert set(D.SHOW) - set(ROLE) == {"R1-turbo", "R3-bigamp", "SBL-pilot", "OMP-pilot"}   # F2legend_sel = these 7 + OMP (pilot-only)
    assert (A["xlabel"], A["ylabel"], A["yscale"]) == ("SNR [dB]", "BLER", "log"), (A["xlabel"], A["ylabel"])

    # ---------------- raws: the records' paths and commits; same blocks; counted = recorded ----------------
    src = sources()
    raws = {r: load(*src[r]) for r in ("base", "pil", "ald", "gcap", "sbl")}
    keys = F.points(raws["base"][0], CELL)
    assert [k[2] for k in keys] == list(SNRS)
    for r, (d, meta, _) in raws.items():                           # the same blocks: Perfect CSI error arrays identical
        assert F.points(d, CELL) == keys and all(np.array_equal(d[k]["R5-genie"]["blk_err"], raws["base"][0][k]["R5-genie"]["blk_err"])
                                                  for k in keys), r
    assert raws["gcap"][1]["kron_K"] == 8192 and raws["base"][1]["kron_K"] == 4096, (raws["gcap"][1]["kron_K"], raws["base"][1]["kron_K"])
    assert all("R0-pilot" in raws["base"][0][k] and sorted(a for a in raws["pil"][0][k] if a != "run") == ["R5-genie", "V1-pilot", "bstar-pilot"]
               for k in keys)                                      # R0-pilot sits in the base raw; the PIL raw holds the pilot-only priors only

    def count(r, arm):
        d = raws[r][0]
        assert all(len(F.fails(d, k, arm)) == N for k in keys) and np.asarray(d[keys[0]][arm]["blk_err"]).shape[1] == (1 if "@1" in arm else 16)
        return tuple(int(F.fails(d, k, arm).sum()) for k in keys)
    cnt = {a: count(ROLE[a], a) for a in arms}
    r0_16, k4096 = count("base", "R0-pilot"), count("base", "M-ours-bstar")
    pairb = rec_rows(os.path.join(RV, "pairB_U28NR32SBL.txt"), "BLER@16 failures / n per SNR -12 -9 -6 -3 +0 +3 +6 dB:")
    f30 = rec_rows(os.path.join(HERE, "..", "..", "conf", "conference_plot", "F30_scale_trend.txt"),
                   "(d) UMi28 C9 (32×4) BLER@16 (raw_U28NR32B16e4), failures / 2560 per SNR -12 -9 -6 -3 +0 +3 +6 dB:")
    scale = rec_rows(os.path.join(RV, "pairB_U28NR32B16e4.txt"), "BLER@16 failures / n per SNR -12 -9 -6 -3 +0 +3 +6 dB:")
    gcap, tab_a = rec_gcap(), table_a_r0()
    vs = {}                                                        # arm -> the records its counts were asserted against
    for a in arms:
        vs[a] = []
        if a in REC:
            assert cnt[a] == REC[a], (a, cnt[a], REC[a])
            vs[a].append("the task prompt")
        for nm, rec in (("pairB_U28NR32B16e4.txt", scale), ("pairB_U28NR32SBL.txt", pairb), ("F30_scale_trend.txt (d)", f30),
                        ("gcap/compare_U28NR32GCAP.txt [new b*]", gcap)):
            if a in rec and (a != "M-ours-bstar" or nm.startswith("gcap/")):   # b* of the other three records = K 4096
                assert cnt[a] == rec[a], (a, nm, cnt[a], rec[a])
                vs[a].append(nm)
    assert tab_a["@1"] == [f"{k / N:.3f}" for k in cnt["R0-pilot@1"]] and tab_a["@16"] == [f"{k / N:.3f}" for k in r0_16], tab_a
    vs["R0-pilot@1"].append("tables_D2_U28NR32B16e4.txt Table A 'R0-pilot (@1)' (BLER to 3 decimals)")
    assert all(len(v) >= 2 for v in vs.values()), vs
    assert pairb["M-ours-bstar"] == scale["M-ours-bstar"] == f30["M-ours-bstar"] == k4096, k4096
    assert r0_16 == pairb["R0-pilot"] == scale["R0-pilot"] == R0_AT16, r0_16
    dps = [SNRS.index(s) for s in DP]
    assert {4096: sum(k4096[i] for i in dps), 8192: sum(cnt["M-ours-bstar"][i] for i in dps)} == DP_SUM
    assert min(min(v) for v in cnt.values()) > 0                  # no zero-failure point (a log axis could not show one)

    # ---------------- draw: the shapes of F2a_snr's curves, the points counted here ----------------
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([C.LEFT0 / W, S.BOTTOM / H, (W - C.LEFT0 - C.RIGHT) / W, (H - S.BOTTOM - S.TOP) / H])
    x = np.array(SNRS)
    for a, lab in zip(arms, names):
        S.draw(ax, dict(A["curves"][lab], x=x, y=np.array(cnt[a]) / N, lo=None, hi=None), lab)
    got = S.grab(ax)["curves"]                                     # grab() stops on any collection, patch or unlabelled line
    assert list(got) == names
    for a, lab in zip(arms, names):
        g = got[lab]
        assert g["lo"] is None and Q.same(g["x"], x) and Q.same(g["y"], np.array(cnt[a]) / N), lab
        assert all(g[k] == A["curves"][lab][k] for k in C.SHAPE), (lab, {k: (g[k], A["curves"][lab][k]) for k in C.SHAPE if g[k] != A["curves"][lab][k]})
    ax.set_yscale("log"); ax.set_xticks(SNRS); ax.set_xlim(*XLIM)
    ax.set_xlabel(A["xlabel"], labelpad=Q.XPAD); ax.set_ylabel(A["ylabel"]); ax.tick_params(axis="x", pad=Q.XTPAD)   # as F2a_snr

    def cut():
        """drawn points whose marker leaves the axes box"""
        fig.canvas.draw()
        ab, px, out = ax.get_window_extent(), 72 / fig.dpi, []
        for lab, c in S.grab(ax)["curves"].items():
            xy, r = ax.transData.transform(np.column_stack([c["x"], c["y"]])), (c["ms"] + c["mew"]) / 2 / (72 / fig.dpi)
            out += [f"{lab} {s:+.0f} dB" for s, p in zip(c["x"], xy)
                    if not (ab.x0 <= p[0] - r and p[0] + r <= ab.x1 and ab.y0 <= p[1] - r and p[1] + r <= ab.y1)]
        return out
    tried = []                                                     # y range: the largest lower limit of YLO that cuts no marker
    for lo in YLO:
        ax.set_ylim(lo, YHI)
        tried.append((lo, cut()))
        if not tried[-1][1]:
            break
    ylim = ax.get_ylim()
    assert not tried[-1][1] and ylim == (tried[-1][0], YHI), tried
    need = C.LEFT0 - fig.get_tightbbox(fig.canvas.get_renderer()).x0   # in: the left margin the drawn text takes
    left = math.ceil((need + C.EDGE) / C.STEP - 1e-9) * C.STEP      # the rule of paper_f2croom.py
    ax.set_position([left / W, S.BOTTOM / H, (W - left - C.RIGHT) / W, (H - S.BOTTOM - S.TOP) / H])
    assert not cut()

    # ---------------- checks; nothing is saved before all have passed ----------------
    px = 72 / fig.dpi

    def xgaps():
        fig.canvas.draw()
        xt = sorted((t.get_window_extent() for t in ax.get_xticklabels() if t.get_text() and t.get_visible()), key=lambda e: e.x0)
        return len(xt), [(b.x0 - a.x1) * px for a, b in zip(xt, xt[1:])]
    nxt, gaps = xgaps()
    four = nxt != len(SNRS) or min(gaps) <= 0
    if four:                                                       # the prompt's fallback: labels at -12 / -6 / 0 / +6, the seven tick lines stay
        labs = [t.get_text() for t in ax.get_xticklabels()]
        ax.set_xticks(SNRS, [s if v in X4 else "" for v, s in zip(SNRS, labs)])
        nxt, gaps = xgaps()
        assert nxt == len(X4) and min(gaps) > 0, gaps
    tight, small = Q.check(fig, NAME)                              # every artist inside the canvas; every visible text >= 7 pt
    box = np.array(ax.get_position().extents) * np.tile((W, H), 2)
    assert tuple(fig.get_size_inches()) == (W, H) and np.allclose(box, [left, S.BOTTOM, W - C.RIGHT, H - S.TOP], rtol=0, atol=1e-12), box
    assert (round(float(box[1]), 9), round(float(box[3]), 9)) == (f2["F2a_snr"][1], f2["F2a_snr"][3]) == (f2["F2b_budget"][1], f2["F2b_budget"][3])
    assert tight[0] >= C.EDGE - 1e-9 and box[2] <= C.RIGHT_MAX + 1e-12, (tight, box)
    assert not ax.containers and not ax.collections and len(ax.lines) == 7 and [l.get_label() for l in ax.lines] == names   # no bar artist
    assert not ax.get_legend() and not fig.legends and not ax.get_title() and not ax.texts and not fig.texts
    yt = [t.get_text() for t in ax.get_yticklabels() if t.get_text() and t.get_visible() and ylim[0] <= t.get_position()[1] <= ylim[1]]
    assert yt and all(re.fullmatch(r"\$\\mathdefault\{10\^\{-?\d+\}\}\$", s) for s in yt), yt   # 10^x, the default log labels as in F2a_snr
    near = "; ".join(f"{a} / {b} at " + ", ".join(f"{v:+.0f} dB" for v in at) for a, b, at in D.coincide(ax, D.NEAR_PT)) or "none"
    assert plt.rcParams["savefig.bbox"] is None and plt.rcParams["pdf.fonttype"] == 42   # "standard" is stored as None: no tight crop
    out, blobs = {}, {}                                            # rendered in memory and checked first: no file is written if a check fails
    for ext in ("pdf", "png"):
        buf = io.BytesIO()
        fig.savefig(buf, format=ext, dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))
        b = blobs[ext] = buf.getvalue()
        out[ext] = (len(b), hashlib.sha256(b).hexdigest())
        if ext == "pdf":
            box_pt = [float(v) for v in re.search(rb"/MediaBox \[ *([\d. ]+?) *\]", b)[1].split()]
            assert box_pt == [0, 0, W * 72, H * 72] and b"/FontFile2" in b and b"/Type3" not in b, box_pt   # TrueType programs only
        else:
            assert png_size(b) == (round(W * 300), round(H * 300)), png_size(b)
    for ext, b in blobs.items():                                   # only now: every check has passed
        with open(os.path.join(FIG, f"{NAME}.{ext}"), "wb") as f:
            f.write(b)

    # ---------------- record ----------------
    lim = lambda v: "(" + ", ".join(f"{float(u):g}" for u in v) + ")"
    row = lambda v: " ".join(f"{u:5d}" for u in v)
    role_txt = {"base": "base (V1, Gaussian prior, Perfect CSI, Pilot-only LMMSE; its GMM prior is K = 4096, not drawn)",
                "pil": "PIL (pilot-only arms; read for the same-blocks check only)", "ald": "ALD (Annealed Langevin)",
                "gcap": "GCAP (GMM prior, K = 8192)", "sbl": "SBL (SBL in loop, rho 4, n_em 3, cold)"}
    txt = [f"F2cumi32 -- panel (c) of Fig. 2 of the manuscript as BLER vs SNR on 3GPP UMi 28 GHz, 32x4 (cell C9, prior UMi28, Nt 4, T 16, Tp 4, "
           f"N' = 1.6e5), test trials 0..2559, n = {N} per SNR -12 .. +6 dB, the same blocks for every curve; BLER after 16 outer iterations "
           "(Pilot-only LMMSE after the first).  The 7 curves of the legend band F2legend_sel without OMP (pilot-only), which was not run at "
           "32x4.  Points counted from raw (frontier_ci.points / fails, as paper_f30.py (d); analysis.load_raw under the rules of "
           "paper_f16deep.raw); shapes = F2a_snr's curves of the same name (paper_f16deep.main() in a fresh interpreter, Figure.savefig "
           "disabled).  No new trial, no number changed.", "",
           f"Reference record text = records/paper_f16deep.txt byte for byte (asserted; {sha16[1]} lines, sha256[:16] {sha16[0]}).", "",
           "Raws (read-only; path and commit from the header line of results/review_next/pairB_U28NR32SBL.txt and from "
           "results/review_next/run_manifest_U28NR32GCAPe.json; run|git of every point = that commit, asserted; content digest = sha256 of the "
           "sorted lines '<file> <sha256 of the file>'):"]
    for r in ("base", "pil", "ald", "gcap", "sbl"):
        d, meta, (nf, dig) = raws[r]
        txt.append(f"  {role_txt[r]}: {src[r][0]}  run|git {src[r][1]}  {nf} files  digest {dig}  meta bstar {meta['bstar']} kron_K "
                   f"{meta['kron_K']} ll_val|kron {meta['ll_val|kron']}")
    txt += ["  every raw: points C9 / UMi28 at -12 -9 -6 -3 +0 +3 +6 dB, chunks contiguous from trial 0 to 2560 (the test set; asserted); no "
            "load_raw WARNING; " + ("NOTE lines: " + "; ".join(NOTES) if NOTES else "no NOTE line (no raised block)") + ".",
            "  same blocks: the Perfect CSI error arrays (blk_err, 2560 x 16 per point) of the five raws are identical (asserted).",
            "  Pilot-only LMMSE (R0-pilot) is read from the base raw: the PIL raw holds V1-pilot, bstar-pilot and Perfect CSI only (asserted; the "
            "task prompt named the PIL raw).", "",
            f"Failures / {N} per SNR -12 -9 -6 -3 +0 +3 +6 dB (drawn curves; counted from raw = the values asserted against):"]
    for a, lab in zip(arms, names):
        txt.append(f"  {lab:<28} {a:<20} {row(cnt[a])}   = " + "; ".join(vs[a]) + ("  [after the first iteration]" if a == "R0-pilot@1" else ""))
    txt += [f"  not drawn: R0-pilot after 16 iterations {row(r0_16)} (= the R0-pilot rows of pairB_U28NR32B16e4.txt and pairB_U28NR32SBL.txt, the "
            f"'pilot_C (@16)' row of Table A, and the task prompt); GMM prior K = 4096 (base raw) {row(k4096)} (= pairB_U28NR32B16e4.txt, "
            "pairB_U28NR32SBL.txt and F30_scale_trend.txt (d)).",
            f"  over the decision points -3 / 0 / +3 dB (GMM anchor): K = 4096 {DP_SUM[4096]} failures, K = 8192 {DP_SUM[8192]} (asserted).", "",
            "File (saved at exactly figsize; PNG 300 dpi; PDF with TrueType fonts, no Type 3 -- asserted on the rendered bytes before the files were written):",
            f"  {NAME}.pdf  {W} x {H} in ({W * 72:.2f} x {H * 72:.2f} pt)  {out['pdf'][0]} bytes  sha256 {out['pdf'][1]}",
            f"  {NAME}.png  {round(W * 300)} x {round(H * 300)} px  {out['png'][0]} bytes  sha256 {out['png'][1]}", "",
            "Axes, from the bottom-left corner of the file [in] (left, bottom, right, top):",
            f"  {NAME:<11} [{', '.join(f'{v:.2f}' for v in box)}]"]
    txt += [f"  {n:<11} [{', '.join(f'{v:.2f}' for v in f2[n])}]   (records/paper_f2sub.txt)" for n in ("F2a_snr", "F2b_budget")]
    txt += [f"  bottom {box[1]:.2f} in / top {box[3]:.2f} in = F2a_snr and F2b_budget (= F2a_snr_sel, F2b_budget_sel; asserted against the axes table "
            f"of records/paper_f2sub.txt), so the three axes line up in a row; right end {box[2]:.2f} in (<= {C.RIGHT_MAX} in); left end {left:.2f} in = "
            f"the smallest multiple of {C.STEP} in that keeps the y tick labels and the y label {C.EDGE} in or more inside the canvas (the drawn text "
            f"takes {need:.4f} in left of the axes, {tight[0]:.4f} in to the canvas edge; the rule of paper_f2croom.py).", "",
            "Curves: " + "; ".join(names) + " -- line + markers with the colour, marker, line style, fill, edge, line width, marker size, edge "
            "width and zorder of F2a_snr's curve of the same name (asserted), so the legend band F2legend_sel serves this panel.  No bar: no "
            "error-bar container, no collection, exactly 7 lines (asserted).  No legend, no panel label, no title (asserted).",
            f"x {lim(ax.get_xlim())}, tick lines at every SNR point; tick labels: " + (f"-12 -6 0 +6 only (the seven overlapped)" if four else
            "all seven, none overlapping (asserted)") + f"; smallest gap between two neighbouring labels {min(gaps):.2f} pt.",
            f"y log {lim(ylim)}: the largest lower limit of {' / '.join(f'{v:g}' for v in YLO)} that cuts no marker -- " + "; ".join(
                f"{lo:g}: " + (", ".join(c) + " cut" if c else "no marker cut") for lo, c in tried) + "; upper limit 1.2 as F2a_snr.  Tick labels "
            + " ".join(re.sub(r"\$\\mathdefault\{10\^\{(-?\d+)\}\}\$", r"10^\1", s) for s in yt) + " (the default log labels, as F2a_snr); "
            f"axis labels '{A['xlabel']}' / '{A['ylabel']}' (the strings of F2a_snr).",
            f"Decision 7 -- markers of two drawn curves with centres closer than {D.NEAR_PT} pt at this panel size (positions unchanged): {near}.",
            f"Every artist inside the canvas (tight bbox [in] {np.round(tight, 3).tolist()}); smallest visible text {small:g} pt (nominal size; the "
            "exponents of the 10^x tick labels are smaller, as in the reference figures); STIXGeneral / mathtext stix.", "",
            "Asserts passed (the script stops before saving otherwise): the reference record text; raw paths, commits, grid, test-trial chunks, "
            "no WARNING; same blocks (Perfect CSI arrays); K 8192 / 4096 from the raw meta; counted = the task prompt's values and the record "
            "files (every drawn curve against two or more); R0-pilot @16 = its record rows; decision-point sums 958 / 942; drawn = counted with "
            "F2a_snr's shapes; no bar artist; file "
            "size, axes box, bottom / top = F2a_snr and F2b_budget; markers inside the axes box; x tick labels clear of each other; every "
            "artist inside the canvas; text >= 7 pt; PNG / PDF sizes and fonts of the rendered bytes; PIL raw arms = V1-pilot, bstar-pilot, genie."]
    print("\n".join(txt))


if __name__ == "__main__":
    main()
