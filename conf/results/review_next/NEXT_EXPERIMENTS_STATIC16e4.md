# NEXT_EXPERIMENTS_STATIC16e4 — 정적 6 데이터셋에서 V1 대 **등록된 baseline 전부** (기존 raw 의 표 B; 규칙 고정 사후 계산, 등록 v2)

- 작성: 2026-09-29 17:01 CDT (= 09-30 07:01 KST) 초안 v1 (Opus 5.5) → 적대적 검토 1건(Fable 5.1 서브에이전트; 반드시 6·권고 7; `prereg_reviews_2026-09-29/review_STATIC16e4.md`) 반영 v2 (2026-09-29 17:31 CDT, Opus 5.5) → 동결 커밋(`DECISIONS.md` 같은 줄). 커밋 뒤 §1~§3 을 바꾸지 않는다.
- 틀: `NEXT_EXPERIMENTS_SUPP16e4.md` §1–§2 (baseline 집합 𝔅, 라벨, X\*, R_X, "전부" 문장 조건, genie ≥ V1 가드, R0-pilot @1) — **규칙을 그대로 쓴다**. `code/pair_baselines.py`.
- **작성 시점 공개 (중요)**: 사용자 지시 2026-09-29 CDT ("빈 곳도 계획에 올려 적절한 순서로"; 빈 곳 1 = "정적 조건에서 V1 대 등록 baseline 전부의 표 B 가 한 번도 계산되지 않았다"). **이 등록은 새 BLER 을 돌리지 않는다**: 6 데이터셋의 raw (14 arm 루프 + PIL + ALD, 같은 테스트 시행) 가 이미 있고, 작성자는 그 raw 의 **실패 수 표와 곡선을 이미 봤다** — `tables_D2_<TAG>.txt` (전 arm BLER), 그림 F21 (R1·R2·R3·b\*·V1·genie 곡선), 등록 `ALD16e4`·`PILOT16e4` §6 (ALD·파일럿 전용 arm 의 표 B 라벨), 각 a1 등록 §6 (b\* → V1). `R2-ours-G → V1` 도 analysis 표 B 에 이미 있다 (6/6 (i); `tables_D2_<TAG>.txt`). X\* 와 R_{X\*} 도 이미 공개된 −3 dB 실패 수로 결정돼 있다 (§0). 따라서 **새로 계산되는 것은 표 B 라벨 48 개** (8 arm — b\*-scalar, gmm32, R0-pilot@1, R1, R3, R4-llr, R4-scvamp, bstar-pilot — × 6 데이터셋) 뿐이고, "전부" 문장은 문장이 가능한 4 데이터셋에서 **새 8 arm 이 모두 (i) 인가** 하나에만 걸려 있다. 원고 명칭은 "사전 등록" 이 아니라 **"규칙 고정 사후 계산"** 을 권고한다 (사용자 결정 대기). 따라서 이 문서의 결과는 **이미 본 곡선 위의 사후 형식 검정**이라는 한계를 가지며, 원고 인용 시 그렇게 적는다. 규칙은 SUPP16e4 와 한 글자도 다르지 않게 고정해 선택의 여지를 없앤다.
- 목적: 원고의 중심인 정적 결과에서 "V1 이 등록된 baseline 13 개 각각보다 적게 실패하는가" 를 비정상 조건(SUPP16e4·ROTMIX16e4·S2V16e4)과 같은 형식으로 적는다. 어느 결과도 기존 등록의 라벨을 바꾸지 않는다.

---

## 0. 알고 있는 것 (판정에 쓰지 않는다; 각 등록 §6 전사)

| 데이터셋 (base raw / PIL / ALD, 셀, prior) | b\* → V1 | V1-pilot → V1 (PILOT16e4 P1) | ALDv-pilot → V1 (ALD16e4 A1) | ALD-pilot → V1 (A2) | R2-ours-G → V1 (analysis 표 B) |
|---|---|---|---|---|---|
| D2 C2 헤드라인 (`raw_B16e4k` / `raw_PILB16e4k` / `raw_ALDB16e4k`, C2, S2) | (i) | (i) | (i) | (i) | (i) 778:69 |
| D2 C6 (`raw_NR16B16e4` / `raw_PILNR16` / `raw_ALDNR16`, C6, S2) | (i) | **(iv)** | (i) | (i) | (i) 396:10 |
| D3 (`raw_D3B16e4` / `raw_PILD3` / `raw_ALDD3`, C2, S2c) | (i) | (i) | (i) | (i) | (i) 705:50 |
| SV8e (`raw_SVB16e4` / `raw_PILSV` / `raw_ALDSV`, C2, SV8e) | **(iv)** | **(iv)** | (i) | (i) | (i) 302:59 |
| UMi28 (`raw_U28B16e4` / `raw_PILU28` / `raw_ALDU28`, C2, UMi28) | (i) | (i) | (i) | (i) | (i) 409:41 |
| MIX3 (`raw_MXB16e4` / `raw_PILMX` / `raw_ALDMX`, C2, MIX3; 보고 전용 부속 점) | (i) | (i) | (i) | (i) | (i) 387:30 |

- **X\* 와 R_{X\*} (이미 결정됨; 공개 −3 dB 실패 수 — ALD16e4 §6.1, TABLE A)**: X\* = b\* 인 곳 D2 C2 (623 < V1-pilot 626), D3 (1298), SV8e (464), UMi28 (1270), MIX3 (1421) — R_{b\*}(−3 dB) = 0.470 [0.427, 0.512], 0.367 [0.335, 0.399], 0.143 [0.095, 0.188], 0.062 [0.033, 0.089], 0.090 [0.062, 0.117] (각 a1 등록); **C6 만 X\* = V1-pilot** (83 < b\* 184; R_{V1-pilot} 만 새 값).
- ALD 추정 파일: `results/ald/ald_PIL<suf>.npz` (ALD16e4 는 추정 태그를 PIL 태그로 저장; `--est PIL<suf>`).
- **이미 정해진 사실**: "등록된 baseline 전부와 멀어진다" 문장은 **D2 C6 (V1-pilot (iv)) 과 SV8e (b\* (iv), V1-pilot (iv)) 에서 결과와 무관하게 불가능**하다. 가능한 곳은 4 데이터셋 (D2 C2, D3, UMi28, MIX3) 이고, 그 넷에서 R_{X\*} 하한 > 0 은 이미 성립한다. §0 의 다섯 라벨 (b\*, V1-pilot, ALD-pilot, ALDv-pilot, R2) 이 재계산과 다르면 코드 드리프트로 보고 그 데이터셋에 문장을 쓰지 않는다 — `pair_baselines --expect-bstar` / `--expect ARM=LABEL` 이 기계적으로 rc = 1 을 낸다.

## 1. 고정되는 것

| 항목 | 값 |
|---|---|
| **입력 (새 실행 없음)** | 위 표의 raw 18 디렉터리 (테스트 시행 0..2559, n = 2560, 7 SNR, 16 반복). base raw 는 14 arm (V0·V1·V4·V4b·b\*·b\*-scalar·gmm32·R0·R1·R2·R3·R4-llr·R4-scvamp·genie) |
| **명령 (데이터셋마다; CPU, GPU 숨김)** | `CUDA_VISIBLE_DEVICES= python code/pair_baselines.py --base raw_<TAG> --pil raw_PIL<suf> --ald raw_ALD<suf> --est PIL<suf> --cell <C2|C6> --prior <PR> --r0 at1 --provenance manifest --expect-bstar "<§0 b*>" --expect "V1-pilot=<§0>" --expect "ALD-pilot=<§0>" --expect "ALDv-pilot=<§0>" --expect "R2-ours-G=(i)" >> results/review_next/pairB_ST<TAG>.txt` (첫 줄 = 스크립트 HEAD) — (TAG, suf, cell, prior) = (B16e4k, B16e4k, C2, S2), (NR16B16e4, NR16, C6, S2), (D3B16e4, D3, C2, S2c), (SVB16e4, SV, C2, SV8e), (U28B16e4, U28, C2, UMi28), (MXB16e4, MX, C2, MIX3). 스크립트 `code/run_static16e4.sh` |
| **무결성 (`pair_baselines` 가 라벨 전에 검사)** | SUPP16e4 §1 과 같다 (점 집합 = 셀 격자, load_raw 경고 없음, genie 4 키 PIL/ALD = base, 2560 시행, 파일럿 전용·ALD raised 0, V1-pilot@1 = V1@1, bstar-pilot@1 = b\*@1, ALD 추정 고정·사전 계산값, ALD 추정의 체크포인트 = base 의 V1 체크포인트) — **단 코드 버전 검사는 `--provenance manifest`**: 이 18 raw 는 `run|git` 이전에 쓰였다(청크에 키 없음). 검사: 각 raw 의 `run_manifest_<tag>.json` 이 **git-tracked·clean**, n_raw_files = 청크 수, manifest 점 목록 = raw 점 집합, **모든 청크 mtime ≤ manifest `written`**, git-tracked raw 디렉터리(raw_B16e4k 등)는 clean. 머리말의 `manifest-head:<commit>` 은 **매니페스트를 쓴 시점의 HEAD** (run_manifest.py) 이지 실행 커밋이 아니다 — 실행 커밋은 각 등록 §6·EXPERIMENTS 행의 값 (예: B16e4k 98e22f8, SV8e 07a8935a, UMi28·MIX3 80bae849, D3 07a8935a, PIL 92d26757, ALD 7e64f5cc). 머리말에는 raw 마다 **청크 sha256 목록의 sha256 (`chunks-sha:`)** 도 찍어 이후 감사가 raw 를 고정한다. `meta|stagec_ckpt_id` 가 없는 raw (B16e4k) 는 manifest 의 stagec_ckpt_id (B16e4k 는 "(none)") → 없으면 `meta|stagec_ckpt` 가 가리키는 파일의 sha256[:16] (현재 4443921ce8d5c4a1 = SUPP16e4 DS 표·eval_accept 기록값) 을 ALD 추정과 대조한다. 실패 → 그 데이터셋 무효 (라벨 없음, 원인 기록) |
| **𝔅 (12) · 판정 · 라벨 · X\* · R_X · 가드 · 다중성** | **SUPP16e4 §1 의 해당 칸 원문 그대로** (𝔅 = b\*-scalar, gmm32, R0-pilot (@1), R1, R2, R3, R4-llr, R4-scvamp, bstar-pilot, V1-pilot, ALD-pilot, ALDv-pilot; 표 B `X → V1`, 판정점 = 앵커 X 기준 자동, 08_SPEC §2 (i)–(iv); X\* = 𝔅 ∪ {b\*} 중 −3 dB 실패 최소 (동률 이름순); R_X paired bootstrap B = 2000, default_rng(20260926), 포화 가드 + genie ≥ V1 가드; 절대 격차 F_X − F_V1). 다중성: 6 × 12 = 72 라벨 = 인용 24 (R2·V1-pilot·ALD·ALDv) + **새 48**; b\* 6 은 별도 인용; 보정 없음, 개수 문장만 |
| **주 라벨** | D2 C2 헤드라인의 **"𝔅 전부" 판정**: k𝔅 = 12 이고 m𝔅 = 0 → **(A) "V1 이 𝔅 12 개 전부보다 적게 실패"**; 그 밖 → (B) 개수 문장. 나머지 5 데이터셋 = 측정 라벨 (개수 서술만) |
| **"전부" 문장** | 데이터셋마다: 원 b\* 라벨 (i) **이고** k𝔅 = 12 **이고** m𝔅 = 0 **이고** R_{X\*} CI 하한 > 0 → "데이터셋 d 에서 등록된 baseline 전부(13 개)와 멀어진다 (이 셀·예산·prior 한정; 이미 본 곡선 위의 사후 형식 검정)" |
| 보고 전용 | R_X 표 전부, 절대 격차, SNR@0.1 격차, −3 dB 실패 수(전 arm), R0-pilot @16 판독, 채널 추정 NMSE@16 중앙값 |
| 비용 | CPU 수 분 × 6 (새 BLER 없음) |

## 2. 라벨·문장
SUPP16e4 §2 표 그대로 (k𝔅 = 12·m𝔅 = 0 → "V1 이 𝔅 12 개 전부보다 적게 실패"; + b\* (i) + R_{X\*} 하한 > 0 → "등록된 baseline 전부(13 개)와 멀어진다"; 그 밖 → 개수 문장; (iv) 는 k 에 세지 않는다). 원고 문장 범위: 이 셀·예산·prior, 그리고 "사후 형식 검정" 캐비엇.

## 3. 미리 적는 예측 (곡선·표를 본 뒤의 예측임을 공개; 열린 48 라벨에 대해서만; 각 항목 적중/빗나감)
0. 이미 실현된 것 (채점 안 함): b\* 6, R2 6 (전부 (i)), P1 6 (4 (i), C6·SV8e (iv)), A1 6·A2 6 (전부 (i)), X\*·R_{X\*} (§0), "전부" 문장 불가 2 곳 (C6, SV8e).
1. 주 라벨 D2 C2 = **(A)** (= D2 C2 의 새 8 arm 모두 (i)).
2. D3 의 새 8 arm 모두 (i).
3. UMi28 의 새 8 arm 모두 (i).
4. MIX3 의 새 8 arm 모두 (i).
5. C6 의 새 8 arm 모두 (i) (→ k𝔅 = 11, V1-pilot 만 (iv)).
6. SV8e: b\*-scalar·gmm32 둘 다 (iv) (한 항목; 근거 b\* 와 같은 판정점 문제), 나머지 새 6 arm 모두 (i) (한 항목).
7. (ii) 는 새 48 라벨 중 0 개.
8. 빗나갈 경로: 무결성 실패 → 그 데이터셋 무효; `--expect` 불일치 → 코드 드리프트, 그 데이터셋 문장 없음.

## 4. 선행 작업
| 항목 | 상태 |
|---|---|
| `pair_baselines.py` `--provenance manifest` (run|git 이전 raw 의 출처 = run manifest) + `meta|stagec_ckpt_id` 없는 raw 의 체크포인트 id (파일 sha) | 구현 (이 동결 커밋에 포함). 기본값 run-git 은 동작 불변 |
| 스모크 (v2 코드): (a) RMX15 회귀 — 기본 경로(run-git) 출력이 v1 코드 출력과 비트 동일, 2 행~끝은 커밋본 `pairB_RMX15.txt` 와 동일 (1 행 머리말은 SUPP16e4 때 바뀐 형식); (b) 정적 6 데이터셋 **무결성 줄만** 확인 — 출력은 머리말·체크포인트 줄만 읽고 즉시 삭제 (라벨·수치 미열람): 6/6 "integrity: OK" (manifest tracked·clean, mtime, 점 목록, 청크 수 통과), B16e4k 체크포인트 id: manifest (none) → 파일 4443921ce8d5c4a1. 첫 v2 스모크에서 B16e4k 가 manifest 의 문자열 "(none)" 을 id 로 읽어 실패 → 코드 정정 뒤 통과 | 완료 (작성자, 동결 직전) |
| `code/run_static16e4.sh` | 이 동결 커밋에 포함 |
| 적대적 검토 → v2 → 동결 → 실행 → §6 → 기록 감사 | 대기 |

## 5. 평가 전 고정 기록
| 항목 | 값 |
|---|---|
| 동결 커밋 | 이 문서를 담은 커밋 (해시는 §6 첫 줄) |

## 6. 결과 (이 절은 추가만 한다)

### 6.1 결과 (기록 2026-09-29 17:36 CDT (= 09-30 07:36 KST), Opus 5.5 — 전사만, 해석 없음; 원본 `results/review_next/pairB_ST<TAG>.txt` 6 개, 로그 `logs/run_static16e4.log`)

**동결 커밋**: 2139f082. **실행**: `bash code/run_static16e4.sh` 2026-09-29 17:31 ~ 17:33 CDT (git 2139f082; 전제 검사 통과), `STATIC_DONE ok=6 fail=0`. 무결성 6/6 OK (`--provenance manifest` 검사 포함), `--expect` 다섯 라벨 (b\*, V1-pilot, ALD-pilot, ALDv-pilot, R2) 6/6 일치 — 코드 드리프트 없음. 새 BLER 없음.

**주 라벨 (D2 C2)**: k𝔅 = 12, m𝔅 = 0 → **(A) "V1 이 𝔅 12 개 전부보다 적게 실패"**; 원 b\* (i), R_{X\*} 하한 0.427 > 0 → **"D2 C2 헤드라인에서 등록된 baseline 전부(13 개)와 멀어진다 (이 셀·예산·prior 한정; 이미 본 곡선 위의 규칙 고정 사후 계산)"**.

**데이터셋별 (각 pairB_ST 파일의 `SUMMARY-B`·X\*·문장 줄 그대로)**:

| 데이터셋 | 원 b\* | k𝔅 · m𝔅 · 판정 못함 | (i) 아닌 X (𝔅) | X\* (F −3 dB) · R_{X\*} [90%] | "전부" 문장 조건 |
|---|---|---|---|---|---|
| D2 C2 (헤드라인) | (i) | 12 · 0 · 0 | — | M-ours-bstar (623) · 0.470 [0.427, 0.512] | 충족 |
| D2 C6 | (i) | 11 · 0 · 1 | V1-pilot (iv) | V1-pilot (83) · 0.492 [0.355, 0.630] | 불충족 |
| D3 | (i) | 12 · 0 · 0 | — | M-ours-bstar (1298) · 0.367 [0.335, 0.399] | 충족 |
| SV8e | (iv) | 9 · 0 · 3 | M-ours-bstar-scalar (iv), M-ours-gmm32 (iv), V1-pilot (iv) | M-ours-bstar (464) · 0.143 [0.095, 0.188] | 불충족 |
| UMi28 | (i) | 12 · 0 · 0 | — | M-ours-bstar (1270) · 0.062 [0.033, 0.089] | 충족 |
| MIX3 (보고 전용) | (i) | 12 · 0 · 0 | — | M-ours-bstar (1421) · 0.090 [0.062, 0.117] | 충족 |

D2 C2 의 `X → V1` (판정점 · pooled a:b · 라벨; 전체 수치는 `pairB_STB16e4k.txt`):

| X | 판정점 | pooled | 라벨 |
|---|---|---|---|
| M-ours-bstar | -3/+0/+3 | 454:78 | (i) 3/3 |
| M-ours-bstar-scalar | -3/+0/+3 | 498:73 | (i) 3/3 |
| M-ours-gmm32 | -3/+0/+3 | 565:78 | (i) 3/3 |
| R0-pilot@1 | +3/+6/+9 | 832:0 | (i) 3/3 |
| R1-turbo | +0/+3/+6 | 724:12 | (i) 3/3 |
| R2-ours-G | -3/+0/+3 | 778:69 | (i) 3/3 |
| R3-bigamp | +3/+12/+15 | 461:4 | (i) 3/3 |
| R4-llr | +9/+12/+15 | 1623:2 | (i) 3/3 |
| R4-scvamp | +3/+6/+9 | 759:2 | (i) 3/3 |
| bstar-pilot | -3/+0/+3 | 814:41 | (i) 3/3 |
| V1-pilot | -3/+0/+3 | 347:51 | (i) 2/3 |
| ALD-pilot | -3/+0/+3 | 678:54 | (i) 3/3 |
| ALDv-pilot | -3/+0/+3 | 644:50 | (i) 3/3 |

머리말 출처 (`manifest-head` = 매니페스트 작성 시점 HEAD — 실행 커밋 아님; `chunks-sha` = raw 별 청크 sha256 목록의 sha256[:16]):

- D2 C2 (헤드라인): base=manifest-head:cd241b7e/chunks-sha:78cbb59fc01ce520 pil=manifest-head:92d26757/chunks-sha:e1ff7ae11ab9eda1 ald=manifest-head:7e64f5cc/chunks-sha:d7a8d327661b00b5
- D2 C6: base=manifest-head:2a36737c/chunks-sha:279cdea5c7a4f054 pil=manifest-head:bfe80c48/chunks-sha:f3eced0a9aa7c393 ald=manifest-head:7e64f5cc/chunks-sha:8b4b4bf4755b0b58
- D3: base=manifest-head:07a8935a/chunks-sha:8777a3522b9ca2e8 pil=manifest-head:bfe80c48/chunks-sha:c02bf6d734e54309 ald=manifest-head:7e64f5cc/chunks-sha:4c15ac9e03fe9906
- SV8e: base=manifest-head:5e074fe6/chunks-sha:6abcfe3dca147362 pil=manifest-head:bfe80c48/chunks-sha:2fa74014713dd514 ald=manifest-head:7e64f5cc/chunks-sha:a207f60d1535131c
- UMi28: base=manifest-head:344d084c/chunks-sha:213dd3a3a3226fa6 pil=manifest-head:bfe80c48/chunks-sha:16528b7b3d370102 ald=manifest-head:7e64f5cc/chunks-sha:e9bf7e57af506811
- MIX3 (보고 전용): base=manifest-head:344d084c/chunks-sha:2d948d75b20605f9 pil=manifest-head:bfe80c48/chunks-sha:33db9f82f3908d76 ald=manifest-head:7e64f5cc/chunks-sha:7d1d2d08045d7133

**집계 (개수 서술만, 보정 없음)**: 새 48 라벨 중 (i) 46, (iv) 2 (SV8e 의 b\*-scalar·gmm32), (ii) 0. 72 라벨 전체 (인용 24 포함) 중 (ii) 0. k𝔅 = 12 인 데이터셋 4/6 (D2 C2·D3·UMi28·MIX3). "등록된 baseline 전부와 멀어진다" 문장 **4/6 충족** — 문장이 가능하던 4 곳 모두 (C6·SV8e 는 §0 에서 불가).

**§3 예측 채점**:

| # | 예측 | 결과 | 채점 |
|---|---|---|---|
| 0 | 이미 실현된 것 | b\*·R2·P1·A1·A2·X\*·R_{X\*} 모두 §0 과 같음 (`--expect` 통과, X\*·R 은 §0 값 그대로) | 채점 안 함 |
| 1 | 주 라벨 D2 C2 (A) | (A) | ✓ |
| 2 | D3 새 8 arm 모두 (i) | 8/8 (i) | ✓ |
| 3 | UMi28 새 8 arm 모두 (i) | 8/8 (i) | ✓ |
| 4 | MIX3 새 8 arm 모두 (i) | 8/8 (i) | ✓ |
| 5 | C6 새 8 arm 모두 (i) (k𝔅 = 11) | 8/8 (i), k𝔅 = 11 | ✓ |
| 6a | SV8e b\*-scalar·gmm32 둘 다 (iv) | 둘 다 (iv) | ✓ |
| 6b | SV8e 나머지 새 6 arm 모두 (i) | 6/6 (i) | ✓ |
| 7 | 새 48 라벨 중 (ii) 0 | 0 | ✓ |

합계: 적중 8, 빗나감 0.

**보고 전용**: 데이터셋 × X 의 R_X (1차·2차)·절대 격차·SNR@0.1 격차, 전 arm −3..+15 dB 실패 수 (R0 @16 포함), NMSE@16 중앙값 → 각 `pairB_ST<TAG>.txt`. C6 의 R_{V1-pilot} (−3 dB) 0.492 [0.355, 0.630] 은 이 계산에서 처음 나온 값이다.

- 원고 명칭 (사용자 결정 09-29 17:48 CDT): **"규칙 고정 사후 계산"** — DECISIONS 같은 시각 줄.

### 6.2 기록 감사 (Fable 5.1 서브에이전트, 2026-09-29 17:57 CDT = 09-30 07:57 KST; `prereg_audit_2026-09-29/audit_STATIC16e4.md` (`recompute_static.py` → `recompute_static.out`); raw npz 18 디렉터리에서 독립 재계산 — pair_baselines·analysis 미호출)

정정 없음. 무결성 6/6, 출처 검사 18/18 raw (manifest tracked·clean, 청크 수·점 목록, 청크 mtime ≤ written, raw_B16e4k git-clean), 머리말의 manifest-head 18·chunks-sha 18 개, 표 B 78 라벨 전부, X\*·R_{X\*}·문장 조건, §0 과의 대조(드리프트 0), 집계와 §3 채점 8/8 이 재현됐다. 동결 뒤 문서 diff 는 추가만, `conf/code`·`Demo` diff 없음.

메모: (1) §0 (동결 본문) 의 "ALD16e4 §6.1, TABLE A" 는 표 이름이 아니라 `NEXT_EXPERIMENTS_ALD16e4.md` 112 행 산문의 수치다 (값은 일치; 동결 본문이라 고치지 않는다). (2) 원고 명칭 결정 줄은 §6.1 끝에 추가됐다 (추가만). (3) 보고 전용: R_X 1차가 포화 가드로 정의되지 않는 것은 D3·UMi28·MIX3 의 R4-llr 세 개뿐. (4) pairB_ST 의 condition 줄은 재계산 b\* 기준이고 §1 문장 조건은 원 b\* 기준 — 드리프트 0 이라 결과 동일. (5) B16e4k manifest 는 마지막 청크보다 10 시간 뒤에 쓰였다 (§1 에 미리 적은 대로; raw 가 git-tracked clean).
