# verifier 검토 — 커밋 09d2ea69 (U28NR32GCAP 코드), 2026-10-16 23:40 CDT 보고 (verifier 서브에이전트, 독립·읽기 전용)

범위: `conf/code/{gmm_em_gpu.py, fit_gpu.py, fit_gcap_cont.py, gcap_compare.py}`, `gcap/{test_gcap_em.py, probe_gcap.py, run_gcap_fits.sh}` 대 `gcap/fit_manifest_U28NR32GCAP.json` · 등록 §1.1–§1.3. 검사 스크립트·출력: `/tmp/claude-1005/-home-HTJ-t2/7f296764-20fc-422b-96c7-feef15a08581/scratchpad/verifier/` (mock_fitgpu.py, mock_cont.py, check_tk.py, num_stop.py, tol_check.py, cmp_npz.py; cmp_self/newA/newB/newC.txt).

## 확인된 결함
없음.

## 추가 확인 필요 (보고 원문 요약) → 처리
1. `gcap_compare.py:54` 가 load_raw 의 NOTE (arm 이 raise 한 블록을 실패로 세고 유지, 01_RULES §4) 까지 거부 사유로 썼다 — 새 raw 에 raise 블록이 하나라도 있으면 시행이 같아도 REFUSED. → **반영 (동결 전)**: WARNING (청크 구멍·겹침, 청크에 없는 키) 만 거부, NOTE 는 출력 파일 머리에 옮겨 적는다. old = new 자체 검사 출력은 수정 전과 바이트 동일 (rc 0).
2. gcap 의 numerical 정지는 E-step Cholesky 실패와 비유한 학습 LL 만 잡는다; M-step 의 `torch.linalg.inv` 실패나 CUDA OOM 은 프로세스를 죽이고 npz 를 남기지 않는다 (기록은 `logs/gcap_fits.log` 의 rc ≠ 0 과 프로세스 로그). "완료" 로 잘못 보고되지는 않는다. → **등록 §1.1 에 규칙으로 적는다** (프로세스 예외 = 수치 이상, 후보 없음, 사용자에게 보고).

## 선택적 개선
- `fit_gcap_cont.py` 의 `steps_done = len(ll) − 1` 은 Cholesky 실패 (상태 j → j−1) 와 비유한 LL (상태 j → j) 에서 뜻이 1 다르다; 둘 다 "NOT completed" + 정지 사유가 남아 판정 영향 없음. → 등록 §1.1 에 정의를 적는다.
- `fit_gpu --merge` 는 후보들의 `stop_rule` 이 섞였는지 검사하지 않는다 (지금 스크립트는 세 재시작 모두 gcap).

## 실행해서 확인한 것 (요약)
1. 기본 경로 비트 동일: `test_gcap_em.py` (old = `09d2ea69^`) T1–T4 통과 (GPU 5); `fit_gpu.py` 이전판 대 새판을 합성 데이터로 (kron, kron 일괄, full κ 4 × 재시작 3, all-in-one) — 후보·병합 파일 필드·값 동일 (`sec` 만 다름).
2. `FIT_STOP_RULE=gcap` 후보에 stop · stop_rule · ll_val_traj, 병합에 cand_stop.
3. continuation 정확히 50 회 (상태 0..50, 검증 [0,10,…,50], stop budget, status completed, steps_done 50); 상태 0 train / val LL 원본과 비트 동일; 주입한 수치 이상 → `numerical (Cholesky failed, train E-step)` / `numerical (non-finite train ll)`; legacy 는 이전처럼 raise.
4. 실제 K4096 fit 의 Tk 복원: I 판정 1015 성분 (continuation 로그와 일치); Van Loan–Pitsianis SVD 독립 검증 — kron 성분 잔차 ≤ 4.2e-16, I 성분 ≥ 0.087; I 성분 전부 `cov − 0.5 Ĉ` rank 1 (seed_cov), π·n ≤ 2.99 < 4; tr T = Nt(1 + 1e-4) 오차 8.9e-16; seed 튜플 manifest 와 일치.
5. gcap 은 학습 LL 감소로 멈추지 않는다 (legacy 는 it 20 tol-decrease; gcap 은 같은 궤적에서 17 번 감소 뒤 patience).
6. `gcap_compare.py` old = new → 표 B 391:32 · +2.29 dB [+1.98, +2.61] · ΣF 958/599/127 · R 0.432 [0.402, 0.462] (`tables_D2_U28NR32B16e4:308–313`, `recovery_U28NR32B16e4` pooled 와 같음); genie 1 ulp 변경·청크 하나 빠짐 → REFUSED; b\* 한 시행 변경은 0 dB 137:12, ΣF 959 로 반영 (짝짓기 정상).
7. `run_gcap_fits.sh`: `bash -n` 통과, GPU→NUMA 쌍 매핑, 인자·SHA·명령 manifest 와 일치.
