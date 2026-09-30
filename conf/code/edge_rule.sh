#!/bin/bash
# GMM kron-K grid edge rule for the stage-2 fits (project rule, DECISIONS 6b1de688 principle 1): whenever the merged fit of the
# largest kron K of a tag exists, recompute b* (arms.gmm_selection, validation ll); if b* = kron at that largest K and K < 4096,
# queue the 2K restarts 0-2 (GPU) + merge (CPU, waits for the 3 candidates) on the gpu_sched.sh queue logs/gpuq.txt (once).  A tag is DONE when b* is interior or K = 4096 is fitted.
# Full-family K is interior for all three tags (checked 09-30), so only kron is extended.  Log logs/edge_rule.log, end EDGE_RULE_DONE.
cd /home/HTJ/t2_wtS/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/edge_rule.log; Q=logs/gpuq.txt
TAGS="NR32B16e4:S2:32 U28NR16B16e4:UMi28:16 U28NR32B16e4:UMi28:32"
while true; do
  pending=0
  for t in $TAGS; do IFS=: read tag pr nr <<< "$t"
    [ -f logs/edge_done_$tag ] && continue; pending=1
    out=$(CUDA_VISIBLE_DEVICES= $P - "$tag" "$pr" "$nr" <<'PY' 2>/dev/null
import sys, os, glob, re; sys.path.insert(0, "code"); import arms as A
tag, pr, nr = sys.argv[1], sys.argv[2], int(sys.argv[3]); d = os.path.join("results", f"gmm_fits_D2_{tag}")
ks = sorted(int(re.search(r"kronK(\d+)_n160000\.npz$", f).group(1)) for f in glob.glob(f"{d}/fit_{pr}_Nr{nr}_kronK*_n160000.npz"))
A.D2_FITS = d; fits, llv, bstar, kK = A.gmm_selection("D2", pr, nr, 160000)
print(max(ks), bstar, kK)
PY
)
    read kmax bstar kK <<< "$out"; [ -z "$kmax" ] && continue
    if [ "$bstar" != "kron" ] || [ "$kK" != "$kmax" ]; then
      echo "[edge $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $tag DONE: b* = $bstar (kron_K $kK) interior; largest kron K fitted $kmax" >> $L; touch logs/edge_done_$tag; continue; fi
    if [ "$kmax" -ge 4096 ]; then
      echo "[edge $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $tag DONE: b* = kron $kK at the 4096 stop (grid-edge caveat)" >> $L; touch logs/edge_done_$tag; continue; fi
    k2=$((kmax * 2)); POPT=""; [ "$pr" != "S2" ] && POPT=" --prior $pr"
    if ! grep -q "kron $k2 160000 $tag " $Q && [ ! -f logs/edge_queued_${tag}_$k2 ]; then
      F="$P code/fit_gpu.py $nr kron $k2 160000 $tag"; O=">> logs/fit_edge_$tag.log 2>&1"
      { for r in 0 1 2; do echo "50 GPU r${r}_${tag}_$k2 $F --restart $r$POPT $O"; done
        echo "50 WAIT:results/gmm_fits_D2_$tag/fit_${pr}_Nr${nr}_kronK${k2}_n160000.k0r[012].npz:3:CPU m_${tag}_$k2 $F --merge$POPT $O"
      } | flock $Q.lock tee -a $Q > /dev/null
      touch logs/edge_queued_${tag}_$k2
      echo "[edge $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $tag: b* = kron $kK = largest K -> queued kron $k2 (3 restarts + merge) on gpuq" >> $L
    fi
  done
  [ $pending -eq 0 ] && { echo "EDGE_RULE_DONE" >> $L; break; }
  sleep 600
done
