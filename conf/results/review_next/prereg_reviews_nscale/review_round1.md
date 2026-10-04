# NSCALE 등록 검토 원문 — 라운드 1 (워크플로 wf_d394d246-6da; 작성자 Opus 5.5, 검토자 Fable 5.1 두 관점)

## 작성자 보고

등록 초안과 CPU 실행 스크립트를 썼습니다. BLER·GPU·커밋·삭제는 하지 않았습니다. 시각은 쓰지 않았고 `{{NOW}}` 자리표시 20개는 그대로 두었습니다.

- 초안: `/home/HTJ/t2/conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md` (v0, §0–§6, §6 비어 있음)
- 스크립트: `/home/HTJ/t2/conf/code/run_nscale.sh`
- 검증 산출물(커밋하지 않음): `/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/nscale_reg/`

## 확인한 것 (BLER 없이)

- **스크립트**:
  - `bash -n` 통과.
  - 스크립트가 쓰는 python 플래그 전부를 각 도구의 argparse에서 grep으로 대조했고, 빠진 플래그는 없습니다 (runner, eval_accept, frontier_ci, recovery_ci, guard_report, run_manifest).
- **`prep` 모드**: 기준 두 점(B32e4, NR16B16e4)으로 돌려 기록값을 그대로 재현했습니다.
  - b\* = kron 4096, ll_val −5.942083265612076 / 63.1751571838059.
  - r 0.6690… → c_K 2.021371931572057, r 0.3816… → c_K 1.
  - K/2 링크 집합의 b\* = kron 2048.
  - sha, epoch, `# done` 줄, D1 게이트, GB′ 행.
- **보조 함수**: P1 자동 라벨, Holm 보조(실제 파일·(T-iv)·가짜 (T±)), `same`, `gitchk`, `qk` 인자 조립(강제 한정어 포함), S5 파싱을 기존 raw와 가짜 입력으로 시험했습니다.
- **기준 raw 상태**:
  - `raw_B32e4`, `raw_NR16B16e4`, `raw_B16e4k`, `raw_B1e4`는 448 파일이고 −3/0/+3과 b\*·V1·genie arm이 있습니다.
  - 예산이 달라도 genie가 같아서 `--paired` assert를 통과합니다 (C2 3.2e5 대 1.6e5, C6 1.6e5 대 1e4).
- **`frontier_ci --paired`의 한계**: `--extrap/--ck/--rstar`를 받지 않습니다 ("need --recovery"로 거부). `--level`은 받지만 무시합니다. 그래서 Q-K와 Q-OP는 `--recovery`로 계산하게 했고, 기준 raw로 배관이 도는 것을 확인했습니다.

## 설계 결정과 근거

1. **P1 (새 점마다)**: 표 B `b*→V1`을 선례 형식 그대로 둡니다. C2는 B32e4 §2(D1 게이트 PASS/FAIL/학습 실패), C6은 C6B16e4 §2 (i)–(iv)에 회수율 대역을 반드시 함께 붙입니다.
2. **P2 짝 추세**:
   - 대비는 ΔR_C2 = R(1.28e6) − R(3.2e5), ΔR_C6 = R(6.4e5) − R(1.6e5)입니다.
   - SNR은 −3/0/+3으로 고정했습니다. 기준점의 기록된 판정점이고, 짝 비교는 같은 점 집합이 필요하기 때문입니다.
   - 비교는 `_best`끼리만 하고 B 2000, seed 20260926입니다.
   - Holm m=2: (T-iv)이면 p := 1, 동률이면 C2를 첫째(GATED 셀)로 둡니다. 라벨은 (T+)/(T−)/(T0)/(T0-Holm)/(T-iv)이고 (T±)에는 G_N을 붙입니다.
3. **Q-K와 Q-OP는 비짝 `--recovery`로 계산**합니다. 코드를 바꾸지 않아도 되고, CI가 짝보다 넓어 "강건" 쪽에 보수적입니다. 공개 9에 적었습니다.
   - 실행 (a) 두 끝 + R\*@0.05, (b) 새 끝만 = (T+)의 최악 방향, (c) 기준 끝만 = (T−)의 최악 방향.
   - 기준 끝 c_K는 C2 2.021371931572057, C6 1입니다.
4. **판정 합성안에 없던 태그를 더했습니다**:
   - bridge `BRB32e4`, `BRNR16B16e4`: 기준 raw가 예전 코드로 만들어져서, 지금 코드가 그것을 비트 단위로 재현하는지 확인합니다. 실패하면 그 셀은 (T-iv)입니다.
   - D2 C2의 chk 태그: SCALE 게이트 관례와 맞추려는 것이고 비용은 청크 1개입니다.
   - `K2B32e4`: 3.2e5의 kron 2048은 BLER로 평가된 적이 없어서 새로 돌립니다. CPU만 씁니다.
5. **보고 전용 kron 8192**: 적합 디렉터리 `gmm_fits_D2_K8B64e4`는 건드리지 않습니다. 따로 링크 집합 `gmm_fits_D2_B64e4k8`(B64e4 격자 + 8192)을 만들어 BLER 태그 `B64e4k8`로만 씁니다. 8192가 ll_val로 이길 때만 실행하고, V1이 B64e4와 비트 동일한지 무결성 줄을 남깁니다.
6. **대체 규칙 F1–F6**은 적합·학습·검사 결과만 보고 판단합니다. F1(1.28e6 실패 → D2 1차가 R(6.4e5) − R(3.2e5)) 발동 조건은 다음 중 하나입니다.
   - 1.28e6 일괄 검사 FAIL: 정확 경로는 재시작당 약 4.5–10일로 추정돼 승인 예산 밖입니다.
   - 1.28e6 kron 4096 재시작에서 OOM.
   - V1 또는 D1 형제가 §3d 시행 3까지 실패.
   - 같은 시드로 다시 돌려도 적합이 비정상 종료.
   - 6.4e5 지점의 일괄 검사 FAIL은 F1이 아니라 F4(정확 경로로 수동 큐)입니다.
7. **학습 집합의 중첩을 assert하지 않습니다**. `prefix.log`상 독립 추출이므로 공개 5로 처리했습니다. 판정 합성안의 "앞부분 포함 assert"는 뺐습니다.
8. **비용 추정**: CPU 약 6–8시간 (C2 last는 B32e4last처럼 arm 전부라 analysis가 돕니다), GPU는 판정 합성안의 수치를 썼습니다.

## 공개할 것과 예측에 앞서 본 것

- 공개 1–12는 §2.4에 모았습니다. 요청하신 8개(순차 선택, 기준 결과 알려짐, 시드 분산이 부트스트랩에 없음, 시행 재사용, 독립 추출, 희소 대 일괄 정확 적합, C6 fb2 대 시행 1, kron 8192 보고 전용)에 비짝 한정어, SNR 고정, K 상한 교란, (E)의 legacy-last V1을 더했습니다.
- **예측을 쓰기 전에 본 것**: C2의 R은 1e4 → 3.2e5에서 0.540 → 0.518 → 0.509 → 0.495로 줄었고, R(3.2e5) − R(1e4) = −0.045 [90% −0.081, −0.012]입니다. 짝 SD는 C2 0.019, C6 0.028이고, 80 % 검정력의 최소 검출 효과는 C2 0.053, C6 0.078입니다(95 %).
- 그래서 예측은 두 추세 모두 (T0)입니다. 이 설계에서 (T0)은 예상되는 결과이고 "예산과 무관하다"는 증거가 아니라는 문구를 넣었습니다. C2에서 (T−)가 나올 가능성은 있습니다.

## 열린 항목 (검토자나 주 세션이 정할 것)

1. Q-K/Q-OP를 짝으로 하려면 동결 전에 `frontier_ci --paired`에 `--extrap/--rstar`를 추가하는 코드 변경과 항등 검사가 필요합니다. 지금 초안은 비짝입니다.
2. `raw_K2NR16B16e4`는 `~/t2_wtS/conf`에만 있습니다. `links` 모드가 SEEDSNR 이후에 main에서 읽기 전용 링크를 만들도록 했고, main에서 다시 돌리는 방법(약 15분)도 있습니다.
3. GB′ 재실행 3개는 주 세션이 gpuq에 넣어야 합니다. `prep`이 GB′ 줄을 `logs/nscale/*.log`에서 찾으므로 로그를 그 디렉터리에 두는 것이 좋습니다.
4. F1 (i)은 판정 합성안대로 정확 경로로 넘어가지 않고 바로 대체합니다. 사용자가 다르게 정할 수 있습니다.
5. 동등성(δ) 라벨은 판정 합성안대로 넣지 않았습니다. 검토자가 검정력 부족을 이유로 요구할 수 있습니다.
6. 주 세션이 할 일: 메모리 노트 `larger-n-after-stage-c.md` 정정, §4.1 GPU 진행 상황 채우기, 검토 원문 디렉터리 `prereg_reviews_nscale/` 만들기.

## 검토 — 관점 stats-fair

### must
- **M1** (run_nscale.sh:363-364, 379-380 (K2 수용 호출) · NEXT_EXPERIMENTS_NSCALE.md §1 수용 검사 (a)/(b) K2)
  - 문제: `lset` 가 만드는 K2 링크 집합은 `.k0r*` 후보를 건너뛰고 병합 파일만 링크한다 (run_nscale.sh:178). 그런데 `eval_accept.py --fits-dir … --grid` 는 kron K ≥ 1024 마다 후보 3 개를 `--cand-dir` 또는 fits-dir 에서 찾고 없으면 FAILED 로 둔다 (eval_accept.py:142-146). 실측: B32e4 병합 파일만 링크한 14 파일 집합에 등록된 K2 수용 명령을 그대로 돌리면 `grid: kron K=1024 has 0 candidate files, expected 3` / `K=2048 …` 로 ACCEPT: FAILED; `--cand-dir results/gmm_fits_D2_B32e4` 를 붙이면 격자 줄이 사라진다. SCALE16e4 의 K2 집합은 후보 링크 6 개를 포함한 20 링크였다 (SCALE16e4 §5 :338 '링크 20'). 따라서 K2B32e4·K2B64e4·K2B128e4·K2NR16B64e4 수용이 데이터와 무관하게 전부 실패 → `ok K2$T`/`ok K2B32e4` 거짓 → 두 셀 모두 '[K 상한 민감: 외삽 불가]' 강제, 실행 (b)(c) 미실행 = 등록된 Q-K 가 항상 비어 있는 오기록.
  - 수정: run_nscale.sh:363-364 를 다음으로 교체:
acc K2B32e4 320000 --nr 8 --bstar kron --kron-K 2048 --ll-val -7.792724507139091 --points C2:-3,0,3 --fits-dir results/gmm_fits_D2_K2B32e4 \
  --cand-dir results/gmm_fits_D2_B32e4 --grid "full:$GF kron:${GK%,*}" --ref-raw raw_B32e4 --tag K2B32e4:best:035744cbe955984d:C2
run_nscale.sh:379-380 을 다음으로 교체:
  [ "$K2K" = - ] || acc K2$T $N --prior S2 --nr $NR --bstar kron --kron-K $K2K --ll-val $K2LL --points $CELL:-3,0,3 \
    --fits-dir results/gmm_fits_D2_K2$T --cand-dir results/gmm_fits_D2_$T --grid "full:$FK kron:${KR%,*}" --ref-raw raw_$T --tag K2$T:best:$BSHA:$CELL
§1 수용 검사 (a) 끝에 추가: "K2 링크 집합 (`lset`) 은 병합 파일만 담으므로 K/2 수용의 kron K ≥ 1024 후보 3 개 검사는 `--cand-dir results/gmm_fits_D2_<원 태그>` (K2B32e4 → B32e4, K2<T> → <T>) 로 원 디렉터리에서 한다 (SCALE16e4 의 K2 집합은 후보 링크 6 개를 포함한 20 링크였다)." 동결 전에 `bash -n` 뒤 B32e4 격자로 수용 명령을 한 번 돌려 격자 줄이 없는지 확인한다.
- **M2** (run_nscale.sh:113 (prep DRAFT), 428-430 (qk 강제 조건) · §1 한정어 Q-K 행)
  - 문제: §1 은 'K2 구성 불가 (K/2 링크 집합의 b* 가 kron 2048 이 아님)' 을 강제 한정어 조건으로 두지만, 스크립트는 S5 의 K2_K = '-' 를 항상 'b* 내부' 로 읽는다 (qk: `[ "$K2K" = - ] ||` → E1=- C1=- 로 (a)(b)(c) 정상 실행, 강제 줄 없음). 게다가 prep 는 그 경우 `… - - <c_K>` 를 써서 (run_nscale.sh:113 은 K2K·K2LL 만 '-' 로 바꾸고 cK 는 남김) 사전 조건 :229 `[ "${12}${13}" = -- ]` 에 걸려 ABORT 하므로 주 세션이 손으로 `- - -` 로 고치게 되고, 그러면 b* = kron 4096 인 격자 끝 점이 '내부' 로 돌아 전사자가 '[K 상한 강건]' 을 쓸 수 있다 — §1 과 어긋나는 오기록 경로.
  - 수정: run_nscale.sh:113 교체: `        K2K, K2LL, cK = ("2048", repr(b2[2]), cK) if ok2 else ("-", "-", "-")`
run_nscale.sh:428-430 교체:
  if [ "$KK" = 4096 ] && [ "$K2K" = - ]; then FORCE="K2 구성 불가 (b* = kron 4096, K/2 집합 b* != kron 2048)"
  elif ! ok $4; then FORCE="기준 K/2 태그 수용 실패 ($4)"
  elif [ "$K2K" != - ] && ! ok K2$T; then FORCE="새 K/2 태그 수용 실패 (K2$T)"
  elif [ "$C1" = inf ]; then FORCE="r >= 1"; else FORCE=""; fi
  if [ -z "$FORCE" ]; then NOTE=""; X="--extrap $E1 $3 --ck $C1 $5"; G=$G,$4; [ "$K2K" = - ] || G=$G,K2$T
  else NOTE="# Q-K: [K 상한 민감: 외삽 불가] (forced, §2.2 Q-K (1): $FORCE -> run (a) without --extrap, no (b)(c))"; X=""; fi
§1 Q-K 행의 '강제 한정어' 문장 뒤에 추가: "S5 표기: b* = kron 4096 인데 `K2_K K2_ll c_K` 가 `- - -` 이면 K2 구성 불가다 (`prep` 가 그렇게 쓴다); 스크립트는 이 조합을 강제 한정어로 처리하고 사유를 파일 머리말에 적는다. `K2_K = -` 가 '내부' 를 뜻하는 것은 b* 가 kron 4096 이 아닐 때뿐이다."
- **M3** (§1 한정어 Q-OP·Q-K 행, §2.2 한정어 (Q-OP, Q-K (2)), §2.4 공개 9 · run_nscale.sh:425-438 (qk))
  - 문제: 1차 ΔR 는 짝 (`--paired`) 인데 Q-K·Q-OP 는 비짝 (`--recovery`) 이고, 한정어 규칙은 L⁺·L* 를 '1차 라벨' 과 비교한다. SCALE16e4 는 1차도 비짝이어서 (§1 1차 통계량 행 'ΔR_d 는 비짝 부트스트랩') 같은 발판이었다. 초안 §0.3 의 자체 수치로 비짝 SD 는 짝의 1.7 배 (C2 0.032/0.019)·1.4 배 (C6 0.040/0.028) 다. 그래서 1차가 (T±) 일 때 외삽을 전혀 하지 않아도 (ΔF_K ≤ 0, b*⁺ = b*) 실행 (a) 의 L⁺ 와 L* 가 CI 폭만으로 (T0) 이 되어 규칙대로 '[K 상한 민감: 실행 (a)/(b)/(c) 의 b*⁺ 에서 (T0)]'·'[운영점 민감: R*@0.05 에서 (T0)]' 을 쓰게 된다 — K 상한·운영점이 원인이 아닌 결과에 그 원인을 적는 오기록 (공개 9 의 '보수적' 은 강건 쪽에만 맞고 민감 문구의 귀인은 틀린다).
  - 수정: 택 1 을 동결 전에 고정한다. (A, 선호) `frontier_ci.py cmd_paired` 에 `--extrap/--ck/--rstar` 를 추가 (같은 (셀, SNR) 인덱스를 두 raw 와 K/2 b* 열에 공유; R* 는 7 SNR 전 격자에 공유 인덱스; 항등 검사: 같은 raw 두 번 → ΔR⁺ ≡ 0·L* ≡ 0, 옵션 없을 때 기존 `--paired`·`--recovery` 출력 바이트 동일) 하고, §1 Q-OP·Q-K 행과 공개 9 의 '비짝' 을 '짝' 으로, run_nscale.sh:432-435 의 `--recovery` 를 `--paired` 로 바꾼다 (코드 변경은 동결 커밋에 포함). (B, 코드 변경 없음) §2.2 '한정어' 첫 하위 항목으로 추가: "- **비짝 기준 L⁰** (한정어의 비교 기준; 1차 라벨이 아니다): 실행 (a) 파일의 `R1 - R2 … (--level L)` 줄 (외삽 없음, 비짝, 그 셀의 Holm 수준) 에 (T+)/(T−)/(T0) 규칙을 적용한 라벨. 1차는 짝·한정어는 비짝이라 CI 폭이 다르므로 (§0.3: 비짝 SD 가 짝의 1.4–1.7 배) 한정어는 1차 라벨이 아니라 L⁰ 와 비교한다. **L⁰ ≠ 1차 라벨이면** Q-K·Q-OP 자리에 '[한정어 판정 불가: 비짝 CI 폭 (L⁰ = <L⁰>)]' 한 줄만 쓰고 강건·민감 어느 쪽도 쓰지 않는다." 그리고 Q-OP 의 '1차와 같은 방향으로 0 을 배제하면' → 'L⁰ 와 같은 방향으로 0 을 배제하면', Q-K (2) 의 'L⁺ 가 **셋 모두** 1차 라벨과 같을 때만' → 'L⁺ 가 **셋 모두** L⁰ 와 같을 때만' 으로 교체; 공개 9 끝에 "한정어는 L⁰ (비짝) 기준이며 1차 라벨과 직접 비교하지 않는다 (§2.2)." 추가. (B) 는 추가 실행이 없다 — (a) 파일에 `R1 - R2` 줄이 이미 찍힌다 (frontier_ci.py:226).
- **M4** (§2.2 (T+)/(T−) 행 · §1 대체 규칙 F1)
  - 문제: (T±) 문장은 '(4 배)' 로 고정돼 있는데 F1 발동 시 D2 1차 대비는 R(6.4e5) − R(3.2e5) = 2 배다. §1 F1 은 '문장의 N′ 만 바뀜' 이라 동결된 문장 그대로면 배수가 틀린 채 기록된다.
  - 수정: §2.2 (T+)·(T−) 두 행의 '(4 배)' 를 '(<N_새/N_기준> 배)' 로 교체. §1 F1 의 '(Holm·라벨·한정어 규칙 그대로, 문장의 N′ 만 바뀜)' 을 '(Holm·라벨·한정어 규칙 그대로, 문장의 N′ 와 배수 (4 → 2) 만 바뀜)' 으로 교체.

### should
- §2.2 (T±) 문장 괄호 안에 '(각 끝 학습·적합 1 회, 시드·학습집합 분산 미반영)' 을 넣어 공개 3·5 를 문장 자체에 싣는다 — 짝 부트스트랩은 시행 재표본만 반영하고 양 끝은 독립 추출 집합의 단일 시행이다.
- §1 예산·학습 집합 행의 '스트림 7 의 앞 N′ 개' 는 같은 칸의 '앞부분으로 포함하지 않는다' 와 자기모순이다. '`sample_vecs(train_rng(…, 7), N′)` 가 뽑는 N′ 개 (배열별로 새로 뽑히므로 작은 N′ 집합의 확장이 아님, §0.5 prefix.log)' 로 고친다.
- `raw_K2NR16B16e4` 를 `~/t2_wtS/conf` 로의 절대 심볼릭 링크로 두는 대신 main 으로 복사 (`cp -r`, 삭제 없음) 하거나 main 에서 재실행 (약 15 분) 하고, (8) 에 `run_manifest.py --tag K2NR16B16e4` 를 넣어 192 파일·run|git 을 기록한다. raw 는 git 미추적 (`git ls-files raw_B32e4` = 0) 이라 worktree 제거 시 링크가 끊기고, 지금은 기록된 `K2NR16B16e4_accept.txt` 가 그 링크 대상이 같은 raw 라는 보증이 없다 (ABORT 로 끝나 오기록은 아니지만 Q-K C6 의 기준 끝이 사라진다).
- prep 의 D1 게이트는 `samplecx.csv` 의 같은 N_train 행이 여럿이면 마지막 행을 gate 로 쓴다 (run_nscale.sh:124-130). §5 에 어느 행 (epochs·attempt) 인지 적도록 §5 표 'D1 형제' 칸에 '(csv 행: epochs …)' 를 넣고, prep 는 행이 2 개 이상이면 경고 한 줄을 찍게 한다.

### verified
- 동일예산: `score.train` → `A.training_set(testbed, prior, Nr, Nt, ntrain)` (score.py:657), `fit_gpu.py` → `runner._sets(prior, Nr, Nt, ntrain)` (fit_gpu.py:29,113,124); GPU 큐는 적합·학습에 같은 N′ 을 넘기고 kron 8192 는 `gmm_fits_D2_K8B64e4` 로 격리 (run_nscale_gpu.sh). `run_d2_sx.py --tag` 는 fits 디렉터리만 바꾸고 stem 은 그대로 (run_d2_sx.py:56,71) → GB′ 재실행은 resume.
- 스크립트 플래그 ⊂ argparse: eval_accept (--ntrain/--kron-K/--ll-val/--n/--points/--ref-raw/--ref-arms/--fits-dir/--grid/--cand-dir/--nr/--prior/--bstar/--tag), recovery_ci (--raw/--cell/--snrs), guard_report (--raw/--testbed), run_manifest (--tag), runner run (--testbed/--prior/--cell/--ntrain/--stagec-ckpt/--n/--chunk/--snr/--arm/--tag), frontier_ci (--paired/--recovery/--pair/--level/--extrap/--ck/--rstar).
- `--paired` 출력 형식이 Holm 보조 정규식과 일치 (frontier_ci.py:326-331, nscale_reg/v_paired_C2_32v16.txt); p = min(1, 2·min(P[D≤0], P[D≥0])) (frontier_ci.py:100); 같은 셀·SNR·n·genie 비트 동일 assert (frontier_ci.py:310-312); `--extrap/--ck/--rstar need --recovery` (:372); `--level` 은 `--paired` 에서 미사용; `--extrap - -` 는 외삽 없음 출력 (:234-262).
- Holm 규칙 = SCALE16e4 §1 다중성 행 ((T-iv) p := 1, 동률 → 첫 셀, 첫째 95 %·둘째 90 %, (T0-Holm)); 라벨 (T+)/(T−)/(T0)/(T0-Holm)/(T-iv) 와 Q-K (2) 세 실행 문구 = SCALE16e4 §2.1; 보조 코드의 정렬 (bool(why), p, k != 'C2') 과 수준 배정이 그 규칙을 구현.
- P1 통과 조건 = B32e4 §1 원문 (POWERED 이고 second arm fewer ≥ 2/3; significant 토큰 무시); C6 (i)–(iv)·회수율 대역 = C6B16e4 §1·§2. `tables_D2_<T>.txt` 블록 형식 (tables_D2_B32e4.txt:368-373; analysis.py:448-454 POWERED/UNDECIDED 문자열) 이 p1 정규식과 일치, UNDECIDED 는 부호검정 줄이 없어 (iv) 로 떨어짐.
- 수용 (f): runner 는 `git -C conf rev-parse --short HEAD` (+dirty) 를 run|git 에 쓴다 (runner.py:471-476); 스크립트 H 도 conf 에서 같은 명령 → 비교 가능 (최근 raw 예: 'bafdf46a+dirty'). 기준 raw B32e4·NR16B16e4 에는 run|git 이 없지만 gitchk 는 새 raw 에만 적용.
- S5 파싱: 14 필드, `FALLBACK 1 ⇔ PT B128e4 -`, K8 줄, K2 `- - -` 규칙 (run_nscale.sh:205-237; fake_s5.txt 로 확인). 일괄 검사 출력 경로 `results/nr{nr}b_batched_check_S2_n<N>.txt` 와 VERDICT 줄 (em_batched_check_nr.py:69,83) = prep 가 읽는 경로. 병합 npz 에 `sparse_tol`·`kron_batched` 배열이 기록됨 (fit_gpu.py:73-75) → prep 의 경로 표기 가능. `samplecx.csv`·`d2_gbprime.csv` 머리말이 prep 의 열 이름과 일치.
- 대체 규칙 F1–F6 의 발동 근거는 검사·OOM·학습 종료·적합 종료만이고 BLER 을 보지 않는다; D1 형제 §3d 는 `run_samplecx.py` 2 번째 인자 (fallback 2/3) 로 구현 가능 (run_samplecx.py:16-18). P2 SNR 은 기준점 기록 판정점 −3/0/+3 으로 동결 전 고정, `_best` 끼리만 비교. (T0) 이 예상 결과이고 동등성 증거가 아님이 명시됨. 예측 1–17 은 수치 범위·이분으로 채점 가능.
- 공개 1–12 는 순차 선택·기준 결과 기지·시드 분산·시행 재사용·독립 추출 (prefix.log)·희소 대 일괄 경로·C6 fb2 대 시행 1·8192 보고 전용·SNR 고정·K 상한 교란·(E) 의 legacy-last V1 을 덮는다; 공개 9 만 M3 로 보정 필요. raw·fits 는 git 미추적 (`git ls-files` 0) — 링크 의존성은 should 3.

## 검토 — 관점 integ

### must
- **M1** (run_nscale.sh `lset` (:174–182) ↔ 문서 §1 태그·arm 행 "fits = kron 4096 과 그 후보를 뺀 링크 집합", §1 수용 (a), §1 실행 스크립트 행 `links`)
  - 문제: `lset` 이 `.k0r*` 후보 파일을 전부 건너뛰어 (:178 `case $f in *.k0r*) continue;; esac`) K2 링크 집합 `gmm_fits_D2_K2B32e4`·`gmm_fits_D2_K2<T>` 에 kron 1024·2048 후보가 없다. `eval_accept.py` 의 `--grid` 검사는 kron K ≥ 1024 마다 `--cand-dir`(기본 = `--fits-dir`) 에서 `.k0r*` 3 개를 요구하므로 (eval_accept.py:143–148 "grid: kron K=… has 0 candidate files, expected 3"), K2 수용 (:363, :379) 은 구조상 전부 FAIL → `qk` 가 두 셀 모두 강제 한정어 "[K 상한 민감: 외삽 불가]" 로 떨어진다 (:428–430). 결과와 무관한 스크립트 오류가 Q-K 라벨을 정한다. 선례 집합은 "K_max 파일과 그 후보만 뺀" 링크 집합이고 (SCALE16e4 §1 K2 행, §5 "kron 1024·2048 후보 각 3", `K2NR16B16e4_accept.txt` = OK 는 그 집합으로 통과한 것), 이 문서 §1 도 "kron 4096 과 그 후보를 뺀" 이라 쓰고 있어 스크립트가 문서와 선례 둘 다에 어긋난다.
  - 수정: run_nscale.sh :174–182 를 다음으로 바꾼다 (제외 정규식 `kronK4096_` 이 `fit_S2_Nr8_kronK4096_n…k0r0.npz` 후보도 함께 걸러낸다 — 확인함):
```
lset () {  # set-dir source-dir exclude-regex(or '') [extra-file]: per-file symlinks to EVERY fit file of source-dir (merged + .k0r* candidates;
           # eval_accept --grid looks for the kron K >= 1024 candidates in --fits-dir) except those matching the regex (K_max merged file AND its candidates)
  local D=results/gmm_fits_D2_$1 S=gmm_fits_D2_$2 f; shopt -s nullglob
  [ -n "$(echo results/$S/fit_*.npz)" ] || die "lset $1: no fit files in results/$S"; mkdir -p $D
  for f in results/$S/fit_*.npz; do
    [ -n "$3" ] && [[ $(basename $f) =~ $3 ]] && continue
    lnk ../$S/$(basename $f) $D/$(basename $f)
  done
  [ -z "$4" ] || lnk ../$4 $D/$(basename $4); }
```
문서 §1 실행 스크립트 행의 `links` 설명 "K2 링크 집합 `gmm_fits_D2_K2{B32e4, <T>}`" 뒤에 "(kron 4096 병합 파일과 그 후보만 뺀 **전체** 파일 링크 — 수용 (a) 가 kron 1024·2048 후보 3 개를 그 디렉터리에서 찾는다; SCALE16e4 ⑥ 과 같은 집합)" 를 넣는다. 대안(동등): :363 과 :379–380 의 K2 `acc` 호출에 `--cand-dir results/gmm_fits_D2_B32e4` / `--cand-dir results/gmm_fits_D2_$T` 를 더한다.
- **M2** (문서 §1 한정어 Q-K 행 "강제 한정어 … K2 구성 불가 (K/2 링크 집합의 b* 가 kron 2048 이 아님)" + §2.2 Q-K (1) ↔ run_nscale.sh `prep` (:107–114), 전제 검사 (:229–231), `qk` (:426–430))
  - 문제: 문서는 "b* = kron 4096 이지만 K/2 링크 집합의 b* 가 kron 2048 이 아님" 을 강제 한정어 조건으로 등록했는데 S5 형식이 이 경우를 표현하지 못한다. `prep` 은 그때 `K2_K K2_ll = - -` 를 쓰면서 c_K 는 값을 그대로 써서 DRAFT 줄이 `- - 2.0…` 이 되고, 전제 검사 :229 (`K2_K = -` 이면 `K2_ll c_K` 도 `- -`) 가 ABORT 한다. 주 세션이 c_K 를 손으로 `-` 로 고치면 `qk` 는 그 끝을 **내부 (b*⁺ = b*)** 로 취급해 `--extrap - <기준 K2> --ck - <기준 c_K>` 로 실행 (a) 를 돌리고 (b) 도 돌린다 — 강제 한정어 없음. 즉 같은 사실 (K2 구성 불가) 에 문서는 "[K 상한 민감: 외삽 불가]", 스크립트는 "[K 상한 강건]" 이 가능 → 사후 선택 여지. (선례 run_scale2.sh 도 같은 결함이지만 이 문서는 조건을 명시적으로 등록했다.)
  - 수정: run_nscale.sh :113–114 를 다음으로 (r·c_K 는 기록용으로 그대로 출력, S5 에는 세 필드 모두 `-`):
```
        cKr = cK                                   # r / c_K stay in the record line even when K2 cannot be built
        if ok2: K2K, K2LL = "2048", repr(b2[2])
        else:   K2K = K2LL = cK = "-"              # S5 '- - -' with b* = kron 4096 = K2 구성 불가 (§1 Q-K 강제 조건) -> qk forces the qualifier
        print(f"  Q-K: r {r!r} -> c_K {cKr};  K2 set b* = {b2[0]} {b2[1]} {b2[2]!r} -> {'kron 2048 OK' if ok2 else 'K2 구성 불가 (forced Q-K qualifier)'}")
```
:427–430 을 다음으로:
```
  G=$T,${T}chk,BR$6; [ "$K2K" = - ] || { E1=raw_K2$T; C1=$CKK; }
  if [ "$BS" = kron ] && [ "$KK" = 4096 ] && [ "$K2K" = - ]; then       # b* at the cap but no K/2 set: K2 구성 불가 (§1 Q-K 강제 조건)
    NOTE="# Q-K: [K 상한 민감: 외삽 불가] (forced, §2.2 Q-K (1): K2 구성 불가 -- b* = kron 4096 but the K/2 link set's b* is not kron 2048 -> run (a) without --extrap, no (b)(c))"; X=""
  elif ok $4 && { [ "$K2K" = - ] || ok K2$T; } && [ "$C1" != inf ]; then
    NOTE=""; X="--extrap $E1 $3 --ck $C1 $5"; G=$G,$4; [ "$K2K" = - ] || G=$G,K2$T
  else NOTE="# Q-K: [K 상한 민감: 외삽 불가] (forced, §2.2 Q-K (1): a K/2 acceptance failed or r >= 1 -> run (a) without --extrap, no (b)(c))"; X=""; fi
```
문서 §1 실행 스크립트 행의 S5 설명 `<K2_K|-> <K2_ll|-> <c_K|->` 뒤에 "(b* 가 kron 4096 인데 셋이 `-` 이면 K2 구성 불가 = Q-K 강제 한정어; b* 내부이면 같은 `- - -` 이지만 `<bstar> <kron_K>` 로 구별된다)" 를 넣고, §5 의 `nscale_s5.txt` 주석에도 같은 한 줄을 넣는다.

### should
- 비용 (§1 비용 행): 청크 1 개 실행은 워커 1 개로 돈다 (`jobs = min(cpu_count, tasks)`). SCALE16e4 §6 :445 의 `U28NR16B16e4chk` (11 arm, Nr 16, 청크 0) 가 18.8 분이었으므로 "bridge 2 개 ≈ 5 분", "chk ×3 ≈ 1–3 분씩" 은 과소다. 교체 문구: "bridge 2 개 ≈ 10–25 분씩 (워커 1 개; C6 14 arm 은 ≈ 25 분), chk ×3 ≈ 10–25 분씩 → 합 ≈ 7–9 h (F1 이면 ≈ 1.3 h 적음)". 나머지 CPU 추정은 선례 실측과 맞다 (B32e4 A 34.4 분, B32e4last 34.2 분, NR16B16e4 A 14 arm 249.1 분, U28NR16B16e4 A 11 arm 120.8 분, K2 12.1 분, last 44.2 분).
- §0.5 마지막 줄 "결과는 아직 없다" 와 §3 예측 1·§4.2 (1): 일괄 검사 3 개는 이미 끝났다 — `logs/nscale/bpass_nr8_n640000` (10-05 01:00 CDT), `bpass_nr16_n640000` (01:03), `bpass_nr8_n1280000` (01:07) 가 있고 `results/nr{8,16}b_batched_check_S2_n{640000,1280000}.txt` 의 VERDICT 는 셋 다 PASS 다 (exit 0 에서만 생성됨을 em_batched_check_nr.py:88 로 확인). 동결 때 §0.5 를 "세 검사 PASS ({{NOW}} 관측)" 로 고치고 F1 (i)·F4 는 발동 불가로 적는다 — 예측 1 은 동결 전에 이미 알려진 값이 되므로 §3 에서 빼거나 "이미 관측" 표시를 한다.
- §1 예산·학습 집합 행 "스트림 7 의 앞 N′ 개; 기존 N′ 집합을 앞부분으로 포함하지 않는다" 는 자기모순이다. `arms.training_set` 은 `gen.sample_vecs(train_rng(…, 7), ntrain)` 이고 §0.5 `prefix.log` 가 비중첩을 보였다. 교체: "스트림 7 에서 N′ 개를 새로 추출 (`D2Gen._draw` 가 n 마다 배열을 뽑는다; 기존 N′ 집합의 확장이 아니다, §0.5)".
- F5 "미완료 → K8 run 0": kron 8192 는 큐 우선순위 40 (격자 50 보다 뒤) 이라 "나머지 §5 입력이 모두 준비됐을 때 병합 없음" 은 큐 순서만으로도 거의 확실히 성립한다 → 사용자가 결정한 보고 전용 8192 가 스케줄 때문에 빠진다. 교체 제안: "F5 = OOM 또는 재시작 실패 (같은 시드 재실행 1 회 뒤에도) 일 때만 `K8 … 0`; 그 밖에는 §5 를 kron 8192 병합 뒤에 채운다 (추가 대기 ≈ 9–23 GPU·h, 임계 경로 아님)". 또 `prep` 의 OOM 검사 glob (:101) 이 `fit_K8B64e4_*.log` 를 보지 않으므로 `for pat in (f"logs/nscale/fit_{T}_*.log", *( ["logs/nscale/fit_K8B64e4_*.log"] if T == "B64e4" else []))` 로 넓힌다.
- GB′ 재실행 (§4.1 행, §1 수용 (h)): `prep` 은 `GMM b* =` 줄을 `logs/nscale/*.log` 에서만 찾는다 (:137). §4.1 에 로그 이름을 고정해 두는 것이 좋다 — 예: `run_d2_sx.py --ntrain 640000 --tag B64e4 > logs/nscale/gbprime_B64e4.log`, `… --tag B128e4 > logs/nscale/gbprime_B128e4.log`, `train_nr16.py --nr 16 --ntrain 640000 --fits-tag NR16B64e4 > logs/nscale/gbprime_NR16B64e4.log`. 재개 안전성은 확인됨 (score.train :955–958: 이미 멈춘 체크포인트는 "no epoch trained, cpath left untouched" → sha 불변; B32e4 선례와 같음). §5 GB′ 행에 "(last-EMA 가중치 `<stem>.pt` 기준, B32e4 선례)" 를 병기하면 좋다.
- Q-K 실행 (b)/(c) 에서 그 끝이 `-` (내부) 이면 그 실행은 외삽이 전혀 없는 비짝 1차 (`R1 - R2`) 와 같아지고, 비짝 CI 가 넓어 (T±) 1차에 대해 (T0) 이 나오면 §2.2 Q-K (2) 규칙상 "[K 상한 민감: 실행 (b) 의 b*⁺ 에서 (T0)]" 가 K 와 무관한 짝/비짝 차이로 붙는다. 제안: §2.2 Q-K (2) 에 "외삽이 있는 실행만 센다 (끝이 `-` 인 실행 (b)/(c) 는 'n/a: 내부' 로 기록)" 를 넣고 `qk` 에서 `[ "$E1" = - ] || fci … _qkN …`, `[ "$3" = - ] || fci … _qkB …` 로 건너뛴다 (예측 2 대로 두 끝이 모두 상한이면 영향 없음).
- S5 의 `K8` 줄이 없으면 `K8RUN` 이 빈 값이 되어 조용히 0 으로 처리된다 (:236–237, :354, :383). 전제 검사에 `[[ $K8RUN =~ ^[01]$ ]] || die "$S5: K8 <kron_K> <ll_val> <1|0> line missing"` 를 더한다.
- B64e4k8 는 K = 8192 를 수신기로 처음 돌리는 실행이다. 메모리는 문제가 아니다 (kron 8192 @ Nr 8 의 covs = 8192·64² complex128 ≈ 537 MB/워커 < C6 kron 4096 @ Nr 16 의 ≈ 1.07 GB/워커, 이미 192 워커로 돌았음) 이지만 §1 비용 행에 그 근거 한 줄을 적어 두면 `--worker-gb` 미사용 결정이 기록된다.

### verified
- 플래그 대조 (내가 다시 grep): runner.py `run`/`analysis` 의 `--testbed --prior --cell --ntrain --stagec-ckpt --n --chunk --snr --arm --tag` (:1201–1268); eval_accept.py `--tag(TAG:ROLE:SHA:CELLS) --ntrain --kron-K --ll-val --n --ref-raw --fits-dir --grid --cand-dir --nr --points --ref-arms --prior --bstar` (:46–63); frontier_ci.py `--pair --recovery --paired --level --extrap --ck --rstar` (:358–366), `--extrap/--ck/--rstar` 는 `--recovery` 필수 (:371–372); recovery_ci.py `--raw --cell --snrs` (:47–49); guard_report.py `--raw --testbed` (:81–82); run_manifest.py `--tag` (:37). 스크립트가 쓰는 플래그 중 없는 것은 없다.
- 이름 일치 (run_nscale_gpu.sh ↔ run_nscale.sh ↔ 코드): fit_gpu.py 는 `runner._init(tag)` 뒤 `arms.fit_path` = `results/gmm_fits_D2_<tag>/fit_S2_Nr<Nr>_<fam>K<K>_n<N>.npz`, 후보 `_cand_path` = `….k0r<r>.npz` (fit_gpu.py:88–89, :102–103; arms.py:66–69) → GPU 큐의 WAIT glob `fit_S2_Nr${nr}_kronK${K}_n$n.k0r[012].npz` 와 `prep` 의 glob/정규식과 일치. 체크포인트: run_d2_sx.py `d2sx_N{ntrain}_a{attempt}[_fb{k}]` (:63–67; `--tag` 는 fits 디렉터리만 바꾸고 stem 은 그대로, :54–56), train_nr16.py `d2sx_NR16_N{ntrain}_a1` (:54–57), run_samplecx.py `sx_N{N}_D1[_fb{k}]` (:22–23); 학습 로그 `logs/train_<stem>.log` ↔ `prep done()`; samplecx.csv 열 `N_train,epochs,…,GA,GB,GC,GD,…,passed`, d2_gbprime.csv 열 `ntrain,…,gmm_ntrain,equal_budget,…,gmm_bstar,gmm_K,…,ratio_min,ratio_max,ratio_median,worst_excess` ↔ prep 의 열 이름. em_batched_check_nr.py 출력 `results/nr{nr}b_batched_check_S2_n{N}.txt` (:68–69, `--nr 8` 또는 N ≠ 160000 이면 `_n<N>`), FAIL 이면 exit 1 (:88) → `bpass_*` 는 PASS 에서만 생긴다.
- kron 8192 격리: runner 는 `--tag` 로만 fits 디렉터리를 정한다 (`d_fits_d2()` = `gmm_fits_D2_<TAG>`, runner.py:94, :113); `gmm_selection` 은 있는 병합 파일만 읽는다 (arms.py:91–99; B32e4 에 8192 없이 통과). `B64e4`·`B64e4chk`·`B64e4last`(링크)·`K2B64e4`·GB′ 재실행 (`run_d2_sx.py --tag B64e4` → `A.D2_FITS = gmm_fits_D2_B64e4`) 은 `gmm_fits_D2_K8B64e4` 를 볼 수 없고, 8192 를 읽는 것은 링크 집합 태그 `B64e4k8` 뿐이다. GPU 큐의 K8 작업은 `fit_gpu.py 8 kron 8192 640000 K8B64e4` → `gmm_fits_D2_K8B64e4` 에만 쓴다 (`assert os.path.dirname(out) == d_fits_d2()`).
- 수용·재생 전제: 기준 raw `raw_B32e4`·`raw_NR16B16e4` (와 `raw_B16e4s3`·`raw_B1e4`·`raw_B32e4last`) 의 arm 은 똑같은 14 개 (M-ours-bstar, bstar-scalar, V0, V1, V4, V4b, gmm32, R0–R3, R4-llr, R4-scvamp, R5-genie) 라 bridge 의 기본 arm + `--ref-arms all` 이 잘 정의된다. eval_accept 는 참조 raw 의 `<arm>|KEYS_RAW` 전부를 공유 시행마다 비트 대조하고 (:111–131), chunk-0 태그 (`--n 40 --points C:-3`) 는 plan `[(0,40)]` 로 통과하는 구조다. 기준 raw 에는 `run|git` 키가 없지만 (DOP16e4 이전) `gitchk` 는 새 태그에만 걸린다; 새 raw 의 `run|git` 은 `git -C conf rev-parse --short HEAD`(+dirty: code/Demo) (runner.py:471–476) 로 스크립트의 `H` 와 같은 명령이다.
- 통계 배관: `frontier_ci --paired` 출력 형식 (frontier_ci.py:330–331, `v_paired_C2_32v16.txt`) 이 Holm 보조의 두 정규식과 맞고, 정의 불가 복제 > 100 (= 5 % of 2000)·ΣF_b* ≤ ΣF_g·ΣF_g ≥ ΣF_V1 가드가 코드에 있다; Holm 정렬 `(why, p, k != 'C2')` = (T-iv) 뒤·p 작은 쪽 먼저·동률 C2 가 문서 §1 다중성 행과 같다. 표 B 블록 형식 (tables_D2_B32e4.txt:368–373, :386–391 "power guard … -> POWERED", "second arm fewer failures at k/3 points, first arm fewer failures at j/3 points") 이 p1 파서와 맞다. `--extrap - - --ck - -` 는 argparse 가 받고 Q-K 줄 없이 끝난다 (CPU, B=5 건식 실행 rc 0).
- 실행 위치·커밋 규칙: `cd /home/HTJ/t2/conf`, `CUDA_VISIBLE_DEVICES=` 비움, flock, `pgrep -f 'code/runner.py run'` (SEEDSNR 의 wtS runner 명령줄과 일치), code/Demo 청결, 문서·DECISIONS·S5 추적+청결, HEAD = S5 를 마지막으로 바꾼 커밋, FREEZE 조상 + `git diff FREEZE HEAD -- code ../Demo` 비어 있음, `FALLBACK 1 ⇔ PT B128e4 -`, 14 필드·sha·격자 = `$GF`/`$GK`·gate 어휘·K2 조건·링크 존재, 기준 raw 448·`raw_K2NR16B16e4` 192·`raw_B16e4k`·`raw_B1e4` 448, 기존 NSCALE raw 없음(또는 --resume) — 모두 스크립트 :201–240 에 있고 문서 §1 실행 위치·실행 스크립트 행과 일치. `run()` 은 호출마다 HEAD 불변을 검사한다 (:250). :191 의 `A || B && C` 는 bash 좌결합이라 의도대로다.
- 재개 안전성: runner 는 끝난 청크를 건너뛴다 (runner.py:501–503 "FINISHED CHUNKS ARE SKIPPED"); `run()` 은 파일 수 = 기대치면 건너뛰고 rc 0 인데 수가 다르면 99 로 실패 처리; 사후 단계는 매번 다시 돈다. GB′ 재실행은 체크포인트를 건드리지 않는다 (score.train :955–958) 라 §5 의 sha 가 GB′ 전후로 같다. `links` 는 만들기만 하고 (`lnk`: 이미 있으면 같은 곳인지 확인, 다르면 ABORT) 지우지 않는다.
- `prep` 재현: 드래프터의 `t_prep.txt` 가 B32e4·NR16B16e4 의 §0.4 값 (ll_val 3 개, r, c_K 2.021371931572057 / 1, K2 집합 b* = kron 2048, sha 035744cbe955984d / c050d611b2c714a6, `# done` 줄, D1 게이트 PASS, GB′ 행) 을 그대로 내놓는 것을 확인했다 (스크래치 nscale_reg/, 커밋 안 함). 정지 사유 규칙 (cap500 / patience ≥ 40 / tol) 이 §0.4 표의 (221/180 patience, 163/160 tol) 과 일치.
- 메모리 가드: C6 kron 4096 @ Nr 16 은 NR16B16e4 (14 arm, 192 워커, 249.1 분) 와 같은 K·차원이라 `--worker-gb` 불필요가 맞다; K 8192 @ Nr 8 의 공분산 메모리는 그 절반이다. GPU 측은 §0.5 memprobe (80.70 / 79.52 GiB) 인용과 OOM grep (`logs/nscale/fit_<T>_*.log`) 으로 다룬다.
- 읽지 않은 것: `~/t2_wtS` 의 파일 내용 (gpuq.txt 줄 수만 `wc -l`), 모든 `*NR32_N160000_a3_fb3*`, SEEDSNR raw·로그, NSCALE 학습 로그·체크포인트 (존재와 mtime 만). BLER·GPU·커밋·삭제 없음; 건식 실행 1 회 (frontier_ci, CPU, B=5, 기존 raw).

