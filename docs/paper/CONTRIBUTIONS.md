# 기여와 신규성 — T2 학회 논문 (4–6쪽)

- 작성: 2026-09-25 22:50 CDT (= 09-26 12:50 KST). 코드·기록 기준 커밋 54d68a14. 개정: 2026-09-25 23:20 CDT (= 09-26 13:20 KST). 최종 점검의 남은 결함을 반영하고, 작업 트리(미커밋)의 새 기록 두 건(`conf/DECISIONS.md:205`: C6 GMM 수렴 캐비엇, 파일럿 위치 검사)을 넣었다.
- 입력: 초안 `contrib_draft.md`와 그 적대적 검증 `contrib_verify.md`. 둘 다 세션 스크래치(`/tmp/claude-1005/-home-HTJ-t2/47f1f727-1d40-4c8f-a798-01f8d9d886c3/scratchpad/framing/`)에 있고 저장소 밖이다. 검증의 정정을 반영했다. 그 뒤 최종 점검(`final_check_contrib.md`, 같은 스크래치)이 "남은 결함"으로 꼽은 16건도 반영했다. 이번 개정은 다시 검증받지 않았다. 이 문서의 수치는 모두 아래 적은 file:line을 작성 중에 다시 열어 대조했다.
- 태그: **[코드]** 코드에서 읽음 · **[유도]** 우리가 유도함(코드에 없음) · **[가정]** 논문에 명시할 모형 가정 · **[기록]** 결과 기록에서 옮김. 경로는 `/home/HTJ/t2` 기준이다. 자주 쓰는 약칭: **T** = `conf/results/tables_D2_B16e4k.txt` (헤드라인 표), **R** = `docs/RESULTS.md`.
- 문구 규칙
  - genie(`R5-genie`)는 "같은 EP 검출기·BCJR 루프에 참 H를 준 known-channel 참조"다. 한계(bound)로 쓰지 않는다 (R:245).
  - headroom·reach·"최적" 계열 표현은 쓰지 않는다.
  - p ≥ 0.05, 또는 UNDECIDED는 "판정하지 못함"으로 쓴다. "차이 없음"으로 바꾸지 않는다 (R:884).
- 배치 원칙(사용자 전략): 어디서 이기는지, 얼마나, 왜를 먼저 쓰고 범위·한계는 §6에 마지막으로 둔다. 등록된 캐비엇은 하나도 빼지 않는다. 격자 끝, 보고 필드처럼 수치의 뜻을 바꾸는 캐비엇은 본문 수치 옆에도 짧게 붙인다.

---

## 0. 결론: 기여 순위와 위험 (검증 반영 개정판)

| 순위 | 기여 | 논문 속 역할 | 신규성 (선행연구 대비) | 채택·해석 위험 | 핵심 사유 |
|---|---|---|---|---|---|
| **H1** | 부호화 EP/turbo 루프의 채널 prior 모듈을 학습 diffusion prior로 바꾸고, 동일예산 GMM b\*(검증 우도로 K 선택, 정확 mixture EP site)와 사전 등록 검정으로 비교 | 주장 본체 (어디서·얼마나) | **중** (조합과 비교 설계. 웹 검색 기준 선례 없음, §2.5) | **채택 위험 상** | 합성 testbed D2 하나뿐이다. 헤드라인 b\*가 K 격자 끝이다. 등록 1차 arm은 V0였다 (§2.4) |
| **H2** | 학습 야코비안으로 만든 EP 행렬 site의 수신기 수준 붕괴 사슬(D2), 그리고 Hermitian-PSD floor(V1) 수리 | 기전 (왜 되고 왜 깨지나) | 원 형태 그대로면 **낮음**: "학습 J는 SPD/PSD가 아니다"와 "학습 J로 Tweedie 공분산을 만든다"는 Rozet 2024 [R1], TMPD [R2], JAPS [R3]가 선점했다. **수신기 수준 붕괴 사슬로 한정하면 중** | 해석 위험 중 | PSD 투영은 교과서적이다 (Higham 1988 [R4]). 붕괴는 D2에서 관측됐고, 같은 레시피·예산의 D1 형제에서는 나타나지 않았다. 사슬의 가운데 고리(site 발산 경로)는 유도다 (§3.1, §3.3) |
| **H3** | Nr 8→16에서 GMM→genie 참조 격차의 회수율이 더 컸다는 관측 | 조건 (어디서 더 이기나) | **중** (부호화 수신기에서 Nr의 함수로 잰 선례를 찾지 못함, 웹 검색 기준. 개념 배경은 [R31], §4) | **해석 위험 상** | 두 셀 비교는 단일 요인 비교가 아니다: 여차원과 주변차원(GMM 파라미터 부담)을 분리할 수 없고, b\*의 K(1024 대 4096)·학습 시행·예산 선택 시점이 다르다. C6 b\*는 격자 끝이고 덜 수렴됐을 수 있으며, 그 방향은 V1에 유리하다 (§4) |
| 보조 | (e) V1은 생성모형을 아는 q-측정 Bayes 참조와 판정하지 못함. 잠재 정보 몫이 유의 (보고 전용) | 분석 한 문단 | 낮음 | 낮음 | 기여로 세우기엔 가치가 작다 |
| 각주 | (f) 격자 밖 질의 규칙 V1-edge | C1 한계의 각주 | **낮음** (공학적 수리) | 낮음 | 별도 arm이다. 등록 C1 판정은 바뀌지 않는다 |

- 열의 뜻: **신규성**은 선행연구 대비 새로운 정도다(높을수록 새롭다). **채택·해석 위험**은 리뷰어가 주장을 받아들이지 않거나 다르게 읽을 위험이다(높을수록 위험하다). 두 열은 따로 매긴다.

**모든 기여에 걸리는 공통 주의 — 이득의 원천.**
- 스칼라 site V4도 b\*를 이긴다: 3/3, pooled 438:85, SNR@0.1 격차 +1.27 dB [+1.08, +1.50], −3 dB BLER 0.154 (T:72, T:375-378) [기록].
- V1↔V4 짝 검정은 어느 표에도 없다. T에서 V4가 들어간 쌍은 `R2-ours-G → V4`(T:343)와 `b* → V4`(T:373)뿐이다 [기록].
- 따라서 GMM 대비 이득의 원천은 "학습 prior를 Module H에 넣은 것"으로 쓴다. "행렬 site"를 H1 이득의 원천으로 쓰지 않는다.
- 이 읽기는 사전 등록된 해석과 같다: "학습 prior 의 1차 통계(평균·score)는 정확하고 2차 구조(야코비안)는 부정확하므로, 2차 구조를 요구하지 않는 site 를 쓰면 이득이 실현된다" (`conf/10_SPEC_stageC.md:269-271`) [기록].

---

## 1. 원고용 기여 문단 (서론 끝; 검증 §5 권고 문구를 바탕으로)

> 본 논문의 기여는 세 가지다.
> **(i)** 미지 MIMO 채널에서 검출, BCJR 복호, 데이터 보조 채널추정을 함께 도는 EP형 turbo 수신기에서 채널 prior 모듈만 학습 diffusion 디노이저로 바꾼다. 이 모듈은 Tweedie 평균, 야코비안 기반 공분산 site, Hermitian-PSD 투영으로 이루어진다. 비교 대상은 같은 학습 표본 수로 적합하고 검증 우도만으로 K를 고른 Kronecker GMM이며, 정확한 mixture EP site를 쓴다. 이 GMM의 K는 헤드라인 예산에서 실행 격자의 끝에 있다. 조건부 Gaussian성을 깨도록 설계한 합성 희소 정반사 testbed의 8×4, $T{=}16$, $T_p{=}4$ 셀에서 사전 등록된¹ 3점 짝지음 부호검정은 헤드라인 예산 $N{=}1.6\times10^5$에서 세 판정점 모두 학습 prior의 실패가 적었다 (3/3). SNR@0.1 격차(BLER 0.1에서의 SNR 차)는 보고 필드로 +1.41 dB [90% CI +1.22, +1.64]다. $10^4$부터 $3.2\times10^5$까지 네 예산에서는 +1.32~+1.68 dB였고, $10^4$와 $4\times10^4$ 두 점은 예산 축 측정이다.
> **(ii)** 합성 testbed에서 학습 야코비안으로 EP 행렬 site를 만들면 수신기가 무너지는 사슬(부정부호 공분산 → site 발산 → BLER 붕괴)을 보고한다. 발산 가드 발동과 BLER 붕괴는 네 학습 예산과 16 안테나 셀 모두에서 관측했다. 같은 레시피·예산으로 학습한 D1 형제 모델에서는 부정부호가 관측되지 않았고, 투영 없는 행렬 site가 Gaussian prior 수신기를 이겼다(D1 은 순환 testbed, 앵커 R2). 사슬의 가운데 고리(부정부호가 site를 발산시키는 경로)는 코드에서 유도한 것이며, 방향별 측정은 없다. Hermitian-PSD 고유값 floor는 호출당 +0.2% 비용으로 같은 체크포인트를 되살린다: −3 dB BLER 점추정 0.593 → 0.145이며, 이 두 값 사이의 짝 검정은 없다. 두 testbed 대조에는 비대칭 크기만으로 설명되지 않는 잡음 수준 영역이 있다. 이는 사후공분산 스펙트럼이 0에서 떨어진 여유가 붕괴를 가른다는 가설과 합치한다. 학습 야코비안의 비-PSD 관측과 Tweedie 공분산 구성은 [R1][R2][R3]을, 투영은 [R4]를 인용한다.
> **(iii)** 수신 안테나가 16인 셀에서 GMM→genie 참조 격차 가운데 학습 prior가 메운 비율은 0.81로, 8 안테나 헤드라인 셀의 0.47보다 컸다². 16 안테나 셀은 게이트 없는 측정이고, 두 셀 모두 GMM의 K가 격자 끝에 있다.
> ¹ 등록된 1차 arm은 투영 없는 V0 단독이었고, V0는 b\*에 세 판정점 모두에서 졌다 (pooled 109:5363). V1은 BLER을 보기 전에 등록된 2차 변형이며, V1을 헤드라인으로 올린 결정 기록은 없다.
> ² 두 셀은 Nr 말고도 다르다. GMM b\*의 K가 1024 대 4096이고, 16 안테나 셀의 학습 prior는 첫 학습이 발산한 뒤 등록된 사다리의 두 번째 시행(기울기 클리핑 1.0)의 가중치다. 이 셀의 $1.6\times10^5$ 예산은 $10^4$ 결과를 본 뒤 골랐고, 두 셀 모두 확산 시드는 하나다. 16 안테나 셀의 b\*(K=4096) 적합은 학습 우도 정지 규칙으로 멈췄고 검증 우도는 마지막 평가 시점에서 최고였다. 덜 수렴된 GMM일 수 있고, 그 방향은 학습 prior에 유리하다. 따라서 이 비교는 Nr의 효과만 떼어 낸 것이 아니다.

**문장별 출처**

| 문장 요소 | 값 | 출처 | 태그 |
|---|---|---|---|
| 모듈 구성 (Tweedie 평균, $\Sigma_H=\nu_q\,\mathrm{Herm}(J)$ site, PSD floor) | — | `Demo/t2_route_a.py:309-318`, `conf/code/score.py:603-619` | [코드] |
| b\*: 정확 mixture EP site, 검증 우도로만 선택 | — | `Demo/t2_route_a.py:276-277, :373-374`, `Demo/t2_gmm.py:54-60`; 선택 규칙 R:110 | [코드]·[기록] |
| 헤드라인 b\* = kron K=1024, 격자 끝 | K=512 대비 +3.18 nat, K=2048 미적합 | R:116-117, R:128; `conf/results/review_next/NEXT_EXPERIMENTS_B32e4.md:16` | [기록] |
| C2 설정 | 8×4, T=16, Tp=4, n=2560/SNR | T:47 | [기록] |
| 3/3, pooled 454:78 p=1.7e-65, POWERED | — | T:369-371 | [기록] |
| +1.41 dB [+1.22, +1.64] (보고 필드) | — | T:372 | [기록] |
| 예산 곡선 +1.32~+1.68 dB | 1e4 +1.68 / 4e4 +1.33 / 1.6e5 +1.41 / 3.2e5 +1.32 (last)·+1.33 (`_best`) | `tables_D2_B1e4.txt:372`, `tables_D2_B4e4k.txt:372`, T:372, `tables_D2_B32e4last.txt:373`, `tables_D2_B32e4.txt:373` | [기록] |
| 1e4·4e4 = 예산 축 측정 | D1 형제 게이트 FAIL (GC 0.24333 / 0.16651) | R:41-42, R:45 | [기록] |
| +0.2% | V1 60.304 ms 대 V0 60.186 ms (호출당 중앙값) | R:283-284 | [기록] |
| 0.593 → 0.145, 짝 검정 없음 | — | T:70-71; R:82 | [기록] |
| 0.47 → 0.81 (관측) | C2 0.470 [0.427, 0.512], C6 0.809 [0.747, 0.870] | `conf/results/review_next/NEXT_EXPERIMENTS_C6B16e4.md:97` | [기록] |
| (ii) D2 전 예산·C6에서 V0 붕괴 | V0 −3 dB BLER (가드) 0.789 (0.712) / 0.741 (0.702) / 0.593 (0.529) / 0.595 (0.542, `_best`); C6 −3~+9 dB BLER·가드 1.000 | R:52-58, R:192-193; `NEXT_EXPERIMENTS_C6B16e4.md:108` | [기록] |
| (ii) D1 형제: 부정부호 없음, V0 우세 | Herm J f<0 20 σ 전부 0.000; D1 C1 R2→V0 449:227 3/3, C2 307:94 2/3 (앵커 R2) | `conf/logs/jacpsd_D1_N160000.log:8-27`; `conf/PAPER_MATERIALS.md:598-599` | [기록] |
| (ii) 발산 경로 | — | §3.3 (`Demo/t2_route_a.py:314-317, :378`) | [유도] |
| 각주 ¹ | V0 대 b\* 3/3, pooled 109:5363; 등록 1차 = V0 단독; V1 = BLER 전 등록 2차 변형; 승격 기록 없음 | T:363-365; `conf/10_SPEC_stageC.md:190-195, :201-202`; `conf/results/NUMBERS_PACKAGE_2026-09-22.md:555` | [기록] |
| 각주 ² 셀 차이 | b\* K 1024 (C2) / 4096 (C6); C6 §3d 시행 2; 1e4를 본 뒤 고른 예산; 1.6e5 시드 하나 | R:117; `NEXT_EXPERIMENTS_C6B16e4.md:81, :83, :5`; R:106 | [기록] |
| 각주 ² GMM 수렴 | K=4096 재시작 셋 모두 학습 우도 규칙으로 정지, 검증 우도 마지막 평가에서 최고; C2 b\*는 patience 정지 | `NEXT_EXPERIMENTS_C6B16e4.md:135`; `conf/DECISIONS.md:205`; 규칙 `Demo/t2_gmm.py:164` | [기록]·[코드] |

- '사전 등록'이라는 말을 쓰면 같은 문단이나 각주에 두 가지를 함께 적는다: 등록 1차는 V0 단독이었고 V0는 b\*에 3/3으로 진다는 것, 그리고 V1을 헤드라인으로 올린 결정 기록이 없다는 것이다 (§2.4). 위 원고 문단에서는 각주 ¹이 이 역할을 한다.

**원고에 쓰지 않는 문장**
- "행렬 site가 GMM 대비 이득을 만든다." 근거는 §0 공통 주의다.
- "학습 야코비안이 PSD가 아님을 처음 관측했다." Rozet 2024 [R1]과 JAPS [R3]가 먼저 보고했다.
- "비대칭이 아니라 여유가 판별자임을 보였다." 이 형태로는 단정할 수 없고, §3.4의 제한된 형태로만 쓴다.
- "학습 prior가 GMM보다 낫다"를 셀·예산 한정 없이 쓰는 것 (`conf/results/review_next/NEXT_EXPERIMENTS_B32e4.md:47`).
- genie 쌍에 대한 검정 진술. C2의 arm→genie 쌍은 판정점이 2개라 전부 UNDECIDED다 (T:397-402; R:68). 회수율은 계산 수치이며 검정이 아니다 (R:203).
- "D2는 물리적으로 표준인 mmWave 모델이다." D2는 "조건부 Gaussian 파괴를 분리하는 통제된 희소 정반사 모델"로 쓴다 (R:831).
- A8 "학습 prior 4.6×" (R:828), M6 여유 "780배" (`conf/PAPER_MATERIALS.md:483`), `jac_spectrum.txt:173` "D2 asym" 행 (R:859).
- "수신 안테나를 늘리면 회수율이 커진다." 두 셀은 Nr 말고도 다르다 (각주 ², §4). 관측으로만 쓴다.
- "학습 야코비안으로 행렬 site를 만들면 무너진다"를 testbed 한정 없이 쓰는 것. D1 형제에서는 나타나지 않았다 (§3.1).

---

## 2. H1 — 어디서, 얼마나 이기나

### 2.1 설정 (방법 절에 필요한 것만)

**수신기**
- M-ours 계열 arm은 R2-ours-G와 Module H만 다르다. Module H를 Gaussian으로 되돌리면 R2와 차이가 정확히 0이다 (test M2; `conf/results/tests.txt:35`, T:15-16) [코드]·[기록]. 따라서 b\*와 V1의 차이는 Module H의 prior뿐이다.
- 학습 prior의 site [코드]
  - 디노이저는 등방 질의 $(q,\nu_q)$에서 불린다 (`Demo/t2_route_a.py:349, :364`).
  - $\hat h=\mathbb E[h\mid q]$, 야코비안 $J$에서 $\Sigma_H=\nu_q\,\tfrac12(J+J^H)$ (`t2_route_a.py:310-311`).
  - site 정밀도 $\Lambda=\Sigma_H^{-1}-I/\nu_q$의 고유값을 `lam_min`에서 floor한다 (`:312-316`).
  - site 벡터 $\eta=\Sigma_H^{-1}\hat h-q/\nu_q$ (`:317`), 사후 $P=\Lambda+G$, $\hat h_{\rm post}=P^{-1}(\eta+b)$ (`:378`).
- V1 [코드]: 행렬 site를 만들기 전에 $J$의 Hermitian 부분 고유값을 `LAM_MIN` $=10^{-6}$에서 floor한다. $\lambda_{\max}$는 건드리지 않는다 (`conf/code/score.py:603-619`, `conf/code/common.py:51`; `ScorePrior(psd_project=True)`, T:22).
- GMM b\* [코드]: 비등방 cavity $(G,b)$ 아래 정확한 tilted-moment EP site를 쓴다 (`t2_route_a.py:276-277, :373-374`; `Demo/t2_gmm.py:54-60`). 사이트 계산은 GMM 쪽이 더 정확하다. 이것은 baseline을 약하게 만드는 방향이 아니다 [유도]. GMM 채널 prior 계열은 Koller 외 [R19]를 인용한다.
- 공통 [기록]: rate-1/2 conv (133,171) ν=6, QPSK, 모든 arm outer 16회, CPU complex128, 결정적 seed (T:4, T:6-7).

**testbed D2 [가정]**
- $\mathbf H=\sqrt{N_rN_t/L}\sum_{\ell}\alpha_\ell\,\mathbf a_r(\theta_\ell)\mathbf a_t(\phi_\ell)^H$, $L\sim\mathrm{Unif}\{3..8\}$, 각도는 연속이고 S2는 섹터 ±π/3이다 (`conf/05_SPEC_testbed_D2.md:13-21`).
- $|\alpha_\ell|$가 결정적이라 각도를 조건으로 줘도 $\mathbf H$가 Gaussian이 아니다 (`05_SPEC_testbed_D2.md:20, :25`). "조건부 Gaussian 파괴를 분리하는 통제된 희소 정반사 모델"로 적는다 (R:831).
- 블록 안 H는 주파수·시간에 평탄하다 (지연 항 없음, `05_SPEC_testbed_D2.md:13`). "RE 16개로 된 한 블록 = OFDM의 한 coherence region"과 "DFT 파일럿 4열(`conf/results/tests.txt:49`, T2b 결정) = 4-포트 CDM DM-RS"라는 대응은 추상화이고, 블록 사이 상관은 쓰지 않는다.
- 블록 페이딩이라 파일럿 열의 위치는 결과를 바꾸지 않는다 [기록]. C2 기하, 0 dB, D2 30 시행, 16 반복에서 파일럿 열끼리·데이터 열끼리 순서를 바꿔도 (파일럿은 앞 4열 유지) RouteA-G(해석적 앙상블 공분산을 쓰는 Gaussian prior Route A), R3-bigamp, R4-scvamp의 블록 오류 궤적이 30/30 같았다. NMSE 차이는 최대 2.73e-15 / 7.40e-09 / 1.71e-09다. 파일럿을 t = 0, 4, 8, 12에 흩어 놓은 배치는 site 수준에서만 확인했다: 고정 Tau 에서 채널 쪽 site $(G,b)$ 합의 상대차 4.79e-16. 위치를 아는 수신기가 열을 다시 정렬하면 배열이 앞 배치와 같아진다는 것이 동치의 근거다 [유도] (`conf/code/pilot_position_check.py` → `conf/results/review_next/pilot_position_check.txt:1-5`).
  - 학습 prior arm과 b\*는 이 검사에 없다. 이 arm들은 Module H만 다르고(M2), Module H는 열 순서와 무관한 $(G,b)$만 받으므로 같은 불변성이 성립한다고 본다 [유도].

**판정 규칙 [기록]**
- 앵커 b\*의 BLER이 0.1에 가장 가까운 3점을 판정점으로 고른다. 창은 [0.005, 0.9]다 (T:368; R:19).
- 판정점마다 짝지은 실패 지표로 양측 부호검정을 한다. 결과 파일은 같은 방향으로 유의한 판정점이 2/3 이상이면 `significant`로 출력한다 (예: `tables_D2_B1e4x.txt:592` `2/3 -> significant`, T:389 `1/3 -> not significant`).
- power guard: 판정점 3개 이상 가운데 2개 이상에서 불일치 쌍 ≥ 6. 미달이면 UNDECIDED다 (`conf/08_SPEC_analysis.md:46`).
- SNR@0.1 격차는 90% paired bootstrap으로 **보고하는 필드**이며 판정이 아니다.

### 2.2 어디서, 얼마나

**헤드라인 (C2, N=1.6e5, n=2560/SNR)** [기록]
- −3 dB BLER@16: b\* 0.243 (0.227, 0.260) → V1 0.145 (0.132, 0.159) (T:69, T:71). 4자리로는 0.2434 → 0.1449, V1 = 371/2560 (R:60).
- 부호검정: −3 dB 302:50, +0 dB 117:21, +3 dB 35:7, pooled 454:78 p=1.7e-65, POWERED, 3/3 `significant` (T:369-371).
- SNR@0.1 격차 +1.41 dB [+1.22, +1.64] (보고 필드, T:372).
- 맥락: R1-turbo 0.543, R2-ours-G 0.328, genie 참조 0.034 (T:63-64, T:75).

**예산 곡선 (C2 −3 dB, 전 arm 동일 N_train)** [기록]

| N_train | b\* (격자 상태) | 지위 | b\*→V1 pooled | SNR@0.1 격차 [90%] (보고 필드) | −3 dB BLER b\* → V1 | 출처 |
|---|---|---|---|---|---|---|
| 1e4 | kron 512 (내부. K=1024가 −0.0992 nat 낮다. 검증 집합 하나이고 restart 범위 0.43–0.59보다 작다) | 예산 축 측정 (D1 형제 게이트 FAIL) | 502:72, 3/3 | +1.68 [+1.47, +1.94] | 0.252 → 0.145 | `tables_D2_B1e4.txt:369-372`; R:53, R:116-117, R:124 |
| 4e4 | kron 2048 (격자 끝) | 예산 축 측정 (D1 형제 게이트 FAIL) | 459:79, 3/3 | +1.33 [+1.14, +1.53] | 0.248 → 0.145 | `tables_D2_B4e4k.txt:369-372`; R:56 |
| **1.6e5** | kron 1024 (격자 끝. K=512 대비 +3.18 nat로 오르는 중이고 K=2048은 적합하지 않음) | **헤드라인** (D1 형제 게이트 PASS 레시피) | 454:78, 3/3 | +1.41 [+1.22, +1.64] | 0.243 → 0.145 | T:69-71, T:369-372; R:117, R:128 |
| 3.2e5 | kron 4096 (격자 끝. K=2048 대비 +1.851 nat로 오르는 중에 사용자가 멈춤) | 등록 판정 `_best`: "동일예산 우위가 N′ = 3.2e5 에서도 유지" | 421:69, 3/3 (`_best`); 418:71 (last, 보고 전용) | +1.33 [+1.14, +1.53] (`_best`); +1.32 [+1.13, +1.52] (last) | 0.238 → 0.146 (`_best`) / 0.144 (last) | `tables_D2_B32e4.txt:370-373`, `tables_D2_B32e4last.txt:370-373`; R:186, R:192-193; `NEXT_EXPERIMENTS_B32e4.md:81` |

- V1의 −3 dB BLER은 네 예산에서 0.145 / 0.145 / 0.145 / 0.144(last)로 평평하다. 같은 구간에서 GMM b\*는 0.252 → 0.238로 내려간다 (R:210-213) [기록]. 예산 곡선에는 추세 검정이 등록되지 않았다 (R:206).
- 시드 반복 (N=1e4, D1 형제 게이트 FAIL 레시피) [기록]: 확산 체크포인트 시드 a1/a2/a3의 V1 BLER은 0.145 / 0.150 / 0.148이다. 세 시드 모두 3/3 `significant`, 격차 +1.68 / +1.68 / +1.71 dB (R:100-102; `tables_D2_B1e4s2.txt:369-372`, `tables_D2_B1e4s3.txt:369-372`). 4e4·1.6e5에는 시드 반복 표가 없다 (R:106).

### 2.3 왜 — 귀속

1. **Module H만 다르다.** M2 = 정확히 0 (`conf/results/tests.txt:35`) [기록]. 헤드라인 차이는 Module H의 prior 차이다.
2. **스칼라화 자체는 GMM을 돕지 않는다.** 필수 대조군 `b* → b*-scalar`는 C2 1.6e5에서 pooled 100:149 p=0.0023이다. b\*(행렬) 쪽 실패가 적다. 3점 규칙으로는 1/3이라 `not significant`다 (T:387-389). 같은 대조가 4e4 (K=2048)에서는 3/3 `significant` (R:92), C6 1.6e5에서는 2/3 `significant`로 b\* 쪽이다 (`NEXT_EXPERIMENTS_C6B16e4.md:106`) [기록]. 이 대조군의 설계 취지는 T:25에 있다: "스칼라화가 GMM도 도우면 이득은 site의 것"이다. 스칼라화가 GMM을 돕지 않으므로 V4가 b\*를 이긴 것도 site 효과로 읽히지 않는다 [유도].
3. **1차 디노이저가 더 좋다 (보고 전용).** 동일예산 3.2e5에서 확산/GMM 디노이징 NMSE 비는 20개 σ 전부 1보다 작다: 0.453–0.879, median 0.513, worst excess −0.121 (R:226) [기록]. 이는 등록된 해석(1차 통계는 정확하고 2차 구조는 부정확하다, `10_SPEC_stageC.md:269-271`)과 합치한다. 루프 안 BLER 이득이 이 1차 성능 차이에서 온다는 것은 가설이다 [유도].

### 2.4 이 기여에 붙는 등록 캐비엇 (§6에서 다시 모은다)

- **격자 끝 b\*.** 헤드라인 b\*(K=1024)는 실행 격자의 끝이다. 검증 ll은 K=512에서 1024로 가며 +3.18 nat 올랐다 (R:116-117, R:128; `NEXT_EXPERIMENTS_B32e4.md:16`).
  - K=2048@1.6e5를 적합하지 않은 이유: 4e4에서 K=2048의 BLER 효과가 −1%였고, 재시작 하나에 약 9시간이 든다 (`conf/DECISIONS.md:100`).
  - 헤드라인 격자 확장은 사용자가 승인하지 않았다 (`conf/DECISIONS.md:173`).
  - 완화 근거: 3.2e5에서 K=4096까지 넓혀도 격차는 +1.33 / +1.32 dB였다 (위 표). 4e4에서는 K=512/1024/2048의 GMM −3 dB BLER이 0.250 / 0.250 / 0.248이었다 (R:54-56) [기록].
- **등록 1차 결과는 V0 단독이었다.** "주 결과는 V0 하나다" (`10_SPEC_stageC.md:201`). V1은 BLER을 보기 전에 등록된 2차 메커니즘 변형이다 (`10_SPEC_stageC.md:190-195, :202`). V1을 헤드라인으로 올린 결정은 DECISIONS에 기록이 없다 (`conf/results/NUMBERS_PACKAGE_2026-09-22.md:555`). 등록 1차 arm V0는 b\*에 3/3으로 진다: pooled 109:5363 (T:363-365). "사전 등록"을 쓰려면 이 사실을 함께 공개한다 [기록].
- **V4는 사후 등록 변형이다** (T:23; `NUMBERS_PACKAGE_2026-09-22.md:556`).
- **게이트 표기.** D2 체크포인트에는 게이트 행이 없다 (T:45). 헤드라인은 "D1 형제 게이트 PASS 레시피 + 동일예산"으로 읽는다 (R:27-29, R:43).
- **평가 가중치.** 헤드라인은 best가 아니라 last-EMA @1784다 (best @1764 가중치 미저장, R:23). 통제 재학습의 best 대 last는 85 대 85, 6:6 p=1로 기각되지 않았다 (R:400) [기록].
- **Stage A/B 표의 원래 `M-ours-dscore` 판정은 BLOCKED 그대로다** (T:19-20; `10_SPEC_stageC.md:267`).
- **비용.** Module H 호출당 V1/b\* = 1.35× (−3 dB), 1.39× (+6 dB). 블록 전체로는 1.33× / 1.38×다 (`conf/results/review_next/complexity_moduleH_ep.txt:21-24`). CPU float64 1스레드로 쟀고, 측정 중 부하 평균이 26.5에서 5.2였으며 학습 2개가 동시에 돌았다. 학습 비용과 EM 적합 비용은 포함하지 않았다 (R:277, R:292) [기록].

### 2.5 가장 가까운 선행연구와의 차이

| 선행연구 | 공통점 | 차이 (우리 쪽) | 확인 수준 |
|---|---|---|---|
| Cai 외 [R5] (JADCE, arXiv:2506.00581) | turbo message passing 안의 score 기반 MMSE 디노이저. 2차 score 네트워크(Hessian 대각)로 분산을 만든다 | 파일럿 단계뿐이고 복호가 없다. 공분산은 공유 스칼라 분산(trace)이다. 3GPP CDL을 쓰고 GMM baseline이 없다 | 이번 대조: HTML v2 문장 |
| Cai 외 [R6] (STMP, arXiv:2512.14435) | 2차 score 네트워크로 turbo MP의 분산 계산 | 압축 영상(CT/MRI/SAR) 문제다. 분산은 스칼라(trace)다 | 이번 대조: HTML |
| Wadayama–Takahashi [R7] (arXiv:2601.07095) | 학습 score prior를 VAMP 안에 넣는다 | Jacobian-free이고 스칼라 Onsager다. 측정 모델은 $y=Ax+n$이고 채널 추정과 부호가 없다 | 제목 이번 대조, 내용은 검증자 확인 |
| Zhou 외 Diff-Rx [R10] (arXiv:2609.25923, 2026-09-22) | soft data decision을 diffusion 채널추정에 되먹인다 | FEC가 루프에 없고, 검출기는 점추정 채널만 쓴다. x0-예측 조건부 diffusion (1-step)이며 Bayes prior site가 아니다. 3GPP UMi + ray tracing, GMM baseline 없음 | 제목 이번 대조, 내용은 검증자 확인. **반드시 인용** |
| Sun 외 [R8] (arXiv:2404.07721) | 채널추정·검출·LDPC 복호를 한 학습 루프에서 함께 한다 | 생성 prior가 없고 unfolding/ADMM이다 | 이번 대조: abs |
| Zilberstein 외 [R11], Bhattacharya 외 [R12] | diffusion 결합 채널추정·검출 | Langevin 사후 샘플링 또는 SIC이고, 부호화·EP가 없다 | 검증자 확인 |
| Arvinte–Tamir [R13] | 학습 score 채널 prior, 부호화 성능 보고 | "최대 5 dB"는 **지도학습 추정기 대비** end-to-end 부호화 이득이다. 파일럿 기반 사후 샘플링이고 반복 루프가 없다. 따라서 "학습 prior가 부호화 성능을 개선한다" 자체는 우리 기여가 아니다 | 이번 대조: abs 문장 + Crossref |
| Fesl 외 WCL [R20] | DM 대 GMM (full K=128 / Kronecker) | 학습 표본 1e5 고정이고 파일럿 NMSE만 잰다. 우리는 1e4–3.2e5 예산 스윕, 부호화 BLER, 루프 안 비교, 사전 등록(등록 1차 arm 은 V0, §2.4)이다 | 서지는 이번 Crossref 대조, 내용은 검증자 확인 |
| Schniter [R14], Karataev 외 [R15] | 미지 채널 공동 추정·복호 / bilinear EP semi-blind JCD | 손으로 만든 prior(2-state GM + Markov)이거나, 학습 prior 여부를 초록으로 판단할 수 없다 | 서지 이번 대조 |
| Weißer 외 [R22][R23] | GMM/VAE semi-blind 추정 | 복호 루프가 없다 | 이번 대조: abs |

**신규성 판단 (반박 시도 뒤)** [기록: `contrib_verify.md` §2]
- 웹 검색 기준으로 다음 세 가지 선례는 찾지 못했다. IEEE 전문 DB는 보지 않았다.
  - 미지 채널 부호화 수신기에서 학습 디노이저의 전체 야코비안으로 EP/VAMP 행렬 site를 만든 연구
  - 그 site의 붕괴 사슬을 보고한 연구
  - 학습 diffusion 대 GMM을 부호화 BLER로 동일예산 스윕한 연구
- 따라서 H1의 신규성은 **조합과 비교 설계**에 있다: 미지 채널, 부호화 EP 루프, 공분산 있는 Bayes site로서의 학습 prior, 동일예산 GMM(정확 mixture EP site, 검증 우도로 K 선택; 헤드라인 예산에서는 격자 끝), 사전 등록(등록 1차 arm 은 V0 였고 V1 승격은 등록된 결정이 아님, §2.4).
- 구성 요소는 각각 출판돼 있다: MP 안의 학습 prior [R5][R16], 부호화 이득 [R13], 데이터 보조 diffusion 추정 [R10], DM 대 GMM 비교 [R20]. 채택 위험은 신규성보다 §6의 단일 testbed와 격자 끝에서 온다.

---

## 3. H2 — 왜 되고 왜 깨지나: 행렬 site의 붕괴와 PSD 투영

### 3.1 주장 (제한된 형태)

D2에서 학습 디노이저 야코비안으로 EP 행렬 site $\Sigma_H=\nu_q\,\mathrm{Herm}(J)$를 만들면 $\Sigma_H$가 부정부호가 되고, 수신기 루프가 발산하며 BLER이 붕괴한다. 네 학습 예산과 C6 모두에서 관측했다 (§3.2). 같은 레시피·예산의 D1 형제에서는 나타나지 않았다: $\mathrm{Herm}\,J$의 음의 고유값 비율은 20개 σ 전부 0.000이고 (`jacpsd_D1_N160000.log:8-27`), D1 C1에서 투영 없는 V0가 R2를 449:227, 3/3으로 이겼다 (`PAPER_MATERIALS.md:598`; 앵커가 R2이고, D1은 순환 testbed다). 부정부호가 site를 발산시키는 경로는 코드에서 유도한 것이고 방향별 측정은 없다 (§3.3). Hermitian 부분의 고유값 floor(V1)는 같은 체크포인트를 호출당 +0.2% 비용으로 쓸 수 있게 만든다. "비대칭이 아니라 여유가 가른다"는 **가설**로 쓰며, σ ≥ 0.4의 D1/D2 대조와 합치한다는 데까지만 쓴다.

### 3.2 붕괴 사슬의 근거 (같은 체크포인트, 같은 시행) [기록]

- C2 1.6e5 V0 (투영 없음)
  - BLER@16은 −3 / +0 / +3 dB에서 0.593 / 0.845 / 0.953이다. SNR이 오를수록 나빠진다 (T:70).
  - F3 발산 가드(16회 중 한 번이라도 NMSE > 10이거나 비유한) 발동률은 0.529 / 0.794 / 0.918이고, 최악 NMSE는 2.942e+09다 (`conf/results/guard_D2_B16e4k.txt:18-20`).
  - −3 dB에서 고전 turbo R1(0.543)보다도 나쁘다 (T:63).
- V1: 가드를 한 번도 발동하지 않은 12개 arm 목록에 들어 있다 (`guard_D2_B16e4k.txt:26`). −3 dB BLER은 0.145다 (T:71).
- 모든 예산에서 V0 가드가 발동한다: −3 dB에서 1e4 0.712, 4e4 0.702, 1.6e5 0.529, 3.2e5 0.542 (`_best`) / 0.715 (last) (R:53-58, R:192-193). 데이터를 늘려도 이 실패는 사라지지 않았다.
- C6 (Nr=16) 1.6e5: V0는 −3~+9 dB에서 BLER 1.000, 가드 1.000이다 (`NEXT_EXPERIMENTS_C6B16e4.md:108`). V1은 −3 dB에서 0.021이다 (`conf/results/tables_D2_NR16B16e4.txt:72`).

### 3.3 코드 경로와 발산 기전

- [코드] V0에도 site 정밀도 $\Lambda$의 고유값 floor가 있다 (`t2_route_a.py:314-316`). 그런데 $\eta=\Sigma_H^{-1}\hat h-q/\nu_q$ (`:317`)는 floor 전의 $\Sigma_H^{-1}$을 그대로 쓴다.
- [유도] $\mathrm{Herm}(J)$의 고유값 $\lambda_j$가 음수이거나 0에 가까운 방향을 보자.
  - 그 방향에서 $\Sigma_H^{-1}$의 고유값은 $1/(\nu_q\lambda_j)$로 크기가 폭주한다.
  - $\Lambda$는 floor 때문에 $10^{-6}$까지만 올라간다. 그래서 그 방향의 사후 $\hat h_{\rm post}=(\Lambda+G)^{-1}(\eta+b)$ (`:378`)가 $G$가 작은 방향에서 커질 수 있다.
  - 이것은 가드 발동(NMSE > 10)과 합치하는 경로다. 방향별 분해 측정은 없다.
- [유도] V1은 $\lambda_j\ge10^{-6}$로 올리므로 그 방향의 $\Sigma_H^{-1}$ 고유값이 양수로 유한해진다. 사후공분산이 거의 특이한 방향("채널 다양체에 수직인 방향")을 강하게 믿는 site가 된다.
- [기록] V1 대 V0 비용: 호출당 60.304 대 60.186 ms, 블록 1006 대 1005 ms (R:283-284).

### 3.4 판별자 가설 — 교정된 수치

인용 금지 행(`jac_spectrum.txt:173` "D2 asym", R:859)은 쓰지 않는다. 아래는 다음 두 로그의 값이다.
- `conf/logs/jacpsd_D2_final.log`: 헤드라인 ckpt `d2sx_N160000_a1`, 128 표본/점, σ 20점
- `conf/logs/jacpsd_D1_N160000.log`: 같은 레시피·예산의 D1 형제 `sx_N160000_D1`

로그 표기: `asym(Jr)`는 실 야코비안의 상대 비대칭, `f<0`은 $\lambda_{\min}<0$인 표본 비율이다. 수신기가 실제로 쓰는 것은 $\mathrm{Herm}(J)$ 열이다.

| 양 | D2 (학습, 1.6e5) | D1 형제 (학습, 1.6e5) | 출처 |
|---|---|---|---|
| asym(Jr) 범위 | 0.146–0.299 | 1.88e-3–9.82e-2 | D2 로그 :8-27, D1 로그 :8-27 |
| $f(\lambda_{\min}(J_r)<0)$ | σ ≤ 0.216에서 ≥ 0.977 | 20점 전부 0.000 | D2 :8-19, D1 :8-27 |
| **$f(\lambda_{\min}(\mathrm{Herm}\,J)<0)$** | σ ≤ 0.182에서 0.81–1.00. σ=0.216에서 0.84, 0.256에서 0.48, 0.304에서 0.49. **σ ≥ 0.36에서 0.03–0.20** | 20점 전부 0.000 | D2 :8-27, D1 :8-27 |
| 같은 격자 번호 k에서 D2/D1 asym 비 [유도: 로그 값의 비] | k=0 (σ≈0.033) 105×, k=6 (≈0.09) 26×, k=12 (≈0.25) 7.2×, k=18 (≈0.7) 1.8×. **k=15–19 (σ ≥ 0.40) 1.5–3.4×** | — | 두 로그 :8-27 |
| 적합 GMM의 $\lambda_{\min}(J)$ (여유의 대리지표). **N=1e4 적합의 b\***이며 헤드라인 b\*(K=1024, N=1.6e5)가 아니다 (`conf/code/jacobian_psd.py:84`가 `common.py:47`의 N_TRAIN=10000으로 선택) | kron K=512 (N=1e4): 5.9e-5–4.7e-3 | kron K=32 (N=1e4): 0.028–0.938 | D2 :31-50, D1 :31-50 |

- **σ ≲ 0.25 (부호가 뒤집히는 영역)에서는 교란돼 있다.** 두 testbed의 비대칭 크기가 7–105배 다르다. 이 영역의 D1/D2 대조로는 "비대칭이 아니라 여유"를 가를 수 없다 [유도].
- **σ ≥ 0.4에서는 가설과 합치한다.** 비대칭 비가 1.5–3.4배로 좁혀져도, D2 Herm J의 부호 뒤집힘은 0.03–0.18이고 D1은 0이다 [기록 + 유도]. 원고에는 "σ ≥ 0.4에서 관측된 D1/D2 대조와 합치하는 가설"로 쓴다. 여차원을 통제한 실험은 없다.
- **"64개 중 26~41개가 0.1 미만"은 학습 모델의 개수다.** 평균은 26.52 / 37.58 / 41.10 / 35.50이다 (`conf/logs/jacspec_D2_final.log:17-20`, n=48). 참 스펙트럼의 값이 아니다.
  - D2에는 폐형식 prior가 없어 참 스펙트럼을 잴 수 없다 (`PAPER_MATERIALS.md:450-451`).
  - 적합 GMM(K=512, N=1e4)은 3.44–16.94개다 (`jacspec_D2_final.log:24-27`).
  - 여차원 40–55는 support 차원 3L에서 나온 이론값이다 (`jacspec_D2_final.log:29`) [유도·기록].
- 기록 위생: `jacpsd_D1_N160000.log:1`의 머리말 문자열은 "held-out D2 samples"라고 적는다. 그러나 σ 격자(3.2936e-02…)와 GMM(K=32)은 D1의 것이다. 원고에 인용하기 전에 생성 스크립트로 확인할 것 [기록].
- 적어 둘 긴장: Fesl 외 AISTATS [R21]는 DM 디노이저가 MSE 조건부 평균 추정기로 수렴한다고 논한다. 그 추정기의 J는 PSD다. 우리 측정과 양립하는 읽기는 이렇다: 그 결과는 점근적이고 디노이저 값(1차)에 관한 것이다. 학습 모델의 미분은 오차를 증폭할 수 있다 (Meng 외 [R25]). solenoidal 오차는 샘플링에서 드러나지 않는다 (Khelifa 외 [R29]) [유도: 문헌 읽기].

### 3.5 V1이 정확 GMM 위에서 항등인가 (M6)

- `conf/results/selftest_M6_2026-09-22.txt:5-7`: 정확 GMM kron K=512, 4σ × 16 표본. 투영의 최대 상대변화는 2.146e-13이다. 4개 σ에서 관측한 $J$의 최소 고유값은 7.835e-04다 (`LAM_MIN` = 1e-6). 이 4점 값의 배수는 인용하지 않고, 여유는 아래 줄의 전 격자 값으로 쓴다. `ALL M6 ASSERTIONS PASSED` (`:23`) [기록].
- σ 20점 전체로 보면 여유는 더 작다. D2 GMM-exact (N=1e4 적합 kron K=512, 위 표 마지막 행과 같은 적합)의 $\lambda_{\min}(J)$ 최솟값은 5.887e-05 (k=11, `jacpsd_D2_final.log:42`)이고, **약 59배**다 [유도: 5.887e-5 / 1e-6]. `PAPER_MATERIALS.md:482`의 "76배"와 "780배"는 쓰지 않는다.
- **헤드라인 b\*(K=1024)에서는 재지 않았다.** M6의 학습 prior 부분([2])도 헤드라인이 아니라 `d2sx_N10000_a1.pt`로 쟀다 (`selftest_M6_2026-09-22.txt:2`).
- 기록끼리 어긋난다: R:865와 `NUMBERS_PACKAGE_2026-09-22.md:738`은 아직 "Test M6 결과 없음"으로 적는다. 결과 파일은 존재한다. 원고 전에 기록 정정이 필요하다 [기록]. 이 어긋남은 `conf/DECISIONS.md:205` 항목 (3)에 기록돼 있다.

### 3.6 공개 사항

- V0→V1 짝지음 검정은 어느 표에도 없다 (R:82). 0.593 → 0.145는 점추정이고, V0 가드율과 함께 인용한다 (R:65).
- 등록 1차는 V0 단독이었고, V1 승격 기록은 없다 (§2.4).
- 보고 전용 calibration: C2 held-out에서 V1 사영 공분산의 cov90(명목 0.90)은 0.71–0.80이다. GMM b\*는 0.79–0.88이다 (R:312-313) [기록]. V1 site는 과소 포함(under-coverage)이다.
- 대안 수리 두 가지는 D1 게이트에서 FAIL했다.
  - **V2** (에너지 매개화 $s=-\nabla E$, 구성상 대칭): GC 0.167 FAIL (`PAPER_MATERIALS.md:332`). 동결 lr에서 두 번 발산해 lr/3으로 학습됐다. 매개화와 lr이 교란돼 있다 (`PAPER_MATERIALS.md:344-347`).
  - **V3** (야코비안 비대칭 정칙화 λ=1.0): GB 0.059 / GC 0.353 / GD 0.345 FAIL (`conf/11_PRIOR_ART_JACOBIAN.md:105`).
  - 둘 다 arm이 아니고, D2 BLER 표가 없다 (R:854).
- [유도] 에너지 매개화는 대칭만 보장한다. $J=I-\sigma^2\nabla^2E$는 대칭이지만 $\nabla^2E\preceq I/\sigma^2$가 아니면 PSD가 아니다. 붕괴가 부호 문제라면 V2만으로는 막지 못할 수 있다. 이 추론은 BLER로 검정되지 않았다.
- 여유로 Chao 외 [R28]와의 충돌을 설명하려던 시도는 철회됐다 (`11_PRIOR_ART_JACOBIAN.md:98-117`). 논문에서 "우리 V3 실패가 여유 가설의 증거"라고 쓰지 않는다.

### 3.7 선행연구와 남는 부분

| 선행연구 | 이미 있는 것 | 우리에게 남는 것 |
|---|---|---|
| Rozet 외, NeurIPS 2024 [R1] | 학습 디노이저 J로 Tweedie 공분산 $\mathbb V[x\mid x_t]\approx\Sigma_t\nabla^\top d_\theta$를 만들어 moment matching에 쓴다. "the Jacobian … is not always perfectly SPD"를 보고하고, CG를 1–3회로 잘라 완화한다 (HTML v2 §4.2, 이번 대조) | 일반 ML에서 선점됐다. **JAPS보다 앞선다** |
| TMPD, Boys 외 [R2] | 전체 야코비안으로 Tweedie moment projection을 한다. 실무에서는 대각이나 row-sum으로 근사한다 (검증자 확인) | 비-PSD 문제는 다루지 않는다 |
| JAPS, Hen 외, TMLR 2026 [R3] | 학습 J의 비-PSD·비대칭 관측(§3.2 Fig. 2). 주 testbed는 D=256, K=8 합성 GMM이다 (검증자 확인. `11_PRIOR_ART_JACOBIAN.md:26`의 "D=32"는 틀림) | 이미징 사후 샘플링이고, PSD 투영은 쓰지 않는다 |
| Higham 1988 [R4] | 가장 가까운 대칭 PSD 행렬 | 투영 자체는 교과서적이다 |
| Shastri 외 D-GEC [R30] | EC 안의 학습 디노이저에 서브밴드 대각 divergence(MC 추정)를 쓴다 | 행렬 site를 만들지 않아 이 문제를 비켜 간다 |
| Cai 외 [R5][R6], Wadayama–Takahashi [R7] | 2차 score(Hessian 대각) 또는 Jacobian-free 스칼라 분산 | 스칼라다 |
| Meng 외 [R25], Manor–Michaeli [R24], Reehorst–Schniter [R26], Terris 외 [R27], Chao 외 [R28], Khelifa 외 [R29] | 디노이저 고차 도함수의 오차 증폭, 사후 고차 모멘트, 학습 디노이저의 비대칭과 그 수리 | — |

- **H2에 남는 신규성:** 미지 채널 부호화 수신기 안에서 학습 야코비안 전체로 EP 행렬 site를 만든 사례, 그 붕괴 사슬(부정부호 $\Sigma_H$ → site 발산 → BLER 붕괴), 그리고 배치 전에 held-out $f(\lambda_{\min}(\mathrm{Herm}\,J)<0)$를 세서 점검하는 절차다 (`PAPER_MATERIALS.md:473-476`) [기록].
- 여유 기준의 두 절반으로 `11_PRIOR_ART_JACOBIAN.md:50-52`가 든 문헌(Stanczuk ICML 2024 [R31], Ventura ICLR 2025, Mohan ICLR 2020, Horvat–Pfister ICLR 2024)은 [R31]만 이번에 서지를 대조했다. 나머지는 인용 전에 원문 확인이 필요하다.

---

## 4. H3 — 어디서 더 이기나: Nr 8 → 16 (C6)

- **설계** [기록]: Tp·T·부호·SNR은 C2와 같고 Nr만 16이다 (C6 = 16×4; R:713).
- **1.6e5 측정 판정** (태그 `_best`) [기록]
  - −3 dB 실패 수: b\* 184 / V1 53 / genie 22 (`NEXT_EXPERIMENTS_C6B16e4.md:103`).
  - b\*→V1: 142:11 · 45:4 · 26:3, pooled 213:18 p=1.8e-43, POWERED, 3/3 (`:94`).
  - SNR@0.1 격차는 `n/a`다. 두 arm 모두 −3 dB에서 이미 0.1 아래다 (`:94`).
- **회수율** [기록]: $(b^*-\mathrm{V1})/(b^*-\mathrm{genie})$ = 0.809 [90% 0.747, 0.870]. 사전 등록 대역 R ≥ 0.70 "기하 효과 대부분 유지"에 든다 (`:97`, 대역 규칙 `:36`). 나란히 놓을 값은 다음과 같다 (`:97`).
  - C6 1e4: 0.838 [0.781, 0.892]
  - C2 1.6e5 헤드라인: 0.470 [0.427, 0.512]
- **지위** [기록]: UNGATED다(D1 형제 없음). "기하·예산 축 측정, arm 판정 아님"이다 (`:92`; R:719, R:721). 1.6e5 점은 1e4 결과를 본 뒤 고른 예산이라 예측은 약한 예측이다 (`:5`).
- **해석 위험** [유도]
  - Nr 8→16은 실수 주변차원을 $2N_rN_t$ = 64에서 128로 두 배로 만든다 (64는 `jacspec_D2_final.log:29`의 식).
  - support 차원 3L은 그대로이므로 여차원은 {40..55}에서 {104..119}로 커진다 [유도].
  - 여차원 증가와 GMM 파라미터 부담 증가를 이 실험으로는 분리할 수 없다. 그래서 "여차원 축"이라는 이름은 가설로만 쓴다.
  - 두 셀은 Nr 말고도 다르다 [기록]: b\* K가 C2 1024 (R:117), C6 4096 (`NEXT_EXPERIMENTS_C6B16e4.md:81`)이다. C6 가중치는 §3d 시행 2다 (`:83`). 1.6e5 예산은 C6 1e4 결과를 본 뒤 골랐다 (`:5`). 두 셀 모두 1.6e5 확산 시드는 하나다 (R:106; C6 `d2sx_NR16_N160000_a1`, `:30`). 그래서 0.47 → 0.81은 단일 요인 비교가 아니라 관측으로 쓴다.
- **추가 캐비엇** [기록]
  - C6 1.6e5의 b\*(kron K=4096)도 격자 끝이다. K=2048 대비 +1.193 nat로 오르는 중에 사용자가 멈췄다 (`NEXT_EXPERIMENTS_C6B16e4.md:81`).
  - 1.6e5 학습의 §3d 시행 1은 발산했다. 수치는 모두 시행 2(기울기 클리핑 1.0, 등록된 사다리)의 가중치다 (`:83`, `:111`, 사다리 규칙 `:31`).
  - **C6 GMM 수렴 (09-26 기록 추가).** b\*인 kron K=4096 재시작 2(163 iter, best@160)를 포함해 K=4096 재시작 셋이 모두 학습 우도 증가량 < tol 규칙으로 멈췄다 (`Demo/t2_gmm.py:164`; 재시드 때문에 증가량이 음수가 된 순간). 셋 모두 검증 우도가 마지막 평가 시점(10 iter 간격)에서 최고였다. 검증 우도가 아직 오르던 중이었을 수 있고, 그 방향은 V1에 유리하다. C2 헤드라인 b\*(K=1024)는 patience(40)로 멈췄다(331 iter, best@290). 동결 EM 프로토콜 그대로라 규칙 위반은 아니고, 수치·판정은 바뀌지 않는다. 회수율 0.809와 측정 판정을 인용할 때 격자 끝 캐비엇과 함께 붙인다 (`NEXT_EXPERIMENTS_C6B16e4.md:135`; `conf/DECISIONS.md:205`).
    - 기록 위생: `:135`는 규칙 위치를 `Demo/t2_gmm.py:162`로 적는다. 현재 파일(커밋 54d68a14와 같음)의 `:162`는 patience 규칙이고, 학습 우도 규칙은 `:164`다.
  - C6 1e4 표 머리말은 학습 arm 예산을 `N_train=1610000`으로 잘못 적었다. 이 표기를 다룬 정정 기록은 없다 (R:722).
  - V0가 C6 전 SNR에서 붕괴하는 것(§3.2)은 여유 가설 쪽이지만 체크포인트 하나다.
- **선행연구**: Stanczuk 외 [R31]가 개념 배경이다. Arvinte–Tamir [R13]는 큰 배열을 다루지만 여차원 분석은 없다. 부호화 수신기에서 GMM 대비 학습 prior의 이득을 Nr의 함수로 잰 작업은 찾지 못했다 (검증자, 웹 검색 기준).

---

## 5. 보조 분석과 각주

### 5.1 (e) V1 대 생성모형을 아는 Bayes 참조 (K1, 보고 전용)

- C2 −3 dB, 개발 시행 3200..4479, n=1280의 실패 수: b\* 307, V1 173, BR-S 167, LO-S 80, genie 53 (`conf/results/review_next/NEXT_EXPERIMENTS_K1K2.md:170-174`) [기록].
- R1′ V1→BR-S 26:20, p=0.46, MDD 16 → **판정하지 못함** (`:176`).
- R2′ BR-S→LO-S 95:8, p=5.1e-20 → 잠재(각도) 정보 몫 87블록 (`:177`).
- C5 −3 dB에서도 V1 230 대 BR-S 229다 (`:179`).
- 한계 (`:181`): BR은 완화 모형에 유한 MCMC를 쓴다. "V1이 이 루프에서 더 갈 수 없다"로 쓰지 않는다.

### 5.2 (f) 격자 밖 질의 규칙 V1-edge (C1 한계의 각주)

- 테스트 확증, C1 −3 dB, n=2560 [기록] (`NEXT_EXPERIMENTS_K1K2.md:152-160`)
  - 실패 수: b\* (kron K=1024) 1906, 동결 V1 2515 (가드 2560), V1-edge 1770, V1-clamp 1783, genie 95.
  - b\*→V1-edge 400:264, p=1.5e-7 → 확증 통과. 기전 V1→V1-edge 758:13.
  - clamp↔edge 75:62, p=0.31, MDD 25 → **판정하지 못함** (`:190`).
- 격차 위치는 +0.075다. genie까지의 격차는 대부분 남는다 (`:156`).
- 개발 1차 검정은 198:134, p=0.00053이고, 이 계열 1차 검정 3건에 Holm을 적용해도 유지된다 (`:132`).
- 별도 arm이며 **등록 C1 판정은 바뀌지 않는다** (`:162`).
  - 주의: `:162`는 3.2e5 C1을 "등록 판정"이라고 적는다. 그러나 `NEXT_EXPERIMENTS_B32e4.md:34`는 C5·C1 표를 보고 전용으로 등록했다. 원고의 등록 C1 판정은 1.6e5 (K=512) 1109:1691이다 (§6).

---

## 6. 범위와 한계 (등록 캐비엇 전부; 원고의 마지막 절)

1. **단일 합성 testbed.** 주장은 D2 하나에 있다. D1은 순환 testbed(참 prior = 격자 GMM)라 학습 prior에 대한 주장이 옮겨지지 않는다 (`PAPER_MATERIALS.md:632-633`).
   - D2 사양에는 "[추측, VERIFY]" 표시를 단 추측이 있다: CDL을 그대로 가져오면 오히려 GMM에 유리할 수 있다 (`05_SPEC_testbed_D2.md:33`; `NUMBERS_PACKAGE_2026-09-22.md:565`). 검증되지 않은 추측이다. 사양이 근거로 드는 것은 GMM 채널추정 계열([R19], Fesl 외 Asilomar 2022)이다.
   - 두 번째 testbed는 준비 중이다 (§7 Q1).
2. **Tp < Nt에서는 이기지 않는다.**
   - C1 (Tp=2) 등록 판정: 1.6e5 (GMM K=512)에서 1109:1691, p=3.1e-28, `first arm fewer failures at 3/3` → **GMM 우세** (`tables_D2_B16e4.txt:806-810`; R:144).
   - 1e4는 1372:1632, 2/3 GMM 우세다 (`tables_D2_B1e4x.txt:590-592`). 3.2e5는 1168:1761, 3/3 GMM 우세지만 **보고 전용**이다 (`tables_D2_B32e4x.txt:593-595`; `NEXT_EXPERIMENTS_B32e4.md:34`).
   - C1 −3 dB에서 V1 가드는 2560/2560 발동한다 (R:156).
   - C5 (Tp=3): 1.6e5 (K=512)에서 623:640, p=0.65, 1/3 대 1/3 → **판정하지 못함** (`tables_D2_B16e4.txt:1088-1090`).
     - 1e4에서는 793:667, 2/3 V1 우세 `significant`다. 이 값은 예산 축 측정이다 (R:141).
     - 3.2e5에서는 662:640, `not significant`이고 보고 전용이다 (R:222).
   - 1.6e5 셀 표의 GMM은 K=512이며, K=1024로 다시 돌리지 않았다 (R:135).
   - 교차 Tp 포락선(TABLE C)은 계산되지 않았다 (`NUMBERS_PACKAGE_2026-09-22.md:564`).
3. **격자 끝 b\*.** 1.6e5 (K=1024), 3.2e5 (K=4096), 4e4 (K=2048), C6 1.6e5 (K=4096) 모두 격자 끝이다. 내부로 판정된 것은 1e4 (K=512)뿐이다. 이 판정은 K=1024가 −0.0992 nat 낮다는 검증 집합 하나의 값에 기대고, 그 차이는 같은 K 안의 restart 범위 0.43–0.59보다 작다 (R:124). `DECISIONS.md:94`의 "b\* 내부가 증명된 N=1e4"는 이 뜻으로 읽는다. C6 1.6e5의 b\*는 격자 끝이면서 덜 수렴됐을 수 있다 (§4 추가 캐비엇).
4. **등록 이탈 공개** (`NUMBERS_PACKAGE_2026-09-22.md:553-566`)
   - V0 단독 1차를 V1로 바꿨다.
   - V4는 사후 등록이다.
   - V4b는 등록 뒤 누락됐다가 추가됐고, D1에서는 실행하지 않았다.
   - §6f 예측은 비맹검이다.
   - TABLE C는 계산하지 않았다.
5. **보고 필드와 판정의 구분.** SNR@0.1 격차는 보고 필드다. 1e4·4e4 점은 예산 축 측정이다 (R:45). genie 쌍은 전부 UNDECIDED다 (R:68). 회수율은 계산 수치다 (R:203). C6는 UNGATED다.
6. **체크포인트 표기.** "D1 형제 게이트 PASS/FAIL 레시피"로 쓴다. D2 체크포인트에는 게이트 행이 없다 (R:27-29). 평가 가중치는 last-EMA다 (R:23).
7. **R4-scvamp는 알고리즘이 아니라 인터페이스 적응이다.**
   - 채널추정은 고전 APP-LMMSE이고, Onsager extrinsic 인터페이스만 [R17]을 따른다 (T:12; `conf/09_PRIOR_ART_NOTE.md:22`).
   - 헤드라인 표에서 R2-ours-G의 SNR@0.1은 R4-scvamp보다 5.77 dB 낮다: 필드 −5.77 dB [−6.50, −5.15] (T:306). Stage A/B의 −5.6 dB는 쓰지 않는다.
8. **R3-bigamp(BiG-AMP [R18])는 구조적 한계로 i.i.d. prior를 쓴다.** 상관 prior를 넣을 방법이 없다 (T:10; `09_PRIOR_ART_NOTE.md:37`).
9. **비용 맥락.** 1.35×는 추론 Module H만이다. 학습 비용과 EM 비용은 빠져 있고, 측정 조건은 §2.4에 적었다. 참고로 1.6e5 K=1024 EM은 재시작 하나에 GPU 1장으로 4.5~6시간이 걸렸다 (`DECISIONS.md:100`).
10. **OFDM 해석은 추상화다.** 블록 안 채널이 평탄하고 블록 사이 상관을 쓰지 않는다. "파일럿 4열 = 4-포트 CDM DM-RS" 대응도 추상화다 [가정]. 파일럿 열의 그룹 내 순서에 궤적이 불변이고(`pilot_position_check.txt:2-4`), 흩어 놓은 배치는 site 수준만 확인했다(`:5`); 학습 prior arm 은 유도 (§2.1).

---

## 7. 리뷰어 질문 — 미리 막아 둘 것

**Q1. 합성 testbed 하나뿐이다. 실제 채널에서도 되는가?**
- 현재 답: D2는 조건부 Gaussian성을 깨도록 설계한 통제 모형이다. 그 선택 이유(`05_SPEC_testbed_D2.md:25`)와, "표준 채널에서는 GMM이 유리할 수 있다"는 사양의 추측(`:33`, "[추측, VERIFY]" 표시)을 추측이라고 밝혀 그대로 공개한다.
- 진행 중인 작업: 두 번째 testbed를 준비하고 있다. 계획은 `docs/plans/2026-09-25_sionna_deepmimo_gmm_vs_dm.md`, 준비 기록은 `conf/DECISIONS.md:203`이다.
  - 후보는 채널 통계(조건부 비-Gaussian성, 희소성, 다봉성)로만 고르고 수신기 BLER로 고르지 않는다. 판정은 별도 사전 등록에서 결과를 보기 전에 고정한다.
  - Sionna 2.1.0이 설치됐다.
  - scratch 탐색(판정 무관): UMi 28 GHz 8×4에서 LOS 블록 조건부 4차 모멘트 비의 중앙값은 1.50으로 비-Gaussian이고, NLOS는 약 2.00으로 Gaussian이다 [기록].
- 주의: 사용자 지시는 "proposed 에 유리할 수 있는 데이터셋"이다 (`DECISIONS.md:203`). 선택 근거를 원고에 공개하지 않으면 cherry-picking으로 읽힌다. 계획 문서의 대조군(near-Gaussian에서는 GMM ≥ DM, `2026-09-25_sionna_deepmimo_gmm_vs_dm.md:25`)도 같이 돌려 보고해야 한다.
- 결과가 원고 마감 전에 없으면 한계 절에 "단일 합성 testbed"로 남긴다.
- 비교 가능한 공개 자료: Fesl WCL [R20]의 데이터셋(Zenodo 20737830, 검증자 확인)으로 파일럿 NMSE를 먼저 맞춰 볼 수 있다.

**Q2. b\*가 격자 끝이다. GMM을 더 키우면 따라잡지 않는가?**
- 헤드라인 K=1024는 +3.18 nat로 오르는 중이고, K=2048은 적합하지 않았다. 사유는 비용과 4e4의 −1% BLER 효과다 (`DECISIONS.md:100`). 격자 확장은 승인되지 않았다 (`DECISIONS.md:173`).
- 답이 되는 측정 두 가지:
  - 3.2e5에서 K=4096까지 넓힌 b\*에도 격차는 +1.33 / +1.32 dB, 3/3이다.
  - 4e4에서 K를 512→2048로 넓히는 동안 GMM BLER은 0.250 → 0.248이었다 (R:54-56).
- 원고에는 "격자 끝" 캐비엇을 표 머리말에 적는다.

**Q3. 스칼라 대안이 있는데 왜 행렬 site인가?** (Wadayama–Takahashi [R7], Cai 외 [R5][R6], D-GEC [R30])
- 우리는 행렬 site를 이득의 원천으로 주장하지 않는다. V4 스칼라 site도 +1.27 dB로 이기고, V1↔V4 직접 검정은 없다 (§0).
- 행렬 site를 쓰는 이유:
  - GMM은 행렬(정확 EP) site에서 스칼라화보다 실패가 적었다: C2 1.6e5 pooled 100:149 p=0.0023이지만 3점 규칙으로는 1/3 `not significant`, 4e4 K=2048에서 3/3, C6 1.6e5에서 2/3 `significant` (§2.3).
  - 같은 수신기 인터페이스로 두 prior를 비교하려면 학습 prior에도 행렬 site가 필요하다.
  - V1은 그 행렬 site를 +0.2% 비용으로 쓸 수 있게 만든다.
- 보조 자료 (약함): D1 C1에서 V0 행렬 site 449:227 3/3, V4 1/3 (`PAPER_MATERIALS.md:598`). 앵커가 R2이고 V1이 아니라 V0이며, D1은 순환 testbed다. C6 1.6e5 −3 dB에서 V1 53 대 V4 65 실패 (`_best`, `conf/results/review_next/k1k2c6_review_raw/recompute.out:176`), last-EMA로는 52 대 68이다 (`:180`). 직접 검정은 없다.

**Q4. 에너지 기반(보존장) diffusion을 쓰면 되지 않는가?** (Diao 외 [R9], Chao 외 [R28])
- 우리 V2(에너지 매개화)는 D1 게이트 GC 0.167로 FAIL했다. lr/3 교란이 있다. V3(비대칭 정칙화)도 FAIL했다 (§3.6).
- 대칭을 구성으로 보장해도 PSD는 보장되지 않는다 [유도]. 붕괴가 부호 문제라면 보존장만으로는 부족할 수 있다. 이 추론은 BLER로 검정되지 않았으므로 그렇다고 적는다.

**Q5. Tp < Nt(파일럿 부족)에서는?**
- 등록 판정으로 C1 (Tp=2)은 GMM 우세, C5 (Tp=3)는 판정하지 못함이다 (§6-2). 원고의 동작 범위 문장은 "Tp = Nt = 4 셀에서 등록 판정"으로 한정한다.
- C1 −3 dB 붕괴는 K2의 기전 검정과 합치한다: V1→V1-edge 758:13이고, V1-edge에서는 F3 가드가 한 번도 발동하지 않았다 (`NEXT_EXPERIMENTS_K1K2.md:155-156, :160`). 격자 밖 질의가 붕괴의 충분조건은 아니라는 반대 기록도 있다 (`:18`). V1-edge 규칙은 별도 arm으로 b\*를 넘는다 (400:264). 이것은 각주로 두고 등록 판정을 바꾸지 않는다 (§5.2).

**Q6. genie 참조까지 얼마나 남았나?**
- genie 쌍은 전부 UNDECIDED다. 회수율 0.470은 계산 수치다.
- K1(보고 전용)에서 V1은 생성모형을 아는 q-측정 참조와 판정하지 못함이다. BR-S→LO-S 95:8은 남은 격차의 큰 몫이 잠재 정보일 수 있음을 시사한다. BR은 완화 모형과 유한 MCMC를 쓴다 (§5.1).

**Q7. R4-scvamp는 허수아비 아닌가?** 인터페이스 적응임을 명시한다 (§6-7).

---

## 8. 참고문헌 (확인 수준 표기)

**확인 수준**
- **[이번 대조]**: 이 문서를 쓰며 arXiv abs/HTML, Crossref, PMLR 페이지에서 제목·저자·서지를 직접 대조했다.
- **[검증자 확인]**: `contrib_verify.md`가 원문을 확인했고, 이번에 다시 대조하지 않았다.
- **[미확인]**: 인용 전에 원문 확인이 필요하다.

**선행연구 여섯 건 (검증에서 추가)**
- [R1] F. Rozet, G. Andry, F. Lanusse, G. Louppe, "Learning Diffusion Priors from Observations by Expectation Maximization," NeurIPS 2024. arXiv:2405.13712.
  - [이번 대조] arXiv abs(제목·저자), HTML v2 §4.2 문장(비-SPD, CG 1–3회).
  - NeurIPS 게재는 proceedings 검색 결과로 확인했다. 쪽수는 [미확인].
- [R2] B. Boys, M. Girolami, J. Pidstrigach, S. Reich, A. Mosca, O. D. Akyildiz, "Tweedie Moment Projected Diffusions For Inverse Problems," TMLR. arXiv:2310.06721.
  - [이번 대조] arXiv abs. arXiv 표기는 "For"다.
  - TMLR 게재는 검색 결과(OpenReview)로 확인했고, 연도·권호는 [미확인]이다.
  - 전체 야코비안과 대각/row-sum 근사에 관한 서술은 [검증자 확인].
- [R5] C. Cai, W. Jiang, X. Yuan, Y.-J. A. Zhang, "Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors," arXiv:2506.00581 (v2 2026-02-07).
  - [이번 대조] abs와 HTML v2 문장: "second-order score network that outputs the Hessian diagonals … to compute the variance", "shared scalar variance", 3GPP CDL, GMM 없음, 복호 없음.
  - 게재지는 [미확인]이다. IEEE Xplore 11389767의 저널명을 확인하지 못했다.
- [R6] C. Cai, H. Jiang, X. Yuan, Y.-J. A. Zhang, "Score-Based Turbo Message Passing for Plug-and-Play Compressive Imaging," arXiv:2512.14435 (arXiv 코멘트 "IEEE Transactions on Signal Processing").
  - [이번 대조] abs와 HTML 문장: "second-order score network that outputs the diagonals of the log-density Hessian". 응용은 압축 영상이다.
  - 권호는 [미확인]. 검증자가 적은 "게재 승인 2026-07-29"는 이번에 대조하지 않았다.
- [R7] T. Wadayama, T. Takahashi, "Score-Based VAMP with Fisher-Information-Based Onsager Correction," arXiv:2601.07095 (2026-01-11). [이번 대조] 제목·저자·날짜. §VII-B 내용은 [검증자 확인].
- [R8] Y. Sun, H. Shen, B. Li, W. Xu, P. Zhu, N. Hu, C. Zhao, "Trainable Joint Channel Estimation, Detection and Decoding for MIMO URLLC Systems," arXiv:2404.07721 (arXiv 코멘트 "accepted by IEEE Transactions on Wireless Communications").
  - [이번 대조] 초록: JCDD와 LDPC는 있고 생성 prior는 없다.
  - 권호·DOI는 [미확인]. 방법 이름 "JCDDNet"은 검증자 표기이고 초록에서는 확인하지 않았다.
- [R9] Z. Diao, X. Zhou, L. Liang, S. Jin, "Robust MIMO Channel Estimation Using Energy-Based Generative Diffusion Models," arXiv:2510.22230 (2025-10-25, "submitted to the IEEE"). [이번 대조]

**수신기·채널추정**
- [R10] W. Zhou, Z. Zhang, Z. Kong, Z. Yang, "MIMO-OFDM AI Receiver Based on Incrementally Conditioned Diffusion with Soft Decision," arXiv:2609.25923 (2026-09-22). [이번 대조] 제목·저자·날짜. 본문 서술은 [검증자 확인].
- [R11] N. Zilberstein, A. Swami, S. Segarra, "Joint channel estimation and data detection in massive MIMO systems based on diffusion models," ICASSP 2024, arXiv:2311.10311. [검증자 확인]. 쪽수 13291–13295는 검색으로만 확인했다.
- [R12] N. Bhattacharya, A. Mohsin, M. Rajabalifardi, J. M. Cioffi, "Successive Interference Cancellation-aided Diffusion Models for Joint Channel Estimation and Data Detection in Low Rank Channel Scenarios," ICASSP 2025 (arXiv 코멘트 기준), arXiv:2501.11229. [검증자 확인]. 저자 이름 머리글자는 [미확인].
- [R13] M. Arvinte, J. I. Tamir, "MIMO Channel Estimation Using Score-Based Generative Models," IEEE TWC 22(6):3698–3713, Jun. 2023, DOI 10.1109/TWC.2022.3220784, arXiv:2204.07122.
  - [이번 대조] Crossref와 abs 문장: "gains of up to 5 dB in end-to-end coded communication performance compared to supervised deep learning methods".
- [R14] P. Schniter, "A Message-Passing Receiver for BICM-OFDM Over Unknown Clustered-Sparse Channels," IEEE JSTSP 5(8):1462–1474, Dec. 2011, DOI 10.1109/JSTSP.2011.2169232, arXiv:1101.4724.
  - [이번 대조] Crossref로 DOI가 이 제목으로 풀린다. 검증자의 "DOI 미확인"은 해소됐다.
- [R15] A. Karataev, C. Forsch, L. Cottatellucci, "Bilinear Expectation Propagation for Distributed Semi-Blind Joint Channel Estimation and Data Detection in Cell-Free Massive MIMO," arXiv:2312.11688 (코멘트 "to be printed in IEEE Open Journal of Signal Processing").
  - [이번 대조] 제목·저자. 최종 권호는 [미확인].
- [R16] H. He, C.-K. Wen, S. Jin, G. Y. Li, "Deep learning-based channel estimation for beamspace mmWave massive MIMO systems," IEEE WCL 7(5):852–855, 2018. [검증자 확인]. DOI와 저자 머리글자는 [미확인].
- [R17] T. Wadayama, T. Takahashi, "Three-Module SC-VAMP for LDPC-Coded Nonlinear Channels," arXiv:2604.19061. [검증자 확인] 기지 채널, 세 모듈, LDPC BP. 본문 기록은 `conf/09_PRIOR_ART_NOTE.md:8-22`에 있다.
- [R18] J. T. Parker, P. Schniter, V. Cevher, "Bilinear Generalized Approximate Message Passing — Part I," arXiv:1310.2632. R3 baseline의 출처다 (`09_PRIOR_ART_NOTE.md:26-37`). 정확한 제목·게재지는 [미확인].

**GMM 계열과 DM 대 GMM**
- [R19] M. Koller, B. Fesl, N. Turan, W. Utschick, "An Asymptotically MSE-Optimal Estimator Based on Gaussian Mixture Models," IEEE TSP 70:4109–4123, 2022, DOI 10.1109/TSP.2022.3194348, arXiv:2112.12499. [이번 대조] Crossref.
- [R20] B. Fesl, M. Baur, F. Strasser, M. Joham, W. Utschick, "Diffusion-Based Generative Prior for Low-Complexity MIMO Channel Estimation," IEEE WCL 13(12):3493–3497, Dec. 2024, DOI 10.1109/LWC.2024.3474570, arXiv:2403.03545.
  - [이번 대조] Crossref. 검증자의 "검색으로만 확인"은 해소됐다.
  - 실험 설정(Mtrain 1e5 고정, MSE)은 [검증자 확인].
- [R21] B. Fesl, B. Böck, F. Strasser, M. Baur, M. Joham, W. Utschick, "On the Asymptotic Mean Square Error Optimality of Diffusion Models," AISTATS 2025, PMLR 258:505–513, arXiv:2403.02957.
  - 제목·저자는 [이번 대조]. PMLR 쪽수는 [검증자 확인].
- [R22] F. Weißer, N. Turan, D. Semmler, W. Utschick, "Data-Aided Channel Estimation Utilizing Gaussian Mixture Models," arXiv:2308.16601. [이번 대조]
- [R23] F. Weißer, N. Turan, D. Semmler, F. Ben Jazia, W. Utschick, "Semi-Blind Strategies for MMSE Channel Estimation Utilizing Generative Priors," arXiv:2504.17573. [이번 대조]
- (추가) B. Fesl, M. Joham, S. Hu, M. Koller, N. Turan, W. Utschick, "Channel Estimation based on Gaussian Mixture Models with Structured Covariances," Asilomar 2022, pp. 533–537, DOI 10.1109/IEEECONF56349.2022.10051921, arXiv:2205.03634.
  - [이번 대조] Crossref. 검증자의 "DOI 미확인"은 해소됐다.

**디노이저 야코비안·score**
- [R3] L. Hen, T. Tirer, R. Giryes, S. Abu-Hussein, "Jacobian-Aware Posterior Sampling for Inverse Problems," TMLR 2026 (arXiv 코멘트 "Accepted by TMLR 2026"), arXiv:2511.18471.
  - [이번 대조] 제목·저자·코멘트. §3.2 문장과 D=256은 [검증자 확인].
- [R4] N. J. Higham, "Computing a nearest symmetric positive semidefinite matrix," Linear Algebra Appl. 103:103–118, May 1988, DOI 10.1016/0024-3795(88)90223-6. [이번 대조] Crossref.
- [R24] G. Manor, T. Michaeli, "On the Posterior Distribution in Denoising: Application to Uncertainty Quantification," ICLR 2024, arXiv:2309.13598. [검증자 확인]
- [R25] C. Meng, Y. Song, W. Li, S. Ermon, "Estimating High Order Gradients of the Data Distribution by Denoising," NeurIPS 2021. [검증자 확인] "can amplify estimation errors".
- [R26] E. T. Reehorst, P. Schniter, "Regularization by Denoising: Clarifications and New Interpretations," IEEE TCI 5(1):52–67, Mar. 2019, DOI 10.1109/TCI.2018.2880326, arXiv:1806.02296.
  - [이번 대조] Crossref. 검증자의 "DOI 검색으로만 확인"은 해소됐다.
- [R27] M. Terris, T. Moreau, N. Pustelnik, J. Tachella, "Equivariant Plug-and-Play Image Reconstruction," CVPR 2024, arXiv:2312.01831. [검증자 확인]. 쪽수 25255–25264는 검색으로만 확인했고, DOI는 [미확인].
- [R28] C.-H. Chao, W.-F. Sun, B.-W. Cheng, C.-Y. Lee, "On Investigating the Conservative Property of Score-Based Generative Models," ICML 2023, arXiv:2209.12753. [검증자 확인]. 저자 머리글자는 [미확인].
- [R29] N. B. Khelifa, R. E. Turner, R. Venkataramanan, "Diffusion Models Observe Only Gradients: A Geometric Perspective on Score Matching Errors," arXiv:2606.06179 (2026-06-04). [이번 대조]
- [R30] S. K. Shastri, R. Ahmad, C. A. Metzler, P. Schniter, "Denoising Generalized Expectation-Consistent Approximation for MR Image Recovery," IEEE JSAIT 3(3):528–542, Sep. 2022, DOI 10.1109/JSAIT.2022.3207109. [이번 대조] Crossref.
- [R31] J. P. Stanczuk, G. Batzolis, T. Deveney, C.-B. Schönlieb, "Diffusion Models Encode the Intrinsic Dimension of Data Manifolds," ICML 2024, PMLR 235:46412–46440.
  - arXiv:2212.12611의 제목은 "Your diffusion model secretly knows the dimension of the data manifold"다. 게재판으로 인용한다.
  - [이번 대조] PMLR 페이지.

**인용 전 확인이 필요한 것 [미확인]**
- `11_PRIOR_ART_JACOBIAN.md:16, :50-52`가 든 Ventura (ICLR 2025), Mohan (ICLR 2020), Horvat–Pfister (ICLR 2024), Cohen (NeurIPS 2021).
- Valenti–Woerner (JSAC 2001, 데이터 보조 turbo 추정의 고전).
- Kim 외 WCL 2026 (DOI 10.1109/LWC.2026.3689648, 초록만 확인).
- 참고만 할 것: Zhang 외 CFM-Rx (arXiv:2602.21654), Jiang 외 MoE-DM + VB (arXiv:2605.18325). 검증자가 초록 수준으로 본 것이다.

**이번 대조에 쓴 페이지**: [arXiv 2405.13712](https://arxiv.org/abs/2405.13712), [HTML v2](https://arxiv.org/html/2405.13712v2), [NeurIPS 2024 proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/hash/9f94298bac4668db4dc77ddb0a244301-Abstract-Conference.html), [arXiv 2310.06721](https://arxiv.org/abs/2310.06721), [OpenReview TMPD](https://openreview.net/forum?id=hDzjO41IOO), [arXiv 2512.14435](https://arxiv.org/abs/2512.14435), [HTML 2512.14435](https://arxiv.org/html/2512.14435), [arXiv 2506.00581](https://arxiv.org/abs/2506.00581), [HTML v2 2506.00581](https://arxiv.org/html/2506.00581v2), [arXiv 2601.07095](https://arxiv.org/abs/2601.07095), [arXiv 2404.07721](https://arxiv.org/abs/2404.07721), [arXiv 2510.22230](https://arxiv.org/abs/2510.22230), [arXiv 2609.25923](https://arxiv.org/abs/2609.25923), [arXiv 2511.18471](https://arxiv.org/abs/2511.18471), [arXiv 2403.03545](https://arxiv.org/abs/2403.03545), [arXiv 2403.02957](https://arxiv.org/abs/2403.02957), [arXiv 2606.06179](https://arxiv.org/abs/2606.06179), [arXiv 2312.11688](https://arxiv.org/abs/2312.11688), [arXiv 2308.16601](https://arxiv.org/abs/2308.16601), [arXiv 2504.17573](https://arxiv.org/abs/2504.17573), [arXiv 2204.07122](https://arxiv.org/abs/2204.07122), [PMLR v235 Stanczuk](https://proceedings.mlr.press/v235/stanczuk24a.html), Crossref `api.crossref.org/works/<DOI>` (LWC.2024.3474570, JSTSP.2011.2169232, TWC.2022.3220784, TSP.2022.3194348, TCI.2018.2880326, IEEECONF56349.2022.10051921, JSAIT.2022.3207109, 0024-3795(88)90223-6).

---

## 9. 이 문서가 읽은 저장소 파일

- 결과·기록
  - `docs/RESULTS.md`
  - `conf/results/tables_D2_B16e4k.txt`, `tables_D2_B16e4.txt`, `tables_D2_B1e4.txt`, `tables_D2_B1e4s2.txt`, `tables_D2_B1e4s3.txt`, `tables_D2_B1e4x.txt`, `tables_D2_B4e4k.txt`, `tables_D2_B32e4.txt`, `tables_D2_B32e4last.txt`, `tables_D2_B32e4x.txt`, `tables_D2_NR16B16e4.txt`
  - `conf/results/guard_D2_B16e4k.txt`, `conf/results/tests.txt`, `conf/results/selftest_M6_2026-09-22.txt`, `conf/results/NUMBERS_PACKAGE_2026-09-22.md`, `conf/results/review_next/pilot_position_check.txt`
  - `conf/results/review_next/NEXT_EXPERIMENTS_B32e4.md`, `NEXT_EXPERIMENTS_C6B16e4.md`, `NEXT_EXPERIMENTS_K1K2.md`, `complexity_moduleH_ep.txt`, `k1k2c6_review_raw/recompute.out`
  - `conf/logs/jacpsd_D2_final.log`, `conf/logs/jacpsd_D1_N160000.log`, `conf/logs/jacspec_D2_final.log`
- 사양·결정
  - `conf/10_SPEC_stageC.md`, `conf/08_SPEC_analysis.md`, `conf/05_SPEC_testbed_D2.md`, `conf/DECISIONS.md`, `conf/PAPER_MATERIALS.md`
  - `conf/09_PRIOR_ART_NOTE.md`, `conf/11_PRIOR_ART_JACOBIAN.md`
  - `docs/plans/2026-09-25_sionna_deepmimo_gmm_vs_dm.md`
- 코드
  - `Demo/t2_route_a.py` (`:276-277`, `:309-318`, `:346-378`), `Demo/t2_gmm.py:54-60, :162-164`
  - `conf/code/score.py:603-619`, `conf/code/common.py:47, :51`, `conf/code/jacobian_psd.py:84`, `conf/code/pilot_position_check.py`
