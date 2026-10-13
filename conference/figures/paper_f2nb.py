"""conference/figures/paper_f2nb.py -- the panels of Fig. 2 of the ICC manuscript WITHOUT error bars (`_nb` = no bars; user,
2026-10-13 14:23 CDT: "그래프들 보면 분산따라서 점에 위아래로 막대 있는데 이거는 지우는게 좋을 거 같아"), with (c) as BLER vs SNR in the
ray-traced room (Sionna RT, random UE positions; prior SRB).  The SNR range is not decided yet, so (a) and (c) come in two ranges:

  F2a_snr_nb.{pdf,png}     3.00 x 2.00 in  = F2a_snr without its bars, -3 .. +15 dB
  F2a_snr12_nb.{pdf,png}   3.00 x 2.00 in  = the same curves up to +12 dB (the +15 dB point and the segment to it are not drawn)
  F2b_budget_nb.{pdf,png}  2.05 x 2.00 in  = F2b_budget without its bars
  F2c_room_nb.{pdf,png}    2.00 x 2.00 in  = the 11 curves of `paper_f21dmc.py SRB hsx`,   -3 .. +15 dB, no bars
  F2c_room12_nb.{pdf,png}  2.00 x 2.00 in  = the 11 curves of `paper_f21dmc.py SRB hsx12`, -3 .. +12 dB, no bars
Any (a) + (b) + any (c) is 7.05 in wide = the legend band F2legend_wide, which is used as it is (its handles are line + marker, no
bar).  No legend, no panel label and no title in the files.  The files with bars (F2a_snr, F2b_budget, F2c_scale, F2c_room,
F2c_room12) and every other figure file stay as they are.

Nothing is recomputed or transcribed (the way of paper_f2sub.py / paper_f2croom.py): paper_f16deep.main() and the stand-alone
`paper_f21dmc.py SRB hsx` / `... SRB hsx12` each run in a fresh interpreter with Figure.savefig disabled (no reference figure file
is rewritten) and return their record text and the drawn content of their axes.  The points and the line / marker shapes are
taken from those artists; the bar ends are read and not drawn.  Asserted, else the script stops before anything is saved:
  - the three record texts = records/paper_f16deep.txt, paper_f21srbhsx.txt, paper_f21srbhsx12.txt byte for byte;
  - every point redrawn here = the reference artist (x, y rtol 1e-12; F2a_snr12_nb: the points up to +12 dB) with its colour,
    marker, line style, fill, edge, sizes and zorder; the shape of every curve of (c) = the curve of the same name in F2a_snr_nb;
  - n per point and drawn = counted, from the count blocks of the reference records;
  - no bar artist in any of the five figures (no error-bar container, no collection, no cap line);
  - axes bottom 0.36 in / top 1.95 in in all five (= the axes table of records/paper_f2sub.txt); (a) and (b) keep the left and right
    ends of F2a_snr and F2b_budget; (c): right end <= 1.96 in, left end by the rule of paper_f2croom.py, one box for both ranges;
  - (b): the Annealed Langevin plus drawn over the Gaussian prior circle at 1.6e5 -- pixels of each colour that show, counted again;
  - x tick labels do not overlap; every artist inside the canvas; every visible text >= 7 pt.
Output next to this script, or in $FIG_OUTDIR.
Run (CPU, about 2 minutes):
  cd ~/t2/conf && CUDA_VISIBLE_DEVICES= taskset -c 0-15 ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f2nb.py \\
      > ~/t2/conference/figures/records/paper_f2nb.txt
"""
import concurrent.futures
import hashlib
import math
import multiprocessing
import os
import re
import sys

sys.dont_write_bytecode = True                                 # no __pycache__ next to the paper_f*.py or in conf/code
import paper_f2croom as C                                      # ref_room(), record(), counts(); the (c) margins, y range and n per point
import paper_f2sub as S                                        # ref(), grab(), draw(); the sizes and margins of the Fig. 2 panels

HERE = os.path.dirname(os.path.abspath(__file__))
# file -> (panel it replaces (size and, for (a)(b), left / right margins), last SNR drawn or None)
FILES = {"F2a_snr_nb": ("F2a_snr", None), "F2a_snr12_nb": ("F2a_snr", 12.0), "F2b_budget_nb": ("F2b_budget", None),
         "F2c_room_nb": ("F2c_scale", None), "F2c_room12_nb": ("F2c_scale", 12.0)}
ROOM = {"F2c_room_nb": "F2c_room", "F2c_room12_nb": "F2c_room12"}   # -> the key of paper_f2croom.MODES
X12 = (-4, 13)                                                 # x range of the +12 dB variants (= records/paper_f21srbhsx12.txt)
YLIM_A, YLIM_B = (2e-4, 1.2), (0, 0.9)                         # y of F2a_snr (log) and F2b_budget (linear)
N_A = {"ALD-pilot": (2560,) * 7}                               # (a): n per SNR point; every other curve 2560 x 3 + 20480 x 4
PENDING = """PENDING conf/DECISIONS.md entry (write after FIGHSYDMI16e4 ends) -- the text between the rules goes into conf/DECISIONS.md as one entry, its time stamp taken from `date` when it is written.  It is not there yet: FIGHSYDMI16e4 (run commit ba17b1a4) was running when these files were made, and until its FIGHS_DONE there is no commit on main and conf/DECISIONS.md is not touched (NEXT_EXPERIMENTS_FIGHSYDMI16e4 §1 '순서·자원').
----
원고 Fig. 2 의 세 패널을 오차 막대 없이, (c) 는 레이 트레이싱 방의 BLER 대 SNR 로 — F2a_snr_nb · F2a_snr12_nb · F2b_budget_nb · F2c_room_nb · F2c_room12_nb (Opus 5.5; 웹 채팅의 프롬프트 2026-10-13 14:3x CDT) | 사용자 결정 둘: (2026-10-12 21:18–21:23 CDT, 웹 채팅) Fig. 2 의 (c) 를 레이 트레이싱 방 (Sionna RT, 무작위 단말 위치; prior SRB) 의 BLER 대 SNR 로 바꾼다 — 배열 규모 결과는 본문 숫자로만 남긴다; 곡선은 11 개 (F2legend_wide 의 범례) 그대로. (2026-10-13 14:23 CDT, 원문) "그래프들 보면 분산따라서 점에 위아래로 막대 있는데 이거는 지우는게 좋을 거 같아" → Fig. 2 의 모든 패널에서 95 % Wilson 막대를 뺀다. 판을 여럿 만든 이유: SNR 범위를 아직 정하지 않았다 — 사용자가 판을 나란히 보고 고른다 (후보 조합: (a) +15 · (c) +15 [웹 채팅 권고] / (a) +15 · (c) +12 / (a) +12 · (c) +12); 그래서 (a) 와 (c) 를 각각 두 범위로 그렸고, 모든 판은 크기가 같아 원고 분량도 같다. 정해진 것 (프롬프트의 1–10): 1. 새 파일 다섯 (PDF + PNG 300 dpi) — F2a_snr_nb (3.00 × 2.00 in; F2a_snr 에서 막대만 뺀 것, −3 … +15 dB), F2a_snr12_nb (같은 곡선을 +12 dB 까지; +15 dB 점과 그 점으로 가는 선분을 그리지 않음), F2b_budget_nb (2.05 × 2.00 in; F2b_budget 에서 막대만 뺀 것), F2c_room_nb · F2c_room12_nb (2.00 × 2.00 in; paper_f21dmc "SRB hsx" · "SRB hsx12" 의 11 곡선, 막대 없음); 세 패널 폭의 합은 어느 조합이든 7.05 in. 2. 축의 아래 끝 0.36 in · 위 끝 1.95 in (다섯 판 모두; records/paper_f2sub.txt 의 축 표와 assert); (a) 두 판과 (b) 의 왼쪽 · 오른쪽 끝은 F2a_snr · F2b_budget 그대로 ([0.50, 2.94], [0.47, 1.98] in); (c) 두 판은 오른쪽 끝 1.96 in 이하, 왼쪽 끝은 y 눈금 글자와 축 이름이 캔버스 안에 들어가는 가장 작은 값 (두 판 같은 축 상자). 3. 점 · 색 · 마커 · 선 모양 · 채움 · 굵기 · 크기 · zorder 는 참조 artist 그대로, 막대 (세로 선과 cap) 만 그리지 않음; (c) 의 곡선 모양 = F2a_snr_nb 의 같은 이름 곡선 (assert). 4. x 눈금은 SNR 점마다, x 범위 +15 판 (−4, 16) · +12 판 (−4, 13); y 는 (a) 로그 (2e-4, 1.2), (b) 선형 (0, 0.9), (c) 로그 (3e-5, 1.2); 눈금 글자 10^x; 축 이름은 F2a_snr · F2b_budget 의 문자열. 5. 그림 안에 범례 · 패널 표시 · 제목 없음. 6. STIXGeneral · mathtext stix · PDF TrueType, 보이는 글자 7 pt 이상 (10^x 지수는 기존 그림과 같은 예외). 7. 마커 중심이 1.5 pt 안으로 가까운 두 곡선의 점을 기록에 나열 (위치는 바꾸지 않음). 8. x 눈금 글자끼리 겹치지 않음 (assert). 9. (b) 의 1.6×10⁵ 에서 Annealed Langevin 의 작은 플러스를 Gaussian prior 의 큰 원 위에 그리는 것은 그대로, 막대가 빠진 뒤 두 색의 보이는 픽셀 수를 다시 세어 각 ≥ 15 (assert). 10. 다섯 그림에 막대 artist 가 하나도 없음 (assert). 범례 띠 F2legend_wide 는 손잡이가 선 + 마커뿐이라 다시 그리지 않고 그대로 쓴다. 수치는 다시 계산하지도 옮겨 적지도 않았다 — conference/figures/paper_f2nb.py 가 paper_f16deep.main() 과 paper_f21dmc.py ("SRB hsx" · "SRB hsx12") 를 새 인터프리터에서 Figure.savefig 를 막고 돌려 그 artist 로만 그린다 (세 기록 출력 = records/paper_f16deep.txt · paper_f21srbhsx.txt · paper_f21srbhsx12.txt 바이트 동일, assert); 새 시행 없음. FIGHSYDMI16e4 실행 중에 그 등록 §1 '순서·자원' 의 동결을 지키며 만들었다: main 커밋 없음, conf/code · Demo · conf/DECISIONS.md · 등록 문서를 건드리지 않음, 만들거나 고친 파일은 conference/figures/ 아래뿐 (paper_f2nb.py, 다섯 판의 PDF · PNG, records/paper_f2nb.txt, preview/F2nb_combo1–3.png, README.md 의 한 행), python · tectonic 은 taskset -c 0-15, GPU 없음, raw_FZ* 는 열지 않음 (읽은 raw 는 paper_f16deep.main() 과 paper_f21dmc "SRB hsx" · "SRB hsx12" 가 읽는 것뿐, 읽기 전용). 막대 있는 판 (F2a_snr · F2b_budget · F2c_scale · F2c_room · F2c_room12) 과 기존 paper_f*.py · 그 출력은 그대로 둔다. 어느 조합을 원고에 넣을지는 사용자가 정한다 (paper 브랜치에 모두 있다).
----"""


def counts_a(rec):
    """(a) of records/paper_f16deep.txt: {arm: [(failures, n) per SNR point]}"""
    blk = rec.split("\n(a) Failures / trials per SNR")[1].split("\n", 1)[1].split("\n\n")[0]
    return {l.split()[0]: [(int(k), int(n)) for k, n in re.findall(r"(\d+)/(\d+)", l)] for l in blk.split("\n")}


def counts_b(rec, arms):
    """(b) of records/paper_f16deep.txt (failures / 2560 at -3 dB): (the six budgets, {arm: [failures or None per budget]})"""
    rows = [l.split() for l in rec.split("\n(b) Failures / 2560 at -3 dB")[1].split("\n", 1)[1].split("\n\n")[0].split("\n")]
    return ([float(v) for v in next(t for t in rows if t[0] == "N_train")[1:7]],
            {t[0]: [None if v == "-" else int(v) for v in t[1:7]] for t in rows if t and t[0] in arms})


def main():
    # ---------------- references: each in a fresh interpreter, Figure.savefig disabled ----------------
    with concurrent.futures.ProcessPoolExecutor(3, mp_context=multiprocessing.get_context("spawn")) as ex:
        f16 = ex.submit(S.ref, "paper_f16deep")
        room = {n: ex.submit(C.ref_room, C.MODES[m][0]) for n, m in ROOM.items()}
        f16, room = f16.result(), {n: f.result() for n, f in room.items()}
    shas = {"paper_f16deep.txt": C.record("paper_f16deep.txt", f16[0]), **{C.MODES[m][1]: C.record(C.MODES[m][1], room[n][0]) for n, m in ROOM.items()}}
    (A, B), (order,), RC = f16[1:]                                 # F16deep_wide (a), (b) = the curves of F2a_snr, F2b_budget (paper_f2sub asserts it)
    with open(os.path.join(HERE, "records", "paper_f2sub.txt"), encoding="utf-8") as f:
        sub = f.read()
    f2 = {m[1]: tuple(float(v) for v in m[2].split(", ")) for m in re.finditer(r"^  (F2\w+) +\[([\d., ]+)\]$", sub, re.M)}   # axes table [in]
    for n in ("F2a_snr", "F2b_budget"):                            # the boxes (a) and (b) keep
        assert f2[n] == (S.SIDE[n][0], S.BOTTOM, round(S.SIZE[n][0] - S.SIDE[n][1], 2), S.SIZE[n][1] - S.TOP), (n, f2[n])
    assert "\nDecision 4, K labels of (b): NOT DRAWN" in sub       # F2b_budget carries no K label, so 'F2b_budget without its bars' has none
    assert all(abs(S.SIZE["F2a_snr"][0] + S.SIZE["F2b_budget"][0] + S.SIZE[FILES[n][0]][0] - S.SIZE["F2legend_wide"][0]) < 1e-9 for n in ROOM)

    import matplotlib.colors
    import matplotlib.pyplot as plt
    import numpy as np
    import paper_f16deep as D                                      # the arm -> figure name table, coincide(), the checks (Q), the output folder
    Q, FIG = D.Q, D.FIG
    plt.rcParams.update(RC)                                        # the style F16deep_wide / F2a_snr is drawn with
    names = [D.BY[a].label for a in D.SHOW]
    assert sorted(A["curves"]) == sorted(B["curves"]) == sorted(names) == sorted(x for x in order if x) and len(names) == 11
    assert [t["s"] for t in A["texts"]] == ["(a)"] and [t["s"] for t in B["texts"] if not t["note"]] == ["(b)"]   # their panel labels: not redrawn
    assert A["yscale"] == "log" and tuple(A["ylim"]) == YLIM_A and tuple(A["xlim"]) == C.MODES["F2c_room"][3] and tuple(B["ylim"]) == YLIM_B

    def panel(name, left, right):
        w, h = S.SIZE[FILES[name][0]]
        fig = plt.figure(figsize=(w, h))
        return fig, fig.add_axes([left / w, S.BOTTOM / h, (w - left - right) / w, (h - S.BOTTOM - S.TOP) / h])

    def plain(ax, curves, last):
        """every curve as line + markers only (no error bar), its points up to `last`; drawn = the reference points and shapes (asserted)"""
        for lab, c in curves.items():
            m = np.ones(len(c["x"]), bool) if last is None else c["x"] <= last
            S.draw(ax, dict(c, x=c["x"][m], y=c["y"][m], lo=None, hi=None), lab)
        got = S.grab(ax)["curves"]                                 # grab() stops on any collection, patch or unlabelled line
        assert list(got) == list(curves)
        for lab, c in curves.items():
            m, g = (np.ones(len(c["x"]), bool) if last is None else c["x"] <= last), got[lab]
            assert g["lo"] is None and Q.same(g["x"], c["x"][m]) and Q.same(g["y"], c["y"][m]) and all(g[k] == c[k] for k in C.SHAPE), lab

    def snr_axes(ax, R, last):
        ticks = [x for x in R["xticks"] if last is None or x <= last]
        ax.set_yscale(R["yscale"]); ax.set_ylim(*R["ylim"]); ax.set_xticks(ticks); ax.set_xlim(*(R["xlim"] if last is None or R["xlim"][1] < 16 else X12))
        ax.set_xlabel(A["xlabel"], labelpad=Q.XPAD); ax.set_ylabel(A["ylabel"]); ax.tick_params(axis="x", pad=Q.XTPAD)   # as paper_f2sub (a)
        return ticks

    figs, src, info = {}, {}, {n: {} for n in FILES}
    # ---------------- (a): F2a_snr without bars, two ranges ----------------
    ka = counts_a(f16[0])
    assert set(ka) == set(D.SHOW) and all(tuple(n for _, n in ka[a]) == N_A.get(a, C.N_PTS[:3] + (20480,) * 4) for a in D.SHOW), ka
    for a in D.SHOW:                                               # drawn = counted
        assert np.allclose(A["curves"][D.BY[a].label]["y"], [k / n for k, n in ka[a]], rtol=1e-12, atol=0), a
    for name in ("F2a_snr_nb", "F2a_snr12_nb"):
        fig, ax = panel(name, *S.SIDE["F2a_snr"])
        plain(ax, A["curves"], FILES[name][1])
        info[name]["ticks"] = snr_axes(ax, A, FILES[name][1])
        figs[name], src[name] = fig, A
    assert figs["F2a_snr12_nb"].axes[0].get_xlim() == X12 == C.MODES["F2c_room12"][3] and info["F2a_snr12_nb"]["ticks"] == A["xticks"][:-1]
    # ---------------- (b): F2b_budget without bars (no K label, as F2b_budget) ----------------
    nb, kb = counts_b(f16[0], D.SHOW)
    for a in D.SHOW:                                               # drawn = counted: failures / 2560 at the budgets the arm has
        c, pts = B["curves"][D.BY[a].label], [(x, k / 2560) for x, k in zip(nb, kb[a]) if k is not None]
        assert np.allclose(c["x"], [x for x, _ in pts], rtol=1e-12, atol=0) and np.allclose(c["y"], [y for _, y in pts], rtol=1e-12, atol=0), a
    fb, bx = panel("F2b_budget_nb", *S.SIDE["F2b_budget"])
    plain(bx, B["curves"], None)
    bx.set_xscale(B["xscale"]); bx.set_xlim(*B["xlim"]); bx.set_ylim(*B["ylim"]); bx.set_yticks([v for v in B["yticks"] if B["ylim"][0] <= v <= B["ylim"][1]])
    bx.set_xlabel(B["xlabel"], labelpad=Q.XPAD); bx.set_ylabel(B["ylabel"]); bx.tick_params(axis="x", pad=Q.XTPAD)   # as paper_f2sub (b)
    figs["F2b_budget_nb"], src["F2b_budget_nb"] = fb, B
    # decision 9 (= decision 5 of paper_f2sub, counted again without the bars): the Annealed Langevin plus over the Gaussian prior circle at 1.6e5
    ald, gau = B["curves"][S.ALD], B["curves"][S.GAUSS]
    assert len(ald["x"]) == 1 and ald["zorder"] > gau["zorder"], (ald["zorder"], gau["zorder"])
    i16, px = int(np.argmin(np.abs(gau["x"] - ald["x"][0]))), 72 / fb.dpi
    gap_pt = float(np.hypot(*(bx.transData.transform((ald["x"][0], ald["y"][0])) - bx.transData.transform((gau["x"][i16], gau["y"][i16])))) * px)
    fb.canvas.draw()
    buf = np.asarray(fb.canvas.buffer_rgba())[::-1, :, :3].astype(int)   # row 0 = the bottom of the figure, as display coordinates
    cxy = bx.transData.transform((gau["x"][i16], gau["y"][i16]))
    yy, xx = np.mgrid[:buf.shape[0], :buf.shape[1]]
    spot = np.hypot(xx + 0.5 - cxy[0], yy + 0.5 - cxy[1]) <= 2.2 / px
    off_line, off_bar = np.abs(yy + 0.5 - cxy[1]) >= 0.9 / px, np.abs(xx + 0.5 - cxy[0]) >= 0.6 / px   # the bands paper_f2sub leaves out for the circle
    hue = lambda c: np.abs(buf - (np.array(matplotlib.colors.to_rgb(c["color"])) * 255).astype(int)).max(axis=2) <= 40
    seen = {S.GAUSS: int((spot & off_line & off_bar & hue(gau)).sum()), S.ALD: int((spot & hue(ald)).sum())}   # the rule of paper_f2sub
    seen_nobar = int((spot & off_line & hue(gau)).sum())           # the circle with the (now empty) band of its former bar counted too
    assert min(seen.values()) >= S.SEE_PX, seen
    # ---------------- (c): the room, two ranges, no bars ----------------
    for name, key in ROOM.items():
        mode, recf, refname, xlim = C.MODES[key]
        rec, R, legs, size, saved = room[name]
        assert saved == [f"{refname}.pdf", f"{refname}.png"] and size == (3.5, 3.45) and legs == [names] and R["legend"] is None and not R["texts"]
        assert sorted(R["curves"]) == sorted(names) and R["yscale"] == "log" and tuple(float(v) for v in R["ylim"]) == C.YLIM
        assert tuple(float(v) for v in R["xlim"]) == xlim and (R["xlabel"], R["ylabel"]) == (A["xlabel"], A["ylabel"]) == ("SNR [dB]", "BLER")
        for lab, c in R["curves"].items():                         # shapes = F2a_snr_nb's curves of the same name (one legend for the three panels)
            assert all(c[k] == A["curves"][lab][k] for k in C.SHAPE), (name, lab, {k: (c[k], A["curves"][lab][k]) for k in C.SHAPE if c[k] != A["curves"][lab][k]})
        kn, npt = C.counts(rec), len(R["xticks"])
        assert set(kn) == set(D.SHOW) and all(tuple(n for _, n in v) == C.N_PTS for v in kn.values()) and npt == (7 if mode == "hsx" else 6), kn
        for a in D.SHOW:
            assert np.allclose(R["curves"][D.BY[a].label]["y"], [k / n for k, n in kn[a][:npt]], rtol=1e-12, atol=0), a
        fig, ax = panel(name, C.LEFT0, C.RIGHT)
        plain(ax, R["curves"], None)
        info[name]["ticks"] = snr_axes(ax, R, None)
        assert info[name]["ticks"] == R["xticks"] == [float(s) for s in D.SNRS[:npt]] and ax.get_xlim() == xlim
        fig.canvas.draw()
        figs[name], src[name] = fig, R
        info[name]["need"] = C.LEFT0 - fig.get_tightbbox(fig.canvas.get_renderer()).x0   # in: the left margin the drawn text takes
    left = math.ceil((max(info[n]["need"] for n in ROOM) + C.EDGE) / C.STEP - 1e-9) * C.STEP   # the rule of paper_f2croom.py
    for name in ROOM:
        w, h = S.SIZE[FILES[name][0]]
        figs[name].axes[0].set_position([left / w, S.BOTTOM / h, (w - left - C.RIGHT) / w, (h - S.BOTTOM - S.TOP) / h])
    assert S.SIZE["F2c_scale"][0] - C.RIGHT <= C.RIGHT_MAX + 1e-12

    # ---------------- checks of the five figures; nothing is saved before all have passed ----------------
    for name, fig in figs.items():
        ax, R, px = fig.axes[0], src[name], 72 / fig.dpi
        w, h = S.SIZE[FILES[name][0]]
        tight, small = Q.check(fig, name)                          # every artist inside the canvas; every visible text >= 7 pt
        box = np.array(ax.get_position().extents) * np.tile((w, h), 2)
        want = [left, S.BOTTOM, w - C.RIGHT, h - S.TOP] if name in ROOM else [S.SIDE[FILES[name][0]][0], S.BOTTOM, w - S.SIDE[FILES[name][0]][1], h - S.TOP]
        assert tuple(fig.get_size_inches()) == (w, h) and np.allclose(box, want, rtol=0, atol=1e-12), (name, box)
        assert (round(float(box[1]), 9), round(float(box[3]), 9)) == (f2["F2a_snr"][1], f2["F2a_snr"][3]) == (f2["F2b_budget"][1], f2["F2b_budget"][3]), (name, box)
        assert name not in ROOM or tight[0] >= C.EDGE - 1e-9, (name, tight)
        # decision 10: no bar artist; decision 5: no legend, panel label or title
        assert not ax.containers and not ax.collections and len(ax.lines) == 11 and sorted(l.get_label() for l in ax.lines) == sorted(names), name
        assert not ax.get_legend() and not fig.legends and not ax.get_title() and not ax.texts and not fig.texts, name
        got = S.grab(ax)["curves"]                                 # the points once more, on the final layout
        for lab, c in R["curves"].items():
            m = np.ones(len(c["x"]), bool) if FILES[name][1] is None or name in ROOM else c["x"] <= FILES[name][1]
            assert Q.same(got[lab]["x"], c["x"][m]) and Q.same(got[lab]["y"], c["y"][m]), (name, lab)
        # decision 8: x tick labels clear of each other
        xt = sorted((t.get_window_extent() for t in ax.get_xticklabels() if t.get_text() and t.get_visible()
                     and ax.get_xlim()[0] <= t.get_position()[0] <= ax.get_xlim()[1]), key=lambda e: e.x0)
        gaps = [(b.x0 - a.x1) * px for a, b in zip(xt, xt[1:])]
        if min(gaps) <= 0 or (name != "F2b_budget_nb" and len(xt) != len(info[name]["ticks"])):
            raise SystemExit(f"{name}: x tick labels overlap or are missing (gaps [pt] {np.round(gaps, 2).tolist()}) -- stopped, nothing written")
        if name != "F2b_budget_nb":                                # 10^x, the default log labels
            yt = [t.get_text() for t in ax.get_yticklabels() if t.get_text() and t.get_visible() and R["ylim"][0] <= t.get_position()[1] <= R["ylim"][1]]
            assert yt and all(re.fullmatch(r"\$\\mathdefault\{10\^\{-?\d+\}\}\$", s) for s in yt), (name, yt)
            info[name]["yt"] = " ".join(re.sub(r"\$\\mathdefault\{10\^\{(-?\d+)\}\}\$", r"10^\1", s) for s in yt)
        ab, cut = ax.get_window_extent(), []                       # markers cut by the axes box ((c): none, asserted; (a)(b): as F2a_snr / F2b_budget)
        for lab, c in got.items():
            xy, r = ax.transData.transform(np.column_stack([c["x"], c["y"]])), (c["ms"] + c["mew"]) / 2 / px
            cut += [lab for p in xy if not (ab.x0 <= p[0] - r and p[0] + r <= ab.x1 and ab.y0 <= p[1] - r and p[1] + r <= ab.y1)]
        assert name not in ROOM or not cut, (name, cut)
        fmt = (lambda x: f"{x:.3g}") if name == "F2b_budget_nb" else (lambda x: f"{x:+.0f} dB")
        info[name].update(box=box, tight=tight, small=small, gap=min(gaps), nxt=len(xt), cut=sorted(set(cut)),
                          near="; ".join(f"{a} / {b} at " + ", ".join(fmt(x) for x in at) for a, b, at in D.coincide(ax, D.NEAR_PT)) or "none")
    sha = {}
    for name, fig in figs.items():
        for ext in ("pdf", "png"):
            p = os.path.join(FIG, f"{name}.{ext}")
            fig.savefig(p, dpi=300, **({"metadata": {"CreationDate": None}} if ext == "pdf" else {}))
            with open(p, "rb") as f:
                sha[f"{name}.{ext}"] = hashlib.sha256(f.read()).hexdigest()[:16]

    # ---------------- record ----------------
    lim = lambda v: "(" + ", ".join(f"{float(x):g}" for x in v) + ")"
    bars = lambda R: "; ".join(l for l, c in R["curves"].items() if c["lo"] is not None)
    txt = ["F2nb -- the panels of Fig. 2 of the manuscript without error bars (user, 2026-10-13 14:23 CDT), (c) as BLER vs SNR in the ray-traced room "
           "(Sionna RT 2.1 built-in scene box at 28 GHz, random UE positions; prior SRB; 8x4, N' = 1.6e5); (a) and (c) in two SNR ranges because the range is "
           "not decided.  Nothing recomputed or transcribed: paper_f16deep.main() and the stand-alone `paper_f21dmc.py SRB hsx` / `SRB hsx12` ran in fresh "
           "interpreters with Figure.savefig disabled (their figure files are not rewritten); every point here is drawn from the artists of those runs, the "
           "bar ends of those artists were read and are not drawn.  No new trial, no number changed.", "",
           "Reference record texts = the record files, byte for byte (asserted): paper_f16deep.main() = records/paper_f16deep.txt "
           f"({shas['paper_f16deep.txt'][1]} lines, sha256[:16] {shas['paper_f16deep.txt'][0]}); " + "; ".join(
               f"`paper_f21dmc.py SRB {C.MODES[m][0]}` = records/{C.MODES[m][1]} ({shas[C.MODES[m][1]][1]} lines, sha256[:16] {shas[C.MODES[m][1]][0]})"
               for m in ROOM.values()) + ".", "",
           "Files (saved at exactly figsize; PNG 300 dpi; PDF with TrueType fonts):"]
    txt += [f"  {n:<14} {S.SIZE[FILES[n][0]][0]} x {S.SIZE[FILES[n][0]][1]} in ({S.SIZE[FILES[n][0]][0] * 72:.2f} x {S.SIZE[FILES[n][0]][1] * 72:.2f} pt)   "
            f"sha256[:16] pdf {sha[n + '.pdf']}  png {sha[n + '.png']}" for n in FILES]
    txt += [f"  any (a) + (b) + any (c): {S.SIZE['F2a_snr'][0]} + {S.SIZE['F2b_budget'][0]} + {S.SIZE['F2c_scale'][0]} = {S.SIZE['F2legend_wide'][0]:.2f} in = the width of "
            "the legend band F2legend_wide (asserted), which is not redrawn: its handles are line + marker without a bar (paper_f2sub.proxy).  The files with "
            "bars (F2a_snr, F2b_budget, F2c_scale, F2c_room, F2c_room12) are not deleted or changed.",
            "", "Axes, from the bottom-left corner of the file [in] (left, bottom, right, top):"]
    txt += [f"  {n:<14} [{', '.join(f'{v:.2f}' for v in info[n]['box'])}]" for n in FILES]
    txt += [f"  {n:<14} [{', '.join(f'{v:.2f}' for v in f2[n])}]   (records/paper_f2sub.txt)" for n in ("F2a_snr", "F2b_budget")]
    txt += [f"  bottom {S.BOTTOM:.2f} in / top {S.SIZE['F2a_snr'][1] - S.TOP:.2f} in in all five = the axes table of records/paper_f2sub.txt (asserted), so the three axes "
            "of any combination line up in a row; (a) both ranges and (b) keep the left / right ends of F2a_snr and F2b_budget (asserted); (c): one box for both "
            f"ranges, right end {S.SIZE['F2c_scale'][0] - C.RIGHT:.2f} in (<= {C.RIGHT_MAX} in), left end {left:.2f} in = the smallest multiple of {C.STEP} in that keeps the y tick "
            f"labels and the y label {C.EDGE} in or more inside the canvas (the drawn text takes " + ", ".join(f"{info[n]['need']:.4f} in ({n})" for n in ROOM)
            + " left of the axes; the rule of paper_f2croom.py).",
            "", "Curves: the 11 of paper_f16deep.SHOW -- " + "; ".join(names) + " -- in every file, as line + markers with the points, colour, marker, line style, "
            "fill, edge, line width, marker size, edge width and zorder of the reference artist (asserted; x, y rtol 1e-12).  The 95% Wilson bars of the "
            f"reference figures ((a)(b): {bars(A)}; (c): {bars(room['F2c_room_nb'][1])}) are NOT drawn: no vertical bar, no cap.  The shape of every curve of "
            "(c) = the curve of the same name in F2a_snr_nb (asserted), so the one legend serves the three panels.",
            "Decision 10 -- bar artists in the five figures: none (asserted for each: no error-bar container, no collection, exactly 11 lines = the 11 labelled "
            "curves).  Decision 5 -- no legend, no panel label, no title in any file (asserted)."]
    for n in FILES:
        v, R, last = info[n], src[n], FILES[n][1]
        ax = figs[n].axes[0]
        if n == "F2b_budget_nb":
            head = (f"{n} (= F2b_budget without bars): x {R['xscale']} {lim(R['xlim'])}, y linear {lim(R['ylim'])}; axis labels '{R['xlabel']}' / '{R['ylabel']}' (the strings "
                    "of F2b_budget); curves with one point (1.6e5 only): " + "; ".join(l for l, c in R["curves"].items() if len(c["x"]) == 1) + ".  No K label, as in "
                    "F2b_budget (records/paper_f2sub.txt, Decision 4: NOT DRAWN -- the caption carries K).")
            npt = "  n per point: 2560 at every budget, every curve (the (b) block of records/paper_f16deep.txt: failures / 2560 at -3 dB; every drawn point = failures / 2560 of that block, asserted)."
        else:
            what = ("F2a_snr without bars" if n == "F2a_snr_nb" else "F2a_snr without bars, drawn up to +12 dB" if n == "F2a_snr12_nb" else
                    f"the curves of {C.MODES[ROOM[n]][2]} without bars")
            head = (f"{n} (= {what}): x {lim(ax.get_xlim())}, ticks " + " ".join(f"{x:+.0f}" for x in v["ticks"]) + f" dB (one per SNR point); y {R['yscale']} "
                    f"{lim(R['ylim'])}, tick labels {v['yt']} (the default log labels, as F2a_snr); axis labels '{R['xlabel']}' / '{R['ylabel']}' (the strings of F2a_snr).")
            if n in ROOM:
                npt = ("  n per point, all 11 curves (the Counts block of the reference record, asserted; every drawn point = failures / n of that block): "
                       + (f"-3/0/+3 dB {C.N_PTS[0]}, +6/+9 dB {C.N_PTS[3]}, +12/+15 dB {C.N_PTS[5]}." if len(v["ticks"]) == 7 else
                          f"-3/0/+3 dB {C.N_PTS[0]}, +6/+9 dB {C.N_PTS[3]}, +12 dB {C.N_PTS[5]}.  The +15 dB point is NOT drawn; it was measured (n = {C.N_PTS[6]}) and is in the "
                          "Counts block of the reference record and in F21srbhsx_col."))
            else:
                npt = ("  n per point (the (a) block of records/paper_f16deep.txt, asserted; every point = failures / n of that block): -3/0/+3 dB 2560, "
                       + ("+6 .. +15 dB 20480" if last is None else "+6/+9/+12 dB 20480") + "; Annealed Langevin (plug-in) 2560 at every SNR."
                       + ("" if last is None else "  The +15 dB point of every curve and the segment to it are NOT drawn; +15 dB was measured and is in "
                          "records/paper_f16deep.txt and in F2a_snr / F2a_snr_nb."))
        txt += ["", head, npt,
                f"  Decision 7 -- markers of two drawn curves with centres closer than {D.NEAR_PT} pt at this panel size (positions unchanged): {v['near']}.",
                f"  Decision 8 -- x tick labels: {v['nxt']}, none overlapping (asserted); smallest gap between two neighbours {v['gap']:.2f} pt.  Markers cut by the axes "
                "box: " + ("; ".join(v["cut"]) or "none") + (" (asserted)." if n in ROOM else "."),
                f"  Every artist inside the canvas (tight bbox [in] {np.round(v['tight'], 3).tolist()}); smallest visible text {v['small']:g} pt (nominal size; the exponents "
                "of the 10^x tick labels are smaller, as in the reference figures); STIXGeneral / mathtext stix."]
        if n == "F2b_budget_nb":
            txt += [f"  Decision 9 -- the Annealed Langevin (plug-in) point at 1.6e5: its marker centre is {gap_pt:.2f} pt from the Gaussian prior point's ({ald['y'][0]:.4f} vs "
                    f"{gau['y'][i16]:.4f}; positions unchanged).  It stays drawn over the Gaussian prior point (zorder {ald['zorder']:g} > {gau['zorder']:g}): the smaller plus "
                    f"({ald['ms']:g} pt) on the larger circle ({gau['ms']:g} pt).  Pixels of each colour within 2.2 pt of the point on the {fb.dpi:g} dpi canvas, counted "
                    f"again without the bar by the rule of paper_f2sub (the circle outside the band of its dashed line and outside the band its bar had): Gaussian prior "
                    f"{seen[S.GAUSS]}, Annealed Langevin {seen[S.ALD]} (asserted >= {S.SEE_PX} each; with bars, records/paper_f2sub.txt: 26 and 64).  With the now empty "
                    f"band of the former bar counted too, the circle shows {seen_nobar} pixels."]
    txt += ["", "Asserts passed (the script stops before saving otherwise): the three record texts above; every redrawn point = its reference artist (x, y rtol 1e-12; "
            "colour, marker, line style, fill, edge, line width, marker size, edge width, zorder equal); curve shapes of (c) = F2a_snr_nb's; n per point and drawn = "
            "counted; no bar artist; file sizes and axes boxes as listed; x and y set-up as listed; x tick labels clear of each other; (c): markers inside the axes box; "
            "(b): both stacked markers show; every artist inside its canvas; text >= 7 pt.",
            "", PENDING]
    print("\n".join(txt))


if __name__ == "__main__":
    main()
