"""recompute_path_strata.py -- transcription + internal-consistency check of the three report-only strata tables of §6.2
(SRPB16e4_path_strata.txt, SRPB16e4_leak_strata.txt, SRPB16e4_rank_strata.txt) against the values typed in the record: rows, n sums
= 2560, failure sums = the raw totals, R / BLER / share recomputed from the printed counts, alignment lines.  The trial replay itself
is NOT re-run (heavy); the tools' own 'alignment OK' (first 40 replayed trials bit-identical to the raw genie) is taken as evidence.

usage (cwd = ~/t2/conf):  ~/miniforge3/envs/torch/bin/python -B results/review_next/prereg_audit_2026-10-11/recompute_path_strata.py
"""
import re

CONF = "/home/HTJ/t2/conf/results/review_next/"
ND, NC = [0], [0]


def chk(l, g, e):
    NC[0] += 1
    if g != e:
        ND[0] += 1
        print("  DIFF", l, "file", g, "record", e)


TOT = {-3: (1356, 812, 428), 0: (498, 204, 81), 3: (133, 24, 7)}
REC_PATH = {-3: [(885, 441, 235, 136, 0.675), (854, 450, 265, 143, 0.603), (821, 465, 312, 149, 0.484)],
            0: [(826, 126, 40, 12, 0.754), (868, 151, 68, 31, 0.692), (866, 221, 96, 38, 0.683)],
            3: [(812, 35, 5, 1, 0.882), (849, 41, 7, 1, 0.850), (899, 57, 12, 5, 0.865)]}
t = open(CONF + "SRPB16e4_path_strata.txt").read()
print("# path strata (file SRPB16e4_path_strata.txt, header git 9ad4caa0, 05:20 KST)")
for s in (-3, 0, 3):
    blk = re.search(rf"\n{re.escape(f'{s:+d}')} dB  n=2560(.*?)(?=\n[+-]\d dB  n=2560|\nalignment OK)", t, re.S).group(1)
    rows = re.findall(r"n=\s*(\d+)\s+failures b\*\s+(\d+)\s+V1\s+(\d+)\s+genie\s+(\d+)\s+R = ([\d.]+)", blk)
    rows = [(int(a), int(b), int(c), int(d), float(e)) for a, b, c, d, e in rows]
    chk(f"path {s:+d} rows", rows, REC_PATH[s])
    chk(f"path {s:+d} n sum = 2560", sum(r[0] for r in rows), 2560)
    chk(f"path {s:+d} failure sums = raw totals", tuple(sum(r[j] for r in rows) for j in (1, 2, 3)), TOT[s])
    for n, b, v, g, R in rows:
        chk(f"path {s:+d} n={n} R recomputed", round((b - v) / (b - g), 3), R)
    chk(f"path {s:+d} alignment OK", "bit-identical): OK" in blk, True)
chk("path strata strata labels 0.015-0.435 / 0.45-0.87 / 0.885-1.305 m", all(x in t for x in ("0.015-0.435 m", "0.45-0.87 m", "0.885-1.305 m")), True)

REC_LEAK = {-3: (0.1781, 0.081, (207, 87, 39, 17, 0.686), (2353, 1269, 773, 411, 0.578)),
            0: (0.1784, 0.071, (181, 24, 8, 0, 0.667), (2379, 474, 196, 81, 0.707)),
            3: (0.1825, 0.077, (196, 6, 1, 1, 1.000), (2364, 127, 23, 6, 0.860))}
REC_LEAK_POOL = ((584, 117, 48, 18, 0.697), (7096, 1870, 992, 498, 0.640))
t = open(CONF + "SRPB16e4_leak_strata.txt").read()
print("# leak strata (file SRPB16e4_leak_strata.txt)")
row = r"\s+n=\s*(\d+)\s+failures b\*\s+(\d+)\s+V1\s+(\d+)\s+genie\s+(\d+)\s+R = ([\d.]+)"
for s in (-3, 0, 3):
    m = re.search(rf"\n{re.escape(f'{s:+d}')} dB  n=2560[^\n]*d median ([\d.]+), share d < 0\.1 = ([\d.]+)\n\s+d < 0\.1{row}\n\s+d >= 0\.1{row}", t)
    g = m.groups()
    got = (float(g[0]), float(g[1]), tuple(int(x) for x in g[2:6]) + (float(g[6]),), tuple(int(x) for x in g[7:11]) + (float(g[11]),))
    chk(f"leak {s:+d} (median, share, d<0.1 row, d>=0.1 row)", got, REC_LEAK[s])
    chk(f"leak {s:+d} n sum", got[2][0] + got[3][0], 2560)
    chk(f"leak {s:+d} failure sums = raw totals", tuple(got[2][j] + got[3][j] for j in (1, 2, 3)), TOT[s])
    chk(f"leak {s:+d} share == n(d<0.1)/2560 (3 dp)", round(got[2][0] / 2560, 3), got[1])
    for n, b, v, gg, R in (got[2], got[3]):
        chk(f"leak {s:+d} n={n} R recomputed", round((b - v) / (b - gg), 3), R)
m = re.search(rf"pooled over the 3 decision SNRs\n\s+d < 0\.1{row}\n\s+d >= 0\.1{row}", t)
g = m.groups()
chk("leak pooled rows", (tuple(int(x) for x in g[0:4]) + (float(g[4]),), tuple(int(x) for x in g[5:9]) + (float(g[9]),)), REC_LEAK_POOL)
chk("leak pooled = sums of the 3 SNRs", (sum(REC_LEAK[s][2][j] for s in (-3, 0, 3) for j in [0]), sum(REC_LEAK[s][3][0] for s in (-3, 0, 3))), (584, 7096))
chk("§6.1 label appendix '0.081 / 0.071 / 0.077'", tuple(REC_LEAK[s][1] for s in (-3, 0, 3)), (0.081, 0.071, 0.077))
chk("leak alignment OK at every SNR", t.count("bit-identical): OK"), 3)

REC_RANK = {-3: [(80, 0.031, 0.450, 0.713, 0.875, 36, 57, 70), (1557, 0.608, 0.158, 0.313, 0.522, 246, 487, 812), (864, 0.338, 0.146, 0.274, 0.499, 126, 237, 431), (59, 0.023, 0.339, 0.525, 0.729, 20, 31, 43)],
            0: [(47, 0.018, 0.085, 0.255, 0.511, 4, 12, 24), (1595, 0.623, 0.034, 0.082, 0.203, 54, 131, 323), (861, 0.336, 0.026, 0.067, 0.156, 22, 58, 134), (57, 0.022, 0.018, 0.053, 0.298, 1, 3, 17)],
            3: [(60, 0.023, 0.000, 0.067, 0.217, 0, 4, 13), (1539, 0.601, 0.003, 0.010, 0.060, 4, 16, 93), (887, 0.346, 0.003, 0.005, 0.029, 3, 4, 26), (74, 0.029, 0.000, 0.000, 0.014, 0, 0, 1)]}
t = open(CONF + "SRPB16e4_rank_strata.txt").read()
print("# rank strata (file SRPB16e4_rank_strata.txt)")
for s in (-3, 0, 3):
    blk = re.search(rf"\n{re.escape(f'{s:+d}')} dB  n=2560(.*?)(?=\n[+-]\d dB  n=2560|\nalignment OK)", t, re.S).group(1)
    rows = re.findall(r"n=\s*(\d+) \(([\d.]+)\)\s+BLER genie ([\d.]+)\s+V1 ([\d.]+)\s+b\* ([\d.]+)\s+failures (\d+) / (\d+) / (\d+)", blk)
    rows = [(int(a), float(b), float(c), float(d), float(e), int(f), int(g), int(h)) for a, b, c, d, e, f, g, h in rows]
    chk(f"rank {s:+d} rows", rows, REC_RANK[s])
    chk(f"rank {s:+d} n sum", sum(r[0] for r in rows), 2560)
    chk(f"rank {s:+d} failure sums (genie, V1, b*) = raw totals", tuple(sum(r[j] for r in rows) for j in (5, 6, 7)), (TOT[s][2], TOT[s][1], TOT[s][0]))
    for r in rows:
        chk(f"rank {s:+d} n={r[0]} BLERs = fails/n (3 dp)", (round(r[5] / r[0], 3), round(r[6] / r[0], 3), round(r[7] / r[0], 3)), (r[2], r[3], r[4]))
        chk(f"rank {s:+d} n={r[0]} share (3 dp)", round(r[0] / 2560, 3), r[1])
chk("rank alignment OK at every SNR", t.count("bit-identical): OK"), 3)
print(f"# SUMMARY: {NC[0]} values checked, {ND[0]} differ")
