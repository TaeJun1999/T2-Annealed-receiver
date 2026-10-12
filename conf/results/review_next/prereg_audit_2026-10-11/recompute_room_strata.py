"""recompute_room_strata.py -- transcription + internal-consistency check of the two report-only strata tables of §6.2
(SRBB16e4_leak_strata.txt, SRBB16e4_rank_strata.txt) against the values typed in the record: rows, n sums = 2560, failure sums = the
raw totals, R / BLER / share recomputed from the printed counts, alignment lines.  The trial replay itself is NOT re-run (heavy).

usage (cwd = ~/t2/conf):  ~/miniforge3/envs/torch/bin/python -B results/review_next/prereg_audit_2026-10-11/recompute_room_strata.py
"""
import re

CONF = "/home/HTJ/t2/conf/results/review_next/"
ND, NC = [0], [0]


def chk(l, g, e):
    NC[0] += 1
    if g != e:
        ND[0] += 1
        print("  DIFF", l, "file", g, "record", e)


TOT = {-3: (827, 704, 299), 0: (153, 126, 36), 3: (40, 17, 9)}
# record §6.2 leak bullet: d<0.1 n (11/12/19, share 0.004/0.005/0.007, no R), d>=0.1 rows, pooled 7638: 1016/841/341 -> 0.259, medians
REC_LEAK = {-3: (0.3445, 0.004, (11, 3, 3, 2), (2549, 824, 701, 297, 0.233)),
            0: (0.3443, 0.005, (12, 1, 2, 1), (2548, 152, 124, 35, 0.239)),
            3: (0.3346, 0.007, (19, 0, 1, 0), (2541, 40, 16, 9, 0.774))}
REC_LEAK_POOL = ((42, 4, 6, 3), (7638, 1016, 841, 341, 0.259))
t = open(CONF + "SRBB16e4_leak_strata.txt").read()
print("# leak strata (file SRBB16e4_leak_strata.txt, header git 7d524638)")
row_lo = r"\s+n=\s*(\d+)\s+failures b\*\s+(\d+)\s+V1\s+(\d+)\s+genie\s+(\d+)\s+\(n < 100: R not written\)"
row_hi = r"\s+n=\s*(\d+)\s+failures b\*\s+(\d+)\s+V1\s+(\d+)\s+genie\s+(\d+)\s+R = ([\d.]+)"
for s in (-3, 0, 3):
    m = re.search(rf"\n{re.escape(f'{s:+d}')} dB  n=2560[^\n]*d median ([\d.]+), share d < 0\.1 = ([\d.]+)\n\s+d < 0\.1{row_lo}\n\s+d >= 0\.1{row_hi}", t)
    g = m.groups()
    got = (float(g[0]), float(g[1]), tuple(int(x) for x in g[2:6]), tuple(int(x) for x in g[6:10]) + (float(g[10]),))
    chk(f"leak {s:+d} (median, share, d<0.1 row, d>=0.1 row)", got, REC_LEAK[s])
    chk(f"leak {s:+d} n sum", got[2][0] + got[3][0], 2560)
    chk(f"leak {s:+d} failure sums = raw totals", tuple(got[2][j] + got[3][j] for j in (1, 2, 3)), TOT[s])
    chk(f"leak {s:+d} share == n(d<0.1)/2560 (3 dp)", round(got[2][0] / 2560, 3), got[1])
    n, b, v, gg, R = got[3]
    chk(f"leak {s:+d} n={n} R recomputed", round((b - v) / (b - gg), 3), R)
    chk(f"leak {s:+d} d<0.1 n < 100 so R not written (record: '도구가 R 을 적지 않았다')", got[2][0] < 100, True)
m = re.search(rf"pooled over the 3 decision SNRs\n\s+d < 0\.1{row_lo}\n\s+d >= 0\.1{row_hi}", t)
g = m.groups()
chk("leak pooled rows", (tuple(int(x) for x in g[0:4]), tuple(int(x) for x in g[4:8]) + (float(g[8]),)), REC_LEAK_POOL)
chk("leak pooled = sums of the 3 SNRs", (sum(REC_LEAK[s][2][0] for s in (-3, 0, 3)), sum(REC_LEAK[s][3][0] for s in (-3, 0, 3))), (42, 7638))
chk("leak pooled R recomputed", round((1016 - 841) / (1016 - 341), 3), 0.259)
chk("§6.1 label appendix '0.004 / 0.005 / 0.007'", tuple(REC_LEAK[s][1] for s in (-3, 0, 3)), (0.004, 0.005, 0.007))
chk("§6.2 'd 중앙값 0.3445 / 0.3443 / 0.3346'", tuple(REC_LEAK[s][0] for s in (-3, 0, 3)), (0.3445, 0.3443, 0.3346))
chk("leak alignment OK at every SNR", t.count("bit-identical): OK"), 3)
chk("leak file: decision SNRs [-3, 0, 3], git 7d524638", "decision SNRs [-3.0, 0.0, 3.0]" in t and "# git commit  : 7d524638" in t, True)

REC_RANK = {-3: [(81, 0.032, 0.321, 0.481, 0.580, 26, 39, 47), (1337, 0.522, 0.123, 0.291, 0.341, 165, 389, 456), (1021, 0.399, 0.082, 0.227, 0.272, 84, 232, 278), (121, 0.047, 0.198, 0.364, 0.380, 24, 44, 46)],
            0: [(80, 0.031, 0.150, 0.287, 0.325, 12, 23, 26), (1335, 0.521, 0.010, 0.049, 0.061, 14, 65, 81), (1054, 0.412, 0.009, 0.035, 0.039, 10, 37, 41), (91, 0.036, 0.000, 0.011, 0.055, 0, 1, 5)],
            3: [(92, 0.036, 0.065, 0.087, 0.174, 6, 8, 16), (1334, 0.521, 0.002, 0.005, 0.012, 3, 7, 16), (1051, 0.411, 0.000, 0.002, 0.007, 0, 2, 7), (83, 0.032, 0.000, 0.000, 0.012, 0, 0, 1)]}
t = open(CONF + "SRBB16e4_rank_strata.txt").read()
print("# rank strata (file SRBB16e4_rank_strata.txt)")
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
chk("rank-1 (share >= 0.95) layer is 3.1-3.6 % of the trials (§3 item 14 'rank-1 층이 거의 비어 있을 것' / §0 test-pool 0.033)", [REC_RANK[s][0][1] for s in (-3, 0, 3)], [0.032, 0.031, 0.036])
print(f"# SUMMARY: {NC[0]} values checked, {ND[0]} differ")
