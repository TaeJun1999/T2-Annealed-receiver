"""conference/figures/paper_f2croom.py -- panel (c) of Fig. 2 of the ICC manuscript as BLER vs SNR in the ray-traced room (Sionna RT,
random UE positions; prior SRB), in two variants of the same size for the user to choose from:

  F2c_room.{pdf,png}    2.00 x 2.00 in  = the 11 curves of F21srbhsx_col   (`paper_f21dmc.py SRB hsx`),   -3 .. +15 dB
  F2c_room12.{pdf,png}  2.00 x 2.00 in  = the 11 curves of F21srbhsx12_col (`paper_f21dmc.py SRB hsx12`), -3 .. +12 dB
Either replaces F2c_scale (same size, so the three panels still add up to the 7.05 in of the legend band F2legend_wide); the files
carry no legend, no panel label and no title -- the legend band is shared by the three panels and subfig writes (c).  F2c_scale
and every other figure file stay as they are.

Nothing is recomputed or transcribed (the way of paper_f2sub.py).  `paper_f21dmc.py SRB hsx` and `... SRB hsx12` each run in a
fresh interpreter as the stand-alone script (runpy, run_name "__main__": the mode set-up of that script is in its __main__ block)
with Figure.savefig disabled -- no reference figure file is rewritten -- and return their record text and the drawn content of
their axes; paper_f16deep.main() runs the same way (paper_f2sub.ref) for the curves of F2a_snr.  Asserted, else the script stops
before anything is saved:
  - the three record texts = records/paper_f21srbhsx.txt, records/paper_f21srbhsx12.txt, records/paper_f16deep.txt byte for byte
    (a difference is printed as a diff);
  - every curve redrawn here = the reference artist (x, y, error-bar ends rtol 1e-12; colour, marker, line style, fill, sizes,
    zorder equal), and its shape = the curve of the same name in F2a_snr (one legend serves the three panels);
  - the Counts block of the reference record: n per point 2560 / 2560 / 2560 / 20480 / 20480 / 81920 / 81920 for all 11 curves, and
    every drawn point = failures / n of that block;
  - both files 2.00 x 2.00 in with the same axes box; axes bottom 0.36 in / top 1.95 in = F2a_snr and F2b_budget (the axes table of
    records/paper_f2sub.txt); right end <= 1.96 in; the left end is the smallest multiple of 0.01 in that keeps the y tick labels and
    the y label EDGE in or more inside the canvas (found from the drawn text, the same for both files);
  - x tick labels do not overlap; no marker is cut by the axes box; every artist inside the canvas; every visible text >= 7 pt.
Output next to this script, or in $FIG_OUTDIR.
Run (CPU, about 2 minutes):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= taskset -c 0-15 ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f2croom.py \\
      > ~/t2/conference/figures/records/paper_f2croom.txt
"""
import concurrent.futures
import contextlib
import difflib
import hashlib
import io
import math
import multiprocessing
import os
import re
import runpy
import sys
from unittest import mock

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
import paper_f2sub as S                                        # ref(), grab(), draw(), same_curves(); the sizes of the Fig. 2 panels

HERE = os.path.dirname(os.path.abspath(__file__))
# file -> (mode of paper_f21dmc.py SRB, its record file, the reference figure it would save, x range)
MODES = {"F2c_room": ("hsx", "paper_f21srbhsx.txt", "F21srbhsx_col", (-4, 16)),
         "F2c_room12": ("hsx12", "paper_f21srbhsx12.txt", "F21srbhsx12_col", (-4, 13))}
W, H = S.SIZE["F2c_scale"]                                     # 2.00 x 2.00 in: the panel these files replace
RIGHT, RIGHT_MAX = 0.04, 1.96                                  # in: right margin; the largest allowed right end of the axes
LEFT0, STEP, EDGE = 0.50, 0.01, 0.005                          # in: trial left margin (F2a_snr's); the left end is a multiple of STEP, text >= EDGE inside
YLIM = (3e-05, 1.2)                                            # the Layout line of both reference records
N_PTS = (2560, 2560, 2560, 20480, 20480, 81920, 81920)         # n per SNR point -3 .. +15 dB, every curve
SHAPE = ("color", "marker", "ls", "mfc", "mec", "lw", "ms", "mew", "zorder")
PENDING = """PENDING conf/DECISIONS.md entry (write after FIGHSYDMI16e4 ends) -- the text between the rules goes into conf/DECISIONS.md as one entry, its time stamp taken from `date` when it is written.  It is not there yet: FIGHSYDMI16e4 (run commit ba17b1a4) was running when these files were made, and until its FIGHS_DONE there is no commit on main and conf/DECISIONS.md is not touched (NEXT_EXPERIMENTS_FIGHSYDMI16e4 §1 '순서·자원').
----
원고 Fig. 2 (c) 를 레이 트레이싱 방의 BLER 대 SNR 로 — F2c_room · F2c_room12 (Opus 5.5; 웹 채팅의 프롬프트 2026-10-13 14:0x CDT) | 사용자 결정 (2026-10-12 21:18–21:23 CDT, 웹 채팅): Fig. 2 의 (c) 를 레이 트레이싱 방 (Sionna RT, 무작위 단말 위치; prior SRB) 의 BLER 대 SNR 로 바꾼다 — 배열 규모 결과는 원고 본문 (IV-C) 에 숫자로만 남긴다; 곡선은 지금처럼 11 개 (F2legend_wide 의 범례 그대로). 두 판을 만든 이유: 범위는 사용자가 두 판을 보고 고른다 — 10-12 00:34 CDT 사용자 결정 (방 그림이 단독 그림일 때) 은 원고판 +12 dB 까지, 10-13 웹 채팅의 권고는 +15 dB 판 ((a) 와 x 축이 같고, 방의 +15 dB 에서 두 곡선이 가까워지지만 교차하지 않는다); 두 판은 크기가 같아 원고 분량도 같다. 정해진 것 (프롬프트의 1–8): 1. 새 파일 둘 (PDF + PNG 300 dpi) F2c_room = paper_f21dmc "SRB hsx" 의 곡선 (−3 … +15 dB), F2c_room12 = "SRB hsx12" 의 곡선 (−3 … +12 dB), 둘 다 2.00 × 2.00 in (= F2c_scale; 세 패널 폭의 합 7.05 in 그대로). 2. 축의 아래 끝 0.36 in · 위 끝 1.95 in (= F2a_snr · F2b_budget, assert), 오른쪽 끝 1.96 in 이하, 왼쪽 끝은 y 눈금 글자와 축 이름이 캔버스 안에 들어가는 가장 작은 값 (두 판 같은 축 상자). 3. 참조 그림 F21srbhsx_col / F21srbhsx12_col 의 11 곡선을 그대로 (점, 95 % Wilson 막대 — Proposed · GMM prior · Gaussian prior · Perfect CSI 에만 —, 색 · 마커 · 선 모양 · 채움 · 굵기 · 크기 · cap · zorder); 곡선 모양 = F2a_snr 의 같은 이름 곡선 (assert). 4. x 눈금은 SNR 점마다, x 범위 (−4, 16) / (−4, 13), y 로그 (3e-05, 1.2), 눈금 글자 10^x, 축 이름 "SNR [dB]" · "BLER". 5. 그림 안에 범례 · 패널 표시 · 제목 없음. 6. STIXGeneral · mathtext stix · PDF TrueType, 보이는 글자 7 pt 이상 (10^x 지수는 기존 그림과 같은 예외). 7. 마커 중심이 1.5 pt 안으로 가까운 두 곡선의 점을 기록에 나열 (위치는 바꾸지 않음). 8. x 눈금 글자끼리 겹치지 않음 (assert). 수치는 다시 계산하지도 옮겨 적지도 않았다 — conference/figures/paper_f2croom.py 가 paper_f21dmc.py 를 "SRB hsx" · "SRB hsx12" 로 새 인터프리터에서 Figure.savefig 를 막고 돌려 그 artist 로만 그린다 (두 기록 출력 = records/paper_f21srbhsx.txt · paper_f21srbhsx12.txt 바이트 동일, assert); 새 시행 없음. FIGHSYDMI16e4 실행 중에 그 등록 §1 '순서·자원' 의 동결을 지키며 만들었다: main 커밋 없음, conf/code · Demo · conf/DECISIONS.md · 등록 문서를 건드리지 않음, 만들거나 고친 파일은 conference/figures/ 아래뿐 (paper_f2croom.py, F2c_room · F2c_room12 의 PDF · PNG, records/paper_f2croom.txt, README.md 의 한 행), python · tectonic 은 taskset -c 0-15, GPU 없음, raw_FZ* 는 열지 않음 (읽은 raw 는 SRB 의 것과, F2a_snr 의 곡선 모양을 대조하려고 돌린 paper_f16deep.main() 이 읽는 헤드라인 그림의 raw — 모두 읽기 전용). F2c_scale 과 기존 paper_f*.py · 그 출력은 그대로 둔다. 어느 판을 원고에 넣을지는 사용자가 정한다 (paper 브랜치에 둘 다 있다).
----"""


def ref_room(mode):
    """runs in a fresh interpreter: `paper_f21dmc.py SRB <mode>` as the stand-alone script with Figure.savefig disabled -> its record
    text, the content of its one axes, the entries of its figure legend, its figure size, the file names it would have saved"""
    import matplotlib.figure
    import matplotlib.pyplot as plt
    buf, sys.argv = io.StringIO(), [os.path.join(HERE, "paper_f21dmc.py"), "SRB", mode]
    with mock.patch.object(matplotlib.figure.Figure, "savefig") as sv, contextlib.redirect_stdout(buf):
        try:
            runpy.run_path(sys.argv[0], run_name="__main__")
        except SystemExit as e:                                    # the room modes end with sys.exit(0)
            assert e.code == 0, e.code
    fig = plt.gcf()                                                # the figure the script made last = the one it saves
    assert not (fig.texts or fig.lines or fig.patches or fig.artists or fig.images), "figure-level content ref_room() does not read"
    (ax,) = fig.axes
    return (buf.getvalue(), S.grab(ax), [[t.get_text() for t in g.get_texts()] for g in fig.legends], tuple(fig.get_size_inches()),
            [os.path.basename(c.args[0]) for c in sv.call_args_list])


def record(name, text):
    """the reference script's record text = its record file, byte for byte -> (sha256[:16], lines); else stop with the diff"""
    with open(os.path.join(HERE, "records", name), encoding="utf-8") as f:
        rec = f.read()
    if text != rec:
        raise SystemExit(f"the reference run no longer prints records/{name} -- stopped, nothing written:\n" + "\n".join(
            difflib.unified_diff(rec.splitlines(), text.splitlines(), f"records/{name}", "reference run", lineterm="")))
    return hashlib.sha256(rec.encode()).hexdigest()[:16], rec.count("\n")


def counts(rec):
    """the Counts block of a paper_f21dmc record: {arm: [(failures, n) per SNR point]}"""
    return {l.split()[0]: [(int(k), int(n)) for k, n in re.findall(r"(\d+)/(\d+)", l)] for l in rec.split("\nCounts:\n")[1].split("\n\n")[0].split("\n")}


def main():
    # ---------------- references: the stand-alone scripts, each in a fresh interpreter ----------------
    with concurrent.futures.ProcessPoolExecutor(3, mp_context=multiprocessing.get_context("spawn")) as ex:
        f16 = ex.submit(S.ref, "paper_f16deep")
        room = {n: ex.submit(ref_room, m[0]) for n, m in MODES.items()}
        f16, room = f16.result(), {n: f.result() for n, f in room.items()}
    shas = {"paper_f16deep.txt": record("paper_f16deep.txt", f16[0]), **{m[1]: record(m[1], room[n][0]) for n, m in MODES.items()}}
    (A, _), (order,), RC = f16[1:]                                 # F16deep_wide (a) = the curves of F2a_snr (paper_f2sub asserts it)
    with open(os.path.join(HERE, "records", "paper_f2sub.txt"), encoding="utf-8") as f:   # the axes table of the Fig. 2 panels [in]
        f2 = {m[1]: tuple(float(v) for v in m[2].split(", ")) for m in re.finditer(r"^  (F2\w+) +\[([\d., ]+)\]$", f.read(), re.M)}
    assert set(f2) == set(S.SIDE) and all(f2[n][1] == S.BOTTOM and f2[n][3] == H - S.TOP for n in ("F2a_snr", "F2b_budget")), f2
    assert (W, H) == (2.0, 2.0) and S.SIZE["F2a_snr"][1] == S.SIZE["F2b_budget"][1] == H and W - RIGHT <= RIGHT_MAX + 1e-12
    assert abs(S.SIZE["F2a_snr"][0] + S.SIZE["F2b_budget"][0] + W - S.SIZE["F2legend_wide"][0]) < 1e-9, S.SIZE

    import matplotlib.pyplot as plt
    import numpy as np
    import paper_f16deep as D                                      # the arm -> figure name table, coincide(), the checks (Q), the output folder
    Q, FIG = D.Q, D.FIG
    plt.rcParams.update(RC)                                        # the style F16deep_wide / F2a_snr is drawn with
    names = [D.BY[a].label for a in D.SHOW]
    assert sorted(A["curves"]) == sorted(names) == sorted(x for x in order if x) and len(names) == 11, sorted(A["curves"])
    figs, info = {}, {}
    for name, (mode, recf, refname, xlim) in MODES.items():
        rec, R, legs, size, saved = room[name]
        assert saved == [f"{refname}.pdf", f"{refname}.png"] and size == (3.5, 3.45), (saved, size)   # the run was that figure's
        assert legs == [names] and R["legend"] is None and not R["texts"], (legs, R["texts"])       # its legend: the 11, above the panel; no text in the axes
        assert sorted(R["curves"]) == sorted(names), sorted(R["curves"])
        # --- the curve shapes = F2a_snr's curves of the same name (one legend for the three panels)
        for lab, c in R["curves"].items():
            a = A["curves"][lab]
            keys = SHAPE + (("capsize", "elinewidth", "ezorder") if c["lo"] is not None else ())
            assert (c["lo"] is None) == (a["lo"] is None) and all(c[k] == a[k] for k in keys), (name, lab, {k: (c[k], a[k]) for k in keys if c[k] != a[k]})
        # --- n per point and drawn = counted, from the Counts block of the reference record
        kn = counts(rec)
        assert set(kn) == set(D.SHOW) and all(tuple(n for _, n in v) == N_PTS for v in kn.values()), kn
        npt = len(R["xticks"])
        assert R["xticks"] == [float(s) for s in D.SNRS[:npt]] and npt == (7 if mode == "hsx" else 6), R["xticks"]
        for a in D.SHOW:
            c = R["curves"][D.BY[a].label]
            assert c["x"].tolist() == R["xticks"] and np.allclose(c["y"], [k / n for k, n in kn[a][:npt]], rtol=1e-12, atol=0), a
        # --- axis set-up of the reference = what the prompt fixes (and F2a_snr's where they share it)
        assert R["yscale"] == A["yscale"] == "log" and tuple(float(v) for v in R["ylim"]) == YLIM, (R["yscale"], R["ylim"])
        assert tuple(float(v) for v in R["xlim"]) == xlim and (mode != "hsx" or tuple(A["xlim"]) == xlim), (R["xlim"], A["xlim"])
        assert (R["xlabel"], R["ylabel"]) == (A["xlabel"], A["ylabel"]) == ("SNR [dB]", "BLER"), (R["xlabel"], R["ylabel"])
        # --- draw
        fig = plt.figure(figsize=(W, H))
        ax = fig.add_axes([LEFT0 / W, S.BOTTOM / H, (W - LEFT0 - RIGHT) / W, (H - S.BOTTOM - S.TOP) / H])
        for lab, c in R["curves"].items():
            S.draw(ax, c, lab)
        ax.set_yscale(R["yscale"]); ax.set_ylim(*R["ylim"]); ax.set_xticks(R["xticks"]); ax.set_xlim(*R["xlim"])
        ax.set_xlabel(A["xlabel"], labelpad=Q.XPAD); ax.set_ylabel(A["ylabel"]); ax.tick_params(axis="x", pad=Q.XTPAD)   # as F2a_snr
        S.same_curves(ax, R["curves"], Q)
        fig.canvas.draw()
        figs[name] = fig
        info[name] = dict(R=R, need=LEFT0 - fig.get_tightbbox(fig.canvas.get_renderer()).x0)   # in: the left margin the drawn text takes
    # ---------------- the left end: the smallest multiple of STEP with the text >= EDGE inside, the same for both files ----------------
    left = math.ceil((max(v["need"] for v in info.values()) + EDGE) / STEP - 1e-9) * STEP
    box = [left, S.BOTTOM, W - RIGHT, H - S.TOP]
    for name, fig in figs.items():
        ax, R, px = fig.axes[0], info[name]["R"], 72 / fig.dpi
        ax.set_position([left / W, S.BOTTOM / H, (W - left - RIGHT) / W, (H - S.BOTTOM - S.TOP) / H])
        tight, small = Q.check(fig, name)                          # every artist inside the canvas; every visible text >= 7 pt
        assert tuple(fig.get_size_inches()) == (W, H) and np.allclose(np.array(ax.get_position().extents) * np.tile((W, H), 2), box, rtol=0, atol=1e-12)
        assert tight[0] >= EDGE - 1e-9 and not ax.get_legend() and not fig.legends and not ax.get_title() and not ax.texts and not fig.texts
        S.same_curves(ax, R["curves"], Q)
        # x tick labels: one per SNR point, none overlapping (decision 8)
        xt = sorted((t.get_window_extent() for t in ax.get_xticklabels() if t.get_text() and t.get_visible()), key=lambda e: e.x0)
        gaps = [(b.x0 - a.x1) * px for a, b in zip(xt, xt[1:])]
        if len(xt) != len(R["xticks"]) or min(gaps) <= 0:
            raise SystemExit(f"{name}: x tick labels overlap or are missing (gaps [pt] {np.round(gaps, 2).tolist()}) -- stopped, nothing written")
        yt = [t.get_text() for t in ax.get_yticklabels() if t.get_text() and t.get_visible()
              and R["ylim"][0] <= t.get_position()[1] <= R["ylim"][1]]
        assert yt and all(re.fullmatch(r"\$\\mathdefault\{10\^\{-?\d+\}\}\$", s) for s in yt), yt   # 10^x, the default log labels as in F2a_snr
        # no marker cut by the axes box; Wilson bar ends beyond the y range are clipped at the axis as in the reference figure
        ab, cut = ax.get_window_extent(), []
        for lab, c in R["curves"].items():
            xy = ax.transData.transform(np.column_stack([c["x"], c["y"]]))
            r = (c["ms"] + c["mew"]) / 2 / px
            assert np.isfinite(xy).all() and (xy[:, 0] - r >= ab.x0).all() and (xy[:, 0] + r <= ab.x1).all() \
                and (xy[:, 1] - r >= ab.y0).all() and (xy[:, 1] + r <= ab.y1).all(), (name, lab)
            if c["lo"] is not None:
                cut += [f"{lab} {x:+.0f} dB (lower end {lo:.2e})" for x, lo in zip(c["x"], c["lo"]) if lo < R["ylim"][0]]
                assert (c["hi"] <= R["ylim"][1]).all(), (name, lab)
        info[name].update(tight=tight, small=small, gap=min(gaps), yt=yt, cut=cut, margin=tight[0],
                          near="; ".join(f"{a} / {b} at " + ", ".join(f"{x:+.0f} dB" for x in at) for a, b, at in D.coincide(ax, D.NEAR_PT)) or "none")
    sha = {}
    for name, fig in figs.items():                                 # only now: every assert of both files has passed
        for ext in ("pdf", "png"):
            p = os.path.join(FIG, f"{name}.{ext}")
            fig.savefig(p, dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))
            with open(p, "rb") as f:
                sha[f"{name}.{ext}"] = hashlib.sha256(f.read()).hexdigest()[:16]

    # ---------------- record ----------------
    lim = lambda v: "(" + ", ".join(f"{float(x):g}" for x in v) + ")"
    bars = [l for l, c in info["F2c_room"]["R"]["curves"].items() if c["lo"] is not None]
    txt = ["F2croom -- panel (c) of Fig. 2 of the manuscript as BLER vs SNR in the ray-traced room (Sionna RT 2.1 built-in scene box at 28 GHz, "
           "random UE positions; prior SRB; 8x4, N' = 1.6e5), two variants of the same size: F2c_room = the curves of F21srbhsx_col "
           "(-3 .. +15 dB), F2c_room12 = the curves of F21srbhsx12_col (-3 .. +12 dB).  Nothing recomputed or transcribed: `paper_f21dmc.py SRB "
           "hsx` and `paper_f21dmc.py SRB hsx12` ran as stand-alone scripts in fresh interpreters with Figure.savefig disabled (their figure "
           "files are not rewritten), and every curve here is drawn from the artists of those runs.  No new trial, no number changed.", "",
           "Reference record texts = the record files, byte for byte (asserted): " + "; ".join(
               f"`paper_f21dmc.py SRB {m[0]}` = records/{m[1]} ({shas[m[1]][1]} lines, sha256[:16] {shas[m[1]][0]})" for m in MODES.values())
           + f"; paper_f16deep.main() = records/paper_f16deep.txt ({shas['paper_f16deep.txt'][1]} lines, sha256[:16] "
           f"{shas['paper_f16deep.txt'][0]}) -- the run whose panel (a) is F2a_snr (paper_f2sub.py).", "",
           "Files (saved at exactly figsize; PNG 300 dpi; PDF with TrueType fonts):"]
    txt += [f"  {n:<11} {W} x {H} in ({W * 72:.2f} x {H * 72:.2f} pt)   sha256[:16] pdf {sha[n + '.pdf']}  png {sha[n + '.png']}" for n in MODES]
    txt += [f"  the size of F2c_scale, which either file replaces: panel widths {S.SIZE['F2a_snr'][0]} + {S.SIZE['F2b_budget'][0]} + {W} = "
            f"{S.SIZE['F2legend_wide'][0]:.2f} in = the width of the legend band F2legend_wide (asserted).  F2c_scale is not deleted or changed.",
            "", "Axes, from the bottom-left corner of the file [in] (left, bottom, right, top):"]
    txt += [f"  {n:<11} [{box[0]:.2f}, {box[1]:.2f}, {box[2]:.2f}, {box[3]:.2f}]" for n in MODES]
    txt += [f"  {n:<11} [{', '.join(f'{v:.2f}' for v in f2[n])}]   (records/paper_f2sub.txt)" for n in ("F2a_snr", "F2b_budget")]
    txt += [f"  the same axes box in both files; bottom {box[1]:.2f} in / top {box[3]:.2f} in = F2a_snr and F2b_budget (asserted against the axes "
            f"table of records/paper_f2sub.txt), so the three axes line up in a row; right end {box[2]:.2f} in (<= {RIGHT_MAX} in).  Left end "
            f"{box[0]:.2f} in = the smallest multiple of {STEP} in that keeps the y tick labels and the y label {EDGE} in or more inside the canvas: "
            "the drawn text takes " + ", ".join(f"{v['need']:.4f} in ({n})" for n, v in info.items()) + " left of the axes, which leaves "
            + ", ".join(f"{v['margin']:.4f} in ({n})" for n, v in info.items()) + " to the canvas edge.",
            "", f"Curves (both files): the 11 of paper_f16deep.SHOW -- " + "; ".join(names) + " -- with the points, the 95% Wilson bars (on "
            + "; ".join(bars) + " only), colour, marker, line style, fill, edge, line width, marker size, cap size and zorder of the reference "
            "figure.  Each curve's shape = the curve of the same name in F2a_snr (asserted: colour, marker, line style, fill, edge, line width, marker "
            "size, edge width, zorder; cap size, bar width and bar zorder for the four with bars), so the one legend F2legend_wide serves the three panels.  "
            "No legend, no panel label and no title in either file (asserted)."]
    for n, (mode, recf, refname, xlim) in MODES.items():
        v, R = info[n], info[n]["R"]
        txt += ["", f"{n} (= {refname}): x {lim(R['xlim'])}, ticks " + " ".join(f"{x:+.0f}" for x in R["xticks"]) + f" dB (one per SNR point); y "
                f"{R['yscale']} {lim(R['ylim'])}, tick labels " + " ".join(re.sub(r"\$\\mathdefault\{10\^\{(-?\d+)\}\}\$", r"10^\1", s) for s in v["yt"])
                + f" (the default log labels, as F2a_snr); axis labels '{R['xlabel']}' / '{R['ylabel']}' (the strings of F2a_snr).",
                "  n per point, all 11 curves (the Counts block of the reference record, asserted; every drawn point = failures / n of that block): "
                + (f"-3/0/+3 dB {N_PTS[0]}, +6/+9 dB {N_PTS[3]}, +12/+15 dB {N_PTS[5]}." if mode == "hsx" else
                   f"-3/0/+3 dB {N_PTS[0]}, +6/+9 dB {N_PTS[3]}, +12 dB {N_PTS[5]}.  The +15 dB point is NOT drawn; it was measured (n = {N_PTS[6]}) and is in the "
                   "Counts block of the reference record and in F21srbhsx_col / F2c_room."),
                f"  Decision 7 -- markers of two drawn curves with centres closer than {D.NEAR_PT} pt at this panel size (positions unchanged): {v['near']}.",
                f"  Decision 8 -- x tick labels: {len(R['xticks'])}, none overlapping (asserted); smallest gap between two neighbours {v['gap']:.2f} pt.",
                "  Wilson bar ends below the y range (the bar is clipped at the axis, as in the reference figure): " + ("; ".join(v["cut"]) or "none")
                + ".  No marker is cut by the axes box (asserted).",
                f"  Every artist inside the canvas (tight bbox [in] {np.round(v['tight'], 3).tolist()}); smallest visible text {v['small']:g} pt (nominal "
                "size; the exponents of the 10^x tick labels are smaller, as in the reference figures); STIXGeneral / mathtext stix."]
    txt += ["", "Asserts passed (the script stops before saving otherwise): the three record texts above; every redrawn curve = its reference "
            "artist (x, y, error-bar ends rtol 1e-12; colour, marker, line style, fill, edge, line width, marker size, cap size, zorder equal); curve "
            "shapes = F2a_snr's; n per point and drawn = counted; file size, axes box, bottom / top = F2a_snr and F2b_budget; x and y set-up as "
            "listed; x tick labels clear of each other; markers inside the axes box; every artist inside its canvas; text >= 7 pt.",
            "", PENDING]
    print("\n".join(txt))


if __name__ == "__main__":
    main()
