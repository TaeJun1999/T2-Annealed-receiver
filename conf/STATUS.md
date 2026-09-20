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

갱신 시각 : 2026-09-20 15:05 KST
경과 시간 : 4시간 43분
현재 phase : **확장 칸 L7~L10 실행 중 · HPO 탐색 시작 (6 GPU 자동 확장)**

## 가장 중요한 결과 — EDM 이 4개 중 3개 게이트를 통과시켰다

| 구성 | GA | GB (<=5%) | GC (<=0.15) | GD (<=0.20) | gate_score |
|------|----|-----------|-------------|-------------|------------|
| L4 a1 (사전 등록 사다리 최선, conv/vp, 310k) | PASS | 2.58% PASS | 0.318 | 0.223 FAIL | 2.109 |
| **L7 a1 (EDM, 동일 아키텍처·동일 파라미터 수)** | PASS | **1.67% PASS** | 0.332 | **0.187 PASS** | ~2.21 |
| HPO trial 0 (conv/edm/angle, 115k) | PASS | 6.53% | **0.297** | 0.362 | **1.981** |

- **EDM preconditioning 이 GD 를 0.223 -> 0.187 로 통과시켰다.** 아키텍처도 파라미터 수도 그대로이고
  파라미터화만 바꿨다. GB 도 최고값(1.67%).
- **남은 것은 GC 하나**. 0.30~0.33 이고 기준은 0.15 이라 약 2.2배 개선이 필요하다.
- **HPO 4번째 무작위 시도만에 사다리 전체 최선을 넘었다** (gate_score 1.981 vs 2.109).
  사용자 지적대로 칸당 3시도는 공간을 크게 과소표집한 것이었다.

## HPO 설계 (사용자 요청)
- 탐색 공간: arch {mlp, conv, unet, dit, uvit, adm} x param {ve, vp, edm} x domain {pixel, angle}
  x width x depth x lr x ema x batch x emb x heads x patch. Optuna TPE, 6 GPU 병렬.
- **목적함수 = 사전 등록 게이트 점수** (max_g G[g]/tol[g]). BLER 은 보지 않는다.
- **동일 데이터 예산**: 같은 1e4 표본, 같은 9:1 분할, 동결된 sigma 격자. 추가 데이터 없음.
- **게이트 과적합 방지**: 탐색은 held-out stream 11 에서 채점하고, **보고용 게이트는 stream 10**.
  우승 구성은 전체 사다리 예산으로 재학습 + stream 10 재게이트를 통과해야만 결과로 인정한다.
  (이 분리가 없으면 수백 시도를 보고 대상 집합에 맞춰 과적합시키는 다중검정이 된다.)
- 실패·가지치기 시도 포함 전 시도를 `results/hpo_trials.csv` 에 기록. 아키텍처별 best/median/p10 을
  시도 수와 함께 보고 -> "conv 가 U-Net 보다 낫다"를 n=3 일화가 아니라 분포로 판정한다.
- **사전 등록 사다리(L1~L6) 결과는 그대로 두고 HPO 는 별도 파일로 보고한다.**

## 완료
- A1~A4 게이트. **A5 사다리 완주(18시도 전부 미달, ABORTED 0건)**. A6 D1 전 arm (C1~C4, n=640).
- 전 체크포인트 재게이트 -> **완전한 gate_D1.txt (21개)**.
- B1 T2d PASS. B2 D2 GMM 재적합 (b* = kron K=256, K=512 확인 중).
- 사전 등록 테스트 25/25, D0~D6t 7/7.

## 진행 중
- L8(DiT) / L9(U-ViT) / L10(ADM) 각 3시도
- HPO: GPU 0,1,5 가동 중. GPU 2,3,4 는 L8/L9/L10 종료 시 자동 합류 (hpo_autoscale.sh)

## 남은 것
- HPO 완주 -> 상위 구성 전체 예산 재학습 + stream 10 재게이트 -> 통과 시 M-ours-dscore 확정
- B3 D2 score 학습 + GB' -> B4 D2 전 arm (headline) -> 표 A~D -> DoD 점검 -> EXPERIMENTS 한 행

## BLOCKED
- 없음

## DECISIONS 누적
- 30건

## 마지막 커밋
- (이 커밋)
