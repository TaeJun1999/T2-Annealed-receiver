# NEXT_EXPERIMENTS_PILOT16e4 — 파일럿 전용 학습 prior (Arvinte–Tamir 형 설정) 와 파일럿 전용 GMM (Koller 형 설정) 을 같은 가중치·같은 시행으로: 6 데이터셋 (사전 등록 v2)

- 작성: 2026-09-26 22:03 CDT (= 2026-09-27 12:03 KST) 초안 v1, Claude Code (Opus 5.5) → 적대적 검토 1건(Fable 5.1 서브에이전트; 반드시 5·권고 11; `prereg_reviews_2026-09-26/review_PILOT16e4.md`) 반영 v2 2026-09-26 22:28 CDT (Opus 5.5). 동결 시각 = 커밋 시각(`DECISIONS.md` 같은 줄). 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 틀: `NEXT_EXPERIMENTS_SEEDS16e4.md` §1 (같은 시행·다른 arm 의 수용 검사), `NEXT_EXPERIMENTS_{D3B16e4,SVB16e4,38901}.md` (UNGATED 측정 라벨), `08_SPEC_analysis.md` §2 표 B, review_next v3 §0.
- **작성 시점 공개**: 이 등록은 6 데이터셋의 루프 arm BLER 결과(헤드라인 B16e4k, C6 NR16B16e4, D3·SV8e·UMi28·MIX3 의 등록 결과; 표 B `b* → V1` 과 모든 기준선의 BLER@1·@16)를 **본 뒤**, 사용자의 "신경망 쪽 SOTA 와 대응" 질문과 "방식 1로 가자" 지시(구현 커밋 2b27ef6a 21:55 CDT 이전; 응답 시각 미기록)로 쓴다. 새 arm 두 개의 **반복 1 출력은 이미 관측된 루프 arm 의 반복 1 과 비트 동일**하다(구성상; §1): 즉 V1-pilot@1 = V1@1, bstar-pilot@1 = b\*@1 이고 이 값들은 §0 에 이미 보인다. 새로 관측되는 것은 새 arm 의 반복 2..16(채널 추정 고정, 검출만 반복)이다. 개발 시행(skip 6400..6439, C2 −3 dB 1 청크, `raw_PILdev`)에서 @1 동일성만 확인했고 그 raw 의 @16 은 판정 전에 보지 않았으며 지웠다(2b27ef6a). **@1 동일성의 개발 확인은 D2 C2 −3 dB 1 청크(S2)뿐**이고, C6(Nr=16)·S2c·SV8e·UMi28·MIX3 은 테스트 시행의 무결성 검사에서 처음 확인된다(C6·SV8e 는 n=2 스모크로 예외 없음만 확인, 수치 버림). `pair_cross.py` 의 자체 검사(v2 작성 중, 22:28 CDT 이전)는 이미 관측된 루프 arm 으로 만든 가짜 파일럿 raw 로 했다: `b* → V1` 을 P2 경로로 넣어 헤드라인 표 B(302:50·117:21·35:7, pooled 454:78, +1.41 [+1.22, +1.64], (i))를 재현했고, nmse 한 값을 바꾸면 라벨 없이 rc=1 로 끝남을 확인했다. 이때 **루프 arm 의 NMSE@1·@16 중앙값**(예: D2 C2 −3 dB V1@1 1.69e-01, b\*@1 2.34e-01, R0 3.18e-01)을 보았다 — 새 arm 의 NMSE 는 구성상 이 @1 값과 같다(보고 전용).
- 목적: 리뷰어 질문 "학습 prior 를 파일럿 채널 추정에만 한 번 쓰면(Arvinte & Tamir, IEEE TWC 2023 의 설정) 충분하지 않은가, 턴보 루프의 채널 재추정이 무엇을 더하는가" 와 "파일럿 전용에서도 학습 prior 가 GMM(Koller et al. 2022 의 GMM 추정기 설정)보다 나은가" 에 **같은 가중치·같은 적합·같은 테스트 시행**으로 답한다. 헤드라인과 기존 등록 판정은 어느 결과에서도 바뀌지 않는다.
- **원 방법의 재현이 아니다**: V1-pilot 은 Arvinte–Tamir 의 annealed Langevin 사후 표본추출이 아니라, V1 의 Module H(EP 등방 외부정보 + V1 디노이저의 사후평균·야코비안)를 파일럿에서 **한 번** 적용한 추정이다; 가중치·학습 데이터·예산은 V1 과 같다. bstar-pilot 은 Koller 의 정확한 GMM 조건부 평균 추정기가 아니라 b\* 의 반복 0 Module H(같은 EP 사이트)를 파일럿에서 한 번 적용한 것이다. 논문 문장은 "Arvinte–Tamir 형 **설정**(학습 prior 를 파일럿 전용으로 사용)" 으로 쓴다.

---

## 0. 출발점 (판정에 쓰지 않는다; 기존 raw 에서, −3 dB 실패 수 / 2560)

| 데이터셋 (base raw, cell, prior) | V1@1 (= V1-pilot@1) | V1@16 | b\*@1 (= bstar-pilot@1) | b\*@16 | R0-pilot@1 | R0-pilot@16 | genie@16 | 루프 표 B `b* → V1` |
|---|---|---|---|---|---|---|---|---|
| D2 C2 (`raw_B16e4k`, C2, S2) — 헤드라인 | 1469 | 371 | 1848 | 623 | 1918 | 1220 | 87 | (i) 3/3 |
| D2 C6 (`raw_NR16B16e4`, C6, S2) | 464 | 53 | 842 | 184 | 1005 | 376 | 22 | (i) 3/3 |
| D3 (`raw_D3B16e4`, C2, S2c) | 1972 | 1000 | 2135 | 1298 | 2164 | 1738 | 485 | (i) 3/3 |
| SV8e (`raw_SVB16e4`, C2, SV8e) | 1489 | 402 | 1527 | 464 | 1616 | 1010 | 31 | (iv) |
| UMi28 (`raw_U28B16e4`, C2, UMi28) | 2099 | 1228 | 2119 | 1270 | 2152 | 1781 | 594 | (i) 3/3 |
| MIX3 (`raw_MXB16e4`, C2, MIX3) | 2180 | 1354 | 2209 | 1421 | 2264 | 1896 | 679 | (i) 3/3, 보고 전용 |

R0-pilot = 같은 수신기의 파일럿 전용 **Gaussian** prior(표본 공분산) + 16 검출 반복(`arms.py` 의 기존 arm). R0-pilot@1 = R2@1 (구성상). 이 등록은 R0-pilot 옆에 같은 구조의 학습 prior·GMM 파일럿 전용 arm 을 놓는다.

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **새 arm (코드 2b27ef6a, `--pilot-arms`)** | **V1-pilot** = `route_a(..., PilotSitePrior(score_prior_v1, eps), mode="pilot_only", clip="eta", exact_prior=True)`: `PilotSitePrior.ep_site` 는 V1 의 반복 0 Module H 를 그대로(외부정보 평균 0·분산 cbar, 등방 외부정보, `denoise` + `denoise_full` 각 1 회 = 사후평균·야코비안, Hermitian-PSD 바닥) 파일럿 우도에 한 번 적용하고, 그 채널 사후를 고정한 채 검출·복호만 16 반복. **bstar-pilot** = `route_a(..., hp[b*].view("eta"), "gmm_site", mode="pilot_only")`: b\* 의 반복 0 사이트를 파일럿에 한 번, 이후 고정. 둘 다 반복 1 출력이 루프 arm(M-ours-dscore-C-V1, M-ours-bstar)의 반복 1 과 비트 동일해야 한다(`selftest_pilot.py`, 개발 시행에서 확인; 테스트 시행에서는 아래 무결성 검사) |
| **데이터셋·체크포인트·GMM (base 태그와 동일; 가중치·적합·시행 재사용)** | 아래 표 §1a. fits 는 링크 `results/gmm_fits_D2_<TAG> → gmm_fits_D2_<base>` (동결 커밋 전에 생성; 커밋되지 않는 `results/` 아래) |
| **실행 (명령 원문)** | `bash code/run_pilot16e4.sh` (6 데이터셋 순차). **6 개 전부 실행·보고한다.** 인자 부분집합(`D2C2 D2C6 D3 SV8e UMi28 MIX3` 중)은 중단된 데이터셋의 **재개에만** 쓰며(runner 는 완료 청크를 건너뜀; 모르는 이름이면 중단), 어떤 데이터셋도 결과를 본 뒤 빼지 않는다. §6 은 6 개 pair 파일(또는 무효 기록)이 모두 있을 때 쓴다. 스크립트 안: `export CUDA_VISIBLE_DEVICES=` (GPU 숨김; 38.901 은 필수, DECISIONS 80bae849), `conf/code`·`Demo` 가 커밋과 다르면 중단, fits 링크·ckpt sha 확인 후 `runner.py run --testbed D2 --prior <P> --cell <C> --n 2560 --chunk 40 --ntrain 160000 --stagec-ckpt <ckpt> --pilot-arms --arm V1-pilot bstar-pilot R5-genie --tag <TAG>` (로그 `logs/run_D2_<TAG>.log`) → `run_manifest.py --tag <TAG>` → `eval_accept.py` (`results/review_next/<TAG>_accept.txt`) → **수용 통과 시에만** `pair_cross.py` (`results/review_next/pair_<TAG>.txt`). `runner.py analysis` 는 돌리지 않는다(표 A 가 파일럿 raw 에 없는 R2-ours-G 를 요구해 죽는다; 검토 1). CPU complex128, 7 SNR −3..15, 테스트 시행 0..2559, chunk 40, 16 반복. 로그 `logs/run_pilot16e4.log`(+ `logs/queue.log`), 끝 표시 `PILOT_EVAL_DONE ok=<n> fail=<n>` (종료 코드 = fail 수) |
| **수용 검사 (데이터셋마다)** | (a) `eval_accept.py --prior <P> --tag <TAG>:<role>:<sha>:<C> --ntrain 160000 --bstar <b*> [--kron-K K] --ll-val <ll> --ref-raw <base raw>` → 청크 {(40k,40)} × 7, meta ntrain/bstar/kron_K/ll_val, ckpt id sha·role, iters 16, **R5-genie 가 base raw 와 모든 시행·반복에서 비트 동일** (출력 `results/review_next/<TAG>_accept.txt`). (b) `pair_cross.py` 무결성(수용 통과 뒤에만 실행): 점 집합 = base = 셀의 7 SNR, `load_raw` 경고 없음, genie 4 키(blk_err, ber, tauL_gmean, alphaD) 동일, **V1-pilot@1 = V1@1, bstar-pilot@1 = b\*@1** (blk_err, ber, nmse; 두 arm 모두 예외 없는 시행 전부), **채널 추정 고정**: 새 arm 의 `nmse[:, t] = nmse[:, 0]` (모든 반복, 예외 없는 시행). 실패하면 **라벨을 계산하기 전에** rc=1 로 끝난다. (a)·(b) 중 하나라도 실패하면 그 데이터셋은 **무효**(판정 없음, 원인 기록, 재실행은 사용자 승인). **예외 시행 규칙**: arm 이 예외를 던진 시행(`<arm>|failed`=1; runner 는 그 시행의 전 반복을 NaN 으로 저장)은 @1·고정 검사에서 빼고, 개수를 pair 파일 머리말에 보고하며, 표 B 에서는 블록 오류(01_RULES §4; `load_raw` NaN→1)로 유지한다 — 예외는 무효 사유가 아니다 |
| **비교 (표 B 규칙 그대로; 첫째 = 앵커 = 기준, `analysis.decision_points/paired` 재사용)** | **P1**: `V1-pilot → M-ours-dscore-C-V1` (파일럿 전용 V1 대 루프 V1; 앵커 V1-pilot). **P2**: `bstar-pilot → V1-pilot` (파일럿 전용 GMM 대 파일럿 전용 V1; 앵커 bstar-pilot). 보고 전용(라벨은 출력되지만 등록 판정이 아님): `bstar-pilot → M-ours-bstar`, `V1-pilot → M-ours-bstar` |
| **판정 층위** | D2 C2 (헤드라인 체크포인트, D1-sibling gate PASS; 파일 sha 4443921ce8d5c4a1 = raw_B16e4k 의 14 arm 을 현재 코드로 비트 재현한 파일, PILchk 2b27ef6a·PARB16e4chk) 의 P1·P2 = 이 등록의 **주 라벨**. 나머지 5 데이터셋(C6·D3·SV8e·UMi28·MIX3; UNGATED 체크포인트, MIX3 는 보고 전용 부속점) 의 P1·P2 = **측정 라벨**(arm 판정 아님). **다중성**: 주 라벨 2 개(P1, P2 @ D2 C2) 는 각각 표 B 규칙(판정점별 정확 부호검정 α=0.05, 2/3 규칙) 그대로이며 둘 사이 보정 없음(서로 다른 질문); 측정 라벨 10 개는 데이터셋별로 보고하고 **데이터셋 간 집계 주장은 개수 서술만**("6 중 k 에서 (i)") 한다. 배치 수준: 이 등록의 1차 검정 2 개, 측정 라벨 10 개, 보고 전용 pair 12 개(데이터셋당 2 개 × 6; 모두 pair 파일에 출력); 등록 사이 보정 없음(서로 다른 가설); 1차 검정 수는 원고에 공개한다 |
| 보고 전용 | 비교마다 SNR@0.1 격차(첫째 − 둘째, 90% paired bootstrap, `analysis.gain`, seed 20260925), 판정점 부호검정 a:b; −3 dB BLER@16 (R0-pilot, b\*, bstar-pilot, V1, V1-pilot, genie); SNR 별 채널 추정 NMSE@16 중앙값(R0-pilot, b\*, bstar-pilot, V1, V1-pilot; 파일럿 전용 arm 은 = @1, 인용 논문의 지표). F21 식 그림(파일럿 전용 3 종 + 루프 2 종 + genie)은 결과 뒤 보고 그림으로 만든다(판정 아님) |
| 비용 | CPU 만(수신기 BLER 은 CPU 규칙). 데이터셋당 3 arm × 448 청크, V1-pilot 의 Module H 는 시행당 1 회(디노이저 + 야코비안 각 1 회) → 데이터셋당 ≈ 10 분 이하 예상, 6 개 순차 ≈ 1 h. GPU·학습 없음 |

### 1a. 데이터셋 표 (모두 N′ = 1.6e5, n = 2560)

| 이름 | TAG | cell | prior | base raw | 체크포인트 (sha256[:16], role) | b\* (ll_val) |
|---|---|---|---|---|---|---|
| D2C2 | PILB16e4k | C2 | S2 | raw_B16e4k | `ckpt/d2sx_N160000_a1.pt` (4443921ce8d5c4a1, legacy-last) | kron 1024 (−11.459169831224418) |
| D2C6 | PILNR16 | C6 | S2 | raw_NR16B16e4 | `ckpt/d2sx_NR16_N160000_a1_fb2_best.pt` (c050d611b2c714a6, best) | kron 4096 (63.1751571838059) |
| D3 | PILD3 | C2 | S2c | raw_D3B16e4 | `ckpt/d2sx_S2c_N160000_a1_best.pt` (7ebf4e6647d4413f, best) | kron 4096 (0.08879931165293979) |
| SV8e | PILSV | C2 | SV8e | raw_SVB16e4 | `ckpt/d2sx_SV8e_N160000_a1_best.pt` (d2d78962c2846364, best) | full gmm256 (−47.80545576704972) |
| UMi28 | PILU28 | C2 | UMi28 | raw_U28B16e4 | `ckpt/d2sx_UMi28_N160000_a1_best.pt` (6f3a1b9490864af1, best) | kron 4096 (5.797910431000217) |
| MIX3 | PILMX | C2 | MIX3 | raw_MXB16e4 | `ckpt/d2sx_MIX3_N160000_a1_best.pt` (b591ae24ae3c5f31, best) | kron 4096 (33.7604873920761) |

체크포인트는 각 base 태그의 판정 가중치 그대로다(base raw 의 `meta|stagec_ckpt_id` 와 같은 sha; B16e4k 는 키가 없는 P0-1 이전 raw 이며 sha 는 헤드라인 기록에서). 새 체크포인트·새 적합·새 학습은 없다.

## 2. 라벨 (비교·데이터셋마다; UNDECIDED / 비유의는 "판정하지 못함" 이며 어느 쪽의 증거도 아니다)

| 표 B `X → Y` (앵커 X) | P1 (X = V1-pilot, Y = 루프 V1) | P2 (X = bstar-pilot, Y = V1-pilot) |
|---|---|---|
| (i) POWERED, second arm fewer ≥ 2/3 | "루프 V1 이 파일럿 전용 V1 보다 적게 실패" | "파일럿 전용에서 V1 이 b\* 보다 적게 실패" |
| (ii) POWERED, first arm fewer ≥ 2/3 | "파일럿 전용 V1 이 루프 V1 보다 적게 실패" | "파일럿 전용에서 b\* 가 V1 보다 적게 실패" |
| (iii) POWERED, 어느 쪽도 ≥ 2/3 아님 | "판정하지 못함 (유의 방향 없음)" | 같음 |
| (iv) UNDECIDED (판정점 < 3 또는 불일치 ≥ 6 인 판정점 < 2) | "판정하지 못함 (검정력 미달)" — 격자 확장 없음 | 같음 |
| 무효 (수용·무결성 실패) | 판정 없음, 원인 기록 | 같음 |

- **P1 의 해석 한계(미리 적음)**: 루프 V1 은 Module H 를 16 번, V1-pilot 은 1 번 적용한다. P1 (i) 는 "데이터 보조 채널 재추정의 몫" 과 "같은 파일럿 우도 위에서 prior 를 반복 적용한 몫(EP 정련)" 을 가르지 못한다. 문장은 "학습 prior 를 파일럿에서 **한 번** 쓰는 설정보다 루프가 …" 로만 쓰고, 파일럿 전용 EP 를 수렴까지 돌린 arm 은 이 등록에 없음을 한계로 적는다.
- 셀·예산·prior·가중치 한정 문장이다. "Arvinte–Tamir 보다 낫다" 는 문장은 쓰지 않는다(재현이 아님, §머리말); 쓰는 문장은 "같은 학습 prior 를 파일럿 전용으로 쓰는 설정보다 루프가 …" 형태다.

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; §0 을 본 뒤의 예측; 항목마다 적중/빗나감 이분)

1. **P1 D2 C2 = (i)** (루프 V1 이 적게 실패). 근거: 루프 V1 −3 dB 371 vs V1@1 1469; R0-pilot 의 1→16 반복 감소(1918→1220)가 루프 R2 보다 작다.
2. P1 측정 라벨: 나머지 5 데이터셋 **모두 (i)** → "6 중 6" (한 항목; 5/5 일 때만 적중).
3. **P2 D2 C2 = (i)** (파일럿 전용에서도 V1 이 적게 실패). 근거: @1 에서 1469 vs 1848.
4. P2 측정 라벨: C6·D3 (i); SV8e·UMi28·MIX3 은 **(i) 아님**((ii)/(iii)/(iv) 중 하나; −3 dB @1 실패율 차이가 0.8–1.5% 포인트로 작다: 38·20·29 / 2560). 5 개 각각 적중/빗나감.
5. 보고 `V1-pilot → M-ours-bstar` (파일럿 전용 V1 대 루프 b\*): D2 C2 에서 **(i)** (루프 b\* 가 적게 실패) — 확신 낮음.
6. D2 C2 −3 dB V1-pilot BLER@16 은 V1@16 (0.145) 과 V1@1 (0.574) 사이(열린 구간; pair 파일의 3 자리 값으로 판정).
7. 빗나갈 경로: (a) P1 이 (ii) → 루프의 이득 주장 철회, 그대로 기록; (b) 무결성 실패 → 무효·원인 기록(코드 결함이면 수정·재실행은 사용자 승인); (c) P2 가 (ii) → "파일럿 전용에서는 GMM 이 우세" 로 기록.

## 4. 선행 작업과 실행 현황 (갱신한다)

| 항목 | 상태 |
|---|---|
| 코드 `--pilot-arms` (arms.PilotSitePrior, runner), `selftest_pilot.py` | 커밋 2b27ef6a (PILchk: 기존 14 arm raw_B16e4k 와 비트 동일; PILdev: @1 동일) |
| `code/pair_cross.py`, `code/run_pilot16e4.sh` | 동결 커밋에 포함 |
| fits 링크 6 개 (`results/gmm_fits_D2_PIL*`) | 동결 시점에 존재(2026-09-27 11:58 KST 생성; 링크는 커밋 대상 아님, 선례 동일) |
| 적대적 검토 1건(Fable) → v2 → 동결 커밋 → BLER 6 데이터셋 → 수용·무결성 → §6 | v2 동결 92d26757; BLER ok=6 fail=0 (22:29–23:07 CDT); §6.1 기록 |

## 5. 평가 전 고정 기록

| 항목 | 값 |
|---|---|
| 동결 커밋 | [동결 커밋 해시는 DECISIONS 줄에] |
| 체크포인트 sha | §1a (실행 스크립트가 실행 직전 다시 확인) |

## 6. 결과 (이 절은 추가만 한다)

### 6.1 결과 (기록 2026-09-26 23:08 CDT, Opus 5.5 — 전사만, 해석 없음; 원본 `results/review_next/pair_PIL*.txt`, `PIL*_accept.txt`)

**실행·수용**: `bash code/run_pilot16e4.sh` 2026-09-26 22:29 ~ 23:07 CDT (tmux `pilot`, GPU 숨김, 192 워커; 시작 git 92d26757 = 동결). 데이터셋 순서 D2C2 (~22:31) → D2C6 (~22:39) → D3 (~22:44) → SV8e (~22:48) → UMi28 (~22:58) → MIX3 (~23:07). **PILOT_EVAL_DONE ok=6 fail=0**. 6 개 모두 **ACCEPT: OK** (청크 계획, meta ntrain/b\*/K/ll_val, ckpt sha·role, iters 16, R5-genie 가 base raw 와 비트 동일) 과 **pair_cross 무결성 OK** (점 집합, genie 동일, V1-pilot@1 = V1@1 · bstar-pilot@1 = b\*@1, 채널 추정 고정 nmse 불변), 예외 시행 0 건(두 arm, 6 데이터셋). pair 파일 머리말의 git 해시: D2C2 92d26757, 나머지 bfe80c48 — 실행 중 커밋된 bfe80c48 은 `SEEDS16e4` 문서만 바꿨고 `conf/code`·`Demo` 는 92d26757 과 동일(`git diff 92d26757 bfe80c48 --stat` = 문서 1 개). run_manifest 6 개(`results/review_next/run_manifest_PIL*.json`).

| 데이터셋 | P1 `V1-pilot → V1 루프` 판정점: a:b | P1 라벨 | P1 SNR@0.1 격차 (V1-pilot − V1) | P2 `bstar-pilot → V1-pilot` 판정점: a:b | P2 라벨 | P2 격차 (bstar-pilot − V1-pilot) |
|---|---|---|---|---|---|---|
| **D2 C2 (주)** | −3/0/+3: 280:25 · 57:17 · 10:9, pooled 347:51 | **(i)** POWERED, 2/3 | +0.92 [+0.77, +1.07] | −3/0/+3: 397:45 · 123:23 · 31:6, pooled 551:74 | **(i)** POWERED, 3/3 | +1.07 [+0.90, +1.25] |
| D2 C6 (측정) | −3/0: 38:8 · 5:5, pooled 43:13 | (iv) 판정점 2 | n/a (둘 다 ≤ −3 dB) | −3/0/+3: 174:17 · 56:3 · 32:5, pooled 262:25 | (i) 3/3 | n/a (둘 다 ≤ −3 dB) |
| D3 (측정) | 0/+3/+6: 160:18 · 65:16 · 22:6, pooled 247:40 | (i) 3/3 | +0.83 [+0.67, +1.01] | 0/+3/+6: 207:37 · 126:28 · 62:10, pooled 395:75 | (i) 3/3 | +1.28 [+0.99, +1.53] |
| SV8e (측정) | −3/0: 415:13 · 63:7, pooled 478:20 | (iv) 판정점 2 | +1.04 [+0.92, +1.17] | −3/0/+3: 124:56 · 29:14 · 5:3, pooled 158:73 | (i) 2/3 | +0.17 [+0.08, +0.25] |
| UMi28 (측정) | +3/+6/+9: 76:19 · 28:14 · 9:7, pooled 113:40 | (i) 2/3 | +0.37 [+0.18, +0.57] | +3/+6/+9: 67:37 · 65:30 · 39:13, pooled 171:80 | (i) 3/3 | +0.63 [+0.33, +0.86] |
| MIX3 (측정, 부속) | +3/+6/+9: 93:26 · 34:10 · 15:13, pooled 142:49 | (i) 2/3 | +0.57 [+0.40, +0.77] | +3/+6/+9: 92:46 · 72:23 · 47:9, pooled 211:78 | (i) 3/3 | +0.88 [+0.58, +1.12] |

a:b = 첫째 arm 만 실패 : 둘째 arm 만 실패 (BLER@16). 격차 = SNR@0.1(첫째) − SNR@0.1(둘째), 90% paired bootstrap.

- **주 라벨 (D2 C2)**: P1 **(i)** "루프 V1 이 파일럿 전용 V1 보다 적게 실패"; P2 **(i)** "파일럿 전용에서 V1 이 b\* 보다 적게 실패".
- **측정 라벨 개수**: P1 — 6 중 4 에서 (i) (D2 C2·D3·UMi28·MIX3), 2 에서 (iv) (C6·SV8e, 판정점 2 개). P2 — 6 중 6 에서 (i).
- P1 해석 한계(§2): 루프 V1 은 Module H 16 회, V1-pilot 은 1 회 — (i) 는 "한 번 쓰는 설정보다 루프가 적게 실패" 로만 읽는다.

보고 전용 (판정 아님):

| 데이터셋 | `bstar-pilot → b* 루프` 라벨 · 격차 | `V1-pilot → b* 루프` 판정점 a:b · 라벨 · 격차 (V1-pilot − b\*) |
|---|---|---|
| D2 C2 | (i) 2/3 · +0.57 [+0.41, +0.73] | 167:164 · 33:89 · 6:33 · **(ii)** 2/3 · −0.50 [−0.69, −0.32] |
| D2 C6 | (iii) · n/a | 24:125 · 5:46 · (iv) 판정점 2 · n/a |
| D3 | (i) 3/3 · +0.70 [+0.46, +0.90] | 90:130 · 40:88 · 15:46 · **(ii)** 3/3 · −0.58 [−0.82, −0.36] |
| SV8e | (i) 2/3 · +0.96 [+0.84, +1.09] | 386:46 · 57:15 · (iv) 판정점 2 · +0.79 [+0.67, +0.92] |
| UMi28 | (i) 2/3 · +0.41 [+0.16, +0.61] | 71:52 · 35:49 · 14:34 · (iii) · −0.22 [−0.49, +0.06] |
| MIX3 | (i) 2/3 · +0.47 [+0.20, +0.69] | 85:64 · 37:63 · 13:42 · **(ii)** 2/3 · −0.41 [−0.71, −0.12] |

(ii) 는 "첫째 arm(V1-pilot) 이 둘째(b\* 루프) 보다 적게 실패" 이다.

−3 dB BLER@16:

| 데이터셋 | R0-pilot | b\* 루프 | bstar-pilot | V1 루프 | V1-pilot | genie |
|---|---|---|---|---|---|---|
| D2 C2 | 0.477 | 0.243 | 0.382 | 0.145 | 0.245 | 0.034 |
| D2 C6 | 0.147 | 0.072 | 0.094 | 0.021 | 0.032 | 0.009 |
| D3 | 0.679 | 0.507 | 0.606 | 0.391 | 0.521 | 0.189 |
| SV8e | 0.395 | 0.181 | 0.341 | 0.157 | 0.314 | 0.012 |
| UMi28 | 0.696 | 0.496 | 0.638 | 0.480 | 0.616 | 0.232 |
| MIX3 | 0.741 | 0.555 | 0.670 | 0.529 | 0.648 | 0.265 |

채널 추정 NMSE@16 중앙값(보고, −3 dB; 파일럿 전용 arm 은 @1 과 같음): D2 C2 R0 3.18e-1, b\* 루프 9.79e-2, bstar-pilot 2.34e-1, V1 루프 5.47e-2, V1-pilot 1.69e-1; 나머지 SNR·데이터셋은 pair 파일.

**§3 예측 채점**: 1 (P1 D2 C2 (i)) ✓; 2 (P1 나머지 5 모두 (i), 한 항목) ✗ (C6·SV8e (iv)); 3 (P2 D2 C2 (i)) ✓; 4 (P2: C6 (i) ✓, D3 (i) ✓, SV8e "(i) 아님" ✗, UMi28 "(i) 아님" ✗, MIX3 "(i) 아님" ✗) = 2/5; 5 (보고 `V1-pilot → b* 루프` D2 C2 에서 (i) = 루프 b\* 가 적게 실패) ✗ — 결과 (ii); 6 (D2 C2 −3 dB V1-pilot BLER@16 ∈ (0.145, 0.574)) ✓ 0.245.

**감사 정정 (2026-09-27 02:14 CDT; 기록 감사 `prereg_audit_2026-09-27/audit_PILOT_SEEDS_MISMATCH.md`, Fable 5.1 서브에이전트 — 수치·라벨·예측 채점 변경 없음)**: (1) §1 판정 층위·§4 의 "PILchk: 14 arm raw_B16e4k 와 비트 동일" 은 판정 출력이 보존되지 않았다: `raw_PILchk` 는 개발 raw 와 함께 지웠고(머리말은 `raw_PILdev` 삭제만 적었다) accept/refarms 출력 파일이 없다; 남은 것은 `logs/run_D2_PILchk.log`(실행 사실)와 커밋 메시지 2b27ef6a. 보존된 대체 근거: 현재 코드(2e18e44a ⊃ 2b27ef6a)로 같은 1 청크를 다시 돌린 `RGB16e4chk` — 14 arm × KEYS_RAW @1..16 모두 raw_B16e4k 와 비트 동일(`results/review_next/RGB16e4chk_accept.txt` "ACCEPT: OK"). 이 등록의 판정 자체는 테스트 시행의 무결성 검사(genie 동일, @1 동일, 채널 추정 고정)에 기대며 PILchk 에 기대지 않는다. (2) §6.1 의 (iv) 칸 문자열: C6·SV8e 의 P1 (iv) 는 §2 원문대로 **"판정하지 못함 (검정력 미달)"** (판정점 2 개; 격자 확장 없음); 보고 `V1-pilot → b* 루프` 의 C6·SV8e (iv) 도 같다. (3) 예측 2 채점 ✗ 는 항목 규칙("5/5 일 때만 적중")대로이며, 두 (iv) 는 어느 쪽의 방향 증거도 아니다.
