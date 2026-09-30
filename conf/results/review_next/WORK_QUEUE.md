# 작업 큐 (review_next 이후; 갱신할 때마다 맨 위 시각을 바꾼다)

갱신 2026-09-30 17:45 CDT (Opus 5.5). 사용자 지시 2026-09-29 CDT: "추천 순서로 계속, 남는 자원에는 계속 작업 할당, 빈 곳도 계획에 올려 적절한 순서로"; 09-30 CDT: 규모 확장 2단계는 "차례가 오면 승인 없이" (DECISIONS 6b1de688). 모든 판정 실험은 사전 등록 → Fable 적대적 검토(서브에이전트) → 동결 → 실행 → §6 전사 → Fable 기록 감사.

## 자원 배치 원칙
- CPU (192 워커, 수신기 BLER): 한 번에 한 등록 실행. 순서 = 아래 대기열.
- GPU (6 장, Exclusive_Process): `~/t2_wtS/conf/code/gpu_sched.sh` (tmux gpusched) 한 곳에서 배정 — 큐 `~/t2_wtS/conf/logs/gpuq.txt` (`<prio> <kind> <label> <cmd>`; 학습 90 > 검사 60 > GMM 재시작 50; 병합은 후보 3 개 뒤 CPU), 로그 `logs/gpu_sched.log`. 격자 끝 규칙 `edge_rule.sh` (tmux edgerule) 가 이 큐에 넣는다. 일괄 EM 검사 PASS 셀의 4096 재시작에는 `logs/batched_prefix.sh` (tmux bprefix) 가 `FIT_KRON_BATCHED=1` 을 붙인다.
- **main 커밋 금지 구간**: main 에서 등록 BLER 이 도는 동안 (raw 의 run|git 이 한 커밋이어야 함). **scale 커밋 금지 구간**: SCALE16e4 §5 커밋부터 마지막 2단계 raw 까지.

## 진행 중
| 작업 | 자원 | 상태 |
|---|---|---|
| 2단계 GMM 격자 (SCALE16e4, 동결 16a9dff6) | GPU 0–5 | D2 C9·UMi28 C9 kron 2048 재시작 실행 중; UMi28 C6 = kron 2048 격자 끝 → 4096 (일괄 경로) 큐. 세 셀 일괄 검사 모두 PASS. 세 셀 V1 1.6e5 학습 완료 (전부 patience, 발산 없음) |
| SPARSE16e4 등록 v2 → Fable 재검토 | 서브에이전트 | `~/t2_wtSBL`; S2 C6 튜닝 (tmux sparsetune) +15 dB 남음. 동결 = sbl → main 병합; C2 5 개 먼저, C6 는 `pick_S2_C6.json` 뒤 |

## 대기열 (순서대로)
| # | 작업 | 자원 | 선행 조건 | 비고 |
|---|---|---|---|---|
| 1 | **SPARSE16e4** BLER (정적 6 데이터셋, main 에서) | CPU | v2 검토 통과 → sbl → main 병합 = 동결 | C6 는 튜닝 선택 파일이 생긴 뒤 |
| 2 | **SCALE16e4** 2단계: 격자 확정 → GB′ 3 → `scale2_s5.txt` 초안 → ALD tune (GPU) → 링크 → §5 + 실행 커밋 → ALD estimate → CPU `run_scale2.sh` | GPU → CPU (큼) | 4096 적합 (셀당 3 재시작 + 병합) | 순서·규칙은 등록 §1·§4 |
| 3 | 기록 감사 (Fable): SPARSE, SCALE16e4 | 서브에이전트 | 각 §6 | STATIC·SEEDS3·HISNR 완료 |
| 4 | RESULTS.md: SEEDS3·HISNR·SPARSE·SCALE 반영, CONTRIBUTIONS.md (09-27 이전에 머묾), 결과 요약 artifact 페이지, 그림 | — | 사용자 요청 시 (규칙: 요청 때 갱신) | |
| 5 | scale·sbl → main 병합 (DECISIONS 양쪽 줄 보존) | — | 각 실행 끝 | |

## 완료 (최근)
- STATIC16e4 (faebac20, 감사 34dbf03b) · genie 고SNR 바닥 진단 (d6f322fb) · 1단계 파일럿 (scale a798d878)
- SEEDS3_16e4 결과·감사 (15d4e1dc) · HISNR16e4 결과·감사 (이 커밋)
- SCALE16e4 등록 동결 (scale 16a9dff6; TMXa PASS, U28NR16g σ 재측정 비트 동일)

## 사용자 결정 대기
1. (사용자가 직접 처리: 저장소 공개 여부 — 목록에서 제외)
2. 비정상 결과: 학회 논문에 강건성 절로 넣을지 / 저널판으로 아낄지
3. (선택) 불일치 20 조합 전부, A′ 시공간 prior, N 확대
