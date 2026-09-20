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

갱신 시각 : 2026-09-20 00:50 KST
경과 시간 : 28분
현재 phase : **A1/A2/A3 게이트 통과 -> A4 (sigma_t 격자 측정) 시작**

## 완료
- P0 지침 통독, 자원 측정, 폴더 생성.
- **A1 baseline 구현 + 게이트 통과** : `conf/code/bigamp.py` (R3 = BiG-AMP Table III + BCJR),
  `conf/code/scvamp.py` (R4 = 3-module SC-VAMP형). 테스트 B1~B6, S1~S7, C1~C6 **전부 PASS**.
  - 식 (95) 부호 오타는 따르지 않음. B6 가 확장정밀도로 잠금 (인쇄된 (95)는 2000점 전부 음수 -> 발산).
  - S4 는 지침 내부 불일치라 `N/A-BY-CONSTRUCTION` (측정 격차 기록) + 대체 테스트 S4b 추가.
- **A2 우리 모델 조립 + 게이트 통과** : `conf/code/arms.py`. M1 0.0 / **M2 0.0** / M1b 0.0 / M2b 1.3e-13
  / M3 4.3e-16 / M4 0 불일치. M2 가 exactly 0 이므로 우리 모델 arm 은 정상 진행.
- **A3 F2 lemma 재현 + 게이트 통과** : `Demo/archive/exp_0915_bcjr_score_check.py` 를 **수정 없이** 실행.
  L1 max|tanh-E| = 2.33e-15 (<=1e-14), Tweedie FD = 6.89e-10 (<=1e-9). L2 재현 (Lc=4 정확, Lc=2 오차 0.495).
  `conf/results/lemma.txt`, `conf/figs/F2_lemma.png`.

## 진행 중
- A4 : sigma_t 격자를 **측정해서** 확정 (04_SPEC §3).

## 남은 것 / 예상
- A4 sigma_t 격자 -> A5 score 사다리 L1~L6 (게이트 GA~GD) -> A6 D1 전 arm 실행
- B1~B4 (D2 검증 -> GMM 재적합 -> score 재학습 -> headline)

## BLOCKED
- 없음

## DECISIONS 누적
- 11건 (`conf/DECISIONS.md`)

## 마지막 커밋
- (이 커밋)
