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

갱신 시각 : 2026-09-20 12:57 KST
경과 시간 : 2시간 35분
현재 phase : **A5 (score 사다리) 실행 중** — tmux 세션 `A5`, GPU 0, 로그 `conf/logs/A5.log`

## 완료 (게이트 통과)
- A1 baseline (B/S/C) · A2 우리 모델 (**M1 = 0.0, M2 = 0.0**) · A3 F2 lemma · A4 sigma 격자.
- 잔여 모듈 4종(score/d2/analysis/runner) 작성 + 적대적 검증 + 지적사항 수정 + 통합.
- **사전 등록 테스트 25/25 PASS** (모듈 통합 후에도 M1/M2 exactly 0 유지).
- score.py 자체검증 3종 통과:
  - `selftest_M5`: 정확 GMM denoiser 대비 Wirtinger J 2.0e-12, alpha 6.0e-13 -> 복소 규약 전 구간 확인
  - `selftest_gates`: 정확 score 를 모델처럼 넣으면 GA~GD ~ 0 -> **게이트 코드가 공허하지 않음**
- **D2 testbed 검증 예비 실행: T2d PASS (결정적)**. 4차 모멘트비 측정 1.615~1.747 vs Gaussian 2,
  99.9% CI 8개 전부 2 를 배제, 최악 CI_hi-2 = -0.249. **T2dm 이 메커니즘까지 확인**: 해석해
  `2 - sum_l p_l^2` 와 측정치가 1.4e-3 이내. -> 조건부 Gaussian 파괴가 수치로 증명됨. Stage B 진행 가능.
  (T2a 6.7e-5, T2b DFT 파일럿 결정 + knife edge 기록, T2c 같은-Tp 비교는 vacuous -> 교차-Tp goodput 으로 읽어야 함)
- run -> analysis 파이프라인 전 구간 검증 (태그 실행 후 산출물 삭제).

## 진행 중 — A5 사다리
- L1 a1: 249 epoch, patience 조기종료, 80 s (0.32 s/ep), cuda:0, ckpt 10.6 MB. 게이트 측정 중.
- 사전 smoke 로 잰 L1(256 ep) 게이트: GB +14.1% / GC 0.742 / GD 0.466 (기준 5% / 0.15 / 0.20) -> 여유 없이 FAIL.
  GC 는 작은 sigma 에서, GB·GD 는 큰 sigma 에서 나빠진다.
- **GD 재정의가 실제로 물린다**: 같은 체크포인트에서 GD_trace 0.159 (통과했을 값) vs GD(J 전체) 0.466 (FAIL).

## 관찰 (결과로 보고할 것, 고치지 않음)
- **R4-llr 이 period-2 한계순환으로 발산**한다 (예비 n=8 9dB: cyc2 87.5%, NMSE@16 = 2.05 > 첫 반복 0.10).
  같은 조건의 R4-scvamp(Onsager)는 안정(BLER 0.25). 원문이 보고한 "Onsager vs LLR 차감" 격차가 우리
  설정에서 훨씬 크게 나타나는 것. damping 을 넣어 고치지 않는다 (DECISIONS).
- R3-bigamp 가 9 dB 에서 BLER 0.875 — Table III 의 구조적 i.i.d. prior 한계가 Tp=2 상관 채널에서 크게 작용.

## 남은 것
- A5 완주 -> A6 D1 전 arm (C1~C4, n=640) -> B1 T2 정식 기록 -> B2 GMM 재적합 -> B3 재측정·재학습 -> B4 headline

## BLOCKED
- 없음

## DECISIONS 누적
- 18건 (`conf/DECISIONS.md`)

## 마지막 커밋
- (이 커밋)
