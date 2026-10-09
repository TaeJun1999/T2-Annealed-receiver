# paper — IEEE ICC 2027 원고 자료 (웹 작성용)

main 의 원고 자료와 **모든 실험의 결과 기록**을 모은 브랜치다 (raw 시행 데이터·배열 데이터 .npz·실험 코드·로그는 없음 — 그것들은 main 과 서버에 있다). main 6135fb93 에서
2026-10-08 23:27 CDT 에 만들었다 (`conference/tools/sync_paper_branch.sh`). 원본은 main 이다.

먼저 읽을 것: `conference/PAPER_PLAN.md` → `conference/README.md` → `conference/figures/README.md` (논문 그림·캡션 메모)
→ `conference/figures/TERMS.md` (그림·본문 용어) → `docs/RESULTS.md` → `docs/paper/CONTRIBUTIONS.md`.
논문 표 초안은 `conference/tables/` (상태는 그 README), 논문 그림은 `conference/figures/F*.pdf|png`, 기록판 그림과 수치·캡션 메모 `.txt` 는 `conf/conference_plot/`,
사전 등록 문서 (설계·규칙·§6 결과 전사·감사) 는 `conf/results/review_next/NEXT_EXPERIMENTS_*.md`.

실험 결과 기록 (main 이 추적하는 것 전부, 1394 파일): `conf/results/` — 표 `tables_D2_<TAG>.txt`, 수용 `review_next/<TAG>_accept.txt`, 매니페스트 `review_next/run_manifest_<TAG>.json`,
짝 비교·회수율·집계표 (`review_next/pair*_*.txt`, `recovery_*.txt`, `hisnr_*.txt`, `fighs_*.txt` 등), 기록 감사 `review_next/prereg_audit_<날짜>/`, 규모 확장 `scale/`·`nscale/`, 희소 baseline 튜닝 `sparse/`, ALD 튜닝 `ald/`;
기록판 그림 `conf/figs/`. 실험 한 줄 요약은 `docs/EXPERIMENTS.md`, 결정 기록은 `conf/DECISIONS.md`, 정리된 결과는 `docs/RESULTS.md`.
