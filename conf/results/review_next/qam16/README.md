# E5 16-QAM 구현 검사 자료

사용자 승인 범위: E5 worktree만 수정, 커밋·삭제·GPU 사용 없음. QPSK test 재평가는 두 기존 청크의 회귀에만 허용된다. 16-QAM은 C2 +9 dB의 개발 trial 2560..2563만 복호한다. 이는 격자 선택이나 성능 평가가 아니다.

- `prepare_inputs.py`: main의 필요한 입력을 같은 상대 경로에 `cp -L`로 복사한다. 기존 추적 입력은 SHA를 확인해 재사용한다. 새 링크를 만들지 않으며 기존 내부 링크를 변경하지 않는다.
- `copied_inputs.json`, `input_sha256.tsv`: 모든 준비 입력 36개의 source, destination, 전체 SHA-256, 복사/기존 구분. 기존 D2 fit 링크의 실제 대상도 JSON에 기록했다.
- `control_runner.py`: 이 worktree의 수정 전 `HEAD:conf/code/runner.py` 그대로. 회귀 시 수정 전 현재 메타 키 집합과 arm 집합을 확인하는 데만 쓴다. 이 파일 자체는 변경하지 않는다.
- `checks.py`: mapping, 무잡음 왕복, 전용 arm 거부, 두 기존 청크의 바이트 비교, 개발 스모크, RNG·routing 검사. 검사용 출력 위치만 `d_raw`를 qam16 하위로 격리한다. 실제 arm 생성·송신·반복·저장·CLI 인자 파싱은 runner를 사용한다. 일반 runner의 `--tag` 경로 규칙은 변경하지 않았다.
- `run_checks.sh`: tmux에서 순서대로 unit → regression → smoke를 실행한 정확한 명령. 파일별 stdout/stderr, 원 raw와 재계산 raw를 보존한다. 중단·SNR 수정 뒤에는 `continue_checks.sh`로 regression → smoke를 이었다. 기존 산출물을 보존하기 위해 같은 디렉터리에서 재실행하지 않는다.
- `execution_context.txt`, `resources.log`: 실행 시각(`date` 출력, CDT), HEAD와 미커밋 상태, 코드 SHA, 잠금 ID, 실제 affinity·환경·GPU 프로세스 확인.
- `unit.json`, `regression.json`, `smoke.json`: 판정 근거와 명령. 실패 시 stdout/stderr를 먼저 확인한다.
- `coverage_*.npz/.json`: V1의 실제 ν_q, sqrt(ν_q/2), 체크포인트의 학습 σ 양끝과 반복별 유한 질의 수·하한 미만 수·상한 초과 수·범위 밖 비율. 1블록 스모크이며 분포 추정 결과로 해석하지 않는다.

실행한 명령:

```bash
tmux new-session -d -s e5_qam16_checks \
  'cd /home/HTJ/t2_wtE5 && bash conf/results/review_next/qam16/run_checks.sh > conf/results/review_next/qam16/suite.log 2>&1'
```

독립 검토와 사용자 잠금은 아직 이루어지지 않았다. 이 자료는 구현자가 수행한 검사이며, 다른 모델의 코드 비열람 golden 검증을 대신하지 않는다.
