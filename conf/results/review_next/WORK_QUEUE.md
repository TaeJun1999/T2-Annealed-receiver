# 작업 큐 (review_next 이후; 갱신할 때마다 맨 위 시각을 바꾼다)

갱신 2026-09-29 23:06 CDT (Opus 5.5). 사용자 지시 2026-09-29 CDT: "추천 순서로 계속, 남는 자원에는 계속 작업 할당, 빈 곳도 계획에 올려 적절한 순서로". 모든 판정 실험은 사전 등록 → Fable 적대적 검토(서브에이전트) → 동결 → 실행 → §6 전사 → Fable 기록 감사 순서를 지킨다.

## 자원 배치 원칙
- CPU (192 워커, 수신기 BLER): 한 번에 한 실행. 순서 = 아래 표의 "CPU" 열.
- GPU (6 장, Exclusive_Process): 학습·GMM 적합. 빈 GPU 가 생기면 다음 GPU 작업을 바로 건다.

## 진행 중
| 작업 | 자원 | 상태 |
|---|---|---|
| 규모 확장 1단계 파일럿 (N=1e4, 개발 시행, D2·UMi28 × Nr 8/16/32) | CPU | S1D2C2·S1D2C9·S1U28C6 완료 → S1U28C9 → S1U28C2 → S1D2C6 재실행 (tmux stage1, stage1c6; 끝 STAGE1_C6_DONE) |
| **CPU 체인** | CPU (대기) | tmux cpuchain = `code/cpu_chain.sh`: STAGE1_C6_DONE → SEEDS3 BLER 6 태그 (`run_seeds3_eval.sh`) → HISNR (동결돼 있으면) |
| 2단계 준비 GPU 적합 | GPU 0–5 | D2 C9 1.6e5 (c9fits 큐, 거의 끝) → 범용 큐 `~/t2_wtS/conf/logs/fitq_queue.txt` (C9 K1024 병합, UMi28 C6·C9 1.6e5 적합); 빈 GPU 에 브리핑이 lane 추가 |
| SPARSE 재튜닝 v2b (MacKay, SNR 별; 검토 반드시 6 반영) | CPU 2 스레드 × 6 | tmux sparsetune (`~/t2_wtSBL`); 끝나면 등록 v2 → 동결 (sbl → main 병합) |
| HISNR16e4 | — | **동결 32444c91** (n = 20480 두 셀, ≈ 8.2 h, 사용자 결정); cpuchain 이 SEEDS3 뒤 자동 실행 |

**main 커밋 금지 구간**: SEEDS3·HISNR·SPARSE 의 BLER 실행 중 (raw 의 run|git 이 한 커밋이어야 함). 등록 동결 커밋은 실행 사이의 틈에만. 지금 main HEAD 는 이 커밋 — 1단계 종료부터 SEEDS3 (≈ 6–9 h) + HISNR (≈ 8.2 h) 동안 main 커밋 금지. SPARSE 동결 (sbl → main 병합) 은 HISNR 뒤 틈에.

## 대기열 (순서대로)
| # | 작업 | 자원 | 선행 조건 | 비고 |
|---|---|---|---|---|
| 1 | ~~STATIC-ALL~~ → **완료** (STATIC16e4, faebac20) | | | |
| 2 | **SEEDS3** BLER (6 태그) | CPU ≈ 6–9 h | 동결 73a93547·§5 dbe0bdb3 완료; 1단계 CPU 종료 → **cpuchain 이 자동 시작** | 끝나면 §6 → Fable 감사 → RESULTS |
| 3 | 1단계 결과 정리 → **사용자: 2단계 진행 여부·kron K 상한·수신기 비용안** | — | 1단계 종료 | |
| 3b | **HISNR 고SNR 보강** (보고 전용): D2 C2·C6, +6..+15 dB, V1·b\*·R2·R1·R3·genie, **시행 10000..30479 (n = 20480, 새 시행)**, 태그 HSB16e4k·HSNR16 | CPU ≈ 8.2 h | **동결 32444c91** | cpuchain 이 SEEDS3 뒤 자동 실행 |
| 4 | **SPARSE16e4** (SBL-loop·SBL-pilot·OMP-pilot; 브랜치 sbl `~/t2_wtSBL`): 검토 1 차 완료 (반드시 6) → 코드 반영 → 재튜닝 v2b 진행 → 등록 v2 → 재검토 → 동결 (sbl → main 병합) → BLER (정적 6, main 에서 실행) | CPU | #3b CPU 종료 | 빈 곳 2 |
| 5 | 2단계 GPU 준비: UMi28 C6·C9 1.6e5 적합 (fitq 큐, **진행**); V1 1.6e5 학습 (D2 C9, UMi28 C6·C9) 은 **보류** — C9 SNR 격자·σ 격자를 2단계 등록에서 정한 뒤 | GPU | #3 결정 (학습) | K 상한 결정 전에는 kron ≤1024 까지만 |
| 6 | 2단계 등록 → 검토 → 동결 → BLER | CPU (큼) | #3 사용자 결정, #5 | |
| 7 | 기록 감사 (Fable): ~~STATIC16e4~~ (완료 34dbf03b), SEEDS3, HISNR, SPARSE | 서브에이전트 | 각 §6 | |
| 8 | RESULTS.md: ALD·DOP·ROT·ROTMIX·S2V·SUPP·STATIC **반영 완료 cf289ebe** (§12–§17); 남은 것 SEEDS3·HISNR·SPARSE 반영, CONTRIBUTIONS.md (09-27 이전에 머묾), 결과 요약 artifact 페이지 갱신, 그림 | — | 각 감사 | |
| 9 | ~~genie 고SNR 바닥~~ → **완료** d6f322fb (L=3 랭크 부족 블록) | | | |

## 사용자 결정 대기
1. (사용자가 직접 처리: 저장소 공개 여부 — 목록에서 제외)
2. 2단계 진행 여부 (#3 뒤), kron K 상한 (1024 / 4096), 수신기 비용안 (score ablation 제외 / V1 GPU 예외)
3. (결정됨 09-29 17:48 CDT: STATIC16e4 원고 명칭 = "규칙 고정 사후 계산")
4. 비정상 결과: 학회 논문에 강건성 절로 넣을지 / 저널판으로 아낄지
5. (선택) 불일치 20 조합 전부, A′ 시공간 prior, N 확대
