# 적대적 검토 B (실행 가능성·코드·사실 대조) — NEXT_EXPERIMENTS_D3B16e4.md · NEXT_EXPERIMENTS_SVB16e4.md (v1 초안)

- 검토: 2026-09-26 10:32 CDT, Claude Code (Fable 5.1), 적대적 검토 B. 읽기 전용(ckpt torch.load cpu, npz, 로그, sha256sum, 코드; `runner.py run` 미실행).
- 대조 원본: ckpt 4개, `results/gmm_fits_D2_{D3B16e4,SVB16e4}/` 전 파일(후보 .k0r* 포함), `d2_gbprime_{S2c,SV8e}.csv`, `sigma_grid_D2_{S2c,SV8e}.txt`, 학습 로그 2개, `testbed_{D3,SV}.txt`, `tables_D2_B16e4k.txt`, `recovery_B16e4k.txt`, `d2_gbprime.csv`, `logs/{d3,tb2,d3_post,tb2_post_SV8e}.log`, DECISIONS 14:06~18:50 KST, 코드 `run_prior_eval.sh`(33719007)·`eval_accept.py`·`frontier_ci.py`·`recovery_ci.py`·`runner.py`·`arms.py`·`analysis.py`·`Demo/t2_gmm.py`.

## 일치 확인(둘 다)
sha256[:16]·epoch·best_epoch·stopped_by·role·sigma_tag·prior·rung·best_val(4 ckpt), 격자 표의 K 별 ll_val·n_iter·it_best·재시작 번호·재시드(npz `n_reseed`)·경로(`kron_batched`) 전부, 병합 ll_val, GB′ csv 4 값, σ 격자 범위·시각·git, 학습 로그 머리말(split_hash·E‖H‖²·hp·시작 시각)·wall, testbed 수치, D2 비교값(실패 수·a:b·SNR@0.1 격차·회수율 3 점·대조군 61:95/30:44/9:10·1e4 GB′ 0.464·3.2e5 0.513/−0.121), D3 65.160 nat·gap 5.403·10.95·1.925 nat, SV 2.52 nat, 0단계 json 4e4/1.65e5/2000 — 모두 원본과 같다.

## NEXT_EXPERIMENTS_D3B16e4.md

1. **[반드시 고침] :40 §1 실행 명령에 9번째 인자(격자)가 없다.** `run_prior_eval.sh` 의 기본 GRID 는 `kron:…,2048` 까지(스크립트 :13). 문서 명령대로 부르면 수용 검사가 kron 4096 병합 파일·후보 3 개를 검사하지 않는다(통과는 하지만 §1 수용 검사 (a)·--grid 문자열과 어긋남). 수정: 명령 끝에 `"full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048,4096"` 을 붙인다.
2. **[반드시 고침] :38, :92 `aborted=False` / "aborted False".** ckpt 의 `aborted` 필드는 `None` 이다(두 ckpt 모두; 학습 로그 "# done" 줄만 `aborted=False`). 문구: "aborted 필드 None(설정되지 않음; 로그 done 줄 aborted=False)".
3. **[반드시 고침] :89 "kron 4096 세 후보 모두 … 학습 우도 tol 규칙으로 정지".** `t2_gmm.fit_gmm_em` 은 patience=40 반복(검증 10 반복마다; :136, :162) 또는 tol(:164) 또는 n_iter 로 멈춘다. r1 은 161/120 → it−best = 41 ≥ 40 → **patience 정지**. r0 (131/130)·r2 (200/190; 병합 후보) 만 tol 로 읽힌다. npz 에 정지 사유 필드가 없으므로 "정지 조건에서의 추론" 이라고 적고 r1 을 분리한다. (§1 :34 의 병합 후보 r2 서술은 그대로 맞다.)
4. **[고치는 편이 좋음] :38 "runner 가 prior·sigma_tag 불일치를 거부".** `runner.py:1201-1206` 은 **prior 불일치만** 거부한다(ckpt `prior` ≠ 실행 prior → sys.exit). sigma_tag 는 ckpt 에 저장된 값을 학습·GB′ 가 읽을 뿐 거부 검사가 없다. 문구 수정.
5. **[고치는 편이 좋음] :81, :95 GB′ 시각.** 파일 mtime `d2_gbprime_S2c.csv`·npz = 2026-09-26 18:30:47 KST = **04:30 CDT**; 04:50 CDT 는 DECISIONS 기록 시각. 격자 확정 근거는 병합 파일 mtime kron2048 17:49:39 / kron4096 17:49:55 KST (= 03:49 CDT) → "격자 확정 03:49 CDT < GB′ 04:30 CDT" 로 수용 (e) 를 적는다.
6. **[고치는 편이 좋음] :92 "21.4~21.6 s/epoch"** → 로그 평균 21.28 s/epoch (done 줄 21.282; epoch 별 20.9~22.2).
7. **[고치는 편이 좋음] §4 마지막 두 행·§5 마지막 행.** 선행 코드는 이미 커밋돼 있다: db038a10 (CELLS C7/C8 격자, eval_accept 인자, frontier_ci.py, run_prior_eval.sh, run_pareto_eval.sh), 33719007 (판정점을 analysis 표에서 파싱). 링크 `gmm_fits_D2_D3B16e4last → gmm_fits_D2_D3B16e4` 는 2026-09-27 00:23 KST (= 09-26 10:23 CDT) 생성됨. "구현 중/채움" 을 값으로 바꾼다.
8. [메모] :40 "`recovery_ci.py --cell C2 --snrs <판정점>`" — 스크립트(33719007)는 −3 dB 단독 + analysis 표(`tables_D2_<TAG>.txt` 의 `M-ours-bstar -> M-ours-dscore-C-V1` 블록)에서 읽은 판정점, 그리고 `frontier_ci.py --recovery` 를 −3 dB(best·last) + 판정점 대 D2 −3,0,3 으로 호출한다 → §1 기전 판독 행과 일치. 출력 `results/review_next/recovery_{TAG,TAGlast}.txt`, `recovery_diff_<TAG>.txt`, `<TAG>_accept.txt` — §6 에서 이 이름을 인용하면 된다.
9. [메모] 수용 (d) 자기 참조: `eval_accept.py --ref-raw raw_D3B16e4` 는 raw_D3B16e4 를 참조로 적재하므로 best 태그는 자명 통과, last 태그가 실질 검사 — 코드 동작 확인(:89-107). C6 선례와 같은 방식.
10. [메모] `git status --porcelain conf/code` 는 conf/code 만 보므로 results/ 의 미커밋 등록 문서는 ABORT 를 일으키지 않는다(현재 clean, HEAD 33719007). 링크 부재 ABORT 도 현재 해당 없음.
11. [메모] 비용 근거(B32e4 §6 34.4 분 @K=4096) 타당. tb2 큐의 CPU 사용은 38.901 채널 생성(단일 스레드 torch)이라 192 워커와의 경합은 작다 — 문구 유지 가능.
12. [메모] 라벨 (iv) :55 "n_d < 6 인 점 ≥ 2" 는 코드(powered = 판정점 3 이고 불일치 ≥ 6 인 점 ≥ 2)와 동치이나, SV 문서와 같은 문구("불일치 쌍 ≥ 6 인 점이 2 개 미만")로 통일하면 읽기 쉽다.

## NEXT_EXPERIMENTS_SVB16e4.md

1. **[반드시 고침] :79 §4 "fits 링크 미생성", §5 마지막 행.** 링크 `results/gmm_fits_D2_SVB16e4last → gmm_fits_D2_SVB16e4` 는 이미 있다(2026-09-27 00:23 KST = 09-26 10:23 CDT). 선행 코드 해시 db038a10·33719007 도 채운다(위 D3-7 과 같음).
2. **[반드시 고침] :47 라벨 (iv) 문구 "판정점 < 3 또는 n_d < 6 인 점 ≥ 2 미충족"** 은 두 가지로 읽힌다. 코드(`analysis.table_B`: powered = len(cand)==3 and (불일치 ≥ 6 인 점) ≥ 2) 대로 "판정점 < 3 또는 불일치 쌍 ≥ 6 인 점이 2 개 미만" 으로 쓴다.
3. **[고치는 편이 좋음] :90 "aborted = None(False)"** → "aborted 필드 None(설정되지 않음; 로그 done 줄 aborted=False)".
4. **[고치는 편이 좋음] 머리말 "사용자 결정: 2026-09-26 00:06 CDT (SV8e 선택 …)"** — DECISIONS 14:06 KST 는 "응답 시각은 기록되지 않았고 이 기록을 쓴 시각 00:06 CDT 직전" 이다. "기록 시각 00:06 CDT" 로 적는다(15:03·15:07 항목은 이미 "무렵" 으로 처리돼 있다).
5. **[고치는 편이 좋음] :32 실행 행 / :34 수용 검사 행에 출력 파일 이름을 적을 것**: 스크립트는 `results/review_next/SVB16e4_accept.txt`, `recovery_SVB16e4{,last}.txt`(−3 dB + 판정점), `recovery_diff_SVB16e4.txt`(best/last 대 D2 −3 dB, 판정점 대 D2 −3,0,3) 를 쓴다; §6 인용 대상.
6. [메모] 실행 명령(8 인자, kron_K '-' → `KARG` 비움)과 기본 격자 `…kron:…,2048` 은 문서 --grid 와 일치. `--bstar gmm256` 일 때 eval_accept 는 `meta|ll_val|gmm256` 을 읽고(arms.py:231 이 llv 전 키를 `ll_val|<k>` 로 기록) kron_K 검사를 건너뛴다(:79). `meta|kron_K` 는 `gmm_selection` 이 병합 파일만 적재하므로 2048 (4096 미병합) — 문서 예상값 맞음. `--grid` 에 4096 을 넣지 않은 것은 검사에 영향 없음(후보 파일 존재는 무해).
7. [메모] kron 4096 후보(51/10, 51/10, 61/20)는 EM patience 40 정지로 읽힌다(참고; 문서는 정지 사유를 주장하지 않음).
8. [메모] "학습 전 일관성 검사 미실행" 근거 확인: tb2.log 01:21 CDT `@train SV8e SVB16e4` 시작(병합 f954a946 직후), DECISIONS 에 실행 기록 없음, `results/review_next` 에 해당 파일 없음.
9. [메모] 파일럿 서술 "√Nt·U[:, :Tp]" 는 `common.make_pilots` 마지막 줄과 일치; 시행 스트림 시드에 pil 이 들어가지 않으므로 "시행 스트림은 다르다" 는 PID 차이 때문 — 문서 표현 그대로 맞다.
10. [메모] 재개 호출 시각 17:50:26 KST (로그 :270) — 문서 "17:50 KST" 일치. GB′ mtime 17:52:21 KST 일치.
11. [메모] SV_WARNING 은 `analysis.main` 이 raw 의 prior 집합에 SV8e 가 있으면 찍는다(:669-670) — 수용 (f) 성립 조건 확인.

## 코드 쪽에서 고쳐야 할 것
- `code/run_prior_eval.sh`: 기본 GRID 가 2048 까지라 D3 (4096 병합) 호출은 9번째 인자가 **필수** — 문서에 명시하거나(권고, 최소 변경), 스크립트가 `results/gmm_fits_D2_<TAG>` 의 병합 파일에서 격자를 유도하도록 바꾼다. 인자 누락 시 실패가 아니라 약한 검사로 통과하는 점이 함정.
- `code/eval_accept.py`: 자기 참조 `--ref-raw` 에서 best 태그 검사가 자명하다는 점을 도움말에 한 줄 적어 두면 §6 기록 감사 때 혼동이 없다(선택).
- 그 외 스크립트·인자·링크·git 상태는 두 문서의 실행 절차와 맞는다.
