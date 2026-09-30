# NEXT_EXPERIMENTS_HISNR16e4 — 고SNR 보강 (D2 C2·C6, +6..+15 dB, 새 시행 n = 20480; **보고 전용**, 등록 v2)

- 작성: 2026-09-29 22:50 CDT (= 09-30 12:50 KST) 초안 v1 (Opus 5.5) → 적대적 검토 1건(Fable 5.1 서브에이전트; 반드시 6·권고 8; `prereg_reviews_2026-09-29/review_HISNR16e4.md`) 반영 v2 (2026-09-29 23:06 CDT, Opus 5.5) → 동결 커밋. 커밋 뒤 §1 을 바꾸지 않는다.
- **작성 시점 공개**: 사용자 질문 2026-09-29 CDT ("BLER 체크 블록 수가 2500 정도인데 적지 않나") → 작업 큐 3b. 작성자는 두 셀의 기존 테스트 raw (`raw_B16e4k`, `raw_NR16B16e4`; n = 2560) 의 고SNR 실패 수와 genie 바닥 진단 (`genie_floor/`; D2 C2 +9..+15 dB genie 실패 6 건 전부 L = 3) 을 봤다. 이 실행의 시행 (10000..30479) 은 **한 번도 쓰이지 않았다** (검토: 기존 raw 의 최대 skip 5720). 셀 선택 이유: C2 = 헤드라인, C6 = 회수율이 가장 높은 여차원 셀 (그림 F16·F17 의 고SNR 구간). 비용 확인 뒤 사용자 결정 ({lt}): 두 셀 모두 n = 20480 (≈ 8.2 h CPU 전부).
- 목적: 등록된 판정은 그대로 두고, BLER ≤ 1e-2 구간의 추정 정밀도를 높인다. 원 태그 BLER 로 본 **기대 실패 수** (n = 20480, +6/+9/+12/+15 dB): V1 C2 128/56/40/24, C6 48/16/16/16; b\* C2 224/136/128/64, C6 176/112/80/40; genie C2 72/16/16/16, C6 48/8/16/0 — Wilson 폭이 원 태그의 약 1/2.8. **새 판정 라벨을 만들지 않는다** — 모든 산출은 보고 전용이며 원고에서 기존 판정을 대신하지 않는다.

## 1. 고정되는 것
| 항목 | 값 |
|---|---|
| 셀·가중치·적합 | **D2 C2** (헤드라인 가중치 `ckpt/d2sx_N160000_a1.pt` 4443921ce8d5c4a1 legacy-last, b\* kron 1024, ll_val −11.459169831224418, 적합 `gmm_fits_D2_B16e4k`) · **D2 C6** (`ckpt/d2sx_NR16_N160000_a1_fb2_best.pt` c050d611b2c714a6 best, b\* kron 4096, ll_val 63.1751571838059, 적합 `gmm_fits_D2_NR16B16e4`) — 원 태그 B16e4k·NR16B16e4 와 같다 |
| SNR · 시행 | +6, +9, +12, +15 dB; **시행 10000..30479** (`common.HISNR_SKIP0`; n = 20480 = 원 n 의 8 배, chunk 40) — 테스트 0..2559, 개발 2560.., P3 3200.., A1C5 4480.. 와 겹치지 않는다 |
| arm | V1 (M-ours-dscore-C-V1), b\* (M-ours-bstar), R2-ours-G, R1-turbo, R3-bigamp, R5-genie. 16 반복, CPU complex128 |
| 실행 | `bash code/run_hisnr16e4.sh` (선행 코드 9356aca5 + 검토 반영 코드 = 동결 커밋; 태그 HSB16e4k, HSNR16; 전제: conf/code·Demo 청결, 이 문서·DECISIONS tracked·clean, raw_HS* 없음). 실행 중 다른 CPU 작업 없음. 중단되면 `--resume` 으로 재개 (runner 가 끝난 청크를 건너뜀; 잘린 npz 는 지우고 기록); 끝난 태그의 재실행은 사용자 승인. `cpu_chain.sh` 가 SEEDS3 BLER 뒤 자동 실행 (DECISIONS 동결 줄 확인) |
| 수용 | `eval_accept.py --n 20480 --skip0 10000 --points <CELL>:6,9,12,15` (청크 {(10000 + 40k, 40)} × 4 점, meta ntrain·bstar·kron_K·ll_val, ckpt sha·role, iters 16). genie 재현 대조는 없다 (새 시행). 수용 실패 → 그 태그 무효·보고 없음·원인 기록 |
| 보고 (전부 보고 전용) | `hisnr_report.py`: SNR·arm 별 실패 수 / n, BLER, 95% Wilson; V1 대 b\* 짝지음 불일치 수와 exact 양측 부호검정 p (**판정 아님**); genie 실패의 L 분포·조건수 (`genie_floor.py --skip0 10000` 을 두 태그 모두에 **무조건** 적용). `hisnr_report.py` 는 arm 누락·load_raw 경고가 있으면 보고 없이 rc = 1. 원 태그 (n = 2560) 와 나란히 적되 합치지 않는다. 그림: 등록된 곡선을 대체하지 않고 별도 패널·표기로 싣는다 |
| 다중성 | 라벨 없음 → 해당 없음. p 값은 서술용 |
| 비용 | CPU (192 워커 전부): C2 ≈ 0.5 h, C6 ≈ 7.5 h (DOPaNR16 같은 arm 실측 ≈ 2400 s/청크 × 2048 태스크 / 192), 합계 ≈ 8.2 h |

## 2. 원고 문장 범위
"고SNR 구간의 BLER 은 추가 n = 20480 시행에서 …" 처럼 **보고 전용 보강**으로만 쓴다. 등록된 판정점·라벨·"전부" 문장은 원 태그의 것이다.

## 3. 미리 적는 예측 (보고 전용; 적중/빗나감만 기록)
1. D2 C2 +9..+15 dB 에서 genie BLER 이 0 보다 크고 (바닥), 그 실패의 대다수 (> 50 %) 가 L = 3 블록이다.
2. V1 BLER ≤ b\* BLER 이 네 SNR 모두에서 두 셀 모두 성립한다 (점추정).
3. **이 실행의** V1·b\* BLER 점추정이 원 태그 (n = 2560) 의 95% Wilson 구간 안에 든다 — 네 SNR × 두 arm × 두 셀 중 ≥ 14/16 (검토의 몬테카를로: 칸당 ≈ 0.94).

## 4. 선행 작업
| 항목 | 상태 |
|---|---|
| 코드 9356aca5 (HISNR_SKIP0, load_raw 오프셋, eval_accept --skip0, run_hisnr16e4.sh, hisnr_report.py) | 커밋됨 |
| 검토 반영 코드: run_hisnr16e4.sh (`--points`, genie_floor 무조건, 보고 rc 처리, 출력 머리말 HEAD, exit $FAIL, `--resume`), genie_floor.py `--skip0` (기본 0 = 기존 출력 동일 확인), hisnr_report.py (arm 누락·경고 시 rc 1), run_manifest.py (시행 ≥ 10000 을 HISNR 집합으로 표기) | 동결 커밋에 포함 |
| 적대적 검토 → v2 → 동결 → 실행 (CPU 순서: SEEDS3 BLER 뒤, cpu_chain 자동) | v2 = 이 커밋 |

## 5. 평가 전 고정 기록
| 항목 | 값 |
|---|---|
| 동결 커밋 | 이 문서를 담은 커밋 |

## 6. 결과 (이 절은 추가만 한다)
