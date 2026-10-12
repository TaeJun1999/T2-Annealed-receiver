"""Read-only simulation for the pre-run review of NEXT_EXPERIMENTS_FIGHSDMI16e4 (draft v1): does ald_new's REUSE branch
(code/run_fighsdmi16e4.sh lines 141-145), which the new "# EARLY" line puts on the critical path of a FRESH run for the first
time, consume the here-string of the `while read ... done <<< "$ROWS"` loops?  The bash below is the script's row loops and
ald_new's reuse branch verbatim apart from log -> echo; the estimate file is an existing hisnr estimate of another prior
(ald_PILSRP_hisnr.npz, prov git c48ee796).  Nothing is written.  Output: review_FIGHSDMI16e4_stdin_sim.out
Run: cd ~/t2/conf && taskset -c 48-63 ~/miniforge3/envs/torch/bin/python -B <this file>"""
import subprocess

BASH = r'''
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
log () { echo "[sim] $*"; }
ROWS='FHDMIB16e4|C2|DMI|DMIB16e4|ck|sha|best|gmm1024|-|112.0|-|DMIB16e4|-||A B
FHSPDMI|C2|DMI|DMIB16e4|-|-|-|gmm1024|-|112.0|FHDMIB16e4|SPDMI|pick:sha||C D
FHALDDMI|C2|DMI|DMIB16e4|ck|sha|best|gmm1024|-|112.0|FHDMIB16e4|ALDDMI|-|--ald-file /home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr.npz|ALD-pilot R5-genie
FHEXTRA|C2|DMI|DMIB16e4|ck|sha|best|gmm1024|-|112.0|FHDMIB16e4|ALDDMI|-||row after the ALD row (must still be read)'
WANT="  "; sel () { [ "$WANT" = "  " ] || [[ "$WANT" == *" $1 "* ]]; }
ald_new () {
  local E T V G; E=$(grep -o '/[^ ]*_hisnr\.npz' <<< "$FL"); V=$(grep -o -e '--rotation [0-9.]*' <<< "$FL" | cut -d' ' -f2)
  T=$(basename $E .npz); T=${T#ald_}; T=${T%_hisnr}
  if [ -f $E ]; then
    [ "$($P -B -c "import json, numpy as np; print(json.loads(str(np.load('$E')['prov']))['git'])" 2>/dev/null)" = "$H" ] \
      && { log "$TAG ALD $T: reusing $E (prov git $H)"; return 0; } \
      || { log "$TAG ABORT: $E exists but its prov git is not $H (stale estimate)"; return 1; }
  fi
  log "would regen+estimate (not simulated)"; return 1; }
for H in c48ee796 deadbeef; do
  echo "--- H=$H: EARLY loop"; n=0
  while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do n=$((n+1)); sel $TAG || continue; [[ $FL == *--ald-file* ]] && { ald_new || log "$TAG early ALD estimate not made (phase R tries once more)"; }; done <<< "$ROWS"  # EARLY
  echo "rows read by the EARLY loop: $n (expected 4); globals at exit TAG=$TAG"
  echo "--- H=$H: phase-R-like loop"; n=0
  while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do
    n=$((n+1)); sel $TAG || continue
    [[ $FL == *--ald-file* ]] && { ald_new || { echo "  FAIL++ $TAG"; continue; }; }
    echo "  row body reached: $TAG"
  done <<< "$ROWS"
  echo "rows read: $n (expected 4)"
done
'''
print(subprocess.run(["bash", "-c", BASH], capture_output=True, text=True).stdout, end="")
