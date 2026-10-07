#!/bin/bash
# Build / refresh the `paper` branch for the web chat (user decision 2026-10-05 CDT: "web 에서는 paper branch 만").
# It holds the paper-writing material and, since 2026-10-07 CDT (user: "실험 결과들 모두 paper 이쪽으로 push하자"), every result
# RECORD that main tracks under conf/results and conf/figs (tables, acceptance files, manifests, audits, figures of record).
# Never shipped: trial raws (not in git), array data (.npz/.npy/.pt/.ckpt/.db), experiment code beyond the paper figure
# scripts, logs.  Built from the main working tree through a temporary index, so main's index, working tree and history
# are untouched.  Each run adds one commit on top of the previous `paper` commit (orphan history, independent of main).
#   [CLAUDE_SESSION_URL=<url>] bash conference/tools/sync_paper_branch.sh [--no-push]
set -euo pipefail
cd /home/HTJ/t2
SP=$(mktemp -d)                                   # temporary index + README text (tiny; left in the temp dir)
PATHS=(conference docs/RESULTS.md docs/EXPERIMENTS.md docs/paper conf/conference_plot conf/DECISIONS.md)
mapfile -t REGS < <(ls conf/results/review_next/NEXT_EXPERIMENTS_*.md)
DATA='\.(npz|npy|pt|ckpt|db)$|__pycache__'        # never shipped
mapfile -t RES < <(git ls-files -- conf/results conf/figs | grep -v -E "$DATA" | while IFS= read -r f; do [ -e "$f" ] && echo "$f"; done)   # result records main tracks
DIRTY=$(git status --porcelain -- "${PATHS[@]}" "${REGS[@]}" "${RES[@]}" | wc -l)   # uncommitted files shipped from the working tree
export GIT_INDEX_FILE="$SP/paper_branch.index"
git read-tree --empty
git add -f -- "${PATHS[@]}" "${REGS[@]}" "${RES[@]}"
{ git ls-files --cached | grep -E "$DATA" || true; } | xargs -r git rm -q --cached --   # never ship data
cat > "$SP/paper_branch_README.md" <<EOF
# paper — IEEE ICC 2027 원고 자료 (웹 작성용)

main 의 원고 자료와 **모든 실험의 결과 기록**을 모은 브랜치다 (raw 시행 데이터·배열 데이터 .npz·실험 코드·로그는 없음 — 그것들은 main 과 서버에 있다). main $(git rev-parse --short HEAD) 에서
$(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') 에 만들었다 (\`conference/tools/sync_paper_branch.sh\`). 원본은 main 이다.$([ "$DIRTY" -gt 0 ] && echo " 단 main 에 아직 커밋하지 않은 작업 트리 파일 $DIRTY 개가 들어 있다 (등록 실행 중에는 main 커밋 금지 — 끝난 뒤 커밋).")

먼저 읽을 것: \`conference/PAPER_PLAN.md\` → \`conference/README.md\` → \`conference/figures/README.md\` (논문 그림·캡션 메모)
→ \`conference/figures/TERMS.md\` (그림·본문 용어) → \`docs/RESULTS.md\` → \`docs/paper/CONTRIBUTIONS.md\`.
논문 표 초안은 \`conference/tables/\` (상태는 그 README), 논문 그림은 \`conference/figures/F*.pdf|png\`, 기록판 그림과 수치·캡션 메모 \`.txt\` 는 \`conf/conference_plot/\`,
사전 등록 문서 (설계·규칙·§6 결과 전사·감사) 는 \`conf/results/review_next/NEXT_EXPERIMENTS_*.md\`.

실험 결과 기록 (main 이 추적하는 것 전부, ${#RES[@]} 파일): \`conf/results/\` — 표 \`tables_D2_<TAG>.txt\`, 수용 \`review_next/<TAG>_accept.txt\`, 매니페스트 \`review_next/run_manifest_<TAG>.json\`,
짝 비교·회수율·집계표 (\`review_next/pair*_*.txt\`, \`recovery_*.txt\`, \`hisnr_*.txt\`, \`fighs_*.txt\` 등), 기록 감사 \`review_next/prereg_audit_<날짜>/\`, 규모 확장 \`scale/\`·\`nscale/\`, 희소 baseline 튜닝 \`sparse/\`, ALD 튜닝 \`ald/\`;
기록판 그림 \`conf/figs/\`. 실험 한 줄 요약은 \`docs/EXPERIMENTS.md\`, 결정 기록은 \`conf/DECISIONS.md\`, 정리된 결과는 \`docs/RESULTS.md\`.
EOF
git update-index --add --cacheinfo "100644,$(git hash-object -w "$SP/paper_branch_README.md"),README.md"
tree=$(git write-tree)
unset GIT_INDEX_FILE
parent=$(git rev-parse -q --verify refs/heads/paper || true)
msg="paper: 원고 자료 동기화 — main $(git rev-parse --short HEAD)$([ "$DIRTY" -gt 0 ] && echo " + 미커밋 $DIRTY") ($(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z'))

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>${CLAUDE_SESSION_URL:+
Claude-Session: $CLAUDE_SESSION_URL}"
if [ -n "$parent" ] && [ "$(git rev-parse "$parent^{tree}")" = "$tree" ]; then echo "paper branch already up to date ($parent)"; exit 0; fi
commit=$(git commit-tree "$tree" ${parent:+-p "$parent"} -m "$msg")
git update-ref refs/heads/paper "$commit"
echo "paper -> $(git rev-parse --short "$commit"): $(git ls-tree -r -l "$commit" | awk '{s+=$4} END {printf "%d files, %.1f MB", NR, s/1e6}')"
[ "${1:-}" = "--no-push" ] || git push -q origin paper
