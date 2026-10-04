# 작업 큐 (review_next 이후; 갱신할 때마다 맨 위 시각을 바꾼다)

갱신 2026-10-04 17:38 CDT (Opus 5.5). 사용자 지시 2026-09-29 CDT: "추천 순서로 계속, 남는 자원에는 계속 작업 할당, 빈 곳도 계획에 올려 적절한 순서로"; 09-30 CDT: 규모 확장 2단계는 "차례가 오면 승인 없이" (DECISIONS 6b1de688). 모든 판정 실험은 사전 등록 → Fable 적대적 검토(서브에이전트) → 동결 → 실행 → §6 전사 → Fable 기록 감사.

## 자원 배치 원칙
- CPU (192 워커, 수신기 BLER): 한 번에 한 등록 실행. 순서 = 아래 대기열. 지금 비어 있음.
- GPU (6 장, Exclusive_Process): `~/t2_wtS/conf/code/gpu_sched.sh` (tmux gpusched) 한 곳에서 배정 — 큐 `~/t2_wtS/conf/logs/gpuq.txt` (`<prio> <kind> <label> <cmd>`; 학습 90 > 검사 60 > GMM 재시작 50; 병합은 후보 3 개 뒤 CPU), 로그 `logs/gpu_sched.log`. 격자 끝 규칙 `edge_rule.sh` (tmux edgerule) 가 이 큐에 넣는다. 일괄 EM 검사 PASS 셀의 4096 재시작에는 `logs/batched_prefix.sh` (tmux bprefix) 가 `FIT_KRON_BATCHED=1` 을 붙인다.
- **main 커밋 금지 구간**: main 에서 등록 BLER 이 도는 동안 (raw 의 run|git 이 한 커밋이어야 함). **main conf/code·Demo 변경 금지**: NSCALE 동결 2d50dab5 부터 NSCALE §5 까지 (eval 전제 `git diff <동결> <§5> -- conf/code Demo` 비어 있음) — 문서·기록 커밋은 됨. **scale 커밋 금지 구간**: SCALE16e4 §5 커밋부터 마지막 2단계 raw 까지.

## 진행 중
| 작업 | 자원 | 상태 |
|---|---|---|
| SEEDSNR16e4 배치 2 (배치 1 ok=47 fail=0; 실행 커밋 2 scale b53a8529 = NR32B16e4s3 fb2 + fb3 로그 열람 공개) | CPU (~/t2_wtS, tmux seedsnr, `--resume`) | chkS2 → NR32B16e4s3 (≈ 5 h). 끝나면 §6 전사 + Fable 기록 감사 (scale). scale→main 병합은 NSCALE_DONE 뒤 |
| NSCALE GPU (main 5571b5d4, `code/run_nscale_gpu.sh` → gpuq 84 작업) | GPU 6 | 일괄 검사 3 → V1 D2 6.4e5·1.28e6·C6 6.4e5, D1 형제 2, 격자 B64e4·B128e4·NR16B64e4, 보고 전용 K8B64e4. 로그 `logs/nscale/` |
| NSCALE 동결 **2d50dab5** (v7; Fable 7 회 + 동결 전 확인) | — | GB′ 감시 tmux `nsgbp` (`code/nscale_gbp_watch.sh`). GPU 산출물 최종 → `run_nscale.sh prep` → §5 + `nscale_s5.txt` → `links` → §5 커밋 (= 실행) → CPU BLER (SEEDSNR 뒤). **main conf/code 변경 금지 (동결 ~ §5 diff 검사)** → SEEDSNR 의 scale→main 병합은 NSCALE_DONE 뒤 |

## 대기열 (순서대로)
| # | 작업 | 자원 | 선행 조건 | 비고 |
|---|---|---|---|---|
| 4 | RESULTS.md: SEEDS3·HISNR·SPARSE·SCALE 반영, CONTRIBUTIONS.md (09-27 이전에 머묾), 결과 요약 artifact 페이지, 그림 | — | 사용자 요청 시 (규칙: 요청 때 갱신) | |

## 완료 (최근)
- STATIC16e4 (faebac20, 감사 34dbf03b) · genie 고SNR 바닥 진단 (d6f322fb) · 1단계 파일럿 (scale a798d878)
- SEEDS3_16e4 결과·감사 (15d4e1dc) · HISNR16e4 결과·감사 (이 커밋)
- SCALE16e4 등록 동결 (scale 16a9dff6; TMXa PASS, U28NR16g σ 재측정 비트 동일)
- SCALE16e4 2단계 실행 10-01 14:16 – 10-03 11:49 CDT ok=101 → 결과·감사 scale 8992254c → main 병합 29391104
- 시드 a2·a3 (세 새 셀, 등록 밖; NR32 a3 diverged → 시드 등록 시 §3d fb2)
- SPARSE16e4 동결 02dafa1c (sbl 병합) → 실행 09-30 19:04–20:22 CDT ok=6 → 결과·감사 e1a5eb79

## 사용자 결정 대기
1. (사용자가 직접 처리: 저장소 공개 여부 — 목록에서 제외)
2. 비정상 결과: 학회 논문에 강건성 절로 넣을지 / 저널판으로 아낄지
3. (선택) 불일치 20 조합 전부, A′ 시공간 prior, N 확대
