# 작업 큐 (review_next 이후; 갱신할 때마다 맨 위 시각을 바꾼다)

갱신 2026-09-29 17:40 CDT (Opus 5.5). 사용자 지시 2026-09-29 CDT: "추천 순서로 계속, 남는 자원에는 계속 작업 할당, 빈 곳도 계획에 올려 적절한 순서로". 모든 판정 실험은 사전 등록 → Fable 적대적 검토(서브에이전트) → 동결 → 실행 → §6 전사 → Fable 기록 감사 순서를 지킨다.

## 자원 배치 원칙
- CPU (192 워커, 수신기 BLER): 한 번에 한 실행. 순서 = 아래 표의 "CPU" 열.
- GPU (6 장, Exclusive_Process): 학습·GMM 적합. 빈 GPU 가 생기면 다음 GPU 작업을 바로 건다.

## 진행 중
| 작업 | 자원 | 상태 |
|---|---|---|
| 규모 확장 1단계 파일럿 (N=1e4, 개발 시행, D2·UMi28 × Nr 8/16/32) | CPU | tmux stage1 → stage1c6 (C6 재실행) |
| 시드 반복 학습 D3·SV8e·MIX3 a2/a3 | GPU 1–5 | tmux seeds3a, seeds3b (MIX3 a3 는 GPU 2 차례) |
| 2단계 준비: D2 C9 GMM 적합 N=1.6e5 (full ≤512, kron ≤1024) | GPU 0 (+빈 GPU) | tmux c9fits, 큐 `~/t2_wtS/conf/logs/c9fits_queue.txt` |
| SEEDS3 등록 | — | **동결 73a93547**; §5 는 학습 종료 뒤, BLER 은 1단계 CPU 종료 뒤 |
| STATIC16e4 | — | **완료·기록 faebac20** (D2 C2 (A), 문장 4/6, 예측 8/8); Fable 기록 감사 진행 중 |
| SBL 튜닝 (개발 NMSE, 6 데이터셋) | CPU 2 스레드 × 6 | tmux sparsetune (`~/t2_wtSBL`) |

## 대기열 (순서대로)
| # | 작업 | 자원 | 선행 조건 | 비고 |
|---|---|---|---|---|
| 1 | ~~STATIC-ALL~~ → **완료** (STATIC16e4, faebac20) | | | |
| 2 | **SEEDS3** BLER (6 태그) | CPU ≈ 6–9 h | 학습 종료 → §5 → 동결; 1단계 CPU 종료 | |
| 3 | 1단계 결과 정리 → **사용자: 2단계 진행 여부·kron K 상한·수신기 비용안** | — | 1단계 종료 | |
| 3b | **HISNR 고SNR 보강** (보고 전용): D2 C2·C6 의 +6..+15 dB, V1·b\*·genie·R2·R1 (+핵심), 점당 1만~2만 블록, **새 시행 2560 이후·별도 태그** (등록된 n 은 바꾸지 않음) → 고SNR 곡선 CI·오류 바닥 수치 | CPU 수 시간 | #2 CPU 종료 | 사용자 요청 09-29 ("2500 블록 적지 않나"); 짧은 등록(보고 전용 규칙) → 검토 → 실행 |
| 4 | **SBL/OMP 희소 baseline** (SBL-loop·SBL-pilot·OMP-pilot; 구현 중, 브랜치 sbl `~/t2_wtSBL`) 튜닝(개발 NMSE) → 등록 → 검토 → 동결 → BLER (정적 6 데이터셋) | CPU | #3b CPU 종료 | 빈 곳 2 |
| 5 | 2단계 GPU 준비 계속: UMi28 C6·C9 N=1.6e5 적합, V1 1.6e5 학습 (D2 C9, UMi28 C6·C9) | GPU (빈 것) | 시드 학습 종료 뒤 | K 상한 결정 전에는 kron ≤1024 까지만 |
| 6 | 2단계 등록 → 검토 → 동결 → BLER | CPU (큼) | #3 사용자 결정, #5 | |
| 7 | 기록 감사 (Fable): STATIC-ALL, SEEDS3, SBL | 서브에이전트 | 각 §6 | |
| 8 | RESULTS.md (ALD·DOP·ROT·ROTMIX·S2V·SUPP·SEEDS3·STATIC-ALL·SBL), CONTRIBUTIONS.md, conference/ + 그림 갱신, push | — | 각 감사 | |
| 9 | genie 고SNR 바닥 원인 확인 (실패 시행 채널 재생성, 조건수) | CPU 수 분 | CPU 틈 | 캡션용 |

## 사용자 결정 대기
1. (사용자가 직접 처리: 저장소 공개 여부 — 목록에서 제외)
2. 2단계 진행 여부 (#3 뒤), kron K 상한 (1024 / 4096), 수신기 비용안 (score ablation 제외 / V1 GPU 예외)
3. (결정됨 09-29 17:48 CDT: STATIC16e4 원고 명칭 = "규칙 고정 사후 계산")
4. 비정상 결과: 학회 논문에 강건성 절로 넣을지 / 저널판으로 아낄지
4. (선택) 불일치 20 조합 전부, A′ 시공간 prior, N 확대
