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

갱신 시각 : 2026-09-20 14:45 KST
경과 시간 : 4시간 23분
현재 phase : **A5 사다리 완주(18시도 전부 게이트 미달) · 확장 칸(EDM/DiT/U-ViT/ADM) 배선 중 · B2 K=512**

## A5 결과 — 사전 등록 사다리 L1~L6, 18시도 전부 게이트 미달 (ABORTED 0건)

| 칸 | 구성 | 최선 GB (<=5%) | 최선 GC (<=0.15) | 최선 GD (<=0.20) |
|----|------|----------------|------------------|-------------------|
| L1 | MLP, VE/DSM | 9.0% | 0.702 | 0.376 |
| L2 | MLP, VP/DDPM-eps | 9.5% | 0.684 | 0.375 |
| L3 | MLP, 각도 도메인 | 9.5% | 0.718 | 0.386 |
| **L4** | **2D conv, 픽셀** | **2.6% PASS** | **0.318** | **0.205** |
| L5 | conv 위 flow matching | 3.4% PASS | 1.054 | 0.206 |
| L6 | VAE prior | 51.3% | 1.033 | 0.715 |
| *L4u* | *U-Net (사용자 지시로 추가)* | *4.5% PASS* | *1.126* | *0.266* |

**04_SPEC §4 의 규정대로 "이 데이터 예산에서 학습 score 는 게이트에 도달하지 못했다"가 결과다.
게이트를 낮추지 않았다.** 증거: D0~D6t 7/7, ABORTED 0건, 전 시도 LADDER.md 기록, ckpt 21개 실재.

### 사다리가 알려준 것 (통과 여부와 무관하게 보고 가능한 ablation)
- **구속 조건은 아키텍처였다.** MLP 9시도는 폭·깊이·학습률·파라미터화·도메인을 다 바꿔도 GC 0.68~0.81.
  conv 로 바꾸자 GB 통과 + GC 0.318. L1/L2 에서 멈췄다면 "데이터 예산 한계"로 **오진**했을 것이다.
- **U-Net 은 flat conv 에 완패** (GC 1.126 vs 0.318). 8x4 에서 4x2 -> 2x1 다운샘플이 skip 으로
  복구되지 않는다 -> "스케일 대신 채널에 깊이를 쓴다"가 실측으로 옳았다.
- **각도 도메인은 도움이 안 된다** (L3 게이트 점수 4.793 > L2 픽셀 4.511).
- **flow matching 은 해롭다** (GC 0.318 -> 1.054~8.86). score 를 속도장에서 복원할 때 (1-t)^2/t ~ 1/sigma
  가 작은 sigma 에서 오차를 증폭한다.
- **용량은 단조롭게 해롭다** (U-Net 1.06M/4.19M/11.3M -> GC 1.13/4.57/6.10). 9000 표본이 한계.
- **실패는 GC(score 정확도)에 국한된다.** GB(denoising NMSE 초과)는 conv 3시도 전부 통과,
  GD_trace(D-14 가 쓰는 스칼라 divergence)는 전 칸 통과(0.029~0.184). 못 넘는 것은 GC 와 J 전체.

## 완료
- A1~A4 게이트, **A6 D1 전 arm 실행 (C1~C4, n=640, raw 320)**, 표 A/B/C/D.
- B1 T2d PASS (L 전 구간 층화). B2 D2 GMM 재적합.
- 사전 등록 테스트 25/25, D0~D6t 7/7.

## 진행 중
- 전 체크포인트 재게이트 -> 완전한 gate_D1.txt (00_GOAL §4)
- 확장 칸 배선: EDM(preconditioning), DiT(adaLN-Zero), U-ViT(long skip), ADM(adaGN+attention)
- B2 K=512 (b* 가 K=256 에서도 경계였음)

## BLOCKED
- 없음. M-ours-dscore 는 게이트 통과 체크포인트 없음으로 D1/D2 양쪽에서 BLOCKED 표기 유지.

## DECISIONS 누적
- 28건

## 마지막 커밋
- (이 커밋)
