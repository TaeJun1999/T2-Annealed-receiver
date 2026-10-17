# 검증 리뷰 요청
목표: 연구 결론이나 명시된 요구사항에 영향을 주는 오류를 찾는다. 파일은 읽기만 한다.
대상: 레포 /home/HTJ/t2, 커밋 09d2ea69..24ad4441 의 코드 — `conf/code/gmm_em_gpu.py`, `conf/code/fit_gpu.py`, `conf/code/fit_gcap_cont.py`, `conf/code/gcap_compare.py`, `conf/code/run_gcap.sh`, `conf/results/review_next/gcap/select_gcap.py`, `conf/results/review_next/gcap/rss_smoke.py` (`git -C /home/HTJ/t2 diff 5bcffc3e 24ad4441 -- conf/code conf/results/review_next/gcap`).
명세: `conf/results/review_next/NEXT_EXPERIMENTS_U28NR32GCAP.md` (등록 v2) §1 과 `conf/results/review_next/gcap/fit_manifest_U28NR32GCAP.json`. 사용자 과제 원문 `conf/results/review_next/gcap/PROMPT_SERVER_GMMCAP.md`, 공통 규칙 `conf/results/review_next/gcap/PROMPT_SERVER_COMMON.md`.
입력·결과 파일: 기존 실행 `/home/HTJ/t2_wtS/conf/raw_U28NR32B16e4/` (448 청크), 기존 fit `/home/HTJ/t2_wtS/conf/results/gmm_fits_D2_U28NR32B16e4/`, 기존 표 `/home/HTJ/t2_wtS/conf/results/tables_D2_U28NR32B16e4.txt`, 기존 회수율 `/home/HTJ/t2_wtS/conf/results/review_next/recovery_U28NR32B16e4.txt`.

검토할 질문:
1. `init=None, stop_rule="legacy"`, `FIT_STOP_RULE` 미설정일 때 GMM EM 과 `fit_gpu.py` 의 수치·출력 파일이 커밋 5bcffc3e 와 같은가.
2. continuation (`fit_gcap_cont.py`) 이 저장된 best-validation 상태에서 정확히 M-step 50 회를 하고, 검증 LL 을 상태 0, 10, …, 50 에서 재고, 상태 0 을 포함한 최고 상태를 저장하는가. kron 플립플롭 시작 행렬 `kron_tk` 가 EM 이 들고 있던 값과 같은가. 수치 이상이 "완료" 로 분류될 길이 있는가.
3. `stop_rule="gcap"` 에서 학습 LL 이 한 번 줄어든 것만으로 tol 정지가 일어나지 않는가. 정지 사유 4 갈래 (tol / patience / budget / numerical) 가 manifest 정의대로 기록되는가.
4. `gcap_compare.py` 가 새 raw 의 b\* 와 기존 raw 의 V1·genie 를 같은 시행끼리 짝짓는가. 그렇게 낸 표 B (판정점 자동 선택, 부호검정, 2/3 규칙, power guard, SNR@0.1 격차 90 % paired bootstrap) 와 R (paired bootstrap B 2000) 이 기존 파이프라인 (`analysis.py`, `recovery_ci.py`) 이 한 raw 폴더로 계산했을 값과 같은가. 시행이 다를 때 거부하는가.
5. `run_gcap.sh` 가 등록 §1.3 의 명령·CPU 집합·fits 폴더 규칙·수용 호출·순서를 그대로 수행하는가. 통과하지 말아야 할 전제를 통과시키거나, 수용 실패를 OK 로 세는 길이 있는가.
6. `select_gcap.py` 가 §1.2 규칙 (검증 LL 최고, B 는 최고 상태 > 0 일 때만 별개 후보, test 미사용) 을 그대로 구현하는가. `rss_smoke.py` 가 test 시행을 쓰지 않고 워커 최대 RSS 를 제대로 재는가.

실행 제한 (지키지 않으면 진행 중인 실험이 망가진다): GPU 0–3 에서 이 실험의 적합이 돌고 있다. GPU 를 쓰지 말고 (`CUDA_VISIBLE_DEVICES=` 빈 값), CPU 는 `taskset -c 32-39` 로 묶어라. `run_gcap.sh`, `rss_smoke.py`, `runner.py run`, `run_gcap_fits.sh` 는 실행하지 마라 (등록된 test 실행이나 GPU 적합이 시작된다). tmux 와 실행 중인 프로세스를 건드리지 마라. `conf/results/gmm_fits_*`, `conf/raw_*`, `conf/logs/` 에 쓰지 마라. 삭제 명령을 쓰지 마라. 작은 검사는 `/tmp/codex-gcap/` 아래의 복사본으로 하라. 파이썬은 `/home/HTJ/miniforge3/envs/torch/bin/python`.

보고: 항목마다 파일:줄 또는 데이터 위치, 재현 방법, 실제로 확인한 결과를 적는다.
확인된 결함 / 추가 확인 필요 / 선택적 개선으로 나눠라. 결함이 없으면 검토 범위와 수행한 확인을 써라. 개수를 채우려 하지 마라.
