"""Known-answer raw for code/e1ms_compare.py (development check, not a result): every raw_B16e4k chunk at -3 / 0 / +3 dB with
M-ours-dscore-C-V1 renamed M-ours-dscore-C-V1ms, R5-genie / meta / run kept, run|git = 'katfake0'.  Expected: primary 0:0 x 3, (iv),
+0.00 dB; secondary V4 -> V1-ms = the recorded V4 -> V1 on the 3-point grid.   python kat_make.py <out_dir>"""
import glob, os, sys, numpy as np
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
for f in sorted(glob.glob("/home/HTJ/t2/conf/raw_B16e4k/D2_C2_S2_*_snr*_skip*_n40.npz")):
    if float(f.split("_snr")[1].split("_")[0]) not in (-3.0, 0.0, 3.0):
        continue
    z = np.load(f); d = {k: z[k] for k in z.files if k.startswith(("run|", "meta|", "R5-genie|"))}
    d.update({k.replace("M-ours-dscore-C-V1|", "M-ours-dscore-C-V1ms|"): z[k] for k in z.files if k.startswith("M-ours-dscore-C-V1|")})
    d["run|git"] = np.array("katfake0")
    np.savez(os.path.join(out, os.path.basename(f)), **d)
