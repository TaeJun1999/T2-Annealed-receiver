# SPARSE16e4 v2 재검토 원문 (Fable 5.1 서브에이전트, 워크플로 wf_f9ef9e37-276)
1회차 = v2 초안 대상, 2회차 = 1회차 반드시(M1·M2) 반영본 대상. 각 회차 앞에 검토 대상을 만든 작성자(Opus 5.5) 보고 원문.

## 1회차

### 검토 대상을 만든 작성자 보고 (원문)

등록 v2를 제자리에 작성했고 v1은 먼저 백업했습니다. 코드는 두 파일을 고쳤습니다. 작업하는 동안 v1 스크립트에서 수용 검사가 6 데이터셋 모두 실패했을 결함을 찾아 고쳤습니다. 커밋은 하지 않았고, main(`/home/HTJ/t2`)은 건드리지 않았으며, 튜닝 프로세스(pid 276838)는 계속 돌고 있습니다.

**파일**
- `/home/HTJ/t2_wtSBL/conf/results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md` — v2 (수정). `{{NOW}}` 2곳(머리말, §4 스모크 행)은 남겨 두었습니다.
- `/home/HTJ/t2_wtSBL/conf/results/review_next/prereg_reviews_2026-09-29/SPARSE16e4_v1.md` — v1 백업 (새 파일, 커밋 1c5ffa6c 판과 같음)
- `/home/HTJ/t2_wtSBL/conf/code/run_sparse16e4.sh` (수정)
- `/home/HTJ/t2_wtSBL/conf/code/eval_accept.py` (수정, 기본 동작은 그대로)

**v2에서 반영한 것 (검토 항목 → 바뀐 절)**
1. **반드시 1 (SNR 별 L·n_em):** `per_snr_pick` 규칙과 runner `--sparse-file`로 반영했습니다. §5 표를 데이터셋 × SNR 7로 바꿔 5개 C2 pick 값을 그대로 옮겼습니다. (§1 하이퍼파라미터·실행, §5.1)
2. **반드시 2 (EM 수렴 미달):** 검토의 (a)안인 MacKay 갱신을 택했고, n_em 격자는 {1,2,3,5,10,25,50}입니다. 격자 끝 규칙은 ALD16e4와 같게("한 축을 한 단계씩 최대 2회 확장") 맞췄습니다. §0 둘째 줄과 §3은 다시 썼고, 예측 내용은 v1과 같습니다. (§0, §1, §3, §5)
3. **반드시 3 (`meta|sparse` 수용):** 스크립트가 모든 청크의 `meta|sparse`를 그 SNR의 pick 값과 대조합니다. 실행 전에는 pick sha256[:16] 대조와, tune JSON에 규칙을 다시 적용했을 때 pick이 재현되는지를 검사합니다. (§1 수용)
4. **반드시 4 (비용):** 1 스레드로 실측해 다시 계산했습니다. 희소 arm만 C2 합계 약 30 CPU·h이고, C6는 pick에 따라 약 9–44, 최악 약 190 CPU·h입니다. runner에는 설계상 `--jobs`가 없으므로(01_RULES §4) "실행 중 다른 CPU 작업 없음"으로 적었습니다. 메모리 가드를 추가했습니다(OMP가 M×M 행렬을 만들어 C6 ρ 16이면 워커당 약 4.35 GB). C6의 ρ는 비용이 아니라 규칙이 정합니다. (§1 비용)
5. **반드시 5 (스모크 raw):** `raw_spsmoke`와 `gmm_fits_D2_spsmoke`가 워크트리와 main 어디에도 없음을 확인했습니다. 삭제 시각은 기록이 없습니다. (§4)
6. **반드시 6 (기존 출력):** 행마다 출력이 있으면 그 행을 ABORT합니다. v1의 `ls a* b*` 검사는 둘 중 하나만 있으면 rc 2가 나와 그냥 통과했는데, 이 결함도 고쳤습니다. 부분 raw가 있으면 resume 로그를 남깁니다. (§1 실행)
7. **새로 찾은 결함 (수용이 항상 실패):** SP 실행은 `--stagec-ckpt`를 넘기지 않아서 `meta|stagec_ckpt_id`가 raw에 없습니다. 그래서 `eval_accept --tag SP<suf>:<ROLE>:<SHA>:<cell>`은 "ckpt id … != sha"로 매번 실패했을 것입니다. `raw_B16e4k`로 같은 실패를 재현했습니다.
   - 고친 방법: `eval_accept`에 `ROLE = SHA = '-'` 규격을 추가했습니다(이 키가 **없어야** 통과). 스크립트는 `SP<suf>:-:-:<CELL>`을 넘깁니다.
   - 시험: 기존 규격은 종전대로 실패하고, `-:-`는 통과하며, 키가 있는 raw에 `-:-`를 쓰면 실패하는 것을 확인했습니다.
8. **튜닝 출처:** pick sha256[:16]은 S2 `2a6d79a23b6b6501`, S2c `afdb48498c76b88c`, SV8e `72a6500e72950141`, UMi28 `3d27f1bb72865fa5`, MIX3 `baffec3e463ad6b3`이고 tune 파일 sha도 §5.1에 적었습니다.
   - 5개 pick 모두 v2b 판이며 `v2b/` 사본과 바이트 동일합니다.
   - 여섯 튜닝은 09-29 20:49:14 CDT에 한 번에 시작했고, 그때 코드는 2381af57과 62ed179e 사이의 작업본입니다.
   - 62ed179e의 `per_snr_pick`을 tune JSON에 다시 적용하면 5개 pick이 `"rhos"` 키만 빼고 정확히 재현됩니다(끝 플래그 포함).
   - 끝 플래그: ρ는 16(격자 끝)입니다. SBL은 S2·S2c·SV8e·MIX3, OMP는 5개 모두이고, UMi28 SBL만 ρ 8로 내부입니다. SNR 별 끝 플래그는 모두 false입니다.
9. **ρ 32 중단 캐비엇 (§5.3):** 09-30 00:23 CDT에 시작해 09:28 CDT에 중단했습니다. SNR 하나에 약 6.4–6.8 h가 걸렸습니다. ρ 32의 NMSE는 저장되지도 열람되지도 않았습니다. 참고로 ρ 8 → 16 개선은 SBL ≤ 0.05 dB, OMP ≤ 0.20 dB, −3 dB에서 ≤ 0.08 dB입니다. ρ 16을 그대로 쓰고 라벨은 바꾸지 않으며, C6에도 같이 적용합니다.
10. **C6 규칙 (§5.2)과 게이트:** C6 pick은 진행 중인 튜닝이 쓰는 `results/sparse/pick_S2_C6.json` 그대로입니다. 실행 순서는 C2 5개 먼저, NR16 마지막입니다.
    - 게이트: pick이 main에 없으면 워크트리의 `tune_S2_C6.json`(pick 다음에 쓰임)을 10분 간격으로 기다렸다가 pick과 tune을 main으로 복사합니다. 튜닝 프로세스가 산출 없이 끝나면 NR16을 ABORT합니다.
    - 프로세스 확인 패턴은 `^[^ ]*python[^ ]* code/sparse_tune.py --prior S2 --cell C6`처럼 앞을 고정했습니다. 명령줄에 이 문자열을 인용만 하는 셸이 잡히지 않게 하려는 것입니다(모의 시험에서 이 문제가 실제로 났습니다).
    - 행 접미사 인자(예: `NR16`)로 일부 행만 다시 돌릴 수 있습니다.
11. **실행 위치 (§1 실행):** sbl → main 병합 뒤 main에서 돌리고, 동결 커밋은 병합 결과입니다. SPARSE_DONE까지(게이트 대기 포함) main 커밋은 금지입니다.
12. **권고 1–9:** 미채택 1·2·9는 해당 동작을 §2에 명시했습니다. 3·4·5·7·8은 문서에 반영했고, 6은 정의가 달라 예측이 아니라 보고 전용으로 넣었습니다.
13. **인자 대조:** `bash -n` 통과. 스크립트 인자를 runner, run_manifest, eval_accept, pair_baselines의 argparse와 맞춰 봤습니다. `git merge-tree` 기준 main 병합에 충돌이 없고, 수정한 두 파일도 main과 3-way 병합 시 충돌이 없습니다.

**남은 항목**
- **C6 pick 값과 sha는 아직 없습니다.** 튜닝은 +15 dB만 남았고, +12 dB가 10-01 07:11 KST에 끝났으니 앞 단계 기준 약 3–5 h 뒤입니다. 값은 §6에 추가로 적고 실행 뒤 커밋합니다.
- **C6 메모리:** pick이 ρ_OMP 16이면 가드 기준 필요량이 약 882 GB입니다. 지금 MemAvailable이 약 1025 GB라 여유가 적고, 부족하면 NR16 행이 ABORT되어 사용자 결정이 필요합니다.
- **C6 비용 범위:** pick이 나와야 확정되며, 최악은 약 190 CPU·h입니다.
- **main 세션 할 일:** 재검토 여부 결정, `{{NOW}}` 채우기, DECISIONS 줄 추가, 병합(= 동결) 커밋. 병합 커밋에 v2 코드 두 파일, pick·tune 5쌍, v1 백업이 들어가야 합니다.
- **남겨 둔 비효율:** OMP가 M×M `AᴴGA`를 만드는 부분이 비용과 메모리를 크게 먹습니다. 하지만 `arms.py`는 튜닝이 쓰는 파일이라 고치지 않았습니다.
- **`sparse_tune.py` 설명문:** 머리 docstring이 아직 v1 규칙(SNR 평균 한 값)을 적고 있습니다. 튜닝이 쓰는 파일이라 고치지 않았고, 튜닝이 끝난 뒤 고치면 됩니다.

### 렌즈 stats-fair

#### 반드시
- (없음)

#### 권고
- §5.3 캐비엇 보강 + SBL 만 2 회째 확장: ρ 32 의 비용은 전부 OMP 의 M×M(AᴴGA, M=32768 → 17 GB)이고 SBL 은 싸다 — 검토자 실측 `gamma_path` 50 단계 ρ 16 0.41 s / ρ 32 1.01 s (N 32, 2 스레드) → 256 샘플 × 7 SNR ≈ 0.5 h/데이터셋. 튜닝 종료 뒤 `sparse_tune.py` 에 `--omp-off` 를 두고 `--rhos 32 --merge-with` 로 SBL 만 규칙 2 회째를 완료하면 정보 있는 쌍 A1(SBL-loop)의 캐비엇이 사라진다. 안 하면 §5.3 에 두 문장을 추가: "SBL 단독 확장은 ≈ 0.5 h 였으나 하지 않았다" 와 "OMP ρ 32 는 테스트 실행 자체가 불가능하다 (C2 워커당 17 GB × 192 = 3.3 TB)".
- §1 실행 행 "실행 중 다른 CPU 작업 없음" → "(진행 중인 S2 C6 튜닝 pid 276838, 2 스레드 제외)" — C2 다섯 행이 도는 동안 그 프로세스가 살아 있는 것이 설계다.
- 예측 6 (`b* → SBL-loop`) 은 `pair_baselines` 가 내지 않는다 (`x → V1` 쌍만 출력, X* 도 V1 기준). 채점 명령을 §1 보고 전용 칸에 고정하거나 (예: `pair_baselines.table_b(data, cell, prior, snrs, 'M-ours-bstar', 'SBL-loop')` 한 줄 스크립트를 §4 에 적고 동결에 포함) 예측 6 을 "보고 전용, 채점 안 함" 으로 내릴 것 — 지금은 결과를 본 뒤 코드를 새로 써야 채점된다.
- C6 게이트의 규칙 재현 검사를 runner 가 읽는 키만 비교로: 튜닝 프로세스가 적재한 10:49 KST 작업본은 git 에 없고 (`sparse_tune.py` mtime 09-30 14:14:59 KST = 62ed179e 직전 편집) `edge_sbl` 의 하한 절(`g == min(grid)`)은 C2 pick 에 n_em 1 이 없어 시험할 수 없다 → C6 가 어느 SNR 에서 n_em 1 을 고르면 플래그만 달라 NR16 이 불필요하게 ABORT. 대체: `ok = (r['rho_sbl'], r['rho_omp']) == (pk['rho_sbl'], pk['rho_omp']) and all((r['per_snr'][s]['n_em'], r['per_snr'][s]['L']) == (pk['per_snr'][s]['n_em'], pk['per_snr'][s]['L']) for s in r['per_snr'])`. 같은 블록에서 tune 파일 sha256[:16] 도 함께 print (§6 기록용; C2 는 §5.1 에 있으나 C6 는 로그에 남을 곳이 없다).
- 동결 전 `--sparse-file` 경로 스모크 1 회 (개발 시행 2560.., n 8, 0 dB, `--tag spsmoke2`, 끝나면 raw·fits 링크 삭제·§4 기록): v1 스모크는 `--sparse-arms` 였고 `_sparse_at`·`meta|sparse` JSON·스크립트의 meta 대조 블록은 한 번도 실행되지 않았다 (검토자 코드 추적: 키 4 개·정수형·SNR 문자열 키 모두 일치하므로 실패는 예상하지 않으나, 실패하면 6 행 전부 INVALID → 재실행에 사용자 승인).
- §1 하이퍼파라미터 행 "희소 prior 는 cbar·N 만 읽음" → "cbar 와 eh2_prior (Cs 의 열별 전력; `t2_route_a.py` 326–327 의 초기 믿음·데이터 site 분산) 만 읽음" — 단위 전력 채널이라 ≈ 1 이지만 "데이터 없이" 문장의 정확한 근거가 된다 (Cinv 는 exact_prior 경로에서 안 읽음: 336·374 행).
- §1 실행 행에 한 줄: "`~/t2_wtSBL` 워크트리와 tmux `sparsetune` 은 `tune_S2_C6.json` 이 쓰일 때까지 지우지 않는다" (프로세스는 절대경로 C.CONF 에 makedirs 로 쓰므로 디렉터리 삭제는 복구되지만, `git worktree remove --force` 뒤의 상태를 규칙으로 막아 두는 편이 싸다).
- 메모리 가드 ABORT (C6 ρ_OMP 16: 필요 882 GB, 지금 MemAvailable 1024 GB) 의 허용 대응을 미리 적기: (a) MemAvailable 이 차면 같은 명령으로 재개; (b) OMP 를 지지집합 위 계산으로 바꾸는 코드 변경은 사용자 승인 + DECISIONS + C2 raw 의 OMP-pilot 키 비트 동일 확인 뒤에만 — 지금 문장 "규칙·pick 을 바꾸지 않는다" 는 코드 변경을 다루지 않는다.
- `sparse_tune.py` 정리는 튜닝 종료 뒤·동결 전에 (동결 커밋에 들어가는 파일): 머리 docstring 이 v1 규칙(SNR 평균 한 값, n_em/L 동률)을 적고 있고 `for fam in ():` 죽은 루프가 남아 있다 — 감사 때 규칙 문장이 두 가지로 읽힌다.

#### 확인
- 선택 규칙이 결과보다 앞선다: `per_snr_pick` (family 별 ρ = SNR 평균 최소, 그 ρ 에서 SNR 별 g 최소, 동률 → 작은 값) 은 2381af57 (09-30 09:53:39 KST) 에 있고, v2a pick (10:08–10:09 KST) 과 v2b 시작 (10:49:14 KST, 프로세스 lstart) 보다 앞선다. `git diff 2381af57 62ed179e -- sparse_tune.py` 는 격자 상수(v2a→v2b), `rhos=` 인자, 끝 플래그(구조상 N 제외·SBL 하한)·`edge_rho_*`·`rhos` 키, `--rhos/--merge-with` 만 바꿨고 규칙 본체는 같다.
- C2 pick 5 개는 스크립트의 재현 블록 그대로 검토자가 실행해 `rule-reproduced=True`, sha256[:16] = §5.1 (2a6d79a2…, afdb4849…, 72a6500e…, 3d27f1bb…, baffec3e…), `grid.rho` [1,2,4,8,16], n 256; pick·tune 10 파일은 `results/sparse/v2b/` 사본과 `cmp` 동일; mtime (14:03–14:21 KST) 과 `wall_sec` (11656–12745 s) 이 §5.1 표와 일치; 튜닝 로그의 pick 줄 = 파일 내용.
- §5.3 의 크기 주장 재계산 (tune JSON, SNR 별 최소의 SNR 평균): ρ 8→16 이득 SBL S2 0.051·S2c 0.038·나머지 ≤ 0.000 dB, −3 dB 0.000; OMP S2c 0.200·S2 0.122·나머지 ≤ 0.012, −3 dB ≤ 0.083 → "SBL ≤ 0.05, OMP ≤ 0.20 (D3), −3 dB ≤ 0.08" 정확. 끝 플래그: 35 칸 × 2 모두 false, `edge_rho_sbl` UMi28 만 false, `edge_rho_omp` 5/5 true.
- ρ 32 확장: `logs/sparse_ext.log` 09-30 00:23 CDT 시작 5 개, 09:28 CDT ABORTED 줄; 데이터셋 로그는 "−3 dB done (23092–24351 s)" 한 줄씩뿐, ρ 32 JSON 없음, tune 파일은 v2b 와 바이트 동일 → NMSE 미저장·미열람이 맞다.
- C6 튜닝: pid 276838 cmdline `…/bin/python code/sparse_tune.py --prior S2 --cell C6 --n 256`, lstart 09-30 10:49:14 KST, +12 dB done 73343 s (= 10-01 07:11 KST = 09-30 17:11 CDT); 앵커드 `pgrep -f '^[^ ]*python[^ ]* code/sparse_tune.py --prior S2 --cell C6'` 는 276838 만 잡고 문자열을 인용한 셸은 안 잡는다; 62ed179e 의 main() 은 pick 을 먼저, tune 을 뒤에 쓴다 (UMi28 mtime pick 14:07:06.6957 < tune .6997 로 적재본도 같은 순서).
- eval_accept `-:-` 규격과 runner 의 정합: `meta|stagec_ckpt_id` 는 `if stagec_ckpt:` 안에서만 쓰인다 (runner 391–393) → SP 실행에 없음; 원 규격은 `(key absent…)` 문자열에 sha 가 없어 항상 실패했을 것이 코드로 확인됨; 새 분기는 키가 있으면 실패. 3-way 병합 모의 (`git merge-file` base=merge-base, main, 워크트리): 충돌 0, py_compile 통과; main 쪽 변경은 `--skip0` (기본 0 → SP 청크 계획 불변); `run_sparse16e4.sh` 는 main 에서 변경 없음; 커밋된 sbl↔main `merge-tree` 충돌 없음.
- `meta|sparse` 대조: runner `_sparse_at` 는 `{rho_sbl, rho_omp, n_em, L}` 4 키를 `str(int(snr))` 로 골라 `json.dumps(sort_keys=True)` 로 `meta|sparse` 에 쓰고 (318–322, 447–448), `SPARSE` 전역은 Pool fork 전 main 에서 설정 (1293–1298; Linux fork); 스크립트는 파일명 `_snr(-?\d+)_` 로 pick 의 문자열 키를 찾아 같은 4 키 dict 와 비교 → 형·키 일치. 단 이 경로가 실제 실행된 적은 없음 (권고 5).
- `run|git` 의 dirty 판정은 `git status --porcelain code ../Demo` 만 본다 (runner 467–472) → 게이트가 `results/sparse/` 에 pick·tune 을 복사해도 NR16 raw 는 clean 커밋으로 남는다; `pair_baselines --provenance manifest` 는 run|git 이 있는 새 raw 에 "한 clean 커밋" 규칙을 적용 (139–141) → "SPARSE_DONE 까지 main 커밋 금지" 가 필요·충분.
- pair_baselines: `--add-baselines` 는 BL 끝에 붙고 (213) X* 는 `rows` (b* + BL) 최소 (271) → 새 arm 이 X* 후보; "전부" 조건은 `k == len(labs)` = 16 (277–279); `--expect` 는 `labs` 이름으로 대조하며 STATIC pairB 도 `R0-pilot@1` 이름을 쓴다. 스크립트 BL·NONI 열 = `pairB_ST*.txt` 재계산 라벨 (SV: b*·bstar-scalar·gmm32·V1-pilot (iv); NR16: V1-pilot (iv), b* (i); 나머지 4 개 전부 (i)).
- main 의 입력 존재: raw_PIL·raw_ALD 6 쌍, `results/ald/ald_PIL<suf>.npz`·`pilots_PIL<suf>_test.npz` 6 쌍, 기준 raw 6 개, `run_manifest_<base>.json` 6 개, fits 디렉터리 6 개; `raw_SP*`·`pairB_SP*`·`SP*_accept.txt` 없음; `raw_spsmoke`·`gmm_fits_D2_spsmoke` 는 워크트리·main 모두 없음; main 의 `results/sparse/` 는 아직 없다 (병합이 만든다).
- OMP 메모리 가드 식: `OMPSitePrior.hhat` 의 `AGA = A.conj().T @ G @ A` 가 유일한 M×M 객체 (complex128 16·M² B; 나머지는 N×M·M 벡터·L×L) → C2 ρ 16 1.07 GB, C6 ρ 16 4.29 GB/워커, 192 워커 기준 264 / 882 GB 가 맞다; 지금 MemAvailable 1024 GB. SBL 은 N×N Woodbury 만 (gamma 248–264).
- 스크립트: `bash -n` 통과; heredoc `T` 12 열 = `read` 12 변수; 루프 안 stdin 소비 명령은 모두 `< /dev/null` 또는 파일 입력; 행별 기존 출력 검사 `[ -n "$(ls a b 2>/dev/null)" ]` 는 한쪽만 있어도 잡는다; 행 접미사 필터 `[[ " $* " != *" $SUF "* ]]` 동작; NR16 행은 `PSHA=-` 로 sha 대조를 건너뛰고 재현·메모리 검사만 한다.
- 정적 라벨 인용 §0 = STATIC pairB SUMMARY-B (C2·D3·U28·MX (i) 12/12, b* (i); SV (i) 9 + b* (iv); NR16 (i) 11, V1-pilot (iv)) 과 일치; v1 백업 `SPARSE16e4_v1.md` 는 `git show 1c5ffa6c:…` 와 diff 0; `{{NOW}}` 2 곳 유지; ALD16e4 §1 의 규칙(점수 = SNR 평균의 단계 최솟값, 멈춤 단계 SNR 별, 끝 축 한 단계씩 최대 2 회)과 구조가 같아 파일럿 baseline 간 동등 대우가 성립하고, ρ 32 미완료만이 차이이며 §5.3 에 기록돼 있다.
- 검토자가 한 계산: 테스트 시행·개발 시행·BLER 어느 것도 계산하지 않음; 사설 시드 `default_rng([77,1,2,3])` 채널 1 개로 `gamma_path` 시간만 측정 (1 프로세스, 2 스레드, GPU 숨김); tune JSON 재집계와 스크립트 재현 블록(읽기 전용)을 워크트리에서 실행; main·튜닝 프로세스·arms/common/sparse_tune 무변경.

### 렌즈 integ

#### 반드시
- **[M1]** §4 선행 작업 (스모크 행) · §1 실행 — `code/run_sparse16e4.sh` 46–47행 (runner 호출)
  - 문제: 등록 명령의 runner 경로 `--sparse-file`(2381af57 에서 추가; `_sparse_at` + main 의 pick 적재 + `meta|sparse` SNR 별 기록)는 한 번도 끝까지 실행된 적이 없다. §4 의 스모크 문장("runner D2 C2 0 dB 개발 n = 8 — 세 arm raw 생성·유한·meta 기록")은 v1 그대로이고 v1 §4 는 그 스모크가 `--sparse-arms` 였다고 적는다. 워크트리·main 의 어느 로그에도 `sparse-file`·`spsmoke` 문자열이 없다 (`grep -rl` 0 건). 첫 행(D2 C2)에서 runner 가 실패하면 6 행 전부 ABORT 이고, 고치려면 동결 커밋을 다시 해야 한다 — 스크립트 실패·재동결 위험을 등록 전 몇 분의 개발 시행 스모크로 없앨 수 있다.
  - 수정: 동결 전, 워크트리(`~/t2_wtSBL/conf`, fits 있음)에서 등록 명령과 같은 모양으로 개발 시행 스모크를 한 번 돌리고 지운다:
`ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_spsmoke2; CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python code/runner.py run --testbed D2 --prior S2 --cell C2 --n 8 --chunk 8 --skip0 2560 --ntrain 160000 --sparse-file results/sparse/pick_S2_C2.json --arm SBL-loop SBL-pilot OMP-pilot R5-genie --tag spsmoke2 > logs/run_D2_spsmoke2.log 2>&1`
이어서 스크립트 55–63행의 `meta|sparse` 검사 블록을 `raw_spsmoke2 results/sparse/pick_S2_C2.json` 인자로 그대로 실행해 "0 mismatching chunks" 를 확인하고, `python -c "import numpy as np,glob; print([('meta|stagec_ckpt_id' in np.load(f).files) for f in glob.glob('raw_spsmoke2/*.npz')])"` 가 모두 False 임을 확인한다. BLER 값은 열지 않는다. 그 뒤 `rm -r raw_spsmoke2 results/gmm_fits_D2_spsmoke2 logs/run_D2_spsmoke2.log results/tables_D2_spsmoke2.txt results/guard_D2_spsmoke2.txt` (있는 것만).
§4 스모크 행을 다음으로 바꾼다:
| 스모크 (v1: `--sparse-arms`, D2 C2 0 dB 개발 n = 8 — raw 삭제; **v2: 등록 명령과 같은 `--sparse-file` + `--arm SBL-loop SBL-pilot OMP-pilot R5-genie`, D2 C2 개발 시행 2560..2567 n = 8, 7 SNR**) | v2 스모크 {{NOW}}: 세 arm raw 생성·유한, 모든 청크 `meta|sparse` = pick 의 그 SNR 값 (스크립트 검사 블록으로 확인), `meta|stagec_ckpt_id` 없음; BLER 미열람; `raw_spsmoke2/`·fits 링크·로그·tables/guard 삭제 (워크트리·main 부재 확인). v1 스모크 raw (`raw_spsmoke/`, `results/gmm_fits_D2_spsmoke`) 도 부재 (삭제 시각 기록 없음) |
- **[M2]** §1 실행·수용 (C6 게이트) · §5.2 — `code/run_sparse16e4.sh` 33–43행 (규칙 재현 파이썬 블록)
  - 문제: C6 pick 은 sha 로 고정되지 않고(PSHA `-`) 규칙 재현 검사만 받는데, 그 검사는 격자를 tune JSON 자신에게서 읽는다 (`rhos=t["grid"]["rho"]`). 저장소에는 ρ 32 확장을 돌려 `pick_/tune_<prior>_<cell>.json` 을 제자리에서 덮어쓰는 `code/run_sparse_ext.sh` (`sparse_tune --rhos 32 --merge-with`) 가 그대로 있다. 누가 C6 에 그것을 (또는 다른 `--n`) 돌리면 §5.2 의 "v2b 격자 한 판, 확장하지 않는다" 와 C2 와의 동등 취급이 깨진 pick 이 게이트를 통과하고 로그에는 rule-reproduced=True 만 남는다. C2 다섯은 sha 가 막지만 C6 는 아무것도 막지 않는다.
  - 수정: 스크립트 35행 `sp, cell = ...; t = json.load(...)` 바로 다음 줄에 추가:
`assert t["n"] == 256 and t["grid"] == dict(rho=[1, 2, 4, 8, 16], n_em=list(S.NEMS), L=list(S.LS)), f"tune grid/n != v2b (§5.2: one v2b pass, never extended): {t['grid']} n {t['n']}"   # C6 is not sha-pinned; run_sparse_ext.sh would overwrite the files in place`
(AssertionError → rc 1 → 그 행 "ABORT: pick not reproduced by the rule, or memory short" 경로; 33행 로그 문구를 `"$TAG ABORT: pick not reproduced by the rule / tune grid not v2b / memory short (see log)"` 로 바꾼다.) 다섯 C2 tune JSON 은 지금 이 검사를 통과한다 (n 256, ρ [1,2,4,8,16], n_em [1,2,3,5,10,25,50], L 끝 64 — 확인).
§1 실행 행의 "행마다 전제: 기존 출력 없음 (…), pick sha256[:16] = §5 (C2), 규칙 재현, 메모리 가드" 를 "행마다 전제: 기존 출력 없음 (…), pick sha256[:16] = §5 (C2), **tune JSON 의 n = 256 · 격자 = v2b (ρ {1,2,4,8,16}, n_em {1,…,50}, L {1,…,64}; C6 포함 — ρ 32 확장·다른 n 의 산출은 ABORT)**, 규칙 재현, 메모리 가드" 로 바꾼다. §5.2 첫 줄 끝에 "(스크립트가 tune JSON 의 n·격자가 v2b 인지 검사한다)" 를 덧붙인다.

#### 권고
- S1 게이트 경쟁 (27–28행): `while [ ! -f tune ] && pgrep …` 는 tune 파일이 `open("w")` 된 순간(쓰기 완료 전)에도 빠져나와 잘린 JSON 을 복사할 수 있다 (10 분 틱이라 확률은 매우 낮지만 결과는 NR16 ABORT). tune 은 마지막에 쓰이고 프로세스는 곧바로 끝나므로 조건을 `while pgrep -f "^[^ ]*python[^ ]* code/sparse_tune.py --prior S2 --cell C6" > /dev/null; do sleep 600; done` 로 바꾸고 그 뒤 `[ -f "$WT/${SP/pick_/tune_}" ] && cp …` 를 두면 경쟁이 없다.
- S2 알 수 없는 행 접미사 인자(예 `NR17`)는 조용히 0 행 실행 후 `SPARSE_DONE ok=0 fail=0` 을 남긴다. run_ald16e4.sh 처럼 17행 앞에 `for w in "$@"; do [[ " B16e4k D3 SV U28 MX NR16 " == *" $w "* ]] || { log "ABORT: unknown row '$w'"; exit 1; }; done` 를 둔다.
- S3 49행 `run_manifest.py` 의 rc 를 기록하지 않는다 (ALD 스크립트는 `log "$NAME run_manifest rc=$?"`). 같은 줄 끝에 `; log "$TAG run_manifest rc=$?"` 를 붙인다.
- S4 C6 튜닝이 동결 전에 끝나면 (≈ 3–5 h) 게이트 대신 고정하라: `pick_S2_C6.json`·`tune_S2_C6.json` 의 sha256[:16] 을 §5.2 에 적고 NR16 행의 PSHA `-` 를 그 값으로 바꾸어 동결 커밋에 넣는다 — 그러면 sha 없이 도는 데이터셋이 없어진다. 끝나지 않았으면 지금 문서대로 두고 §5.2 에 "동결 뒤 도착 시 스크립트 로그의 sha 를 §6 에 옮긴다" 는 이미 있는 문장으로 충분하다.
- S5 동결(병합) 커밋 대상에 `results/sparse/v2b/` (§5.1 "바이트 동일" 주장의 근거; 지금 untracked) 와 `logs/sparse_tune_*.log`·`logs/sparse_ext*.log` (§5.2·§5.3 이 인용; conf/logs 는 추적 대상인데 sparse 로그는 0 건 추적) 를 넣는다. 드래프터 목록(코드 2·pick/tune 5쌍·v1 백업)에는 빠져 있다.
- S6 §2 에 한 문장 명시: "SBL-loop 의 n_em 은 파일럿 전용 개발 NMSE 로 고른 값을 루프 안에서도 그대로 쓴다 (루프 가능도로는 튜닝하지 않았다)". 정보 있는 쌍 A1 의 baseline 이 다른 가능도로 튜닝된 손잡이 하나로 도는 점은 결과 전에 독자에게 보여야 한다 (지금은 §1 두 행을 합쳐 읽어야 보인다).
- S7 `sparse_tune.py` 머리 docstring 이 v1 규칙(SNR 평균 한 값)을 적고 있다 (드래프터도 인지). 튜닝 프로세스가 끝난 뒤 첫 커밋(동결이 그 뒤면 동결 커밋)에서 §1 의 `per_snr_pick` 규칙으로 고친다; 파일 편집은 실행 중 프로세스에 영향이 없지만 규칙대로 튜닝 종료 뒤에 한다.
- S8 게이트는 `WT=/home/HTJ/t2_wtSBL/conf` 를 하드코딩한다. §1 실행 행에 "SPARSE_DONE 전에는 sbl 워크트리를 지우지 않는다 (게이트가 거기서 읽는다)" 를 적는다.
- S9 메모리 가드가 NR16 을 ABORT 하면 문서는 "사용자 결정" 까지만 말한다. §3 7 항 또는 §1 비용 행에 재실행 명령 `bash code/run_sparse16e4.sh NR16` (다른 CPU 작업이 끝나 MemAvailable 이 충분할 때; 규칙·pick 불변) 을 적어 두면 결정 뒤 절차가 등록에 남는다.

#### 확인
- 인자 대조: 스크립트의 runner 인자 (--testbed --prior --cell --n --chunk --ntrain --sparse-file --arm --tag) = runner.py argparse (1181–1244, 1232); eval_accept (--prior --ntrain --bstar --kron-K --ll-val --ref-raw --tag) 존재; pair_baselines (--base --pil --ald --est --extra --add-baselines --cell --prior --r0 --provenance --expect-bstar --expect) = 107–123행; run_manifest --tag; `bash -n` 통과. 12 필드 `read` 와 6 행의 필드 수 일치; 행 순서 = 문서 순서 (C2 5 → NR16).
- pick 출처·sha: 다섯 C2 pick 의 sha256sum[:16] = §5.1 표 = 스크립트 PSHA 열 (2a6d79a23b6b6501 / afdb48498c76b88c / 72a6500e72950141 / 3d27f1bb72865fa5 / baffec3e463ad6b3); tune sha 5 개도 §5.1 과 일치; pick·tune 10 파일이 `results/sparse/v2b/` 사본과 `cmp` 동일; mtime 09-30 14:16/14:03/14:21/14:07/14:06 KST 와 wall_sec 12444/11656/12745/11872/11806 = §5.1.
- 규칙 재현: 62ed179e 의 `per_snr_pick(t["nmse_db"], C2, 32, rhos=grid.rho)` 가 다섯 tune JSON 에서 pick 파일을 `rhos` 키만 빼고 정확히 재현 (끝 플래그 포함); tune JSON 안의 `pick` == pick 파일; pick 에 `rhos` 키 없음 (2381af57–62ed179e 사이 작업본 산출, 드래프터 진술과 일치). 동률 규칙 (작은 ρ, 작은 g) 코드와 §1 문장 일치.
- 튜닝 값 재현성: 현재 arms.py·sparse_tune.py 로 S2 C2 ρ = 1 (7 SNR × n_em 7 × L 12) 을 다시 계산 → tune JSON 과 최대 차 0.000 dB (비트 동일); `SparsePrior.gamma()` == `gamma_path()[5]` (C2 ρ 4, 3 표본); arms.py 는 2381af57↔62ed179e 사이 불변 (diff --stat 에 없음), arms.py mtime 09-30 09:51:51 KST < 2381af57 커밋 09:53:39 < 여섯 튜닝 시작 10:49:14 (pid 276838 lstart). 스모크 raw 부재 (워크트리·main `raw_sp*`, `gmm_fits_D2_spsmoke` 없음).
- §5.1·§0·§5.3 수치 전사: 35 × 2 셀의 n_em/L 과 NMSE, ρ, 끝 플래그, SNR 평균이 pick JSON 과 일치 (SNR 별 edge 70 개 모두 false); §0 의 SBL−OMP SNR 평균 −1.01…−1.66 dB, −3 dB 차 0.10/0.00/1.41/1.50/1.03 dB; §5.3 의 ρ 8→16 개선 SBL ≤ 0.051, OMP D3 0.200·나머지 ≤ 0.122, −3 dB ≤ 0.083 dB — 모두 tune JSON 에서 재계산해 일치.
- ρ 32 중단 캐비엇: `logs/sparse_ext.log` 에 09-30 00:23 CDT 시작 5 건 + 09:28 CDT ABORTED 줄; `logs/sparse_ext_*.log` 는 "−3 dB done (23092–24351 s)" 한 줄씩뿐 — ρ 32 NMSE 는 어디에도 저장되지 않았고 `results/sparse/` 파일은 v2b 그대로 (ext 스크립트가 제자리 덮어쓰기하기 전 중단).
- C6 게이트·프로세스: pid 276838 `python code/sparse_tune.py --prior S2 --cell C6 --n 256` 은 C2 다섯과 같은 초(09-30 10:49:14 KST)에 시작, 로그 +12 dB done 10-01 07:11 KST (73343 s), +15 dB 진행 중; 앵커 패턴 `pgrep -f "^[^ ]*python[^ ]* code/sparse_tune.py --prior S2 --cell C6"` 는 276838 만 반환 (앵커 없는 패턴은 문자열을 인용한 내 셸도 잡았다 — 드래프터 진술 재현). 62ed179e 의 main() 은 pick 을 먼저, tune 을 나중에 쓴다 (게이트 전제).
- eval_accept `-:-` 규격: runner 는 `meta|stagec_ckpt_id` 를 `if stagec_ckpt:` 안에서만 쓴다 (runner.py:393) → SP 실행(--stagec-ckpt 없음)에는 키가 없고 종전 규격은 반드시 실패, 새 규격은 키 부재를 요구; 기본 경로(role/sha 지정) 코드는 그대로. 워크트리 eval_accept.py 를 main 판(--skip0 추가)과 `git merge-file` 3-way → 충돌 0; `git merge-tree --write-tree main sbl` 충돌 0; pair_baselines 의 sbl 변경은 `--add-baselines` 추가·BL/miss/len 세 줄뿐.
- run|git·커밋 규칙: `_git_head()` 는 code/·Demo 만 dirty 판정 (runner.py:472) → main 의 수정된 추적 로그(conf/logs 1183 파일 추적)는 raw 의 run|git 을 오염시키지 않는다; 스크립트 전제 검사도 같은 경로 + 등록 문서·DECISIONS tracked+clean. pair_baselines `--provenance manifest` 는 run|git 있는 SP raw 를 "한 clean 커밋" 규칙으로 검사 (139–142행).
- 라벨 대조: 스크립트 EXPARMS 12 개·NONI·BL = STATIC16e4 §6.1 (SV8e b* (iv) + bstar-scalar·gmm32·V1-pilot (iv); C6 V1-pilot (iv); 나머지 전부 (i), D2 C2 V1-pilot (i) 2/3); `labs` 는 (BSTAR,)+BL 로 키가 잡혀 `R0-pilot@1`·`--add-baselines` 3 개가 포함; extra raw 의 dup 검사는 GENIE 제외, genie 4 키 = base 검사 있음.
- 튜닝의 테스트 시행 비접촉: sparse_tune 스트림 `[20260930, TBID, PID, Nr, snr+100]` (시행 `[20260926, …, T, Tp, …]`); 어떤 raw 도 읽지 않음; ρ 32 확장도 같은 개발 스트림. v1 백업 `SPARSE16e4_v1.md` 는 1c5ffa6c 판과 `cmp` 동일; `{{NOW}}` 2 곳.
- 행별 기존 출력 검사 `[ -n "$(ls a b 2>/dev/null)" ]` 는 둘 중 하나만 있어도 ABORT (v1 결함 해소); 메모리 가드 식 = 문서 (C2 ρ16 264 GB, C6 ρ16 882 GB; cpu_count 192, 지금 MemAvailable 1028 GB, load ≈ 10); runner 풀 = min(cpu_count, tasks 448) = 192, `--jobs` 없음; start method 미지정(fork) 이라 main 에서 세운 SPARSE 전역이 워커에 전달 (v1 `--sparse-arms` 스모크와 같은 경로); runner 는 pick 의 `rho_sbl, rho_omp, per_snr` 만 적재 (1297–1298행).

## 2회차

### 검토 대상을 만든 작성자 보고 (원문)

M1과 M2를 모두 문서와 스크립트에 반영했지만, M1의 v2 스모크는 아직 실행하지 않았습니다. 이번 작업 규칙이 수신기 BLER 실행을 금지하고 CPU는 단일 프로세스만 허용하기 때문입니다. runner는 7개 워커로 BLER을 계산하므로 동결 전에 메인 세션이 돌려야 합니다. 커밋은 하지 않았고 tmux `sparsetune`은 계속 돌고 있습니다(C6 +15 dB 남음). arms.py·common.py·sparse_tune.py와 /home/HTJ/t2, /home/HTJ/t2_wtS는 건드리지 않았습니다.

**수정한 파일**
- /home/HTJ/t2_wtSBL/conf/code/run_sparse16e4.sh
  - M2의 assert를 규칙 재현 블록의 35행 바로 뒤(36행)에 그대로 넣었습니다.
  - 33행 ABORT 로그 문구를 `pick not reproduced by the rule / tune grid not v2b / memory short (see log)`로 바꿨습니다.
  - 한 줄이 늘어서 `meta|sparse` 검사 블록은 이제 56–64행입니다. `bash -n`은 통과합니다.
- /home/HTJ/t2_wtSBL/conf/results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md
  - 머리말 작성 줄에 "v2 재검토 (렌즈 integ, 반드시 2) 반영 ({{NOW}})"를 넣었습니다.
  - 작성 시점 공개의 스모크 문장을 v1(`--sparse-arms`)과 v2(`--sparse-file`, 7 SNR, BLER 미열람·삭제)로 나눴습니다.
  - 요약 표 뒤에 v2 재검토 요약 줄을 새로 넣었습니다(M1, M2, 확인 내용).
  - §1 실행 행과 §5.2 첫 줄은 M2 fix 문구 그대로 고쳤습니다.
  - §4
    - 코드 행에 있던 스모크 문장을 "v1, `--sparse-arms`"로 표시했습니다.
    - 스모크 행 제목은 M1 fix 그대로 바꿨습니다. 상태 칸은 **"v2 스모크: 대기 — 동결 전 필수"**로 두고, 통과 뒤 넣을 fix 문구를 칸 안에 적어 두었습니다.
    - v2 코드 행에 M2 검사와 그 확인 결과를 더했습니다.
    - 표 아래에 "v2 스모크 절차" 네 단계를 붙였습니다.
  - `{{NOW}}`는 모두 4개입니다(머리말 2, 요약 줄 1, 스모크 칸 1).

**확인한 것 (단일 프로세스, GPU 숨김, 수신기 없음)**
- **M2, 정상 파일:** C2 tune JSON 다섯 개가 새 assert를 통과합니다. 추출한 게이트 블록을 단독으로 돌리면 다섯 개 모두 규칙 재현 True이고, sha256[:16]이 §5.1 값과 같습니다. 메모리는 필요 약 264 GB, 가용 약 1024 GB입니다.
- **M2, 모의 파일:** ρ 32를 더한 모의 tune과 n 128 모의 tune은 AssertionError(rc 1)로 막힙니다. 모의 파일은 지웠습니다.
- **M1, 부분 확인:** 다섯 C2 pick을 runner 방식으로 적재해 `_sparse_at`으로 `meta|sparse`를 만들면, 스크립트 검사의 기대값과 35칸 모두 일치합니다. 이것은 전체 스모크를 대신하지 않습니다.

**메인 세션이 할 일 (동결 전, `~/t2_wtSBL/conf`, 문서 §4 표 아래 절차 그대로)**
1. `ln -sfn gmm_fits_D2_B16e4k results/gmm_fits_D2_spsmoke2; CUDA_VISIBLE_DEVICES= ~/miniforge3/envs/torch/bin/python code/runner.py run --testbed D2 --prior S2 --cell C2 --n 8 --chunk 8 --skip0 2560 --ntrain 160000 --sparse-file results/sparse/pick_S2_C2.json --arm SBL-loop SBL-pilot OMP-pilot R5-genie --tag spsmoke2 > logs/run_D2_spsmoke2.log 2>&1`
2. 청크가 7개인지 먼저 봅니다. 검사 블록은 빈 폴더에서도 0 불일치로 통과하기 때문입니다. 이어서 `sed -n '/^import sys, json, glob, re, numpy/,/mismatching chunks/p' code/run_sparse16e4.sh | python - raw_spsmoke2 results/sparse/pick_S2_C2.json`로 "0 mismatching chunks"를 확인합니다.
3. `meta|stagec_ckpt_id`가 모두 없는지(모두 False) 봅니다. 세 arm의 키가 있고 nmse가 유한한지도 봅니다. 이 검사는 True/False만 출력합니다.
4. `rm -r …`로 지우고, 워크트리와 main 양쪽에 남은 것이 없는지 확인합니다. 그다음 §4 스모크 행의 상태 칸을 적어 둔 문구로 바꾸고 `{{NOW}}`를 채웁니다.

**남은 빈칸**
- 재검토 원문 파일의 경로, 검토 모델, 권고 수를 몰라서 문서에 적지 않았습니다. 필요하면 요약 줄에 추가해 주세요.

### 렌즈 stats-fair

#### 반드시
- **[M1]** §4 표 '커밋 대상' 행 (NEXT_EXPERIMENTS_SPARSE16e4.md 64행) + §5.1 첫 단락 (76행)
  - 문제: v2b 의 pick·tune 다섯 쌍 (`results/sparse/{pick,tune}_{S2,S2c,SV8e,UMi28,MIX3}_C2.json`), `results/sparse/v2b/` 사본, `logs/sparse_tune_*_C2.log`·`logs/sparse_ext*.log` 가 워크트리에서 **미추적**이다 (`git -C /home/HTJ/t2_wtSBL status`: 전부 `??`; `git ls-files conf/results/sparse` 는 v1_em·v2a 15 개만). v1 의 문장 "튜닝 파일 `results/sparse/tune_<prior>_<cell>.json` (브랜치 sbl, 동결 커밋에 포함)" 이 v2 에서 빠졌고, §4 커밋 대상 행은 실행 **뒤** 파일만 적는다. `run_sparse16e4.sh` 는 main 에서 행마다 pick (31·32 행) 과 tune (35 행) 을 읽으므로 병합에 빠지면 C2 다섯 행이 모두 `pick file … missing (§5)` ABORT 이고, §5.1 의 sha 표는 기록에 없는 파일을 가리킨다 (재현 불가).
  - 수정: 64 행을 다음으로 바꾼다: `| 커밋 대상 — **동결 커밋 (sbl → main 병합에 포함, 현재 미추적)**: \`results/sparse/{pick,tune}_{S2,S2c,SV8e,UMi28,MIX3}_C2.json\` (sha = §5.1 표), \`results/sparse/v2b/\` 사본, \`logs/sparse_tune_{S2,S2c,SV8e,UMi28,MIX3}_C2.log\`·\`logs/sparse_ext*.log\`; **실행 뒤** (선례와 같이): \`raw_SP*\`, \`results/review_next/{SP*_accept.txt, pairB_SP*.txt, run_manifest_SP*.json}\`, \`results/sparse/{pick,tune}_S2_C6.json\` (게이트가 복사) + \`logs/sparse_tune_S2_C6.log\` | 동결 전 \`git add\` (스크립트가 main 에서 읽는다) / 실행 뒤 대기 |`. 76 행 끝에 덧붙인다: `다섯 쌍과 \`v2b/\` 사본·튜닝 로그는 동결 커밋에 들어간다 (스크립트가 main 의 파일을 읽고 sha 를 대조한다).`

#### 권고
- S1 (공정성·원고 범위, §2 + §1 보고 전용): SBL-loop 의 n_em 은 파일럿 전용 NMSE 로 SNR 별 튜닝됐지만 루프에서는 데이터 열이 더해져 유효 SNR 이 높다. 튜닝 표로 본 상한: pick 의 −3 dB n_em 을 더 높은 SNR 에 쓰면 D2 C2 +0.27 dB (n_em 5 vs 10 @+15), D3 +0.85 dB (3 vs 10 @+15), SV8e·UMi28·MIX3 ≤ 0.15 dB 손해 — V1 쪽으로 기우는 방향. §2 에 한 문장 추가: "n_em 은 파일럿 전용 개발 NMSE 로 고른 값을 루프에도 그대로 쓴다 (루프 전용 튜닝 없음; 튜닝 표 기준 최대 ≈ 0.3 dB, D3 +15 dB 0.85 dB 손해 가능)", §1 보고 전용에 "SBL-loop NMSE@16 − SBL-pilot NMSE@1" 추가.
- S2 (동등 처리, §1 수용 + 스크립트 56–63 행): 새 arm 의 예외 시행은 `pair_baselines.fails` 가 실패로 센다 (01_RULES §4) 반면 PIL/ALD arm 은 `failed().any()` → 무결성 실패(라벨 없음). §1 수용 행에 "새 arm 의 예외 시행 = 실패 (01_RULES §4; PIL/ALD 와 달리 무효 처리하지 않음), 개수는 로그·§6 에 기록" 을 적고, meta|sparse 검사 블록 print 줄 앞에 `ex = {a: int(sum(np.nansum(np.load(f)[a+'|failed']) for f in glob.glob(f'{raw}/*.npz') if a+'|failed' in np.load(f).files)) for a in ('SBL-loop','SBL-pilot','OMP-pilot')}; print(f'[sparse] raised trials {ex}')` 를 넣는다 (보고 전용, 판정 불변).
- S3 (스크립트 27–29 행, C6 게이트 경쟁): `sparse_tune.py` 는 pick → tune 순서로 쓰고 tune 은 `open(...,'w')` 직후 `-f` 가 참이므로 게이트가 쓰다 만 tune 을 복사할 수 있다 (확률은 낮으나 그러면 assert 가 JSON 오류로 ABORT 하고 main 에 잘린 파일이 남아 `NR16` 재개도 게이트를 건너뛴다). 29 행 조건을 완료 표식으로 바꾼다: `[ -f "$WT/${SP/pick_/tune_}" ] && grep -q '^\[sparse_tune\] pick ' $WT/logs/sparse_tune_S2_C6.log && cp …` (sparse_tune 108 행이 tune 저장 뒤 찍는 줄); 27 행 while 조건에도 같은 grep 을 넣는다.
- S4 (스크립트 41 행 + §5.2): 규칙 재현 블록은 pick sha 만 찍는다 — C6 는 sha 고정이 없으므로 tune sha 도 같이 찍어 §6 에 두 값을 옮길 수 있게 한다 (`print` 에 `tune sha256[:16]=…` 추가). 튜닝이 동결 **전에** 끝나면 §5.2 의 "동결 커밋에 들어가지 않는다" 가 틀리게 되므로 그 경우 pick·tune 을 동결 커밋에 넣고 표 77 행 PSHA 와 §5.2 에 sha 를 채운다고 한 줄 적는다.
- S5 (§2 원고 문장): OMP 의 L = N (= 임의의 독립 N atom 위 LS = G⁻¹b) 가 SV8e·UMi28 ≥ +3 dB, MIX3 ≥ +6 dB, D2 C2 +15 dB 에서 골라졌다 (§0 에는 있음) — §2 에 "고 SNR 에서 OMP-pilot 은 LS-pilot 과 같다" 를 넣어 원고가 '희소 복원' 을 과장하지 않게 한다.
- S6 (§4 v2 스모크 절차 1·4 단계): runner 는 stdout 에 청크별 blk_err 평균을 찍으므로 (runner.py 605 행) `logs/run_D2_spsmoke2.log` 에 새 arm 의 개발 BLER 이 남는다 — 4 단계에서 지우는 것은 맞으나 "로그는 열지 않는다 (실패 시에만 오류 줄 grep)" 를 절차에 명시.
- S7 (머리말·요약 줄): v2 재검토 원문의 경로·모델·권고 수가 비어 있다 (작성자 보고) — 메인 세션이 이 검토를 저장한 경로 (`prereg_reviews_2026-09-29/review_SPARSE16e4_v2.md` 등) 와 "Fable 5.1, 반드시 1·권고 7" 로 채운다.

#### 확인
- 규칙 재현: 다섯 C2 tune JSON 에 62ed179e 의 `per_snr_pick` 을 다시 적용하면 pick 과 ("rhos" 제외) 정확히 일치, `tune['pick'] == pick`, grid == v2b (ρ [1,2,4,8,16], n_em NEMS, L LS), n = 256; pick sha256[:16] 2a6d79a2…/afdb4849…/72a6500e…/3d27f1bb…/baffec3e… 와 tune sha 6f1e19bd…/42b07801…/1b737191…/40999752…/b02e6aca… 가 §5.1 표·스크립트 PSHA 와 모두 같다 (단일 프로세스, 수신기 없음).
- 끝 플래그: 35 칸 × 2 의 `edge_sbl`·`edge_omp` 전부 false; `edge_rho_sbl` D2 C2·D3·SV8e·MIX3 true, UMi28 false (ρ 8); `edge_rho_omp` 다섯 모두 true — §5.1·§5.3 문장과 일치.
- §5.3 포화 수치: ρ 8 → 16 SNR 평균 개선 SBL +0.051/+0.038/0/0/0 dB (S2/S2c/SV8e/UMi28/MIX3), OMP +0.122/+0.200/+0.012/+0.003/+0.012; −3 dB SBL 0, OMP ≤ +0.083 → "SBL ≤ 0.05, OMP ≤ 0.20 (D3), 나머지 ≤ 0.12, −3 dB ≤ 0.08" 성립. §0 의 SBL−OMP 평균 차 1.32/1.17/1.01/1.51/1.66 dB (1.0–1.7), −3 dB 0.10/0.005/1.41/1.50/1.03 dB 일치.
- 튜닝 경로 = 실행 경로: `gamma_path(stops)` 와 `SparsePrior(n_em).gamma()` 가 C2 ρ 16·ρ 8, C6 ρ 8, n_em 2·3·5·10 에서 비트 동일 (사설 시드 채널 1 개, 0 dB).
- C6 튜닝 코드 판: `arms.py`·`common.py` 는 2381af57 이후 diff 없음 (arms.py mtime 09-30 09:51 KST, 커밋 09:53 KST) < C6 프로세스 시작 `ps lstart` 09-30 10:49:14 KST; `sparse_tune.py` mtime 14:14 KST (시작 뒤) 이고 62ed179e 의 변경은 sparse_tune.py·run_sparse_ext.sh·v2a 파일뿐 → 진행 중 C6 는 MacKay 판 arms.py + 62ed179e 직전 sparse_tune.py (doc §5.1 출처 확인 문장과 일치). C6 셀 = Nr 16·Nt 4 (N 64), SNR 7 개 = C2 와 같음.
- ρ 32 확장: `logs/sparse_ext_{S2,S2c,SV8e,UMi28,MIX3}.log` 각 1 줄 ("-3 dB done (23806 s)" 류) — NMSE 값 없음; `sparse_ext.log` 에 09-30 00:23 CDT 시작·09:28 CDT ABORTED 기록 — §5.3 서술과 일치.
- 스크립트 (`/home/HTJ/t2_wtSBL/conf/code/run_sparse16e4.sh`): `bash -n` 통과; pgrep 앵커 패턴이 pid 276838 (`…/python code/sparse_tune.py --prior S2 --cell C6 --n 256`) 만 잡고 bash 래퍼 276835·패턴을 인용한 셸은 잡지 않음; runner·run_manifest·eval_accept·pair_baselines 모두 `< /dev/null` (while-read 의 heredoc stdin 을 소비하지 않음); 행별 출력 존재 ABORT (`ls a b 2>/dev/null` → 한쪽만 있어도 잡힘); 규칙 재현 블록은 eval_accept 뒤가 아니라 실행 전, meta|sparse 블록은 eval_accept (점 집합·청크 계획 검사) 뒤 → 실제 실행에서 빈 raw 통과 불가; 메모리 가드 need = 192 × (16·(256·32)²/1e9 + 0.3) = 264 GB, MemAvailable 현재 1027 GB; OMP `hhat` 은 M×M complex128 하나 (`A.conj().T @ G @ A`) 만 만들므로 16·M² B 식이 정점과 맞고 pool = min(192, 448 태스크) = 192 = cpu_count.
- eval_accept 변경: `tag:-:-:cells` 분기가 `meta|stagec_ckpt_id` 존재 시에만 실패, 그 외 기존 경로 불변; `--bstar gmm256` (SV) 에서 kron_K 미검사·`meta|ll_val|gmm256` 검사; BS/KK/LL 6 행이 `run_ald16e4.sh` DS 표와 동일; `--ref-raw raw_<TAG>` 로 R5-genie 4 키 비트 대조 + pair_baselines 가 extra raw 의 genie 4 키·시행 수 2560 을 다시 검사.
- 라벨 대조: STATIC16e4 pairB_ST*.txt — B16e4k·D3·U28·MX 는 12 개 (i) + b* (i); NR16 은 V1-pilot (iv) 나머지 (i) + b* (i); SV 는 b*-scalar·gmm32·V1-pilot (iv) + b* (iv) → 스크립트 EXPARMS(12)·NONI·BL 열과 일치; `--add-baselines` 는 BL 뒤에 붙어 X* 후보에 자동 포함, SUMMARY-B 는 15 개.
- runner 경로: `--sparse-file` 은 rho_sbl·rho_omp·per_snr 만 읽고 `_sparse_at(str(int(snr)))` 키 "-3"…"15" 가 pick 키와 일치; `meta|sparse` 는 sort_keys JSON, 검사 블록은 dict 동등 비교; `build_our_arms` 가 SBL-loop/SBL-pilot/OMP-pilot 을 `exact_prior` 로 만들고 RouteA 는 pilot_only·루프 모두 `prior.ep_site` 를 호출 (Cinv 경로 아님); 초기 상태 `cbar`·`eh2_prior` 는 Cs 표본 공분산 (doc "R2 와 같은 초기 상태" 와 일치); `run|git` 의 dirty 판정은 `code`·`../Demo` 만 보므로 게이트가 복사한 pick·tune 이나 raw·logs 는 dirty 를 만들지 않고, pair_baselines 는 run|git 이 있는 SP raw 를 clean 단일 커밋 규칙으로 잡는다 ("main 커밋 금지" 와 정합).
- 예측·라벨 불변: §3 1–6 이 v1 사본과 같고 ("정보 낮음" 주석·7 번 확장만), §1 주 라벨·"전부" 문장·다중성 18 개 = v1 과 같다; C6·SV8e 의 "전부" 불가 근거 (V1-pilot (iv), b* (iv)) 가 STATIC 출력과 일치.
- 스모크 전제: `raw_spsmoke*`·`results/gmm_fits_D2_spsmoke*` 가 main·워크트리 모두 부재; 워크트리에 `results/gmm_fits_D2_B16e4k` 존재; §4 2 단계 sed 범위 (`^import sys, json, glob, re, numpy` ~ `mismatching chunks`) 가 스크립트 57–63 행만 뽑는다 (34 행 `import sys, os, json, hashlib` 는 불일치); 3 단계 키 이름 `<arm>|nmse`·`<arm>|blk_err` 는 runner 기록 키와 일치; `--skip0 2560 --n 8 --chunk 8` → 7 태스크. `{{NOW}}` 4 개 (3 줄).

### 렌즈 integ

#### 반드시
- **[M1]** §1 실행 행 (36행) · §4 커밋 대상 행 (64행) · code/run_sparse16e4.sh 32행 뒤
  - 문제: 실행에 쓰는 v2b pick·tune JSON 다섯 쌍 (`results/sparse/{pick,tune}_{S2,S2c,SV8e,UMi28,MIX3}_C2.json`) 과 `results/sparse/v2b/` 사본이 sbl 에서 **미추적** (`git status` `??`; 62ed179e 가 추적한 것은 v1_em·v2a 뿐). 동결 = sbl → main 병합은 커밋된 파일만 옮기므로 main 에는 `results/sparse/` 자체가 없고 (`ls ~/t2/conf/results/sparse` 없음), 스크립트는 C2 다섯 행 모두 31행 "pick file missing" ABORT. 손으로 복사해 돌리면 raw 의 `run|git` 동결 커밋이 실행에 쓴 하이퍼파라미터를 담지 않아 재현 불가 (ALD16e4 선례는 `results/ald/tune_PIL*.json` 추적). 문서는 이 다섯 쌍을 동결 커밋 대상으로 어디에도 적지 않았고 (§4 커밋 대상 행은 C6 쌍만), 스크립트도 pick·tune 의 추적·clean 여부를 검사하지 않는다 (sha 만 검사).
  - 수정: (1) 문서 36행 "행마다 전제: 기존 출력 없음 (있으면 ABORT, 재실행은 사용자 승인), pick sha256[:16] = §5 (C2)," → "행마다 전제: 기존 출력 없음 (있으면 ABORT, 재실행은 사용자 승인), **pick·tune JSON 이 git 추적 + clean** (C2 다섯 쌍 `results/sparse/{pick,tune}_<PR>_C2.json` 과 `results/sparse/v2b/` 사본은 **동결 커밋에 포함** — 지금은 sbl 미추적; 스크립트가 행마다 검사, 아니면 ABORT), pick sha256[:16] = §5 (C2),". (2) 문서 §4 표 64행 앞에 새 행: "| 동결 커밋 대상 (병합 전 sbl 에 커밋): `results/sparse/{pick,tune}_{S2,S2c,SV8e,UMi28,MIX3}_C2.json` (sha = §5.1), `results/sparse/v2b/` (바이트 동일 사본), `logs/sparse_tune_*.log`·`logs/sparse_ext*.log` (§5.3 근거), `prereg_reviews_2026-09-29/SPARSE16e4_v1.md`, 이 문서, `run_sparse16e4.sh`·`eval_accept.py` | 대기 |". (3) 스크립트 32행 (sha 검사) 바로 뒤에 한 줄 추가:
  [ "$PSHA" = "-" ] || { [ "$(git ls-files $SP ${SP/pick_/tune_} | wc -l)" = 2 ] && [ -z "$(git status --porcelain $SP ${SP/pick_/tune_})" ]; } \
    || { log "$TAG ABORT: $SP / tune JSON not tracked+clean (the freeze commit must hold both)"; FAIL=$((FAIL+1)); continue; }

#### 권고
- S1 C6 게이트 (스크립트 27–28행): tune 파일 출현이 아니라 프로세스 종료를 기다릴 것 — `json.dump` 가 비원자적이라 쓰는 도중 복사하면 게이트 python 이 json 오류로 ABORT 하고 main 에 잘린 tune 이 남는다; 문서 36행 "튜닝 종료를 기다려 복사" 와도 맞춘다. 27–28행 → `while pgrep -f "^[^ ]*python[^ ]* code/sparse_tune.py --prior S2 --cell C6" > /dev/null; do sleep 600; done` (다음 29행은 그대로).
- S2 게이트 python 블록: `$P - $SP $CELL $PR` 로 prior 를 넘겨 `assert t["prior"] == sys.argv[3] and t["cell"] == cell` 를 36행 assert 에 더하고, print 에 `tune sha256[:16]=…` 을 추가 (§5.2 "sha256[:16] 과 규칙 재현을 로그에 남긴다" 는 pick sha 만 남기고 있음; C6 는 sha 고정이 없어 tune sha 가 §6 의 근거).
- S3 C6 규칙 재현 실패 대비를 §5.2 에 미리 적을 것: 실행 중 프로세스의 코드는 09-30 10:49:14 KST 작업본 (파일은 14:14 KST 에 수정, 62ed179e 14:57 KST) 이고, C2 산출로 검증되지 않은 분기는 `edge_sbl` 의 `n_em == min(grid)` 뿐 → "rule-reproduced False 가 끝 플래그 차이뿐이면 tune JSON 의 nmse_db 에 62ed179e `per_snr_pick` 을 적용해 pick 을 다시 쓰고 사실·두 sha 를 로그·§6 에 남긴다; ρ·n_em·L 값이 다르면 ABORT (NR16 라벨 없음)".
- S4 재검토 원문: v2 재검토 (M1·M2) 와 이번 검토 원문을 `prereg_reviews_2026-10-01/review_SPARSE16e4_v2.md` 같은 파일로 저장하고 3행·22행에 경로·모델·권고 수를 적을 것 (round-1 은 파일이 있고 §6.2 감사가 원문을 찾는다).
- S5 인자 검증·종료 코드 (ALD16e4 선례): 알 수 없는 접미사는 아무 행도 돌리지 않고 `SPARSE_DONE ok=0 fail=0` 으로 끝난다 → 17행 앞에 `for w in "$@"; do case " B16e4k D3 SV U28 MX NR16 " in *" $w "*) ;; *) log "ABORT: unknown row '$w'"; exit 1;; esac; done`; 마지막 줄 뒤 `exit $FAIL`.
- S6 동결 커밋 해시: 병합 커밋은 만들기 전에 해시를 알 수 없으므로 3행에 "DECISIONS 줄은 sbl 팁 해시, 병합(동결) 해시는 로그 `start (git $H)`·pairB 머리말·§6 첫 줄에 기록" 을 적을 것.
- S7 비용 행 "실행 중 다른 CPU 작업 없음": C2 다섯 행이 도는 동안 C6 튜닝 (2 BLAS 스레드, +15 dB ≈ 3–5 h) 이 아직 돌고 있을 수 있다 → "(sbl 워크트리의 C6 튜닝 프로세스 2 스레드는 예외)" 한 마디.

#### 확인
- 스크립트 ↔ 문서 §1 실행·수용·판정 행 대조: runner 명령·인자·순서 (C2 다섯 → NR16)·게이트 간격 600 s·ABORT/INVALID 조건·eval_accept `SP<suf>:-:-:<CELL>`·pair_baselines 인자 모두 일치; `bash -n` 통과; 표 12 열 = `read` 12 변수; 루프 안 외부 명령은 heredoc 또는 `< /dev/null`.
- 플래그 존재: runner `--sparse-file`(1232행)·`--skip0`(1187행)·`--tag`·`--arm`; eval_accept `--tag/--bstar/--kron-K/--ll-val/--ref-raw/--prior`; pair_baselines `--est/--extra/--add-baselines/--r0 at1/--provenance manifest/--expect/--expect-bstar` (103–122행).
- eval_accept `-:-` (미커밋 diff): 워크트리 raw_B16e4k (키 없음) → ACCEPT OK rc 0; main 의 raw_PILB16e4k (키 있음, 읽기만) → FAILED "… present, tag spec '-:-' expects none" rc 1; 원 규격 `B16e4k:legacy-last:4443…` 은 종전대로 실패 (기본 경로 불변).
- 게이트 python 블록 (34–43행) 을 sed 로 추출해 다섯 C2 에 단독 실행 (단일 프로세스, GPU 숨김): rule-reproduced True ×5, sha256[:16] = §5.1 다섯 값과 일치, need 264 GB / MemAvailable 1024 GB, rc 0 ×5. tune 내장 `pick` == pick 파일 ×5, `rhos` 키 없음, n 256, grid = v2b, seed 문자열 20260930 스트림; pick·tune ↔ `v2b/` 사본 `cmp` 바이트 동일 ×5.
- meta|sparse 검사 블록 (57–63행) sed 추출 → 빈 폴더에서 "0 mismatching chunks" rc 0 (문서 §4 2단계의 청크 수 선확인이 필요한 이유 확인); 스크립트 안에서는 eval_accept 의 점·청크 계획 검사가 먼저라 빈 raw 는 도달 불가.
- C6 게이트: pgrep 패턴이 실제 튜닝 pid 276838 (`…/bin/python code/sparse_tune.py --prior S2 --cell C6 --n 256`, 시작 09-30 10:49:14 KST, +12 dB 완료 73343 s) 에 일치 (rc 0); run_sparse_ext 프로세스 없음; `logs/sparse_ext.log` ABORTED 09-30 09:28 CDT; C2 pick·tune mtime 14:03–14:21 KST < 확장 시작 14:23 KST (덮어쓰기 없음).
- 튜닝 ↔ 시행 무접촉: sparse_tune 스트림 `default_rng([20260930, TBID, PID, Nr, snr+100])` vs common.SEED 20260926 시행 스트림; 스모크는 `--skip0 2560` = DEV_SKIP0 (테스트 0..2559 밖).
- `run|git` 은 `git status --porcelain code ../Demo` 만 봄 (runner 466–472행) → 게이트가 복사한 pick·tune, raw_SP*, logs 는 dirty 아님; pair_baselines 는 run|git 이 있는 SP raw 에 한 clean 커밋 규칙 적용 (139–144행), `--extra` 병합 시 genie·run·meta 제외 (203–208행).
- `--expect` 12 라벨 = STATIC16e4 §6.1: C6 V1-pilot (iv) 만 (11·0·1), SV8e M-ours-bstar-scalar·M-ours-gmm32·V1-pilot (iv) + b* (iv) (9·0·3), 나머지 (i); `R0-pilot@1` 별칭은 BL 에 있음 (213행).
- main 에 입력 존재: raw_{B16e4k,D3B16e4,SVB16e4,U28B16e4,MXB16e4,NR16B16e4}, raw_PIL*/raw_ALD* 6 쌍, results/gmm_fits_D2_* 6 개, results/ald/ald_PIL*.npz 6 개, conf/DECISIONS.md; `results/sparse/`·`raw_SP*`·`run_manifest_SP*.json`·`conf/logs` 는 gitignore 대상 아님.
- 병합: `git merge-tree main sbl` (커밋 상태) 충돌 없음; main 이 분기점 34dbf03b 이후 바꾼 공유 코드는 common (+HISNR_SKIP0 1 줄)·eval_accept (`--skip0`, 49–67행; sbl 미커밋 hunk 86–95행과 겹치지 않음)·run_manifest 뿐 → runner·arms 는 main 에서 불변이므로 워크트리 v2 스모크가 병합 뒤의 `--sparse-file` 경로를 그대로 덮는다.
- 메모리 가드 식 = 문서 수치 (C2 ρ16 264 GB, C6 ρ16 882 GB, ρ8 109 GB); nproc 192; KEYS_RAW 에 nmse·blk_err (스모크 3단계 키); C6 SNR 7 점.
- 스모크 잔여물: 워크트리·main 모두 raw_spsmoke*·gmm_fits_D2_spsmoke* 부재; 워크트리에 gmm_fits_D2_B16e4k 있음 (v2 스모크 가능). `{{NOW}}` 4 개 유지. 미커밋 변경 = eval_accept.py·run_sparse16e4.sh·문서 3 파일뿐; arms/common/sparse_tune 미수정.


## 3회차 (최종 확인; 워크플로 wf_9dace310-0b0)

### 검토 대상을 만든 작성자 보고 (원문)

두 파일 모두 고쳤습니다. 반드시 1개와 권고 13개를 전부 반영했고, 하네스 시험은 모두 통과했습니다. 스모크는 이번 작업 규칙대로 돌리지 않았으므로 **v2 `--sparse-file` 스모크는 여전히 동결 전에 메인 세션이 돌려야 합니다.** 커밋과 git add는 하지 않았습니다. /home/HTJ/t2, /home/HTJ/t2_wtS, arms.py·common.py·sparse_tune.py는 건드리지 않았고, tmux `sparsetune`(pid 276838)은 계속 돌고 있습니다. `{{NOW}}`는 모두 6개입니다(머리말 3, 요약 두 줄에 1씩, §4 스모크 칸 1).

**수정한 파일**
- /home/HTJ/t2_wtSBL/conf/results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md
- /home/HTJ/t2_wtSBL/conf/code/run_sparse16e4.sh

**반드시 (2회차, 두 렌즈의 수정을 합침)**
- **문서:** C2 pick·tune 다섯 쌍, `v2b/` 사본, 튜닝 로그가 동결 커밋에 들어간다고 적었습니다. 메인 세션이 병합 전에 sbl에서 `git add`한다는 점도 적었습니다.
  - §1 실행 행의 전제에 "sha가 고정된 행은 pick·tune이 git 추적 + clean"을 넣었습니다.
  - §4 커밋 대상은 두 행으로 나눴습니다. 동결 커밋 행에는 다섯 쌍, `v2b/`, `logs/sparse_tune_*_C2.log`, `logs/sparse_ext*.log`, v1 백업, 재검토 원문, 이 문서, 코드 두 파일을 넣었습니다. 실행 뒤 행은 따로 두었습니다.
  - §5.1에 문장 하나를 더했습니다.
- **스크립트:** sha 검사 바로 뒤에 다음 줄을 넣었습니다.
  ```
  [ "$PSHA" = "-" ] || { [ "$(git ls-files $SP ${SP/pick_/tune_} | wc -l)" = 2 ] && [ -z "$(git status --porcelain $SP ${SP/pick_/tune_})" ]; } \
    || { log "$TAG ABORT: $SP / tune JSON not tracked+clean (the freeze commit must hold both)"; FAIL=$((FAIL+1)); continue; }
  ```

**권고 반영**
1. **C6 게이트:** 파일 대신 튜닝 프로세스가 끝나기를 기다립니다(`while pgrep -f "^[^ ]*python[^ ]* code/sparse_tune.py --prior S2 --cell C6" …; do sleep 600; done`). 그 뒤 tune이 있을 때만 pick과 tune을 복사합니다. §1 문구도 맞췄습니다.
2. **C6 규칙 재현:**
   - 스크립트: runner가 읽는 키(ρ_SBL, ρ_OMP, SNR 별 n_em·L)만 비교합니다. prior를 인자로 넘기고 `t["prior"]`와 `t["cell"]`을 assert하며, pick과 tune의 sha256[:16]을 둘 다 출력합니다.
   - §5.2: 결과별 처리를 미리 적었습니다. 끝 플래그만 다르면 구성상 통과하고, ρ·n_em·L이 다르면 NR16을 라벨 없이 ABORT합니다.
   - §5.2: 도착 시점별 분기도 적었습니다. (가) 동결 전에 끝나면 sha를 고정하고 두 파일과 로그를 동결 커밋에 넣습니다. (나) 동결 뒤에 끝나면 게이트가 복사하고, 두 sha를 로그와 §6에 남깁니다.
3. **실행 제어:**
   - 알 수 없는 행 접미사는 아무 행도 돌리지 않고 ABORT합니다(ALD 선례).
   - 행 표를 `ROWS` 변수로 옮겨, 이 검사와 루프가 같은 표를 읽습니다.
   - 끝에 `exit $FAIL`을 넣고, `run_manifest rc`를 로그에 남깁니다.
4. **§1 실행 행:**
   - "실행 중 다른 CPU 작업 없음"에 예외를 달았습니다: sbl 워크트리의 S2 C6 튜닝 프로세스, 2 스레드.
   - SPARSE_DONE 전에는 `~/t2_wtSBL`과 tmux `sparsetune`을 지우지 않는다고 적었습니다.
5. **§2 SBL-loop n_em:** 파일럿 전용으로 튜닝한 n_em을 루프 안에서도 그대로 쓴다고 적었습니다. 튜닝 표에서 다시 계산한 가능한 손해는 D2 C2 0.28, D3 0.85, SV8e 0.15, UMi28 0.05, MIX3 0.09 dB이고, 방향은 V1 쪽입니다.
   - §1 보고 전용에 "SBL-loop NMSE@16 − SBL-pilot NMSE"를 넣었습니다. raw에는 이미 `<arm>|nmse`(시행 × 16) 키가 있습니다. `pair_baselines`도 `--add-baselines`로 넣은 arm의 median NMSE@16을 찍으므로, 새 코드 없이 읽을 수 있습니다.
6. **§2 OMP-pilot:** L = N이 골라진 점에서는 OMP-pilot이 파일럿 LS(G⁻¹b)와 같다고 적었습니다. 해당 점은 SV8e·UMi28 ≥ +3 dB, MIX3 ≥ +6 dB, D2 C2 +15 dB이고, D3에는 없습니다.
7. **§1 수용:**
   - 새 arm의 예외 시행은 실패로 셉니다(01_RULES §4). PIL/ALD의 예외가 무결성 실패인 것과 다르다고 적었습니다.
   - `meta|sparse` 블록에 arm 별 개수 출력을 넣었고, 이 값을 §6에 옮깁니다.
   - §4 스모크 2단계는 이 개수가 모두 0이어야 한다는 기대를 새로 추가했습니다. 두 리뷰에 없던 동결 전 합격 조건이 하나 더 생긴 것이니, 원치 않으면 빼 주세요.
8. **§5.3 캐비엇 두 문장:**
   - SBL만의 ρ 32 확장은 데이터셋당 ≈ 0.5 h였을 것이나 하지 않았다(ρ 8 → 16 이득은 SBL ≤ 0.05 dB).
   - OMP ρ 32는 테스트 실행 자체가 불가능하다. M = 32768이라 워커당 ≈ 17 GB이고, 192 워커면 ≈ 3.3 TB입니다.
9. **예측 6:** 보고 전용, 채점 안 함으로 내렸습니다. `pair_baselines`는 `x → V1` 쌍만 내고, 등록된 채점 명령도 없기 때문입니다. §1 보고 전용 칸에도 같은 이유를 적었습니다.
10. **cbar·eh2_prior 문구:** 이 문장은 §1 하이퍼파라미터 행이 아니라 "새 arm" 행에 있어서 거기서 고쳤습니다. 희소 arm이 읽는 것은 cbar와 eh2_prior뿐입니다(Demo/t2_route_a.py 326–327). Cinv는 읽지 않습니다(336·374 행).
11. **메모리 가드 ABORT의 허용 대응:**
    - (a) `MemAvailable`이 충분해지면 `bash code/run_sparse16e4.sh NR16` 재실행(규칙·pick 불변).
    - (b) 코드 변경은 사용자 승인 + DECISIONS + C2 OMP-pilot 키 비트 동일 확인 뒤에만.
12. **`sparse_tune.py` 정리:** §4에 적었습니다. v1 규칙을 적은 docstring과 `for fam in ():` 죽은 루프는 C6 튜닝이 끝난 뒤 첫 커밋에서 정리하고, 동작은 바꾸지 않습니다. 동결 뒤에 끝나면 SPARSE_DONE 뒤에 정리합니다(실행 중 main의 code/를 고치면 run|git이 dirty가 됨).
13. **머리말과 요약:**
    - 동결 해시 기록: DECISIONS 줄에는 sbl 팁 해시를 적습니다. 병합 해시는 실행 로그 `start (git $H)`, pairB 머리말, §6 첫 줄에 남습니다.
    - 재검토 원문 경로와 회차별 반드시 수(Fable 5.1; 1회차 stats-fair 0·integ 2, 2회차 1씩 같은 항목)를 적었습니다.
    - 2회차 요약 줄을 새로 넣었습니다. 미채택은 두 건입니다: 1회차의 "SBL만 ρ 32 확장"(§5.3 두 문장으로 대신)과 2회차 stats-fair S3(프로세스 종료 대기로 대신).
14. **§4 스모크 절차:** 로그를 열지 않고, 실패했을 때만 `grep -nE 'Traceback|Error'`로 오류 줄만 봅니다. 로그는 raw와 함께 지웁니다.
    - 리뷰는 로그에 새 arm의 BLER이 찍힌다고 했지만, 실제로 runner가 찍는 것은 R5-genie의 청크별 개발 BLER16뿐입니다. 문서에는 이 사실대로 적었습니다.

**확인 (단일 프로세스, GPU 숨김, 수신기 없음)**
- **문법·인자:** `bash -n` 통과. 스크립트와 문서 명령의 인자는 모두 argparse에 있습니다. 대조한 대상은 runner, eval_accept(`--kron-K` 포함), pair_baselines(`--expect` 포함), run_manifest, sparse_tune `--rhos/--merge-with`입니다. `--prior`·`--cell`·`--testbed` 값도 C.PID·CELLS·TBID에 있습니다.
- **하네스 (스크래치 git 저장소 + 가짜 python, runner 없음):**

| 경우 | 결과 |
|---|---|
| 알 수 없는 행 `NR17`, 빈 문자열 | start 전 ABORT, rc 1 |
| 추적 + clean 쌍 | 검사 통과 |
| tune 미추적 / tune dirty / pick 미추적 / 둘 다 미추적 | 각각 그 행 ABORT |
| PSHA `-` 행 | 막히지 않음 |
| 전체 실행 종료 코드 | 6 (= 실패 행 수) |
| 게이트: 산출 없음, pick만 있음 | "pick file missing" ABORT |
| 게이트: pick + tune | 복사함 |

- **규칙 재현 블록:** 다섯 C2 모두 True이고, pick·tune sha는 §5.1과 같습니다(tune 6f1e19bd…/42b07801…/1b737191…/40999752…/b02e6aca…). 모의 pick으로 보면 끝 플래그만 바꾸면 True, n_em이나 ρ_OMP를 바꾸면 rc 1, prior가 다르면 AssertionError rc 1입니다.
- **`meta|sparse` 블록:** 가짜 raw에서 예외 개수를 제대로 세고, 불일치 청크가 있으면 rc 1입니다. §4의 sed 추출 범위도 그대로 맞습니다.
- **pgrep:** 앵커 패턴은 pid 276838만 잡습니다.

### 최종 확인 (Fable 5.1)

#### 반드시
- (없음)

#### 권고 (주 세션 반영: 1 명시 경로 add, 3 한 커밋 동결, 4 잔여물 확인, 5 §2 예외 시행 문장; 2 는 해당 없음 — C6 튜닝이 동결 전에 끝나지 않아 sparse_tune.py 정리는 SPARSE_DONE 뒤)
- 동결 전 `git add` 는 §4 목록의 **명시 경로만** (절대 `git add -A`/`git add .` 금지): sbl 에는 `conf/ckpt` 가 main 의 실제 디렉터리(`/home/HTJ/t2/conf/ckpt`, 미추적)를 가리키는 미추적 **심볼릭 링크**로 있어, 같이 add 되면 병합 시 디렉터리 ↔ 링크 충돌이 난다. §4 동결 커밋 행 끝에 "(명시 경로로만 add; `conf/ckpt` 링크 제외)" 한 마디.
- `sparse_tune.py` 정리(docstring·죽은 루프)가 **동결 커밋에 들어가는 경우**(C6 가 동결 전에 끝남): 정리 뒤·커밋 전에 §4 의 규칙 재현 블록을 다섯 C2 에 다시 돌려 rc 0 ×5·sha 불변을 §4 코드 행에 적을 것 — 실행 시 main 의 `per_snr_pick` 이 C6 pick 을 판정하므로 '동작 불변' 을 등록된 검사로 남긴다.
- 동결 커밋 = 한 commit 임을 절차로 고정: `DECISIONS.md` 줄을 `git merge --no-commit sbl` 뒤 같은 커밋에 넣거나, 아니면 '동결 커밋 = `start (git $H)` 의 HEAD (DECISIONS 커밋 포함)' 로 머리말에 한 줄. 지금 문장 "병합 결과, DECISIONS 같은 줄" 은 두 커밋이 될 여지가 있다 (스크립트는 DECISIONS tracked+clean 만 본다).
- §4 스모크 4 단계 뒤 `ls results/*spsmoke2* logs/*spsmoke2* 2>/dev/null` 로 잔여물 0 확인을 절차에 추가 — runner `--tag` 는 raw·tables·guard 외에도 태그별 출력을 낼 수 있다 (runner 1244 행 도움말: LADDER·gates·sigma grid).
- §2 에 한 줄: 새 arm 의 예외 시행 수가 0 이 아니면 원고의 그 라벨 문장에 개수를 함께 적는다 (`(i), k raised trials counted as failures`) — 지금은 §6 기록까지만 고정돼 있고, 예외 시행이 실패로 세어져 V1 쪽으로 기우는 점은 독자에게 보여야 한다.

#### 확인
- 2 회차 반드시 (추적 + clean): 스크립트가 sha 검사 바로 뒤에 `git ls-files pick tune | wc -l = 2` 와 `git status --porcelain` 빈 출력을 요구하고 PSHA `-` 행은 건너뛴다 (`A || {B && C} || ABORT` 단락 평가 확인); 문서 §1 실행 전제·§4 동결 커밋 행·§5.1 문장이 같은 파일 집합을 적는다. 동결 커밋 대상 파일은 어느 것도 gitignore 되지 않는다 (`git check-ignore -v` 8 경로 rc 1; `.gitignore` 의 `/logs/` 는 루트 한정, conf/logs 는 1183 파일 추적).
- `bash -n` 통과; `{{NOW}}` 6 개 (3 행 3, 22·23 행 1 씩, 64 행 1). 플래그 존재: runner `--testbed/--cell/--prior/--n/--chunk/--skip0(1187)/--arm/--ntrain/--sparse-file(1232)/--tag`; eval_accept `--tag/--ntrain/--kron-K/--ll-val/--ref-raw/--prior/--bstar`; pair_baselines `--r0/--add-baselines/--expect/--expect-bstar/--extra/--provenance`; run_manifest `--tag` → `results/review_next/run_manifest_<tag>.json`.
- 규칙 재현 블록을 스크립트에서 sed 로 뽑아 다섯 C2 에 단일 프로세스로 직접 실행: rule-reproduced=True ×5, pick sha 2a6d79a2…/afdb4849…/72a6500e…/3d27f1bb…/baffec3e…, tune sha 6f1e19bd…/42b07801…/1b737191…/40999752…/b02e6aca… = §5.1 표, need 264 GB / avail ≈1024 GB, rc 0 ×5; prior 를 틀리게 넘기면 `AssertionError: tune JSON is S2 C2, the row wants S2c C2` rc 1. tune JSON 키 = cell/grid/n/nmse_db/pick/prior/seed/wall_sec, grid = v2b, per_snr 키 '-3'…'15' (문자열) — `per_snr_pick` 도 `str(snr)` 키를 내므로 dict 비교가 성립.
- C6 게이트: 앵커 pgrep 은 pid 276838 (`…/bin/python code/sparse_tune.py --prior S2 --cell C6 --n 256`) 만 잡고 bash 래퍼 276835·패턴을 인용한 내 셸은 안 잡는다; tmux `sparsetune` 생존, 로그 마지막 줄 +12 dB done (73343 s), C6 pick/tune 파일 아직 없음; `common.CONF` 는 `__file__` 기준이라 튜닝 산출은 워크트리 `results/sparse/` 에 쓰인다 (main 에는 `results/sparse` 부재 — 병합이 만든다); `sparse_tune.main()` 은 pick 을 먼저(103 행)·tune 을 뒤(107 행)에 쓴다.
- meta|sparse 블록: raw 파일명 형식 `…_snr<int>_skip<k>_n<n>.npz` (runner 29·124 행, main raw 실물 `D2_C2_S2_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz`) 가 정규식 `_snr(-?\d+)_` 와 맞고 pick 의 문자열 키와 일치; `<arm>|failed` 는 (n,) float 1.0 이고 예외가 없으면 키 자체가 없다 (runner 33·579 행) → 블록의 `if a+'|failed' in z.files else 0` 과 `.sum()` 이 맞다. §4 2 단계 sed 범위는 정확히 9 줄 (첫 줄 `import sys, json, glob, re, numpy`, 끝 줄 `mismatching chunks`) 이고 py_compile 통과.
- 새 arm 예외 = 실패: `pair_baselines.fails` 는 blk_err[:, -1] 비유한 → 1.0 (37–39 행) 으로 𝔅 12 와 같은 규칙; PIL/ALD 만 `failed().any()` → 무결성 실패 (184–185 행). 'report-only, median NMSE@16' 줄은 `(V1, BSTAR) + BL` 을 돌고 BL 에 `--add-baselines` 가 붙으므로 (213·278–281 행) SBL-loop·SBL-pilot 값이 찍힌다.
- §2 수치 재계산 (tune JSON, 그 데이터셋 ρ_SBL 에서 −3 dB n_em 을 다른 SNR 에 쓸 때 최대 손해): D2 C2 0.275 dB (+15, 5 대 10), D3 0.850 (+15, 3 대 10), SV8e 0.147 (+12, 2 대 5), UMi28 0.045 (+15), MIX3 0.093 (+15) = 문서 0.28/0.85/0.15/0.05/0.09. OMP L = 32 = N 인 점: D2 C2 {+15}, D3 없음, SV8e·UMi28 {+3…+15}, MIX3 {+6…+15} = §2·§0 문장. OMP ρ 32: M = 32768, 16·M² = 17.2 GB/워커 × 192 = 3.3 TB — 맞다.
- eval_accept `-:-` 분기 (4e36abc0 diff): `role == sha == '-'` 일 때만 키 존재 → 실패, 그 외 기존 경로 불변; 스크립트 `--tag SP$SUF:-:-:$CELL` 은 `spec.split(':')` 4 필드와 맞다. 3-way 병합 모의 (`git merge-file` base=merge-base, main, 워크트리) 충돌 0·py_compile 통과; `git merge-tree --write-tree main sbl` 충돌 없음. ROWS 의 BS/KK/LL 6 행 = `run_ald16e4.sh` DS 표 (kron 1024 −11.459…, kron 4096 63.175…/0.0888…/5.798…/33.760…, gmm256 − −47.805…).
- 문서 사실 주장: 희소 arm 은 `Cs` 의 cbar·eh2_prior 만 읽는다 (`t2_route_a.py` 326–327 행 `nuE = self.prior.cbar`, `eh2 = self.prior.eh2_prior.copy()`; 336·374 행은 exact_prior 의 `ep_site` 경로, Cinv 는 else 분기; `arms.SparsePrior` 233·254 행 `base.cbar * base.N / M`); OMP 의 M×M 은 `AGA = A.conj().T @ G @ A` 하나뿐 (이후 diag·`np.ix_(S,S)` L×L) → 메모리 가드 식이 정점과 맞다. 스모크 로그의 BLER 줄은 runner `show` 목록 (R2/R3/R4-scvamp/gmm32/score/R5-genie) 중 SP 실행에 있는 R5-genie 뿐 (603–608 행) — §4 문장대로.
- arm 이름 `SBL-loop`/`SBL-pilot`/`OMP-pilot` = `build_our_arms(sparse=…)` (arms.py 404–406, 모두 exact_prior assert); runner 는 pick 의 rho_sbl/rho_omp/per_snr 만 적재해 Pool fork 전에 전역 설정 (1292–1298), `_sparse_at(str(int(snr)))` 로 SNR 별 4 키 → `meta|sparse` sort_keys JSON (318–323·447–448). 회차별 반드시 수 (1 회차 stats-fair 0·integ 2, 2 회차 1 씩) 와 원문 경로 `prereg_reviews_2026-10-01/review_SPARSE16e4_v2.md` (53609 B, 미추적) 가 머리말과 일치; 1 회차 원문 `prereg_reviews_2026-09-29/review_SPARSE16e4.md` 는 추적됨. 권고 13 항 모두 문서·스크립트에서 위치 확인; 미채택 2 건 (SBL 만 ρ 32, 로그 grep 게이트) 은 대체 처리가 적혀 있다. main 에 SP 출력·raw_SP*·results/sparse 없음, 입력 24 경로 존재. 이 검토는 테스트·개발 시행·BLER 을 계산하지 않았고 main·t2_wtS·arms/common/sparse_tune·튜닝 프로세스를 건드리지 않았다.
