#!/bin/bash
# Build / refresh the slim `paper` branch for the web chat (user decision 2026-10-05 CDT: "web 에서는 paper branch 만").
# It holds only paper-writing material (no raw data, no .npz, no code beyond the paper figure scripts), built from the
# main working tree through a temporary index, so main's index, working tree and history are untouched.  Each run adds
# one commit on top of the previous `paper` commit (orphan history, independent of main).
#   bash conference/tools/sync_paper_branch.sh [--no-push]
set -euo pipefail
cd /home/HTJ/t2
SP=/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad
mkdir -p "$SP"
PATHS=(conference docs/RESULTS.md docs/EXPERIMENTS.md docs/paper conf/conference_plot conf/DECISIONS.md)
mapfile -t REGS < <(ls conf/results/review_next/NEXT_EXPERIMENTS_*.md)
DIRTY=$(git status --porcelain -- "${PATHS[@]}" "${REGS[@]}" | wc -l)   # uncommitted paper files shipped from the working tree
export GIT_INDEX_FILE="$SP/paper_branch.index"
git read-tree --empty
git add -f -- "${PATHS[@]}" "${REGS[@]}"
{ git ls-files --cached | grep -E '\.(npz|pt|ckpt)$|__pycache__' || true; } | xargs -r git rm -q --cached --   # never ship data
cat > "$SP/paper_branch_README.md" <<EOF
# paper — IEEE ICC 2027 원고 자료 (웹 작성용)

main 의 원고 관련 파일만 모은 가벼운 브랜치다 (raw 데이터·.npz·실험 코드 없음). main $(git rev-parse --short HEAD) 에서
$(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') 에 만들었다 (\`conference/tools/sync_paper_branch.sh\`). 원본은 main 이다.$([ "$DIRTY" -gt 0 ] && echo " 단 main 에 아직 커밋하지 않은 작업 트리 파일 $DIRTY 개가 들어 있다 (NSCALE eval 중에는 main 커밋 금지 — 끝난 뒤 커밋).")

먼저 읽을 것: \`conference/PAPER_PLAN.md\` → \`conference/README.md\` → \`conference/figures/README.md\` (논문 그림·캡션 메모)
→ \`conference/figures/TERMS.md\` (그림·본문 용어) → \`docs/RESULTS.md\` → \`docs/paper/CONTRIBUTIONS.md\`.
논문 표 초안은 \`conference/tables/\` (상태는 그 README), 논문 그림은 \`conference/figures/F*.pdf|png\`, 기록판 그림과 수치·캡션 메모 \`.txt\` 는 \`conf/conference_plot/\`,
사전 등록 문서는 \`conf/results/review_next/NEXT_EXPERIMENTS_*.md\`.
EOF
git update-index --add --cacheinfo "100644,$(git hash-object -w "$SP/paper_branch_README.md"),README.md"
tree=$(git write-tree)
unset GIT_INDEX_FILE
parent=$(git rev-parse -q --verify refs/heads/paper || true)
msg="paper: 원고 자료 동기화 — main $(git rev-parse --short HEAD)$([ "$DIRTY" -gt 0 ] && echo " + 미커밋 $DIRTY") ($(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z'))

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01CA4DKmTZ2qnP2kZBAu9q4b"
if [ -n "$parent" ] && [ "$(git rev-parse "$parent^{tree}")" = "$tree" ]; then echo "paper branch already up to date ($parent)"; exit 0; fi
commit=$(git commit-tree "$tree" ${parent:+-p "$parent"} -m "$msg")
git update-ref refs/heads/paper "$commit"
echo "paper -> $(git rev-parse --short "$commit"): $(git ls-tree -r -l "$commit" | awk '{s+=$4} END {printf "%d files, %.1f MB", NR, s/1e6}')"
[ "${1:-}" = "--no-push" ] || git push -q origin paper
