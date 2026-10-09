# 기록 감사 — SITE16e4 §6.1 (헤드라인 셀 V4 → V1 짝 검정, 규칙 고정 사후 계산)

- 감사자: Fable 5.1 서브에이전트 (독립 기록 감사; 읽기 전용, 이 폴더에만 씀). 감사 시각 2026-10-08 23:18 CDT (= 10-09 13:18 KST; `TZ=America/Chicago date`).
- 대상: `conf/results/review_next/NEXT_EXPERIMENTS_SITE16e4.md` §6.1 (동결 커밋 9c4b6fe7 뒤 추가, 미커밋) — 원본 `conf/results/review_next/pairB_SITEB16e4k.txt`, 로그 `conf/logs/run_site16e4.log`, raw `conf/raw_B16e4k`.
- 독립 재계산: `recompute_site.py` (이 폴더; 자체 로더·`math.comb` 부호검정·자체 power guard/라벨·자체 앵커 규칙·자체 SNR@0.1 보간·자체 paired bootstrap; `pair_baselines.py`·`analysis.py`·`Demo/*` 를 import 하지 않음) → `recompute_site.out`.

## 판정

**§6.1 은 원본 출력·로그·동결 등록과 일치하고, raw 로부터의 독립 재계산이 모든 수 (실패 수, a:b, p, pooled, power guard, 라벨, 앵커 확인, SNR@0.1 격차와 90% 구간) 를 마지막 자리까지 재현한다. MUST 0 · SHOULD 1 · NIT 5. 반증 실패.**

## 발견 (MUST / SHOULD / NIT)

### MUST — 없음

### SHOULD-1. §6.1 :125 "V1·V4 체크포인트 … (출력 머리말, …)" — V4 부분은 출력 머리말에 없다

- 증거: 출력 :3·:17 은 `# base V1 checkpoint id: manifest (none), file d2sx_N160000_a1.pt 4443921ce8d5c4a1` — **V1 만** 말한다 (`pair_baselines.py` :170 이 base 의 `meta|stagec_ckpt` 로 찍는 줄). V4 가 같은 파일을 쓴다는 것은 raw 의 `meta|budget|M-ours-dscore-C-V4` (`ckpt=/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt`; `recompute_site.out` §2) 와 §0 에서 온다. 사실 자체는 맞다 (파일 sha256[:16] 재계산 4443921ce8d5c4a1).
- 제안 (:125 교체):
  `- 무결성 (출력 머리말, 두 단계 모두): `integrity: OK`; base `manifest-head:cd241b7e/chunks-sha:78cbb59fc01ce520`; V1 체크포인트 `d2sx_N160000_a1.pt 4443921ce8d5c4a1` (출력 3·17 행; §5 와 같다). V4 가 같은 파일을 쓴 것은 출력이 아니라 raw 의 `meta|budget|M-ours-dscore-C-V4` 의 ckpt 경로 (§0) 로 확인된다.`

### NIT-1. §6.1 :161 "a − b = +23 / +8 / -8" — ASCII 하이픈

- 머리말 (a)·§3 항목 0 은 "−8" (U+2212). 제안: `-8` → `−8`.

### NIT-2. §6.1 :124 "push 뒤 실행" — 초 단위로는 기록이 증명하지 못한다

- 증거: `git reflog show origin/main` → 9c4b6fe7 push 2026-10-09 13:08:47 KST (= 23:08:47 CDT); 로그·출력의 start 는 "23:08" (초 없음); 출력 파일 mtime 13:09:13 KST. 순서는 그럴듯하나 start 초가 없어 push(23:08:47) 뒤인지 확정 불가 (커밋 23:08:42 뒤인 것은 스크립트의 HEAD 검사로 확정).
- 제안: `push 뒤 실행` → `push (reflog 23:08:47 CDT) 와 같은 분에 실행; 스크립트의 HEAD = 동결 커밋 검사 통과`. 또는 그대로 두고 이 감사를 인용.

### NIT-3. §6.1 :143 "§2 에서 **고른** 문장" — 사후 선택으로 읽힐 수 있다

- 문장은 라벨이 기계적으로 정한 것이고 (§2 :69) 결과 뒤 고른 것이 없다 (:148 도 그렇게 적음). 제안: `§2 에서 고른 문장` → `§2 의 규칙이 라벨로 정한 문장`.

### NIT-4. SNR@0.1 격차의 점추정 미반올림 값은 +0.1425 dB — 둘째 자리 반올림 경계

- `recompute_site.out` §4: V4 −2.0839, V1 −2.2264, 차 +0.1425 → `gain` 문자열 `+0.14` (§2 규칙은 `gain` 문자열의 세 수를 그대로 쓰므로 기록은 맞다). 구간은 [+0.0567, +0.2334] → [+0.06, +0.23] (경계 아님). 제안 (선택): :140 끝에 `(미반올림 +0.1425 [+0.0567, +0.2334], 감사 재계산)` 을 덧붙여 뒤 감사가 셋째 자리에서 헷갈리지 않게.

### NIT-5. 원본 출력·로그가 아직 untracked

- `git status --porcelain` → `?? conf/results/review_next/pairB_SITEB16e4k.txt`, `?? conf/logs/run_site16e4.log` (conf/logs 는 ignore 되지 않음). §6.1 의 sha256[:16] e3d1e6a00b45f5e9 만이 원본을 고정한다. 제안: §6.1 커밋에 두 파일을 함께 넣는다 (§1 "출력 … 로그 …" 가 기록의 일부).

## 확인한 것 (항목별)

1. **독립 재계산 (raw → 자체 코드)**: 아래 표. 모든 수 일치. bootstrap 은 등록 §1 과 같은 설정 (B = 2000, `default_rng(20260925)`, 격자 7 점 순서로 SNR 마다 한 번 `rng.integers(2560, size=2560)` 을 뽑아 두 arm 에 같이 적용, log10(BLER)–SNR 선형 보간의 첫 하향 교차, 바닥 0.5/n, `nanpercentile` 5/95) 을 **내 코드로 다시 구현**한 것이라 자릿수까지 같은 것이 기대값이며 실제 같았다. 다른 seed (1) 로는 [+0.05, +0.24] (등록 설정 아님, 참고). p 는 `math.comb` 와 `scipy.stats.binomtest` 둘 다: 0.019187 / 0.255875 / 0.115318 / pooled 0.069233.
2. **짝의 유효성**: V1·V4 는 **같은 chunk 파일의 열**이다 (448 파일 모두 두 arm 의 `blk_err` (40, 16) 보유; chunk 마다 `run|seed` = 20260926·`run|skip`·`run|n` 이 파일명과 일치; `runner.run_task` :544–567 이 시행마다 (H, u, perm, Y) 를 한 번 뽑아 모든 arm 에 준다 → 06_SPEC §2 "셀 안에서 전 arm paired"). SNR 7 점 × 64 chunk, skip 0..2520 연속·겹침 없음, 2560 시행; `<arm>|failed` 키 없음 = raised 0 (V4/V1/b* 전 SNR); blk_err 전부 {0,1}. a + c = F_V4, b + c = F_V1, a − b = F_V4 − F_V1 이 세 점 모두 성립 (assert). 출처: chunks-sha 재계산 78cbb59fc01ce520, manifest git_commit cd241b7e, n_raw_files 448, written 2026-09-23 07:36:44 KST ≥ 모든 chunk mtime (2026-09-22 21:23–21:39 KST; 실행 2026-10-09 13:08–13:09 KST 뒤 바뀐 파일 0); raw 디렉토리 git-tracked 448 파일·clean; 체크포인트 sha256[:16] 4443921ce8d5c4a1 = manifest `stagec_checkpoint.sha256_16` (stored_epoch 1784, evaluated_weights last-epoch EMA = §0 "last-EMA @1784").
3. **실행 출처**: 출력 첫 줄 git 9c4b6fe7 = HEAD = `git log -1 -- REG` (동결 커밋; 커밋 시각 2026-10-08 23:08:42 CDT, author = committer); `git show 9c4b6fe7:conf/code/run_site16e4.sh | sha256sum` = 작업 사본 = b3bee226cf046878 = §5; `git status --porcelain conf/code Demo` 비어 있음; 등록 diff vs 9c4b6fe7 = `56 0` (추가만; 헤더·§0–§5·`## 6.` 제목 변경 없음); 로그 3 줄 (`start` 1, `drift check OK` 1, `SITE_DONE rc=0` 1; ABORT 없음); 출력의 드리프트 8 줄은 `git show 9c4b6fe7:conf/results/tables_D2_B16e4k.txt` :369·:372·:375·:378 과 글자 단위로 같고 (내 재계산도 같음), 출력의 ` -> ` 줄은 6 (쌍 머리줄 3 + POWERED 3: b*→V1, b*→V4, V4→V1 뿐); DECISIONS.md tracked·clean, 동결 커밋에 DECISIONS·WORK_QUEUE·검토 파일 포함.
4. **전사**: §6.1 의 긴 backtick 문자열 7 개 전부 출력/로그에 `grep -F` 로 존재; 표·D·방향·라벨 문자열·power guard 문장·"혼합 결과 해당 없음"·해시·시각 전부 일치 (아래 표). 기록 시각 23:10 CDT = 등록 파일 mtime 13:10:25 KST.
5. **§2 문장**: (iii) 문장은 §2 :69 와 바이트 동일 (sed 비교); 공통 문장은 §2 :70 에 x=0.14, l=+0.06, u=+0.23 을 채운 것과 바이트 동일; 채움 규칙 (x 양수 → 부호 없음, l·u 는 `$+0.06$` 꼴) 준수. 부호: `gain(x=V4, y=V1)` = SNR@0.1(V4) − SNR@0.1(V1) = +0.14 > 0 ⟺ V4 가 0.1 에 닿는 SNR 이 0.14 dB 높다 ⟺ V1 (\ours) 이 더 낮은 SNR 에서 닿는다 → "gain of \ours{} over \scdiff{} = 0.14" 가 맞다 (기존 원고 문장 "1.27 dB lower SNR" 이 b* − V4 = +1.27 인 것과 같은 관례). 단, \ours = V1·\scdiff = V4 라는 매크로 정의 자체는 이 저장소에 없다 (아래 "확인 못 한 것").
6. **§3 채점**: §3 의 1–6 전부 채점, 7 (빗나갈 경로) 은 "일어나지 않았다" 로, 0 은 채점 안 함 + 확인 — §3 에 없는 항목을 채점하지 않았고 빠진 것도 없다. 각 항목의 보조 조건까지 성립: 2) D = 89 ≤ 125, c = 338 ≥ 320; 3) D = 38 ≥ 14, c = 73 ≤ 85; 4) D = 20 ≥ 14, c = 15 ≤ 18; 5) pooled D = 147 ≥ 127; 6) 하한 +0.06 > 0. 머리말 (c)(d)(e) 의 산술도 재계산과 일치 (10:2 p = 0.0386, 11:3 0.0574, 74:51 0.0487, 75:52 0.0505; a − b = 23 → D ≤ 125, 8 → D ≤ 12; c(−3) ≥ 321 + 338 − 623 = 36). "적중 6, 빗나감 0" 맞다.
7. **금지 표현**: §6.1 :116–170 에서 "비긴다|동등|차이 없음|tie|equal" 은 :164 의 부정문 한 곳뿐; 동등을 암시하는 다른 문장 없음; 해석 문장 없음 (지위·범위·규칙 인용은 사실 서술).
8. **지위·범위 가독성**: "규칙 고정 사후 계산 — 두 arm 의 BLER 표·실패 수를 본 뒤에 규칙을 고정" (:166), 범위 (:167), §3 표 머리의 "본 뒤의 것" 이 모두 적혀 있어 사전 등록으로 오독할 여지는 작다. NIT-3 의 "고른" 만 손질.
9. 기타: "V1 과 V4 를 함께 든 쌍은 없다" — 커밋본 표에서 두 이름이 같이 든 줄 0 (grep); V4 가 든 쌍은 :343·:373·:403 셋 (CONTRIBUTIONS.md :34 는 "둘뿐" — §6.1 의 지적이 맞다). V4 기준 앵커 규칙 재계산 ['-3', '+0', '+3'] (V4 BLER −3: 0.1539, 0: 0.0375, +3: 0.0082, +6: 0.0063 → |log10(·/0.1)| 최소 셋).

## 수치 대조표 — §6.1 의 모든 수

| §6.1 기록값 | 출력 파일 / 로그 / git | 독립 재계산 (`recompute_site.out`) | 일치 |
|---|---|---|---|
| 로그 3 줄: `start (git 9c4b6fe7)` 23:08, `drift check OK` 23:09, `SITE_DONE rc=0 (… -> (iii))` 23:09 | 로그 :1–3 동일 | — | ✓ |
| 동결 커밋 9c4b6fe7, 커밋 시각 2026-10-08 23:08:42 CDT | `git log -1 9c4b6fe7` 23:08:42 CDT (author=committer); HEAD = 9c4b6fe7 = `git log -1 -- REG` | — | ✓ |
| 출력 첫 줄 (git 9c4b6fe7 … sha256[:16] b3bee226cf046878 … code/run_site16e4.sh) | 출력 :1 동일; `git show 9c4b6fe7:…sh` sha = 작업 사본 sha = b3bee226cf046878 | — | ✓ |
| 원본 sha256[:16] e3d1e6a00b45f5e9 | `sha256sum pairB_SITEB16e4k.txt` e3d1e6a00b45f5e9 | — | ✓ |
| 기록 시각 23:10 CDT (= 13:10 KST) | 등록 파일 mtime 2026-10-09 13:10:25 KST | — | ✓ |
| conf/code·Demo 청결; 재실행·ABORT 없음 | `git status --porcelain conf/code Demo` 비어 있음; 로그에 ABORT 0, start 1 | — | ✓ |
| `integrity: OK` (두 단계) | 출력 :4·:18 | 구조 문제 없음 (raised 0, 2560 시행, 연속 chunk) | ✓ |
| base manifest-head:cd241b7e/chunks-sha:78cbb59fc01ce520 | 출력 :4·:18 | 재계산 78cbb59fc01ce520; manifest git_commit cd241b7e | ✓ |
| V1·V4 체크포인트 d2sx_N160000_a1.pt 4443921ce8d5c4a1 | 출력 :3·:17 (**V1 만**; SHOULD-1) | 파일 sha 4443921ce8d5c4a1; raw meta 의 V1·V4 ckpt 경로 동일 | ✓ (출처 표기만 손질) |
| DRIFT CHECK 줄 "8 recorded lines … 4 of them … both labels (i) 3/3" | 출력 :15 동일; 4 줄 = `git show 9c4b6fe7:…tables_D2_B16e4k.txt` :369·:372·:375·:378 | — | ✓ |
| b*→V1 302:50 · 117:21 · 35:7, pooled 454:78, +1.41 [+1.22, +1.64], 실패 623/184/57·371/88/29 | 출력 :6·:8·:9 | §5: 동일 (p 4.7e-45·2.4e-17·1.5e-05·1.7e-65 포함) | ✓ |
| b*→V4 285:56 · 111:23 · 42:6, pooled 438:85, +1.27 [+1.08, +1.50], 실패 623/184/57·394/96/21 | 출력 :11·:13·:14 | §5: 동일 (p 4.5e-38·5e-15·1e-07·2.8e-58 포함) | ✓ |
| "출력 5–14 행" | 드리프트 블록 = :5–:14 | — | ✓ |
| V4→V1 머리줄, FIXED, 확인 줄 ['-3', '+0', '+3'], decision SNRs ['-3', '+0', '+3'] | 출력 :19 동일 | 앵커 규칙(V4) = ['-3', '+0', '+3'] | ✓ |
| a:b 56:33 / 23:15 / 6:14 / pooled 85:62 | 출력 :20 | 56:33 / 23:15 / 6:14 / 85:62 (a = V4 만 실패, b = V1 만 실패 — 코드 `paired(d, x=V4, y=V1)`: a = (ex==1)&(ey==0)) | ✓ |
| p 0.019 / 0.26 / 0.12 / 0.069 | 출력 :20 | 0.019187 / 0.255875 / 0.115318 / 0.069233 (comb·scipy 동일) | ✓ |
| 방향: V1 쪽 유의 / V1 쪽 비유의 / V4 쪽 비유의 / pooled V1 쪽 비유의 | a>b, p<.05 / a>b / b>a / a>b | 동일 | ✓ |
| D = 89 / 38 / 20 / 147 | 56+33 / 23+15 / 6+14 / 85+62 | 89 / 38 / 20 / 147 (c = 338 / 73 / 15) | ✓ |
| 실패 수 V4·V1 394·371 / 96·88 / 21·29 | 출력 :23 | 394/371, 96/88, 21/29 | ✓ |
| POWERED=True, second arm fewer 1/3, first arm fewer 0/3 → (iii); "세 점 모두 ≥ 6" | 출력 :21 | POWERED (3/3 점 D ≥ 6), wy 1, wx 0 → (iii) | ✓ |
| 혼합 결과 해당 없음 | +3 dB p = 0.12 ≥ .05 | mixed = False | ✓ |
| SNR@0.1 격차 +0.14 dB [90% +0.06, +0.23; censored 0%] | 출력 :22 동일 | +0.1425 → +0.14; [+0.0567, +0.2334] → [+0.06, +0.23]; censored 0% | ✓ |
| 원고 문장 0.14\,dB [$+0.06$, $+0.23$] | §2 :70 채움 (바이트 동일) | 같은 수 | ✓ |
| (iii) 문장 | §2 :69 바이트 동일 | — | ✓ |
| 채점 6 항목 ✓, "적중 6, 빗나감 0" | 각 결정 수 = 출력 :20·:22 | 각 조건 재검 (위 6.) | ✓ |
| 항목 0 확인: a − b +23 / +8 / −8, pooled +23; 점추정 +0.14; (ii)·(iv) 아님 | 출력 :20·:22·:23 | +23 / +8 / −8, +23; +0.14; (iii) | ✓ (NIT-1 하이픈) |
| CONTRIBUTIONS.md §0 :34 "둘" 이나 실제 셋 (:343·:373·:403) | `git show 9c4b6fe7:…tables` grep: :343·:373·:403; CONTRIBUTIONS :34 "둘뿐" | — | ✓ |
| 범위: C2 8×4, N′ = 1.6e5, raw_B16e4k, last-EMA 가중치, −3/0/+3 | manifest cells.C2 Nr 8 Nt 4, ntrain 160000, evaluated_weights last-epoch EMA | — | ✓ |

## 확인하지 못한 것

- **원고 매크로**: `\ours{}` = V1, `\scdiff{}` = V4 라는 정의는 ICC 원고 저장소 (T2-ICC2027-paper) 에 있고 이 저장소에는 .tex 가 없다 (`find ~ -maxdepth 4 -name '*.tex'` + grep scdiff: 0). 등록 §0 :15 의 "V4 … 원고 이름 scalar-site diffusion prior" 와 기존 원고 문장의 관례 (b* − V4 = +1.27 "lower SNR") 로만 부호 방향을 확인했다.
- **§4 의 회귀·스모크 ("기본 경로 … `pairB_STB16e4k.txt` 와 비트 동일", §6.1 :165 가 인용)**: 산출물이 세션 스크래치패드에 있어 저장소에 없고, 재현하려면 baseline 13 쌍을 다시 계산해야 하므로 (범위 밖) 하지 않았다. 드리프트 쌍 2 개는 내 코드로 재현했다.
- **"push 뒤 실행"** 의 초 단위 순서 (NIT-2).
- **짝의 의미적 동일성 (같은 H·잡음)**: raw 에 채널·잡음 배열이 없어 비교할 수 없다; 같은 chunk 파일·같은 `run|seed`·`runner.run_task` 의 구조로만 확인했다.
- 기록자·시각 서술 중 사람의 행위 (사용자 결정 22:21 CDT, "Opus 5.5", 사용자 알림) 는 기록 밖이라 확인 대상이 아니다.
