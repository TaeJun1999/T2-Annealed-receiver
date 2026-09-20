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

갱신 시각 : 2026-09-20 13:12 KST
경과 시간 : 2시간 50분
현재 phase : **A5 사다리 실행 중** (L1/L2 소진, L3 진행) · A6 는 C3/C4 완료

## 사다리 현황 — 6시도 6실패 (전부 정상 학습 후 게이트 미달)

| 칸 | 시도 | epoch | 종료 | GB (<=5%) | GC (<=0.15) | GD (<=0.20) | GD_trace | 판정 |
|----|------|-------|------|-----------|-------------|-------------|----------|------|
| L1 | a1 | 249 | patience | 14.2% | 0.744 | 0.467 | 0.159 | FAIL |
| L1 | a2 | 340 | patience |  9.0% | 0.784 | 0.380 | 0.081 | FAIL |
| L1 | a3 | 242 | patience |  9.0% | 0.702 | 0.376 | 0.089 | FAIL |
| L2 | a1 | 223 | patience | 14.2% | 0.746 | 0.468 | 0.176 | FAIL |
| L2 | a2 | 351 | patience |  9.9% | 0.807 | 0.381 | 0.100 | FAIL |
| L2 | a3 |  -  | patience |  9.5% | 0.684 | 0.375 | 0.103 | FAIL |

- 전 시도가 `aborted=False` (조기종료 조건 충족) -> 칸을 정당하게 소진했다.
- **GC 가 구속 조건**이고 폭·깊이·학습률·파라미터화를 바꿔도 0.68~0.81 에서 움직이지 않는다.
  이 데이터 예산(9000 표본 / 64 실차원)의 한계로 보인다.
- **GD 재정의가 계속 물린다**: 6시도 전부 GD_trace 는 0.08~0.18 로 통과했을 값인데 J 전체는 0.375~0.468.
- L3 의 게이트 점수 선택이 **실제로 작동**: `{'L1': 4.6253, 'L2': 4.5110} -> base L2` (BLER 미사용).
  이건 적대적 검증이 "예외가 삼켜져 조용히 L1 으로 되돌아가고 있었다"고 잡아낸 바로 그 지점이다.

## 완료
- A1~A4 게이트 전부 통과. 사전 등록 테스트 25/25 + D0~D6t 구현.
- **D2t: diffusion 학습셋이 GMM 이 받은 1e4 표본과 원소 단위로 동일 (최대 차이 0.0)** — 동일 예산 보장이 측정됨.
- **T2d 를 L 전 구간으로 층화**: L in {3..8} 6개 전부 검증, 측정 vs 해석해 최대 편차 5.0e-3,
  within-L 산포 0.0010 vs across-L 0.1294. 조건부 Gaussian 파괴가 메커니즘까지 확인됨.
- A6 C3/C4 (4x4 sanity) n=640 완료.

## 고친 것 (내 코드의 실제 결함)
- **R3-bigamp 가 NMSE 1e57 로 발산하고 있었는데 isfinite 로는 안 잡혔다.** nu^p 가 유한하게 유지되기
  때문(곱 HX 는 일관, bilinear scale 만 달아남). 판정 기준을 NMSE>10 으로 동결하고 01_RULES §4 의
  사전 등록 사다리 beta 0.7->0.5->0.3 을 시행별로 적용, 사용한 beta 를 raw 에 기록.
  -> R3 NMSE 중앙값 0.56 -> 0.23 (baseline 이 강해지는 방향). C3/C4 재실행함.
- 게이트 결과가 LADDER.md 에 안 남던 문제 -> cmd_gate 가 GA|GB|GC|GD 행을 append (append-only 유지).

## 남은 것
- A5 완주 (L3/L4/L5/L6) -> A6 C1/C2 -> B1 T2 정식 기록 -> B2 D2 GMM 재적합 -> B3 -> B4 headline

## BLOCKED
- 없음

## DECISIONS 누적
- 19건

## 마지막 커밋
- (이 커밋)
