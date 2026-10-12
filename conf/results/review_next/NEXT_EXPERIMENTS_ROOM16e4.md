# NEXT_EXPERIMENTS_ROOM16e4 — 고정 기지국 한 곳·방(실내) ray-traced 풀 두 개의 수신기 BLER: **Sionna RT `box` (prior SRB) 와 DeepMIMO `i1_2p4` (prior DMI), 각각 주 실행 + 등록된 baseline 전부** (셀 C2, 동일예산 N′ = 1.6e5, 태그 SRBB16e4 / PILSRB / ALDSRB / SPSRB · DMIB16e4 / PILDMI / ALDDMI / SPDMI) — 사전 등록 v2

- 작성: 2026-10-11 11:10 CDT (= 10-12 01:10 KST), Claude Code (Opus 5.5), 초안 v1 (커밋 01f5a726) → 적대적 검토 1 건(Fable 5.1 서브에이전트, 2026-10-11 11:19 CDT 보고; `prereg_reviews_2026-10-11/review_ROOM16e4.md`, 검사 `room_pool_check.py` → `.out`: MUST 4 · SHOULD 8 · NIT 3 — 전부 반영, §4) → **v2 2026-10-11 11:22 CDT (= 10-12 01:22 KST)**. 동결 시각 = 동결 커밋 시각(`DECISIONS.md` 같은 줄). **결과 관측 전**: SRB·DMI 의 어떤 체크포인트·적합도 BLER 로 평가된 적이 없고, prior 에 의존하는 arm(V1·GMM·baseline)은 이 두 풀에서 한 번도 돌지 않았다(아래 "선택 경위" 의 Perfect CSI 선별은 prior 를 쓰지 않는 arm 하나뿐). 커밋 뒤에는 §1~§3 을 바꾸지 않는다; 바꿔야 하면 사용자 승인 + `DECISIONS.md`.
- 사용자 지시(2026-10-11 CDT, 이 세션; 원문): "Deepmimo랑 Sionna기 Rank 1이 안되도록 할 수 있어?" · "꼭 28GHz 로 해야해? 이정도면 당연히 los도 많도 rank 1도 많겠는데" · "그리고 기지국은 고정하고 위치를 비꿔서 채널을 수집하는게 좋을 거 같은데" · "Deepmimo, Sionna 모두 rank1이 적게 나오는 채널로 찾아봐" · "뭐가 됬던 rank 1 가장 낮은가로 해보자" · "기지국하나에 연속적으로 위치를 바꿔서 보는거 맞지?" · "모든 선택 기준은 bler가 낮게 나올거 같은 방향으로 해야해". 앞선 지시가 그대로 적용된다: 채널은 **라이브러리 자체 생성기**로; "기존 실험과 같은 사이즈로 해야해"; "우리 conference에 넣는 11개 그래프 모두 찍어야 해".
- 배경: 도시 ray-traced 풀 두 개(DeepMIMO 6 개 도시 `NEXT_EXPERIMENTS_DMC16e4.md`, Sionna RT 3 개 장면 `NEXT_EXPERIMENTS_SRT16e4.md`)는 둘 다 라벨 (i) 였지만 **모든 arm 의 BLER 이 높았다**(Perfect CSI 의 +15 dB BLER 0.239 · 0.499): 테스트 채널의 0.66 · 0.80 이 사실상 rank-1 이고 실패가 그 층에 몰린다(SRT16e4 §6.2 · §6.9). 사용자는 BLER 이 낮게 나오는 ray-traced 풀을 원한다.
- **한 문서에 두 prior 의 주 실행과 baseline 확장을 함께 등록한다.** 틀(새 판정 규칙 없음) = `NEXT_EXPERIMENTS_SRT16e4.md` v2 §1~§2 (= DMC16e4 · DMCBASE16e4 의 틀). 아래 §1 에 **다른 곳과 고정 값**을 적고, 긴 규칙 문장(라벨·수용 검사 (a)~(e)·회수율 CI·ΔR 세 갈래·포화 가드·X\*·R_X·"전부"/"멀어진다" 문장·§3d 사다리·격자 반복 규칙)은 SRT16e4 v2 의 문장을 prior SRB / DMI · 해당 태그로 읽는다. 두 prior 는 서로 독립이다: 라벨·수용·예측 채점을 prior 마다 따로 하고, 한쪽이 멈춰도 다른 쪽은 등록대로 간다.
- 목적: 고정 기지국 한 곳의 방 안 채널(다중경로가 풍부해 rank-1 이 드문 ray-traced 채널)에서 같은 파이프라인·같은 크기·같은 규칙으로 b\* 대 V1 과 등록된 baseline 전부를 잰다. 결과가 어느 쪽이든 보고한다. 헤드라인(C2 1.6e5 B16e4k)·D2·38.901·DeepMIMO 도시·Sionna RT 도시 기록은 어느 결과에서도 바뀌지 않는다.

**선택 경위(공개 — 이 풀들은 "BLER 수준이 낮게 나오도록" 채널 통계와 Perfect CSI 선별로 골랐다; 기록 `rank_probe_2026-10-11/`)**

1. **무엇을 보고 골랐나.** (a) 채널 통계: rank-1 비율(최대 특이값 에너지 비중 ≥ 0.95)·유효 랭크·LoS 비율. (b) **Perfect CSI 수신기 하나(R5-genie: 같은 EP 검출기 + BCJR, 참 H)의 BLER** (`genie_screen.py`): 후보 채널 묶음에서 뽑은 채널(풀 전체 또는 탐색 표본; **시행 스트림이 아닌 별도 rng** `[20261011, 후보 번호, snr + 100]`)로 2048–4096 블록. R5-genie 는 채널 prior·파일럿을 쓰지 않는다 — **V1·b\*·그 밖의 prior 의존 arm 은 어느 후보에서도 돌리지 않았고, 두 arm 의 비교는 본 적이 없다.** 이 선별 때문에 아래 §3 에서 Perfect CSI 의 BLER 수준은 예측이 아니라 "관측됨(채점 제외)" 이다.
2. **생성 설정으로는 안 됐다.** 고정 기지국 1 곳(Munich)에서 28 → 3.5 GHz 는 rank-1 을 줄이지 않았고(0.74 → 0.89), 굴절·회절을 켜도 0.91–0.94 였다(`srt_fixed_probe.py` 의 콘솔 출력 — 파일로 남기지 않은 로그 외 사실). DeepMIMO 의 3.5 GHz 도시판은 28 GHz 판과 통계가 같았다(Miami 기지국 셋 0.61 / 0.69 / 0.62 — 이것도 콘솔 출력뿐인 로그 외 사실; 파일에 남은 3.5 GHz 행은 `asu_campus_3p5` 와 `city_1_losangeles_3p5_s` 뿐). 도시 장면 셋의 기지국 위치 2,896 곳(쌍 400 개 이상인 1,929 곳 가운데)을 훑어도 기지국별 최저 0.26 (`rank_*.txt`; 높이 10 m, Munich 은 25 m · 5 m 도), DeepMIMO 의 28 GHz 도시 시나리오는 기지국별 최저 0.54 (Dallas 의 한 기지국), 실외 캠퍼스 `asu_campus_3p5` 는 0.46 (Perfect CSI 선별 −3 dB 0.528), Boston 0.77 (`dm_scan_summary.txt` · `genie_screen_deepmimo.txt`; 28 GHz 도시 14 곳 중 6 곳 — charlotte · indianapolis · sanfrancisco(16) · seattle · denver · oklahoma — 은 다운로드 한도(HTTP 429)로 받지 못해 재지 못했다).
3. **방(실내) 시나리오가 가장 낮았다.** Sionna RT 내장 `box` (10 × 10 × 5 m 빈 방, **벽 재질은 기본 제공 그대로 `box-mat`: 비유전율 1, 전도도 1e7 S/m = 금속**) 와 DeepMIMO 실내 `i1_2p4` (2.4 GHz, Wireless InSite, 반사 2 회, 기지국 위치 64 곳 × 단말 격자 2 개). 재질을 바꾼 `box` 는 유리 0.07 · 콘크리트 0.11 · 석고보드 0.51 · 목재 0.88 (rank-1 비율, 깊이 5; `srt_box_material.py` 의 콘솔 출력 — 로그 외 사실; 파일에 남은 값은 `genie_screen_final.txt` 의 유리 0.062 · 콘크리트 0.100). 실내 DeepMIMO 의 다른 후보: `i2_28b` 0.133, `i3_60` 기지국별 0.126–0.635 — **사용자에게 금속 벽임을 알렸고(10-11 CDT), 사용자 지시("bler가 낮게 나올거 같은 방향")에 따라 기본 제공 그대로 쓴다.**
4. **BLER 을 가장 낮추는 설정을 그대로 쓰지 않은 이유와 그 판단의 시간 순서(작성자 판단, 공개; 검토 M2).** SNR 격자는 다른 실험과 같은 −3 … 15 dB 로 고정이고(§1), 판정점은 앵커 b\* 의 BLER 이 [0.005, 0.9] 안인 SNR 3 개가 필요하다 — Perfect CSI BLER 이 너무 낮은 설정은 폭포가 격자 아래쪽 끝에 붙어 판정점이 3 개에 못 미칠 위험이 크다.
   - **(가) 10-11 10:25–10:29 CDT, 첫 선별** (`genie_screen_deepmimo.txt`, `genie_screen_sionna.txt`, `genie_screen_lowsnr.txt`). 이때의 Sionna 후보 묶음은 **링크별 정규화(경로 전력 합 = 1) 없이** 저장한 것이었다(`box_save.log` 의 `_norm` 없는 이름; 그 판의 `srt_box_save.py` 는 덮어써서 남아 있지 않다) — 풀 레시피보다 BLER 이 높게 나온다. 그때 세운 기준(= `srb_build.py` 머리말의 문장): **"Perfect CSI BLER 이 가장 낮되 Perfect CSI BLER(0 dB) ≥ D2 기준 채널의 값 0.011"**. 그 표에서 `box` 기본 재질 깊이 1 / 2 / 3 / 5 의 0 dB 값 0.037 / 0.006 / 0.000 / 0.000 → **깊이 1** (−3 dB 0.199; 유리 · 콘크리트 깊이 5 는 0.281 · 0.332). DeepMIMO `i1_2p4` 데이터셋 120 은 0 dB 0.019 로 이 기준을 넘는다(예외가 아니다); 이 풀은 그보다 앞서(10:20 CDT) "rank-1 비율 최저(0.023; 동률 셋 중 유효 랭크가 높은 것)" 로 만들었고, 선별에서 −3 dB BLER 이 최저권(같은 격자의 기지국 10 곳이 0.120–0.157, 이 데이터셋 0.122)임을 확인해 그대로 뒀다.
   - **(나) 10:31–10:44 CDT**, 깊이 1 로 SRB 풀을 만들었다(앞서 깊이 5 로 시작한 빌드는 출력 전에 멈춤).
   - **(다) 10:55–11:02 CDT, 풀과 정규화한 후보의 재선별** (`genie_screen_pools.txt` n = 2048, `genie_screen_final.txt` n = 4096; `srt_box_save.py` 를 링크별 정규화하도록 고친 판). 풀 자체: SRB −6 / −3 / 0 / +2 / +3 / +6 dB = 0.452 / 0.102 / 0.017 / 0.007 / 0.003 / 0.000 (n = 2048 판은 0 dB 0.010), DMI 0.546 / 0.127 / 0.019 / 0.003 / 0.002 / 0.000; 정규화한 `box` 깊이 2 · 5 는 0 dB 0.002 · 0.000, 유리 · 콘크리트 깊이 5 는 −3 dB 0.133 · 0.191. **(가) 의 기준으로 다시 봐도 선택은 같다**(깊이 1 의 0 dB 0.010–0.017 대 0.011; 깊이 2 이상은 미달).
   - **(라) 그 뒤 이 문서를 쓰면서** 같은 걱정을 더 날카롭게 적은 문장 — "Perfect CSI BLER(+2 dB) ≥ 0.005 (Perfect CSI 보다 1 dB 나쁜 arm 도 +3 dB 에서 판정 범위에 들도록; D2 기준 0.007)" — 은 **풀을 만든 뒤에 쓴 것이고 어떤 선택에도 쓰이지 않았다.** 이 잣대로는 SRB 0.007 (같은 설정의 다른 표본 0.004), **DMI 0.003 으로 아슬아슬하거나 미달**이다 → 두 풀 모두, 특히 DMI 는 판정점이 3 개에 못 미쳐 (iv) 가 될 위험을 안고 간다(§3 예측 2). 더 안전한 후보(`i1_2p4` 데이터셋 65: −3 dB 0.197 · +2 dB 0.014, `i2_28b`: 0.294 · 0.076; 유리 벽 `box`)는 BLER 이 더 높아 사용자 지시(낮은 BLER)에 따라 택하지 않았다.
   - 이 기준들은 결과를 보기 전에 작성자가 정한 휴리스틱이며 검정이 아니다.
5. **기지국 한 곳(사용자 지시).** Sionna: 장면 경계 상자에서 규칙으로 정한 한 점(x 20 % · y 30 % · z 80 % = (−3, −2, 4) m; 탐색 스크립트의 규칙 그대로, 다른 위치는 재지 않았다). DeepMIMO: 데이터셋 하나(기지국 1 곳 × 격자 1 개)는 위치가 70,801 개뿐이라 학습 160,000 에 못 미친다 → **같은 위치에서 단말 yaw 를 5 번 독립 추첨**해 354,005 쌍(도시 풀 342,597 과 같은 규모). 처음에는 기지국 5 곳을 쓰려 했으나 사용자 지시("기지국하나에…")로 바꿨다.
6. 어느 선택도 V1·b\* 의 BLER 을 보고 하지 않았다. **그러나 이 등록은 "도시 풀 두 개의 결과를 본 뒤, BLER 수준이 낮은 채널을 골라 다시 재는" 것이다** — 모집단은 "이 방·이 기지국 한 곳" 이며 다른 장소·다른 재질로의 일반화는 주장하지 않는다. 도시 풀 두 개의 기록은 그대로 남고, 무엇을 원고에 쓸지는 사용자가 정한다.

---

## 0. 출발점 (판정에 쓰지 않는다)

**풀** (BLER 없음; 빌드 시점의 코드 = git 36e0a264 + 미커밋 작업 트리 = 커밋 44d3ab5e 의 빌더, 빌드 뒤 그 파일들을 바꾸지 않았다):

| | SRB (Sionna RT 2.1 `box`) | DMI (DeepMIMO v4.0.5 `i1_2p4`) |
|---|---|---|
| 빌더 · 로그 | `code/srb_build.py build 8` (GPU 0, 10-11 10:31 → 10:44 CDT; `logs/srb_build.log`) | `code/dmi_build.py 8` (CPU, 10-11 10:20 → 10:21 CDT; `logs/dmi_build.log`) |
| 채널 | 28 GHz, `PathSolver` max_depth 1 (LoS + 정반사; 난반사·굴절·회절 off), samples_per_src 1e8, `PlanarArray` 1×8 / 1×4 등방성 V, `Paths.cfr` (반송파), 링크당 경로 7 개 | 2.4 GHz, `dm.load(max_paths=25)` + `compute_channels` (반송파, 등방성 반파장 ULA 8×1 / 4×1, BS yaw = 단말 격자 중심 방향 +88.2°), 링크당 평균 경로 11.06 개 |
| 기지국 · 단말 | BS 1 곳 (−3, −2, 4) m; 단말 345,600 위치 = 바닥 평면 [−4.5, 4.5]² 균등, 높이 1.5 m, yaw ~ U[−π, π) | BS 1 곳 (−20.89, 12.60, 5.00) m; 단말 격자 701 × 101 = 70,801 위치(1 cm 간격, 높이 1 m) × yaw 5 회 ~ U[−180°, 180°) |
| 쌍 = 학습 풀 + 검증 풀 + 테스트 풀 | 345,600 = 273,247 + 20,000 + 52,353 (테스트 0.1515) | 354,005 = 273,305 + 20,000 + 60,700 (테스트 0.1715) |
| block split | 1 m 타일 100 개 중 16 개가 테스트 | 위치 기준 0.5 m 타일 45 개 중 8 개가 테스트(한 위치의 yaw 5 개는 같은 쪽) |
| sha256[:16] `H.npy` / `split.npy` (`dmimo.POOL_SHA`) | ae1c023605d002b4 / 24c202836d56b34e | dec5e7a1ea1e4605 / f0f716718f1c15d1 |
| 보정 (학습 스트림 7, n = 160000) | P_RAW 1.0005289046575756, TRAIN_SHA 2544c37a719436e2 | P_RAW 0.0019453481377247777, TRAIN_SHA 3380177f4c38cf57 (DeepMIMO 의 전력 단위 상수; 도시 풀 DMC 도 0.00195) |

- SRB 의 배열 packing 은 `srt_build.py` 와 같은 방식(수신기를 배열로 넘김): `srb_build.py selfcheck` — 위치·방향 차 0, 소자 오프셋 차 9.3e-10 m, 유효 경로 마스크 동일, 채널 상대 오차 5.9e-07 (결정적 solver, 수신기 64 개; 세션 콘솔 출력 — 로그 외 사실, 재실행 명령은 같은 것). 처음에 깊이 5 로 시작한 빌드는 출력 파일을 쓰기 전에 멈췄다(`logs/srb_build.log`).

**testbed 검증** (`results/testbed_{SRB,DMI}.txt`, `code/testbed_dm.py`, BLER 없음):

| 검사 | SRB | DMI | (문맥) SRT / DMC |
|---|---|---|---|
| TDMa 정규화(검증 스트림 8, n = 20000) | 0.99984 (s.e. 0.00311) **PASS**; 블록 전력 CV 0.440 | 1.00422 (s.e. 0.00189) **PASS**; CV 0.266 | CV 0.354 / 0.396 |
| TDMc 풀 정체 | 345,600 쌍, 장면 box, BS 1 곳, LoS 1.000, 평균 경로 7.00 **PASS** | 354,005 = 70,801 × 5, 데이터셋 120, LoS 1.000, 평균 경로 11.06 **PASS** | LoS 0.848 / 0.281 |
| TDMd 파일럿 단계 K = 1 Gaussian NMSE @ −3 dB (보고) | 0.3134 | 0.2847 | 0.3191 / 0.3161 |
| TDMe T2b 파일럿 결정 / erank(C_ens) | erank(Rt) 3.991/4 ≥ 3.6 → **DFT 파일럿** / 25.95/32 | 3.839/4 → **DFT 파일럿** / 20.47/32 | 3.392 → eigen / 3.422 → eigen |
| TDMf block split | 서로소·전체, 양쪽에 걸친 타일 없음 **PASS** | **PASS** | PASS |
| TDMg split 이동(보고): outage P(MI < 4 bit) @ −3 dB 검증 / 테스트; K = 1 NMSE 검증 / 테스트 | 0.0231 / 0.0304; 0.3134 / 0.3371 | 0.0019 / 0.0018; 0.2847 / 0.2918 | 0.1399 / 0.1349 (SRT) |
| TDMh 누수(보고): 테스트 2000 표본의 최근접 학습 채널, 정규화 제곱거리 중앙값 · < 0.1 비율 | 0.3509 · **0.004** | 0.1789 · **0.058** | 0.0500 · 0.634 / 0.1261 · 0.433 |
| 종합 | **ALL PASS** | **ALL PASS** | |

- 채널 랭크(풀에서 직접): 풀 전체 rank-1 비율 SRB 0.026 / DMI 0.023, 평균 유효 랭크 1.84 / 1.64 (`genie_screen_pools.txt` 의 표본; SRT 0.808 · 1.12, DMC 0.677 · 1.23, D2 S2 0.013 · 2.20). **테스트 풀만**: rank-1 비율 SRB 0.033 / DMI 0.021, 비중 0.80–0.95 층 0.526 / 0.815, < 0.80 층 0.441 / 0.164 (검토의 재계산 `prereg_reviews_2026-10-11/room_pool_check.out`). 링크별 원시 전력 ‖H‖²/(NrNt) (보정 전): SRB 중앙값 0.912 · 최소 0.088 · 최대 3.88, DMI 중앙값 0.0019 (같은 파일).
- `results/testbed_{SRB,DMI}.txt` 는 동결 커밋의 `testbed_dm.py` 로 다시 만든 판이다(검토 S4: 문구 "no tile"·좌표 반올림만 다름, 수치 동일).
- **Perfect CSI 선별값**(R5-genie BLER@16, n = 4096, 별도 rng, 풀 전체에서 추출; `genie_screen_final.txt`): SRB −6 / −3 / 0 / +2 / +3 / +6 dB = 0.452 / 0.102 / 0.017 / 0.007 / 0.003 / 0.000; DMI 0.546 / 0.127 / 0.019 / 0.003 / 0.002 / 0.000; D2 S2 기준 0.199 / 0.042 / 0.011 / 0.007 / 0.008 / 0.003. (선별 도구의 검증 `genie_screen_validation.txt`: 같은 도구로 SRT 풀 −3 / +15 dB 0.813 / 0.496, DMC 풀 0.722 / 0.244 — 등록 실행(테스트 풀)의 Perfect CSI 0.817 / 0.499, 0.686 / 0.239 와 같은 수준.)

**σ 격자** (`runner.py sigma --testbed D2 --prior <P> --cell C1 C2 --tag <P>`; `sigma_grid_D2_{SRB,DMI}.{txt,npz}`): SRB 20 점 ν_q [2.142e-03, 1.461e+00] → σ_t [3.273e-02, 8.548e-01]; DMI ν_q [2.162e-03, 1.437e+00] → σ_t [3.288e-02, 8.477e-01]. **공개: 이 측정으로 두 prior 의 테스트 시행 0..63 (C1·C2, 7 SNR) 이 Gaussian 수신기로 한 번 실행됐다**(BLER 은 읽지도 쓰지도 않음; 모든 prior 의 관례).

**일괄 kron EM 검사** (`results/nr8b_batched_check_{SRB,DMI}_n160000.txt`, GPU 1): SRB (a) N′ = 160000 K = 512 PASS (max\|Δll\| 4.8e-11, 재시드 600/600), (b) N = 10000 PASS (재시드 2725/2725); DMI (a) PASS (1.3e-10, 재시드 113/113), (b) PASS (1418/1418) → kron 계열은 일괄 경로, full 계열은 정확 경로.

**기존 경로 불변**: `selftest_sv.py` 742 배열 · `selftest_mix3.py` 968 배열 IDENTICAL; `dmimo.py selfcheck 8 DMC` · `SRT` train sha 불변(e6ddafc27367f975 · d15b033bc915cf88); `paper_f21dmc.py` (DMC · SRT) · `paper_f33cdf.py SRT` 의 그림·기록 바이트 동일.

---

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **셀·예산·시행 (기존 실험과 같은 크기 — 사용자 지시)** | SRT16e4 §1 첫 행 그대로: C2 = 8×4, T 16, Tp 4, K = 42, rate-1/2 conv (133,171)_8, QPSK, 16 반복, **7 SNR (−3 … 15 dB; 결과 전에도 뒤에도 격자를 바꾸지 않는다)**, n = 2560, 테스트 시행 0..2559 (chunk 40), 수신기 CPU complex128, 시행 시드 `common.trial_rng` 에 **PID SRB = 13 · DMI = 14** (다른 모든 prior 와 다른 스트림 → 다른 데이터셋과의 비교는 짝 없음). N′ = 160000 = `arms.training_set("D2", <P>, 8, 4, 160000)` (스트림 7) 을 GMM 적합과 score 학습(자체 9:1)이 함께 쓴다; GMM 검증 5000 = 스트림 8 |
| **지위** | **UNGATED** → "prior·기전 축 측정" 이며 arm 판정이 아니다. SRB·DMI 는 어느 결과에서도 헤드라인이 되지 않는다 |
| **생성 모델** | §0 의 표와 빌더 머리말(`code/srb_build.py`, `code/dmi_build.py` @44d3ab5e = 원문; 동결 — 바꾸려면 새 결정 + 새 prior id). 풀 파일 `~/data/sionna_rt/srb_Nr8/` · `~/data/deepmimo/dmi_Nr8/` 의 `{H.npy, split.npy}` 는 git 밖, sha 로 고정 |
| **block split 과 스트림** (`dmimo.py`; 도시 풀과 같은 코드) | 타일을 섞어 쌍의 15 % 이상을 담을 때까지 = 테스트 타일; 나머지의 동결된 무작위 20,000 = 검증 풀, 나머지 = 학습 풀. 타일: SRB floor(xy / 1 m), DMI floor(위치 xy / 0.5 m) — 방이 작아 도시 풀의 20 m 타일은 쓸 수 없다. 스트림 → 풀: 학습 스트림 7 → 학습 풀에서 서로 다른 n 쌍; 스트림 8 → 검증 풀; 스트림 10·모든 시행 스트림·`sparse_tune` 개발 스트림 → 테스트 풀 복원 추출 |
| **고유 사항 (공개; 고치지 않고 그대로 잰다)** | (1) **유한 풀·한 장소**: 테스트 시행은 테스트 풀(SRB 52,353 · DMI 60,700 쌍)에서 복원 추출(한 점의 2560 시행 안의 기대 중복 약 2560²/(2·52353) ≈ 63 쌍 · 2560²/(2·60700) ≈ 54 쌍); 채널 모집단은 "이 방·이 기지국 한 곳의 테스트 타일". (2) **가까운 이웃**: 타일이 1 m · 0.5 m 라 테스트 위치가 학습 위치와 가깝다(SRB 는 28 GHz 에서 약 93 λ, DMI 는 2.4 GHz 에서 4 λ 타일) — 채널 거리로 본 누수는 §0 TDMh (0.004 · 0.058); DMI 는 같은 위치를 yaw 만 바꿔 5 번 쓴다(한 위치의 yaw 5 개는 split 의 같은 쪽). (3) **Sionna `box` 는 금속 벽**(기본 제공 재질)이고 반사는 1 차까지만 넣었다 — 현실의 방이라기보다 "LoS + 무손실 1 차 반사 6 개" 인 기하 채널이다. (4) **선택 편향**: 이 두 풀은 BLER 수준이 낮도록 고른 것이다(선택 경위). (5) 모든 링크가 LoS 다(1.000). (6) V1·b\* 의 학습·모델 선택은 학습 타일 안에서만 한다; baseline 조정용 개발 채널은 테스트 풀에서 나온다(DMCBASE16e4 "DMC 고유 1" 과 같음 — baseline 에 유리한 방향). (7) σ 격자 측정은 테스트 시행 0..63 을 Gaussian 수신기로 한 번 실행한다(§0). (8) SRB 의 `PathSolver` 는 기본(비결정적 후보 생성)으로 돌렸다 — 재생성이 같은 sha 를 낸다는 보장이 없다 |
| **파일럿** | D2 의 T2b 규칙을 학습 집합의 Rt 에 적용(`dmimo.RT`) → 두 prior 모두 **DFT 파일럿**(§0 TDMe; 도시 풀은 eigen 정렬이었다) |
| **GMM 격자와 b\*** | SRT16e4 §1 과 같다: full K ∈ {16 … 512} (정확 경로) + kron K ∈ {16 … 512} + kron 1024·2048·4096 재시작 후보 3 개씩(일괄 경로), 선택 = 검증 우도 최대(스트림 8). 반복 규칙: b\* 가 kron 2048 이면 4096 병합, **4096 에서 멈춘다** + 캐비엇; b\* 가 full 512 이면 full 1024 한 번 + 캐비엇. **BLER 은 선택에 쓰지 않는다.** 큐 `code/run_room_gpu.sh` (두 prior 한 큐: 학습 2 + 적합 42 작업, GPU 0·1·2). 병합·선택·끝 규칙·fits 링크는 `code/run_{srb,dmi}_post_select.sh <동결 커밋>` (동결 커밋이 v2 인지와 그 prior 의 적합 21 작업의 rc=0 을 확인; 선택 결과는 `logs/tb2_post_<P>.sel`) |
| **체크포인트·평가 가중치·학습 실패 처리·σ 격자** | SRT16e4 §1 과 같다: 동결 레시피 `run_d2_sx.py --prior <P> --ntrain 160000 --tag <P>B16e4 --fallback 1 --no-gbprime` (479,426 params; patience 20, 최소 200, 최대 3000 epoch), rung **D2SXSRB160000 · D2SXDMI160000**, attempt 1 → `ckpt/d2sx_<P>_N160000_a1{,_best}.pt`; 판정 태그 `<P>B16e4` = `_best`, `<P>B16e4last` = last-EMA 보고 전용; §3d 사다리(발산 → 시행 2 = 기울기 클리핑 1.0 → 시행 3; `run_tb2.sh train_chain` 이 자동으로 이어 돌린다 — 44d3ab5e 부터 학습을 시작부터 `taskset` 으로 HT 쌍 하나에 고정, 결과 중립); σ 격자 = prior 자체 격자 `sigma_tag = <P>` (§0) |
| **순서 규칙** | 동결 커밋 → prior 마다 kron 1024·2048 병합·b\* 선택(→ 4096) → ALD 개발 재생성·조정 → §5 채움·커밋(두 prior 를 한 커밋 또는 prior 마다; 각 prior 의 실행 커밋 = 그 prior 의 §5 를 담은 커밋) → 주 실행 → 수용 → baseline 단계 → §6. **주 실행은 한 번에 하나만 돈다**(192 워커): SRB 먼저, 이어서 DMI — 순서는 결과와 무관하게 여기서 고정. 한 prior 의 주 실행·baseline 이 끝난 뒤 다른 prior 의 runner 가 돌기 전에는 커밋할 수 있다(runner 가 도는 동안 main 커밋 금지; raw 마다 깨끗한 커밋 하나). **작성자는 동결 전에 다음을 읽지 않는다**: `results/gmm_fits_D2_{SRB,DMI}B16e4/*.npz` 와 `logs/tb2_gpu{0,1,2}.log` (ll_val 이 찍힌다), `logs/tb2_post_{SRB,DMI}.{log,sel}`, `results/sparse/{tune,pick}_{SRB,DMI}_C2.json` 과 `logs/sparse_tune_{SRB,DMI}_C2.log`, `results/ald/tune_PIL{SRB,DMI}.json` 과 `logs/ald_tune_PIL{SRB,DMI}.log`, `results/d2_gbprime_{SRB,DMI}*`·`logs/gbprime_{SRB,DMI}B16e4.log` (읽는 것은 `logs/tb2.log` 의 작업 시작·종료 줄, 파일 개수, 학습 로그의 epoch 줄, `logs/tb2_train_state_<P>.txt` (시행 번호·정지 사유), `logs/ald_regen_PIL<P>_dev.log` (점수 없음)뿐). `logs/tb2_queue.txt`·`logs/queue.log`·`logs/tb2.log`·`logs/sparse_tune.log` 는 두 prior 가 함께 쓰는 추가 전용 로그다(적합 폴더·`.sel`·raw·태그는 prior 마다 따로). 병합 파일 `fit_<P>_Nr8_kronK{1024,2048,4096}_n160000.npz`·`tb2_post_<P>.sel` 의 mtime 은 동결 커밋 시각보다 뒤여야 한다(§5). 희소 baseline 조정(`sparse_tune.py --prior <P> --cell C2 --n 256`, CPU 2 스레드, BLER 없음)은 풀이 고정되는 대로 시작해 다른 단계와 겹쳐 돈다. **GB′ 는 보고 전용이고 그 prior 의 §5 커밋 뒤에 계산한다**(`run_{srb,dmi}_post_gpu.sh <k> GBP <GPU>`; 주 실행과 겹쳐도 된다) |
| **실행 — 주 실행** | `CUDA_VISIBLE_DEVICES= code/run_prior_eval.sh <P> <P>B16e4 d2sx_<P>_N160000_a1[_fb<k>] <bstar> <kronK\|-> <ll_val> <best_sha> <last_sha> "<grid>"` (인자는 §5 가 기록한 것만; `code/run_{srb,dmi}_eval.sh` 에 원문 — §5 커밋에서 채운다). prior 마다 한 번 |
| **실행 — baseline** | SRT16e4 §1 "실행 — baseline" 그대로, prior 마다: 선행 `ald.py regen --tag PIL<P> --prior <P> --cell C2 --fits-tag <P>B16e4 --set dev` → `ald.py tune --tag PIL<P> --ckpt ckpt/<stem>_best.pt` (`run_{srb,dmi}_post_gpu.sh <k> ALD <GPU>`); 본 실행 `code/run_{srb,dmi}_base.sh <ckpt_stem> <best_sha16> <pick_sha16> <tune_ald_sha16> <bstar> <kron_K\|-> <ll_val>` — 순서 PIL → ALD → SP → `pair_baselines`. 빈 GPU 가 없으면 `DEFER_ALD=1` (SRT16e4 §1 의 조건 그대로). SPARSE 격자는 한 판으로 끝낸다(끝값이면 끝값 + 캐비엇) |
| **수용 검사** | SRT16e4 §1 (a)~(e) 그대로, prior = SRB / DMI. (c) 의 글자 조건: 두 태그의 `results/tables_D2_<tag>.txt` 에 문자열 `SITE-SPECIFIC RAY-TRACED TESTBED (prior <P>)` 가 있고 문자열 `CLAIM TESTBED -- sparse specular` 가 없다; DMI 는 더해서 `FIVE frozen UE yaws per position` 이 있고 `FIVE fixed` 가 없다(검토 M1: 초안 커밋의 배너가 "기지국 5 곳" 으로 잘못 적혀 있었다 — 동결 커밋에서 문구만 고침); `eval_accept.py` 가 검사하지 않는 항목(배너·raw 이름·`N_train` 줄·저장된 prior / sigma_tag·Demo 해시)은 읽어 확인하고 §6 에 적는다. (e) GB′ 로그의 `GMM b* =` 줄 = §5 최종 b\* 이고 `d2_gbprime_<P>_*.npz` 의 mtime 이 병합 파일 뒤 — 어긋나면 GB′ 수치만 무효. baseline: 태그마다 `eval_accept.py`, R5-genie 가 `raw_<P>B16e4` 와 비트 동일, `pair_cross`·`pair_ald` 무결성, pick 재현·`meta\|sparse` |
| **측정 판정** | 주: 표 B `M-ours-bstar → M-ours-dscore-C-V1` (판정점 = 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 안에서 \|log10(BLER/0.1)\| 최소 3 SNR, 점마다 exact 양측 부호검정; POWERED 이고 second arm fewer ≥ 2/3 → (i); first arm fewer ≥ 2/3 → (ii); 둘 다 아님 → (iii); UNDECIDED(범위 안 SNR 이 3 개 미만이거나 불일치 쌍 부족) → (iv)). baseline: `pair_baselines.py --base raw_<P>B16e4 --pil raw_PIL<P> --ald raw_ALD<P> --est PIL<P> --extra raw_SP<P> --add-baselines SBL-loop SBL-pilot OMP-pilot --cell C2 --prior <P> --r0 at1 --provenance manifest` → 표 B `X → V1`, X ∈ 𝔅 15 → prior 마다 새 라벨 15 개 + 주 라벨 1 개; 출력 `results/review_next/pairB_SP<P>.txt` |
| **기전 판독** | SRT16e4 §1 그대로: R = (b\*−V1)/(b\*−genie) 를 −3 dB(1차)와 판정점 합(2차)에서, paired bootstrap 90 % (B 2000, `default_rng(20260926)`); ΔR = R(<P>) − R(D2 B16e4k) 비짝 CI 세 갈래 "회수율이 D2 보다 낮다 / 높다 / 판정하지 못함"; 포화 가드(−3 dB 에서 앵커 b\* 의 BLER@16 이 [0.005, 0.9] 밖이거나 b\* 실패 ≤ genie 실패 → 1차 "판정하지 못함(범위 밖)", 2차만 보고; **가드가 발동하면 −3 dB 의 R 값은 §6 에 옮기지 않는다** — SRT16e4 감사 S1); 정의 불가 규칙 |
| **보고 전용** | V0·V4·V4b, F3 가드, best 대 last V1, GB′, 격자 표, SNR@0.1 (이번에는 격자 안일 수 있다 — 표 B 의 SNR@0.1 격차 줄을 그대로 옮긴다; 판정에는 쓰지 않는다); **누수 층화** `code/dmc_leak_strata.py --tag <P>B16e4 --prior <P>`; **랭크 층화** `code/rank_strata.py --tag <P>B16e4 --prior <P>` (rank-1 층이 거의 비어 있을 것 — 그대로 적는다); **채널 추정 NMSE 의 CDF** `conference/figures/paper_f33cdf.py <P>` — 패널 넷 = −3 dB 와 판정점 3 SNR, **−3 dB 가 판정점이면 넷째 패널 = 판정점 바로 위의 격자 SNR; 판정점이 3 개에 못 미치면((iv)) 패널 = −3 / 0 / +3 / +6 dB 고정**(검토 M4; 동결 커밋의 스크립트 원문); ALD·SPARSE 조정 표, `pair_cross`·`pair_ald` 의 등록 비교 |
| **그림** | 11 곡선(`paper_f16deep.SHOW`)을 전 SNR n = 2560 으로: `conference/figures/paper_f21dmc.py <P>` → `F21srb_col` · `F21dmi_col`. y 축은 원고 주 그림 F16deep_wide (a) 의 규칙(이 커밋의 `ROOM` 분기 원문): 0 실패 점이 없고 모든 점·막대 끝이 2e-4 위면 (2e-4, 1.2), 아니면 (3e-5, 1.2); 0 실패 점에서는 곡선이 끊기고 Perfect CSI 에만 Wilson 상한 화살표(`paper_f16deep.draw`). n = 20480 보강은 하지 않는다 |
| **다중성** | prior 마다 주 라벨 1 + baseline 새 라벨 15; 등록 사이·prior 사이 보정 없음(다른 데이터셋과 같은 관례) |
| 비용·일정 [추정] | 학습 2 개 5 s/epoch × 300–1200 epoch ≈ 0.5–1.7 h; GMM 격자 42 작업 GPU 3 장 ≈ 3–4 h; SPARSE 조정 ≈ 2–3 h; 주 실행 prior 당 2 태그 ≈ 1.7 h (합 3.4 h, 순차); baseline prior 당 ≈ 15 분 |

## 2. 라벨 (여기서 고정; "측정" 이지 arm 판정이 아니다)

표 B `b* → V1` (C2), prior 마다. 이름: SRB = "Sionna RT 방 (내장 `box` 장면 28 GHz, 고정 기지국 한 곳, block split)", DMI = "DeepMIMO 실내 (`i1_2p4` 2.4 GHz, 고정 기지국 한 곳, block split)".

| 결과 | 기록 |
|---|---|
| (i) | "<이름> 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)" — 회수율·ΔR 문장과 함께 |
| (ii) | "<이름> 에서 b\* 가 V1 보다 적게 실패" — 회수율(음수 포함)·ΔR 과 함께 |
| (iii) | "판정하지 못함 (유의 방향 없음)" |
| (iv) | "판정하지 못함 (검정력 미달)"; SNR 격자를 결과 뒤 늘리지 않는다 |
| 학습 실패 | BLER 미실행, "학습 실패" |

- baseline: (i)~(iv) 는 같은 규칙을 X → V1 에 적용. **"전부" 문장**: 그 prior 의 주 라벨이 (i) 이고 15 개가 모두 (i) 일 때만 "<이름> 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)"; 여기에 R_{X\*}(−3 dB) 90 % CI 하한 > 0 (`pair_baselines` 의 condition 줄 MET) 이면 "…전부와 멀어진다"; 아니면 (i) 의 수와 (i) 가 아닌 arm 의 이름·라벨을 그대로 적는다.
- 어디에서도 동치 문구를 만들지 않는다. 모든 라벨 문장에 §1 "고유 사항" 의 (1) 유한 풀·한 장소 · (2) 가까운 이웃 · (3) 금속 벽·1 차 반사(SRB 에만) · (4) 선택 편향 · (6) 개발 채널(baseline 라벨에만) 을 붙인다. 범위: 이 방·이 기지국·이 split·이 크기 한정.

## 3. 미리 적는 예측 (빗나가면 그대로 쓴다; 도시 풀 두 개의 결과와 §0 의 통계·Perfect CSI 선별값을 본 뒤의 예측이며, 두 풀에서 prior 의존 arm 의 BLER 은 본 적이 없다)

prior 마다 따로 채점한다(문장마다 SRB / DMI).

1. **표 B: (i)** — V1 이 b\* 보다 적게 실패. 확신 중간 이하. 근거: D2 (B16e4k) · 38.901 UMi28 · DeepMIMO 도시 · Sionna RT 도시가 (i) 였다. 반대 근거: 방 하나의 채널은 (위치, yaw) 3 차원 다양체라 큰 K 의 kron GMM 이 잘 덮을 수 있다; 판정점이 3 개에 못 미치면 (iv). 채점: (i) = 적중; (ii)·(iii) = 빗나감; (iv) = 채점 불가.
2. **판정점 = −3 / 0 / +3 dB 이고 POWERED** (앵커 b\*). SRB 확신 중간, **DMI 확신 낮음**(선택 경위 4: +2 dB 선별값 0.003). 채점: 세 점이 −3 / 0 / +3 이고 POWERED = 적중; 범위 안 SNR 이 3 개 미만이거나 다른 세 점 = 빗나감.
3. Perfect CSI 의 BLER 수준: **관측됨(채점 제외)** — 선별에서 봤다(§0).
4. **1차 ΔR 의 포화 가드는 발동하지 않는다**(−3 dB 에서 b\* 의 BLER@16 ∈ [0.005, 0.9] 이고 b\* 실패 > genie 실패). 채점: 미발동 = 적중. ΔR 의 방향은 예측하지 않는다.
5. 회수율 R(−3 dB) 의 90 % CI 하한 > 0 (가드가 발동하면 채점 불가).
6. `R2-ours-G → b*`: b\* (second arm) 가 ≥ 2/3 점에서 적게 실패. 확신 높음.
7. **SNR@0.1 이 격자 안**: 표 A 에서 V1 과 b\* 의 SNR@0.1 이 둘 다 숫자다("> 15" 도 "< −3" 도 아님; 한 문장으로 채점; Perfect CSI 는 선별에서 봤으므로 넣지 않는다 — 검토 S2). 그리고 표 B `b* → V1` 의 SNR@0.1 격차(b\* − V1) > 0 dB (격차가 n/a 면 채점 불가).
8. GB′ median ≤ 0.90.
9. 학습: **평가에 쓰는 시행(사다리의 마지막 시행)** 이 patience 정지이고 그 시행의 epoch ∈ [300, 1500] (시행마다 epoch 은 0 부터; 발산 여부는 예측하지 않는다 — SRT 는 시행 1 이 발산했다). [초안을 쓸 때 본 것: 두 학습 로그의 epoch 30 부근 줄. 동결 시점의 epoch 은 `DECISIONS.md` 동결 줄에 — 그때 이미 300 을 넘었으면 하한은 "관측됨" 이고 상한과 정지 사유만 채점한다]
10. GMM: **b\* = kron 계열**이고 K ≥ 1024 (도시 풀·UMi28·MIX3 선례는 4096 = 격자 끝). 두 문장 따로 채점하지 않는다; b\* 가 full 계열이면(끝 규칙으로 full 1024 를 돌린 경우 포함) 빗나감.
11. V0: 가드 발동률이 −3 dB 에서 ≥ 0.5 이고 −3 dB BLER ≥ 0.9. best 대 last V1: 판정하지 못함(pooled p > 0.05).
12. 대조군 `b* → b*-scalar`: (iii). 채점: (iii) = 적중; (i)·(ii) = 빗나감; (iv) = 채점 불가.
13. baseline 15 개(`V1-pilot` 포함): **(ii) 0 이고 (i) ≥ 12**; `pair_ALD<P>.txt` 의 A3 (`ALDv-pilot → V1-pilot`) = (i); `pairB_SP<P>.txt` 의 실패 수 표에서 −3 dB 에 `SBL-pilot` < `R0-pilot@1`. 세 문장을 따로 채점한다. (`V1-pilot` 의 라벨은 예측하지 않는다 — 도시 풀에서는 (iii) 였지만 랭크가 높은 채널에서는 루프 이득이 있을 수 있다.)
14. 랭크 층화: **관측됨(채점 제외)** — 테스트 풀의 rank-1 비율을 이미 봤다(§0: 0.033 · 0.021; 검토 S1). 층별 BLER 은 예측하지 않는다.
15. 누수 층화·NMSE CDF: 예측하지 않는다.
16. 빗나갈 경로: (a) (ii) 또는 (iii) → 그대로 기록, 레시피 탐색 없음, 사후 설명은 사용자; (b) R 이 음수 → 그대로; (c) (iv) → 그대로, **SNR 격자 확장도 다른 풀로의 교체도 이 등록 안에서는 하지 않는다**(새 풀은 새 등록 + 사용자 결정); (d) 발산 → §3d; (e) b\* 가 full 512 → full 1024 한 번 + 캐비엇; (f) baseline 에 (ii) 가 하나라도 → 그대로, 재조정 없음.

## 4. 선행 작업과 실행 현황 (갱신한다; 시각은 `date` 로 읽음)

| 항목 | 상태 |
|---|---|
| rank-1 탐색·Perfect CSI 선별 (`rank_probe_2026-10-11/`: Sionna 기지국 위치 탐색, DeepMIMO 시나리오 탐색, 방 장면·재질·깊이, 선별 도구) | **완료·커밋 44d3ab5e** (10-11 09:59 → 11:00 CDT) |
| 풀 빌더·연결(`srb_build.py`, `dmi_build.py`, `common`·`dmimo`·`analysis` 등, `run_{srb,dmi}_*.sh`, `run_room_gpu.sh`) + sha 고정·보정·testbed·σ 격자·일괄 EM 검사 + 기존 경로 비트 동일 검사 | **완료·커밋 44d3ab5e** (§0) |
| 그림 스크립트의 방 풀 분기(`paper_f21dmc.py` `ROOM`, `paper_f33cdf.py` 넷째 패널 규칙) | v1 커밋 01f5a726 에 포함; 동결 커밋에서 (iv) 일 때의 패널 규칙(M4)과 SRB 제목 문구(S6)를 더함 (DMC · SRT 의 그림·기록 바이트 동일 확인) |
| 학습 SRB · DMI (`@train`, tmux `tb2room`, GPU 1 · GPU 0, 시작부터 HT 쌍 고정) | 진행 중: 큐 시작 10-11 11:03 CDT (git 44d3ab5e); split_hash c009329584978bd9 (SRB) · fecf46b30175b5c8 (DMI), E‖H‖² 1.000000 |
| GMM 격자 SRB · DMI (42 작업, `logs/tb2_queue.txt`, GPU 2 → 학습 뒤 GPU 0·1 도) | 진행 중: 10-11 11:03 CDT 부터 (`logs/tb2.log`) |
| SPARSE 조정 SRB · DMI (`run_{srb,dmi}_sparse_tune.sh`, tmux `sptsrb` · `sptdmi`, CPU 2 스레드씩) | 진행 중: 10-11 11:03 CDT 시작 (git 44d3ab5e; 동결 전에 읽지 않는다) |
| 이 문서 초안 v1 → 적대적 검토(Fable) → v2 → 동결 커밋 | 검토 끝(10-11 11:19 CDT 보고; MUST 4 · SHOULD 8 · NIT 3). 반영: **M1** DMI 배너 문구("기지국 5 곳" → "기지국 1 곳 × yaw 5"; `common.py` 문구만) + 수용 (c) 글자 조건, **M2** 선택 경위 4 를 시간 순서로 다시 씀(빌드 때의 기준 = 0 dB ≥ 0.011, 정규화 안 한 첫 선별; "+2 dB" 문장은 빌드 뒤), **M3** DeepMIMO 실외 최저값 문장 정정, **M4** NMSE CDF 의 (iv) 패널 규칙 + 스크립트 분기, S1 예측 14 를 관측으로·테스트 풀 rank-1 을 §0 에, S2 예측 7 의 정의, S3 콘솔뿐인 수치 표시, S4 testbed 재실행, S5 `DECISIONS.md`·`WORK_QUEUE.md` 줄, S6 그림 제목의 금속 벽·1 차 반사, S7 열람 목록 명시, S8 예측 9 · 10 · 13 의 채점 세칙, N1 복제 스크립트 주석, N2 기대 중복, N3 원시 전력. 검토가 실행으로 확인한 것: 풀 sha·크기·타일·yaw 묶음·키 재계산, DFT 파일럿, 배너(SRB), `analysis.PAT`·rung 색인, `_which`, §0 수치 대조, 큐·로그와 §4, 선별 도구의 rng·채널 출처, 그림 보조 함수, 스크립트 13 개 `bash -n`. **동결 시점의 관측 상태는 `DECISIONS.md` 동결 줄에.** 초안 2026-10-11 11:10 CDT |
| prior 마다: 병합·b\* 선택 → ALD 조정 → §5 → 주 실행 (+ GB′) → 수용 → baseline → §6 → 기록 감사(Fable) → 그림 | 대기 |
| 공개: GPU 2 에서 돌던 시드 학습(`run_srt_seeds_train.sh`: SRT a2 · a3, DMC a2 는 patience 로 끝남, DMC a3 는 epoch 675 에서 멈춤 — 이 등록과 무관)을 10-11 09:53 CDT 에 멈추고 GPU 를 탐색·이 등록에 넘겼다(`logs/seeds_SRT_train.log`) | — |

## 5. 평가 전 고정 기록 (실행 전에 채우고 커밋한다)

갱신 2026-10-11 15:06 CDT (Opus 5.5). 값은 파일에서 읽었다(생성기 `prereg_audit_2026-10-11/s5_gen.py SRB SRBB16e4 d2sx_SRB_N160000_a1`; `logs/tb2.log`, `logs/tb2_post_SRB.{log,sel}`, `results/sparse/pick_SRB_C2.json`, `results/ald/tune_PILSRB.json`). **모두 동결(b737fd55, 10-11 11:23:26 CDT) 뒤에 읽었다.**

**DMI — 사용자 결정으로 실행 전 철회** (2026-10-11 CDT, 원문 "Deepmimo 포기하고 sionna에 올인해"; 큐에서 뺀 시각 13:49 CDT; `DECISIONS.md` 같은 날 줄): DMI 의 학습은 끝나 있었고(시행 1, patience 정지, epoch 1162; `ckpt/d2sx_DMI_N160000_a1{,_best}.pt` 는 디스크에 남김), GMM 적합은 하나도 시작하지 않았으며 큐에서 적합 21 작업을 뺐다(10-11 13:49 CDT, `logs/tb2.log` NOTE). SPARSE 조정 파일은 만들어졌으나(12:49 CDT) 읽지 않았고 ALD·GB′ 는 없다. **DMI 의 BLER 은 한 번도 돌지 않았다 — 라벨 없음, §6 없음.** 이 문서의 DMI 에 관한 §1~§3 은 실행되지 않은 등록으로 남는다. 아래는 SRB 만이다. **[2026-10-12 16:13 CDT 추가: 이 철회를 되돌렸다 — 사용자 "Deepmimo 지금 못하나?" (10-12 CDT); DMI 의 평가 전 고정 기록은 이 절 끝의 '5-DMI' 블록, `DECISIONS.md` 10-13 04:02 KST 줄]**

| 항목 | SRB (SRBB16e4) |
|---|---|
| PID · rung · σ 격자 태그 | 13 · D2SXSRB160000 · `SRB` σ_t [3.272627191797374e-02, 8.548070100767116e-01] (20 점) |
| 풀·보정 | `H.npy` ae1c023605d002b4 / `split.npy` 24c202836d56b34e; P_RAW 1.0005289046575756, TRAIN_SHA 2544c37a719436e2; testbed ALL PASS (§0); 파일럿 DFT (erank Rt 3.991) |
| 격자: K 별 ll_val (재시작, n_iter/it_best, 재시드, κ) · 구현 경로 | **full** (정확 경로): 16 30.445 (r0, 361/340, 재시드 0, κ=0) / 32 41.698 (r2, 179/150, 재시드 354, κ=0) / 64 55.912 (r2, 190/180, 재시드 188, κ=0) / 128 68.085 (r1, 388/370, 재시드 4,632, κ=0) / 256 79.119 (r0, 244/240, 재시드 8,953, κ=0) / 512 89.214 (r1, 188/180, 재시드 15,243, κ=0) / 1024 97.009 (r0, 182/180, 재시드 44,081, κ=0). **kron** (일괄 경로): 16 25.940 (r1, 121/80, 재시드 0, κ=0) / 32 34.173 (r2, 164/140, 재시드 164, κ=0) / 64 41.133 (r2, 196/160, 재시드 970, κ=0) / 128 46.060 (r2, 161/120, 재시드 3,657, κ=0) / 256 51.939 (r1, 123/90, 재시드 6,171, κ=0) / 512 56.836 (r1, 147/140, 재시드 15,658, κ=0) / **1024 61.1622399385799** (r0, 181/140, rs 43,670; 후보 r0 61.162 181/140 rs 43,670, r1 61.064 162/160 rs 40,157, r2 61.028 121/80 rs 29,268) / **2048 64.84831463937753** (r0, 215/200, rs 124,714; 후보 r0 64.848 215/200 rs 124,714, r1 64.754 151/110 rs 91,621, r2 64.745 186/170 rs 115,696). kron 4096 후보 셋은 적합됐으나 병합하지 않았다(b\* 가 kron 2048 이 아니라 규칙 미발동; 후보 ll_val 67.634 / 67.807 / 67.584). 상한 500 정지 없음(전 파일 최대 388 반복). 큐의 적합 21 작업 10-11 11:03 → 10-11 14:07 CDT, 모두 rc=0 (`logs/tb2.log`; GPU 0·1·2) |
| 확장 결정과 시각 (`code/run_srb_post_select.sh b737fd55`, `logs/tb2_post_SRB.log`; **순서 규칙**: 동결 11:23:26 CDT 가 먼저) | 병합 파일 mtime: kron 1024 10-11 14:07:49 CDT · 2048 14:07:55 CDT → **b\* = full 512** (89.21392313986264 = full 계열의 기본 격자 끝; kron 계열 최고는 2048 의 64.848) → 등록된 끝 규칙 "b\* 가 full 512 이면 full 1024 한 번": `fit_gpu.py 8 full 1024 160000 SRBB16e4 --prior SRB` (GPU 2, 14:08 → 14:49 CDT, rc=0; 파일 mtime 14:49:46 CDT) → 같은 선택 코드(`arms.gmm_selection`)로 다시: **b\* = full 1024** (97.00871495382869) → **여기서 멈춤**(full 2048 은 돌리지 않는다). `tb2_post_SRB.sel` = `gmm1024 - 97.00871495382869` (스크립트가 처음 쓴 `gmm512 …` 를 full 1024 뒤에 손으로 다시 씀 — `logs/tb2_post_SRB.log` 의 10-11 14:50 CDT 줄). **[감사 S2 — 실행 뒤 추가, 2026-10-11 17:03 CDT]** `run_srb_post_select.sh` 는 kron 2048 → 4096 규칙만 구현하고 full 512 → full 1024 는 손으로 한다(스크립트 머리말; 스크립트 자신의 마지막 줄은 `gmm512 - 89.21392313986264`). 14:50 CDT 의 재선택은 작성자가 인라인 파이썬 `runner._init("SRBB16e4"); arms.gmm_selection("D2", "SRB", 8, 160000)` 을 돌려 나온 `SELECT b* = gmm1024 ll_val = 97.00871495382869` 를 `echo` 로 `.sel` 과 로그에 옮겨 적은 것이다. `.sel` 을 읽는 코드는 없다 — `run_srb_eval.sh` · `run_srb_base.sh` 는 `gmm1024` 를 인자로 받고 `eval_accept` 가 raw 의 meta 와 대조한다(감사가 `gmm_selection` 을 다시 돌려 같은 값을 확인). 모두 동결 뒤 ✓ (큐의 적합 21 작업 가운데 3 개(kron 1024 후보)는 동결 전에 끝났다 — 작성자는 동결 전 어떤 ll_val 도 읽지 않았다) |
| 최종 b\*: 계열·K·ll_val, 격자 끝 캐비엇 | **b\* = full K = 1024, ll_val 97.00871495382869** (재시작 0, 182 반복 / 최고 180, 재시드 44,081). **격자 끝**(512 대비 +7.795 nat, 오르는 중 — 등록 규칙대로 한 번만 확장) + 수렴 캐비엇(재시드 4.4 만). 이 풀에서는 full 계열이 kron 계열을 크게 앞선다(97.0 대 64.8; 도시 풀·경로 풀과 반대). 수용 검사 `--bstar gmm1024 --ll-val 97.00871495382869` |
| 학습 | 시행 1 (클리핑 없음): `ckpt/d2sx_SRB_N160000_a1.pt` epoch 1680, stopped_by **patience** (best val 0.24769899249076843 @1660; 10-11 11:03 → 13:27 CDT, 8627.0 s, 5.135 s/epoch; 시작부터 `taskset -c 21,117` 고정). 발산 없음 → 사다리 미발동. `logs/tb2_train_state_SRB.txt` = `1 patience` |
| 체크포인트 | best `ckpt/d2sx_SRB_N160000_a1_best.pt` **ed437f21af15c305** (epoch 1660, role best); last `…_a1.pt` **b5f74923f2bd2920** (epoch 1680, best_epoch 1660, stopped_by patience, role last); prior SRB, sigma_tag SRB, rung D2SXSRB160000, attempt 1, split_hash c009329584978bd9 |
| SPARSE 조정 (`run_srb_sparse_tune.sh`, CPU 2 스레드) | 10-11 11:03 → 12:49 CDT (`SPARSE_TUNE_DONE rc=0`; wall_sec 6345.2; git 44d3ab5e). `pick_SRB_C2.json` sha256[:16] **4c6da315c701b9d4**, `tune_SRB_C2.json` 5ab11b4a8c4189d1. 고른 값: **SBL ρ = 16 = 격자 끝**(−14.798 dB), n_em −3…15 dB = 3 / 5 / 5 / 5 / 5 / 10 / 10 (끝값 없음); **OMP ρ = 16 = 격자 끝**(−13.455 dB), L = 3 / 4 / 4 / 6 / 8 / 8 / 32 (끝값 없음). 두 ρ 모두 끝값 + 캐비엇, 확장하지 않는다 |
| ALD 조정 (`run_srb_post_gpu.sh 1 ALD 0`, GPU 0) | 10-11 14:07 → 14:19 CDT rc=0 (최종 b\* 확정 전에 돌았다 — ALD 조정은 b\* 를 쓰지 않는다). `results/ald/tune_PILSRB.json` sha256[:16] **e0adb06cce792093** (git 99039ef5 = 그때의 HEAD, ckpt `ckpt/d2sx_SRB_N160000_a1_best.pt`, ckpt_sha ed437f21af15c305, n_dev 512, dev_skip 2560), `tune_PILSRB_curves.npz` 881f0ce4ea700da0. 고른 값: **c = 0.01, β = 0.005** (개발 최적 c 0.01 · β 1e-05 −16.646 dB; 저자 기본값 β 0.005 가 −16.607 dB 로 0.1 dB 안 → 유지; β 축 두 번 확장, 확장 뒤 끝값 없음); 멈춤 단계 −3…15 dB = 390 / 525 / 600 / 600 / 600 / 600 / 600; 개발 NMSE −7.34 / −10.85 / −14.73 / −17.17 / −19.75 / −22.12 / −24.30 dB |
| GB′ | 아직 계산하지 않았다(§1: §5 커밋 뒤, 보고 전용) |
| §3 예측 가운데 BLER 전에 채점되는 것 (SRB) | **9 (patience 정지 · epoch ∈ [300, 1500]): 빗나감** (patience ✓, epoch 1680 ✗). **10 (b\* = kron 계열, K ≥ 1024): 빗나감** (b\* = full 1024). 나머지는 실행 뒤 |
| 실행 사실(공개) | (1) 큐 조작: 정지 파일로 작업자를 두 번 멈췄다 다시 띄웠고(11:45 → 11:52, 13:13 → 13:23 CDT; `NEXT_EXPERIMENTS_PATH16e4.md` 의 SRP 풀 생성·ALD 조정에 GPU 를 쓰려고), SRP 의 22 작업을 큐 맨 앞에 넣었으며(12:11 CDT), DMI 적합 21 작업을 뺐다(13:49 CDT) — SRB 의 작업 내용과 순서는 `run_room_gpu.sh` 그대로다(`logs/tb2.log`). (2) SRB 학습(GPU 1)은 11:03 → 13:27 CDT 내내 방해 없이 돌았다. (3) 이 §5 는 `NEXT_EXPERIMENTS_PATH16e4.md` 의 SRP 주 실행이 끝난 뒤에 커밋한다(두 등록 공통 순서: SRP 주 → SRP baseline → SRB 주 → SRB baseline); 작성자는 이 §5 를 쓸 때 SRP 의 결과 표를 열지 않았다 |
| 스크립트 인자 원문 | 주 실행: `CUDA_VISIBLE_DEVICES= code/run_prior_eval.sh SRB SRBB16e4 d2sx_SRB_N160000_a1 gmm1024 - 97.00871495382869 ed437f21af15c305 b5f74923f2bd2920 "full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048"` (= `code/run_srb_eval.sh`, 이 커밋에서 채움). baseline: `bash code/run_srb_base.sh d2sx_SRB_N160000_a1 ed437f21af15c305 4c6da315c701b9d4 e0adb06cce792093 gmm1024 - 97.00871495382869`. 실행 커밋 = 이 §5 커밋; fits 링크 `gmm_fits_D2_SRBB16e4last` 는 `run_srb_post_select.sh` 가 10-11 14:07 CDT 에 만듦 |

### 5-DMI. 평가 전 고정 기록 — DMI (철회를 되돌려 실행; 기록 2026-10-12 16:13 CDT, Opus 5.5)

**경위와 공개**: DMI 는 10-11 CDT 에 사용자 결정으로 실행 전 철회됐고(위), 10-12 CDT 사용자 질문 "Deepmimo 지금 못하나?" 에 따라 되돌렸다(이 세션의 해석 — `DECISIONS.md` 같은 날 줄). **규칙은 이 문서 v2 (동결 b737fd55) 의 DMI 에 관한 §1~§3 그대로**이고 새 규칙·새 예측은 없다(§3 의 예측은 동결 때의 것). 동결 뒤·DMI 실행 전에 작성자와 사용자는 **SRB 의 §6 전부와 PATH16e4 (SRP) 의 결과 전부, 두 풀의 그림 보강(n = 20480 / 81920)과 시드 강건성**을 봤다. DMI 에 대해서는 §0 의 풀 통계·Perfect CSI 선별값과 아래 표의 값(검증 우도, ALD 개발 NMSE, 학습 곡선)만 봤다 — **DMI 의 BLER 은 이 커밋 전까지 한 번도 계산되지 않았다**(`raw_DMIB16e4*` 없음; `raw_DMI/` 는 σ 격자 단계의 빈 디렉토리). 동결(b737fd55) 뒤의 `conf/code` 변경은 SRP 용 추가·그림 보강·시드 드라이버·`ald.py` 의 세트 `hisnr4` 추가뿐이고 DMI 의 수신기 경로를 바꾸는 것은 없다(주 실행의 수용과 기록 감사가 본다). **CPU**: 사용자 지시(10-12 CDT "192개 중 절반 정도만" · "한번에 CPU 스레드 다 쓰지 말고")에 따라 runner 를 `taskset -c 24-47,120-143,72-95,168-191` (96 스레드) 아래에서 돈다 — 결과 불변, 시간만 늘어난다.

값은 파일에서 읽었다(생성기 `prereg_audit_2026-10-11/s5_gen.py DMI DMIB16e4 d2sx_DMI_N160000_a1`; `logs/tb2.log`, `logs/tb2_post_DMI.{log,sel}`, `logs/fit_full1024_DMI.log`).

| 항목 | DMI (DMIB16e4) |
|---|---|
| 격자: K 별 ll_val (재시작, n_iter/it_best, 재시드, κ) · 구현 경로 | **full** (정확 경로): 16 28.002 (r1, 103/80, 재시드 0, κ=0) / 32 44.495 (r2, 121/80, 0) / 64 67.588 (r2, 307/300, 0) / 128 83.443 (r2, 179/170, 1) / 256 96.447 (r1, 183/150, 542) / 512 105.851 (r2, 191/190, 5,661) / **1024 112.043** (r0, 72/70, 6,847). **kron** (일괄 경로): 16 10.964 / 32 17.682 / 64 22.517 / 128 26.746 / 256 30.850 / 512 34.837 / 1024 38.050615215363074 (후보 r0 38.051 · r1 37.981 · r2 38.007) / 2048 41.18010947841611 (후보 r0 41.180 · r1 41.097 · r2 41.119); 4096 후보 43.957 / 44.071 / 44.067 — **병합하지 않음**(kron 끝 규칙은 b\* 가 kron 2048 일 때만). 파일 24 개, 최대 n_iter 307. 모든 적합이 it_best ≥ 40 에서 선택됐다(EM 이 초기화에서 멈춘 SRP 와 다르다) |
| 적합 시각 (큐; `logs/tb2.log`) | 21 작업 10-12 14:01 → 14:35 CDT (GPU 0–5; 등록된 목록·순서; 모두 rc=0). 10-11 의 큐에서는 한 작업도 시작하지 않았다(13:49 CDT 에 뺌) |
| 확장 결정과 시각 (`code/run_dmi_post_select.sh b737fd55`, `logs/tb2_post_DMI.log`; **순서 규칙**: 동결 10-11 11:23:26 CDT 가 먼저) | 병합 파일 mtime: kron 1024 10-12 15:46:21 CDT · 2048 15:46:25 CDT → **b\* = full 512** (105.85089193400368 = full 계열의 기본 격자 끝; kron 계열 최고는 2048 의 41.180) → 등록된 끝 규칙 "b\* 가 full 512 이면 full 1024 한 번": `fit_gpu.py 8 full 1024 160000 DMIB16e4 --prior DMI` (GPU 2, 15:46 → 16:11 CDT, rc=0; 파일 mtime 16:11:10 CDT; κ·재시작 12 회 중 (κ 0, r0) 선택) → 같은 선택 코드로 다시(인라인 `runner._init("DMIB16e4"); arms.gmm_selection("D2", "DMI", 8, 160000)` 의 출력을 `echo` 로 `.sel` 과 로그에 옮김 — SRB 와 같은 절차; `.sel` 을 읽는 코드는 없다): **b\* = full 1024** (112.04253042212595) → **여기서 멈춤**(full 2048 은 돌리지 않는다). 적합이 끝난 뒤(14:35) 선택까지 71 분이 빈 것은 작성자의 대기 명령 오류 때문이다(결과와 무관) |
| 최종 b\*: 계열·K·ll_val, 캐비엇 | **b\* = full 공분산 K = 1024 (`gmm1024`), ll_val 112.04253042212595**. **격자 끝 캐비엇**: 확장한 격자의 끝이고 ll_val 은 거기서도 오르고 있었다(512 대비 +6.192 nat) — 규칙대로 한 번만 확장. 수렴 캐비엇(재시드 6,847). 수용 검사 `--bstar gmm1024 --ll-val 112.04253042212595`, 격자 `full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048` |
| 학습 | 시행 1 (클리핑 없음): `ckpt/d2sx_DMI_N160000_a1.pt` epoch 1162, stopped_by **patience** (best val 0.21521511673927307 @1142; 10-11 11:03 → 12:44 CDT, 6074.0 s, 5.227 s/epoch; GPU 0 큐, `taskset -c 20,116`). 발산 없음 → 사다리 미발동. `logs/tb2_train_state_DMI.txt` = `1 patience` |
| 체크포인트 | best `ckpt/d2sx_DMI_N160000_a1_best.pt` **dc784649f1e9b890** (epoch 1142, role best); last `…_a1.pt` **20d28bf06e317ca5** (epoch 1162, best_epoch 1142, stopped_by patience, role last); prior DMI, sigma_tag DMI, rung D2SXDMI160000, attempt 1, grad_clip 0, split_hash fecf46b30175b5c8. σ 격자 20 점 ν [2.162e-03, 1.437e+00] → σ_t [3.288e-02, 8.477e-01] (§0 와 같음) |
| SPARSE 조정 (`run_dmi_sparse_tune.sh`, CPU 2 스레드) | 10-11 11:03 → 12:49 CDT (`SPARSE_TUNE_DONE rc=0`; wall_sec 6342.6) — 철회 전에 만들어졌고 그 뒤 읽지 않았다가 이 기록을 쓰면서 읽었다. `pick_DMI_C2.json` sha256[:16] **8f72c113efb91b0b**, `tune_DMI_C2.json` ec9e1e11da519ae8. 고른 값: **SBL ρ = 16 = 격자 끝**(−14.554 dB), n_em −3…15 dB = 3 / 5 / 5 / 5 / 5 / 10 / 10; **OMP ρ = 16 = 격자 끝**(−13.561 dB), L = 2 / 3 / 4 / 6 / 8 / 8 / 32. 두 ρ 모두 끝값 + 캐비엇, 확장하지 않는다 |
| ALD 조정 (`run_dmi_post_gpu.sh 1 ALD 0`, GPU 0) | 10-12 15:46 → 15:55 CDT rc=0 (최종 b\* 확정 전에 돌았다 — ALD 조정은 b\* 를 쓰지 않는다). `results/ald/tune_PILDMI.json` sha256[:16] **1e7824c1bae10376** (git 003c8e51 = 그때의 HEAD, ckpt `ckpt/d2sx_DMI_N160000_a1_best.pt`, ckpt_sha dc784649f1e9b890, n_dev 512, dev_skip 2560), `tune_PILDMI_curves.npz` 0dac600e287a5224. 고른 값: **c = 0.01, β = 0.005** (개발 최적 c 0.01 · β 1e-05 −16.900 dB; 저자 기본값 β 0.005 가 −16.868 dB 로 0.1 dB 안 → 유지; β 축 두 번 확장, 확장 뒤 끝값 없음); 멈춤 단계 −3…15 dB = 369 / 484 / 552 / 600 / 600 / 600 / 600; 개발 NMSE −8.05 / −11.86 / −14.50 / −17.50 / −19.79 / −22.15 / −24.23 dB |
| GB′ | 아직 계산하지 않았다(§1: §5 커밋 뒤, 보고 전용) |
| 실행 명령 (이 커밋 뒤, 한 번) | `tmux new -d -s dmieval -c /home/HTJ/t2/conf "taskset -c 24-47,120-143,72-95,168-191 bash code/run_dmi_eval.sh"` — `run_dmi_eval.sh` = `CUDA_VISIBLE_DEVICES= bash code/run_prior_eval.sh DMI DMIB16e4 d2sx_DMI_N160000_a1 gmm1024 - 112.04253042212595 dc784649f1e9b890 20d28bf06e317ca5 "full:16,32,64,128,256,512,1024 kron:16,32,64,128,256,512,1024,2048"`. 실행 중 main 커밋·`conf/code`·`DECISIONS.md`·이 문서 변경 없음 |

## 6. 결과 — SRB (주 실행 2026-10-11 15:22~16:17 CDT, `run_prior_eval.sh` @9ad4caa0 = §5 커밋; baseline 16:18~16:32 CDT, `run_srb_base.sh` @7d524638; DMI 는 철회 — §5; 이 절은 추가만 한다; 기록 2026-10-11 16:35 CDT, Opus 5.5 — 전사만, 해석 없음)

수치의 출처: 생성기 `prereg_audit_2026-10-11/s6_gen.py SRBB16e4` 와 `s6_base_gen.py pairB_SPSRB.txt` (표 B 줄은 `results/tables_D2_SRBB16e4{,last}.txt`·`pairB_SPSRB.txt` 원문, 실패 수·BLER 은 raw 를 `analysis.load_raw` 로 읽음, 회수율·ΔR·수용·가드는 각 파일 원문).

**실행·운영 기록**: `code/run_srb_eval.sh` (= §5 의 인자 원문) 한 번, tmux `srbeval`, 10-11 15:22 CDT 시작(git 9ad4caa0 = §5 커밋, `conf/code` clean; 두 등록 공통 순서대로 SRP 의 baseline 이 끝난 직후). 측정 태그 `SRBB16e4` (`_best`) 15:22 → 15:50 CDT (runner 28.3 분), 보고 태그 `SRBB16e4last` 15:50 → 16:15 CDT (24.8 분), 각각 448 작업 · 192 워커; 수용 검사 16:16 CDT, `PRIOR_EVAL_DONE` 16:17 CDT. manifest `run_manifest_SRBB16e4{,last}.json` 둘 다 git 9ad4caa0 · config_hash 6b12b56f55a3319e. 실행 중 main 커밋 없음(다음 커밋 7d524638 은 `PRIOR_EVAL_DONE` 뒤). 함께 돈 것(결과 중립): SRP 의 GB′ (GPU 1, ~15:52 CDT) [감사 N4: 14:07 → 15:52 CDT 에 돌았다 — 이 주 실행의 첫 30 분과 겹침(GPU 만; 수신기는 CPU)], SRP 시드 a2 학습(GPU 0), PATH16e4 의 기록 감사(CPU 3 스레드 이하, 이 실행의 파일은 읽지 않음). 주 실행이 도는 동안 작성자는 SRB 의 진행 줄·결과를 보지 않았다(작업 수 `grep -c` 만).

**수용 검사**: **`ACCEPT: OK -- SRBB16e4, SRBB16e4last`** (`results/review_next/SRBB16e4_accept.txt`; `eval_accept.py` rc 0 — 격자 full 7 (16 … 1024) + kron 8 (16 … 2048) · kron K ≥ 1024 후보 3 개씩, 청크 {(40k, 40)} × 7 SNR, meta ntrain 160000 / bstar gmm1024 / ll_val = §5, 체크포인트 sha·role, last 의 R5-genie 가 best 와 비트 동일). §1 (c) 의 글자 조건: 두 태그의 `results/tables_D2_<tag>.txt` 에 `SITE-SPECIFIC RAY-TRACED TESTBED (prior SRB)` 가 한 번씩 있고 `CLAIM TESTBED -- sparse specular` 는 0 번. `eval_accept.py` 가 검사하지 않는 항목은 읽어 확인했다: raw 이름 `D2_C2_SRB_Nr8_T16_Tp4_dft_snr…` (태그당 448 파일; 파일럿 = DFT), 학습 예산 줄 `N_train=160000`, 저장된 prior·sigma_tag = SRB (§5), 두 태그의 Demo 해시·manifest config_hash 동일. (e) GB′: 이 절을 쓸 때 계산 중(GPU 1, 16:33 CDT ~) — 끝나면 추가 줄로 적는다. 판정점(앵커 b\*, 자동): **−3 / 0 / +3 dB**.

### 6.1 측정 판정 — 표 B `b* → V1` (C2, 태그 SRBB16e4 = `_best`, UNGATED)

| 태그 | 판정점 | a:b (부호검정 p) | pooled | 가드 | 라벨 | SNR@0.1 격차 b\*−V1 [90 % paired] |
|---|---|---|---|---|---|---|
| **SRBB16e4 (판정)** | −3 / 0 / +3 | 209:86 (5.6e-13) · 65:38 (0.01) · 28:5 (6.6e-05) | 302:129 (4.5e-17) | POWERED, second arm fewer 3/3 | **(i) "Sionna RT 방 (내장 `box` 장면 28 GHz, 고정 기지국 한 곳, block split) 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)"** | +0.32 dB [+0.18, +0.45] |
| SRBB16e4last (보고) | −3 / 0 / +3 | 196:103 (8.2e-08) · 70:45 (0.025) · 24:6 (0.0014) | 290:154 (1.1e-10) | POWERED, 3/3 | (같은 문자열, 보고 전용) | +0.28 dB [+0.12, +0.42] |

라벨 문장에 붙는 것(§2): **(1) 유한 풀·한 장소** — 테스트 시행은 테스트 타일 52,353 쌍에서 복원 추출; **(2) 가까운 이웃** — 1 m 타일; 테스트 채널의 0.004 가 학습 집합에 정규화 제곱거리 0.1 안의 이웃을 가짐(판정점 시행에서는 0.004 / 0.005 / 0.007 — 6.2); **(3) 금속 벽·1 차 반사**; **(4) 선택 편향** — BLER 수준이 낮도록 고른 풀. 범위: 이 방·이 기지국·이 split·이 크기 한정. **b\* 는 full 계열 K = 1024 (격자 끝 규칙으로 한 번 확장한 값; §5)** — 이 풀의 GMM 적합은 정상적으로 수렴했다(반복 182, 최고 180). **[감사 S1 — 격자 끝 캐비엇]** full 1024 는 확장한 격자의 끝이고 ll_val 은 거기서도 오르고 있었다(512 대비 +7.795 nat; full 계열의 배증당 증가 +10.1 · +11.0 · +10.1 · +7.8 nat **[정정 2026-10-11 18:58 CDT — FIGHSROOM16e4 기록 감사 S1: 이 수열은 틀렸다. §5 격자의 ll_val 30.445 / 41.698 / 55.912 / 68.085 / 79.119 / 89.214 / 97.009 로 계산한 배증당 증가는 +11.3 · +14.2 · +12.2 · +11.0 · +10.1 · +7.8 nat (16 → 32 → … → 1024) 이다; 틀린 수열은 `audit_ROOM16e4.md` S1 의 오타를 옮긴 것]**) — 등록 규칙에 따라 여기서 멈췄다(§1 "full 1024 한 번 + 캐비엇"). **[감사 N1]** "K = 1024" 는 적합 작업의 이름이다: EM 끝에서 1024 성분 가운데 245 개는 다시 뿌려진 자리채움 성분(π 각 6.24e-6, 합 0.0015)이고 질량의 99.85 % 는 779 성분에 있다(모든 K 에서 같은 현상 — full 512: 82 개, kron 2048: 586 개; §5 의 재시드 수가 그 흔적). 헤드라인·D2·38.901·도시 풀 기록 불변.

대조군 `b* → b*-scalar` (−3 / 0 / +3): 56:94 (0.0024) · 19:50 (0.00024) · 6:14 (0.12), pooled 81:158 (p 7.1e-07), POWERED, second arm fewer 0/3 · first arm (b\*) fewer 2/3 → 라벨 규칙으로 **(ii)** (b\* 가 b\*-scalar 보다 적게 실패); SNR@0.1 격차 (b\* − b\*-scalar) −0.28 dB [−0.39, −0.17]. `R2-ours-G → b*` (앵커 R2, 판정점 0 / +3 / +6): 534:17 · 145:7 · 46:3, pooled 725:27, POWERED, b\* (second arm) 가 3/3 에서 적게 실패; SNR@0.1 격차 (R2 − b\*) +3.09 dB [+2.85, +3.34].

**기전 판독**: 회수율 R (best, paired 90 %): **−3 dB 0.233 [0.187, 0.279]** (b\* 827 / V1 704 / genie 299); 판정점 −3 / 0 / +3 0.233 [0.187, 0.279] / 0.231 [0.100, 0.347] / 0.742 [0.536, 0.930], 합 **0.256 [0.212, 0.299]** (b\* 1020 / V1 847 / genie 344). last: −3 dB 0.176 [0.126, 0.224] (V1 734; `recovery_diff_SRBB16e4.txt`). [감사 N2: best 태그와 같은 도구 `recovery_ci.py` 로는 last 의 CI 가 [0.128, 0.223] (`recovery_SRBB16e4last.txt`).] **1차 ΔR (−3 dB)**: 포화 가드 미발동(b\* BLER@16 −3 dB 0.323 ∈ [0.005, 0.9], b\* 827 > genie 299), undefined 0 → **ΔR = −0.237 [90 % 비짝 −0.302, −0.174] → 등록 라벨 "회수율이 D2 보다 낮다"** (D2 B16e4k −3 dB R 0.470 [0.427, 0.512]; last: −0.294 [−0.363, −0.229]). 2차(보고): 판정점 합 0.256 vs D2 (−3, 0, +3 합) 0.509 → −0.253 [−0.308, −0.196]. 실패 수 격차(−3 dB): V1 − genie 405 [370, 435], b\* − genie 528 [491, 563] (D2: 284 [256, 311], 536 [501, 571]).

### 6.2 보고 전용

**BLER@16 (괄호 = 실패 수 / 2560; best 태그; R0-pilot 은 @1)**

| arm | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|---|---|---|
| **V1** | 0.275 (704) | 0.049 (126) | 0.007 (17) | 0.001 (3) | 0.002 (4) | 0.000 (0) | 0.000 (0) |
| V1 (last 태그) | 0.287 (734) | 0.050 (128) | 0.009 (22) | 0.001 (3) | 0.000 (1) | 0.001 (2) | 0.000 (0) |
| V4 | 0.290 (742) | 0.052 (133) | 0.011 (27) | 0.002 (4) | 0.002 (4) | 0.000 (0) | 0.000 (0) |
| V4b | 0.289 (740) | 0.051 (130) | 0.009 (23) | 0.002 (4) | 0.001 (3) | 0.000 (0) | 0.000 (0) |
| **b\*** | 0.323 (827) | 0.060 (153) | 0.016 (40) | 0.002 (6) | 0.002 (5) | 0.000 (1) | 0.000 (1) |
| b\*-scalar | 0.338 (865) | 0.072 (184) | 0.019 (48) | 0.004 (10) | 0.002 (4) | 0.000 (0) | 0.000 (1) |
| gmm32 | 0.485 (1242) | 0.135 (345) | 0.032 (82) | 0.006 (15) | 0.004 (11) | 0.000 (1) | 0.001 (3) |
| R2-ours-G | 0.658 (1685) | 0.262 (670) | 0.070 (178) | 0.019 (49) | 0.007 (18) | 0.002 (4) | 0.001 (2) |
| R1-turbo | 0.816 (2089) | 0.468 (1198) | 0.159 (406) | 0.042 (108) | 0.017 (44) | 0.004 (10) | 0.002 (6) |
| R0-pilot (@1) | 0.945 (2420) | 0.706 (1807) | 0.336 (860) | 0.124 (318) | 0.055 (140) | 0.021 (53) | 0.007 (17) |
| pilot_C (@16; 문맥) | 0.805 (2061) | 0.364 (931) | 0.096 (246) | 0.027 (69) | 0.008 (21) | 0.003 (7) | 0.001 (3) |
| R4-scvamp | 0.870 (2228) | 0.579 (1482) | 0.270 (690) | 0.118 (301) | 0.058 (149) | 0.029 (73) | 0.008 (21) |
| R3-bigamp | 0.880 (2252) | 0.535 (1369) | 0.248 (634) | 0.149 (382) | 0.114 (291) | 0.134 (342) | 0.129 (331) |
| R4-llr | 0.938 (2401) | 0.849 (2174) | 0.782 (2003) | 0.586 (1500) | 0.364 (931) | 0.207 (531) | 0.107 (273) |
| V0 | 1.000 (2560) | 1.000 (2560) | 1.000 (2559) | 0.999 (2557) | 0.984 (2519) | 0.900 (2304) | 0.654 (1674) |
| **genie** | 0.117 (299) | 0.014 (36) | 0.004 (9) | 0.000 (1) | 0.000 (0) | 0.000 (0) | 0.000 (0) |

- **SNR@0.1** (표 A; dB): genie −2.78 · V1 −1.24 · V4b −1.17 · V4 −1.14 · b\* −0.92 · b\*-scalar −0.64 · gmm32 0.62 · R2-ours-G 2.18 · pilot_C (@16) 2.91 · R1-turbo 4.04 · R4-scvamp 6.69 · R0-pilot (@1) 6.79; R3-bigamp · R4-llr · V0 는 "> 15". 표 B 의 격차: `V1 → genie` +1.54 dB [+1.38, +1.73], `b* → genie` +1.86 dB [+1.68, +2.05].
- **V4 · V4b · V0 (앵커 b\*, −3 / 0 / +3)**: `b* → V4` 200:115 (1.9e-06) · 66:46 (0.072) · 23:10 (0.035), pooled 289:171, second arm fewer 2/3 (격차 +0.23 dB); `b* → V4b` 201:114 · 66:43 · 24:7, pooled 291:164, 3/3 (+0.25 dB); `b* → V0` 0:1733 · 0:2407 · 0:2519, pooled 0:6659, first arm (b\*) fewer 3/3. 판정점 3 점 실패 수 합: V1 847 / V4 902 / V4b 893; 7 SNR 합: V1 854 / V4 910 / V4b 900 (검정 없음).
- **`V1 → genie`** (앵커 genie; 범위 안 SNR 이 −3 · 0 dB 둘뿐 → UNDECIDED): 427:22 · 95:5, pooled 522:27. `b* → genie`: 552:24 · 127:10, pooled 679:34 (UNDECIDED).
- **best 대 last V1 짝 부호검정** (−3 / 0 / +3; a = best 만 실패, b = last 만 실패): 45:75 (p 0.00785) · 20:22 (0.878) · 4:9 (0.267), pooled 69:106 (p 0.00634) — best 가 last 보다 적게 실패(유의).
- **F3 가드 발동률** (`results/guard_D2_SRBB16e4{,last}.txt`): V0 — best −3 … +15 dB 0.997 / 0.998 / 0.994 / 0.984 / 0.950 / 0.851 / 0.668, last 0.988 / 0.990 / 0.960 / 0.946 / 0.514 / 0.633 / 0.084. V0 밖의 발동 없음. 한 번도 발동하지 않은 arm 12 개: M-ours-bstar, M-ours-bstar-scalar, M-ours-dscore-C-V1, M-ours-dscore-C-V4, M-ours-dscore-C-V4b, M-ours-gmm32, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp.
- **동일예산 GB′**: 계산 중(`run_srb_post_gpu.sh 1 GBP 1`, GPU 1, 10-11 16:33 CDT ~) — 끝나면 추가 줄로 적는다.
- **누수 층화** (보고 전용; `code/dmc_leak_strata.py --tag SRBB16e4 --prior SRB`, 10-11 16:29 CDT 실행 → `SRBB16e4_leak_strata.txt`; 정렬 OK). d < 0.1 인 시행은 판정점마다 11 / 12 / 19 개뿐이라(비율 0.004 / 0.005 / 0.007) 도구가 R 을 적지 않았다; d ≥ 0.1: −3 dB 2549: 824 / 701 / 297 → 0.233, 0 dB 2548: 152 / 124 / 35 → 0.239, +3 dB 2541: 40 / 16 / 9 → 0.774, 3 점 합 7638: 1016 / 841 / 341 → 0.259 (n: b\* / V1 / genie 실패 수 → 점추정 R). d 중앙값 0.3445 / 0.3443 / 0.3346.
- **랭크 층화** (보고 전용; `code/rank_strata.py --tag SRBB16e4 --prior SRB` → `SRBB16e4_rank_strata.txt`; 정렬 OK). 칸 = n (비율): genie / V1 / b\* 의 BLER@16 (실패 수):

| SNR | ≥ 0.95 | 0.80–0.95 | 0.60–0.80 | < 0.60 |
|---|---|---|---|---|
| −3 dB | 81 (0.032): 0.321 / 0.481 / 0.580 (26 / 39 / 47) | 1337 (0.522): 0.123 / 0.291 / 0.341 (165 / 389 / 456) | 1021 (0.399): 0.082 / 0.227 / 0.272 (84 / 232 / 278) | 121 (0.047): 0.198 / 0.364 / 0.380 (24 / 44 / 46) |
| 0 dB | 80 (0.031): 0.150 / 0.287 / 0.325 (12 / 23 / 26) | 1335 (0.521): 0.010 / 0.049 / 0.061 (14 / 65 / 81) | 1054 (0.412): 0.009 / 0.035 / 0.039 (10 / 37 / 41) | 91 (0.036): 0.000 / 0.011 / 0.055 (0 / 1 / 5) |
| +3 dB | 92 (0.036): 0.065 / 0.087 / 0.174 (6 / 8 / 16) | 1334 (0.521): 0.002 / 0.005 / 0.012 (3 / 7 / 16) | 1051 (0.411): 0.000 / 0.002 / 0.007 (0 / 2 / 7) | 83 (0.032): 0.000 / 0.000 / 0.012 (0 / 0 / 1) |

### 6.3 baseline — 표 B `X → V1`: 새 라벨 15 개 + 주 라벨 1 개 (C2, prior SRB, UNGATED; 앵커 = X, R0-pilot 은 @1)

**실행·운영 기록**: `bash code/run_srb_base.sh d2sx_SRB_N160000_a1 ed437f21af15c305 4c6da315c701b9d4 e0adb06cce792093 gmm1024 - 97.00871495382869` (= §5 의 인자 원문) **한 번**, tmux `srbbase`, 10-11 16:18 CDT 시작(git 7d524638; `DEFER_ALD` 스위치 없이). PIL runner 1.4 분 → 16:19 CDT `ACCEPT: OK -- PILSRB`, `pair_cross` 무결성 OK(raised 0 / 0) → ALD 시험 사이트 재생성(CPU) → ALD 추정 GPU 1 (16:20 CDT; `results/ald/ald_PILSRB.npz` sha256[:16] a3d249188f9c061a) → ALD runner 0.4 분 → 16:21 CDT `ACCEPT: OK -- ALDSRB`, `pair_ald` 무결성 OK → pick 규칙 재현(`rule-reproduced=True`, 메모리 필요 ≈ 264 GB / 가용 1028 GB) → SP runner 10.4 분 → `meta|sparse` 불일치 0, raised 0 / 0 / 0 → 16:31 CDT `ACCEPT: OK -- SPSRB` → `pair_baselines` rc 0 → 16:32 CDT `SRB_BASE_DONE rc=0`. raw 마다 깨끗한 커밋 하나: `pair_baselines` 머리말 `git base=9ad4caa0 extra0=7d524638 pil=7d524638 ald=7d524638; integrity: OK`. 커밋 7d524638 은 `PRIOR_EVAL_DONE` 뒤·baseline 시작 전에 PATH16e4 의 §6·감사·그림과 이 주 실행의 결과 파일을 더한 것이다(`git diff 9ad4caa0 7d524638 -- conf/code Demo` 비어 있음).

| X | 판정점 [dB] | a:b (X 만 실패 : V1 만 실패) | pooled (p) | 가드 · 유의 점 수 | 라벨 | F_X − F_V1 (−3 dB) | R_X (−3 dB) [90 %] | R_X (판정점 합) [90 %] |
|---|---|---|---|---|---|---|---|---|
| b\* (주 라벨, 6.1) | -3 / +0 / +3 | 209:86 · 65:38 · 28:5 | 302:129 (4.5e-17) | POWERED, V1 3/3 · X 0/3 | **(i)** | 123 | 0.233 [0.187, 0.279] | 0.256 [0.212, 0.299] |
| b\*-scalar | -3 / +0 / +3 | 243:82 · 94:36 · 36:5 | 373:123 (2.7e-30) | POWERED, V1 3/3 · X 0/3 | **(i)** | 161 | 0.284 [0.241, 0.328] | 0.332 [0.292, 0.373] |
| gmm32 | -3 / +0 / +3 | 581:43 · 244:25 · 68:3 | 893:71 (8.6e-182) | POWERED, V1 3/3 · X 0/3 | **(i)** | 538 | 0.571 [0.543, 0.601] | 0.620 [0.596, 0.646] |
| R0-pilot@1 | +3 / +6 / +9 | 843:0 · 315:0 · 136:0 | 1294:0 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1716 | 정의 안 됨 (범위 밖: 0.9453) | 0.989 [0.983, 0.995] |
| R1-turbo | +0 / +3 / +6 | 1075:3 · 391:2 · 106:1 | 1572:6 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1385 | 0.774 [0.757, 0.792] | 0.940 [0.930, 0.950] |
| R2-ours-G | +0 / +3 / +6 | 555:11 · 164:3 · 47:1 | 766:15 (2.6e-204) | POWERED, V1 3/3 · X 0/3 | **(i)** | 981 | 0.708 [0.686, 0.731] | 0.882 [0.863, 0.901] |
| R3-bigamp | +9 / +12 / +15 | 288:1 · 342:0 · 331:0 | 961:1 (4.9e-287) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1548 | 0.793 [0.777, 0.809] | 0.996 [0.992, 0.999] |
| R4-llr | +9 / +12 / +15 | 927:0 · 531:0 · 273:0 | 1731:0 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1697 | 정의 안 됨 (범위 밖: 0.9379) | 0.998 [0.996, 0.999] |
| R4-scvamp | +3 / +6 / +9 | 674:1 · 298:0 · 145:0 | 1117:1 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1524 | 0.790 [0.774, 0.808] | 0.988 [0.981, 0.994] |
| bstar-pilot | -3 / +0 / +3 | 535:43 · 138:26 · 28:4 | 701:73 (1.1e-129) | POWERED, V1 3/3 · X 0/3 | **(i)** | 492 | 0.548 [0.518, 0.580] | 0.555 [0.527, 0.584] |
| V1-pilot | -3 / +0 / +3 | 417:34 · 92:23 · 9:4 | 518:61 (2.8e-91) | POWERED, V1 2/3 · X 0/3 | **(i)** | 383 | 0.486 [0.455, 0.520] | 0.476 [0.446, 0.508] |
| ALD-pilot | -3 / +0 / +3 | 657:45 · 181:20 · 41:3 | 879:68 (1.5e-180) | POWERED, V1 3/3 · X 0/3 | **(i)** | 612 | 0.602 [0.575, 0.631] | 0.617 [0.593, 0.642] |
| ALDv-pilot | -3 / +0 / +3 | 652:41 · 171:26 · 29:2 | 852:69 (1.8e-172) | POWERED, V1 3/3 · X 0/3 | **(i)** | 611 | 0.601 [0.574, 0.630] | 0.609 [0.585, 0.635] |
| SBL-loop | -3 / +0 / +3 | 760:41 · 398:14 · 113:4 | 1271:59 (3.5e-297) | POWERED, V1 3/3 · X 0/3 | **(i)** | 719 | 0.640 [0.614, 0.667] | 0.707 [0.686, 0.728] |
| SBL-pilot | -3 / +0 / +3 | 1089:19 · 536:12 · 122:2 | 1747:33 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1070 | 0.725 [0.706, 0.747] | 0.773 [0.757, 0.790] |
| OMP-pilot | +0 / +3 / +6 | 771:9 · 273:2 · 75:2 | 1119:13 (2.6e-311) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1220 | 0.751 [0.733, 0.771] | 0.917 [0.903, 0.931] |

- 표의 pooled p "(0)" 은 도구의 `%.2g` 출력이 언더플로한 것이다(실제 값 < 1e-300).
- **요약 줄(원문)**: `SUMMARY-B (baselines without b*, 15): (i) 15, (ii) 0, not decided 0; b* -> V1 (i)` · `SUMMARY registered baselines 16 (b* + 𝔅 15): (i) 16, (ii) 0, not decided 0`.
- **"전부" 문장 (§2 조건 충족: 주 라벨 (i) 이고 15 개 모두 (i))**: **"Sionna RT 방 (내장 `box` 장면 28 GHz, 고정 기지국 한 곳, block split) 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)"**.
- **"멀어진다" 문장 (조건 충족)**: `'등록된 baseline 전부와 멀어진다' condition (k = 16, (ii) = 0, R_X* CI lower > 0): MET` — `X* (fewest -3 dB failures, ties by name) = M-ours-bstar (F=827); R_X* -3 dB = 0.233 [90% 0.187, 0.279]` → **"… 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다 (UNGATED 측정)"**. 여기서 가장 가까운 baseline X\* 는 GMM prior(b\*) 자신이다.
- 두 문장 모두 6.1 의 캐비엇과 §1 고유 사항 (6)(baseline 조정용 개발 채널이 테스트 풀에서 나옴)을 붙여서만 쓴다. 범위: 이 방·이 기지국·이 split·이 크기 한정; 동치 문구·일반화 문장은 쓰지 않는다.
- **드리프트 검사**: `b* → V1` 을 `pair_baselines` 가 다시 낸 값(209:86 · 65:38 · 28:5, pooled 302:129, (i), R(−3 dB) 0.233 [0.187, 0.279], 판정점 합 0.256 [0.212, 0.299]) = 6.1 → 드리프트 없음.
- R_X(−3 dB) 는 X 의 −3 dB BLER 이 0.9 를 넘는 **2 개**(R0-pilot@1 0.9453 · R4-llr 0.9379)에서 정의되지 않는다(포화 가드); 나머지 14 개는 정의된다. `V1-pilot` 은 (i) 이지만 유의한 점은 2/3 (+3 dB 9:4, p 0.27).

### 6.4 원고 범례 11 곡선 — BLER@16 실패 수 / 2560 (`pairB_SPSRB.txt` 의 표; 전 SNR n = 2560)

| 곡선 | −3 | 0 | +3 | +6 | +9 | +12 | +15 dB |
|---|---|---|---|---|---|---|---|
| Proposed (V1) | 704 | 126 | 17 | 3 | 4 | 0 | 0 |
| Annealed Langevin (plug-in) = ALD-pilot | 1316 | 287 | 55 | 11 | 3 | 2 | 0 |
| GMM prior = b\* | 827 | 153 | 40 | 6 | 5 | 1 | 1 |
| Gaussian prior = R2-ours-G | 1685 | 670 | 178 | 49 | 18 | 4 | 2 |
| Turbo LMMSE = R1-turbo | 2089 | 1198 | 406 | 108 | 44 | 10 | 6 |
| BiG-AMP = R3-bigamp | 2252 | 1369 | 634 | 382 | 291 | 342 | 331 |
| Pilot-only LMMSE = R0-pilot@1 | 2420 | 1807 | 860 | 318 | 140 | 53 | 17 |
| SBL (in loop) | 1423 | 510 | 126 | 22 | 7 | 3 | 4 |
| SBL (pilot-only) | 1774 | 650 | 137 | 35 | 12 | 4 | 2 |
| OMP (pilot-only) | 1924 | 888 | 288 | 76 | 39 | 8 | 6 |
| Perfect CSI = genie | 299 | 36 | 9 | 1 | 0 | 0 | 0 |

- 11 곡선에 없는 등록 arm (같은 순서): V1-pilot 1087 / 195 / 22 / 6 / 3 / 0 / 0; bstar-pilot 1196 / 238 / 41 / 6 / 6 / 1 / 1; ALDv-pilot 1315 / 271 / 44 / 9 / 5 / 1 / 0; M-ours-bstar-scalar 865 / 184 / 48 / 10 / 4 / 0 / 1; M-ours-gmm32 1242 / 345 / 82 / 15 / 11 / 1 / 3; R4-scvamp 2228 / 1482 / 690 / 301 / 149 / 73 / 21; R4-llr 2401 / 2174 / 2003 / 1500 / 931 / 531 / 273.
- 그림: `conference/figures/F21srb_col.{pdf,png}` (`paper_f21dmc.py SRB`, 기록 `records/paper_f21srb.txt`): 실패 수 = 위 표(assert), 세 raw 의 Perfect CSI 오류 배열 동일(assert), y 축 (3e-05, 1.2) (0 실패 점이 있어서), 0 실패 점 6 개(Proposed +12 · +15, Annealed Langevin +15, Perfect CSI +9 · +12 · +15 dB)에서 곡선이 끊김. 그려진 baseline 9 개의 라벨 모두 (i). **점추정으로 제안 곡선 이하인 baseline 점이 있다**(기록 파일의 해당 줄 원문 그대로: Annealed Langevin (plug-in) at +9 dB (3 vs 4), +15 dB (0 vs 0)) — 높은 SNR 에서 실패가 몇 건뿐인 점들이며, 등록된 판정은 판정점의 짝 검정이다.
- **NMSE CDF** (보고 전용): `conference/figures/F33cdf_SRB_wide.{pdf,png}` (`paper_f33cdf.py SRB`, 기록 `records/paper_f33cdf_SRB.txt`): 패널 −3 · 0 · +3 · +6 dB, 곡선 10 개, 2560 시행 전부(비유한·비양수 0 건). −3 dB 의 중앙값 10 log10 NMSE [dB]: Proposed −14.39 · GMM prior −12.43 · Annealed Langevin (plug-in) −8.44 · Gaussian prior −6.17 (나머지는 기록 파일).

### 6.5 baseline 보고 전용

- `pair_PILSRB.txt`: P1 `V1-pilot → V1` 417:34 · 92:23 · 9:4, pooled 518:61 → (i) (2/3); P2 `bstar-pilot → V1-pilot` 208:99 · 96:53 · 24:5, pooled 328:157 → (i); `bstar-pilot → b*` 410:41 · 107:22 · 15:14, pooled 532:77 → (i) (2/3); `V1-pilot → b*` 365:105 · 88:46 · 6:24, pooled 459:175 → (i) (b\* 가 2/3 에서 적게 실패; +3 dB 는 V1-pilot 이 적게 실패).
- `pair_ALDSRB.txt`: A1 `ALDv-pilot → V1` 652:41 · 171:26 · 29:2 → (i); A2 `ALD-pilot → V1` 657:45 · 181:20 · 41:3 → (i); A3 `ALDv-pilot → V1-pilot` 342:114 · 123:47 · 28:6, pooled 493:167 → (i); `ALDv-pilot → b*` 562:74 · 161:43 · 27:23, pooled 750:140 → (i) (2/3); `bstar-pilot → ALDv-pilot` 178:297 · 86:119 · 19:22, pooled 283:438 → (ii) (bstar-pilot 이 2/3 에서 적게 실패); `ALD-pilot → ALDv-pilot` 44:43 · 39:23 · 13:2, pooled 96:68 → (iii). 시험 ALD NMSE(추정 파일 평균) −7.22 / −11.11 / −14.34 / −17.17 / −19.66 / −22.15 / −24.36 dB.
- 조정 표: §5 (SBL ρ 16 · OMP ρ 16 — 둘 다 격자 끝 + 캐비엇; ALD c 0.01 · β 0.005).
- raised trials: PIL 0 / 0, ALD 0, SP 0 / 0 / 0.

### 6.6 §3 예측 채점 — SRB (적중 / 빗나감; 범위 밖은 채점 불가; DMI 는 실행하지 않아 채점 없음)

1. 표 B (i) → 결과 (i) → **적중**.
2. 판정점 −3 / 0 / +3 dB 이고 POWERED → **적중**.
3. Perfect CSI 의 BLER 수준: 관측됨(채점 제외).
4. 1차 ΔR 의 포화 가드 미발동 → **적중** (b\* BLER(−3 dB) 0.323, b\* 827 > genie 299).
5. R(−3 dB) 의 90 % CI 하한 > 0 → **적중** (0.187).
6. `R2-ours-G → b*` b\* 가 ≥ 2/3 점에서 적게 실패 → **적중** (3/3).
7. V1 과 b\* 의 SNR@0.1 이 둘 다 숫자 → **적중** (−1.24 · −0.92 dB); 격차(b\* − V1) > 0 dB → **적중** (+0.32 dB [+0.18, +0.45]).
8. GB′ median ≤ 0.90 → **채점 보류** — GB′ 계산이 끝나면 추가한다.
9. 학습(patience · epoch ∈ [300, 1500]) → **빗나감** (§5: patience ✓, epoch 1680 ✗).
10. b\* = kron 계열, K ≥ 1024 → **빗나감** (§5: b\* = full 1024).
11. V0: −3 dB 가드 발동률 ≥ 0.5 이고 BLER ≥ 0.9 → **적중** (0.997 · 1.000). best 대 last V1 판정하지 못함(pooled p > 0.05) → **빗나감** (pooled 69:106, p 0.00634).
12. 대조군 `b* → b*-scalar` (iii) → **빗나감** (POWERED, b\* 가 2/3 에서 적게 실패 → (ii)).
13. baseline — 세 문장: "(ii) 0 이고 (i) ≥ 12" → **적중** ((ii) 0, (i) 15 / 15); `pair_ALDSRB.txt` A3 = (i) → **적중**; −3 dB 실패 수 `SBL-pilot` < `R0-pilot@1` → **적중** (1774 < 2420).
14. 랭크 층화: 관측됨(채점 제외). 15. 예측 없음.
16. 빗나갈 경로: (e) b\* 가 full 512 → full 1024 한 번 + 캐비엇 — **발동**(§5). (a)(b)(c)(d)(f) 미발동((i); R > 0; POWERED; 발산 없음; baseline 에 (ii) 없음).

### 6.7 등록 대비 공개 사항 (수치·판정 불변)

- **DMI 는 사용자 결정으로 실행 전 철회**(§5): 이 등록의 두 prior 가운데 SRB 만 실행됐다.
- 동결(b737fd55) 뒤·SRB 의 BLER 전의 `conf/code`·`Demo` 변경: PATH16e4 (SRP) 를 위한 추가(`srp_build.py`, `path_strata.py`, `run_srp_*.sh`, PID 15 등 연결 — ce5fdacc · 45c4ae07 · 99039ef5)와 `run_srb_eval.sh` 의 인자(9ad4caa0). SRB 의 수신기 경로를 바꾸는 변경은 없다(기존 prior 의 비트 동일 검사는 PATH16e4 §0; SRB 의 train sha 불변 — 같은 곳).
- 주 실행과 baseline 실행은 각각 한 번 돌았고 재실행·중단·재개가 없다(`logs/run_D2_SRBB16e4{,last}.log` 각 448 done, exists 줄 없음; `run_srb_base.log` 의 시작 줄 하나). 이 로그들은 git 밖이다.
- 큐 조작(정지 파일 두 번, SRP 작업을 맨 앞에, DMI 작업 제거)과 full 1024 추가 적합은 §5 에 적은 그대로다.
- 보고 전용 층화 둘(누수·랭크)은 baseline runner 가 도는 동안 돌렸다(주 실행의 raw 만 읽는다).
- 이 §6 은 PATH16e4 (SRP) 의 결과·감사를 모두 본 뒤에 썼다 — 이 절의 수치는 모두 SRB 의 파일에서 나온다.
- GB′ 는 이 절을 쓸 때 계산 중이었다 — 수치·수용 (e)·예측 8 은 추가 줄로 적는다.

### 6.8 기록 감사 (Fable 5.1 서브에이전트, 보고서 파일 mtime 2026-10-11 17:01 CDT; `prereg_audit_2026-10-11/audit_ROOM16e4.md`, 재계산 `recompute_room_{main,base,s5,strata}.py` → `.out`, 등록 도구 재실행 `rerun_room_*.txt`)

감사 대상 = 커밋 f183160d 의 §5 (SRB; DMI 철회)·§6. §1–§3 은 동결 b737fd55 와 바이트 동일(감사 확인). 독립 재계산(raw 청크를 자체 판독기로 직접 읽음): 자동 비교 **1,048 값(328 + 466 + 194 + 60)**, 불일치로 찍힌 7 줄은 감사 스크립트 쪽 문제이거나 기록이 이미 밝힌 사항이고 기록의 오류가 아니다. **주 라벨과 baseline 표의 16 라벨 모두 재현**: `b* → V1` (i) (두 태그; 판정점 −3 / 0 / +3, POWERED, 3/3; 209:86 · 65:38 · 28:5, pooled 302:129; last 290:154), 대조군 `b* → b*-scalar` (ii) (첫 arm b\* 가 −3 · 0 dB 에서 유의하게 적게 실패 — 예측 12 는 빗나감이 맞다), `V1 → genie` · `b* → genie` 는 genie 의 +3 dB BLER 이 9/2560 = 0.0035 < 0.005 라 UNDECIDED; baseline 16 행의 a:b · p · 라벨 · F_X − F_V1 · R_X · CI, 15/15 · 16/16, X\* = M-ours-bstar (F 827), R_X\* 0.233 [0.187, 0.279] > 0 → "전부"·"멀어진다" 조건 충족; 6.2 · 6.4 표, SNR@0.1 과 격차, F3 가드, 회수율·ΔR (감사의 별도 재표집 [−0.299, −0.176] — 결론 같음), 층화 표, 그림 기록, 수용·manifest·raw 당 깨끗한 커밋 하나·R5-genie 비트 동일(raw 다섯)·`meta|sparse` == pick, 시각표(실행 중 커밋 없음), DMI 철회(DMI 적합·BLER 파일 없음), 코드 diff 진술, 6.6 채점(너그러운 채점 없음). 등록 도구 재실행: `eval_accept` × 4 → `ACCEPT: OK`; `recovery_ci` · `frontier_ci` · `pair_cross` · `pair_ald` · `pair_baselines` → 기록의 파일과 머리말 날짜·git 줄 말고 바이트 동일. **평가된 b\* 는 실제로 수렴한 full 공분산 K = 1024 EM 적합이다**(학습 우도가 181 단계 내내 단조 증가 −48.6 → 100.43, it_best 180, 학습 우도 허용 오차 규칙으로 정지, 학습−검증 3.4 nat, Gaussian 대비 +161 nat; 격자의 다른 적합도 모두 수렴 — SRP 와 반대).

**MUST 0 · SHOULD 2 · NIT 8 — 모두 반영(수치·라벨 불변; 기록 2026-10-11 17:03 CDT, Opus 5.5)**: **S1** 격자 끝 캐비엇을 6.1 의 라벨 문단에 직접 적음(제자리 표시); **S2** full 1024 뒤 재선택의 실제 명령과 손으로 쓴 `.sel` 의 출처를 §5 에 적음(제자리 표시); N1 살아 있는 성분 수(6.1); N2 last 태그 CI 의 도구(6.1); N3 `logs/train_d2sx_SRB_N160000_a1.log` 에는 16:33 CDT 의 둘째 머리말이 있다 — GB′ 단계(`run_srb_post_gpu.sh 1 GBP 1` → `run_d2_sx.py` 재개)가 학습기를 다시 열어 "no epoch trained … left untouched" 를 남긴 것이고(1.6 s) 체크포인트의 mtime·sha 는 그대로다; N4 SRP 의 GB′ 가 돈 구간(6 머리말); N5 `raw_DMI/` 와 `raw_SRB/` 는 σ 격자 단계가 등록 전에 만든 **빈 디렉토리**다 — BLER 실행이 아니다(`results/sparse/{pick,tune}_DMI_C2.json` 은 있고 한 번도 쓰이지 않았다); N6 GB′ → 6.9; N7 `wall_sec` 는 `tune_SRB_C2.json`, git 은 `sparse_tune.log` 에 있다(pick JSON 에는 없음); N8 그려진 baseline 가운데 점추정이 제안 곡선 이하인 점은 정확히 ALD-pilot +9 dB (3 대 4) · +15 dB (0 대 0) 둘이다(6.4 그대로). 감사가 확인하지 않은 것: GB′(당시 보류), 층화 스크립트 안의 시행 재생(인쇄된 정렬 검사와 산술만), §0 의 통계, "작성자는 … 보지 않았다" 진술과 tmux 세션 이름.

### 6.9 추가 줄 — GB′ (2026-10-11 17:03 CDT; 6.2 · 6.6 · 6.7 에서 미뤄 둔 것)

- **동일예산 GB′** (`run_srb_post_gpu.sh 1 GBP 1`, GPU 1, 10-11 16:33 → 16:40 CDT, rc 0; `logs/gbprime_SRBB16e4.log`, last 파일 `d2sx_SRB_N160000_a1.pt`; `results/d2_gbprime_SRB_N160000_a1.npz`): median **0.6472** (min 0.5949 · **max 5.1046**; SRP 0.5836 · D3 0.559 · Sionna RT 도시 0.543 · DeepMIMO 도시 0.715 · UMi28 0.920 과 나란히). 잡음 수준 20 개 가운데 18 개에서 비 < 1 이고, 가장 큰 두 수준에서 1 을 넘는다: σ 0.720 에서 1.017 (모델 NMSE 0.2301 대 GMM 0.2263), **σ 0.855 (격자 끝)에서 5.105 (모델 1.514 대 GMM 0.297)**. (SRP 는 20 개 모두 < 1, max 0.913.) **수용 (e)**: 로그의 `GMM b* = gmm1024 (full K=1024) @N=160000` = §5 최종 b\* ✓, `d2_gbprime_SRB_N160000_a1.npz` mtime 10-11 16:40:45 CDT > full 1024 적합 파일 mtime 14:49:46 CDT ✓ → GB′ 수치 유효.
- **예측 8** (GB′ median ≤ 0.90) → **적중** (0.6472).
- 이 줄은 기록 감사(6.8) 뒤에 추가했다 — 감사는 GB′ 를 "보류" 로만 확인했다(감사 N6: 파일이 생긴 것과 (e) 의 두 조건은 봤고 채점은 하지 않았다).

### 6.10 추가 줄 — 사후 진단과 그림 보강 (2026-10-11 17:03 CDT; 등록 밖·보고 전용, 판정·라벨 불변)

- **사후 진단** (사용자 질문 "proposed 보면 6dB에서 BLER가 9 dB 보다 낮게 나오는데 좀 이상하지 않아?" 뒤; `prereg_audit_2026-10-11/highsnr_fail_SRB.py` → `SRBB16e4_highsnr_fail.txt`, 커밋 1404d315; 주 실행의 raw 만 읽는다): V1 의 BLER@16 실패는 +6 dB 3 건(시행 818 · 1737 · 2421) · +9 dB 4 건(177 · 1000 · 1528 · 2346) · +12 · +15 dB 0 건 / 2560. 그 7 시행의 최대 특이값 에너지 비중은 0.914 · 0.938 · 0.933 / 0.917 · 0.816 · 0.930 · 0.922 (전체 시행의 중앙값 0.82), 7 시행 모두 같은 시행에서 다른 arm 도 실패했고(b\* · R2-ours-G · V4 · genie 가운데 둘 이상), V1 의 반복별 실패 수는 줄기만 한다(+6 dB 77 → 15 → 4 → 3 → 3, +9 dB 33 → 6 → 5 → 4 → 4; 반복 1 · 2 · 4 · 8 · 16). 이 두 점은 판정점(−3 / 0 / +3 dB)이 아니다.
- **그림 보강** (사용자 지시 "figure는 매끄러운 곡선이 나타나는게 좋아"): +6 / +9 / +12 / +15 dB 점을 새 시행 n = 20480 으로 다시 재는 보고 전용 실행은 별도 문서 `NEXT_EXPERIMENTS_FIGHSROOM16e4.md` (v2 = 실행 커밋 193776a1, 10-11 17:01 CDT 시작)에 등록했다. 이 문서의 판정·라벨·6.4 의 표와 그림 `F21srb_col` 은 그대로 남고, 보강 그림은 `F21srbhs_col` 이라는 다른 파일이다.

## 7. 결과 — DMI (주 실행 2026-10-12 16:15~17:54 CDT, `run_prior_eval.sh` @4131a3b0 = 5-DMI 커밋; baseline 17:56~18:15 CDT, `run_dmi_base.sh` @29cf411d; 이 절은 추가만 한다; 기록 2026-10-12 18:19 CDT, Opus 5.5 — 전사만, 해석 없음)

수치의 출처: 생성기 `prereg_audit_2026-10-11/s6_gen.py DMIB16e4` 와 `s6_base_gen.py pairB_SPDMI.txt` (표 B 줄은 `results/tables_D2_DMIB16e4{,last}.txt`·`pairB_SPDMI.txt` 원문, 실패 수·BLER 은 raw 를 `analysis.load_raw` 로 읽음, 회수율·ΔR·수용·가드는 각 파일 원문). §6 (SRB) 과 같은 틀이다; §1~§3 은 동결 b737fd55 그대로.

**실행·운영 기록**: `code/run_dmi_eval.sh` (= 5-DMI 의 인자 원문) 한 번, tmux `dmieval`, `taskset -c 24-47,120-143,72-95,168-191` (CPU 96 스레드 — 사용자 지시; runner 는 192 워커를 만들고 96 스레드를 나눠 쓴다), 10-12 16:15 CDT 시작(git 4131a3b0 = 5-DMI 커밋, `conf/code` clean). 측정 태그 `DMIB16e4` (`_best`) 16:15 → 17:02 CDT (runner 46.6 분), 보고 태그 `DMIB16e4last` 17:02 → 17:53 CDT (49.9 분), 각각 448 작업; 수용 검사 17:53 CDT, `PRIOR_EVAL_DONE` 17:54 CDT. manifest `run_manifest_DMIB16e4{,last}.json` 둘 다 git 4131a3b0 · config_hash 76399fb1c7f57517. 실행 중 main 커밋 없음(다음 커밋 29cf411d 는 `PRIOR_EVAL_DONE` 뒤). 함께 돈 것(결과 중립): DMI 의 GB′ (GPU 0, `taskset -c 20,116`, 16:16 → 16:24 CDT; 수신기는 CPU). 주 실행이 도는 동안 작성자는 DMI 의 진행 줄·결과를 보지 않았다(시작 직후의 runner 머리말 세 줄과 종료 표식만).

**수용 검사**: **`ACCEPT: OK -- DMIB16e4, DMIB16e4last`** (`results/review_next/DMIB16e4_accept.txt`; `eval_accept.py` rc 0 — 격자 full 7 (16 … 1024) + kron 8 (16 … 2048), 청크 {(40k, 40)} × 7 SNR, meta ntrain 160000 / bstar gmm1024 / ll_val = 5-DMI, 체크포인트 sha·role, last 의 R5-genie 가 best 와 비트 동일). §1 (c) 의 글자 조건: 두 태그의 `results/tables_D2_<tag>.txt` 에 `SITE-SPECIFIC RAY-TRACED TESTBED (prior DMI)` 가 한 번씩, `FIVE frozen UE yaws per position` 이 한 번씩 있고 `CLAIM TESTBED -- sparse specular` 와 `FIVE fixed` 는 0 번. `eval_accept.py` 가 검사하지 않는 항목은 읽어 확인했다: raw 이름 `D2_C2_DMI_Nr8_T16_Tp4_dft_snr…` (태그당 448 파일; 파일럿 = DFT), 학습 예산 줄 `N_train=160000`, 두 태그의 Demo 해시·manifest config_hash 동일; `dmimo.py selfcheck 8 DMI` → `OK (DMI) | pools fit 273305 val 20000 test 60700 | train sha 3380177f4c38cf57` (= §0; 이 절을 쓰면서 한 번 실행). (e) GB′: 7.2. 판정점(앵커 b\*, 자동): **−3 / 0 / +3 dB**.

### 7.1 측정 판정 — 표 B `b* → V1` (C2, 태그 DMIB16e4 = `_best`, UNGATED)

| 태그 | 판정점 | a:b (부호검정 p) | pooled | 가드 | 라벨 | SNR@0.1 격차 b\*−V1 [90 % paired] |
|---|---|---|---|---|---|---|
| **DMIB16e4 (판정)** | −3 / 0 / +3 | 178:122 (0.0015) · 72:48 (0.035) · 13:9 (0.52) | 263:179 (7.5e-05) | POWERED, second arm fewer 2/3 | **(i) "DeepMIMO 실내 (`i1_2p4` 2.4 GHz, 고정 기지국 한 곳, block split) 에서 V1 이 b\* 보다 적게 실패 (prior·기전 축 측정, UNGATED)"** | +0.23 dB [+0.08, +0.37] |
| DMIB16e4last (보고) | −3 / 0 / +3 | 184:114 (6e-05) · 74:49 (0.03) · 14:9 (0.4) | 272:172 (2.4e-06) | POWERED, 2/3 | (같은 문자열, 보고 전용) | +0.24 dB [+0.11, +0.39] |

라벨 문장에 붙는 것(§2): **(1) 유한 풀·한 장소** — 테스트 시행은 테스트 타일 60,700 쌍에서 복원 추출; **(2) 가까운 이웃** — 0.5 m 타일(2.4 GHz 에서 4 λ), 같은 위치를 yaw 만 바꿔 5 번 쓴다; 테스트 채널의 0.058 이 학습 집합에 정규화 제곱거리 0.1 안의 이웃을 가짐(§0 TDMh; 판정점 시행에서는 0.074 / 0.066 / 0.064 — 7.2); **(4) 선택 편향** — BLER 수준이 낮도록 고른 풀. ((3) 은 SRB 에만.) 범위: 이 방·이 기지국·이 split·이 크기 한정. **b\* 는 full 계열 K = 1024 (격자 끝 규칙으로 한 번 확장한 값; 5-DMI)** — **격자 끝 캐비엇**: 확장한 격자의 끝이고 ll_val 은 거기서도 오르고 있었다(512 대비 +6.192 nat) — 등록 규칙에 따라 여기서 멈췄다(§1 "full 1024 한 번 + 캐비엇"). 유의한 점은 3 점 중 2 점이다(+3 dB 13:9, p 0.52). 헤드라인·D2·38.901·도시 풀·SRB·SRP 기록 불변.

대조군 `b* → b*-scalar` (−3 / 0 / +3): 48:71 (0.043) · 11:36 (0.00035) · 5:6 (1), pooled 64:113 (p 0.00028), POWERED, second arm fewer 0/3 · first arm (b\*) fewer 2/3 → 라벨 규칙으로 **(ii)** (b\* 가 b\*-scalar 보다 적게 실패); SNR@0.1 격차 (b\* − b\*-scalar) −0.21 dB [−0.31, −0.12]. `R2-ours-G → b*` (앵커 R2, 판정점 −3 / 0 / +3): 1074:35 · 680:15 · 173:5, pooled 1927:55, POWERED, b\* (second arm) 가 3/3 에서 적게 실패; SNR@0.1 격차 (R2 − b\*) +3.13 dB [+2.89, +3.38].

**기전 판독**: 회수율 R (best, paired 90 %): **−3 dB 0.099 [0.050, 0.146]** (b\* 885 / V1 829 / genie 321); 판정점 −3 / 0 / +3 0.099 [0.050, 0.146] / 0.180 [0.050, 0.297] / 0.211 [−0.250, 0.533], 합 **0.117 [0.071, 0.164]** (b\* 1081 / V1 997 / genie 365). last: −3 dB 0.124 [0.076, 0.171] (V1 815; `recovery_DMIB16e4last.txt` — `recovery_diff_DMIB16e4.txt` 의 같은 값은 재표집이 달라 [0.076, 0.169]). **1차 ΔR (−3 dB)**: 포화 가드 미발동(b\* BLER@16 −3 dB 0.346 ∈ [0.005, 0.9], b\* 885 > genie 321), undefined 0 → **ΔR = −0.371 [90 % 비짝 −0.439, −0.308] → 등록 라벨 "회수율이 D2 보다 낮다"** (D2 B16e4k −3 dB R 0.470 [0.427, 0.512]; last: −0.346 [−0.413, −0.285]). 2차(보고): 판정점 합 0.117 [`recovery_diff` 의 CI 0.069, 0.162] vs D2 (−3, 0, +3 합) 0.509 → −0.391 [−0.452, −0.334]. 실패 수 격차(−3 dB): V1 − genie 508 [473, 544], b\* − genie 564 [526, 599] (D2: 284 [256, 311], 536 [501, 571]).

### 7.2 보고 전용

**BLER@16 (괄호 = 실패 수 / 2560; best 태그; R0-pilot 은 @1)**

| arm | −3 dB | 0 dB | +3 dB | +6 dB | +9 dB | +12 dB | +15 dB |
|---|---|---|---|---|---|---|---|
| **V1** | 0.324 (829) | 0.058 (149) | 0.007 (19) | 0.002 (4) | 0.000 (0) | 0.000 (0) | 0.000 (0) |
| V1 (last 태그) | 0.318 (815) | 0.058 (148) | 0.007 (18) | 0.001 (3) | 0.000 (0) | 0.000 (0) | 0.000 (0) |
| V4 | 0.328 (840) | 0.068 (174) | 0.007 (18) | 0.002 (4) | 0.000 (0) | 0.000 (0) | 0.000 (0) |
| V4b | 0.347 (888) | 0.070 (179) | 0.009 (22) | 0.002 (4) | 0.000 (1) | 0.000 (0) | 0.000 (0) |
| **b\*** | 0.346 (885) | 0.068 (173) | 0.009 (23) | 0.003 (7) | 0.000 (0) | 0.000 (0) | 0.000 (0) |
| b\*-scalar | 0.355 (908) | 0.077 (198) | 0.009 (24) | 0.004 (9) | 0.000 (0) | 0.000 (0) | 0.000 (0) |
| gmm32 | 0.491 (1256) | 0.128 (327) | 0.018 (46) | 0.003 (7) | 0.000 (1) | 0.000 (0) | 0.000 (0) |
| R2-ours-G | 0.752 (1924) | 0.327 (838) | 0.075 (191) | 0.012 (31) | 0.005 (12) | 0.000 (0) | 0.000 (0) |
| R1-turbo | 0.877 (2245) | 0.517 (1324) | 0.166 (424) | 0.035 (90) | 0.009 (23) | 0.002 (4) | 0.000 (0) |
| R0-pilot (@1) | 0.985 (2521) | 0.802 (2052) | 0.360 (922) | 0.118 (302) | 0.032 (81) | 0.009 (23) | 0.001 (3) |
| pilot_C (@16; 문맥) | 0.871 (2230) | 0.457 (1169) | 0.103 (263) | 0.016 (41) | 0.004 (10) | 0.000 (1) | 0.000 (0) |
| R4-scvamp | 0.915 (2342) | 0.622 (1593) | 0.266 (680) | 0.098 (250) | 0.029 (73) | 0.012 (30) | 0.003 (7) |
| R3-bigamp | 0.938 (2402) | 0.684 (1751) | 0.362 (928) | 0.216 (554) | 0.171 (437) | 0.224 (573) | 0.236 (603) |
| R4-llr | 0.955 (2446) | 0.842 (2155) | 0.820 (2100) | 0.614 (1572) | 0.302 (774) | 0.131 (336) | 0.043 (111) |
| V0 | 1.000 (2560) | 1.000 (2560) | 1.000 (2560) | 0.997 (2552) | 0.981 (2511) | 0.798 (2043) | 0.252 (644) |
| **genie** | 0.125 (321) | 0.016 (40) | 0.002 (4) | 0.000 (0) | 0.000 (0) | 0.000 (0) | 0.000 (0) |

- **SNR@0.1** (표 A; dB): genie −2.67 · V1 −0.95 · V4 −0.74 · b\* −0.72 · V4b −0.67 · b\*-scalar −0.51 · gmm32 0.37 · R2-ours-G 2.41 · pilot_C (@16) 3.04 · R1-turbo 3.98 · R4-scvamp 5.93 · R0-pilot (@1) 6.38 · R4-llr 12.74; R3-bigamp · V0 는 "> 15". 표 B 의 격차: `V1 → genie` +1.73 dB [+1.56, +1.90], `b* → genie` +1.95 dB [+1.76, +2.14].
- **V4 · V4b · V0 (앵커 b\*, −3 / 0 / +3)**: `b* → V4` 177:132 (0.012) · 64:65 (1) · 15:10 (0.42), pooled 256:207 (p 0.026), second arm fewer 1/3 → not significant (격차 +0.02 dB [−0.13, +0.17]); `b* → V4b` 164:167 · 61:67 · 13:12, pooled 238:246 (p 0.75), 0/3 (−0.05 dB [−0.20, +0.10]); `b* → V0` 0:1675 · 0:2387 · 0:2537, pooled 0:6599, first arm (b\*) fewer 3/3. 판정점 3 점 실패 수 합: V1 997 / V4 1032 / V4b 1089; 7 SNR 합: V1 1001 / V4 1036 / V4b 1094 (검정 없음).
- **`V1 → genie`** (앵커 genie; 범위 안 SNR 이 −3 · 0 dB 둘뿐 → UNDECIDED): 537:29 · 116:7, pooled 653:36. `b* → genie`: 598:34 · 141:8, pooled 739:42 (UNDECIDED).
- **best 대 last V1 짝 부호검정** (−3 / 0 / +3; a = best 만 실패, b = last 만 실패): 46:32 (p 0.141) · 23:22 (1) · 2:1 (1), pooled 71:55 (p 0.181) — 판정하지 못함(유의 방향 없음).
- **F3 가드 발동률** (`results/guard_D2_DMIB16e4{,last}.txt`): V0 — best −3 … +15 dB 1.000 / 1.000 / 0.999 / 0.996 / 0.963 / 0.820 / 0.509, last 1.000 / 1.000 / 1.000 / 0.990 / 0.958 / 0.782 / 0.552. V0 밖의 발동 없음. 한 번도 발동하지 않은 arm 12 개: M-ours-bstar, M-ours-bstar-scalar, M-ours-dscore-C-V1, M-ours-dscore-C-V4, M-ours-dscore-C-V4b, M-ours-gmm32, R0-pilot, R1-turbo, R2-ours-G, R3-bigamp, R4-llr, R4-scvamp.
- **동일예산 GB′** (`run_dmi_post_gpu.sh 1 GBP 0`, GPU 0, 10-12 16:16 → 16:24 CDT, rc 0; `logs/gbprime_DMIB16e4.log`, last 파일 `d2sx_DMI_N160000_a1.pt` — 재개는 학습 없이 끝났고(`trained 1162 ep`, stopped_by patience) 체크포인트의 sha 는 5-DMI 그대로(20d28bf06e317ca5 · dc784649f1e9b890); `results/d2_gbprime_DMI_N160000_a1.npz`): median **0.8038** (min 0.7272 · max 1.0217; SRB 0.6472 · SRP 0.5836 · D3 0.559 · Sionna RT 도시 0.543 · DeepMIMO 도시 0.715 · UMi28 0.920 과 나란히). 잡음 수준 20 개 가운데 19 개에서 비 < 1 이고, 가장 큰 수준 σ 0.848 (격자 끝)에서 1.022 (모델 NMSE 0.2233 대 GMM 0.2186). **수용 (e)**: 로그의 `GMM b* = gmm1024 (full K=1024) @N=160000` = 5-DMI 최종 b\* ✓, `d2_gbprime_DMI_N160000_a1.npz` mtime 10-12 16:24:17 CDT > full 1024 적합 파일 mtime 16:11:10 CDT ✓ → GB′ 수치 유효.
- **누수 층화** (보고 전용; `code/dmc_leak_strata.py --tag DMIB16e4 --prior DMI`, 10-12 17:57 CDT 실행(CPU 4 스레드; baseline runner 와 겹침, 주 실행의 raw 만 읽음) → `DMIB16e4_leak_strata.txt`; 정렬 OK). d < 0.1 의 비율은 판정점마다 0.074 / 0.066 / 0.064 (d 중앙값 0.1803 / 0.1813 / 0.1810). n: b\* / V1 / genie 실패 수 → 점추정 R: **d < 0.1** −3 dB 189: 74 / 60 / 29 → 0.311, 0 dB 169: 12 / 19 / 4 → −0.875, +3 dB 165: 2 / 2 / 0 → 0.000, 3 점 합 523: 88 / 81 / 33 → 0.127; **d ≥ 0.1** −3 dB 2371: 811 / 769 / 292 → 0.081, 0 dB 2391: 161 / 130 / 36 → 0.248, +3 dB 2395: 21 / 17 / 4 → 0.235, 3 점 합 7157: 993 / 916 / 332 → 0.116.
- **랭크 층화** (보고 전용; `code/rank_strata.py --tag DMIB16e4 --prior DMI` → `DMIB16e4_rank_strata.txt`; 정렬 OK; 비중 중앙값 0.872 / 0.874 / 0.873). 칸 = n (비율): genie / V1 / b\* 의 BLER@16 (실패 수):

| SNR | ≥ 0.95 | 0.80–0.95 | 0.60–0.80 | < 0.60 |
|---|---|---|---|---|
| −3 dB | 59 (0.023): 0.339 / 0.661 / 0.678 (20 / 39 / 40) | 2040 (0.797): 0.136 / 0.336 / 0.360 (278 / 686 / 735) | 457 (0.179): 0.050 / 0.225 / 0.241 (23 / 103 / 110) | 4 (0.002): 0.000 / 0.250 / 0.000 (0 / 1 / 0) |
| 0 dB | 52 (0.020): 0.115 / 0.327 / 0.308 (6 / 17 / 16) | 2110 (0.824): 0.016 / 0.060 / 0.071 (34 / 127 / 149) | 391 (0.153): 0.000 / 0.013 / 0.020 (0 / 5 / 8) | 7 (0.003): 0.000 / 0.000 / 0.000 (0 / 0 / 0) |
| +3 dB | 53 (0.021): 0.019 / 0.075 / 0.094 (1 / 4 / 5) | 2096 (0.819): 0.001 / 0.006 / 0.009 (3 / 13 / 18) | 408 (0.159): 0.000 / 0.005 / 0.000 (0 / 2 / 0) | 3 (0.001): 0.000 / 0.000 / 0.000 (0 / 0 / 0) |

### 7.3 baseline — 표 B `X → V1`: 새 라벨 15 개 + 주 라벨 1 개 (C2, prior DMI, UNGATED; 앵커 = X, R0-pilot 은 @1)

**실행·운영 기록**: `bash code/run_dmi_base.sh d2sx_DMI_N160000_a1 dc784649f1e9b890 8f72c113efb91b0b 1e7824c1bae10376 gmm1024 - 112.04253042212595` (인자 = 5-DMI 의 값) **한 번**, tmux `dmibase`, 같은 `taskset` (96 스레드), 10-12 17:56 CDT 시작(git 29cf411d; `DEFER_ALD` 스위치 없이). PIL runner 1.6 분 → 17:58 CDT `ACCEPT: OK -- PILDMI`, `pair_cross` 무결성 OK(raised 0 / 0) → ALD 시험 사이트 재생성(CPU) → ALD 추정 GPU 0 (17:59 CDT; `results/ald/ald_PILDMI.npz` sha256[:16] b0145dac7b7076aa) → ALD runner 0.6 분 → 17:59 CDT `ACCEPT: OK -- ALDDMI`, `pair_ald` 무결성 OK → pick 규칙 재현(`rule-reproduced=True`, 메모리 필요 ≈ 264 GB / 가용 1040 GB) → SP runner 14.9 분 → `meta|sparse` 불일치 0, raised 0 / 0 / 0 → 18:15 CDT `ACCEPT: OK -- SPDMI` → `pair_baselines` rc 0 → 18:15 CDT `DMI_BASE_DONE rc=0`. raw 마다 깨끗한 커밋 하나: `pair_baselines` 머리말 `git base=4131a3b0 extra0=29cf411d pil=29cf411d ald=29cf411d; integrity: OK`. 커밋 29cf411d 는 `PRIOR_EVAL_DONE` 뒤·baseline 시작 전에 주 실행의 결과 파일과 baseline 입력(`results/sparse/{pick,tune}_DMI_C2.json`, `results/ald/tune_PILDMI{.json,_curves.npz}` — 5-DMI 에 sha 로 고정돼 있던 파일을 추적만 함; `run_dmi_base.sh` 가 추적·clean 을 요구한다)을 더한 것이다(`git diff 4131a3b0 29cf411d -- conf/code Demo` 비어 있음).

| X | 판정점 [dB] | a:b (X 만 실패 : V1 만 실패) | pooled (p) | 가드 · 유의 점 수 | 라벨 | F_X − F_V1 (−3 dB) | R_X (−3 dB) [90 %] | R_X (판정점 합) [90 %] |
|---|---|---|---|---|---|---|---|---|
| b\* (주 라벨, 7.1) | -3 / +0 / +3 | 178:122 · 72:48 · 13:9 | 263:179 (7.5e-05) | POWERED, V1 2/3 · X 0/3 | **(i)** | 56 | 0.099 [0.050, 0.146] | 0.117 [0.071, 0.164] |
| b\*-scalar | -3 / +0 / +3 | 201:122 · 87:38 · 14:9 | 302:169 (9.2e-10) | POWERED, V1 2/3 · X 0/3 | **(i)** | 79 | 0.135 [0.085, 0.182] | 0.174 [0.129, 0.218] |
| gmm32 | -3 / +0 / +3 | 502:75 · 214:36 · 34:7 | 750:118 (3.4e-113) | POWERED, V1 3/3 · X 0/3 | **(i)** | 427 | 0.457 [0.424, 0.488] | 0.500 [0.473, 0.527] |
| R0-pilot@1 | +3 / +6 / +9 | 903:0 · 298:0 · 81:0 | 1282:0 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1692 | 정의 안 됨 (범위 밖: 0.9848) | 0.985 [0.979, 0.991] |
| R1-turbo | +0 / +3 / +6 | 1180:5 · 406:1 · 88:2 | 1674:8 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1416 | 0.736 [0.718, 0.753] | 0.929 [0.918, 0.939] |
| R2-ours-G | -3 / +0 / +3 | 1129:34 · 709:20 · 176:4 | 2014:58 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1095 | 0.683 [0.662, 0.703] | 0.756 [0.741, 0.771] |
| R3-bigamp | +6 / +9 / +12 | 551:1 · 437:0 · 573:0 | 1561:1 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1573 | 정의 안 됨 (범위 밖: 0.9383) | 0.997 [0.995, 0.999] |
| R4-llr | +9 / +12 / +15 | 774:0 · 336:0 · 111:0 | 1221:0 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1617 | 정의 안 됨 (범위 밖: 0.9555) | 정의 안 됨 (판정점에서 genie 실패 ≥ V1 실패) |
| R4-scvamp | +3 / +6 / +9 | 661:0 · 247:1 · 73:0 | 981:1 (4.8e-293) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1513 | 정의 안 됨 (범위 밖: 0.9148) | 0.981 [0.973, 0.989] |
| bstar-pilot | -3 / +0 / +3 | 449:66 · 154:34 · 18:8 | 621:108 (2.3e-88) | POWERED, V1 2/3 · X 0/3 | **(i)** | 383 | 0.430 [0.396, 0.462] | 0.448 [0.417, 0.478] |
| V1-pilot | -3 / +0 / +3 | 410:46 · 130:26 · 15:4 | 555:76 (7.9e-91) | POWERED, V1 3/3 · X 0/3 | **(i)** | 364 | 0.417 [0.384, 0.449] | 0.431 [0.402, 0.459] |
| ALD-pilot | -3 / +0 / +3 | 608:62 · 239:28 · 47:4 | 894:94 (2.6e-164) | POWERED, V1 3/3 · X 0/3 | **(i)** | 546 | 0.518 [0.489, 0.547] | 0.559 [0.534, 0.584] |
| ALDv-pilot | -3 / +0 / +3 | 587:59 · 209:29 · 34:5 | 830:93 (1.3e-148) | POWERED, V1 3/3 · X 0/3 | **(i)** | 528 | 0.510 [0.479, 0.538] | 0.538 [0.512, 0.563] |
| SBL-loop | -3 / +0 / +3 | 958:47 · 553:20 · 113:4 | 1624:71 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 911 | 0.642 [0.619, 0.665] | 0.711 [0.693, 0.728] |
| SBL-pilot | -3 / +0 / +3 | 1198:18 · 728:15 · 165:4 | 2091:37 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1180 | 0.699 [0.679, 0.718] | 0.765 [0.750, 0.779] |
| OMP-pilot | +0 / +3 / +6 | 1080:12 · 298:2 · 77:1 | 1455:15 (0) | POWERED, V1 3/3 · X 0/3 | **(i)** | 1302 | 0.719 [0.701, 0.737] | 0.918 [0.906, 0.930] |

- 표의 pooled p "(0)" 은 도구의 `%.2g` 출력이 언더플로한 것이다(실제 값 < 1e-300).
- **요약 줄(원문)**: `SUMMARY-B (baselines without b*, 15): (i) 15, (ii) 0, not decided 0; b* -> V1 (i)` · `SUMMARY registered baselines 16 (b* + 𝔅 15): (i) 16, (ii) 0, not decided 0`.
- **"전부" 문장 (§2 조건 충족: 주 라벨 (i) 이고 15 개 모두 (i))**: **"DeepMIMO 실내 (`i1_2p4` 2.4 GHz, 고정 기지국 한 곳, block split) 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)보다 적게 실패 (UNGATED 측정)"**.
- **"멀어진다" 문장 (조건 충족)**: `'등록된 baseline 전부와 멀어진다' condition (k = 16, (ii) = 0, R_X* CI lower > 0): MET` — `X* (fewest -3 dB failures, ties by name) = M-ours-bstar (F=885); R_X* -3 dB = 0.099 [90% 0.050, 0.146]` → **"… 에서 V1 이 등록된 baseline 전부(16 개, 희소 baseline 포함)와 멀어진다 (UNGATED 측정)"**. 여기서 가장 가까운 baseline X\* 는 GMM prior(b\*) 자신이다.
- 두 문장 모두 7.1 의 캐비엇과 §1 고유 사항 (6)(baseline 조정용 개발 채널이 테스트 풀에서 나옴)을 붙여서만 쓴다. 범위: 이 방·이 기지국·이 split·이 크기 한정; 동치 문구·일반화 문장은 쓰지 않는다.
- **드리프트 검사**: `b* → V1` 을 `pair_baselines` 가 다시 낸 값(178:122 · 72:48 · 13:9, pooled 263:179, (i), R(−3 dB) 0.099 [0.050, 0.146], 판정점 합 0.117 [0.071, 0.164]) = 7.1 → 드리프트 없음.
- R_X(−3 dB) 는 X 의 −3 dB BLER 이 0.9 를 넘는 **4 개**(R0-pilot@1 0.9848 · R3-bigamp 0.9383 · R4-llr 0.9555 · R4-scvamp 0.9148)에서 정의되지 않는다(포화 가드); 나머지 12 개는 정의된다. R4-llr 은 판정점 합의 R_X 도 정의되지 않는다(판정점 +9 / +12 / +15 dB 에서 V1 과 genie 의 실패가 모두 0). (i) 이지만 유의한 점이 2/3 인 행: b\* (+3 dB 13:9) · b\*-scalar (+3 dB 14:9) · bstar-pilot (+3 dB 18:8).

### 7.4 원고 범례 11 곡선 — BLER@16 실패 수 / 2560 (`pairB_SPDMI.txt` 의 표; 전 SNR n = 2560)

| 곡선 | −3 | 0 | +3 | +6 | +9 | +12 | +15 dB |
|---|---|---|---|---|---|---|---|
| Proposed (V1) | 829 | 149 | 19 | 4 | 0 | 0 | 0 |
| Annealed Langevin (plug-in) = ALD-pilot | 1375 | 360 | 62 | 4 | 1 | 1 | 0 |
| GMM prior = b\* | 885 | 173 | 23 | 7 | 0 | 0 | 0 |
| Gaussian prior = R2-ours-G | 1924 | 838 | 191 | 31 | 12 | 0 | 0 |
| Turbo LMMSE = R1-turbo | 2245 | 1324 | 424 | 90 | 23 | 4 | 0 |
| BiG-AMP = R3-bigamp | 2402 | 1751 | 928 | 554 | 437 | 573 | 603 |
| Pilot-only LMMSE = R0-pilot@1 | 2521 | 2052 | 922 | 302 | 81 | 23 | 3 |
| SBL (in loop) | 1740 | 682 | 128 | 16 | 5 | 0 | 0 |
| SBL (pilot-only) | 2009 | 862 | 180 | 20 | 3 | 1 | 0 |
| OMP (pilot-only) | 2131 | 1217 | 315 | 80 | 24 | 3 | 0 |
| Perfect CSI = genie | 321 | 40 | 4 | 0 | 0 | 0 | 0 |

- 11 곡선에 없는 등록 arm (같은 순서): V1-pilot 1193 / 253 / 30 / 3 / 0 / 0 / 0; bstar-pilot 1212 / 269 / 29 / 5 / 0 / 0 / 0; ALDv-pilot 1357 / 329 / 48 / 4 / 1 / 1 / 0; M-ours-bstar-scalar 908 / 198 / 24 / 9 / 0 / 0 / 0; M-ours-gmm32 1256 / 327 / 46 / 7 / 1 / 0 / 0; R4-scvamp 2342 / 1593 / 680 / 250 / 73 / 30 / 7; R4-llr 2446 / 2155 / 2100 / 1572 / 774 / 336 / 111.
- 그림: `conference/figures/F21dmi_col.{pdf,png}` (`paper_f21dmc.py DMI`, 기록 `records/paper_f21dmi.txt`): 실패 수 = 위 표(assert), 세 raw 의 Perfect CSI 오류 배열 동일(assert), y 축 (3e-05, 1.2) (0 실패 점이 있어서), 0 실패 점 18 개에서 곡선이 끊김(Proposed +9 · +12 · +15, Annealed Langevin +15, GMM prior +9 · +12 · +15, Gaussian prior +12 · +15, Turbo LMMSE +15, SBL (in loop) +12 · +15, SBL (pilot-only) +15, OMP (pilot-only) +15, Perfect CSI +6 · +9 · +12 · +15 dB). 그려진 baseline 9 개의 라벨 모두 (i). **점추정으로 제안 곡선 이하인 baseline 점이 있다**(기록 파일의 해당 줄 원문 그대로: Annealed Langevin (plug-in) at +6 dB (4 vs 4), +15 dB (0 vs 0); GMM prior at +9 dB (0 vs 0), +12 dB (0 vs 0), +15 dB (0 vs 0); Gaussian prior at +12 dB (0 vs 0), +15 dB (0 vs 0); Turbo LMMSE receiver at +15 dB (0 vs 0); SBL (in loop) at +12 dB (0 vs 0), +15 dB (0 vs 0); SBL (pilot-only) at +15 dB (0 vs 0); OMP (pilot-only) at +15 dB (0 vs 0)) — 한 점(+6 dB 4 대 4)을 빼면 모두 양쪽이 0 실패인 점이며, 등록된 판정은 판정점의 짝 검정이다.
- **NMSE CDF** (보고 전용): `conference/figures/F33cdf_DMI_wide.{pdf,png}` (`paper_f33cdf.py DMI`, 기록 `records/paper_f33cdf_DMI.txt`): 패널 −3 · 0 · +3 · +6 dB, 곡선 10 개, 2560 시행 전부(비유한·비양수 0 건). −3 dB 의 중앙값 10 log10 NMSE [dB]: Proposed −14.39 · GMM prior −13.49 · Annealed Langevin (plug-in) −9.30 · Gaussian prior −6.33 (나머지는 기록 파일).

### 7.5 baseline 보고 전용

- `pair_PILDMI.txt`: P1 `V1-pilot → V1` 410:46 · 130:26 · 15:4, pooled 555:76 → (i) (3/3); P2 `bstar-pilot → V1-pilot` 142:123 (0.27) · 81:65 (0.21) · 11:12 (1), pooled 234:200 (p 0.11) → (iii); `bstar-pilot → b*` 366:39 · 118:22 · 13:7, pooled 497:68 → (i) (2/3); `V1-pilot → b*` 376:68 · 128:48 · 19:12, pooled 523:128 → (i) (b\* 가 2/3 에서 적게 실패).
- `pair_ALDDMI.txt`: A1 `ALDv-pilot → V1` 587:59 · 209:29 · 34:5 → (i); A2 `ALD-pilot → V1` 608:62 · 239:28 · 47:4 → (i); A3 `ALDv-pilot → V1-pilot` 289:125 · 126:50 · 28:10, pooled 443:185 → (i) (3/3); `ALDv-pilot → b*` 547:75 · 207:51 · 36:11, pooled 790:137 → (i) (3/3); `bstar-pilot → ALDv-pilot` 146:291 · 86:146 · 16:35, pooled 248:472 → (ii) (bstar-pilot 이 3/3 에서 적게 실패); `ALD-pilot → ALDv-pilot` 66:48 (0.11) · 56:25 · 18:4, pooled 140:77 → (i) (2/3). 시험 ALD NMSE(추정 파일 평균) −8.10 / −11.70 / −14.64 / −17.40 / −19.90 / −22.20 / −24.40 dB.
- 조정 표: 5-DMI (SBL ρ 16 · OMP ρ 16 — 둘 다 격자 끝 + 캐비엇; ALD c 0.01 · β 0.005).
- raised trials: PIL 0 / 0, ALD 0, SP 0 / 0 / 0.

### 7.6 §3 예측 채점 — DMI (적중 / 빗나감; 범위 밖은 채점 불가; 예측은 동결 b737fd55 때의 것 — DMI 의 실행은 SRB · SRP 의 결과를 본 뒤였다(5-DMI))

1. 표 B (i) → 결과 (i) → **적중**.
2. 판정점 −3 / 0 / +3 dB 이고 POWERED (DMI 확신 낮음) → **적중**.
3. Perfect CSI 의 BLER 수준: 관측됨(채점 제외).
4. 1차 ΔR 의 포화 가드 미발동 → **적중** (b\* BLER(−3 dB) 0.346, b\* 885 > genie 321).
5. R(−3 dB) 의 90 % CI 하한 > 0 → **적중** (0.050).
6. `R2-ours-G → b*` b\* 가 ≥ 2/3 점에서 적게 실패 → **적중** (3/3).
7. V1 과 b\* 의 SNR@0.1 이 둘 다 숫자 → **적중** (−0.95 · −0.72 dB); 격차(b\* − V1) > 0 dB → **적중** (+0.23 dB [+0.08, +0.37]).
8. GB′ median ≤ 0.90 → **적중** (0.8038).
9. 학습(patience · epoch ∈ [300, 1500]) → **적중** (5-DMI: patience, epoch 1162).
10. b\* = kron 계열, K ≥ 1024 → **빗나감** (5-DMI: b\* = full 1024).
11. V0: −3 dB 가드 발동률 ≥ 0.5 이고 BLER ≥ 0.9 → **적중** (1.000 · 1.000). best 대 last V1 판정하지 못함(pooled p > 0.05) → **적중** (pooled 71:55, p 0.181).
12. 대조군 `b* → b*-scalar` (iii) → **빗나감** (POWERED, b\* 가 2/3 에서 적게 실패 → (ii)).
13. baseline — 세 문장: "(ii) 0 이고 (i) ≥ 12" → **적중** ((ii) 0, (i) 15 / 15); `pair_ALDDMI.txt` A3 = (i) → **적중**; −3 dB 실패 수 `SBL-pilot` < `R0-pilot@1` → **적중** (2009 < 2521).
14. 랭크 층화: 관측됨(채점 제외). 15. 예측 없음.
16. 빗나갈 경로: (e) b\* 가 full 512 → full 1024 한 번 + 캐비엇 — **발동**(5-DMI). (a)(b)(c)(d)(f) 미발동((i); R > 0; POWERED; 발산 없음; baseline 에 (ii) 없음).

### 7.7 등록 대비 공개 사항 (수치·판정 불변)

- **DMI 는 10-11 CDT 에 실행 전 철회됐다가 10-12 CDT 에 되돌려 실행했다**(5-DMI): 규칙·예측은 동결 v2 그대로이고, 실행은 SRB (§6) 와 SRP (PATH16e4) 의 결과·그림 보강·시드 강건성을 모두 본 뒤였다. §1 의 "SRB 먼저, 이어서 DMI" 순서는 지켜졌으나 그 사이에 다른 등록(PATH · FIGHS* · SEEDSROOM) 의 runner 가 돌았다.
- **CPU 96 스레드**: 주 실행·baseline 모두 `taskset` 으로 NUMA 노드 1 · 3 에 묶어 돌렸다(사용자 지시; §1 은 "192 워커"). 수신기는 결정적이라 결과는 같고(수용 검사의 R5-genie 비트 동일·청크 계획 통과), 시간만 늘었다(태그당 46.6 · 49.9 분; SRB 는 28.3 · 24.8 분).
- 동결(b737fd55) 뒤·DMI 의 BLER 전의 `conf/code` 변경(`git diff --stat b737fd55 4131a3b0 -- conf/code Demo`: 23 파일, Demo 0): 새 파일 `srp_build.py` · `path_strata.py` · `run_srp_*.sh` 5 개 · `run_fighsroom16e4.sh` · `run_fighspath16e4.sh` · `run_fighsx16e4.sh` · `run_seedsroom16e4.sh`; 고친 파일 `ald.py` · `analysis.py` · `common.py` · `dmimo.py` · `em_batched_check_nr.py` · `run_d2_sx.py` · `run_manifest.py` · `run_prior_eval.sh` · `sigma.py` · `testbed_dm.py` (prior SRP = PID 15 의 연결과 ALD 의 세트 `hisnr` · `hisnr4`), `run_srb_eval.sh` · `run_dmi_eval.sh` (인자). DMI 의 풀·학습 집합은 그대로다(`dmimo.py selfcheck 8 DMI` 의 train sha = §0 의 3380177f4c38cf57).
- 주 실행과 baseline 실행은 각각 한 번 돌았고 재실행·중단·재개가 없다(`logs/run_D2_DMIB16e4{,last}.log` 각 448 done, exists 줄 없음; `run_prior_eval_DMIB16e4.log` 와 `run_dmi_base.log` 의 시작 줄 하나씩). 이 로그들은 git 밖이다.
- 큐·적합의 경위(10-11 큐에서 뺌 → 10-12 다시 21 작업, full 1024 추가 적합, 대기 명령 오류로 71 분 공백)와 ALD 조정이 최종 b\* 확정 전에 돈 것은 5-DMI 에 적은 그대로다.
- baseline 입력 파일 세 개는 5-DMI 커밋(4131a3b0)에 sha 만 적혀 있었고 git 추적은 29cf411d 에서 시작했다(내용은 5-DMI 의 sha 와 같음 — `run_dmi_base.sh` 가 sha 를 검사).
- 보고 전용 층화 둘(누수·랭크)은 baseline runner 가 도는 동안 CPU 8 스레드(NUMA 노드 0)로 돌렸다(주 실행의 raw 만 읽는다).
- **그림 보강**: F21dmi_col 은 +9 dB 부터 제안 곡선이 끊긴다(0 실패). SRB · SRP 와 같은 n = 20480 보강(보고 전용)은 별도 문서로 등록한다 — 이 문서의 판정·라벨·7.4 의 표와 그림 `F21dmi_col` 은 그대로 남는다.
