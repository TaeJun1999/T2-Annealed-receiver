# 작업 큐 (review_next 이후; 갱신할 때마다 맨 위 시각을 바꾼다)

갱신 2026-10-11 17:00 CDT (Opus 5.5). **Sionna RT 방 실험 둘 (PATH16e4 = SRP, ROOM16e4 = SRB) 실행·§6 끝 — 둘 다 b\* → V1 (i), baseline 16 개 전부 (i). 지금: FIGHSROOM16e4 (SRB 그림의 +6..+15 dB 점을 n = 20480 으로; 보고 전용) 실행 중 — `FIGHS_DONE` 까지 main 커밋 금지. DeepMIMO 는 사용자 결정으로 철회.** (이전 머리말: 2026-10-10 23:56 CDT (Opus 5.5). **DeepMIMO: 주 실행 DMC16e4 끝 (라벨 (i), 기록·감사 끝); baseline 확장 `NEXT_EXPERIMENTS_DMCBASE16e4.md` 는 PIL·SP 통과, ALD 단계만 GPU 대기 (GPU 6 장이 컨테이너 밖 프로세스로 점유; 비면 `bash code/run_dmc_base.sh d2sx_DMC_N160000_a1 65b26ddd4f6437f4 ff25622dfcb0c7d5 8c92ea491d654012` 재실행 → ALD → `pair_baselines` → §6 → Fable 기록 감사 → `conference/figures/paper_f21dmc.py`) — 사용자 결정 10-10 CDT "DeepMIMO 만"·"DeepMIMO 자체 생성기"·"기존 실험과 같은 사이즈".** 그 전 상태: 실험 단계 끝 — 원고 (웹 채팅, paper 브랜치); 마지막 실행 = SITE16e4 (10-08 23:08 ~ 23:09 CDT, 라벨 (iii), 기록·감사 끝). 사용자 지시 2026-09-29 CDT: "추천 순서로 계속, 남는 자원에는 계속 작업 할당, 빈 곳도 계획에 올려 적절한 순서로"; 09-30 CDT: 규모 확장 2단계는 "차례가 오면 승인 없이" (DECISIONS 6b1de688). 모든 판정 실험은 사전 등록 → Fable 적대적 검토(서브에이전트) → 동결 → 실행 → §6 전사 → Fable 기록 감사.)

## 원고 목표 (사용자 10-05 CDT)
- **IEEE ICC 2027** (Washington DC). 공식 call 페이지 기준 투고 마감 **2026-10-16**, 통지 2027-01-15, 최종본 2027-02-19. 투고본 **6 쪽 (10 pt) 상한** — 넘으면 심사 없이 거절. 저널판 없음 (DECISIONS 3a64d0ae) → 6 쪽에 못 넣는 것은 arXiv 확장판.

## 자원 배치 원칙
- CPU (192 워커, 수신기 BLER): 한 번에 한 등록 실행. 순서 = 아래 대기열. 지금 비어 있음. 컨테이너가 다시 만들어지면 (2026-10-06 20:38 CDT 에 한 번 — tmux·`/tmp`·세션 감시가 사라지고 홈은 남는다) 등록의 재개 절차로 잇는다 (예: `conf/logs/fighs_interrupt_20261006CDT/`).
- GPU (6 장, Exclusive_Process): `~/t2_wtS/conf/code/gpu_sched.sh` (tmux gpusched) 한 곳에서 배정 — 큐 `~/t2_wtS/conf/logs/gpuq.txt` (`<prio> <kind> <label> <cmd>`; 학습 90 > 검사 60 > GMM 재시작 50; 병합은 후보 3 개 뒤 CPU), 로그 `logs/gpu_sched.log`. 격자 끝 규칙 `edge_rule.sh` (tmux edgerule) 가 이 큐에 넣는다. 일괄 EM 검사 PASS 셀의 4096 재시작에는 `logs/batched_prefix.sh` (tmux bprefix) 가 `FIT_KRON_BATCHED=1` 을 붙인다.
- **main 커밋 금지 구간**: main 에서 등록 BLER 이 도는 동안 (raw 의 run|git 이 한 커밋이어야 함). **main conf/code·Demo 변경 금지**: NSCALE 동결 2d50dab5 부터 NSCALE §5 까지 (eval 전제 `git diff <동결> <§5> -- conf/code Demo` 비어 있음) — 문서·기록 커밋은 됨. **scale 커밋 금지 구간**: SCALE16e4 §5 커밋부터 마지막 2단계 raw 까지.

## 진행 중
| 작업 | 자원 | 상태 |
|---|---|---|
| **FIGHSROOM16e4** (Sionna RT 방 그림 = prior SRB 의 +6/+9/+12/+15 dB 점을 새 시행 10000..30479, n = 20480 으로; 세 행 FHSRBB16e4 · FHSPSRB · FHALDSRB; 보고 전용; `NEXT_EXPERIMENTS_FIGHSROOM16e4.md` v2 = 실행 커밋) — **사용자: "figure는 매끄러운 곡선이 나타나는게 좋아"** | CPU 192 (tmux `fighsroom`, `bash code/run_fighsroom16e4.sh`; 로그 `logs/run_fighsroom16e4.log`) + 빈 GPU 한 장 잠깐 (ALD 대조·추정) | 실행 중 (약 2 시간). **`FIGHS_DONE` 까지 main 커밋 금지** (HEAD 가 움직이면 스크립트가 중단). 끝나면: `cd ~/t2/conf && CUDA_VISIBLE_DEVICES= python -B ~/t2/conference/figures/paper_f21dmc.py SRB hs > ~/t2/conference/figures/records/paper_f21srbhs.txt` → `F21srbhs_col` → §6 → Fable 기록 감사 → 사용자에게 그림. 컨테이너가 다시 만들어져 중단되면 `bash code/run_fighsroom16e4.sh --resume` (등록 §1 의 재개 규칙) |
| **ROOM16e4 (SRB) 마무리** | — | §6 은 f183160d (감사 전). 남은 것 (모두 `FIGHS_DONE` 뒤 커밋): Fable 기록 감사 반영 (`prereg_audit_2026-10-11/audit_ROOM16e4.md`) → §6.8; GB′ 추가 줄 (median 0.6472, `logs/gbprime_SRBB16e4.log`; 수용 (e), 예측 8); 사후 진단 `SRBB16e4_highsnr_fail.txt` 공개 줄; `docs/EXPERIMENTS.md` 에 SRP · SRB 행 (주 실행 + baseline); paper 브랜치 동기화 |
| 시드 학습 (등록 밖, 학습만): SRP a2 → a3 | GPU 0 (tmux `seedsrp`; `logs/seeds_SRP_train.log`) | 진행 중. BLER 은 별도 등록 + 사용자 결정 뒤 |
| 원고 (IEEE ICC 2027, 마감 2026-10-16) — 웹 채팅에서 사용자가 작성, 자료는 paper 브랜치 (`conference/tools/sync_paper_branch.sh`) | — | 진행 중. 실험 큐·GPU 큐 비어 있음 |

## 대기열 (순서대로)
| # | 작업 | 자원 | 선행 조건 | 비고 |
|---|---|---|---|---|
| 4 | RESULTS.md: SEEDS3·HISNR·SPARSE·SCALE 반영, CONTRIBUTIONS.md (09-27 이전에 머묾), 결과 요약 artifact 페이지, 그림 | — | 사용자 요청 시 (규칙: 요청 때 갱신) | |

## 완료 (최근)
- **ROOM16e4 — SRB** (2026-10-11 17:00 CDT 기록): 동결 b737fd55 → §5 = 실행 커밋 9ad4caa0 → 주 실행 10-11 15:22–16:17 CDT (ACCEPT OK) 표 B `b* → V1` **(i)** 302:129, 판정점 −3/0/+3, SNR@0.1 격차 +0.32 dB; b\* = full 1024 (정상 수렴); baseline @7d524638 16:18–16:32 CDT 16 개 전부 (i) ("전부"·"멀어진다" 충족, X\* = b\*); §6 f183160d; GB′ median 0.6472; 그림 `F21srb_col` · `F33cdf_SRB_wide`. DMI (DeepMIMO 실내) 는 실행 전 철회. 감사·GB′ 줄은 위 "진행 중"
- **PATH16e4 — SRP** (2026-10-11 16:18 CDT 기록): 동결 45c4ae07 → §5 = 실행 커밋 99039ef5 → 주 실행 10-11 13:29–15:05 CDT (ACCEPT OK) 표 B `b* → V1` **(i)** 1044:97, 판정점 −3/0/+3, SNR@0.1 격차 +2.01 dB; baseline @9ad4caa0 15:06–15:21 CDT 16 개 전부 (i); §6·Fable 감사 (MUST 1 · SHOULD 3 · NIT 6 반영)·GB′ 0.5836 = 7d524638. **캐비엇: 이 풀의 GMM b\* 는 EM 이 무너져 선택된 씨앗 초기화** (잘 맞춘 GMM 이 아님). 그림 `F21srp_col` · `F33cdf_SRP_wide`
- **SRT16e4** (2026-10-11 06:59 CDT 기록): 동결 2e50f269 → §5 = 실행 커밋 28f38d55 → 주 실행 10-11 04:30–06:11 CDT (ACCEPT OK) 표 B `b* → V1` **(i)** 403:93, 판정점 +9/+12/+15; baseline @6cbf9a5e 06:13–06:27 CDT 16 개 중 (i) 14 · `V1-pilot` (iii) · `R4-llr` (iv) → §6 전사 2cb2dca6 + Fable 감사 MUST 0 → 그림 `F21srt_col` · `F33cdf_SRT_wide`, EXPERIMENTS 두 행. DeepMIMO (DMC16e4 · DMCBASE16e4) 도 같은 날 끝.
- SITE16e4 (2026-10-08 23:23 CDT 기록): 동결 = 실행 커밋 9c4b6fe7 → `run_site16e4.sh` 한 번 (10-08 23:08 CDT; 드리프트 검사 OK) → 표 B `V4 → V1` 라벨 (iii) "판정하지 못함 (유의 방향 없음)", −3 dB 56:33 p=0.019 · 0 dB 23:15 p=0.26 · +3 dB 6:14 p=0.12, pooled 85:62 p=0.069, SNR@0.1 격차 +0.14 dB [90% +0.06, +0.23] → §6.1 + §6.2 Fable 감사 (MUST 0 · SHOULD 1 · NIT 5 반영, 수치 정정 없음) → RESULTS §24·EXPERIMENTS·CONTRIBUTIONS §0 한 줄 (이 커밋). 원고 IV-F 의 §2 문장 반영은 원고 채팅 몫.
- FIGHS16e4 (2026-10-07 17:09 CDT 기록): 실행 커밋 331f6e57 → 10-06 19:30 CDT 시작, 20:38 CDT 컨테이너 재생성으로 중단, 21:15 CDT `--resume` → 10-07 16:12 CDT `FIGHS_DONE ok=24 fail=0` → §6.1 (생성기 `prereg_audit_2026-10-07/s6_gen.py`) + §6.2 Fable 감사 MUST 0 → 논문 그림 7 개 (F16 (a)·F17·F20 (b)·F21·F22·F24 (c)(d)·F31 (b)) 의 +6..+15 dB 점 = n 20480, 기록 `conference/figures/records/`, 캡션 메모 `conference/figures/README.md` 'FIGHS16e4 merge'.
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
4. (10-11 CDT) ray-traced 두 풀 (DeepMIMO · Sionna RT): NMSE CDF 그림 (`F33cdf_{DMC,SRT}_wide`) 을 원고에 넣을지·어느 SNR 을 보일지
5. (10-11 CDT) DMC·SRT 시드 강건성 BLER (시드 a2·a3 학습은 GPU 2 에서 진행 중) 을 등록·실행할지
6. (10-11 CDT) BLER 이 낮은 구성 (스트림 수를 줄이는 등) 을 ray-traced 풀에 새로 등록할지; DMC16e4 수용 (c) 문구 판단 (감사 N4)

## 원고 결정 기록 (2026-10-06 15:50 CDT)
- GitHub 기본 브랜치 = `paper` (사용자가 바꿈).
- 원격 옛 `conference` 브랜치는 지우지 않는다 (사용자 "일단 지우지 마").
- F17: 그림은 그대로, 캡션에 가중치 종류를 밝힌다 (사용자 "캡션에 밝히는게 좋겠다").
- 표 I: "너무 큰 table은 안돼" → 본문용 `conference/tables/table1_small.tex` (단 높이 0.41); 큰 판 둘은 arXiv 확장판용.
- (2026-10-07 18:16 CDT) paper 브랜치에 **실험 결과 기록 전부**를 싣는다 (사용자 "실험 결과들 모두 paper 이쪽으로 push하자"): `conference/tools/sync_paper_branch.sh` 가 원고 자료에 더해 main 이 추적하는 `conf/results/`·`conf/figs/` 의 결과 기록 1388 파일 (표·수용·매니페스트·감사·기록판 그림) 을 함께 올린다. 싣지 않는 것: raw 시행 데이터 (git 밖, 서버에만), 배열 데이터 (.npz 등 — main 에는 있음), 실험 코드, 로그.
