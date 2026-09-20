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

갱신 시각 : 2026-09-20 13:20 KST
경과 시간 : 2시간 58분
현재 phase : **A5 사다리(L3 소진 직전) · B1 완료 · B2 실행 중**

## 사다리 현황 — 9시도 9실패 (전부 정상 학습 후 게이트 미달, ABORTED 0건)

| 칸 | 시도 | epoch | GB (<=5%) | GC (<=0.15) | GD (<=0.20) | GD_trace |
|----|------|-------|-----------|-------------|-------------|----------|
| L1 | a1/a2/a3 | 249/340/242 | 14.2/9.0/9.0% | 0.744/0.784/0.702 | 0.467/0.380/0.376 | 0.159/0.081/0.089 |
| L2 | a1/a2/a3 | 223/351/- | 14.2/9.9/9.5% | 0.746/0.807/0.684 | 0.468/0.381/0.375 | 0.176/0.100/0.103 |
| L3 | a1/a2 | -/- | 14.6/9.5% | 0.753/0.785 | 0.472/0.389 | 0.168/0.098 |

- **GC 가 구속 조건**. 폭·깊이·학습률·파라미터화(ve/vp)·도메인(pixel/angle) 어느 축을 바꿔도 0.68~0.81.
- **9시도 전부 GD_trace 로는 통과했을 값**(0.08~0.18)인데 J 전체로는 0.375~0.472 -> GD 재정의가 결정적.
- L3 의 게이트 점수 선택 정상 작동: `{L1: 4.6253, L2: 4.5110} -> base L2` (BLER 미사용).

## 완료
- A1~A4 게이트. 사전 등록 테스트 **25/25**, **D0~D6t 7/7** (D4t: L1/L2/L3 ckpt 로드·forward 확인,
  **D6t: ABORTED 0건** -> "게이트 미달"이 부족한 학습 탓이 아님이 증거로 확보됨).
- **D2t: diffusion 학습셋 = GMM 학습셋, 원소 단위 최대 차이 0.0** (동일 예산 보장이 측정됨).
- A6 C3/C4 (4x4, n=640) 완료.
- **B1 완료 — T2d PASS, `conf/results/testbed_D2.txt` 기록.** L in {3..8} 6개 전부 층화 검증,
  측정 vs 해석해 최대 편차 5.0e-3, worst CI_hi-2 = -0.2518, within-L 산포 0.0010 vs across-L 0.1294.
  **조건부 Gaussian 파괴가 메커니즘까지 확인됨 -> Stage B 진행 가능.**
- D2 생성기 규약을 독립 재구성으로 검증: `sample_vecs == vec(H) column-major` 오차 **0.0**,
  `h[i+Nr*j]==H[i,j]` 오차 **0.0**, E||H||^2 = 32.0097 vs 32.

## 진행 중
- A5: L3 a3 -> L4/L5/L6 (GPU 0)
- B2: D2 GMM 재적합 120 EM runs (CPU 120 workers). K={16,32,64,128} x {full,kron} x kappa x restarts,
  **선택은 검증 우도만**. 초기 관찰: K=128 은 starved component 재시드 다발 + ll_val -52.6 (K=32 는 -48.3)
  -> 검증 우도가 과대 K 를 제대로 배제하고 있다.

## 고친 것 (내 오류 2건)
- **R3-bigamp 가 NMSE 1e57 로 발산하는데 isfinite 로 안 잡혔다** (nu^p 는 유한, bilinear scale 만 달아남).
  판정 기준 NMSE>10 동결 + 01_RULES §4 의 beta 0.7->0.5->0.3 사다리 적용, 사용 beta 를 raw 에 기록.
  -> R3 NMSE 중앙값 0.56 -> 0.23.
- **M-ours-score(oracle)를 4x4 셀에서 잘못 제외**하고 있었다. oracle 은 폐형식이라 학습 네트워크가
  불필요하고 배열 크기 제약이 없다. 재실행 결과 C3 에서 genie 제외 최상위(0.128/0.091/0.075)로,
  R6-exactEP(0.148/0.102/0.089)보다 좋다 — 빠뜨렸다면 D1 계측기 표에서 통째로 사라질 결과였다.

## 남은 것
- A5 완주 -> 전 체크포인트 재게이트(LADDER 게이트 행 백필) -> A6 C1/C2 -> B3 -> B4 headline

## BLOCKED
- 없음

## DECISIONS 누적
- 20건

## 마지막 커밋
- (이 커밋)
