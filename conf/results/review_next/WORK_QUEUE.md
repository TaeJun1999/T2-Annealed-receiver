# 작업 큐 (review_next 이후; 갱신할 때마다 맨 위 시각을 바꾼다)

갱신 2026-10-01 14:18 CDT (Opus 5.5). 사용자 지시 2026-09-29 CDT: "추천 순서로 계속, 남는 자원에는 계속 작업 할당, 빈 곳도 계획에 올려 적절한 순서로"; 09-30 CDT: 규모 확장 2단계는 "차례가 오면 승인 없이" (DECISIONS 6b1de688). 모든 판정 실험은 사전 등록 → Fable 적대적 검토(서브에이전트) → 동결 → 실행 → §6 전사 → Fable 기록 감사.

## 자원 배치 원칙
- CPU (192 워커, 수신기 BLER): 한 번에 한 등록 실행. 순서 = 아래 대기열. 지금 SCALE16e4 2단계 실행 중.
- GPU (6 장, Exclusive_Process): `~/t2_wtS/conf/code/gpu_sched.sh` (tmux gpusched) 한 곳에서 배정 — 큐 `~/t2_wtS/conf/logs/gpuq.txt` (`<prio> <kind> <label> <cmd>`; 학습 90 > 검사 60 > GMM 재시작 50; 병합은 후보 3 개 뒤 CPU), 로그 `logs/gpu_sched.log`. 격자 끝 규칙 `edge_rule.sh` (tmux edgerule) 가 이 큐에 넣는다. 일괄 EM 검사 PASS 셀의 4096 재시작에는 `logs/batched_prefix.sh` (tmux bprefix) 가 `FIT_KRON_BATCHED=1` 을 붙인다.
- **main 커밋 금지 구간**: main 에서 등록 BLER 이 도는 동안 (raw 의 run|git 이 한 커밋이어야 함). **scale 커밋 금지 구간**: SCALE16e4 §5 커밋부터 마지막 2단계 raw 까지.

## 진행 중
| 작업 | 자원 | 상태 |
|---|---|---|
| **SCALE16e4 2단계 CPU BLER** (`~/t2_wtS/conf/code/run_scale2.sh`, tmux scale2) | CPU (C9 셀은 --worker-gb 8.0 메모리 가드) | 실행 커밋 scale b4433d3c (§5), 동결 16a9dff6; 10-01 14:16 CDT 시작, 로그 `~/t2_wtS/conf/logs/run_scale2.log` (끝 SCALE2_DONE); 추정 60–200 h. **실행 중 scale 커밋 금지** |
| 시드 a2·a3 (세 새 셀, 학습만) | — | 완료 (NR32 a3 = diverged @1240 → 시드 등록 시 §3d fb2); 등록 밖 |

## 대기열 (순서대로)
| # | 작업 | 자원 | 선행 조건 | 비고 |
|---|---|---|---|---|
| 2 | SCALE16e4 §6 전사 → Fable 기록 감사 → EXPERIMENTS·DECISIONS → scale → main 병합 | — | SCALE2_DONE | |
| 3 | 기록 감사 (Fable): SCALE16e4 | 서브에이전트 | §6 | STATIC·SEEDS3·HISNR·SPARSE 완료 |
| 4 | RESULTS.md: SEEDS3·HISNR·SPARSE·SCALE 반영, CONTRIBUTIONS.md (09-27 이전에 머묾), 결과 요약 artifact 페이지, 그림 | — | 사용자 요청 시 (규칙: 요청 때 갱신) | |
| 5 | scale → main 병합 (DECISIONS 양쪽 줄 보존; sbl 은 02dafa1c 로 병합됨) | — | 2단계 실행 끝 | |

## 완료 (최근)
- STATIC16e4 (faebac20, 감사 34dbf03b) · genie 고SNR 바닥 진단 (d6f322fb) · 1단계 파일럿 (scale a798d878)
- SEEDS3_16e4 결과·감사 (15d4e1dc) · HISNR16e4 결과·감사 (이 커밋)
- SCALE16e4 등록 동결 (scale 16a9dff6; TMXa PASS, U28NR16g σ 재측정 비트 동일)
- SPARSE16e4 동결 02dafa1c (sbl 병합) → 실행 09-30 19:04–20:22 CDT ok=6 → 결과·감사 e1a5eb79

## 사용자 결정 대기
1. (사용자가 직접 처리: 저장소 공개 여부 — 목록에서 제외)
2. 비정상 결과: 학회 논문에 강건성 절로 넣을지 / 저널판으로 아낄지
3. (선택) 불일치 20 조합 전부, A′ 시공간 prior, N 확대
