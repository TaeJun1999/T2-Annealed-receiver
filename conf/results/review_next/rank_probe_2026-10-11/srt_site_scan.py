"""rank_probe_2026-10-11/srt_site_scan.py -- channel statistics only (no receiver, no BLER): scan many candidate BS sites of a
Sionna RT scene with the pool recipe of conf/code/srt_build.py (28 GHz, depth 2, LoS + specular, 8x4 ULAs, UEs in the 120 deg
sector 10-200 m around the boresight, outdoor), fewer UEs per site, to find FIXED BS sites whose links are rarely rank-1.
User, 2026-10-11 CDT: "기지국은 고정하고 위치를 비꿔서 채널을 수집하는게 좋을 거 같은데" / "Deepmimo, Sionna 모두 rank1이 적게
나오는 채널로 찾아봐".  srt_build is imported and only its module constants are overridden here (conf/code untouched).
usage: CUDA_VISIBLE_DEVICES=<g> python -I srt_site_scan.py <scene> <n_sites> <h_bs> <out_dir> [n_cand_per_site] [cap_per_site]"""
import os
import sys

sys.path.insert(0, "/home/HTJ/t2/conf/code")
import srt_build as B

name, nsite, hbs, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
B.NC = int(sys.argv[5]) if len(sys.argv) > 5 else 1024
B.NB = int(sys.argv[6]) if len(sys.argv) > 6 else 512
B.H_BS, B.TARGET = hbs, nsite * B.NB
B.out_dir = lambda Nr: out
os.makedirs(out, exist_ok=True)
print(B.build_scene(name, 8))
