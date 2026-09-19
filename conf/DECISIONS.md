# DECISIONS — 자율 판단 기록

> 지침이 모호해서 Claude Code가 스스로 정한 것을 한 줄씩 append한다. 지우지 않는다.
> 형식: `[시각] 모호했던 점 | 선택 | 근거 | 되돌리는 법`

---

`[2026-09-20 00:30 KST] exp_0915_bcjr_score_check.py 경로 | 지침은 Demo/ 라 했으나 실재 위치는 Demo/archive/ | 01_RULES §4 "repo가 정본" | conf/code/runner.py 의 LEMMA_SRC 상수만 바꾸면 된다`
`[2026-09-20 00:30 KST] R0-pilot 의 "1-pass" | mode='pilot_only' 를 16 반복으로 돌려 raw 에 전 궤적을 남기되 결과 표에서는 반복 index 0 (= 1 패스) 값을 R0-pilot 으로 읽는다 | 06_SPEC "turbo 루프 없음" 을 만족하면서 paired 실현/시드를 전 arm 과 공유하려면 이 방법뿐. 16 반복 값도 pilot_C 로 같이 보고 | 분석에서 index 를 -1 로 바꾸면 됨`
`[2026-09-20 00:30 KST] diffusion 학습 데이터의 train/val 분할 | GMM 이 받은 것과 동일한 N_train=1e4 표본(시드 [20260925,7,prior_id,Nr])을 9:1 로 쪼개 9000/1000 사용. GMM 이 쓴 별도 검증셋 5000 은 diffusion 에 주지 않는다 | 04_SPEC §2 "동일 N_train, 9:1 분할" 을 둘 다 만족. 결과적으로 diffusion 이 GMM 보다 데이터가 적다 = 우리 주장에 불리한 쪽 | score.py 의 VAL_FRAC`
`[2026-09-20 00:30 KST] D1 의 GMM 적합 재사용 | Demo/exp_0925_fits/ 의 기존 적합(동일 훈련셋 정의, K{16,32,64} x full/kron, 검증 우도 선택)을 그대로 읽어 쓴다. 새로 적합하지 않는다 | (i) 테스트 M1 "기존 arm 과 로그 차이 0.0" 이 성립하려면 동일 적합이어야 한다 (ii) BLER 보기 전에 확정된 b* 를 그대로 승계 = 재선택 여지 없음. D2 는 05_SPEC §4 대로 새로 적합한다 | conf/code/arms.py 의 D1_FITS`
`[2026-09-20 00:30 KST] sigma_t 격자 측정에 쓸 수신기 | 04_SPEC §3 은 "R2-ours-G 를 돌려 Module H 가 받는 cavity 정밀도"라 했으나 R2-ours-G(=lmmseC_pf)는 mode='colored' 라 Module H 를 질의하지 않는다(nu_q 가 NaN). 대신 score arm 과 동일한 인터페이스(scal='belief', hsite='matrix')에 Gaussian 표본공분산 prior 를 넣은 수신기의 nu_q 를 쓴다 | "수신기가 실제로 질의하는 범위"가 격자를 정한다는 §3 의 목적에 이 쪽이 정확히 부합. Module H 만 Gaussian 인 M-ours-G 와 같은 경로 | runner.py sigma 서브커맨드`
`[2026-09-20 00:30 KST] D2 채널 정규화 | 05_SPEC §1 의 sqrt(Nr*Nt/L) 와 "sum_l p_l = 1" 을 동시에 쓰면 E||H||_F^2 = Nr*Nt/L 이 되어 L~Unif{3..8} 에서 T2a(오차 1e-3)를 구조적으로 위반한다. 표준 관례(sum_l E|alpha_l|^2 = L)와 등가가 되도록 sqrt(Nr*Nt) * (sum p_l = 1) 로 고정 | 두 관례는 수학적으로 동일하고, 이 쪽만 T2a 를 만족. 경로 수 L 이 블록마다 변해도 평균 전력이 일정해야 SNR 정의가 유지된다 | conf/code/d2.py 의 SCALE`
`[2026-09-20 01:20 KST] 테스트 S4 (R4-llr == R1-turbo 로그 차이 0.0) | N/A-BY-CONSTRUCTION 으로 기록하고 측정된 격차(max|dBER| = 0.82)를 남긴다. 대신 S4 가 잠그려던 성질(=llr 모드가 정확히 고전 extrinsic 을 내보낸다)을 새 테스트 S4b 로 잠갔다 | 02_SPEC §2.2(c)+§2.3 이 R4 에 스칼라 분산 SISO-LMMSE + APP-LMMSE 채널추정을 지정했고, R1 은 RouteA 'colored' 의 행렬 site EP + per-column R_n 이다. 두 수신기는 구조가 달라 항등이 성립할 수 없다(지침 내부의 불일치). arm 을 빼면 09_PRIOR_ART_NOTE 가 요구한 Onsager-vs-LLR ablation 자체가 사라지므로, 검증은 S1/S2/S3/S4b/S5/S6 로 하고 표 헤더에 S4 N/A 를 명시한다 | S4 를 항등 테스트로 되돌리려면 R4 의 Module C/채널추정을 R1 과 같게 바꿔야 하는데 그러면 R4 가 아니다`
`[2026-09-20 01:20 KST] (R5)-(R8) 의 구현 형태 | nu^s 를 (R7) 문자 그대로 (1-nu^z/nu^p)/nu^p 로 쓰지 않고 AWGN 폐형식 1/(nu^p+sigma^2) (원문 식 72) 로 구현 | 두 식은 대수적으로 같지만 (R7) 철자는 sigma^2 >> nu^p 에서 상대오차 ~eps*(1+sigma^2/nu^p) 로 상쇄된다(실측 6.0e-10). 02_SPEC §1.2 가 "적분하지 말고 이 폐형식으로 직접 구현한다"고 지시한 그대로다. (R7) 의 부호와 항등성은 테스트 B6 가 확장정밀도로 따로 잠근다 | bigamp.awgn_out 의 nu_s 한 줄`
`[2026-09-20 01:20 KST] 테스트 B1/B4 의 무감쇠 기준 궤적 | 참조 코어(bigamp_iter_plain)가 같은 AWGN 폐형식을 쓰도록 맞췄다. B4 는 beta=0.7(생산 설정) 궤적에서 상대오차로 측정 | beta=1 무감쇠 BiG-AMP 는 Gaussian prior 에서 수치적으로 발산해(nu^p -> 4e10) 1e-16 반올림이 12 반복 만에 1e-5 로 증폭된다. 그 상태에서 항등을 재면 damping 배선이 아니라 궤적 불안정성을 재게 된다. B1 은 damping 만, B2/B6 는 (R5)-(R8) 만 잠그도록 역할을 분리 | tests.test_B1/test_B4`
`[2026-09-20 01:20 KST] C4 셀 SNR 격자 | 4x4 Tp=4 셀은 exp_0925 에 대응 격자가 없다. 01_RULES §4 fallback 의 "Tp=4 -> 0,3,6,9 dB" 와 exp_0925 R 셀(4x4 Tp=2: 9/12/15)의 간격을 맞춰 3/6/9 dB 로 둔다 | fallback 표를 따르되 R 셀과 같은 3점·3 dB 간격을 유지해 교차-Tp 비교가 가능하게 함 | common.CELLS['C4']['snrs']`
