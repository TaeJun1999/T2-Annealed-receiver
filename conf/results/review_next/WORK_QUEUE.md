# 작업 큐 (review_next 이후; 갱신할 때마다 맨 위 시각을 바꾼다)

갱신 2026-10-06 15:46 CDT (Opus 5.5). **실험 단계 끝 — NSCALE 결과·감사·RESULTS §23 까지 main 에 기록 (7adcee92), scale → main 병합 (36cd150e); 이제 원고 (웹 채팅, paper 브랜치).** 사용자 지시 2026-09-29 CDT: "추천 순서로 계속, 남는 자원에는 계속 작업 할당, 빈 곳도 계획에 올려 적절한 순서로"; 09-30 CDT: 규모 확장 2단계는 "차례가 오면 승인 없이" (DECISIONS 6b1de688). 모든 판정 실험은 사전 등록 → Fable 적대적 검토(서브에이전트) → 동결 → 실행 → §6 전사 → Fable 기록 감사.

## 원고 목표 (사용자 10-05 CDT)
- **IEEE ICC 2027** (Washington DC). 공식 call 페이지 기준 투고 마감 **2026-10-16**, 통지 2027-01-15, 최종본 2027-02-19. 투고본 **6 쪽 (10 pt) 상한** — 넘으면 심사 없이 거절. 저널판 없음 (DECISIONS 3a64d0ae) → 6 쪽에 못 넣는 것은 arXiv 확장판.

## 자원 배치 원칙
- CPU (192 워커, 수신기 BLER): 한 번에 한 등록 실행. 순서 = 아래 대기열. 지금 비어 있음.
- GPU (6 장, Exclusive_Process): `~/t2_wtS/conf/code/gpu_sched.sh` (tmux gpusched) 한 곳에서 배정 — 큐 `~/t2_wtS/conf/logs/gpuq.txt` (`<prio> <kind> <label> <cmd>`; 학습 90 > 검사 60 > GMM 재시작 50; 병합은 후보 3 개 뒤 CPU), 로그 `logs/gpu_sched.log`. 격자 끝 규칙 `edge_rule.sh` (tmux edgerule) 가 이 큐에 넣는다. 일괄 EM 검사 PASS 셀의 4096 재시작에는 `logs/batched_prefix.sh` (tmux bprefix) 가 `FIT_KRON_BATCHED=1` 을 붙인다.
- **main 커밋 금지 구간**: main 에서 등록 BLER 이 도는 동안 (raw 의 run|git 이 한 커밋이어야 함). **main conf/code·Demo 변경 금지**: NSCALE 동결 2d50dab5 부터 NSCALE §5 까지 (eval 전제 `git diff <동결> <§5> -- conf/code Demo` 비어 있음) — 문서·기록 커밋은 됨. **scale 커밋 금지 구간**: SCALE16e4 §5 커밋부터 마지막 2단계 raw 까지.

## 진행 중
| 작업 | 자원 | 상태 |
|---|---|---|
| 원고 (IEEE ICC 2027, 마감 2026-10-16) — 웹 채팅에서 사용자가 작성, 자료는 paper 브랜치 (`conference/tools/sync_paper_branch.sh`) | — | 진행 중. 실험 큐·GPU 큐 비어 있음 |

## 대기열 (순서대로)
| # | 작업 | 자원 | 선행 조건 | 비고 |
|---|---|---|---|---|
| 4 | RESULTS.md: SEEDS3·HISNR·SPARSE·SCALE 반영, CONTRIBUTIONS.md (09-27 이전에 머묾), 결과 요약 artifact 페이지, 그림 | — | 사용자 요청 시 (규칙: 요청 때 갱신) | |

## 완료 (최근)
- NSCALE (2026-10-06 15:46 CDT 기록): §5 = 실행 커밋 68d4d353 → eval 10-06 08:11–15:06 CDT `NSCALE_DONE ok=89 fail=0` → §6.1 (생성기 s6_gen.py) + §6.2 Fable 감사 MUST 0 (c69222a5) → RESULTS §23 (7adcee92); 논문 F16 (b) 에 6.4e5·1.28e6 점 (35e9b293), 표 I 초안·F30top (46a7477d).
- SEEDSNR16e4 실행 (1 묶음 ok=47 → 실행 커밋 2 b53a8529 → 2 묶음 ok=51) → 결과·감사 scale c689a935 (6/6 표 B (i), 세 셀 '시드 강건 (3/3 (i))'; fb3 로그 열람 공개). **scale→main 병합 대기: NSCALE_DONE 뒤** (main conf/code 동결)
- STATIC16e4 (faebac20, 감사 34dbf03b) · genie 고SNR 바닥 진단 (d6f322fb) · 1단계 파일럿 (scale a798d878)
- SEEDS3_16e4 결과·감사 (15d4e1dc) · HISNR16e4 결과·감사 (이 커밋)
- SCALE16e4 등록 동결 (scale 16a9dff6; TMXa PASS, U28NR16g σ 재측정 비트 동일)
- SCALE16e4 2단계 실행 10-01 14:16 – 10-03 11:49 CDT ok=101 → 결과·감사 scale 8992254c → main 병합 29391104
- 시드 a2·a3 (세 새 셀, 등록 밖; NR32 a3 diverged → 시드 등록 시 §3d fb2)
- SPARSE16e4 동결 02dafa1c (sbl 병합) → 실행 09-30 19:04–20:22 CDT ok=6 → 결과·감사 e1a5eb79

## 사용자 결정 대기
1. (사용자가 직접 처리: 저장소 공개 여부 — 목록에서 제외)
2. (해결 10-05 CDT, 사용자: "저널까지 확장하는 건 무리 — paper 에 쓸 좋은 source·결과는 모두 conference 에") → 저널판 없음, 비정상 묶음 포함 학회 원고. DECISIONS 같은 날 줄
3. (선택) 불일치 20 조합 전부, A′ 시공간 prior, C9 N-스케일링 (SEEDSNR 끝남) — 저널판이 없으므로 하려면 학회 원고 일정 안에서

## 원고 결정 기록 (2026-10-06 15:50 CDT)
- GitHub 기본 브랜치 = `paper` (사용자가 바꿈).
- 원격 옛 `conference` 브랜치는 지우지 않는다 (사용자 "일단 지우지 마").
- F17: 그림은 그대로, 캡션에 가중치 종류를 밝힌다 (사용자 "캡션에 밝히는게 좋겠다").
- 표 I: "너무 큰 table은 안돼" → 본문용 `conference/tables/table1_small.tex` (단 높이 0.41); 큰 판 둘은 arXiv 확장판용.
