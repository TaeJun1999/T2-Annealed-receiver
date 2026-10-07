#!/bin/bash
# FIGHS16e4 recovery after the container re-creation of 2026-10-06 20:38 CDT (old container 9000babdde68 -> 262d04c812cc; host NVIDIA
# driver 580.173.02 -> 580.178.04; same image build, glibc 2.39-0ubuntu8.7).  The run (commit 331f6e57) was cut after 3 accepted rows,
# row 4 (FHD3B16e4) had written no chunk.  NOT part of the registration -- it only adds a pre-resume environment check and then runs
# the REGISTERED resume (NEXT_EXPERIMENTS_FIGHS16e4 §1 '중단·재개'): bash code/run_fighs16e4.sh --resume.
#   1 backup  the artefacts the resume rewrites (control verdicts, ALD control estimates, accept / count / manifest of the 3 finished
#             rows, the two logs) -> logs/fighs_interrupt_20261006CDT/before/ (+ sha256), so before / after can be compared
#   2 envchk  every row's receiver-control command (= run_fighs16e4.sh ctl: test chunk 0, trials 0..39, +6/+9/+12/+15 dB; already
#             observed trials, no new information) recomputed in the NEW container under scratch tags ZZ<row>; every arm x
#             common.KEYS_RAW must be bit-identical to raw_FHC<row> (computed in the OLD container, itself = the original raws)
#   3 resume  only if 24/24 rows are identical; otherwise STOP (nothing resumed; the user decides)
# Usage: bash recover.sh [dry]   (dry = print the 24 envchk commands, change nothing).  Runs once.  Log recover.log (CDT).
cd /home/HTJ/t2/conf || exit 1
P=/home/HTJ/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
D=logs/fighs_interrupt_20261006CDT; RL=$D/recover.log; OUT=results/review_next; SNRS="6 9 12 15"; DRY=$1
log () { echo "[recover $(TZ=America/Chicago date '+%m-%d %H:%M:%S %Z')] $*" | tee -a $RL; }
stop () { log "STOP: $* -- nothing resumed"; exit 1; }
eval "$(sed -n "/^ROWS='/,/'\$/p" code/run_fighs16e4.sh)"
[ "$(wc -l <<< "$ROWS")" = 24 ] || { echo "could not read the 24 ROWS"; exit 1; }
rowargs () {  # = run_fighs16e4.sh args() + ctl's test-set ALD file (globals of the current row)
  local a="--testbed D2 --prior $PR --cell $CELL --chunk 40 --ntrain 160000"
  [ "$CK" = - ] || a="$a --stagec-ckpt /home/HTJ/t2/conf/$CK"
  [ "$PICK" = - ] || a="$a --sparse-file ${PICK%%:*}"
  echo "$a ${FL//_hisnr.npz/.npz}"; }
if [ "$DRY" = dry ]; then
  while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do
    echo "ZZ${TAG#FH} (fits $BF, vs raw_${TAG/FH/FHC}): runner.py run $(rowargs) --snr $SNRS --n 40 --arm $ARMS --tag ZZ${TAG#FH}"; done <<< "$ROWS"
  exit 0
fi
# ---------------------------------------------------------------- 0 guards
H=$(git rev-parse --short HEAD)
[ "$H" = 331f6e57 ] || stop "HEAD $H is not the run commit 331f6e57"
[ -z "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] || stop "conf/code or Demo dirty"
pgrep -f "[c]ode/runner[.]py" > /dev/null && stop "a runner is already running"
[ -z "$(ls -d raw_ZZ* results/gmm_fits_D2_ZZ* 2>/dev/null)" ] || stop "scratch raw_ZZ* / results/gmm_fits_D2_ZZ* already exist"
[ ! -e $D/before ] || stop "$D/before exists (this script runs once)"
grep -q "FIGHS_DONE" logs/run_fighs16e4.log && stop "the run log already has FIGHS_DONE"
log "start: host $(hostname), driver $(nvidia-smi --query-gpu=driver_version --format=csv,noheader | sort -u | tr '\n' ' '), $(ldd --version | head -1), git $H; run log ends: $(tail -1 logs/run_fighs16e4.log | cut -c1-48)"
# ---------------------------------------------------------------- 1 backup
mkdir -p $D/before $D/envchk
cp -p $OUT/FHC*_control.txt $OUT/FHC*_aldcontrol.txt $OUT/FH*_accept.txt $OUT/fighs_FH*.txt $OUT/run_manifest_FH*.json \
  results/ald/ald_FHCXAROTaB16e4k.npz results/ald/ald_FHCXAROTbB16e4k.npz logs/run_fighs16e4.log logs/fighs_tmux.out $D/before/ || stop "backup copy failed"
( cd $D/before && sha256sum * ) > $D/before.sha256
log "backup: $(ls $D/before | wc -l) files -> $D/before/ (sha256 in $D/before.sha256)"
# ---------------------------------------------------------------- 2 envchk (rows in parallel, as phase C)
log "envchk: recomputing the 24 receiver controls (test chunk 0 = trials 0..39 at $SNRS dB) under scratch tags ZZ<row>"
while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do
  Z=ZZ${TAG#FH}
  ln -s gmm_fits_D2_$BF results/gmm_fits_D2_$Z || stop "link results/gmm_fits_D2_$Z"
  echo "# recover envchk git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z'): runner.py run $(rowargs) --snr $SNRS --n 40 --arm $ARMS --tag $Z" > $D/envchk/run_$Z.log
  $P code/runner.py run $(rowargs) --snr $SNRS --n 40 --arm $ARMS --tag $Z >> $D/envchk/run_$Z.log 2>&1 < /dev/null &
done <<< "$ROWS"
wait
NOK=0
while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do
  Z=ZZ${TAG#FH}; C=${TAG/FH/FHC}
  $P - raw_$Z raw_$C 4 $ARMS > $D/envchk/cmp_$Z.txt 2>&1 <<'PY'
import glob, os, sys
sys.path.insert(0, "code")
import common as C, numpy as np
new, ref, nf, arms = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4:]
fs, bad, n, other = sorted(glob.glob(new + "/D2_*.npz")), [], 0, set()
for f in fs:
    g = os.path.join(ref, os.path.basename(f))
    if not os.path.exists(g):
        bad.append(f"{os.path.basename(f)}: not in {ref}"); continue
    with np.load(f) as z, np.load(g) as y:
        for a in arms:
            for k in (f"{a}|{q}" for q in C.KEYS_RAW):   # the registered control's comparison (run_fighs16e4.sh cmp_arms)
                n += 1
                if k not in z.files or k not in y.files or z[k].shape != y[k].shape or not np.array_equal(
                        np.nan_to_num(z[k], nan=1e300), np.nan_to_num(y[k], nan=1e300)):
                    bad.append(f"{os.path.basename(f)} {k}")
        for k in sorted(set(z.files) | set(y.files)):    # every other key: listed only (meta strings name the tag / fits link)
            try:
                d = k not in z.files or k not in y.files or z[k].shape != y[k].shape or not (
                    np.array_equal(z[k], y[k], equal_nan=True) if z[k].dtype.kind in "fc" else np.array_equal(z[k], y[k]))
            except Exception as e:
                d = True
            if d:
                other.add(k)
ok = len(fs) == nf and n > 0 and not bad
print(f"envchk {new} (new container) vs {ref} (old container): {len(fs)} chunk files (expected {nf}), arms {arms}, "
      f"{n} (chunk, arm, key) comparisons, {len(bad)} differ")
print("\n".join("  " + b for b in bad[:20]))
print(f"  keys differing anywhere in the files (information only): {sorted(other) or 'none'}")
print("ENVCHK: " + ("OK" if ok else "FAILED"))
PY
  grep -qx 'ENVCHK: OK' $D/envchk/cmp_$Z.txt && NOK=$((NOK+1)) || log "envchk $Z vs raw_$C: NOT identical ($D/envchk/cmp_$Z.txt)"
done <<< "$ROWS"
log "envchk done: $NOK/24 rows bit-identical to the old-container control raws"
[ $NOK = 24 ] || stop "environment check failed"
# ---------------------------------------------------------------- 3 the registered resume
log "resume: bash code/run_fighs16e4.sh --resume (output appended to logs/fighs_tmux.out)"
bash code/run_fighs16e4.sh --resume >> logs/fighs_tmux.out 2>&1; RC=$?
log "run_fighs16e4.sh --resume exited rc=$RC; run log ends: $(tail -1 logs/run_fighs16e4.log | cut -c1-60)"
