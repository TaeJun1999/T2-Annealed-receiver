# STATUS — conf 실험

> Claude Code가 이 파일을 계속 덮어쓴다. **매 phase 종료 시 + 최소 30분마다 갱신 후 commit & push.**

## 세션 설정 (요청대로 첫 줄에 기록)

- 모델 : **Opus 5 (1M context)** — `claude-opus-5[1m]`. 요구사항(Opus) 충족.
- effort / thinking : 세션 내부에서 읽거나 바꿀 수 없는 클라이언트 측 설정이라 **모델이 확인·변경할 수 없다.**
  사용자가 Max 가 아니면 `/model` 에서 올려야 한다. 이 이유로 작업을 멈추지는 않는다(운영 모드 §1).
- 시작 시각 : 2026-09-20 00:22 KST

## 계산 자원 (시작 시 측정)

- GPU : NVIDIA RTX PRO 6000 Blackwell Server Edition x 6, 각 97887 MiB, **6장 전부 0 MiB 사용 = 전부 가용**.
  드라이버 580.173.02 / CUDA 13.0 / Compute Mode Exclusive_Process.
- CPU : 192 코어. RAM 1007 GB (사용 12 GB). 디스크 `/home/HTJ` 6.5T 중 463G 사용 (8%).
- torch 2.14.0+cu130, `torch.cuda.is_available() = True`, device_count 6, `get_arch_list()` 에 `sm_120` 있음.
- numpy 2.5.2 / scipy 1.18.1 / python 3.12.14 (`~/miniforge3/envs/torch`).
- 계획 : 수신기 실행 = CPU 멀티프로세스(192코어, `--jobs` 미지정). score 학습 = GPU(cuda).

---

갱신 시각 : 2026-09-20 00:35 KST
경과 시간 : 13분
현재 phase : **P0 (읽기·설정) 완료 -> P1 (A1 baseline R3/R4 구현) 시작**

## 완료
- conf/ 지침 10개 전부 통독 (README, 00~09).
- `Demo/t2_route_a.py`, `t2_trellis.py`, `t2_gmm.py`, `exp_0925_run.py`, `exp_0925_analysis.py`,
  `exp_0921_run.py`, `exp_0921_analysis.py`, `archive/exp_0915_bcjr_score_check.py`, `CLAUDE.md` 통독.
  - `exp_0915_bcjr_score_check.py` 는 `Demo/` 가 아니라 **`Demo/archive/`** 에 있다 (지침의 경로와 다름; repo 가 정본).
- `nvidia-smi` 측정, 환경 확인, `conf/{code,results,raw,logs,figs,ckpt}` 생성.

## 진행 중
- P1: `conf/code/common.py` (testbed/pilot/code/seed/헤더), `bigamp.py` (R3), `scvamp.py` (R4) 구현.

## 남은 것 / 예상
- P1 A1 baseline + 테스트 B/S/C
- P2 A2 우리 모델 조립 + 테스트 M1~M4
- P3 A3 F2 lemma (L1/L2)
- P4 A4 sigma_t 격자 측정
- P5 A5 score 사다리 L1->L6 (게이트 GA~GD)
- P6 A6 D1 전 arm 실행
- P7 B1~B4 (D2 검증 -> GMM 재적합 -> score 재학습 -> headline)

## BLOCKED
- 없음

## DECISIONS 누적
- 6건 (`conf/DECISIONS.md`)

## 마지막 커밋
- (이 커밋)
