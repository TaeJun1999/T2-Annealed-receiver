#!/bin/bash
# review_next overnight chain (user authorisation 2026-09-28 ~00:3x CDT: "나 잘거니까 그냥 진행해. 내가 허가한거로 하고"; token-light).
# Lives OUTSIDE conf/code.  Steps (any unmet condition -> "CHAIN_STOP <reason>" and exit; no retries):
#  1. wait for ROT16e4 to end; require all 12 pair_ROT files with a "pair_rot rc=0" line each and no INVALID/ABORT after the
#     resume line.  ROT §6 transcription is NOT done here (morning, needs the assistant).
#  2. commit ROT outputs + the session's untracked records in main (no §6).
#  3. move main's untracked copies of files the branch c-rotmix tracks to ~/t2_merge_backup/ (identical or older copies), then
#     `git merge c-rotmix`; a conflict is resolved only for conf/DECISIONS.md (union: both sides' appended lines), else abort.
#  4. record `git diff 389e23f4 HEAD --stat -- conf/code Demo` (registrations §5; prerequisite-code commits are expected there).
#  5. run code/run_rotmix16e4.sh (B', ~2.2 h) then code/run_s2v16e4_eval.sh (C, ~9 h).  End marker CHAIN_DONE.
# Log ~/t2/conf/results/review_next/after_rot_chain.log
M=~/t2/conf; LOG=$M/results/review_next/after_rot_chain.log
log () { echo "[chain $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $LOG; }
stop () { log "CHAIN_STOP $*"; exit 1; }
R=$M/logs/run_rot16e4.log
log "waiting for ROT_EVAL_DONE after the resume re-run"
until sed -n '/resume re-run after reboot/,$p' $R | grep -q ROT_EVAL_DONE; do sleep 120; done
sed -n '/resume re-run after reboot/,$p' $R | grep -E "INVALID|ABORT" && stop "ROT INVALID/ABORT lines after the resume (user decision)"
n=0
for d in B16e4k NR16 D3 SV U28 MX; do for a in a b; do
  f=$M/results/review_next/pair_ROT$a$d.txt
  [ -s $f ] && head -1 $f | grep -q "integrity .*: OK" && n=$((n+1)) || log "missing/invalid: $(basename $f)"
done; done
[ $n -eq 12 ] || stop "ROT pair files OK = $n/12"
log "ROT done: 12/12 pair files with integrity OK"
cd ~/t2
git add conf/results/review_next/pair_ROT*.txt conf/results/review_next/ROT*_accept.txt conf/results/review_next/run_manifest_ROT*.json \
  conf/results/review_next/HANDOFF_2026-09-27b.md conf/results/review_next/HANDOFF_2026-09-27c.md conf/results/review_next/worktree_copy.log \
  conf/DECISIONS.md resume_after_reboot.sh copy_worktree_artifacts.sh after_rot_chain.sh 2>>$LOG
git -c core.pager=cat commit -q -m "conf: ROT16e4 실행 산출물 (pair 12·accept·manifest; ROT_EVAL_DONE) + 인수인계 b/c·재부팅 복구·복사·체인 스크립트·DECISIONS 미커밋 줄 — §6 전사는 아침 (야간 무인 체인, 사용자 허가)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_0146ChSXaTthtpCxFMDP6eGh" || stop "main commit of ROT outputs failed"
log "main commit $(git rev-parse --short HEAD)"
[ -n "$(git status --porcelain conf/code Demo)" ] && stop "main conf/code or Demo dirty before merge"
B=~/t2_merge_backup; mkdir -p $B
for f in $(git diff --name-only HEAD c-rotmix); do
  [ -e "$f" ] && [ -z "$(git ls-files -- "$f")" ] && { mkdir -p "$B/$(dirname $f)"; mv "$f" "$B/$f"; log "moved untracked main copy -> backup: $f"; }
done
if ! git merge --no-edit c-rotmix >>$LOG 2>&1; then
  CF=$(git diff --name-only --diff-filter=U)
  [ "$CF" = "conf/DECISIONS.md" ] || { git merge --abort; stop "merge conflict outside DECISIONS.md: $CF"; }
  git show :2:conf/DECISIONS.md > /tmp/claude-1005/-home-HTJ-t2/fd8fe397-0695-4b56-84e6-322007e2842e/scratchpad/dec_ours; git show :1:conf/DECISIONS.md > /tmp/claude-1005/-home-HTJ-t2/fd8fe397-0695-4b56-84e6-322007e2842e/scratchpad/dec_base
  git show :3:conf/DECISIONS.md > /tmp/claude-1005/-home-HTJ-t2/fd8fe397-0695-4b56-84e6-322007e2842e/scratchpad/dec_theirs
  git merge-file --union /tmp/claude-1005/-home-HTJ-t2/fd8fe397-0695-4b56-84e6-322007e2842e/scratchpad/dec_ours /tmp/claude-1005/-home-HTJ-t2/fd8fe397-0695-4b56-84e6-322007e2842e/scratchpad/dec_base /tmp/claude-1005/-home-HTJ-t2/fd8fe397-0695-4b56-84e6-322007e2842e/scratchpad/dec_theirs
  cp /tmp/claude-1005/-home-HTJ-t2/fd8fe397-0695-4b56-84e6-322007e2842e/scratchpad/dec_ours conf/DECISIONS.md && git add conf/DECISIONS.md
  git -c core.pager=cat commit -q --no-edit || stop "merge commit failed"
  log "DECISIONS.md conflict resolved by union (both sides' lines kept)"
fi
log "merge commit $(git rev-parse --short HEAD); diff 389e23f4..HEAD -- conf/code Demo: $(git diff 389e23f4 HEAD --stat -- conf/code Demo | tail -1)"
git diff 389e23f4 HEAD --stat -- conf/code Demo >> $LOG
[ -n "$(git status --porcelain conf/code Demo)" ] && stop "conf/code or Demo dirty after merge"
cd $M
log "B' start: code/run_rotmix16e4.sh"; bash code/run_rotmix16e4.sh; log "B' exit $? ($(grep ROTMIX_EVAL_DONE logs/run_rotmix16e4.log | tail -1 | cut -c1-80))"
log "C start: code/run_s2v16e4_eval.sh"; bash code/run_s2v16e4_eval.sh; log "C exit $? ($(grep S2V_EVAL_DONE logs/run_s2v16e4_eval.log | tail -1 | cut -c1-80))"
log "CHAIN_DONE"
