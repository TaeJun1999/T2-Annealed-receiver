# 작업 큐 (review_next 이후; 갱신할 때마다 맨 위 시각을 바꾼다)

갱신 2026-10-11 20:39 CDT (Opus 5.5). **지금: FIGHSX16e4 (SRB · SRP 그림의 +12 · +15 dB 점을 n = 81920 으로; 보고 전용; 약 8 시간) 실행 중 — `FIGHS_DONE` 까지 main 커밋 금지.** 끝난 것: FIGHSROOM16e4 (SRB, n = 20480; 감사 반영 aefbfc12) · FIGHSPATH16e4 (SRP, n = 20480; §6 aefbfc12, 기록 감사 전). GPU 0 · 2: SRB 시드 a2 · a3 학습 (등록 밖), GPU 1: 비워 둠 (ALD 단계용). 사용자 결정 대기: 원고에 쓸 Sionna 결과 (SRB / SRP), hs / hsx 그림 선택.

## 원고 목표 (사용자 10-05 CDT)
- **IEEE ICC 2027** (Washington DC). 공식 call 페이지 기준 투고 마감 **2026-10-16**, 통지 2027-01-15, 최종본 2027-02-19. 투고본 **6 쪽 (10 pt) 상한** — 넘으면 심사 없이 거절. 저널판 없음 (DECISIONS 3a64d0ae) → 6 쪽에 못 넣는 것은 arXiv 확장판.

## 자원 배치 원칙
- CPU (192 워커, 수신기 BLER): 한 번에 한 등록 실행. 순서 = 아래 대기열. 지금 비어 있음. 컨테이너가 다시 만들어지면 (2026-10-06 20:38 CDT 에 한 번 — tmux·`/tmp`·세션 감시가 사라지고 홈은 남는다) 등록의 재개 절차로 잇는다 (예: `conf/logs/fighs_interrupt_20261006CDT/`).
- GPU (6 장, Exclusive_Process): `~/t2_wtS/conf/code/gpu_sched.sh` (tmux gpusched) 한 곳에서 배정 — 큐 `~/t2_wtS/conf/logs/gpuq.txt` (`<prio> <kind> <label> <cmd>`; 학습 90 > 검사 60 > GMM 재시작 50; 병합은 후보 3 개 뒤 CPU), 로그 `logs/gpu_sched.log`. 격자 끝 규칙 `edge_rule.sh` (tmux edgerule) 가 이 큐에 넣는다. 일괄 EM 검사 PASS 셀의 4096 재시작에는 `logs/batched_prefix.sh` (tmux bprefix) 가 `FIT_KRON_BATCHED=1` 을 붙인다.
- **main 커밋 금지 구간**: main 에서 등록 BLER 이 도는 동안 (raw 의 run|git 이 한 커밋이어야 함). **main conf/code·Demo 변경 금지**: NSCALE 동결 2d50dab5 부터 NSCALE §5 까지 (eval 전제 `git diff <동결> <§5> -- conf/code Demo` 비어 있음) — 문서·기록 커밋은 됨. **scale 커밋 금지 구간**: SCALE16e4 §5 커밋부터 마지막 2단계 raw 까지.

## 진행 중
| 작업 | 자원 | 상태 |
|---|---|---|
| **FIGHSX16e4** (Sionna RT 방 그림 둘 = prior SRB · SRP 의 +12/+15 dB 점을 새 시행 10000..91919, n = 81920 으로; 여섯 행 FX{SRBB16e4,SPSRB,ALDSRB,SRPB16e4,SPSRP,ALDSRP}; 보고 전용; `NEXT_EXPERIMENTS_FIGHSX16e4.md` v2 = 실행 커밋) — **사용자: "15dB에서 왜 위로 튀지?" → "2번 해"** | CPU 192 (tmux `fighsx`, `bash code/run_fighsx16e4.sh`; 로그 `logs/run_fighsx16e4.log`) + GPU 1 (ALD 대조·추정; **비워 둘 것**) | 실행 중 (추정 약 8 시간; SRB 세 행 → SRP 세 행). **`FIGHS_DONE` 까지 main 커밋 금지.** 그림은 스크래치 도우미가 그린다 (tmux `fighsxfig`, 로그 `logs/fighsx_figs.log`): `F21srbhsx_col` (SRB 세 행 수용 뒤) · `F21srphsx_col` (`FIGHS_DONE` 뒤) — 도우미가 없으면 §1 의 명령 `cd ~/t2/conf && CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python -B ~/t2/conference/figures/paper_f21dmc.py <SRB\|SRP> hsx > ~/t2/conference/figures/records/paper_f21<srb\|srp>hsx.txt`. 끝나면: 그림을 사용자에게 → §6 (집계표 + `# split` 줄, 예측 8 개 채점) → Fable 기록 감사 (처음 20480 시행의 비트 동일 포함) → 커밋. 컨테이너가 다시 만들어져 중단되면 `bash code/run_fighsx16e4.sh --resume` (다른 커밋 전에만) |
| **FIGHSPATH16e4 기록 감사** (Fable; §6 = aefbfc12) | — | FIGHSX 실행과 나란히 가능(읽기 전용, CPU 3 스레드 이하); 반영은 FIGHSX 의 `FIGHS_DONE` 뒤 커밋. 그 뒤 paper 브랜치 동기화 |
| 시드 학습 (등록 밖, 학습만): SRB a2 · a3 | GPU 0 · 2 (tmux `seedsrb2` · `seedsrb3`; `logs/seeds_SRB_train.log`; 스크립트는 세션 스크래치 `srb_seeds.sh`) | 진행 중 (10-11 19:26 CDT ~). SRP a2 · a3 는 끝남 (`logs/seeds_SRP_train.log`). 시드 BLER 은 별도 등록 + 사용자 결정 뒤 |
| 원고 (IEEE ICC 2027, 마감 2026-10-16) — 웹 채팅에서 사용자가 작성, 자료는 paper 브랜치 (`conference/tools/sync_paper_branch.sh`) | — | 진행 중. 실험 큐·GPU 큐 비어 있음 |

## 대기열 (순서대로)
| # | 작업 | 자원 | 선행 조건 | 비고 |
|---|---|---|---|---|
| 4 | RESULTS.md: SEEDS3·HISNR·SPARSE·SCALE 반영, CONTRIBUTIONS.md (09-27 이전에 머묾), 결과 요약 artifact 페이지, 그림 | — | 사용자 요청 시 (규칙: 요청 때 갱신) | |

## 완료 (최근)
- **FIGHSPATH16e4** (2026-10-11 20:39 CDT 기록): 실행 커밋 c48ee796 → 10-11 18:34–20:36 CDT `FIGHS_DONE ok=3 fail=0` → §6 aefbfc12: V1 실패 수 / 20480 (+6/+9/+12/+15 dB) 45 / 7 / 0 / 0, b\* 202 / 33 / 3 / 1, genie 14 / 1 / 1 / 0; 그림 `F21srphs_col` (V1 은 +9 dB 에서 끝남); 예측 6 개 적중; 기록 감사 전. FIGHSROOM16e4 의 기록 감사 (수치 오류 0; MUST 1 = EXPERIMENTS 의 'eig 파일럿' → DFT) 반영도 같은 커밋
- **FIGHSROOM16e4** (2026-10-11 18:34 CDT 기록): 실행 커밋 193776a1 → 10-11 17:01–18:31 CDT `FIGHS_DONE ok=3 fail=0` → §6 ed265304: V1 실패 수 / 20480 (+6/+9/+12/+15 dB) 45 / 10 / 3 / 4, b\* 90 / 23 / 11 / 6, genie 17 / 5 / 1 / 1; 0 실패 점 없음; 그림 `F21srbhs_col`; 예측 5 개 적중. ROOM16e4 (SRB) 의 기록 감사 MUST 0 · SHOULD 2 · NIT 8 반영·GB′ 0.6472 도 같은 커밋
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
