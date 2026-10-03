# SCALE16e4 사전 등록 — 3차·4차 검증 원문 (Fable 5.1, 워크플로 wf_70b2c9ef-8c9)
3차 = v3(2차 검토 반영본) 대상, 4차 = 3차 반영본 대상. 각 차수마다 먼저 검증 대상을 만든 반영자(Opus 5.5) 보고 원문, 이어서 렌즈별 검증 원문. 4차 반드시 2 건(integ4-1, integ4-2)은 주 세션이 문안 그대로 적용(등록 문서 머리 목록 '4차 검증 반영').

## 3차 검증

### 검증 대상을 만든 반영자 보고 (원문)

v3 반영을 끝냈습니다. 커밋은 하지 않았고, GPU 사용·실행 중 스크립트 수정·`/home/HTJ/t2` 수정도 없습니다. `{{NOW}}` 두 곳은 그대로 두었습니다. 허용 범위 밖 작업이 하나 있었습니다: 제가 띄운 자체 검사를 kill 하려 한 명령과, 이어서 wf JSON 을 읽으려 한 명령이 권한 분류기에 거부됐습니다. 검사는 끝까지 돌았고, 그 JSON 조회는 다시 시도하지 않았습니다.

#### 검사 결과
- **`bash -n code/run_scale2.sh`**: 통과.
- **`check_frontier_scale.py`**: ALL PASS. 새로 넣은 (6) 도 통과했습니다. HISNR 부하 아래 nice 19 로 돌아 벽시계 21분 56초가 걸렸습니다(user CPU 42.1 s). 출력은 scratchpad `cfs_v3.out` 에 있습니다.
  - (6) 결과: `b*(K/2) 899 dF=+35`, R⁺_C2 = 0.346 [90% 0.106, 0.492], R1⁺−R2⁺ = +0.477 [95% +0.301, +0.787].
  - 비교용 외삽 없는 값: R1−R2 = +0.314 [95% +0.241, +0.393]. 즉 CI 폭이 약 3.2 배입니다.
- **CLI 플래그 대조**: `run_scale2.sh` 가 쓰는 모든 플래그를 grep 으로 대조했고, 빠진 것은 없습니다. 셸 변수로 넘기는 `--n --chunk --worker-gb --stagec-ckpt --bstar --kron-K` 도 확인했습니다. 대상 도구는 runner run/analysis, eval_accept, run_manifest, guard_report, recovery_ci, frontier_ci, pair_baselines, ald 입니다. frontier_ci 가 `--extrap - - --ck - -` 를 받아들이는 것도 확인했습니다.
- **새 셸 함수 단위 확인**(가짜 입력): `qkv`, `trend` 게이트, `acc` 의 태그 파싱, `kchk`, `bsl`, `dp` 모두 정상입니다. 앵커를 건 `dp()` 는 1단계 표 6개와 단일 셀 기록 표에서 기존 정규식과 같은 값을 냈고, 여러 셀 표에서는 ''(가드)를 돌려줍니다.
- **common.py**: `import common, arms` 통과. C9 = (-12,-9,-6,-3,0,3,6), `DEFAULT_CELLS` = C1–C6 로 변화 없음.

#### 항목별 변경

**A. must 전부 반영**
- **stats2-1**: §1 다중성 행을 교체했습니다((T-iv) 는 p:=1, 동률이면 D2 먼저, (T-iv) 인 쪽은 항상 둘째). §2.1 (T0-Holm) 행은 "첫째가 (T0)" 로 고쳤습니다.
- **stats2-2 + integ M1 (병합)**:
  - 판정점이 정확히 3개가 아니면 `DP[$T]=""` 로 비우고 가드를 기록합니다.
  - 추세 블록은 `trend` 함수로 줄마다 게이트를 겁니다. else 분기는 없앴습니다.
- **stats2-3**: 실행 (a)/(b)/(c) 셋 모두가 1차 라벨과 같을 때만 "[K 상한 강건]" 입니다.
  - 출력 파일은 `scale2_primary_{D2,U28}_L{95,90}{,_qkC9,_qkC2}.txt` 로 고정했습니다.
  - 스크립트에 `qkv` 를 추가했고, `--rstar` 는 (a) 에만 붙습니다.
  - 문서 §1 Q-K 행에 명령 원문을, §2.1 (2) 에 새 규칙을 적었습니다.
- **fair2-1**: `check_frontier_scale.py` 에 (6) 을 넣고 실행했습니다. ⑤ 문구도 정정했습니다. 이 과정에서 v2 가 주장한 "r ≥ 1 분기" 검사도 스크립트에 없다는 것을 발견해 문서에 공개했습니다.
- **fair2-2**:
  - `acc $T`(A 단독 + 격자) = 추세 게이트, `acc ${T}pa`(A·PIL·ALD) = pair 게이트로 나눴습니다.
  - pair 는 `ok $T ${T}pa` 일 때만 돕니다. 문서 (b)·실행 스크립트 행·§5 를 맞췄습니다.
- **integ M2**: 문서 (b) 에 chk 가 별도 호출이라고 적었고, v1→v2 요약 줄도 정정했습니다.

**B. 권고 반영**
- **stats**:
  - §0.1 R\* CI 에 수준을 값마다 적었습니다(UMi28 은 95%, 90% 는 미계산이라고 명시).
  - 보고 전용 `scale2_report_C6_dFK.txt` 를 추가했습니다(머리말 포함, 게이트 = U28 C6 A·K2 들·BRNR16).
  - p 해상도와 "동률 규칙이 실제 순서를 정할 가능성" 을 적었습니다.
  - `dp()` 를 표 B 줄에 앵커하고 블록이 정확히 하나일 때만 받습니다.
  - 등록 CI = `scale2_primary_<d>_L90.txt` 의 R2 줄(D2 C6 은 `scale2_step_D2_S2`)로 고정했습니다.
- **fair**:
  - 방향 문장(§1 GMM b\* 행, §2.1), R⁺_C2 와 CI 폭 증폭(§0.1 표 아래)을 넣었습니다.
  - bridge 게이트는 14 arm 전부 비트 동일로 고정했습니다.
  - §5 재사용 대조 문구: 세 raw 에 `run|git` 키가 없고 B16e4k 는 `stagec_ckpt_id` 도 없다는 것을 확인해 적었습니다.
  - (c) epoch 는 수동 대조로 적었습니다(형식 `epoch= best_epoch=` 확인).
  - §4.1 에 링크 생성 행을 넣었습니다(`gmm_fits_D2_NR16B16e4` 가 worktree 에 없음을 확인).
  - 강제 Q-K 한정어 줄을 fci 출력 파일 머리말에 쓰게 했고, 이때 (b)(c) 는 돌리지 않습니다.
  - C9 격자 변경의 무해성: grep 으로 확인했습니다. fit_gpu, gmm_em_gpu, train_nr16, score, arms, d2, em_batched_check_nr, gpu_sched, edge_rule, gpu_filler, run_fitq 는 CELLS 를 읽지 않습니다. runner 는 run/smoke/sigma 기본값에서만 읽습니다.
  - ALD regen 문장: 7 워커 × ≈7.4 GB ≈ 52 GB, 파일럿 내용은 `R5-genie` 의 transmit/_sites 만 쓴다는 것을 코드로 확인했습니다.
- **integ**:
  - EM 일괄 검사 3개가 gpuq 우선순위 60 에 있음을 gpuq.txt 에서 확인해 §1·§4 에 적었습니다.
  - `FIT_KRON_BATCHED=1` 삽입 규칙을 원문으로 적었습니다. `gpu_sched.sh` 가 `CUDA_VISIBLE_DEVICES=<g> <cmd>` 로 띄우는 것과, `fit_gpu.py:75` 가 후보별로 기록하는 것을 확인했습니다.
  - 같은 물리 파일 문구: readlink 로 확인했습니다(B16e4 → n16e4, B16e4k 의 12개 Nr8 파일 → `../gmm_fits_D2_n16e4`).
  - 비용 행에 상한을 넣었습니다(last 의 b\* + PIL/ALD 포함 → 합계 약 60–200 h, 작성자 산술).
  - σ 재측정 명령은 `nice -n 19 taskset -c 191` 을 유지해 원문으로 적었습니다.

**C.** `LASTARMS` 에 `M-ours-bstar` 를 넣어 `recovery_ci raw_<T>last` 가 짝 CI 를 냅니다. `bsl` 이 b\* 의 KEYS_RAW 를 A 태그와 대조해 보고 전용 줄을 `recovery_<T>last.txt` 에 적습니다. 게이트는 아니고, 실패하면 fail 로만 셉니다. 문서 평가 가중치·태그·보고 전용 행도 맞췄습니다.

**D.** `results/gmm_fits_D2_B1e4` 의 옛 대상(`gmm_fits_D2`)과 새 대상은 24개 파일 sha256 이 모두 같았습니다. 그래서 `git checkout` 으로 추적 링크를 복원했습니다. `d2_gbprime_UMi28.csv` 는 동결 커밋에 넣는 것으로 문서에 적었습니다(결정 14).

**E.** `common.py` 는 C9 튜플 한 줄만 `os.replace` 로 원자적으로 바꿨습니다. 주석은 건드리지 않았습니다. "① 동결 커밋에서 바꾼다" 문구도 맞게 고쳤습니다.

**F.** gpuq 에서 확인했습니다(`trainU28NR16`/`trainU28NR32`, 우선순위 90). §1 V1 학습 행, §4.1, §0.5 에 반영했고 관측 시각은 09-30 12:58 CDT(date)입니다.

**G.** `conf/results/review_next/prereg_reviews_scale16e4/` 에 두 파일을 만들었습니다.
- `review_round1.md`: 원본과 cmp 동일.
- `review_round2.md`: 세 렌즈의 must/should/v1 미해결/verified 원문(7/30/41 항목).

**문서 공통**: v3 로 올리고, 주 세션 결정을 **11–15** 로 번호를 매겨 공개했습니다(A–E 에 해당). 머리에 v2→v3 요약을 넣고 v1→v2 요약은 남겼습니다. 표 열 개수가 맞는지도 확인했습니다.

#### 다르게 반영했거나 반영하지 않은 것
- **수용 (k)**: "run_manifest 의 meta 값 집합" 으로는 할 수 없었습니다. `run_manifest.py` 는 JSON 에 `jobs`/`worker_gb` 를 싣지 않습니다. 대신 `acc` 가 C9 태그마다 청크 전부를 읽는 `kchk` 를 돌리고 그 결과를 같은 수용 키에 합칩니다. 문서에도 공개했습니다.
- **fair S14**(D2 C6 spec-1 CI 예시): 결정 B 목록에 없었고, 그 값은 등록 대조에 쓰이지 않아 넣지 않았습니다.
- **`--ck inf` 분기 검사**: 추가하지 않았습니다. 또 한 번 약 20분 걸리는 재실행이 필요해서입니다. 문서에는 "검사 스크립트 밖" 이라고만 적었습니다.
- **링크 생성**: 결정대로 §4.1 행에만 적고 실제 링크는 만들지 않았습니다(§5 전 작업).

#### 파일
- /home/HTJ/t2_wtS/conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md
- /home/HTJ/t2_wtS/conf/code/run_scale2.sh
- /home/HTJ/t2_wtS/conf/code/check_frontier_scale.py
- /home/HTJ/t2_wtS/conf/code/common.py
- /home/HTJ/t2_wtS/conf/results/review_next/prereg_reviews_scale16e4/review_round1.md
- /home/HTJ/t2_wtS/conf/results/review_next/prereg_reviews_scale16e4/review_round2.md
- v2 백업: /tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/SCALE16e4_v2_backup.md

### 렌즈 stats-fair

#### 반드시
- **[r3-1]** §1 메모리 가드 행 (NEXT_EXPERIMENTS_SCALE16e4.md:148 "G 를 넘으면 멈추고 G 를 올려 `--resume`") + 수용 검사 (k) (:157 "worker_gb 값 집합 = {`WGB`}") / code/run_scale2.sh 줄 33·89·105·149·218
  - 문제: 등록된 G 인상 경로가 스크립트·수용과 모순돼 실행 불가이거나, 강행하면 추세 게이트가 (T-iv) 를 만든다. 스크립트는 G 를 `scale2_s5.txt` 의 WGB 줄에서만 읽고(줄 33·218) 전제가 S5 추적·청결 + HEAD = S5 커밋(줄 85–86)을 요구하므로 G 를 올리려면 S5 를 고쳐 커밋해야 한다 → DECISIONS 7(§5 커밋 뒤 커밋 금지) 위반이고, `runner._git_head` 가 HEAD 를 청크마다 `run|git` 에 쓰므로(runner.py:457–463) 재개 뒤 청크는 다른 커밋 → 수용 (f) '깨끗한 커밋 하나' 실패. 그래도 진행하면 `kchk` 가 `len(wg) != 1 … != g` 로 (k) FAIL(줄 149) → A 단독 수용 = 추세 게이트 실패 → 그 셀의 1차·2차가 (T-iv) 로 건너뛰어진다. 문서 자신도 148 행에서 '값 집합' 이 둘 이상일 수 있다고 쓰면서 157 행 (k) 는 = {WGB} 를 요구한다. G 는 BLER 과 무관한 워커 수 상한이라 인상은 무해해야 하는데, 지금 규칙은 결과와 무관한 자원 문제로 라벨을 바꾸고 전사자가 (k) 를 무시할지 고르게 만든다.
  - 수정: run_scale2.sh 줄 33 을 두 줄로:
```
WGB=$(awk '$1=="WGB"{print $2}' $S5 2>/dev/null)   # <<< §5 value of runner --worker-gb G (C9 cells); acceptance (k): every C9 chunk's meta|worker_gb >= WGB
WGBR=${SCALE2_WGB:-$WGB}   # a raise after the first K=4096 chunk's RSS (§1 memory guard): SCALE2_WGB=<G'> bash code/run_scale2.sh --resume; S5 and HEAD stay (DECISIONS 7)
```
줄 89 를:
```
  awk -v g="$WGB" -v r="$WGBR" 'BEGIN {exit !(g + 0 > 0 && r + 0 >= g + 0)}' || die "WGB '$WGB' (runner --worker-gb for C9) not set in $S5, or SCALE2_WGB '$WGBR' < WGB (a raise only)"
```
줄 105 의 `WGB ${WGB:-unset}` → `WGB ${WGB:-unset} (run ${WGBR:-unset})`; 줄 218 의 `M="--worker-gb $WGB"` → `M="--worker-gb $WGBR"`; 줄 149 (kchk) 의 `if len(wg) != 1 or None in wg or float(next(iter(wg))) != g or None in jb:` → `if None in wg or None in jb or any(float(x) < g for x in wg):` (줄 148 의 값 집합 출력은 그대로). 문서 148 행의 "첫 실제 K = 4096 청크에서 워커 RSS(`ps`)를 보고 G 를 넘으면 멈추고 G 를 올려 `--resume`(BLER 무관; `meta\|worker_gb` 가 청크마다 남는다; analysis 는 첫 청크 값, `run_manifest` 는 전체 집합을 보인다)." → "첫 실제 K = 4096 청크에서 워커 RSS(`ps`)를 보고 G 를 넘으면 멈추고 **`SCALE2_WGB=<G′> bash code/run_scale2.sh --resume`** (G′ ≥ G; `scale2_s5.txt` 와 HEAD 는 바꾸지 않는다 — 결정 7·수용 (f) 유지; BLER 무관; `meta\|worker_gb` 가 청크마다 남으므로 값 집합 {G, G′} 과 올린 시각·RSS 를 §4.1 에 적는다; analysis 는 첫 청크 값, `run_manifest`·`ACCEPT (k)` 줄은 전체 집합을 보인다)." 문서 157 행 (k) 의 "worker_gb 값 집합 = {`WGB`}" → "worker_gb 의 모든 값 ≥ `WGB`(§5 값; 값 집합은 `ACCEPT (k)` 줄에 기록 — 올린 경우 {G, G′})". `bash -n` 재확인.
- **[r3-2]** code/run_scale2.sh 전제 줄 69–70 (`CELL $T ckpt stem / best sha not filled` → die) + 줄 112·217 / §1 실행 스크립트 행 (:149 `scale2_s5.txt` 형식) · 학습 실패 행 (:142)
  - 문제: §1 학습 실패 행은 'fb3 까지 실패하면 학습 실패로 적고 그 셀의 BLER 은 없으며 (T-iv)' 이고 다중성 행은 '한쪽이 (T-iv) 면 다른 쪽은 첫째로 95 % 판정' 인데, 스크립트는 새 셀 3 개의 CELL 줄이 모두 `d2sx_…` 스템과 16 hex sha 로 채워져야만 시작한다(줄 69–70·72–73, 세 모드 공통). 한 셀이 학습 실패면 S5 를 채울 수 없어 `die` → 다른 데이터셋의 1차·2차와 나머지 셀의 pair 까지 등록 스크립트로 낼 수 없고, 전사자가 `frontier_ci`·`pair_baselines` 를 손으로 돌리게 된다(명령·spec 순서·게이트가 등록 밖으로 나감 — 2차 M1 이 막으려던 경로). 등록이 정의한 결과 갈래를 스크립트가 낼 수 없다.
  - 수정: run_scale2.sh 줄 25 뒤에 주석 한 줄:
```
#     CELL <tag> -   = training failed through fb3 (§1 학습 실패 -> (T-iv)): that cell is skipped entirely (no runs, no acceptance); the other cells / dataset run
```
줄 69 앞에:
```
  [ "$1" = - ] && { log "$T: CELL stem '-' = training failed (§1 학습 실패 -> (T-iv)); the cell is skipped"; continue; }
```
줄 112 를:
```
    read ST BSHA REST <<< "$(s5 $T)"; [ "$ST" = - ] && continue; E=PIL$SUF; CKB=ckpt/${ST}_best.pt      # the SAME --ckpt string for tune and estimate (ald.py asserts); '-' = training failed, skipped
```
줄 217 (`read ST BSHA LSHA … ; read NR NS S0 <<< "$(cellinfo $CELL)"`) 바로 뒤에:
```
  [ "$ST" = - ] && { st 1 "cell $T SKIPPED: training failed through fb3 (§1 학습 실패 -> (T-iv); no runs, no acceptance)"; DP[$T]=""; continue; }
```
(ACC[$T] 미설정 → `trend`·`ok` 가 그 셀을 쓰는 줄과 pair 만 건너뛴다.) 문서 149 행의 `CELL <tag> <ckpt_stem> … <c_K 또는 ->` 뒤에 "; **학습 실패(fb3 까지) 셀은 `CELL <tag> -`** 로 적고 스크립트가 그 셀을 통째로 건너뛴다(실행·수용 없음 → 그 셀을 쓰는 추세 줄·pair 만 fail, 다른 셀·데이터셋은 돈다; 다중성 행의 (T-iv) p := 1)" 를 넣고, 142 행 끝 "라벨은 (T-iv)가 된다" 뒤에 "(§5 `CELL <tag> -`, 실행 스크립트 행)" 을 덧붙인다. `bash -n` 재확인.

#### 2차 항목 미해결
- (없음)

#### 권고
- §1 실행 스크립트 행(:149)·Q-K 행(:154) "Q-K 가 강제 한정어면 (b)(c) 는 돌리지 않는다" 는 K/2 수용 실패(`qk` 가 '' )일 때만 참이다. c_K = inf (r ≥ 1) 이면 `Q_<d>` 가 비어 있지 않아 (a)(b)(c) 가 모두 돌고 `frontier_ci` 가 "(r >= 1) [K 상한 민감: 외삽 불가]"·"R1+ - R2+: n/a" 를 찍는다(무해, (1) 이 우선). 두 곳을 "K/2 수용 실패로 강제면 (b)(c) 를 돌리지 않고, r ≥ 1 이면 세 실행이 돌지만 §2.1 (1) 이 우선한다" 로.
- §1 다중성 행에 p 의 출처를 한 절로 고정: "p = 실행 (a) 파일 `scale2_primary_<d>_L95.txt`(= `_L90.txt`)의 `R1 − R2 … (--level)` 줄의 p (ΔR 의 p; `_qkC9`·`_qkC2` 와 두 수준에서 같다 — 재표본은 `--level`·`--extrap`·`--rstar` 에 독립, ⑤ (3)(6) 의 bo 동일)" — 지금은 1차 통계량 행에서만 유추된다.

#### 확인
- stats2-1: §1 다중성 행(:151)이 제안 원문과 일치((T-iv) p := 1, 동률 → D2 첫째, 한쪽 (T-iv) 면 항상 둘째, m = 2 고정, p 해상도 1/2000 공개); §2.1 (T0-Holm) 행(:177) '둘째 데이터셋, 첫째가 (T0)'. 순서 규칙은 라벨을 바꿀 수 없음도 확인(두 p 가 같으면 어느 순서든 같은 라벨).
- stats2-2 · integ M1: run_scale2.sh 줄 226–228 이 판정점을 정확히 3 개 아니면 비우고 가드를 기록; 줄 265–268 `trend`(coreutils `tr` 과 다른 이름)가 줄마다 DP == 3 을 검사한 뒤 `fci` 의 수용 게이트로 넘김; 줄 283–294·300 의 추세 8 줄 + 보고 전용 1 줄이 모두 `trend` 경유, else 분기 없음; `bash -n` 통과(직접 실행). 문서 :149 '추세는 줄마다 게이트 … 정확히 3 개', :152 가드 행 반영.
- stats2-3: §2.1 Q-K (2)(:182) 세 실행·'셋 모두' 규칙·방향 문장; §1 Q-K 행(:154) 명령 원문과 출력 파일 `scale2_primary_{D2,U28}_L{95,90}{,_qkC9,_qkC2}.txt`; 스크립트 `qkv`(줄 272–273) 토큰 재배열이 (b) `E1 - C1 -`·(c) `- E2 - C2` 로 맞고, 줄 285–290 이 `--rstar` 없이 `--level $LV` 로 돌리며 (a) 에만 `--rstar 0.05`; `frontier_ci` argparse 가 `--extrap - - --ck - -` 를 받고 k2 = [None, None] 이면 외삽 없음과 같은 출력(코드 확인).
- fair2-1: check_frontier_scale.py 65–76 행에 (6) 교차 raw Q-K 검사(제안 원문과 같은 assert: bo 동일, R1⁺ = R1, ΣF⁺ 부동소수 식 |차| < 1e-12, 'b*(K/2) 899  dF = +35', 'SigmaF+ <= SigmaF_g in 0.0%', 나머지 줄 바이트 동일); scratchpad `cfs_v3.out` = ALL PASS, R⁺ 0.346 [90% 0.106, 0.492], R1⁺−R2⁺ +0.477 [95% +0.301, +0.787], user 42.1 s / 벽시계 21m56s; 문서 ⑤(:159) 가 (6) 과 시간을 적고 v2 의 '서로 다른 raw 의 genie 정렬 PASS'·'r ≥ 1 분기' 가 검사에 없었음을 공개; §0.1(:70) 사전 공개.
- fair2-2: run_scale2.sh 줄 244–247 A 단독(`--nr --fits-dir --grid`, 키 `$T`) + `${T}pa`(`--ref-raw`, A·PIL·ALD 세 `--tag`); 추세 `fci` 게이트 키는 `$T`(줄 283–294), pair 는 `ok $T ${T}pa`(줄 304); eval_accept.py 는 `--nr`/`--fits-dir` 를 격자 검사에만, `common_meta` (bstar, kron_K, em_sec) 와 `--ref-raw` 재생을 호출 안 태그끼리 검사하므로(:94,128) 분리가 유효. 문서 :149 게이트 문장, :157 (b) 원문, :305 §5 수용 파일 목록에 `<T>pa_accept.txt`(§4.1 에는 수용 파일 목록이 원래 없어 §5 에 둔 것으로 충분).
- integ M2(참고 확인): :157 chk 별도 호출 + `eval_accept.py:51,67`(실제 51 `--n`, 67 `plan`), `:94,128`(실제 94, 128) 줄 번호 정확; :26 v1→v2 요약 정정.
- `dp()` 정규식(줄 167)을 기록 표 B16e4k·NR16B16e4·U28B16e4·D3B16e4 와 1단계 S1D2C9·S1U28C6 에 직접 적용: 각 1 블록, '+0' 포함 파싱이 −3 0 3 / 3 6 9 / −9 −6 −3 / 0 3 6 으로 정확(analysis.py:440–442 출력 형식과 일치).
- p 가 수준·실행에 걸쳐 같음: `cmd_recovery` 의 R 재표본(bo)은 `--level` 을 읽지 않고, Q-K 는 base 키로 `rs.take` 재사용, Q-OP 는 자체 `Resampler` — 코드와 ⑤ (3)(6) 으로 확인. `pct`/`ci_p` 는 정의된 복제만 쓰므로 소수의 정의 불가 복제가 CI 를 NaN 으로 만들지 않는다(가드 5 % 규칙과 정합).
- (k) 검사 `kchk` 가 A 단독·pa·chk·K2·last 의 C9 `--tag` 마다 청크 전부의 두 키를 읽고(줄 155–160), 모든 C9 실행이 `$B` 로 `--worker-gb` 를 받으며(줄 218–219, 233–234) runner 가 `meta|jobs`·`meta|worker_gb` 를 청크마다 기록(runner.py diff `RUN_META`).
- 결정 13: `LASTARMS` 에 `M-ours-bstar`(줄 52), `recovery_ci raw_<T>last` 짝 CI(줄 240–241), `bsl` 이 `C.KEYS_RAW` 7 키(common.py:108)를 기저 이름으로 A raw 와 대조해 게이트 아닌 보고 줄을 씀(줄 171–186, 242).
- 검토 원문: `prereg_reviews_scale16e4/review_round1.md` 가 scratchpad `stage2_reviews.md` 와 cmp 동일, `review_round2.md` 에 세 렌즈 반드시 7 건 원문 존재. `common.py` diff 는 C9 튜플 한 줄뿐; `results/gmm_fits_D2_B1e4` 링크는 porcelain 에 없음(복원됨); `d2_gbprime_UMi28.csv` +1 행.

### 렌즈 integ

#### 반드시
- **[integ3-1]** §1 메모리 가드 행 (NEXT_EXPERIMENTS_SCALE16e4.md:148 끝 문장 "첫 실제 K = 4096 청크에서 … G 를 올려 `--resume`") + §4.2 #4 (:268) + §4.1 CPU 행 (:258); run_scale2.sh:33,85-86 (WGB 는 추적·청결한 scale2_s5.txt 에서만), :138-153 `kchk`, :155-160 `acc`
  - 문제: 문서가 정한 "RSS > G 이면 G 를 올려 --resume (BLER 무관)" 경로는 스크립트로 실행할 수 없고, 실행하면 라벨이 바뀐다. G(`WGB`)는 `scale2_s5.txt` 에서만 읽히고 그 파일은 추적·청결 + HEAD == 그 파일을 마지막으로 건드린 커밋이어야 하므로(:85-86) G 변경 = 새 scale 커밋 = 결정 7(§5 커밋부터 마지막 raw 까지 커밋 금지) 위반이고, 이어지는 청크의 `run|git` 이 달라져 (f) "raw 마다 깨끗한 커밋 하나 = §5 커밋" 이 깨진다(`run_manifest.one()` 은 값이 둘이면 목록을 돌려줄 뿐 실패하지 않는다). 더 중요하게, 수용 (k) 의 구현 `kchk` 는 `len(worker_gb 집합) != 1` 이면 FAILED 이고 `acc` 가 이를 `ACC[<T>]`(A 단독 = 추세 게이트)에 합치므로, G 를 올려 재개한 C9 셀은 구조상 (k) 실패 → 1차·2차 추세 줄 SKIPPED → (T-iv). 운영상 선택(G 상향 여부)이 그 데이터셋의 라벨을 정하게 된다.
  - 수정: :148 의 문장 "첫 실제 K = 4096 청크에서 워커 RSS(`ps`)를 보고 G 를 넘으면 멈추고 G 를 올려 `--resume`(BLER 무관; `meta\|worker_gb` 가 청크마다 남는다; analysis 는 첫 청크 값, `run_manifest` 는 전체 집합을 보인다)." 을 다음으로 교체: "첫 실제 K = 4096 청크의 워커 RSS(`ps`)는 `logs/run_scale2.log` 에 적고 §6 전사 때 §4.1 로 옮긴다. **G 는 §5 커밋 뒤 바꾸지 않는다** — `WGB` 는 추적·청결한 `scale2_s5.txt` 에서만 읽으므로(`run_scale2.sh:33,85-86`) G 변경은 새 scale 커밋(결정 7 위반)이고, 그 raw 의 `run\|git` 이 둘이 되며(수용 (f) 위반), 수용 (k) 의 `worker_gb` 값 집합 = {WGB} 가 깨져(`kchk`: 집합 크기 ≠ 1 → FAILED) 그 셀의 추세 게이트 `ACC[<T>]` 가 실패 → (T-iv) 가 된다. RSS 가 G 를 넘어도 jobs = floor(0.8·M/G) 라 RSS ≤ 1.25·G 까지는 총 사용량 ≤ M 이다. RSS > 1.25·G 또는 OOM 이면 멈추고 사용자에게 알린다; 재개는 사용자 결정이며, 새 G 로 하려면 그 raw 를 처음부터(`raw_<T>` 전체 삭제, 새 §5 커밋 + `DECISIONS.md` 줄) 돌린다 — 청크 사이 G·커밋 혼용은 (k)(f) 로 수용 실패다." :268 의 결정 규칙 열을 다음으로 교체: "첫 청크 시간·RSS 는 `logs/run_D2_<T>.log`(`done … (N s)`)·`logs/run_scale2.log` 에서 읽어 §6 전사 때 §4.1 에 옮긴다. RSS > 1.25·G 또는 OOM 이면 멈추고 사용자에게 알린다(G 변경 = 새 §5 커밋 + 그 raw 처음부터; §1 메모리 가드 행). **비용이 늘어도 n·arm·K 는 줄이지 않는다**; 순서만 §1 실행 순서대로". :258 의 상태 열은 must integ3-2 의 문구로.
- **[integ3-2]** §4.1 CPU 행 (:258 "첫 청크 시간과 … 여기 적는다"), §1 실행 순서 행 (:160 "첫 청크 시간을 §4.1 에 적는다"), §1 비용 행 (:161 "확정은 첫 청크 시간"), §1 실행 스크립트 행 전제 목록 (:149) vs run_scale2.sh:60
  - 문제: 문서는 CPU 실행 중에 첫 청크 시간·RSS 를 §4.1 에 적으라고 하지만 `run_scale2.sh:60` 은 모든 호출(`--resume` 포함)에서 이 문서와 `DECISIONS.md` 의 추적·청결을 요구하고 결정 7 은 그 구간의 커밋을 금지한다 → 문서대로 §4.1 을 편집한 뒤 재부팅·kill 뒤의 정당한 `--resume` 이 "not tracked+clean (freeze first)" 로 ABORT 한다(스크립트 실패). 같은 전제가 `tune` 에도 걸리므로 §5 채움을 tune 전에 시작해도 ABORT 한다.
  - 수정: :258 상태 열을 "대기. **실행 중(`SCALE2_DONE` 전)에는 이 문서와 `DECISIONS.md` 를 편집하지 않는다** — `run_scale2.sh:60` 이 `--resume` 에서도 두 파일의 추적·청결을 요구하고 결정 7 이 커밋을 금지한다. 첫 청크 시간(`logs/run_D2_<T>.log` 의 `done … (N s)`)과 첫 K = 4096 청크의 워커 RSS 는 §6 전사 때 여기 옮긴다" 로 교체. :160 의 "첫 청크 시간을 §4.1 에 적는다." → "첫 청크 시간은 로그에서 §6 전사 때 §4.1 로 옮긴다(실행 중 문서 편집 금지). ALD tune 은 §5 편집을 시작하기 전에 돌린다(tune 도 문서 청결이 전제)." :161 의 "확정은 첫 청크 시간" → "확정은 첫 청크 시간(§6 전사 때)". :149 전제 목록의 "이 문서·DECISIONS 추적·청결" 뒤에 "(`--resume`·`tune`·`estimate` 도 같은 전제 — 실행 중 두 파일을 편집하지 않는다)" 를 덧붙인다.
- **[integ3-3]** run_scale2.sh:135 `run()` — `> logs/run_D2_$T.log 2>&1` ; §1 실행 스크립트 행 (:149)
  - 문제: `--resume`(또는 같은 태그의 두 번째 호출)마다 runner 표준출력 로그가 `>` 로 잘려 이전 호출의 기록이 사라진다. 그 로그가 유일한 출처인 항목이 있다: 메모리 가드 줄 `[run] --worker-gb G: memory guard allows M workers -> jobs = J`(§1 메모리 가드 행 "실행 로그에 … 찍고", §5 "jobs TBD(실행 로그)")와 청크별 `done … (N s)` 시간(§4.1 첫 청크 시간, 비용 행 "확정은 첫 청크 시간"). 재개가 예정된 설계(문서 :149, 스크립트 머리말)에서 §5·§4.1 기록이 훼손된다(misrecord). 선례 run_pilot16e4.sh:32 도 `>` 였지만 재개 모드가 없었다.
  - 수정: run_scale2.sh:135 를 다음 두 줄로 교체:
  echo "# run_scale2 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') resume=$RESUME: runner.py run $* --tag $T" >> logs/run_D2_$T.log
  $P code/runner.py run --testbed D2 --ntrain 160000 "$@" --tag $T >> logs/run_D2_$T.log 2>&1 < /dev/null; rc=$?
그리고 `bash -n code/run_scale2.sh` 재확인. :149 의 "로그 `logs/run_scale2.log` (CDT)" 뒤에 "; runner 로그 `logs/run_D2_<T>.log` 는 호출마다 머리말 줄을 붙여 이어 쓴다(`--resume` 뒤에도 첫 호출의 jobs 줄·청크 시간이 남는다)" 를 덧붙인다.

#### 2차 항목 미해결
- (없음)

#### 권고
- 동결 커밋은 명시 목록으로 `git add` 한다(`-A`/`git add conf` 금지): `git status --porcelain conf | grep -v logs` 에 `conf/ckpt`, `conf/raw_{NR16B16e4,U28B16e4}`, `results/gmm_fits_D2_*`, `results/sigma_grid_D2_NR16.{npz,txt}` 의 절대경로 링크와 새 fits 디렉터리 등 45 개 미추적 항목이 있고, `conf/ckpt` 링크가 커밋돼 main 으로 병합되면 main 의 실제 미추적 `conf/ckpt/` 디렉터리와 충돌한다. §1 실행 위치·커밋 행에 add 목록(문서, DECISIONS, code 8 파일, csv, TMXa 2, σ U28NR16g 2, prereg_reviews 3)을 원문으로 적을 것.
- §1 태그 행의 last `--stagec-ckpt ckpt/<stem>.pt` 는 스크립트에서 `/home/HTJ/t2/conf/ckpt/<stem>.pt`(절대경로; A·PIL·ALD·K2·chk 도 같음, ALD16e4 선례 run_ald16e4.sh:49 와 동일)다. 같은 파일이고 ALD 파일 대조는 sha(runner.py:313)라 무해하지만 `meta|stagec_ckpt` 에는 절대경로가 남으므로 문서 문구를 스크립트에 맞출 것.
- `scale2_s5.txt` 의 `CELL` 줄에는 뒤 `#` 주석을 붙일 수 없다(`s5()` 가 필드 수로 검사해 "needs 11 filled fields" 로 ABORT). 머리말의 "'#' comments" 를 "줄 머리 '#' 만" 으로 고치거나 `s5()` 에 `sub(/#.*/, "")` 를 넣을 것.
- 수용 (f) "raw 마다 깨끗한 커밋 하나 = §5 커밋" 을 스크립트가 직접 검사하지 않는다(`eval_accept` 는 `run|git` 을 보지 않고, `run_manifest.one()` 은 값이 둘이면 목록을 돌려줄 뿐 rc 0). 각 `run` 호출 전 HEAD 재확인(:133)이 사실상의 보장이므로, (f) 는 `run_manifest_<T>.json` 의 `run|git` 집합 = {§5 커밋, dirty 없음} 을 §6 에서 수동 대조한다고 적거나 `man()` 뒤에 그 집합을 검사하는 3 줄을 넣을 것.

#### 확인
- integ M1 해결(문서+스크립트): run_scale2.sh:226-228 이 판정점이 정확히 3 개가 아니면 `DP[$T]=""` 로 비우고 가드를 기록, :231-234 로 K2·last 만 건너뜀; :265-268 `trend`(coreutils `tr` 과 다른 이름)가 줄마다 그 줄의 새 셀 판정점 3 개를 요구하고 SKIP 을 fail 로 셈; :283-294 의 1차 2 수준·(b)(c)·단계 3 줄·보고 전용 C6 dFK 가 모두 `trend` 경유, else 분기 없음. 문서 :149 "추세는 줄마다 게이트 … 정확히 3 개 … 다른 데이터셋·단계는 돈다", "판정점이 3 개가 아닌 셀은 K2·last·그 셀을 쓰는 추세 줄만" 과 일치.
- integ M2 해결: 문서 :157 (b) 가 A 단독 호출·A·PIL·ALD 공동 호출·chk 별도 호출(`--n` 과 청크 계획은 호출 단위, eval_accept.py:51,67)을 원문으로 적고 스크립트 :244-252 와 일치(A 단독 1, pa 1, chk·K2·last 각 1); v1→v2 요약 :26 정정됨.
- 2차 integ v1 미해결 3 건도 해소: integ-4 → logs/gpuq.txt 에 `60 GPU bchk_S2_32/bchk_U28_16/bchk_U28_32` 3 줄 존재(학습 90 다음, 4096 50 앞), 문서 EM 경로 행·§4.1·§4.2 #2 에 반영; integ-5 → M2; integ-1 (k) → `kchk`(:138-153) 가 C9 `--tag` 가 있는 `acc` 마다 청크 전부의 `meta|worker_gb`(= WGB)·`meta|jobs` 를 검사해 같은 수용 키에 합침(문서 :157 (k), :15 "달리 반영" 공개).
- `bash -n code/run_scale2.sh` 통과. 스크립트가 쓰는 플래그 전부 존재: runner `--testbed --ntrain --prior --cell --stagec-ckpt --n --chunk --snr --arm --pilot-arms --ald-file --worker-gb --tag`(runner.py:1187-1252, `--worker-gb` :1248 신규); eval_accept `--tag --ntrain --kron-K --ll-val --n --ref-raw --fits-dir --grid --nr --points --ref-arms --prior --bstar`(:45-62); ald `regen|tune|estimate --tag --prior --cell --fits-tag --set --ckpt`(:284-288); recovery_ci `--raw --cell --snrs`; guard_report `--raw --testbed`; run_manifest `--tag`; frontier_ci `--level --extrap --ck --rstar`(:328-331, '-' 위치 일치·c_K ≥ 1·`--recovery` 필요 검사). arm 이름 `V1-pilot bstar-pilot ALD-pilot ALDv-pilot` 는 runner.py:434-444/arms.py:296-303 에 있음.
- check_frontier_scale.py (6) 이 fair2-1 의 fix 원문과 동일하게 들어갔고 cfs_v3.out = ALL PASS(`b*(K/2) 899  dF = +35 … R+ = 0.346 [90% 0.106, 0.492]`, R1+ − R2+ +0.477 [95% +0.301, +0.787], plain +0.314 [+0.241, +0.393]; user 42.1 s, 벽시계 21m56s) — 문서 ⑤·§0.1 수치와 일치. `results/review_next/recovery_diff_U28B16e4.txt` 대조 (1) 포함.
- common.py 변경은 C9 튜플 한 줄뿐(`git diff`: `(-12, -9, -6, -3, 0, 3, 6)`), 스크립트 :61 의 문자열 비교와 일치. `train_nr16.py fit_gpu.py score.py gmm_em_gpu.py arms.py d2.py em_batched_check_nr.py` 는 `CELLS`/`snrs` 를 읽지 않음(grep) → 실행 중·큐 대기 중 적합·학습·검사에 무해하다는 문서 :137 근거 성립. gpuq 의 학습 2 줄은 `--sigma-tag U28NR16g / U28NR32` 로 σ 파일을 쓰며 격자 무관.
- runner.py diff: `--worker-gb` 는 jobs 상한만 바꾸고(`min(jobs, mem_jobs)`), `RUN_META` 가 `_init` initargs·직렬 경로 양쪽으로 워커에 닿아 `P["meta"].update(RUN_META)`(:493) 로 `meta|jobs`·`meta|worker_gb` 저장; 플래그 없으면 RUN_META 빈 dict → 기본 경로 불변. `:606` 가드 (8,16,32). sigma.py/testbed_mix3.py/em_batched_check_nr.py diff 는 `--snr`·`--nr`·`--prior` 옵션 추가와 출력 파일명 분리뿐이고 기본값은 원 실행과 같다.
- dp() 정규식을 실제 표에 적용: tables_D2_S1D2C9 → ['-9','-6','-3'], S1U28C6 → ['+0','+3','+6'], NR16B16e4 → ['-3','+0','+3'] (각 블록 1 개) — 기록 판정점과 일치; `int(float(...))` 로 `+0` → 0.
- 실행 커밋 규칙: 전제 :59-66(code/../Demo 청결, FREEZE 조상 + `git diff --quiet FREEZE HEAD -- code ../Demo`), :85-86(S5 추적·청결, HEAD == S5 마지막 커밋), :133(각 `run` 전 HEAD 재확인) 이 문서 :147 결정 7 원문과 일치; `runner._git_head`(:457-464) 는 `code ../Demo` 만 보므로 실행 중 생기는 results/·logs/·raw_ 는 dirty 가 아니고 `__pycache__/` 는 .gitignore. ald.py:155 는 `rev-parse --short HEAD` 만 기록(dirty 표시 없음) → estimate 의 git = §5 커밋.
- 링크·전제: worktree 에 `raw_NR16B16e4`·`raw_U28B16e4`·`results/gmm_fits_D2_U28B16e4`·`ckpt` 링크 존재, `results/gmm_fits_D2_NR16B16e4` 는 없음(문서 §4.1 링크 생성 행에 대기로 적힘, 스크립트 :94 가 ABORT 로 잡음); `results/gmm_fits_D2_B1e4 -> gmm_fits_D2` 추적 링크로 복원돼 status 에 없음; `d2_gbprime_UMi28.csv` diff 는 1e4 행 1 줄(ratio_median 0.904131 = 문서 "비 0.904"); `prereg_reviews_scale16e4/review_round1.md` 는 scratchpad stage2_reviews.md 와 cmp 동일, review_round2.md 는 must 7(#### 7 개)·verified 41 로 문서 주장과 일치. gpuq 의 `50 GPU r{0,1,2}_U28NR32B16e4_2048` 줄 형식이 문서 EM 경로 행의 `FIT_KRON_BATCHED=1` sed 치환 원문과 맞음.
- ALD 체크포인트 경로 차이(tune/estimate `ckpt/<stem>_best.pt` vs runner `/home/HTJ/t2/conf/ckpt/<stem>_best.pt`)는 무해: ald.py:253 은 tune↔estimate 의 같은 `--ckpt` 문자열·sha 를, runner.py:313 은 ald 파일의 `ckpt_sha` 를 stagec ckpt 의 sha 와 대조(경로 무관). `ckpt -> /home/HTJ/t2/conf/ckpt` 라 같은 파일.
- 문서 `{{NOW}}` 2 곳(:3, :238) 유지, `x CDT` 자리표시 0. 표 열 수·§2 라벨 규칙(stats2-1 Holm 순서, stats2-3 세 실행)·§1 Q-K 행 명령 원문·출력 파일명 `scale2_primary_{D2,U28}_L{95,90}{,_qkC9,_qkC2}.txt` 가 스크립트 :280-291(`V=L${LV#0.}`, `_$q`)과 일치; `qkv` 가 (a) 의 6 토큰에서 (b) `E1 - C1 -`/(c) `- E2 - C2` 를 정확히 만든다.

## 4차 검증

### 검증 대상을 만든 반영자 보고 (원문)

All five round-2 musts are applied in `/home/HTJ/t2_wtS/conf`. r3-1 and integ3-1 conflict on the same sentence (§1 memory guard, line 148) and on acceptance (k), so I merged them instead of applying both exactly. The details are under "Not applied as given" below. No commits, no GPU, and nothing in `/home/HTJ/t2` was modified.

**Checks**
- `bash -n code/run_scale2.sh` passes.
- `CUDA_VISIBLE_DEVICES= python code/check_frontier_scale.py` gives **ALL PASS**. It ran single-threaded under `nice 19` and took 70 s. R* is 0.610017 / 0.806386 / 0.218465, R_dp is 0.508796 / 0.822785 / 0.150427, and the cross-raw R2+ is 0.346 [0.106, 0.492].
- CLI flags: every literal flag in `run_scale2.sh` is declared in the argparse of the tool it calls. The tools checked were runner.py, ald.py, eval_accept.py, run_manifest.py, guard_report.py, recovery_ci.py, frontier_ci.py and pair_baselines.py. The first pass flagged pair_baselines `--prior`, but that was wrong: the flag is declared in a loop (`for k in (..., "--prior")`), so it is present.
- The script's `kchk` (acceptance (k)) was tested on made-up npz files. Values {8.0, 9.5} pass against G = 8.0. A value of 7.5 fails, and a missing `meta|worker_gb` key fails. A `'-'` CELL line is read correctly by both `set --` and `read`.
- All table rows in the doc still have the right number of columns. The two `{{NOW}}` placeholders are kept.

**Per item**
- **r3-1**, applied as given in the script:
  - line 33 is now `WGB` plus `WGBR=${SCALE2_WGB:-$WGB}`;
  - the precondition requires `WGBR >= WGB`, with the "a raise only" error message;
  - the start log line shows `(run $WGBR)`;
  - C9 runs pass `--worker-gb $WGBR`;
  - `kchk` fails if any value is below g, and the header comment is updated to match.
  - Doc: the (k) text now reads "모든 값 ≥ `WGB` … {G, G′}". The memory guard row uses the `SCALE2_WGB=<G′> … --resume` path, with `scale2_s5.txt` and HEAD left unchanged.
- **r3-2**, applied as given: the comment line after line 25, the `'-'` skip in the precondition loop, the GPU loop (`[ "$ST" = - ] && continue`) and the CPU loop (`st 1 … SKIPPED`, `DP[$T]=""`). The doc's execution-script row now describes `CELL <tag> -`, and the training-failure row gets "(§5 `CELL <tag> -`, 실행 스크립트 행)".
- **integ3-1**, merged with r3-1:
  - Taken from integ3-1: the RSS goes into `logs/run_scale2.log` and moves to §4.1 at the §6 transcription. The argument that RSS ≤ 1.25·G still fits in memory. Stopping and telling the user when RSS > 1.25·G or on OOM. §4.2 #4 rewritten with the log sources (`done … (N s)`).
  - Not taken: "G never changes after §5; a new G means the raw restarts from scratch with a new §5 commit". r3-1's path already keeps (f), (k) and decision 7 intact.
- **integ3-2**, applied as given: the §4.1 CPU row text; "첫 청크 시간은 로그에서 §6 전사 때…" plus "ALD tune 은 §5 편집 전" in the execution-order row; "(§6 전사 때)" at both places in the cost row that say "확정은 첫 청크 시간"; and the `--resume`·`tune`·`estimate` note in the precondition list.
- **integ3-3**, applied as given: `run()` now appends to the runner log (`>>`) and writes a `# run_scale2 git … resume=…` header line on every call. The doc's execution-script row is updated to say so.
- Doc header: I added a round-3 bullet listing the item ids, the files and sections changed, and the author choices below. The version line now reads "→ 3차 검증(v3 대상; 반드시 5 건) 반영".

**Not applied as given, or added beyond the fixes**
- integ3-1's "G 는 §5 뒤 바꾸지 않는다; 새 G 면 raw 처음부터" and its §4.2 #4 wording "G 변경 = 새 §5 커밋 + 그 raw 처음부터" were left out because they contradict r3-1's raise mechanism. If you prefer integ3-1's stricter rule, revert the `WGBR` lines, the `kchk` condition, and the memory-guard and (k) text.
- Choices I made myself; please confirm or override them:
  - Resuming after a G raise needs no user approval (it is a resource issue), but the user is notified.
  - G′ is set by the same rule as G: highest observed RSS plus 5 %, rounded up to the next 0.5 GB.
  - `kchk` also fails when a raw has no chunks (`not wg`). The old `len(wg) != 1` check caught that case; r3-1's exact condition would have let it through.
  - The two "Q-K undefined" log messages now also mention the `CELL -` case. With a failed C9 cell, `qk` returns empty, so the old wording would blame a K/2 acceptance failure.
- common.py and check_frontier_scale.py are unchanged. None of the five items touches them, and the check passes as is.
- Backups of the pre-round files: `/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/run_scale2_pre_r3.sh` and `…/scratchpad/SCALE16e4_v3_pre_r3.md`.

Files changed:
- `/home/HTJ/t2_wtS/conf/code/run_scale2.sh`
- `/home/HTJ/t2_wtS/conf/results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md`

### 렌즈 stats-fair

#### 반드시
- (없음)

#### 2차 항목 미해결
- (없음)

#### 권고
- §1 메모리 가드 행(:154) "analysis 는 첫 청크 값, `run_manifest`·`ACCEPT (k)` 줄은 전체 집합을 보인다" 는 같은 행의 수용 (k) 문장("`run_manifest.py` 는 이 두 키를 JSON 에 싣지 않는다")과 어긋난다 — `run_manifest.py` 에는 jobs/worker_gb 가 전혀 없다(grep 0 건). → "analysis 는 첫 청크 값, `ACCEPT (k)` 줄이 전체 집합을 보인다(`run_manifest` 는 싣지 않음, 수용 (k))" 로.
- §1 Q-K 행 끝 "Q-K 가 강제 한정어면 (b)(c) 는 돌리지 않는다" 는 스크립트와 반만 맞다: `qk` 가 '' 를 돌려주는 경우(K/2 태그 수용 실패·K2 구성 불가)만 (b)(c) 를 건너뛰고, `c_K = inf`(r ≥ 1) 는 세 실행이 다 돌며 도구가 `(r >= 1) [K 상한 민감: 외삽 불가]` 를 찍는다(라벨은 어차피 강제). → "Q-K 가 K/2 수용 실패·K2 구성 불가로 강제 한정어면 (b)(c) 는 돌리지 않는다; r ≥ 1(`inf`) 은 세 파일이 생기고 도구 출력의 강제 한정어가 우선한다" 로 실행 스크립트 행 문구("강제 한정어(K/2 수용 실패)")와 맞춘다.
- ⑤ 의 "ALL PASS (user CPU 42.1 s; 벽시계 21 분 56 초)" — 이번 재실행은 user 38 s / 벽시계 73 s(nice 19, 1 스레드, HISNR 부하), 적용자 보고 70 s. 부하 의존 수치이므로 "부하에 따라 1–22 분" 정도로 적거나 시간을 빼도 된다(판정 무관).

#### 확인
- stats2-1 해결: §1 다중성 행(:157)이 제안 원문 그대로((T-iv) p := 1, 동률 D2 첫째, 한쪽 (T-iv) 면 그쪽 둘째, 첫째 (T-iv) 는 둘 다일 때뿐, m = 2 고정) + p 해상도·동률 공개 문장; §2.1 (T0-Holm) 행(:183) "첫째가 (T0)". 스크립트는 데이터셋마다 L95·L90 두 파일을 모두 만들어(:285-289) 전사자가 p 순서로 수준 파일을 고를 때 재실행이 없다; p 는 `ci_p` 가 수준과 무관하게 같은 복제에서 계산(코드 확인).
- stats2-2 · integ M1 해결(코드): `trend()`(:270-273) 가 줄마다 그 줄이 쓰는 새 셀의 판정점이 정확히 3 개일 때만 `fci` 를 부르고 아니면 그 줄만 st 1; (:231-233) 이 3 개가 아니면 DP 를 비워 K2·last 를 건너뜀; 가짜 s5/DP 로 시뮬레이션(UMi28 C9 판정점 없음 → U28 1차·S2 만 SKIPPED, D2 1차 2×3 파일·U28 S1 은 실행). `decision_points`(analysis.py:405-413) 는 최대 3 점을 돌려주므로 '정확히 3' = '≥ 3'. §1 실행 스크립트 행에 문장 있음.
- stats2-3 해결: §2.1 Q-K (2) 세 실행 규칙 원문 + D2 기울기 공개; §1 Q-K 행에 (a)(b)(c) 명령·출력 파일 `scale2_primary_{D2,U28}_L{95,90}{,_qkC9,_qkC2}.txt` 고정; 스크립트 `qkv`(:277-278) 를 시뮬레이션: (a) `--extrap raw_K2NR32B16e4 raw_B16e4 --ck 1.5 5.2637007373767215` → (b) `--extrap raw_K2NR32B16e4 - --ck 1.5 -`, (c) `--extrap - raw_B16e4 --ck - 5.2637007373767215`; C9 내부면 (b) = `--extrap - - --ck - -`. `frontier_ci.py --extrap - - --ck - - --level 0.95 --B 5` 직접 실행 → argparse 통과, 외삽 없음과 같은 줄(Q-K 줄 없음). `--rstar` 는 (a) 에만, `--level $LV` 는 셋 다(:288-294).
- fair2-1 해결: `check_frontier_scale.py` (6) 이 제안 코드 그대로 들어 있고 이 세션에서 재실행(CUDA 숨김, nice 19, 1 스레드): ALL PASS, 벽시계 72.9 s / user 38.2 s; R*@0.05 0.610017 / 0.806386 / 0.218465, R_dp 0.508796 / 0.822785 / 0.150427, 교차 raw `b*(K/2) 899  dF = +35  c_K = 5.2637  SigmaF+ = 679.77  R+ = 0.346 [90% 0.106, 0.492]  SigmaF+ <= SigmaF_g in 0.0%`, R1+ − R2+ = +0.477 [95% +0.301, +0.787], 외삽 없음 R1 − R2 = +0.314 [95% +0.241, +0.393]. §1 ⑤ 문구가 (6) 을 실제 검사로 서술하고 v2 의 거짓 문장을 정정.
- fair2-2 해결: `run_scale2.sh` (:249-252) A 단독 호출(`--nr --fits-dir --grid --tag $T`) → ACC[$T] = 모든 `trend` 줄의 게이트 키(:288-305), `${T}pa` A+PIL+ALD 공동 호출(`--ref-raw raw_$T`, 3 `--tag`) → ACC[${T}pa]; pair 는 `ok $T ${T}pa`(:309). 문서 §1 실행 스크립트 행·수용 (b)·§5 실행 인자 행(`<T>pa_accept.txt`) 일치. PIL·ALD 만 실패하면 pair 만 빠지고 추세는 돈다.
- r3-1 · r3-2(3차, 내 렌즈) 적용 확인: `WGBR=${SCALE2_WGB:-$WGB}`(:35), 전제 `r ≥ g`(:92), 시작 로그 `(run $WGBR)`(:108), C9 `--worker-gb $WGBR`(:223), `kchk` 가 `not wg | None | any(<g)` 면 실패(:153); `CELL <tag> -` 는 전제(:71)·GPU 루프(:115)·CPU 루프(:222) 에서 건너뜀 — 시뮬레이션에서 `s5` 가 '-' 를 첫 필드로 돌려주고 `read` 의 ST='-', K2K='' 로 `qk` 가 '' → 강제 Q-K 로그, 그 셀 추세 줄은 DP 가드로 SKIPPED. 문서 메모리 가드 행·수용 (k)·§4.2 #4·학습 실패 행·실행 스크립트 행이 스크립트와 일치.
- `dp()` 앵커 정규식을 실제 표 5 개에 적용: tables_D2_S1D2C9 → -9 -6 -3, S1U28C6 → 0 3 6, S1U28C9 → -3 0 3, main tables_D2_NR16B16e4 → -3 0 3, U28B16e4 → 3 6 9 (모두 블록 1 개, 기록 판정점과 일치); analysis.py:440-442 의 줄 형식과 정합. `eval_accept` 는 `ACCEPT: OK/FAILED`, `kchk` 는 `ACCEPT (k): …` 를 찍어 `grep ^ACCEPT` 가 둘 다 잡는다. `acc` 의 (k) 태그 파싱은 `--tag …:C9` 만 잡고 `--points C9:…`·`--grid` 는 잡지 않는다.
- 문서 정합: 표 열 수 불일치 0, `{{NOW}}` 2 개 유지, 314 줄. 1차 명령 원문(:156)·2차(:161)·보고 전용 C6 ΔF_K(:162) 와 스크립트 인자가 순서만 다를 뿐 동일(argparse 순서 무관). 재사용 셀 등록 CI = `scale2_primary_<d>_L90.txt` R2 줄(수준 무관 `pct(bo,[5,95])`, 같은 seed 라 L95 파일과 동일). Holm CI 와 p 가 같은 복제에서 나와 라벨(CI 기준) 과 p 순서가 정합.
- 새 반드시 없음: 라벨을 결과가 고를 경로(Holm 동률·(T-iv)·강제 Q-K·판정점 자동·게이트)는 모두 결정론적이고, 동일예산(N′ 1.6e5, K ≤ 4096, 격자 끝 규칙, c_K 는 §5 ll_val 입력)·재현성(seed 20260926, B 2000, spec 순서 고정, 머리말 git)·스크립트 실행(모든 플래그 존재, 가짜 입력 시뮬레이션 통과)에서 결함을 찾지 못했다.

### 렌즈 integ

#### 반드시
- **[integ4-1]** §1 실행 스크립트 행 (`bash code/run_scale2.sh tune` 문장) + §1 실행 순서 행 ("→ ALD tune (GPU) →") + §4.1 "[동결 뒤] ALD 조정 3" 행
  - 문제: `tune` 모드도 `run_scale2.sh` 줄 65–73 에서 `results/scale/scale2_s5.txt` 를 읽는다: 파일이 없으면 `die "$S5 missing"`, 있으면 `FREEZE` 가 HEAD 의 조상이고 code·Demo 가 같아야 하며 새 셀마다 `CELL <tag> <stem> <best_sha16>` 로 `_best.pt` 의 sha256 을 대조한 뒤에야 74행 `continue` 로 나머지 필드 검사를 건너뛴다. 문서는 tune 을 "동결 뒤·§5 전" 에 두고 `scale2_s5.txt` 는 "§5 와 함께 커밋" 이라고만 적었으므로, 문서의 실행 순서(동결 → … → ALD tune → 링크 생성 → §5 + scale2_s5.txt 커밋)대로 `tune` 을 부르면 반드시 `ABORT (precondition): results/scale/scale2_s5.txt missing` 으로 끝난다(gpuq 줄 `95 GPU ald_scale2 bash code/run_scale2.sh tune` 로 넣었으면 rc 1 로 소비되고 재큐가 필요). 스크립트가 문서와 다른 전제를 요구하는 것이므로 지금 문서에 적어야 한다(코드 변경 불필요).
  - 수정: §1 실행 스크립트 행의 "`bash code/run_scale2.sh tune` (동결 뒤·§5 전, 호출자가 `CUDA_VISIBLE_DEVICES=<빈 GPU 하나>`; 예: gpuq 줄 `95 GPU ald_scale2 bash code/run_scale2.sh tune`)" 를 다음으로 바꾼다: "`bash code/run_scale2.sh tune` (동결 뒤·§5 전, 호출자가 `CUDA_VISIBLE_DEVICES=<빈 GPU 하나>`; 예: gpuq 줄 `95 GPU ald_scale2 bash code/run_scale2.sh tune`; **tune 도 `results/scale/scale2_s5.txt` 를 읽으므로 그 전에 미추적 초안을 만든다** — `FREEZE <동결 커밋>` 한 줄 + 새 셀마다 `CELL <tag> <ckpt_stem> <best_sha16>` (학습 실패 셀은 `CELL <tag> -`); 스크립트 줄 65–73 은 이 세 필드와 `_best.pt` sha256 만 보고 나머지 8 필드·`WGB` 는 §5 때 채워 §5 커밋에 넣는다)". §1 실행 순서 행의 "→ GB′ 3 → ALD tune (GPU) →" 를 "→ GB′ 3 → `scale2_s5.txt` 초안(FREEZE + CELL stem·best sha; 미추적) → ALD tune (GPU) →" 로, §4.1 의 "[동결 뒤] ALD 조정 3 (`run_scale2.sh tune`, GPU) | 대기 → §4.2 항목 8" 을 "[동결 뒤] `scale2_s5.txt` 초안(FREEZE·CELL stem·best sha, 미추적) → ALD 조정 3 (`run_scale2.sh tune`, GPU) | 대기 → §4.2 항목 8" 로 바꾼다.
- **[integ4-2]** §1 실행 스크립트 행 "게이트" 문장 + 수용 검사 (e) + `run_scale2.sh` 15행 머리말, (4) 추세 줄 288·289·291·293·297·298·299, G6 (302–303), (5) 309행
  - 문제: chk 는 수용 검사 (e) 의 항목이고 그 표의 머리말은 "하나라도 어긋나면 그 태그 무효" 인데, 스크립트의 추세 게이트 키는 A 단독 `<T>` (+ bridge), pair 게이트는 `<T>`·`<T>pa` 뿐이라 `<T>chk_accept.txt` 가 FAILED(A 청크 0 이 동결 코드로 11 arm 비트 재현되지 않음)여도 그 셀의 1차·2차 줄과 pair 가 그대로 돌아 라벨이 파일에 찍힌다(fail 수만 +1). 문서는 bridge 실패의 결과("추세에서 빠지고 (T-iv) 수용 실패")는 정했지만 chk 실패의 결과는 어디에도 정하지 않았고 §2.1 (T-iv) 사유에는 "수용 실패" 가 있다 → 전사자가 결과를 본 뒤 그 데이터셋을 파일의 (T±) 로 옮길지 "수용 실패" (T-iv) 로 둘지 고르게 된다. 재현되지 않은 A raw 는 bridge 가 깨진 재사용 raw 와 같은 지위여야 하므로 지금 게이트에 넣어 결정론적으로 만든다(비용 0; chk 는 이미 돈다).
  - 수정: (1) `run_scale2.sh` 게이트 키에 `<T>chk` 를 넣는다 — 288행 `NR32B16e4,BRB16e4k` → `NR32B16e4,NR32B16e4chk,BRB16e4k`; 289행 `U28NR32B16e4,BRU28` → `U28NR32B16e4,U28NR32B16e4chk,BRU28`; 291행 `NR32B16e4,BRB16e4k` → `NR32B16e4,NR32B16e4chk,BRB16e4k`; 293행 `U28NR32B16e4,BRU28` → `U28NR32B16e4,U28NR32B16e4chk,BRU28`; 297행 `NR32B16e4,BRNR16` → `NR32B16e4,NR32B16e4chk,BRNR16`; 298행 `U28NR16B16e4,BRU28` → `U28NR16B16e4,U28NR16B16e4chk,BRU28`; 299행 `U28NR32B16e4,U28NR16B16e4` → `U28NR32B16e4,U28NR32B16e4chk,U28NR16B16e4,U28NR16B16e4chk`; 302행 `G6=U28NR16B16e4,K2NR16B16e4,BRNR16` → `G6=U28NR16B16e4,U28NR16B16e4chk,K2NR16B16e4,BRNR16`, 303행 `G6=U28NR16B16e4,K2U28NR16B16e4,K2NR16B16e4,BRNR16` → `G6=U28NR16B16e4,U28NR16B16e4chk,K2U28NR16B16e4,K2NR16B16e4,BRNR16`; 309행 `ok $T ${T}pa || { st 1 "pair_baselines $T SKIPPED: acceptance A or A+PIL+ALD failed (no pair on a failed tag)"; continue; }` → `ok $T ${T}chk ${T}pa || { st 1 "pair_baselines $T SKIPPED: acceptance A / chk / A+PIL+ALD failed (no pair on a failed tag)"; continue; }`; 15행 `#   (A ALONE with the grid = TREND gate; A+PIL+ALD one call = PAIR gate; chk, K2, last separate calls; every C9 tag also acceptance (k))` → `#   (A ALONE with the grid + <T>chk replay = TREND gate; those two + A+PIL+ALD one call = PAIR gate; chk, K2, last separate calls; every C9 tag also acceptance (k))`; `bash -n` 재확인. (2) §1 실행 스크립트 행: "새 셀의 **추세 게이트 = A 단독 수용 호출** `results/review_next/<T>_accept.txt` (격자 (a)·meta·ckpt id; C9 는 (k) 포함), **pair 게이트 = A 단독 + A·PIL·ALD 공동 호출** `<T>pa_accept.txt` ((b) fits 실체·em_sec 동일, (d) genie 재생)" → "새 셀의 **추세 게이트 = A 단독 수용 호출** `results/review_next/<T>_accept.txt` (격자 (a)·meta·ckpt id; C9 는 (k) 포함) **+ chk 수용 호출** `<T>chk_accept.txt` (수용 (e): A 청크 0 의 11 arm 비트 재현), **pair 게이트 = 그 둘 + A·PIL·ALD 공동 호출** `<T>pa_accept.txt` ((b) fits 실체·em_sec 동일, (d) genie 재생)". (3) 수용 검사 (e) 의 "**bridge 가 실패하면** 그 재사용 태그는 추세에서 빠지고" 바로 앞에 넣는다: "**chk 가 실패하면** 그 새 셀의 A 태그는 동결 코드로 재현되지 않은 것이므로 추세·pair 에서 빠지고(그 셀을 쓰는 1차는 (T-iv) \"수용 실패\", 2차 단계는 \"판정하지 못함\"; `run_scale2.sh` 게이트 키 `<T>chk`), 재실행은 사용자 승인이다(bridge 와 같은 규칙). "

#### 2차 항목 미해결
- (없음)

#### 권고
- §1 메모리 가드 행 끝 "`run_manifest`·`ACCEPT (k)` 줄은 전체 집합을 보인다" → "`ACCEPT (k)` 줄(과 청크 npz)이 전체 집합을 보인다" — `run_manifest.py` 는 `meta|jobs`·`meta|worker_gb` 를 JSON 에 싣지 않는다(직접 grep 0 건; 머리 목록 '달리 반영' 과도 어긋남).
- Q-K `--ck inf` (r ≥ 1) 는 강제 한정어인데 스크립트는 `Q_<d>` 가 비어 있지 않아 (b)(c) 도 돌린다 — 라벨은 안 바뀌지만 §1 Q-K 행·실행 스크립트 행의 "강제 한정어면 (b)(c) 는 돌리지 않는다" 를 "(K/2 수용 실패·K2 구성 불가로 `--extrap` 없이 도는 경우; `--ck inf` 면 (b)(c) 도 돌지만 파일의 '[K 상한 민감: 외삽 불가]' 가 우선)" 로 고쳐 원문을 맞춘다.
- 2차 단계 세 줄(297–299)에 `--level 0.90` 을 명시해 §1 2차 행의 명령 원문과 파일 머리말이 글자까지 같게 한다(기본값이라 결과 동일).
- 줄 번호 인용 정정: 수용 (b) `eval_accept.py:94,128` → `:94,129` (tags disagree 줄); §4.1 CPU 행 `run_scale2.sh:60` → `:62` (60 은 주석).
- ⑤ 시간 문구: 이번 재실행 ALL PASS, 벽시계 73 s (nice 19, BLAS 1 스레드, GPU 숨김, HISNR 부하 중) — "벽시계 21 분 56 초" 는 그때의 부하값이므로 조건을 함께 적거나 지운다.
- 동결 뒤 GB′ 3 이 추적 파일 `results/d2_gbprime_UMi28.csv`(·D2 csv)에 행을 더하면 실행 내내 dirty 로 남는다(스크립트 전제는 code·Demo·이 문서·DECISIONS 만 보므로 실행은 되나 §5 '문서 + scale2_s5.txt 만 커밋' 과 어긋남) → §5 커밋에 GB′ csv 행도 넣는다고 §1 §5 행에 한 구절.
- 작성자 선택 확인(내 렌즈): G′ 규칙·재개 승인 불필요·`kchk` 의 `not wg` 실패·Q-K 미정의 문구 모두 동의; integ3-1 의 '새 §5 커밋' 경로를 버린 병합도 결정 7·수용 (f) 와 정합.

#### 확인
- integ M1 해결: run_scale2.sh 231–233 (판정점 정확히 3 개 아니면 DP 비우고 가드 기록), 270–273 `trend` 줄별 게이트(`tr` 와 겹치지 않음), 285–299 1차 L95/L90·(b)(c)·단계 세 줄 모두 `trend` 경유; 문서 §1 실행 스크립트 행에 '줄마다 게이트'·'판정점 3 개 아닌 셀은 K2·last·그 셀 추세만 건너뜀' 문장 있음.
- integ M2 해결: §1 수용 (b) = A 단독 / A·PIL·ALD 공동 / chk 별도(`eval_accept.py:51,67` 근거) 원문, 스크립트 249–257 과 일치; v1→v2 요약(32행)에 정정 표기.
- 3차 항목 확인: r3-1 (`WGBR` 35행, 전제 92행 raise-only, 시작 로그 108행, `--worker-gb $WGBR` 223행, `kchk` ≥ WGB + `not wg`; 문서 (k)·메모리 가드 행), r3-2 (`CELL <tag> -` 26·71·115·222행, 문서 학습 실패·실행 스크립트 행), integ3-1 병합(RSS ≤ 1.25·G 근거, 멈춤 조건, §4.2 #4), integ3-2 (§4.1 CPU 행, 실행 순서·비용·전제 문구), integ3-3 (`run()` 138–139 `>>` + 머리말 줄; 문서 실행 스크립트 행).
- `bash -n code/run_scale2.sh` 통과; 스크립트가 쓰는 플래그 전부가 argparse 에 있음: runner.py (cmd, --testbed --ntrain --prior --cell --worker-gb --stagec-ckpt --n --chunk --arm --pilot-arms --ald-file --snr --tag), ald.py (regen/tune/estimate, --tag --prior --cell --fits-tag --set --ckpt), eval_accept.py (--ntrain --prior --nr --bstar --kron-K --ll-val --points --ref-raw --fits-dir --grid --tag --n --ref-arms), run_manifest --tag, guard_report --raw --testbed, recovery_ci --raw --cell --snrs, frontier_ci --recovery --level --extrap --ck --rstar, pair_baselines --base --pil --ald --est --cell --prior --r0.
- `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 nice -n 19 python code/check_frontier_scale.py` → ALL PASS, 벽시계 73 s; R* 0.610017/0.806386/0.218465, R_dp 0.508796/0.822785/0.150427, (6) 교차 raw `b*(K/2) 899 dF = +35`, R2+ 0.346 [0.106, 0.492], R1+ − R2+ +0.477 [95% +0.301, +0.787] — 문서 §0.1·⑤ 값과 동일.
- common.py 변경은 C9 snrs 한 줄뿐; fit_gpu·gmm_em_gpu·train_nr16·score·arms·d2·em_batched_check_nr·gpu_sched.sh·edge_rule.sh·gpu_filler.sh·run_fitq.sh 어디에도 `snrs`/`CELLS[` 없음(grep); 실행 중 worktree fit_gpu.py 6 개는 격자를 읽지 않음. /home/HTJ/t2 는 건드리지 않았고 파일 수정 없음.
- gpu_sched.sh 는 `CUDA_VISIBLE_DEVICES=<index 0–5>` 로 띄우므로 `[[ $G =~ ^[0-9]$ ]]` 통과; tune/estimate 의 `--ckpt ckpt/<stem>_best.pt` 문자열이 두 호출에서 같아 ald.py 253행 assert 통과.
- 가짜 입력 단위 검사(스크래치): `s5()`·K2/c_K 전제(77–78행)·`read` 11 필드·`CELL -`·full b*(gmm256, KK '-') 모두 기대대로; `qkv` (b)(c) 출력 정확; `kchk` {8.0,9.5}→OK, 7.5→FAIL, 키 없음→FAIL, 청크 없음→FAIL.
- `dp()` 정규식을 1단계 표 3 개에 적용: S1D2C9 −9 −6 −3, S1U28C6 0 3 6, S1U28C9 −3 0 3, 블록 각 1 개.
- ckpt sha256[:16] 5 개가 RU 표·§0.6 과 일치(4443921ce8d5c4a1 / c050d611b2c714a6 / 6f3a1b9490864af1 / 3cf5d3eff96f0341 / 1f782042a5ad06b8); `d2sx_N160000_a1.pt` 는 role 키가 없어 `legacy-last` (score.py:712) → BRB16e4k 수용 태그 문자열 정확; 새 ckpt 는 best/last 로 저장됨(score.py:1026–1027).
- raw_B16e4k 448 C2 파일 git 추적, raw_B16e4 C2 448 (추적 1344), raw_NR16B16e4·raw_U28B16e4 링크 448 씩, ckpt 링크 → /home/HTJ/t2/conf/ckpt; `results/gmm_fits_D2_NR16B16e4` 는 아직 없음(§4.1 링크 행·전제 ABORT 로 처리됨); kron 1024 후보 3 + 병합 파일 존재(NR32B16e4).
- frontier_ci: `--extrap - - --ck - -` 는 argparse 통과, Q-K 줄을 찍지 않아 외삽 없음과 동일(문서 문장과 일치); `_k2_cols` 가 genie 동일을 assert; B/SEED 2000/20260926. runner: 끝난 청크 건너뜀(:489), `run|git` +dirty 표시(:457), meta|jobs·worker_gb 는 `_init` 로 기록, `d_fits_d2` = gmm_fits_D2_<tag>; V0·V4·V4b 는 여전히 빌드됨(arms.py:265–271) → 14 arm bridge 구성 가능. run_manifest 는 tables 파일 없이도 씀. pair_baselines run-git 규칙 = raw 마다 깨끗한 커밋 하나, 점 집합 = CELLS 격자.
- 문서: `{{NOW}}` 2 곳 유지, 표 열 수 정상, §5 수용 파일 목록에 `<T>pa_accept.txt` 포함, 검토 원문 디렉터리에 round1·round2 존재.
