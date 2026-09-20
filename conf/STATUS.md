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

갱신 시각 : 2026-09-20 12:45 KST
경과 시간 : 2시간 23분
현재 phase : **A1~A4 게이트 통과. 잔여 모듈 4개 작성·적대적 검증 완료 -> 지적사항 수정 중 -> A5 진입**

## 사용자가 먼저 볼 것 — 사전 등록 게이트 2건을 확정했다 (어떤 체크포인트도 게이트에 걸리기 전에)

1. **GA 는 이 모델 계열에서 구조적으로 0 이다.** 직접 대수 검증함:
   ve 는 `x+s^2(-eps/s)=x-s*eps`=native, vp 는 `sqrt(abar)/sqrt(1-abar)=1/sigma` 라 score 가 `-eps/sigma`
   로 환원, rf 는 `(1-t)^2/t=1/(sigma(1+sigma))` 라 `x+s^2*score=x(1-t)-t*v`=native.
   세 경우 모두 **단일 네트워크 출력의 재배열**이라 두 경로가 항등이다.
   -> 기준 1e-6 은 그대로 두되, "GA PASS 는 학습된 모델의 변환이 검증됐다는 뜻이 아니다. PASS 는 사실상
   GB·GC·GD 에 달려 있다"를 gate_D1.txt·LADDER.md 에 명시한다. GA 를 물게 하려고 별도 x0 head 를
   새로 만드는 것은 게이트에 측정거리를 주려고 모델을 바꾸는 것이라 하지 않는다.
2. **GD 를 tr(J)/N 이 아니라 J 전체의 상대 Frobenius 오차로 확정했다** (기준 0.20 유지, tr 오차는
   GD_trace 로 병기). D-14 가 실제로 소비하는 것은 `SigH=nu*J` 의 역행렬, 즉 행렬 전체다. 두 해석이
   가능할 때 01_RULES §1 은 "우리 주장에 불리한 쪽"을 택하라고 했고 전체 행렬 쪽이 통과하기 더 어렵다.
   (실측: 5-epoch 체크포인트의 비-Hermitian 잔차 7.5e-2 — tr 만 맞고 J 가 틀릴 여지가 실재한다.)

**이 두 결정으로 사다리 전 칸이 게이트를 못 넘을 가능성이 올라갔다.** 04_SPEC §4 가 그 경우를
"실패가 아니라 findings" 로 규정해 두었으므로 그대로 진행한다. 게이트를 낮추지 않는다.

## 완료
- A1 baseline (B/S/C 17/17) · A2 우리 모델 (**M1 = 0.0, M2 = 0.0**) · A3 F2 lemma (L1/L2) · A4 sigma 격자.
- 잔여 모듈 4개 작성 + 적대적 검증 완료: `score.py`(사다리 L1~L6 + 학습 + GA~GD), `d2.py`(sparse
  specular + T2a~T2e), `analysis.py`(표 A/B/C/D), `runner.py`(CLI).
  검증에서 나온 치명/중대 결함은 전부 재현 증거와 함께 잡혔다. 주요 건:
  - score.py: `gates_D1` 이 device=cuda 에서 예외 -> 그 예외가 삼켜져 **L3 의 사전 등록 게이트 선택이
    실제로는 한 번도 실행되지 않고 조용히 L1 로 되돌아가고 있었다** (수정됨).
  - score.py: 재개(resume) 시 학습 네트워크·검증 네트워크·기록된 hp 가 서로 다른 구성이 될 수 있었다
    (MLP 는 파라미터화가 달라도 state_dict 가 그대로 로드된다) (수정됨).
  - score.py: 게이트 집계가 builtin `max` 라 **NaN 격자점이 조용히 사라져** 부분 발산 모델이 PASS 할
    수 있었다 -> `np.max` 로 NaN 전파 (수정됨).
  - analysis.py: chunk 마다 키 집합이 달라지면 KeyError 로 분석 전체가 죽었다 (수정됨).
  - analysis.py: arm 이 예외를 던진 블록이 모든 sign test 에서 **조용히 빠지고** 있었다 -> 블록 오류로
    세고 NOTE 출력 (수정됨, 보수적 방향).
  - analysis.py: R6-exactEP(참 prior oracle, EM 안 돌림)에 GMM EM 시간이 **날조되어** 찍히고 있었다 (수정됨).
  - runner.py <-> score.py **API 불일치로 `train`/`gate` 가 전부 죽어 있었고 M-ours-dscore 가 어느
    testbed 에서도 생성되지 않고 있었다** (수정 중).

## 진행 중
- 위 검증 지적사항 수정 (4개 파일 동시). 수정 후 **게이트는 orchestrator 가 직접 재실행**한다.

## 남은 것
- A5 score 사다리 L1->L6 (칸당 최대 3회, 첫 통과 칸에서 정지) — GPU 학습
- A6 D1 전 arm 실행 -> B1 D2 검증(T2d 가 관문) -> B2 GMM 재적합 -> B3 재학습 -> B4 headline

## BLOCKED
- 없음

## DECISIONS 누적
- 17건 (`conf/DECISIONS.md`)

## 마지막 커밋
- de46d6e
