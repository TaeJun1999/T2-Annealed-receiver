"""prereg_audit_2026-10-11/s6_base_gen.py <pairB file> -- §6 baseline table rows (X -> V1) and the 11-curve failure table, transcribed by
regex from a pair_baselines output (pairB_SP<prior>.txt).  Read-only; no number is typed by hand.  Checked against the DeepMIMO
record: `s6_base_gen.py pairB_SPDMC.txt` reproduces NEXT_EXPERIMENTS_DMCBASE16e4 §6.1 / §6.2 row by row."""
import re
import sys

t = open(sys.argv[1], encoding="utf-8").read()
NAME = {"M-ours-bstar": "b\\*", "M-ours-bstar-scalar": "b\\*-scalar", "M-ours-gmm32": "gmm32"}
print("\n".join(l for l in t.split("\n")[:3]))
print()
for m in re.finditer(r"^(\S+) -> M-ours-dscore-C-V1  \[anchor \S+\]  decision SNRs \[([^\]]*)\]\n((?:    .*\n)+)", t, re.M):
    x, dec, body = m.group(1), " / ".join(s.strip("' ") for s in m.group(2).split(",")), m.group(3)
    st = re.search(r"sign test @16: (.*?)\s+pooled (\S+) p=(\S+)", body)
    ab = " · ".join(re.findall(r"dB (\d+:\d+) p=", st.group(1)))
    pw = re.search(r"POWERED=(\S+)\s+second arm fewer at (\d/\d), first arm fewer at (\d/\d)\s+-> (\S+)", body)
    gap = re.search(r"F_X - F_V1 = (-?\d+) blocks", body)
    r1 = re.search(r"R_X -3 dB \(primary\): (.*)", body).group(1).strip()
    r2 = re.search(r"R_X decision points \(secondary\): (.*?)(?: over|$)", body, re.M).group(1).strip()
    fmt = lambda s: re.sub(r"undefined \(out of range: -3 dB BLER ([\d.]+).*\)", r"정의 안 됨 (범위 밖: \1)", s.replace("[90% ", "["))
    print(f"| {NAME.get(x, x)} | {dec} | {ab} | {st.group(2)} ({st.group(3)}) | {'POWERED' if pw.group(1) == 'True' else 'UNDECIDED'}, "
          f"V1 {pw.group(2)} · X {pw.group(3)} | **{pw.group(4)}** | {gap.group(1) if gap else '?'} | {fmt(r1)} | {fmt(r2)} |")
print()
print("\n".join(l for l in t.split("\n") if l.startswith(("SUMMARY", "'등록된", "    M-ours-bstar=("))))
print()
i = t.index("BLER@16 failures / n per SNR")
print(t[i:])
