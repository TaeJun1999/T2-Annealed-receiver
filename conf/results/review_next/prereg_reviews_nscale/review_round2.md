# NSCALE 등록 검토 원문 — 라운드 2 (워크플로 wf_d394d246-6da; 작성자 Opus 5.5, 검토자 Fable 5.1 두 관점)

## 작성자 보고

6개 반드시 항목을 NEXT_EXPERIMENTS_NSCALE.md 와 `run_nscale.sh` 에 모두 반영했고, 헤더에 검토 라운드 요약 bullet 을 넣었다. 커밋은 하지 않았다. `bash -n` 이 통과했고, 아래 확인은 모두 스크래치에서 단일 프로세스로 돌렸다 (GPU·BLER 안 씀, 삭제 없음, `{{NOW}}` 그대로).

**바뀐 곳**
- **stats-fair M1 + integ M1 (병합)**: 두 수정을 다 넣었다.
  - `lset` 이 이제 kron 4096 병합 파일과 그 후보만 빼고 후보까지 모든 파일을 링크한다 (integ M1 본안).
  - K2 수용 두 호출에 `--cand-dir results/gmm_fits_D2_B32e4` 와 `--cand-dir results/gmm_fits_D2_$T` 를 붙였다 (stats-fair M1).
  - 문서는 §1 수용 (a) 와 실행 스크립트 행의 `links` 설명을 고쳤다. stats-fair 문안의 "병합 파일만 담으므로" 는 integ M1 을 넣은 뒤 사실이 아니어서 "후보 6 개를 담는다" 로 바꿔 적었다.
- **stats-fair M2 + integ M2 (병합)**:
  - `prep` 은 K2 구성 불가일 때 S5 에 `- - -` 를 쓰고, r·c_K 는 기록 줄에 남긴다 (integ 문안, S5 출력은 stats-fair 와 같음).
  - `qk` 는 stats-fair 의 사유별 FORCE 구조에 integ 의 `BS = kron` 조건을 더했다. `FORCE` 는 `qk` 의 local 변수로 넣었다.
  - 스크립트 머리말의 S5 설명, 문서 §1 Q-K 행, 실행 스크립트 행의 S5 설명, §5 `nscale_s5.txt` 주석 줄을 같이 고쳤다.
- **stats-fair M3**: 택 (B) 로 했다. §2.2 한정어에 첫 하위 항목 "비짝 기준 L⁰" 를 넣고, Q-OP 와 Q-K (2) 의 비교 기준을 L⁰ 로 바꾸고, 공개 9 끝에 문장을 더했다.
  - (A) 는 커밋된 `frontier_ci.py` 를 바꿔야 해서 이번 범위 (문서와 스크립트) 밖이라 택하지 않았다.
  - 스크립트는 머리말 주석 한 줄만 바뀌었다.
- **stats-fair M4**: §2.2 (T+)·(T−) 의 배수를 '(<N_새/N_기준> 배)' 로, F1 을 '문장의 N′ 와 배수 (4 → 2) 만 바뀜' 으로 바꿨다.
- **헤더**: 제목과 상태를 v1 로 올렸고, 검토 라운드 표의 행을 채웠고, "1차 적대적 검토 반영" bullet 에 id 별로 바뀐 곳과 확인 결과를 적었다.

**확인 결과**
- 새 `lset K2B32e4 B32e4 kronK4096_` 는 링크 20 개를 만든다 (후보 6, kron 4096 계열 0, 원 디렉터리 24 파일). 두 번째 실행은 아무것도 바꾸지 않는다.
- 이 집합에 등록된 K2B32e4 수용 명령을 돌리면 `--cand-dir` 유무와 관계없이 격자 줄이 없다. 남은 FAILED 줄은 아직 없는 `raw_K2B32e4` 의 points 줄과 meta 줄뿐이다.
- 검토자의 병합 파일 14 개 집합에 `--cand-dir` 없이 돌리면 `grid: kron K=1024/2048 has 0 candidate files` 가 재현되고, `--cand-dir` 를 붙이면 사라진다.
- `qk` 를 가짜 S5·ACC 로 6 경우 돌렸다. 끝 + `- - -`, 기준 K2 수용 실패, 새 K2 수용 실패, c_K inf 네 경우만 사유별 강제 줄이 나오고 (b)(c) 를 돌리지 않는다. 내부 `- - -` 는 `--extrap - raw_K2B32e4` 로 정상 실행된다.
- `prep` 의 K2 블록을 가짜 ll 로 돌리면 K/2 집합 b* 가 kron 2048 일 때 `2048 <ll> <c_K>`, 아니면 `- - -` 가 나오고 기록 줄의 c_K 는 남는다.

**주 세션이 정할 것**: L⁰ ≠ 1차 라벨인데 동시에 Q-K 강제 조건 (예: K2 구성 불가) 이 걸리면 규칙이 서로 겹친다. M3 문안대로라면 '[한정어 판정 불가]' 한 줄만 쓰고 강제 문구 "[K 상한 민감: 외삽 불가]" 는 안 쓰게 된다. 어느 쪽이 우선인지 문서에 정해져 있지 않다. 강제 사유는 어느 경우든 `qk` 출력 파일 머리말에 남는다. 동결 전에 정할지 판단이 필요하다.

파일 (`/tmp/claude-1005/-home-HTJ-t2/6cbef450-8bb7-430d-b07a-4c32854f5588/scratchpad/nscale_reg/` 아래는 커밋하지 않는 스크래치):
- /home/HTJ/t2/conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md
- /home/HTJ/t2/conf/code/run_nscale.sh
- r2lset/ (lset 시험 트리)
- r2_k2accept_check.txt
- qk_test.sh

## 검토 — 관점 stats-fair

### must
- **stats-fair r2 M1** (NEXT_EXPERIMENTS_NSCALE.md §2.2 한정어 ("비짝 기준 L⁰" 하위 항목 마지막 문장, Q-K (1)) + §1 Q-K 행 강제 한정어 문장)
  - 문제: 두 규칙이 겹친다. §2.2 L⁰ 항목: "L⁰ ≠ 1차 라벨이면 Q-K·Q-OP 자리에 '[한정어 판정 불가 …]' 한 줄만 쓰고 강건·민감 어느 쪽도 쓰지 않는다". §2.2 Q-K (1)·§1 Q-K 행: 강제 조건(K2 구성 불가·K/2 수용 실패·r ≥ 1·분모 ≤ 0 복제 > 5 %·점 R⁺ 정의 불가)이면 "[K 상한 민감: 외삽 불가]" 를 **강제로** 붙인다. 1차가 (T±) 이고 L⁰ 가 (T0) 인데(비짝 SD 가 짝의 1.4–1.7 배라 (T±) 가 경계면 거의 항상) 동시에 강제 조건이 걸리면 전사자가 두 문구 중 하나를 결과를 본 뒤 고른다. 강제 사유는 BLER 전에 정해지는 적합·수용 사실이라 CI 폭(L⁰)과 무관하므로 우선순위를 지금 고정해야 한다. 스크립트(`qk`)는 강제 줄을 파일 머리말에 항상 쓰므로 코드 변경은 없다.
  - 수정: §2.2 L⁰ 항목의 마지막 문장을 다음으로 교체: "**L⁰ ≠ 1차 라벨이면** Q-OP 와 Q-K (2) 자리에 '[한정어 판정 불가: 비짝 CI 폭 (L⁰ = <L⁰>)]' 한 줄만 쓰고 강건·민감 어느 쪽도 쓰지 않는다. **Q-K (1) 의 강제 조건은 이 규칙보다 우선한다** (강제 사유는 §5·수용 파일의 적합·수용 사실이라 CI 폭과 무관): 강제 조건이면 L⁰ 와 관계없이 \"[K 상한 민감: 외삽 불가]\" 를 쓰고, L⁰ 줄은 보고 전용으로 병기한다." §2.2 Q-K (1) 을 다음으로 교체: "(1) 강제 조건 (§1 Q-K 행; `nscale_qk_<c>_L<L>.txt` 머리말의 `# Q-K: … (forced …)` 줄이 근거) 이면 **L⁰ 와 무관하게** \"[K 상한 민감: 외삽 불가]\" 를 강제로 붙인다." §1 Q-K 행의 "**강제 한정어 \"[K 상한 민감: 외삽 불가]\"**:" 뒤에 "(§2.2 의 L⁰ 규칙보다 우선)" 을 삽입.
- **stats-fair r2 M2** (NEXT_EXPERIMENTS_NSCALE.md §2.2 합성 문장 S_N (C2 조건))
  - 문제: S_N C2 의 조건 "새 점의 P1 이 모두 '통과' 일 때만" 과 같은 문장 안의 "<새 점이 FAIL 이면 그 점도 예산 축 측정>" 이 서로 어긋난다. §2.1 C2 표에서 D1 게이트 FAIL 점의 P1 기록은 (표 B 결과와 무관하게) "예산 축 측정" 이지 "통과" 가 아니므로, 새 점 하나가 게이트 FAIL 이면 한 읽기에서는 S_N 불성립, 다른 읽기(표 B 출력만 보고 게이트는 표기)에서는 성립이다 — 결과를 본 뒤 고를 수 있는 문장 조건. 1e4·4e4 (게이트 FAIL) 를 이미 '예산 축 측정' 으로 S_N 안에 세는 작성자 의도에 맞춰 표 B 출력 기준으로 고정해야 한다.
  - 수정: §2.2 S_N 의 "C2 — 새 점의 P1 이 모두 \"통과\" 일 때만" 을 다음으로 교체: "C2 — 새 점 각각의 표 B `b* → V1` 출력이 모두 '통과' (POWERED 이고 second arm fewer ≥ 2/3; **D1 게이트와 무관하게 표 B 출력으로만 판정**) 일 때만". 같은 문장의 "1.6e5 이상은 PASS 레시피<새 점이 FAIL 이면 그 점도 예산 축 측정>" 을 "1.6e5 이상은 PASS 레시피; 게이트 FAIL 인 새 점은 표 B 가 통과여도 '예산 축 측정' 으로 표기하고 arm 주장에는 쓰지 않는다 (§2.1 FAIL 행)" 로 교체. 끝의 "하나라도 아니면 개수 문장만 쓴다" 는 그대로.
- **stats-fair r2 M3** (NEXT_EXPERIMENTS_NSCALE.md §1 대체 규칙 F1 · §1 실행 위치·커밋 행 · run_nscale.sh eval 전제 (207행 뒤))
  - 문제: 대체 규칙 F1 은 (i)–(iv) 만 적고 '1.28e6 산출물 미완료' 를 정하지 않았고, 스크립트는 §5(S5) 재커밋 뒤 `--resume` 을 허용한다 (전제는 'HEAD = S5 를 마지막으로 건드린 커밋'·FREEZE 조상·코드 diff 없음·`FALLBACK ⇔ PT B128e4 -` 만 본다; `run` 은 완성된 raw 를 건너뛰고 (9) 단계는 매번 다시 돈다). 따라서 1.28e6 이 늦으면 S5 v1 `FALLBACK 1` 로 eval 을 돌려 B64e4 의 BLER·P2 를 본 뒤 S5 v2 `FALLBACK 0` + `PT B128e4 …` 를 커밋하고 `--resume` 하면 B128e4 만 추가로 돌고 1차 대비가 R(6.4e5)−R(3.2e5) 에서 R(1.28e6)−R(3.2e5) 로 바뀐다 — 결과를 본 뒤 대체 규칙(1차 대비)을 고르는 경로가 열려 있다. SCALE16e4 결정 7 (`scale2_s5.txt`·HEAD 불변) 에 해당하는 규칙과 검사가 없다.
  - 수정: §1 대체 규칙 F1 의 "(iv) …비정상 종료." 뒤에 삽입: "**미완료는 F1 사유가 아니다**: (i)–(iv) 가 F1 의 전부이며, 1.28e6 의 검사·적합·학습이 끝나기 전에는 §5 를 쓰지 않고 기다린다 (SEEDSNR16e4 종료로 CPU 가 비어도 같다). 바꾸려면 사용자 승인 + `DECISIONS.md` (등록 이탈로 기록)." §1 실행 위치·커밋 행의 "§5 커밋부터 `NSCALE_DONE` 까지 main 커밋 없음" 뒤에 삽입: "**§5 (S5·FALLBACK) 커밋은 한 번이다**: 첫 `eval` 시작 뒤 S5 를 바꾸지 않으며 `--resume` 은 같은 §5 커밋에서만 허용된다 (스크립트가 `logs/run_nscale.log` 의 첫 `start eval (git …)` 과 HEAD 를 대조; 다른 §5 커밋이면 ABORT, 새 §5 는 사용자 승인 + DECISIONS)." `run_nscale.sh` 207행 (`[ "$(git log -1 --format=%H -- $S5)" = … ] || die …`) 바로 뒤에 두 줄 삽입:
H0=$(grep -m1 -oE 'start eval \(git [0-9a-f]+' $L 2>/dev/null | awk '{print $4}')   # the §5 commit the FIRST eval started on
[ -z "$H0" ] || [[ "$(git rev-parse HEAD)" == "$H0"* ]] || die "an earlier eval started on §5 commit $H0 ($L); S5 / FALLBACK are fixed once BLER has started (--resume only on that commit; a new §5 needs user approval + DECISIONS)"
(머리말 `--resume` 설명에 "same §5 commit only" 추가.) 스니펫은 스크래치 `nscale_reg/r3guard` 에서 같은 접두 → 통과, 다른 해시 → ABORT 로 확인했다.

### should
- run_nscale.sh `why ()`: `fci` 가 수용 미통과로 SKIPPED 된 경우와 `frontier_ci.py` 자체가 rc≠0 (예: 출력 형식·SNR 누락) 인 경우를 모두 "수용 실패" 로 적어 (T-iv) 사유를 잘못 기록할 수 있다. 사유를 나누라: `why () { pt $1 || { echo "학습 실패 / 적합 실패 (§5)"; return; }; ok $2 $3 $4 || { echo "수용 실패"; return; }; [ "$5" = 0 ] || echo "정의 불가 (frontier_ci rc $5)"; }` 와 호출 `"$(why $N2 $N2 ${N2}chk BRB32e4 $RS2)"` / `"$(why NR16B64e4 NR16B64e4 NR16B64e4chk BRNR16B16e4 $RS6)"`.
- §3 예측 10·11·13 은 1.28e6 을 가리키는데 F1 이면 채점 대상이 바뀐다. 지금 고정: "F1 이면 예측 10 의 1.28e6 항·11 의 ΔR_C2·13 의 N2 는 6.4e5 로 읽고 범위는 그대로 채점한다 (또는 '채점 불가, 빗나감 아님')" 중 하나를 §3 머리말에 적을 것.
- `prep` D1 게이트: `samplecx.csv` 에 같은 `N_train` 행이 둘 이상이면 마지막 행이 조용히 게이트를 정한다; D1 형제가 §3d 를 타면 `run_samplecx.py` 는 `sx_N<N>_D1<sfx>.pt` 를 쓰는데 §1·S5 는 `sx_N<N>_D1.pt` 만 적는다. prep 이 행 수 > 1 이면 gate `?` 로 두고 전부 출력하게 하고, §5 표 'D1 형제' 행에 쓴 ckpt 파일명·sha256[:16] 을 추가할 것.
- §2.2 (T+)/(T−) 문장의 괄호에 "attempt 1 · 학습 집합 1 개 (공개 3·5)" 를 넣을 것 — N′ 에 대한 주장인데 CI 는 시행 재표본만 반영하고 G_N 에도 이 조건이 없다.
- 공개 9 에 한 문장 추가: "비짝 SD 가 짝의 1.4–1.7 배 (§0.3) 라 1차가 경계의 (T±) 이면 L⁰ = (T0) 로 '[한정어 판정 불가]' 가 예상되는 결과다" — 결과 뒤 해석으로 읽히지 않게 지금 적어 둔다.

### verified
- `frontier_ci.py main()` (370–378행): `--extrap/--ck/--rstar` 는 `--recovery` 없이는 argparse 오류 → §0.5·공개 9 (Q-K·Q-OP 비짝) 사실. `--extrap - - --ck - -` 는 통과하고 Q-K 줄이 없다 (`k2 = [None, None]`) → 내부 끝의 (b) 파일이 L⁰ 줄과 같다는 §1 문구 성립.
- Holm 보조 정규식 ↔ `cmd_paired` 출력 (326–331행: `R{j}: … b* {b} V1 {v} genie {g}  R = {r:.3f}`, `dR = R1 - R2 = … [90% paired …]  [95% paired …]  bootstrap two-sided p = …  undefined replicates N`) 토큰·공백 일치; 드래프터의 `v_paired_C2_32v16.txt` 실출력(ΔR −0.014, p 0.4860)과 §0.3 표 일치. `pct`/`ci_p` 는 정의 불가 복제를 걸러 백분위를 구하고 (94–104행) p = min(1, 2·min(P[≤0], P[≥0])) = §1 정의; 보조의 (T-iv) 가드 (ΣF_b* ≤ ΣF_g, genie 가드, 정의 불가 > 100/2000, p nan) = §1 가드 행.
- Holm 정렬 `(bool(why), p, k != 'C2')` = (T-iv) 는 둘째·p 작은 쪽 첫째·동률 C2 첫째; 첫째 95 %·둘째 90 %, 첫째가 (T±) 아니면 (T0-Holm) + 자체 90 % CI 보고 전용 = §1 다중성·§2.2 표.
- `eval_accept.py --cand-dir` 존재 (57행; 143–146행에서 kron K ≥ 1024 후보 3 개를 그 디렉터리에서 센다). `results/gmm_fits_D2_B32e4` 24 파일 중 후보 9 → `lset … 'kronK4096_'` 뒤 20 링크 (후보 6) 가 산술상 맞고 드래프터의 `r2lset` 트리에 후보 링크 6 개가 있다.
- `qk` 6 경우 시험 스크립트 (`nscale_reg/qk_test.sh`) 를 읽음: FORCE 분기 (BS = kron ∧ KK = 4096 ∧ K2K = '-' / 기준 K2 수용 실패 / 새 K2 수용 실패 / c_K inf) 와 비강제 분기의 `--extrap $E1 $3 --ck $C1 $5` 구성이 §1 Q-K 행 (a)(b)(c)·강제 조건과 일치; `FORCE` 는 `local`, `NOTE` 는 전역이라 `fci` 머리말에 찍힌다. `bash -n code/run_nscale.sh` 통과 (재확인).
- `p1` 정규식 ↔ `analysis.py` 448–450행 (`power guard: … -> POWERED`, `second arm fewer failures at k/3 points, first arm fewer failures at j/3 points`) 과 pair 머리줄 `"  {x} -> {y}        [decision-point anchor …"` 일치; C2 '통과' 규칙은 B32e4 §1 (33행) 그대로.
- `prep` 의 `bstar()` = `arms.gmm_selection` (full K 별 ll_val + kron 최대 ll_val 중 최대); `arms.D2_KS` 에 8192 포함 → kron 8192 를 별도 디렉터리 `gmm_fits_D2_K8B64e4` 에 두는 설계가 필요하고 GPU 큐 (`run_nscale_gpu.sh` 51–55행) 가 그렇게 쓴다. GPU 큐의 로그·파일명 (`logs/nscale/fit_<T>_kron<K>_r<r>.log`, `bpass_nr<Nr>_n<N>`, `results/nr{nr}b_batched_check_S2_n<N>.txt` — `em_batched_check_nr.py` 68–69행의 `_n{n}` 접미), 학습 stem (`run_d2_sx.py` 63·67행 `d2sx_N<N>_a<k>[_fb<j>]`, `run_samplecx.py` 23행 `sx_N<N>_D1<sfx>.pt`), `samplecx.csv` 열 (N_train,epochs,…,GA,GB,GC,GD,…,passed) 이 `prep` 의 glob·파싱과 맞는다.
- main 의 기준 입력: `raw_B32e4`·`raw_NR16B16e4`·`raw_B16e4k`·`raw_B1e4` 각 448 파일; `raw_K2NR16B16e4` 는 main 에 없고 `~/t2_wtS/conf/raw_K2NR16B16e4` 에 192 파일 (링크 대상 존재); `results/review_next/K2NR16B16e4_accept.txt` 는 main 추적 파일이고 첫 줄 `ACCEPT: OK -- K2NR16B16e4` → 스크립트 368행 grep 이 ACC=0 을 준다. 드래프터의 `t_prep.txt` 가 §0.4 의 ll_val·r·c_K·재시드·경로 (B32e4 kron 4096 sparse 1e-12, 2048 batched [0,0,1]) 와 ckpt sha (035744cbe955984d / c050d611b2c714a6) 를 재현한다.
- `runner._git_head` (471–476행) = `rev-parse --short HEAD` (+dirty) 이고 스크립트 `H` 도 `--short` → `gitchk` 의 `run|git == H` 비교가 같은 형식. eval 전제의 `[ "$1" = - ]`·14 필드·`FALLBACK ⇔ PT B128e4 -`·게이트 값 집합·K2 조건 검사는 S5 형식과 일치하며, B128e4 줄이 통째로 빠지면 14 필드 검사에서 ABORT 한다.
- 짝 부트스트랩 (`cmd_paired`): (셀, SNR) 마다 raw1 의 인덱스 한 번을 두 raw 에 같이 쓰고 n·genie 열 비트 동일을 assert → 같은 테스트 시행에 조건부인 추론이며 학습 집합·시드 분산은 들어가지 않는다 — 공개 3·5 가 이를 적고 있고 `prefix.log` 사실 (독립 추출) 과 모순 없음. Q-K (b)/(c) 의 최악 방향 서술 ((b) 새 끝 R 하향 = (T+) 최악, (c) 기준 끝 R 하향 = (T−) 최악) 은 R1 − R2 부호 관계상 맞다.

## 검토 — 관점 integ

### must
- **integ2-M1** (NEXT_EXPERIMENTS_NSCALE.md §2.2 한정어 첫 하위 항목 '비짝 기준 L⁰' (:159) 와 Q-K (1) (:161); run_nscale.sh 변경 없음)
  - 문제: L⁰ ≠ 1차 라벨인데 동시에 Q-K 강제 조건 (K2 구성 불가 / K/2 수용 실패 / r ≥ 1) 이 걸리면 두 규칙이 겹친다. :159 문안 ("Q-K·Q-OP 자리에 '[한정어 판정 불가 …]' 한 줄만 쓰고 강건·민감 어느 쪽도 쓰지 않는다") 대로면 강제 문구 "[K 상한 민감: 외삽 불가]" 를 쓰지 않고, :161 (1) 대로면 쓴다 — 어느 쪽을 쓰는지가 전사자 선택이 된다 (결과를 본 뒤 라벨을 고를 수 있음). 강제 사유는 BLER 전·수용 단계의 사실이라 L⁰ 가 필요 없고, 스크립트 (`qk`) 도 강제 줄을 L⁰ 와 무관하게 파일 머리말에 쓴다 (:436).
  - 수정: :159 의 마지막 문장을 다음으로 바꾼다: "**L⁰ ≠ 1차 라벨이면** Q-OP 와 Q-K (2) 자리에 '[한정어 판정 불가: 비짝 CI 폭 (L⁰ = <L⁰>)]' 한 줄을 쓰고 강건·민감 어느 쪽도 쓰지 않는다. **Q-K (1) 의 강제 한정어 \"[K 상한 민감: 외삽 불가]\" 는 L⁰ 와 무관하게 항상 붙인다** (강제 사유는 BLER 전·수용 단계의 사실이라 L⁰ 가 필요 없다; 그때는 두 줄이 함께 나온다 — `qk` 출력 파일 머리말의 `# Q-K: … (forced, …)` 줄이 근거)." :161 의 "(1) 강제 조건 (§1 Q-K 행) 이면 \"[K 상한 민감: 외삽 불가]\" 를 **강제로** 붙인다." 뒤에 "(L⁰ ≠ 1차 라벨이어도; 위 첫 항목)" 를 덧붙인다.
- **integ2-M2** (NEXT_EXPERIMENTS_NSCALE.md §5 `nscale_s5.txt` 전문 틀 (:270); run_nscale.sh 변경 없음)
  - 문제: 틀의 B128e4 줄 `PT B128e4    C2 1280000 <… 또는 '-' (F1)>` 는 F1 때 `PT B128e4 C2 1280000 -` 로 쓰라고 읽힌다. 스크립트는 셋째 필드 (`set -- $(s5 $T)` 의 `$1`) 가 '-' 인 줄만 실패 점으로 읽는다 (:225, :194, :247 `pt`): `PT B128e4 C2 1280000 -` 는 `$1`=C2 라 `[ $# -eq 14 ]` 에서 "PT B128e4 needs 14 fields (has 3)" ABORT 하고, 그 전에 `FBX` (:212 `s5 B128e4 | xargs` = 'C2 1280000 -' ≠ '-') 가 0 이 돼 `FALLBACK 1` 과 어긋나 ABORT 한다 (스크래치 하네스 `nscale_reg/fable_integ/pre_test.sh` 로 두 형식을 모두 확인: 등록 형식 `PT B128e4 -` 만 '-' 로 건너뛰고 FBX=1). CPU 창 시작 때의 전제 실패 = 일정 손실; 머리말 (:23) 과 §1 실행 스크립트 행 ("실패한 점은 `PT <tag> -`") 과도 어긋난다.
  - 수정: :270 을 두 줄로 바꾼다: "PT B128e4    C2 1280000 <stem> <best_sha16> <last_sha16> <bstar> <kron_K|-> <ll_val> 16,32,64,128,256,512 16,32,64,128,256,512,1024,2048,4096 <2048|-> <K2_ll|-> <c_K|-> <PASS|FAIL>" 과 "PT B128e4 -      (F1 이면 위 줄 대신 정확히 이 형식 — 스크립트는 셋째 필드가 '-' 인 줄만 실패 점으로 읽는다; `PT B128e4 C2 1280000 -` 는 14 필드 검사와 `FALLBACK 1 ⇔ PT B128e4 -` 검사에서 ABORT)". §5 표의 '대체 규칙' 행에도 "F1 이면 S5 는 `FALLBACK 1` + `PT B128e4 -`" 를 적는다.

### should
- §1 Q-K 행 강제 조건 다섯 가지 중 '분모 ≤ 0 복제 > 5 %'·'점 R⁺ 정의 불가' 는 실행 (a) 를 돌린 뒤에만 알 수 있어 스크립트의 `FORCE` (pre-run: K2 구성 불가·K/2 수용 실패·r ≥ 1) 가 아니라 `frontier_ci.py` 가 R⁺ 줄에 "[K 상한 민감: 외삽 불가]" 를 찍고 `R1+ - R2+` 를 'n/a' 로 쓰는 경로다 (cmd_recovery :243-:261); 이때 (b)(c) 도 돈다. 문장 "그때 (a) 는 `--extrap` 없이 (Q-OP 만), (b)(c) 는 돌리지 않고 파일 머리말에 강제 줄을 쓴다" 를 "앞 셋 (BLER 전·수용 단계) 이면 스크립트가 (a) 를 `--extrap` 없이 돌리고 (b)(c) 를 생략하며 머리말에 강제 줄을 쓴다; 뒤 둘은 (a) 파일의 R⁺ 줄 자체가 '[K 상한 민감: 외삽 불가]' 를 담고 `R1+ - R2+` 가 n/a 다 — 그 줄로 (1) 을 적용한다" 로 나눠 적을 것.
- eval 전제에 K2 링크 집합·K8 집합의 구성 검사 두 줄을 더하면 수용 (g) 가 CPU 실행 뒤에야 잡는 결함을 미리 막는다: `for d in K2B32e4 ${K2 있는 K2$T}; do [ -z "$(ls results/gmm_fits_D2_$d/*kronK4096_* 2>/dev/null)" ] || die; done` 과 `[ "$K8RUN" != 1 ] || [ -e results/gmm_fits_D2_B64e4k8/fit_S2_Nr8_kronK8192_n640000.npz ] || die`.
- GB′ 재실행 (§4.1 행) 의 로그 경로가 정해져 있지 않다. `prep` 의 "GB′ log lines @N=" 는 `logs/nscale/*.log` 만 grep 하므로 (:140) gpuq 줄을 `… > logs/nscale/gbp_<T>.log 2>&1` 로 고정해 적을 것 (안 그러면 §5 (h) 의 로그 근거가 'none' 이 되고 csv 만 남는다).
- §1 비용 행 "메모리 가드 불필요 (C6 K 4096 은 1.6e5 와 같은 K)" 는 B64e4k8 (b* = kron 8192, CPU 수신기로 처음) 을 다루지 않는다. 한 줄 추가: "B64e4k8 의 b* arm 은 K 8192 (C2 K 4096 의 2 배 성분; 1 TB·192 워커면 여유) — `--worker-gb` 없이 가고 첫 청크 RSS 를 §6 전사 때 적는다".
- `prep` 은 `PT B64e4 -` (B64e4 학습 실패) 여도 격자·8192 가 있으면 `DRAFT K8 … 1` 을 낸다; S5 작성자가 `K8 … 0` 으로 바꿔야 전제 (:240) 를 통과한다. §1 F5 에 "B64e4 점이 '-' 면 K8 run = 0" 한 구절 추가.
- `results/samplecx.csv` 에는 stem 열이 없어 같은 N_train 행이 여럿 (재개·재측정·§3d `_fb2`) 이면 `prep` 은 모두 출력하고 마지막 행의 게이트를 DRAFT 에 쓴다 (:127-:134). §1 자격 행에 "같은 N_train 행이 여럿이면 마지막 행 (최신 실행) 이 게이트; 전부 §5 에 전사" 를 적을 것.
- §0.5 "결과는 아직 없다" 와 §4.1 '진행 중' 은 이미 지났다: `logs/nscale/bpass_nr8_n640000`·`bpass_nr8_n1280000`·`bpass_nr16_n640000` 과 `results/nr8b_batched_check_S2_n{640000,1280000}.txt`·`nr16b_batched_check_S2_n640000.txt` 가 존재한다 (이 검토는 파일 존재만 봤고 내용은 열지 않음; exit 0 때만 생기는 bpass 셋 존재 = 세 검사 PASS). 동결 때 주 세션이 §0.5·§4.1·예측 1 의 지위 ('이미 알려진 값') 를 채울 것.
- 비용: C6 A (11 arm) 1.9–2.6 h 는 SCALE16e4 §1 이 같은 Nr 16·K 4096·11 arm 의 UMi28 C6 A 에 둔 3–5 h 추정보다 낮다. 추정 근거 (스모크 arm 비중) 는 적혀 있으니 "SCALE16e4 의 U28NR16B16e4 A 실측 (`~/t2_wtS/conf/logs/run_scale2.log`, SEEDSNR 종료 뒤 열람) 으로 동결 때 보정" 한 구절만 더할 것.
- `run_nscale.sh:47` `csv ()` 는 쓰이지 않는다 (무해; 지워도 된다).
- `results/review_next/prereg_reviews_nscale/` 가 아직 없다 — 동결 커밋에 검토 원문을 넣는다는 상태 줄과 맞추려면 주 세션이 만들어야 한다.

### verified
- `bash -n code/run_nscale.sh` 통과; 두 대상 파일은 미추적 (`?? conf/code/run_nscale.sh`, `?? conf/results/review_next/NEXT_EXPERIMENTS_NSCALE.md`), HEAD 5571b5d4. 커밋·GPU·BLER·삭제 없이 검토했고, 스크래치는 `nscale_reg/fable_integ/` (p2_test, holm.py, p1.py, gitchk.py, qk_*.txt, s5_fake.txt, pre_test.sh). `~/t2_wtS` 는 `raw_K2NR16B16e4`·`gmm_fits_D2_K2NR16B16e4` 의 `ls` 와 `gpuq.txt` 의 읽기 전용 grep 만 했다 (`*NR32_N160000_a3_fb3*` 미접근).
- 플래그 전부 존재 (argparse 대조): eval_accept.py `--tag(append, TAG:ROLE:SHA:CELLS) --ntrain --kron-K --ll-val(1e-9) --iters 16 --chunk 40 --n 2560 --ref-raw --fits-dir --grid --cand-dir --nr(기본 8) --points(CELL:s1,s2) --ref-arms --prior(기본 S2) --bstar(기본 kron)`; frontier_ci.py `--pair(nargs 2, append) --recovery(2) --paired(2) --level(float, 기본 0.90) --extrap(2) --ck(2) --rstar(float) --B --seed` 와 상수 `SEED, B = 20260926, 2000`, `REC_ARMS = (M-ours-bstar, M-ours-dscore-C-V1, R5-genie)`; runner.py run `--testbed --prior --cell --ntrain --stagec-ckpt --n --chunk --snr(nargs +, float) --arm(nargs +; --tag 필요) --tag`, analysis `--testbed --tag`; recovery_ci `--raw --cell --snrs(nargs +)` (B 2000, seed 20260926); guard_report `--raw --testbed`; run_manifest `--tag`. 음수 값 (`--snr -3`, `--ll-val -5.94…`) 은 선례 (run_b32e4_eval.sh, run_scale2.sh) 와 같은 형식.
- 이름이 run_nscale_gpu.sh (5571b5d4) 와 일치: `run_d2_sx.py --ntrain N --no-gbprime` → tag `N{N}_a1[_fb{k}]`, `ckpt/d2sx_N640000_a1.pt`·`_best.pt`, 로그 `logs/train_d2sx_N640000_a1.log` (prep `done(stem)` = `logs/train_{stem}.log` 와 일치); `train_nr16.py --nr 16` → `d2sx_NR16_N640000_a1` (`pre=''` for S2); `run_samplecx.py N` → `ckpt/sx_N{N}_D1.pt` (score.train 의 `ckpt` = role last 파일, gates_D1 이 그 파일을 잼) + `logs/train_sx_N{N}_D1.log` + `samplecx.csv` 열 `N_train,epochs,val_loss,GA,GB,GC,GD,GD_trace,gate_score,passed`; fits 디렉터리 `results/gmm_fits_D2_{B64e4,B128e4,NR16B64e4,K8B64e4}`, 파일 `fit_S2_Nr{nr}_{fam}K{K}_n{n}.npz` + 후보 `.k0r{r}.npz` (K ≥ 1024·8192 만; 16..512 는 all-in-one `_write_final` 로 같은 키 `kappa restart n_iter it_best n_reseed sec ll_val sparse_tol kron_batched`); 일괄 검사 출력 `results/nr{nr}b_batched_check_S2_n{n}.txt` 에 `VERDICT:` 줄; bpass 파일 = exit 0 때만; 84 작업 = 3+3+2 + 3×(9+3+6+6) + 4.
- K8 격리: `arms.load_fits` 는 `A.D2_FITS = results/gmm_fits_D2_<tag>` (runner._init: A.D2_FITS 와 TAG 만 바꿈; σ 격자는 ckpt 의 sigma_tag) 의 정확한 병합 파일명만 읽고 (`D2_KS` 에 8192 포함), `gmm_fits_D2_K8B64e4` 는 별도 디렉터리; 8192 파일을 담는 곳은 `lset B64e4k8` 집합뿐; GB′ 재실행 `run_d2_sx.py --tag B64e4` (B32e4 §4.1 선례와 같은 형식) 도 `gmm_fits_D2_B64e4` 만 읽는다. `lset K2* … 'kronK4096_'` 정규식은 4096 병합+후보만 뺀다 (B32e4 24 파일 → 20; t2_wtS K2NR16B16e4 = 20 파일로 같은 구성).
- 수용·재생: eval_accept `--ref-arms all` 은 기준 raw 청크의 모든 `<arm>|KEYS_RAW` 키를 비교하고 bridge 는 기본 arm 전부로 돈다; 호출마다 `common_meta (bstar, kron_K, em_sec)` 는 그 호출의 태그 하나뿐이라 K2/last/K8 집합의 em_sec 차이는 문제 없음; (f) `gitchk` 는 `run|git` 을 `git rev-parse --short HEAD` 와 비교하고 runner `_git_head` 도 같은 명령 (+dirty = code/Demo) — 기존 raw_B32e4 의 `run|git` 은 None 이라 (f) 가 새 raw 에만 걸리는 것을 실행으로 확인 (`(f) raw_B32e4: run|git ['None'] → FAILED`).
- Holm 보조 파서를 실제 `--paired` 출력 (raw_B32e4 vs raw_B16e4k, B 200, nice 19 단일 프로세스) 에 돌려 두 정규식이 맞는 것과 (T0)/(T-iv)/(T0-Holm) 분기를 확인 (`first C2: dR -0.014 [95% -0.052, +0.021] p 0.4000 -> (T0)`, 둘째 (T-iv)/(T0-Holm)). P1 보조를 `tables_D2_B32e4.txt`·`tables_D2_NR16B16e4.txt` 에 돌려 블록 6 줄·POWERED·k/3 파싱 확인. Q-K 실행 형식 `--extrap - - --ck - -` (R⁺ 줄 없음, `R1 - R2 … (--level 0.95)` 줄 있음) 과 `--extrap - raw_B16e4 --ck - 5.26 --rstar 0.05 --level 0.95` (R2+, `R1+ - R2+`, R*1/R*2) 를 B 100 으로 실행해 frontier_ci 가 받는 것을 확인.
- S5 파싱 하네스 (가짜 S5): 14 필드 검사, `PT <tag> -` 건너뛰기, `FALLBACK 1 ⇔ PT B128e4 -`, `$9/${10}` 격자 비교, gate case, K2 `- - -` + kron 4096 → `qk` 강제 조건 참, `pt()`, K8 줄 읽기 모두 의도대로 (잘못된 형식 `PT B128e4 C2 1280000 -` 는 ABORT → M2).
- 전제 입력 존재: `../Demo`; `raw_B32e4`·`raw_NR16B16e4`·`raw_B16e4k`·`raw_B1e4` 각 448 (C2/C6); `/home/HTJ/t2_wtS/conf/raw_K2NR16B16e4` 192 (목록만); `results/review_next/K2NR16B16e4_accept.txt` 첫 줄 `ACCEPT: OK -- K2NR16B16e4`; `gmm_fits_D2_B32e4` 24 (병합 15 + 후보 9), `gmm_fits_D2_NR16B16e4` 24; `flock pgrep sha256sum` 존재; `DECISIONS.md`·`results/review_next`·`results/nscale` 추적, `raw_*`·`results/gmm_fits_D2_*` 미추적 (무시 아님) — 전제는 code/Demo 와 세 파일만 보므로 링크 생성·새 raw 가 전제를 막지 않음. c_K 산술 재계산: B32e4 r = 1.850641241527015/2.766178462867444 = 0.66902 → 2.0214; NR16 r = 0.38163 → 1.
- 재개·커밋 규칙: runner 는 기존 청크 파일을 건너뜀 (runner.py:502); `run` 은 완성 raw 를 건너뛰고 호출마다 HEAD 불변 검사; 후처리 출력은 `>` 로 덮어씀; `flock` 잠금; 전제 `HEAD = S5 를 마지막으로 건드린 커밋`, `FREEZE` 조상 + `git diff FREEZE HEAD -- code ../Demo` 비어 있음, `pgrep -f 'code/runner.py run'` (SEEDSNR 포함) — 문서 §1 실행 위치·커밋 행과 일치. `K2B32e4` 수용의 `--grid "full:$GF kron:${GK%,*}"` = 2048 까지 + `--cand-dir results/gmm_fits_D2_B32e4`; 새 K2 는 `${KR%,*}` + `--cand-dir results/gmm_fits_D2_$T`.
- 문서 ↔ 스크립트 대조 (태그·arm·SNR·출력 파일명): A/chk/last/K2/bridge/B64e4k8 의 arm 목록·`--n/--chunk`·`--snr`·기대 파일 수 (448/1/192), 수용 호출의 인자 (A: 격자+`--ref-raw` 기준 raw; chk: `--n 40 --points <C>:-3 --ref-arms all`; last: role last, C6 `--points C6:-3,0,3`; K2: 2048·K/2 ll·3 점; bridge: 기준 sha·ll; K8: 8192·K8 ll), 출력 `nscale_P2_{C2,C6}.txt`·`nscale_P2_holm.txt`·`nscale_qk_{C}_L{95,90}{,_qkN,_qkB}.txt`·`nscale_S1/S2_C2`·`nscale_eff_C2`·`nscale_eff128_C2`·`nscale_K8_V1.txt`·`nscale_P1_<T>.txt`·`recovery_<T>{,last}.txt`·`guard_D2_<T>.txt`·`<key>_accept.txt`, 게이트 (P2 = A+chk+bridge, S2 = 두 A+chk, Q-K = +K2 두 끝, E = A+chk, K8 = B64e4k8+B64e4), 실행 순서 (1)–(9) 모두 일치. 비용 (CPU 6–8 h) 은 B32e4 ① 34.4 분 (EXPERIMENTS :35) 과 정합; GPU 쪽은 판정 합성안 그대로.

