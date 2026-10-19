# NEXT_EXPERIMENTS_V1LS — 학습 σ 범위 아래 질의의 V1 처리: 고 SNR 붕괴의 해소와 b\* 대비 이득 (UMi28 · D2 C2 8×4, QPSK · 16-QAM) — 사전 등록 v2.2

작성 2026-10-18 CDT (Opus 5.5). 사용자 결정: WORK_QUEUE 11 · 13 — "9 -12 모두 제안대로 하자" (V1 고 SNR 붕괴 원인을 개발 시행으로 진단), "위 내용은 제안대로 진행" (해결 후보 셋 — σ 자르기, 범위 밖 GMM 대체, 더 낮은 σ 재학습 — 을 진행; test 는 등록 동결 뒤 사용자 승인).

v2 작성 2026-10-18 20:54 CDT (Fable 5.1 subagent, Claude 의뢰): 적대적 검토 `prereg_reviews_2026-10-18/review_V1LS.md` (MUST 4 · SHOULD 6 · NIT 7) 반영. 판정 규칙 — L1 · L2 의 검정 · 임계값 · 판정점 정의 — 는 v1 과 같다. 더한 것은 MONOTONE · SUFFIX · ΣF · R 출력, 다중성 문구, 판정 순서 명시뿐이다. 이 문서의 §0–§5 는 **test 를 보기 전에** 브랜치 `v1-lowsig` 에 커밋한다. **FREEZE** = v2 와 남은 검토를 반영한 뒤 `v1-lowsig` 를 main 에 병합한 커밋. **실행 커밋** = 그다음 `results/review_next/v1ls/v1ls_s5.txt` (§5) 를 더한 커밋 — `code/run_v1ls.sh` 가 요구하는 조건: HEAD 가 s5 를 마지막으로 건드린 커밋, s5 의 FREEZE 가 HEAD 의 조상, FREEZE..HEAD 사이에 `code/` · `Demo/` 변경 없음.

v2.1 작성 2026-10-18 21:22 CDT (Fable 5.1 subagent, Claude 의뢰): v2 (1586a508) 에 대한 Codex 교차 검토 (`~/t2/reviews/20261019-110034-prompt_pretest_v1ls.md`, 결함 2) 와 verifier 검토 (결함 2, 선택 개선 2) 반영. 판정 규칙 (검정 · 임계값 · 판정점) 은 바꾸지 않았다. 코드 변경은 `v1ls_compare.py` 의 SUFFIX 하나 (99f62bfb).

v2.2 작성 2026-10-18 21:43 CDT (Fable 5.1 subagent, Claude 의뢰): v2.1 (90783ce3) 의 verifier 재검토 — 결함 2 (문구: 데이터 분할의 출처, 정지 epoch · 인용 줄 번호) 와 선택 개선 2 반영. 판정 규칙 · 코드 변경 없음.

v1 → v2 (검토 항목마다 한 줄):
- M1: §0 의 test 시행 사용 이력 문장 교체 (σ 격자 측정이 test 번호 시행 0..63 을 썼다는 사실, 동결 격자 · 옛 HS 격자의 SNR 범위, 등록 V1 의 학습 σ 범위 출처); C 를 학습 σ 범위의 하한을 개발 시행 2560..2623 에서 다시 잰 격자 (상한은 등록 V1 과 같은 동결 격자) 로 다시 학습한 체크포인트로 교체 (§1.1 표 · WIDE 두 줄 · C 서술), 선택 규칙 재적용 결과 (§0).
- M2: §2.1 L1 (a) 의 "(고 SNR 붕괴 해소)" 와 (c) 의 "(해소하지 못함)" 삭제; §1.4 에 MONOTONE 조건, §2.1 에 MONOTONE = yes 일 때만 붙이는 괄호 문구.
- M3: §1.4 에 판정점 ΣF (b\*, X, genie) · R · 90 % paired bootstrap, SUFFIX 조건 (코드 그대로); §2.1 에 접미 규칙 (라벨 불변).
- M4: 판정점 SNR 의 개발 해 없음 확인 — 기준은 결과 전 커밋 (08e47ec2), 결과 표를 §0 에.
- S1: §0 에 PRIMARY 근거의 paired 크기 (옛 C · 새 C) 와 커밋 시각.
- S2: §0 · §2.1 에 16-QAM L1 = E5 와 같은 test 시행의 재평가, QPSK +18 · +21 dB 는 V1 에게도 새 점, V1 의 QPSK 붕괴 보고 방식 (여섯 arm 표; 원 QPSK 등록 라벨 불변).
- S3: §1.4 에 다중성 (run 4 × 라벨 2 = 8, 보정 없음, run 마다 문장 단독, 4/4 는 채점용).
- S4: §1.3 에 체인 스크립트 · 시작 조건 · 실패 때 정지; 머리말 · §5 에 FREEZE 와 실행 커밋; §5 에 스모크 G · 청크 시간 · 추정 시간.
- S5: §5 에 플래그 없음 확인 (셀 · 변조마다 +18 dB 개발 청크, V1 · b\* · genie 비트 동일).
- S6: §1.1 C 서술 — 로그 균등 추출, 격자 측정 시행, D2 는 role last, attempt 하나 (v2.1 Codex 1: 초기화는 통제되지 않음).
- N1: §1.4 L1 판정 순서 (a) → (c) → (b).
- N2: 줄 머리가 `WIDE_U28 ` · `WIDE_D2 ` 인 줄은 문서 전체에서 하나씩 (옛 sha 9298…3175 · 4531…ae5e 는 줄 머리에 두지 않는다).
- N3: §0 LSchk 의 대조 키 (blk_err · nmse) 와 arm (genie 없음) 정정; 새 C 의 WIDECHK 추가.
- N4: §3 예측 3 을 "수용 ③ 통과 시 사실상 기계적" 으로 표시.
- N5: §1.1 에 A 가 DECISIONS 2026-09-20 의 "clamp 하지 않고 외삽" 과 어긋나는 변형이라는 한 줄.
- N6: §3 예측 5 를 p 값 대신 방향 · 크기로.
- N7: §1.3 수용 ② 에 16-QAM payload 90 · protocol E5-qam16-v1 검사 (E5 와 맞춤).

v2 → v2.1 (항목마다 한 줄; 출처 Codex · verifier):
- Codex 1 (수용) — 가중치 초기화는 통제되지 않았다: `score.py:895` 의 `make_model` 은 전역 PyTorch RNG 로 초기화하고, rung · attempt 가 정하는 시드 (`score.py:900`, SEED_TRAIN + rung·17 + attempt) 는 학습 추첨 전용 Generator 다; 학습 길이 · 정지 epoch 도 다르다 (U28: V1 399 · C 513 정지, 쓰는 best 379 · 493; D2: V1 1784 · C 1028). §1.1 C 서술 · §2.1 고정 문장 · §1.6 을 "같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피, 학습 σ 범위의 하한을 낮춰 다시 학습; 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름" 으로 제한하고, §2.2 에 "σ 범위만의 효과" 를 더했다.
- Codex 2 = verifier A (수용) — C 격자 상한의 출처: 하한은 개발 시행 2560..2623 에서 다시 잰 HSd · UMi28HSd 의 하한, 상한은 등록 V1 과 같은 동결 격자의 상한 (0.8451555 · 0.8372515; test 번호 시행 0..63 의 라벨 없는 질의 통계, DECISIONS 4c08302d). 머리말 M1 줄 · §0 M1 불릿 · §1.1 표 머리 · §2.1 고정 문장을 고쳤다 (§1.1 C 서술은 v2 에서 이미 그렇게 적혀 있었다).
- verifier B (코드 99f62bfb) — §1.4 SUFFIX 를 지금 코드에 맞췄다: 같은 SNR 은 한 번만, 판정점으로 이미 들어간 점은 다시 넣지 않음, 라벨 (ii) 에서는 +18 · +21 dB 의 b\* 접미를 붙이지 않음.
- verifier 선택 개선 ① — §2.1 문장 꼴: MONOTONE = no 의 괄호 꼴, L1 (c) 의 두 SNR, 문장에 붙는 것의 순서 고정.
- verifier 선택 개선 ② — §3 예측 6 · 7 의 채점 기준 줄 (compare 출력의 `PRIMARY LABELS`) 명시, 예측 7 의 근거에 12 점 screen 의 b\*:C 점별 표.
- verifier 추가 확인 — §4 · §5 에 병합 확인 (FREEZE 의 main 에서 여섯 arm 개발 청크 비트 대조 + meta `lowsig_s_lo`) 과 그 기록 위치; §4 검토 상태 갱신.

v2.1 → v2.2 (항목마다 한 줄; 출처 verifier 의 v2.1 재검토):
- 결함 1 — 데이터 분할의 출처: 분할은 `training_split` (`score.py:653–664`) 이 고정 시드 SEED_SPLIT = 20260926 (`score.py:77`) 으로 만들어 rung · attempt 와 무관하다 ("the same split for every rung and every attempt"); `score.py:900` 의 g 는 학습 추첨 (randperm · σ · ε) 에만 쓰인다. 머리말 Codex 1 줄 · §1.1 C 서술 · §2.1 V1-wide 설명의 "(데이터 분할 · 학습 추첨 시드)" 를 "(학습 추첨 시드)" 로 줄이고, 분할은 데이터 쪽에 적었다.
- 결함 2 — 정지 epoch: 379 · 493 은 U28 의 best epoch 이고 정지 epoch 는 V1 399 (`d2sx_UMi28_N160000_a1.pt`, patience) · C 513; D2 는 V1 1784 · C 1028 (쓰는 것 = 마지막 epoch; best 1764 · 1008). 같은 세 곳과 §1.1 표의 V1 칸을 고쳤다. 인용 줄 번호 `score.py:897` → 895 (make_model 호출; 897 은 `_EMA`), `arms.py:174` → 175 (s_lo assert; 174 는 주석).
- 선택 개선 3 — §2.1 (c) 의 SNR 판별: L1 줄의 p 는 `.2g` 라 0.0495 ≤ p < 0.0505 가 모두 p=0.05 로 보인다 → 그 a:b 로 `analysis.sign_p` 를 다시 계산해 정한다 (라벨은 코드가 정한다).
- 선택 개선 4 — §5: 실행 시작 DECISIONS 줄은 s5 와 같은 커밋 (실행 커밋) 에 넣는다 (`run_v1ls.sh` 는 HEAD = s5 를 마지막으로 건드린 커밋을 요구하므로 s5 뒤의 별도 커밋은 ABORT).

## 0. 알고 있는 것 (판정에 쓰지 않는다; E5 test 의 기록 외에는 모두 개발 시행)

- **E5 test** (`NEXT_EXPERIMENTS_E5QAM16.md` §6): 16-QAM 두 셀 모두 V1 이 +18 · +21 dB 에서 첫 데이터 보조 반복 (반복 2) 부터 붕괴 (실패 / 2560: UMi 1844 · 2543, D2 2485 · 2557); b\* · V1-pilot 은 붕괴 없음.
- **진단** (`qam16/diag_v1/SUMMARY.md`, 개발 시행 5440..5479): QPSK 도 같은 SNR 에서 붕괴 (QPSK test 는 −3 … +15 dB 만 평가했다); 같은 배선에 넣은 b\* GMM (`gmmB-scorew-eta`) 은 정상; 합성 질의로 네트워크 denoiser 가 학습 σ 격자 하한 s_lo 의 약 0.9 배 아래에서 망가짐 (MSE/ν 10–10⁵); 반복 2 의 질의 σ 는 +15 dB 1.0 s_lo, +18 dB 0.72 s_lo, +21 dB 0.52 s_lo. 원인은 범위 밖 외삽으로 보인다 (개발 시행; 한계는 SUMMARY).
- **변형 후보와 개발 선택** (`lowsig/`): A = V1-clamp, B = V1-gmmfb, C = V1-wide (§1.1). 선택 규칙 `lowsig/SELECTION_RULE.md` 는 큰 선별 결과 전에 커밋했다 (1f4c5c4c, 10-18 17:21:28 CDT; 큰 선별의 첫 출력은 17:41). 개발 평가 집합: 12 점 (두 셀 × 두 변조 × +15 · +18 · +21 dB, 점마다 n = 320; 16-QAM 시행 5120..5439, QPSK 6000..6319), 지표 M = 반복 16 실패 합.
  - 옛 C (격자 HSU · UMi28HSU) 의 결과 `lowsig/select_lowsig.out` (a97161be, 18:24:52 CDT): M — V1 2279, b\* 148, A 114, B 122, C 104; +15 dB 해 없음 조건 (V1 55, 한계 69.83) A 55 · B 55 · C 53 통과 → PRIMARY = C.
  - 검토 M1 · M4 의 추가 절 (`SELECTION_RULE.md` "추가", 08e47ec2, 18:51:00 CDT) 은 개발 격자 측정 · M4 실행 · C 재학습이 시작되기 (18:51 · 18:51 · 18:57 CDT) 전에 커밋했다. 5af1b147 (18:58:23 CDT; 격자 HSd · UMi28HSd · HSUd · UMi28HSUd, 선택 스크립트의 'd' 세트, M4 확인 코드) 도 결과 (M4_DONE 19:26, TRAIN_CD_DONE 20:28, EVAL_CD_DONE 20:38 CDT; `logs/diag_lowsig.log`) 보다 앞이다.
  - **새 C (격자 HSUd · UMi28HSUd, §1.1) 로 같은 규칙 재적용** `lowsig/select_lowsig_d.out` (9fe40517, 20:40:38 CDT): M — V1 2279, b\* 148, A 114, B 122, **C 110**; +15 dB 해 없음 조건 (V1 55, 한계 69.83) A 55 · B 55 · C 56 통과 → **PRIMARY = C** (옛 C 와 같은 결과). 새 C 는 21 개 개발 점 모두에서 격자 밖 질의 0 (`lowsig/screenCd_*.txt`).
  - **PRIMARY 근거의 크기** (S1; 같은 개발 시행의 paired, 표기 a = 앞 arm 만 실패 : b = C 만 실패, 반복 16, 12 점 합, exact 양측 부호검정; 출처 `lowsig/screen_*_320_snr*.npz` · `screenCd_*.npz`): 새 C — A:C 14:10 (p .54; +15 dB 만 5:6, +18 · +21 dB 만 9:4 p .27), B:C 20:8 (p .036; +18 · +21 dB 만 15:2), b\*:C 45:7 (p 7e-8), V1:C 2175:6 (+18 · +21 dB 만 2170:0). 옛 C — A:C 15:5 (p .041), B:C 23:5, b\*:C 49:5. 새 C 와 A 의 paired 차이는 유의하지 않다 (p .54); PRIMARY 는 규칙 (M 최소) 이 정한 것이다.
  - **판정점 SNR 의 개발 해 없음 확인 (M4)** — 판정점 SNR 가운데 12 점에 없는 점, 같은 개발 시행, n 320, run 별 실패 합 (`select_lowsig_d.out`; 기준 PRIMARY ≤ V1 + 2√V1):

    | run | 점 | V1 | b\* | C | 한계 | 판정 |
    |---|---|---|---|---|---|---|
    | U28 QPSK | +3 · +6 · +9 | 92 | 107 | 92 | 111.18 | ok |
    | D2 QPSK | −3 · 0 · +3 | 56 | 107 | 60 | 70.97 | ok |
    | U28 16-QAM | +12 | 59 | 68 | 60 | 74.36 | ok |
    | D2 16-QAM | +9 · +12 | 69 | 90 | 67 | 85.61 | ok |

    U28 QPSK 에서는 A 92 · B 92 다. 같은 점들의 paired (run 순서 같음): V1:C 8:8 · 9:13 · 1:2 · 8:6, b\*:C 20:5 · 58:11 · 8:0 · 34:11.
- **runner arm 과 개발 래퍼의 비트 동일** (N3): `arms.LowSigmaPrior`, `--lowsig-arms`, `--wide-ckpt` 의 arm 은 UMi28 16-QAM +18 dB, 시행 5120..5159 에서 개발 래퍼와 비트 동일 — 대조 키 blk_err · nmse, arm V1 · b\* · A · B · 옛 C (genie 없음) (worktree `v1-lowsig` b714a0fb, `raw_LSchk`). 새 C 는 **WIDECHK** (7052e5f2; 10-18 20:43–20:46 CDT, `v1ls/run_widechk.sh` → `log_widechk_compare.txt`, WIDECHK OK 0 problems): 개발 청크 넷 (+18 dB; QPSK 6000..6039, 16-QAM 5120..5159) 에서 runner 의 `M-ours-dscore-C-V1-wide` 가 `lowsig/eval_c.py 'd'` (`screenCd_*`) 와 blk_err · nmse 비트 동일, V1 은 `diag_lowsig` 의 screen 과 동일, meta 의 `wide_ckpt_id` · `wide_sigma_tag` = 새 C. 이로써 옛 LSchk 의 "runner = 개발 래퍼" 확인이 새 C 에도 이어진다.
- **16-QAM L1 은 재평가, QPSK 고 SNR 은 새 점** (S2): 16-QAM 의 L1 (+18 · +21 dB) 은 E5 에서 V1 의 붕괴를 처음 관찰한 바로 그 test 시행 (0..2559) 을 다시 평가하는 것이다. QPSK +18 · +21 dB 는 V1 에게도 새 점이다 (아래).
- **test 시행의 사용 이력** (M1):
  - QPSK test 0..2559 는 두 셀에서 −3 … +15 dB 를 V1 · b\* · genie 등으로 평가했다 (raw `raw_U28B16e4`, `raw_B16e4k`). 16-QAM test 0..2559 (+3 … +21 dB) 는 E5 가 V1 · b\* · R2 · genie · V1-pilot 으로 평가했다 (`raw_U28QAM16`, `raw_D2QAM16`). 변형 셋 (A · B · C) 은 어느 test 시행에서도 수신기 BLER 로 평가한 적 없다.
  - QPSK +18 · +21 dB test: **수신기 BLER 로 평가한 arm 은 없다.** 다만 σ 격자 측정 (`code/sigma.py` `measure_point` — M-ours-G 수신기, 질의 ν_q 만 수집, BLER · 라벨은 저장하지 않음) 이 각 (prior, 셀, SNR) 스트림의 시행 0..63 (**test 번호**) 을 돌렸다: 동결 격자 (`sigma_grid_D2` · `_UMi28`) 는 −3 … +15 dB 에서, 옛 넓힌 격자 HS · UMi28HS 는 −3 … +24 dB (+18 · +21 포함) 에서다. 등록 V1 의 학습 σ 범위도 그 동결 격자에서 나왔다 (DECISIONS 2026-10-19 09:03 KST, 4c08302d). 이 때문에 C 는 **학습 σ 범위의 하한을 개발 시행 2560..2623 에서 같은 측정으로 다시 잰 격자** 로 다시 학습한 체크포인트로 바뀌었다 (`SELECTION_RULE.md` 추가 절, 08e47ec2; §1.1). 상한은 등록 V1 과 같은 동결 격자의 상한 (0.8451555 · 0.8372515) 그대로이고, 그 동결 격자는 위의 test 번호 시행 0..63 의 라벨 없는 질의 통계다 (Codex 2 · verifier A).

## 1. 고정되는 것

### 1.1 셀 · 체크포인트 · arm

| 셀 | prior · fits | V1 (등록된 Stage C V1) | C 의 체크포인트 (재학습; σ 하한 = 개발 시행 격자, 상한 = 동결 격자) |
|---|---|---|---|
| U28 | UMi28 C2 8×4, `results/gmm_fits_D2_U28B16e4` 의 바이트 복사본 (b\* kron 4096, ll_val 5.797910431000217; fullK32) | `ckpt/d2sx_UMi28_N160000_a1_best.pt` (sha256 6f3a1b94…3d1c, role best, epoch 379; 399 에서 patience 정지) | `ckpt/d2sx_UMi28_N160000_a1_sgUMi28HSUd_best.pt` (sha256 03cc9005…f245, role best, epoch 493; 513 epoch 학습 뒤 patience 정지; σ 격자 UMi28HSUd [0.011747, 0.83725]) |
| D2 | S2 C2 8×4, `results/gmm_fits_D2_B16e4k` 의 바이트 복사본 (b\* kron 1024, ll_val −11.459169831224418; fullK32) | `ckpt/d2sx_N160000_a1.pt` (sha256 4443921c…2f29, role legacy-last, epoch 1784, best 1764) | `ckpt/d2sx_N160000_a1_sgHSUd.pt` (sha256 bd48a886…a29b, role last — 등록 V1 의 legacy-last 와 같은 역할, epoch 1028 / best 1008; `_best.pt` 는 쓰지 않는다; σ 격자 HSUd [0.011709, 0.84516]) |

WIDE_U28 03cc9005164fe31d21fc87875105d3840063cd6309b0f76e81dad302fc81f245
WIDE_D2 bd48a8860ca2543e17227cb9d7f7b6c56862dedd0dcfb3837f320914bedea29b

(위 두 줄은 `run_v1ls.sh` 가 `grep "^WIDE_<셀> "` 로 읽는 C 체크포인트의 sha256 이다 — 줄 머리가 이 꼴인 줄은 문서 전체에서 셀마다 하나뿐이어야 한다. 옛 C — `_sgUMi28HSU_best.pt` epoch 456 / 476, `_sgHSU.pt` epoch 826 / best 806 — 는 test 실행에 쓰지 않는다.)

- **arm 여섯** (같은 run 의 같은 시행): `M-ours-dscore-C-V1` (V1), `M-ours-bstar` (b\*), `R5-genie`, `M-ours-dscore-C-V1-clamp` (A), `M-ours-dscore-C-V1-gmmfb` (B), `M-ours-dscore-C-V1-wide` (C).
  - A: σ = √(ν/2) < s_lo (V1 체크포인트의 동결 격자 하한) 인 질의는 네트워크를 ν_lo = 2 s_lo² 에서 평가해 prior site (Λ_c, η_c) 를 만들고, 실제 ν 의 matrix site 가 그 site 를 정확히 재현하는 (m′, J′) 를 돌려준다. 그 밖의 질의는 V1 과 같다. A 는 DECISIONS 2026-09-20 12:35 KST ("범위 밖 질의는 clamp 하지 않고 외삽한다") 와 어긋나는 변형이다 (N5); 그 결정은 등록 V1 arm 에 그대로 유지되고, A 는 이 등록의 변형 arm 으로만 평가한다.
  - B: σ < s_lo 인 질의는 b\* 의 GMM (raw GMMPriorB, `gmmB-scorew-eta` 와 같은 객체) denoiser 로. 그 밖은 V1.
  - C (S6, Codex 1): 같은 rung (D2SXUMi28160000 · D2SX160000) · attempt 1 (학습 추첨 시드 SEED_TRAIN + rung·17 + attempt 를 정한다, `score.py:900`; randperm · σ · ε 추첨에만 쓰인다) · 데이터 (1.6e5; split_hash 98cc168731eb922c · a00951cf75b852a6 — 옛 C · 등록 V1 과 같다; 분할 시드는 rung · attempt 와 무관한 SEED_SPLIT = 20260926, `score.py:77` · `training_split` 653–664) · 레시피 (DiT, VP, angle, lr 0.002238, EMA 0.999, batch 256; patience 20, 최소 200 · 최대 3000 epoch; hp 동일, params 479426) 로, 학습 σ 범위의 **하한을 낮춘** 격자에서 다시 학습 (`code/run_d2_sx.py --sigma-tag UMi28HSUd / HSUd`, `lowsig/run_train_cd.sh`; 10-18 18:57–20:28 CDT, GPU 0 · 1; 학습 로그 `logs/train_d2sx_UMi28_N160000_a1_sgUMi28HSUd.log` · `train_d2sx_N160000_a1_sgHSUd.log`). **가중치 초기화는 통제 · 확인하지 않았다** (`score.py:895` 의 `make_model` 은 전역 PyTorch RNG 로 초기화하고, 그 앞에 전역 시드를 정하는 호출이 없다; 저장된 V1 · C 의 초기 가중치가 같았는지는 미검증). 학습 길이 · 정지 epoch 도 다르다 (U28: V1 399 · C 513 에서 patience 정지, 쓰는 best 는 379 · 493; D2: V1 1784 · C 1028, 쓰는 것은 마지막 epoch, best 1764 · 1008). 그래서 V1 ↔ C 의 차이는 학습 σ 범위 · 초기화 · 학습 길이가 함께 바뀐 결과이고, σ 범위 하나의 효과로 적지 않는다 (§2.2). 격자 = 개발 시행 2560..2623 에서 동결 격자와 같은 측정 (`lowsig/measure_grid_dev.py`: `sigma.measure_point` 의 수신기 M-ours-G · 추첨 순서 그대로, 각 점의 앞 2560 시행은 뽑고 버림; C1 · C2, n 64, SNR −3 … +24 dB, 1–99 percentile) 으로 잰 넓은 격자 HSd · UMi28HSd 의 **하한** + 동결 격자의 **상한** (0.8451555 · 0.8372515 — 등록 V1 과 같은 격자, test 번호 시행 0..63 의 라벨 없는 질의 통계; §0), 20 점 로그 등간격 (`lowsig/make_union_grid.py`; `results/sigma_grid_D2_HSUd.txt` · `_UMi28HSUd.txt`: 동결 하한 0.033062 · 0.032681 → 0.011709 · 0.011747). 학습은 σ 를 [하한, 상한] 에서 **로그 균등으로 뽑는다** (학습 로그 "sigma grid : MEASURED, 20 points, log-uniform draw over [...]"); 20 점은 격자 파일에 있는 점이다. 범위 밖 질의는 V1 처럼 외삽. 배선 · psd 투영은 V1 과 같다.
- **대표 (primary)**: §0 의 개발 선택 = **C** (`M-ours-dscore-C-V1-wide`). A · B 는 같은 규칙의 보고 전용 행.

### 1.2 test 점 (네 run)

| run (태그) | 셀 · 변조 | SNR (dB) | 청크 |
|---|---|---|---|
| U28LSQ | UMi28 · QPSK | −3, 0, 3, 6, 9, 12, 15, 18, 21 | 9 × 64 = 576 |
| D2LSQ | D2 · QPSK | 같은 9 점 | 576 |
| U28LS16 | UMi28 · 16-QAM (`--mod 16qam`) | 3, 6, 9, 12, 15, 18, 21 (E5 격자) | 448 |
| D2LS16 | D2 · 16-QAM | 같은 7 점 | 448 |

시행 = 각 (prior, 변조, SNR) 스트림의 test 0..2559 (n 2560, chunk 40), 외부 반복 16, CPU complex128.

### 1.3 실행 (동결 뒤; main 의 실행 커밋에서, tmux)

| 항목 | 고정 값 |
|---|---|
| 체인 (S4) | `cd ~/t2/conf && V1LS_CPUS=24-47,120-143,72-95,168-191 bash code/run_v1ls_chain.sh` → `code/run_v1ls.sh` 를 **U28 qpsk → U28 16qam → D2 qpsk → D2 16qam** 순서로 부른다. 앞 run 의 종료 코드가 0 일 때만 다음 run 을 시작하고, 아니면 `CHAIN_STOPPED after <셀> <변조>` 를 남기고 끝낸다 (사용자에게 보고, §1.5). 로그 `logs/run_v1ls_chain.log`, 끝 `CHAIN_DONE`. |
| run 하나 | `V1LS_CPUS=<목록> bash code/run_v1ls.sh <U28\|D2> <qpsk\|16qam> [--resume]` |
| 시작 조건 (하나라도 어기면 `ABORT (precondition)`, 실행 없음) | V1LS_CPUS 설정; `code/` · `Demo/` 가 깨끗; 이 문서와 s5 가 추적되고 HEAD 와 같음; HEAD = s5 를 마지막으로 건드린 커밋; s5 에 FREEZE · PRIMARY · WGB_<셀>_<변조>; FREEZE 가 HEAD 의 조상; FREEZE..HEAD 에 `code/` · `Demo/` 변경 없음; V1 체크포인트 sha256; C 체크포인트 sha256 = 이 문서의 `WIDE_<셀>` 줄; fits 폴더 `results/gmm_fits_D2_<T>` = 원본의 바이트 복사본 (링크 없음, 개수 · cmp · b\* / fullK32 sha256); 기준 raw 에 `D2_*.npz` ≥ 448; 다른 `runner.py run` 없음; `raw_<T>` 비어 있음 (`--resume` 제외) |
| 주 실행 | `taskset -c $V1LS_CPUS python code/runner.py run --testbed D2 --prior <UMi28\|S2> --cell C2 --ntrain 160000 --stagec-ckpt <V1> [--mod 16qam] --chunk 40 --n 2560 --snr <§1.2> --arm <여섯> --lowsig-arms --wide-ckpt <C> --worker-gb <WGB_<셀>_<변조>, s5> --tag <§1.2>` → `logs/run_D2_<T>.log` |
| 순서 · CPU | 한 번에 하나 (스크립트가 다른 runner 를 거부). CPU 96 (`24-47,120-143,72-95,168-191`), 워커 = min(96, 청크 수, ⌊0.8·MemAvailable / G⌋); G 는 §5 의 스모크 (개발 청크) 에서 |
| 수용 ① | `eval_accept.py --tag <T>:<role>:<sha16>:C2 --prior <…> --ntrain 160000 --kron-K <K> --ll-val <repr> --points C2:<§1.2> --chunk 40 --n 2560` → `results/review_next/v1ls/<T>_accept.txt` |
| 수용 ② | 모든 청크: run\|git = HEAD, `meta|modulation` = 변조 (없으면 qpsk 로 간주), 16-QAM 이면 `meta|payload_bits` 90 · `meta|protocol` E5-qam16-v1 (N7), `meta|lowsig_arms` 있음, `meta|wide_ckpt_id` 에 WIDE 줄 sha256 의 앞 16 자리 · `meta|wide_sigma_tag` = UMi28HSUd / HSUd, 여섯 arm × KEYS_RAW 모양 (40, 16); 청크 수 = 9 × 64 = 576 / 7 × 64 = 448 |
| 수용 ③ (같은 시행) | 기준 raw 에 같은 이름의 청크가 있는 **모든** 청크 — 두 변조 모두 448 청크 (QPSK: −3 … +15 dB 7 점 × 64 ↔ `raw_U28B16e4` · `raw_B16e4k`; 16-QAM: 일곱 점 전부 ↔ `raw_U28QAM16` · `raw_D2QAM16`) — 에서 V1 · b\* · genie 의 모든 KEYS_RAW 배열이 **비트 동일** (NaN 은 같은 것으로). 대조 청크 수가 448 이 아니거나 다른 배열이 하나라도 있으면 실패. QPSK +18 · +21 dB 는 기준이 없어 대조하지 않는다 (새 점). |
| 분석 | ①–③ 이 모두 OK 일 때만 `code/v1ls_compare.py --raw raw_<T> --cell C2 --prior <…> --snrs <§1.2> --primary M-ours-dscore-C-V1-wide --out results/review_next/v1ls/compare_<T>.txt` (§1.4). 스크립트의 자체 검사 (하나라도 어기면 REFUSED, 아무것도 계산하지 않음): `analysis.load_raw` 의 WARNING 없음 (NOTE = raise 된 블록은 실패로 세고 출력), 점 = 등록 격자, 모든 점 n 2560, 여섯 arm. 수용이 실패하면 `compare: NOT RUN` |
| 끝 표시 | `logs/run_v1ls.log`, `V1LS_DONE <셀> <변조> ok=<n> fail=<n>`; fail = runner 비정상 종료 (1) + 실패한 단계 수 (수용 실패로 compare 를 안 돌린 것도 1); 종료 코드 = fail |

### 1.4 분석 (`code/v1ls_compare.py`; 수치만, 해석 없음)

- **L1 (V1 대비, +18 · +21 dB)**: run 마다 X = C 에 대해 +18 · +21 dB 의 점별 exact 양측 paired 부호검정 V1 → X (a = V1 만 실패 : b = X 만 실패; 반복 16). 판정은 코드 순서대로 (N1) — 두 점 모두 X 가 적게 실패하고 p < .05 → **(a)**; 그렇지 않고 어느 점에서든 V1 이 적게 실패하고 p < .05 → **(c)**; 그 밖 → **(b)**.
  - **MONOTONE** (M2; 서술 조건, 검정 없음, 라벨을 바꾸지 않는다): X 의 실패 수 (반복 16, / 2560) 가 +18 dB ≤ +15 dB 이고 +21 dB ≤ +18 dB 이면 yes, 아니면 no. 세 실패 수와 yes / no 를 출력한다. §2.1 의 괄호 문구에만 쓴다.
- **L2 (b\* 대비)**: run 마다 `b* → X` 를 `analysis.table_B` 와 같은 함수 · 규칙으로 — 판정점 = 앵커 b\* 의 BLER@16 이 0.1 에 |log10| 로 가장 가까운 3 점 (BLER ∈ [0.005, 0.9]), 판정점별 exact 양측 부호검정 p < .05, power guard (판정점 3 개, 불일치 쌍 ≥ 6 인 점 ≥ 2), "second arm fewer failures" 2/3 이상 → **(i)**, "first arm fewer failures" 2/3 이상 → **(ii)**, POWERED 이고 둘 다 아님 → **(iii)**, POWERED 아님 → **(iv)**; SNR@0.1 격차 (b\* − X) 90 % paired bootstrap (exp_0925_analysis.gain). 판정점의 pooled a:b 도 적지만 판정에 쓰지 않는다.
  - **ΣF · R** (M3): 판정점에서 b\*, X, genie 의 실패 합 ΣF (raise 된 블록 = 실패) 와 R = (F_b\* − F_X) / (F_b\* − F_genie) (F_b\* ≤ F_genie 면 정의하지 않음), 90 % paired bootstrap (`recovery_ci.boot`, B 2000, seed 20260926; 판정점에 걸쳐 같은 시행 index 를 재표집, 정의되지 않은 replicate 수를 함께 적음). 출력만 한다.
  - **SUFFIX** (M3; 코드 99f62bfb 그대로): (i) 이면 판정점 가운데 b\* 가 유의하게 (p < .05) 적게 실패한 점마다 "(단 <SNR> dB 에서는 M-ours-bstar 가 적게 실패: a:b, p = …)"; (ii) 이면 X 가 유의하게 적게 실패한 판정점마다 같은 꼴 (arm 이름은 runner 이름). 라벨이 (ii) 가 **아닐** 때만, +18 · +21 dB 에서 b\* 가 X 보다 유의하게 적게 실패하면 같은 꼴을 더한다 ((ii) 에서는 라벨과 같은 방향이라 붙이지 않는다). 같은 SNR 은 한 번만 — (i) 의 판정점으로 이미 들어간 점은 +18 · +21 dB 규칙으로 다시 넣지 않는다. 해당이 없으면 none. 라벨은 바꾸지 않는다.
- **보고 전용**: A · B 의 L1 (MONOTONE 포함) · L2 (ΣF · R · SUFFIX 포함) — 같은 규칙, 라벨 문장 없음; V1 → X 의 다른 격자점 점별 부호검정과 +15 dB 이하 합 (pooled); b\* → X 의 +18 · +21 dB 점별 부호검정; 여섯 arm × SNR 실패 수 / 2560.
- **다중성** (S3): 판정은 run 4 × 라벨 2 (L1, L2) = 8 개이고 보정하지 않는다. run 마다 문장은 단독이다 (네 run 을 합친 문장은 쓰지 않는다, §2.2). §3 의 "4/4" 는 채점용 예측이지 판정이 아니다.
- 판정은 run (셀 × 변조) 마다 따로; 네 run 을 합치지 않는다.

### 1.5 예외 · 중단

- runner 비정상 종료 · 메모리 초과: 같은 HEAD 에서 `run_v1ls.sh <셀> <변조> --resume`. 수용 ①–③ 실패 → 분석 표를 결과로 쓰지 않고 사용자에게 보고 (원인 확인 뒤 결정).
- 체인이 멈추면 (`CHAIN_STOPPED`) 남은 run 은 원인 확인 · 사용자 결정 뒤 `run_v1ls.sh` 로 run 마다 §1.3 의 순서대로 돌린다 (체인 스크립트는 처음부터 시작하므로 끝난 run 의 `raw_<T>` 가 있으면 거부한다).
- 판정하지 못함 ((b) · (iii) · (iv)) 도 완료된 결과. 점 · 표본을 늘리지 않는다. test 를 본 뒤 primary 나 변형을 바꾸지 않는다.
- 실행 중 main 에 커밋하지 않는다; 실행 중인 등록 문서 · conf/code · Demo · DECISIONS 를 고치지 않는다 (DECISIONS 줄은 모았다가 끝난 뒤).

### 1.6 하지 않는 것

다른 셀 · 배열 · 체크포인트 (C9 32×4, 다른 데이터셋), 다른 SNR, test 를 본 뒤의 재선택, 변형의 하이퍼파라미터 탐색, C 의 다른 attempt · 시드, V1 과 같은 초기화로 맞춘 C 의 비교 (Codex 1; 이 등록 밖).

## 2. 라벨 · 문장

### 2.1 run 마다 (네 run 각각)
- L1 (a): "<셀> <변조> 에서 V1-wide 가 +18 · +21 dB 에서 V1 보다 적게 실패"; 뒤에 MONOTONE = yes 이면 "(V1 의 고 SNR 붕괴가 이 격자에서는 나타나지 않음)", no 이면 "(V1-wide 반복 16 실패 +15 / +18 / +21 dB = a / b / c, n 2560)" 을 붙인다 — a / b / c 는 compare 출력의 MONOTONE 줄에서 옮긴다 (M2). (b): "판정하지 못함"; (c): "V1 이 +<SNR> dB 에서 V1-wide 보다 적게 실패" — 두 점이 모두 해당하면 "+18 · +21 dB" 로 둘 다 쓴다 (해석 문구 없음). (c) 에 적는 SNR 은 V1 이 적게 실패하고 p < .05 인 점이다; L1 줄의 p 는 `.2g` 표기라 출력이 p=0.05 로 보이면 그 a:b 로 `analysis.sign_p` 를 다시 계산해 정한다 (라벨은 코드가 정한다).
- L2: (i) "V1-wide 가 b\* 보다 적게 실패", (ii) "b\* 가 V1-wide 보다 적게 실패", (iii) "판정하지 못함 (유의 방향 없음)", (iv) "판정하지 못함 (검정력 미달)". GMM b\* 의 "[K 상한 민감: 외삽 불가]" 한정어는 U28 에만 (E5 · 원 등록과 같음). §1.4 의 SUFFIX 가 none 이 아니면 그 문자열을 그대로 붙인다; 라벨은 바꾸지 않는다 (M3).
- 문장에 붙는 것의 순서 (고정): L1 — 라벨 문장 → ((a) 에서만) MONOTONE 괄호 → V1-wide 설명. L2 — 라벨 문장 → (U28 에서만) "[K 상한 민감: 외삽 불가]" → SUFFIX (compare 출력의 "(단 …)" 들을 "; " 로 이은 그대로) → V1-wide 설명.
- V1 의 QPSK +18 · +21 dB 붕괴 (예측 4) 는 여섯 arm × SNR 실패 수 표 (보고 전용) 로만 보고한다; 원 QPSK 등록 (`U28B16e4` · `B16e4k`, 격자 −3 … +15 dB) 의 라벨 · 문장은 바꾸지 않는다 (S2).
- V1-wide 설명 (모든 문장 끝에): "V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)".

### 2.2 쓰지 않는 문구
"동등", "비열등", "완전히 해결", "모든 SNR 에서", "원인을 증명", "σ 범위만의 효과" (V1 ↔ C 의 차이를 학습 σ 범위 하나로 돌리는 모든 표현 — 초기화 · 정지 epoch 도 다르다, §1.1). 네 run 을 합친 문장 (판정은 run 별).

## 3. 미리 적는 예측 (test 미열람; §6 에서 적중 / 빗나감; 모두 채점용이며 판정이 아니다)
1. L1 = (a) in 4/4 runs.
2. L2 = (i) in 4/4 runs (판정점은 b\* 기준이므로 E5 · 원 QPSK 등록의 판정점과 같을 것이다 — 예측 3).
3. 판정점이 기록과 같다: U28 QPSK +3 · +6 · +9 (원 기록 `U28B16e4`), D2 QPSK −3 · 0 · +3 (`B16e4k`), U28 16-QAM +12 · +15 · +18, D2 16-QAM +9 · +12 · +15 (E5). N4: 수용 ③ 이 통과하면 b\* 의 실패 수가 기록과 같으므로 사실상 기계적이다 — 16-QAM 은 격자도 E5 와 같고, QPSK 는 +18 · +21 dB 가 더해졌을 뿐이다. 채점은 하되 적중을 증거로 세지 않는다.
4. QPSK 두 run 의 +18 · +21 dB 에서 V1 의 실패 수 > b\* 의 실패 수 (네 점 모두; 개발 진단의 붕괴가 QPSK test 에서도 나타난다 — 여섯 arm 실패 수 표로 채점).
5. (N6) +15 dB 이하 격자점을 합친 C 의 실패 수 ≤ V1 의 실패 수 + 2√(V1 의 실패 수), 네 run 모두 (여섯 arm 실패 수 표로 채점; 개발 근거: `select_lowsig_d.out` 의 +15 dB 해 없음 조건과 M4 표). 판정 아님.
6. MONOTONE = yes in 4/4 runs (개발 근거: 새 C 의 +15 / +18 / +21 dB 실패 수 / 320 — U28 QPSK 3 / 0 / 0, U28 16-QAM 33 / 21 / 9, D2 QPSK 0 / 0 / 0, D2 16-QAM 20 / 15 / 9; `select_lowsig_d.out`). 채점은 `compare_<T>.txt` 의 `PRIMARY LABELS … (monotone yes/no) …` 줄로.
7. SUFFIX = none in 4/4 runs. 채점은 같은 줄의 `(suffixes n)` 으로 (n = 0 이 적중). 개발 근거 (b\*:C, a = b\* 만 실패 : b = C 만 실패, 같은 개발 시행 n 320, 반복 16): 판정점 SNR (M4, §0) 에서 20:5 · 58:11 · 8:0 · 34:11; 12 점 screen 에서

   | run | +15 | +18 | +21 |
   |---|---|---|---|
   | U28 QPSK | 0:0 | 0:0 | 1:0 |
   | U28 16-QAM | 8:1 (p .039) | 5:3 (p .73) | 2:0 (p .5) |
   | D2 QPSK | 0:0 | 0:0 | 0:0 |
   | D2 16-QAM | 14:2 (p .0042) | 8:1 (p .039) | 7:0 (p .016) |

   접미는 b\* 가 유의하게 **적게** 실패할 때 ((i) 의 판정점, 또는 (ii) 가 아닐 때의 +18 · +21 dB) 붙는데, 개발에서 유의한 점 (U28 16-QAM +15 — 예상 판정점; D2 16-QAM +15 — 예상 판정점, +18, +21) 은 모두 C 가 적게 실패하는 쪽이라 접미를 만들지 않는다. (ii) 에서 X 가 적게 실패하는 판정점의 접미는 (ii) 자체가 예측 2 와 어긋나므로 따로 예측하지 않는다.

## 4. 선행 작업 · 검토

- 코드 (Claude, worktree `v1-lowsig`): `arms.LowSigmaPrior` · runner `--lowsig-arms` / `--wide-ckpt` (b714a0fb), `code/run_d2_sx.py --sigma-tag` (main 64e7bd07), `code/run_v1ls.sh`, `code/v1ls_compare.py` (0879b238); 검토 반영 2ca34ef1 — MONOTONE · SUFFIX · ΣF · R (`v1ls_compare.py`), `code/run_v1ls_chain.sh`, 수용 ② 의 16-QAM payload · protocol 검사; 99f62bfb — SUFFIX 중복 제거 (verifier B; 합성 raw 두 사례로 확인). 회귀: 개발 래퍼와 비트 동일 (LSchk, WIDECHK; §0); 기본 경로 (플래그 없음) 불변 — §5 의 플래그 없음 확인, 수용 ③ 이 test 에서 다시 확인.
- 검토 상태 (v2.2 작성 시점):
  - verifier (코드, v1): 결함 0, 선택적 개선 3 반영 (Claude 보고).
  - Fable 적대적 검토 1 회 (`prereg_reviews_2026-10-18/review_V1LS.md`, MUST 4 · SHOULD 6 · NIT 7) → 반영 = v2 (1586a508).
  - verifier (v2 검토): 결함 2 (A 격자 상한 출처, B SUFFIX 중복) → 반영 (문서 v2.1, 코드 99f62bfb); 선택 개선 2 (§2.1 문장 꼴, §3 예측 6 · 7) 반영; 추가 확인 1 (병합 확인, §5).
  - Codex 교차 검토 (코드 + 문서, v2): 결함 2 (초기화 미통제, 격자 상한 출처) → 반영 = 이 v2.1 (`~/t2/reviews/20261019-110034-prompt_pretest_v1ls.md`, 끝에 Claude 의 처리).
  - verifier (v2.1 재검토): 결함 2 (데이터 분할의 출처, 정지 epoch · 인용 줄 번호 — 문구만) → 반영 = 이 v2.2; 선택 개선 2 (§2.1 (c) 의 p 판별, §5 DECISIONS 줄의 커밋 시점) 반영.
  - 남은 것: v2.2 의 고친 범위 확인 → `v1-lowsig` 를 main 에 병합 = FREEZE → **병합 확인** (§5) → s5 + 실행 시작 DECISIONS 줄 커밋 = 실행 커밋 → 사용자 승인 → 체인 실행.

## 5. 평가 전 고정 기록

- **스모크** (`v1ls/rss_smoke_v1ls.py`, `run_smoke.sh`; 10-18 18:28–18:36 CDT, 커밋 0879b238; `logs/v1ls_smoke.log`, `log_smoke_*.txt`): run 마다 개발 청크 하나 (+18 dB; QPSK 6320..6359, 16-QAM 5520..5559 — 전에 쓴 적 없음) 를 여섯 arm · jobs 1 로. max RSS 1.236 · 1.237 · 0.981 · 0.980 GB (U28 QPSK · U28 16-QAM · D2 QPSK · D2 16-QAM) → **G = 1.5** (⌈1.05·RSS / 0.5⌉·0.5) 네 run 모두. 스모크는 옛 C 로 돌았다; 새 C 는 네트워크 구조 · 크기가 같다 (hp 동일, params 479426).
- **청크 시간** (스모크, 40 시행 × 여섯 arm, jobs 1): 458 · 443 · 186 · 192 s (같은 순서). **추정 시간**: 워커 = min(96, 청크 수, ⌊0.8·MemAvailable / G⌋); 96 워커면 물결 ⌈576/96⌉ = 6 · ⌈448/96⌉ = 5 → 6 × 458 + 5 × 443 + 6 × 186 + 5 × 192 ≈ 7040 s ≈ 2.0 h (네 run 합). 96 개 하이퍼스레드가 함께 돌면 청크가 느려질 수 있어 **2–4 h** 로 잡는다.
- **플래그 없음 확인** (S5; `v1ls/run_noflag.sh`, 10-18 18:51–18:56 CDT, 커밋 0879b238; `log_noflag_*.txt`, `logs/v1ls_smoke.log`): 셀 · 변조마다 같은 +18 dB 개발 청크를 `--lowsig-arms` · `--wide-ckpt` 없이 V1 · b\* · genie 만으로 다시 돌려 플래그를 켠 스모크 raw 와 대조 — 네 run 모두 26 배열 전부 비트 동일 (differing []).
- **WIDECHK** (새 C; §0): 10-18 20:43–20:46 CDT, 7052e5f2, WIDECHK OK (0 problems).
- **병합 확인** (verifier 추가 확인; FREEZE 뒤, s5 커밋 전): FREEZE 의 main 에서 셀 · 변조마다 +18 dB 개발 청크 하나 (QPSK 6000..6039, 16-QAM 5120..5159) 를 여섯 arm · `--lowsig-arms` · `--wide-ckpt` 로 돌린다. V1 · b\* · A · B 는 `lowsig/screen_*` 의, C 는 `screenCd_*` 의 0..39 행과 blk_err · nmse 를 비트 대조하고, meta `lowsig_s_lo` 가 V1 격자의 하한인지 본다. 이유: 2ca34ef1 에서 더한 `LowSigmaPrior` 의 s_lo assert (`arms.py:175`) 와 meta `lowsig_s_lo` (`runner.py:485–486`) 는 기록된 runner 실행에서 한 번도 돌지 않았다 (스모크 · 플래그 없음 확인은 0879b238, WIDECHK 는 `--lowsig-arms` 없이). 결과는 이 문서가 아니라 **실행 커밋 메시지와 DECISIONS 줄** (아래, 실행 커밋에 포함) 에 적는다. 하나라도 다르면 s5 를 만들지 않고 사용자에게 보고한다.
- **코드 커밋**: 실행 커밋의 `code/` · `Demo/` = FREEZE 의 것 (`run_v1ls.sh` 가 `git diff FREEZE HEAD -- code ../Demo` 가 비어 있음을 확인). 병합 확인은 코드를 바꾸지 않는다.
- **s5 형식** (`results/review_next/v1ls/v1ls_s5.txt`, 여섯 줄): `FREEZE <병합 커밋 해시>`, `PRIMARY M-ours-dscore-C-V1-wide`, `WGB_U28_qpsk 1.5`, `WGB_U28_16qam 1.5`, `WGB_D2_qpsk 1.5`, `WGB_D2_16qam 1.5`. FREEZE 해시는 병합 뒤에 s5 파일에만 적는다 (이 문서에는 적지 않는다). s5 를 더한 커밋이 실행 커밋이고, 그 커밋은 `code/` · `Demo/` 를 건드리지 않는다. **실행 시작 DECISIONS 줄 (병합 확인 결과 포함) 은 s5 와 같은 커밋 (실행 커밋) 에 넣는다** — `run_v1ls.sh` 는 HEAD 가 s5 를 마지막으로 건드린 커밋이기를 요구하므로, s5 다음에 따로 커밋하면 ABORT 가 난다 (선택 개선 4).

## 6. 결과 (이 절은 추가만 한다)

기록 2026-10-19 03:16 CDT (Opus 5.5). 출처: `results/review_next/v1ls/compare_<T>.txt` (`code/v1ls_compare.py` 출력, 수치는 옮긴 것), `logs/run_v1ls.log` · `logs/run_v1ls_chain.log`, `logs/run_D2_<T>.log`.

### 6.1 실행 · 수용
- 실행 커밋 1d706648 (s5: FREEZE 2a9b4d14 = `v1-lowsig` 병합, PRIMARY `M-ours-dscore-C-V1-wide`, WGB 1.5 ×4). 사용자 승인 "승인할게" (DECISIONS 실행 시작 줄). 병합 확인 MERGECHK OK (10-18 21:56–22:04 CDT; §5).
- 체인 `code/run_v1ls_chain.sh` (tmux `v1ls`), CPU 96 (`24-47,120-143,72-95,168-191`), 워커 96, 재개 없음. U28LSQ 10-18 22:13–23:50 CDT (runner 96.2 min) → U28LS16 23:50–01:07 (77.2 min) → D2LSQ 01:07–02:18 (70.5 min) → D2LS16 02:18–03:13 (55.1 min) → `CHAIN_DONE` 10-19 03:13 CDT. 네 run 모두 `V1LS_DONE … ok=4 fail=0`.
- 수용 ① `eval_accept` ACCEPT OK ×4 (`v1ls/<T>_accept.txt`); ② run|git = 1d706648 · meta · 모양 · 청크 수 (576 / 448) OK ×4; ③ V1 · b\* · genie 의 모든 KEYS_RAW 배열이 기록 raw 와 448 청크 비트 동일 ×4 (`logs/run_v1ls.log` 의 `accept_ref: OK`; 대조 수는 체인 화면이 세션 종료로 남지 않아 저장된 raw 로 다시 계산 — `v1ls/accept_ref_recheck.txt`: 네 run 모두 448 청크, 다른 배열 0). raise 된 블록 0 (load_raw NOTE 0).
- 실행 중 사건 (결과 무관): 같은 시각 E4 Codex 작성 프로세스의 명령줄 (명세 본문) 이 run 가드의 pgrep 패턴을 담고 있어, 다음 run 시작 때 ABORT 할 수 있었다 → 10-18 22:48 CDT 에 그 Codex 를 멈췄다 (verifier 가 발견; 이후 가드에 걸리는 runner 밖 프로세스 0 을 매 점검에서 확인). DECISIONS 에 기록.

### 6.2 판정 (PRIMARY = C = `M-ours-dscore-C-V1-wide`; §1.4 규칙 그대로, `compare_<T>.txt`)

| run | L1 V1 → C (+18 · +21 dB, a:b) | L1 | MONOTONE (C 실패 +15 / +18 / +21) | L2 판정점 (b\* 앵커) | b\* → C a:b (점별) · pooled | L2 | SNR@0.1 격차 (b\* − C) [90 %] | ΣF b\* / C / genie | R [90 %] | SUFFIX |
|---|---|---|---|---|---|---|---|---|---|---|
| U28LSQ (UMi28 QPSK) | 929:0 · 2555:0 | **(a)** | yes (24 / 5 / 1) | +3 · +6 · +9 | 81:37 · 53:27 · 35:10; 169:74 | **(i)** | +0.58 dB [+0.30, +0.86] | 800 / 705 / 215 | 0.162 [0.121, 0.202] | none |
| U28LS16 (UMi28 16-QAM) | 1693:3 · 2463:0 | **(a)** | yes (273 / 154 / 80) | +12 · +15 · +18 | 69:18 · 52:19 · 44:16; 165:53 | **(i)** | +0.69 dB [+0.43, +1.02] | 1004 / 892 / 438 | 0.198 [0.159, 0.236] | none |
| D2LSQ (D2 QPSK) | 2256:0 · 2557:0 | **(a)** | yes (3 / 2 / 2) | −3 · 0 · +3 | 299:47 · 112:18 · 31:6; 442:71 | **(i)** | +1.40 dB [+1.21, +1.63] | 864 / 493 / 125 | 0.502 [0.464, 0.538] | none |
| D2LS16 (D2 16-QAM) | 2396:1 · 2491:0 | **(a)** | yes (132 / 90 / 66) | +9 · +12 · +15 | 160:26 · 116:22 · 93:11; 369:59 | **(i)** | +3.33 dB [+2.51, +4.28] | 922 / 612 / 465 | 0.678 [0.631, 0.729] | none |

모든 판정점에서 POWERED, "second arm fewer failures" 3/3; 판정점의 점별 p 는 모두 < .005 (가장 큰 값 U28LSQ +6 dB 53:27, p = .0049; `compare_<T>.txt`). L1 의 점별 p 는 모두 ≈ 0.

### 6.3 등록 문장 (§2.1 의 틀 · 순서 그대로; run 마다 단독, 네 run 을 합친 문장은 쓰지 않는다)
- **UMi28 QPSK** — L1 (a): "UMi28 QPSK 에서 V1-wide 가 +18 · +21 dB 에서 V1 보다 적게 실패 (V1 의 고 SNR 붕괴가 이 격자에서는 나타나지 않음). V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)" · L2 (i): "V1-wide 가 b\* 보다 적게 실패 [K 상한 민감: 외삽 불가]. V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)"
- **UMi28 16-QAM** — L1 (a): "UMi28 16-QAM 에서 V1-wide 가 +18 · +21 dB 에서 V1 보다 적게 실패 (V1 의 고 SNR 붕괴가 이 격자에서는 나타나지 않음). V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)" · L2 (i): "V1-wide 가 b\* 보다 적게 실패 [K 상한 민감: 외삽 불가]. V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)"
- **D2 QPSK** — L1 (a): "D2 QPSK 에서 V1-wide 가 +18 · +21 dB 에서 V1 보다 적게 실패 (V1 의 고 SNR 붕괴가 이 격자에서는 나타나지 않음). V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)" · L2 (i): "V1-wide 가 b\* 보다 적게 실패. V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)"
- **D2 16-QAM** — L1 (a): "D2 16-QAM 에서 V1-wide 가 +18 · +21 dB 에서 V1 보다 적게 실패 (V1 의 고 SNR 붕괴가 이 격자에서는 나타나지 않음). V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)" · L2 (i): "V1-wide 가 b\* 보다 적게 실패. V1-wide = V1 과 같은 rung · attempt (학습 추첨 시드) · 데이터 (같은 분할) · 레시피로 학습 σ 범위의 하한을 낮춰 다시 학습한 체크포인트 (가중치 초기화는 통제 · 확인하지 않음; 학습 길이 · 정지 epoch 다름); 학습 σ 범위의 하한은 개발 시행 2560..2623 에서 측정, 상한은 등록 V1 과 같은 동결 격자 (test 번호 시행 0..63 의 라벨 없는 질의 통계) (개발 선택: A · B · C 가운데 C)"
- SUFFIX 는 네 run 모두 none 이라 붙는 접미가 없다. §2.2 의 쓰지 않는 문구 ("동등", "비열등", "완전히 해결", "모든 SNR 에서", "원인을 증명", "σ 범위만의 효과") 는 쓰지 않는다.

### 6.4 보고 전용 (라벨 문장 없음)
- **A (V1-clamp) · B (V1-gmmfb)**: 네 run 모두 L1 (a) · L2 (i). L2 격차 (b\* − X): A · B 같은 값 — U28LSQ +0.60 [+0.33, +0.85], U28LS16 +0.60 [+0.36, +0.93], D2LSQ +1.41 [+1.22, +1.64], D2LS16 +3.44 [+2.62, +4.33] dB (점별 실패 수는 `compare_<T>.txt` 의 여섯 arm 표). MONOTONE: A yes · yes · no (3 / 0 / 2) · yes; B no (24 / 4 / 5) · yes · no (3 / 0 / 7) · no (135 / 91 / 125) (U28LSQ · U28LS16 · D2LSQ · D2LS16 순).
- **V1 → C, +15 dB 이하의 다른 격자점** (pooled, a = V1 만 실패 : b = C 만 실패): U28LSQ 123:128 (p .80), U28LS16 95:74 (p .12), D2LSQ 82:87 (p .76), D2LS16 173:185 (p .56); 점별로 유의한 점 없음.
- **b\* → C, +18 · +21 dB**: U28LSQ 4:2 · 6:1, U28LS16 44:16 · 35:8, D2LSQ 3:1 · 4:0, D2LS16 68:11 · 64:7 (a = b\* 만 실패).
- **V1 의 QPSK +18 · +21 dB 붕괴** (§2.1 S2 — 여섯 arm 표로만 보고; 원 QPSK 등록 `U28B16e4` · `B16e4k` 의 라벨 · 문장은 바꾸지 않는다): V1 실패 / 2560 — UMi28 934 · 2556, D2 2258 · 2559; 같은 시행의 b\* 7 · 6, 4 · 6.
- 여섯 arm × SNR 실패 수 표 전체는 `compare_<T>.txt` 끝.

### 6.5 예측 채점 (§3)
1. L1 = (a) in 4/4 — **적중** (4/4).
2. L2 = (i) in 4/4 — **적중** (4/4).
3. 판정점이 기록과 같다 — **적중** (U28 QPSK +3 · +6 · +9, D2 QPSK −3 · 0 · +3, U28 16-QAM +12 · +15 · +18, D2 16-QAM +9 · +12 · +15). N4: 수용 ③ 이 통과했으므로 사실상 기계적 — 적중을 증거로 세지 않는다.
4. QPSK +18 · +21 dB 에서 V1 실패 > b\* 실패 (네 점) — **적중** (934 > 7, 2556 > 6, 2258 > 4, 2559 > 6).
5. +15 dB 이하 합에서 C ≤ V1 + 2√V1 (네 run) — **적중**: U28LSQ C 2669 vs V1 2664 (한계 2767.2), U28LS16 4006 vs 4027 (4153.9), D2LSQ 524 vs 519 (564.6), D2LS16 1917 vs 1905 (1992.3) (raw 에서 다시 계산, 반복 16, raise = 실패).
6. MONOTONE = yes in 4/4 (PRIMARY LABELS 줄) — **적중**.
7. SUFFIX = none in 4/4 (`(suffixes 0)`) — **적중**.
→ 7/7 (3 은 기계적).

### 6.6 남은 일
verifier (§6 전사), Codex 교차 검토 (제안), 기록 감사 (Fable, 1 회), 원고 · `docs/RESULTS.md` 반영은 사용자 요청 때.

### 6.7 보충 (2026-10-19 03:29 CDT, verifier §6 검토의 선택 개선 — 보고 전용, 판정 무관)
- §6 검토 (verifier): 결함 0 — 동결 코드 (1d706648) 로 다시 돌린 compare 출력이 커밋본과 바이트 동일 ×4, 독립 구현 (npz 직접 · scipy binomtest) 으로 §6.2–§6.5 수치 · 라벨 · 문장 일치, 수용 ① 재실행 ACCEPT OK ×4, 수용 ③ 독립 재확인 (해당 arm 의 모든 키) 448 청크 차이 0 ×4.
- A · B 의 판정점 ΣF (b\* / X / genie) · R [90 %] · SUFFIX (`compare_<T>.txt`): U28LSQ A · B 800 / 712 / 215, R 0.150 [0.110, 0.189]; U28LS16 A · B 1004 / 898 / 438, R 0.187 [0.148, 0.226]; D2LSQ A · B 864 / 488 / 125, R 0.509 [0.470, 0.545]; D2LS16 A 922 / 607 / 465, R 0.689 [0.642, 0.736], B 922 / 605 / 465, R 0.694 [0.648, 0.740]. SUFFIX 모두 none.
- §6.1 의 실행 중 사건 근거: `logs/v1ls_guard_incident.txt` (Codex 래퍼 출력 · 중단 기록, 체인 점검 시각별 가드 확인).

### 6.8 기록 감사 (Fable 서브에이전트, 2026-10-19 08:48–09:08 CDT 보고; `prereg_audit_2026-10-19/audit_V1LS.md`, 재계산 `recompute_v1ls.py` → `recompute_v1ls.out`, 도구 재실행 `rerun_compare_V1LS_<T>.txt` ×4 · `rerun_compare_V1LS_diff.txt` · `rerun_accept_V1LS.txt`; 기록 2026-10-19 09:09 CDT, Opus 5.5)

감사 대상 = HEAD 9a2c9fd4 (실행 커밋 1d706648, FREEZE 2a9b4d14). **MUST 0 · SHOULD 0 · NIT 0.** 자동 350 / 350 일치 (raw npz 직접, conf/code 미임포트): 청크 계획 · raise 0, 수용 ② meta 76 항목, 수용 ③ — 448 청크 ×4 에서 V1 · b\* · genie 의 9 키 (KEYS_RAW + guardH + clip) 11648 배열 ×4 비트 동일, 실패 수 32 행, L1 a:b · p · 라벨 · MONOTONE, L2 판정점 · a:b · p · pooled · power guard · 라벨, SNR@0.1 격차와 90 % bootstrap (자체 구현, 12 쌍), ΣF · R · bootstrap (12 쌍), SUFFIX none ×12, 보고 전용 표, 예측 4 · 5, scipy p 교차 60 값, 개발 선택 규칙 재적용 (`select_lowsig*.out` 전 줄, M4 4 행, §0 · 예측 6 · 7 의 개발 표). `v1ls_compare.py` ×4 재실행이 커밋본과 바이트 동일, `eval_accept.py` ×4 ACCEPT OK. 수동 약 300 값 불일치 0. §6.3 여덟 문장은 §2.1 틀과 문자열 동일, 금지 문구 · 합친 문장 없음. 규칙 재적용: PRIMARY = C, L1 (a) ×4 · MONOTONE yes ×4, L2 (i) ×4, SUFFIX none ×4, 예측 7/7 (관대한 채점 없음). 동결 §0–§5 불변 (추가는 §6 만), FREEZE → 실행 커밋 code · Demo 변경 없음, 실행 창 안 main first-parent 커밋 없음. test / 개발 분리: 선별 · M4 · σ 재측정 (2560..2623) · C 학습 (train/val) 모두 개발; test 번호 시행 0..63 사용은 σ 격자 측정뿐 (`sigma.py` 전 14 버전에 skip 없음 — DECISIONS 의 공개 · 정정과 일치); 옛 C 는 test 에 쓰이지 않음. 실행 중 사건 (E4 Codex 중단 22:48 CDT) 은 파일 mtime 과 맞고, 가드가 run 시작 조건이라 뒤 세 run 이 ABORT 없이 끝난 것이 결과 무관의 근거.
사실 메모 (지적 아님): WIDECHK 의 실행 HEAD 0d179feb · 결과 커밋 7052e5f2 (둘 다 참); 체인 실제 5 h 00 min (§5 추정 2–4 h); 사건 파일이 옮긴 Codex 래퍼의 output 경로 파일은 없음 (중단된 turn); 수용 ③ 대조 수는 recheck 파일로 셈 (§6.1 에 공개). 감사가 확인하지 못한 것: tmux 세션 이름 · 화면의 원래 accept_ref 출력 · 사건 메모의 pid; §6.7 verifier 의 재실행 주장 (같은 항목을 따로 확인함); 실행 중 run 사이의 main code · Demo 청결 (시작 검사 4 회 외 기록 없음) 과 동시 CPU 작업; "b\* BLER 만 열람" · "test 를 보기 전 고정" 같은 진술; 격자 밖 질의 0 (eval_c 집계를 읽음); 작은 선별 (5440..) 수치.
