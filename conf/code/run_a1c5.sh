#!/bin/bash
# (review_next NEXT_EXPERIMENTS_A1C5 v2 §1, §5; frozen ad32f48b) A1-C5 evaluation, fully automatic after training:
#  1. wait for A1C5_TRAIN_DONE (run_a1c5_train.sh); refuse to run with uncommitted conf/code (provenance)
#  2. pair eligibility + identities of the 6 checkpoints -> DECISIONS.md + a1c5_ckpts.json, COMMITTED (pathspec, checked)
#     before any evaluation; stop if an a2/a3 pair is not eligible (H9 = 판정 불가(쌍 부족) unless the user approves
#     attempt 4 before evaluation).  A relaunch (수용 실패 절차) reuses the committed identities, never re-records them.
#  3. report-only GB' / eps_phi on FREE GPUs only (checked with nvidia-smi), background, every rc logged
#  4. BLER on the A1-C5 set (C5 -3 dB n=1280; C5 0 dB, C2 -3 dB n=640; skip 4480..), 6 tags, CPU receiver, 3 tags at a
#     time = 192 workers  5. manifests  6. pair_tags accept (plan, run params, role=best + registered/recorded sha,
#     b*/genie bit-identity + their failure counts)  7. H9 (--h9: a2, a3 at C5 -3 dB) + report-only rows.
main () {
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python
L=logs/review_next/run_a1c5.log
CK=/home/HTJ/t2/conf/ckpt_review_next
J=results/review_next/a1c5_ckpts.json
log () { echo "[a1c5eval $(TZ=America/Chicago date '+%H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
tag () { echo review_next_A1C5_$1_a$2; }
log "waiting for A1C5_TRAIN_DONE (git $(git rev-parse --short HEAD))"
until grep -q "A1C5_TRAIN_DONE" logs/review_next/run_a1c5_train.log; do sleep 60; done
if [ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code)" ]; then
  log "ABORT: conf/code has uncommitted changes -- commit the evaluation code first"; exit 1; fi
log "training done; code $(git rev-parse --short HEAD) clean"

# ---- 2. identities (once)
if git -C /home/HTJ/t2 ls-files --error-unmatch conf/$J >/dev/null 2>&1; then
  log "identities already committed ($J) -- relaunch: not re-recorded"
else
  $P code/a1c5_report.py ckpts >> $L 2>&1; rc=$?
  if [ $rc -ne 0 ] && [ $rc -ne 2 ]; then log "ABORT: a1c5_report.py ckpts crashed (rc $rc)"; exit 1; fi
  git -C /home/HTJ/t2 add conf/DECISIONS.md conf/$J || { log "ABORT: git add failed"; exit 1; }
  git -C /home/HTJ/t2 commit -q -m "conf: review_next A1-C5 체크포인트 자격·identity 기록 (평가 전; NEXT_EXPERIMENTS_A1C5 §1)

a1c5_report.py ckpts, rc=$rc (0 = a2·a3 쌍 모두 자격, 2 = 쌍 부족 -> 평가하지 않음).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01Gukr8JteRRih57DJvEXgKG" -- conf/DECISIONS.md conf/$J || { log "ABORT: identity commit failed"; exit 1; }
  git -C /home/HTJ/t2 diff --quiet HEAD -- conf/DECISIONS.md conf/$J || { log "ABORT: identities not in HEAD"; exit 1; }
  log "identities committed $(git rev-parse --short HEAD), rc=$rc"
  if [ $rc -eq 2 ]; then log "STOP: an a2/a3 pair is not eligible -> no evaluation (ask the user about attempt 4)"; exit 1; fi
fi
[ "$($P -c "import json; print(json.load(open('$J'))['h9_judgeable'])")" = "True" ] || { log "STOP: $J says H9 not judgeable"; exit 1; }
EXP=$($P -c "import json; d=json.load(open('$J')); print(' '.join(f'{t}={s}' for t, s in d['expect_ckpt'].items()))")
[ -n "$EXP" ] || { log "ABORT: empty --expect-ckpt"; exit 1; }

# ---- 3. report-only GPU metrics on free GPUs (a queue per free GPU)
FREE=($(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1}'))
log "free GPUs: ${FREE[*]:-none}"
gp=()
if [ ${#FREE[@]} -gt 0 ]; then
  JOBS=(); for k in 1 2 3; do for kind in aug ctrl; do JOBS+=("$kind $k"); done; done
  for gi in "${!FREE[@]}"; do g=${FREE[$gi]}
    ( for ji in "${!JOBS[@]}"; do [ $((ji % ${#FREE[@]})) -eq $gi ] || continue
        set -- ${JOBS[$ji]}; T=$(tag $1 $2); C_=$CK/$1_N160000_a$2_best.pt
        CUDA_VISIBLE_DEVICES=$g $P code/a1c5_report.py gbprime --tag $T --ckpt $C_ > logs/review_next/gbprime_$T.log 2>&1; r1=$?
        CUDA_VISIBLE_DEVICES=$g $P code/diag_p1_heldout.py --ckpt $C_ --out results/review_next/p1_heldout_$T --device cuda \
           > logs/review_next/p1_heldout_$T.log 2>&1; r2=$?
        echo "[a1c5eval $(TZ=America/Chicago date '+%H:%M %Z')] GPU report $T (GPU $g): gbprime rc=$r1, p1_heldout rc=$r2" >> $L
      done ) & gp+=($!)
  done
else
  log "GPU report-only metrics NOT RUN (no free GPU) -- recorded, judgement proceeds (§1)"
fi

# ---- 4. BLER, 3 tags at a time (3 x 64 = 192 workers)
COMMON="--testbed D2 --prior S2 --skip0 4480 --chunk 40 --ntrain 160000 --arm M-ours-dscore-C-V1 M-ours-bstar R5-genie"
bad=0
for kind in aug ctrl; do
  pids=()
  for k in 1 2 3; do
    T=$(tag $kind $k); ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_$T
    for pt in "C5 -3 1280" "C5 0 640" "C2 -3 640"; do set -- $pt
      CUDA_VISIBLE_DEVICES="" $P code/runner.py run $COMMON --cell $1 --snr $2 --n $3 \
         --stagec-ckpt $CK/${kind}_N160000_a${k}_best.pt --tag $T > logs/review_next/run_a1c5_${T}_$1_$2.log 2>&1 & pids+=($!)
    done
  done
  for p in "${pids[@]}"; do wait $p || bad=1; done
  log "BLER $kind a1..a3 done (bad=$bad)"
done
[ $bad = 0 ] || { log "ABORT: a runner call failed (수용 실패 절차: relaunch fills missing chunks)"; exit 1; }
for k in 1 2 3; do for kind in aug ctrl; do
  $P code/run_manifest.py --tag $(tag $kind $k) >> $L 2>&1 || { log "ABORT: manifest $(tag $kind $k) failed"; exit 1; }
done; done

# ---- 6. acceptance (A1C5 §1)
ALL="$(tag aug 1) $(tag ctrl 1) $(tag aug 2) $(tag ctrl 2) $(tag aug 3) $(tag ctrl 3)"
for pt in "C5 -3 0" "C2 -3"; do set -- $pt; c=$1; shift
  $P code/pair_tags.py accept --registry A1C5 --cell $c --snr "$@" --tags $ALL --expect-ckpt $EXP \
     --out A1C5_accept_$c --overwrite >> $L 2>&1 || { log "ABORT: acceptance FAILED at $c $* (A1C5 §1 수용 실패 절차)"; exit 1; }
done
log "acceptance OK"

# ---- 7. H9 (judging) + report-only rows, verbatim pair_tags outputs
V=M-ours-dscore-C-V1
m () { echo $(tag $1 $2):$V; }
$P code/pair_tags.py group --registry A1C5 --h9 --cell C5 --snr -3 --aug $(m aug 2) $(m aug 3) --ctrl $(m ctrl 2) $(m ctrl 3) \
   --expect-ckpt $EXP --out A1C5_H9_C5_m3 --overwrite >> $L 2>&1 || { log "ABORT: H9 failed"; exit 1; }
rep=0
for pt in "C5 -3 m3" "C5 0 0" "C2 -3 m3"; do set -- $pt; c=$1; s=$2; nm=${c}_$3
  if [ "$nm" != "C5_m3" ]; then
    $P code/pair_tags.py group --registry A1C5 --cell $c --snr $s --aug $(m aug 2) $(m aug 3) --ctrl $(m ctrl 2) $(m ctrl 3) \
       --expect-ckpt $EXP --out A1C5_rep_group2_$nm --overwrite >> $L 2>&1 || rep=1
  fi
  $P code/pair_tags.py group --registry A1C5 --cell $c --snr $s --aug $(m aug 1) $(m aug 2) $(m aug 3) \
     --ctrl $(m ctrl 1) $(m ctrl 2) $(m ctrl 3) --expect-ckpt $EXP --out A1C5_rep_group3_$nm --overwrite >> $L 2>&1 || rep=1
  for k in 1 2 3; do
    $P code/pair_tags.py pair --registry A1C5 --cell $c --snr $s --x $(m aug $k) --y $(m ctrl $k) --expect-ckpt $EXP \
       --out A1C5_rep_pair_a${k}_$nm --overwrite >> $L 2>&1 || rep=1
  done
done
log "H9 + report rows written (results/review_next/A1C5_*.txt), report-row failures: $rep"
for p in "${gp[@]}"; do wait $p; done
log "A1C5_EVAL_DONE"
}
main "$@"; exit
