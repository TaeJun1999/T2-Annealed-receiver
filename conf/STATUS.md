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

갱신 시각 : 2026-09-20 11:35 KST
경과 시간 : 1시간 13분
현재 phase : **A1~A4 게이트 통과 -> A5 (score 사다리) 준비 중**

## 완료
- P0 지침 통독, 자원 측정, 폴더 생성.
- **A1 baseline (게이트 통과)** : `bigamp.py` (R3 = BiG-AMP Table III + BCJR), `scvamp.py` (R4).
  테스트 B1~B6, S1~S7, C1~C6 전부 PASS. 식 (95) 부호 오타는 따르지 않음(B6 가 확장정밀도로 잠금).
  S4 는 지침 내부 불일치라 N/A-BY-CONSTRUCTION + 대체 테스트 S4b.
- **A2 우리 모델 조립 (게이트 통과)** : `arms.py`. **M1 = 0.0, M2 = 0.0** (+ M1b 0.0, M2b 1.3e-13,
  M3 4.3e-16, M4 0). M2 가 exactly 0 이므로 우리 모델 arm 전체 정상 진행.
- **A3 F2 lemma (게이트 통과)** : archive 스크립트 무수정 실행. L1 = 2.33e-15 / 6.89e-10, L2 재현.
  `results/lemma.txt`, `figs/F2_lemma.png`.
- **A4 sigma_t 격자 (게이트 통과)** : `results/sigma_grid.txt`. nu_q 14336 표본(C1·C2 x 7 SNR x 64 trial
  x 16 반복), 1-99 퍼센타일 [2.17e-3, 1.25] 을 덮는 20점 로그 등간격. sigma_t in [3.29e-2, 7.91e-1].
  **이후 변경하지 않는다.**

## 진행 중
- 남은 모듈 4개를 멀티에이전트로 동시 작성 + 적대적 검증 중 (orchestrator 가 게이트는 직접 실행):
  `score.py` (사다리 L1~L6 + 학습 + GA~GD), `d2.py` (sparse specular + T2a~T2e),
  `analysis.py` (표 A/B/C/D), `runner.py` (CLI).

## 남은 것 / 예상
- A5 score 사다리 L1->L6 (칸당 최대 3회, 게이트 GA~GD) — GPU 학습
- A6 D1 전 arm 실행 (C1/C2/C3/C4 x n=640)
- B1 D2 검증 (T2d 가 관문) -> B2 GMM 재적합 -> B3 sigma 재측정 + score 재학습 -> B4 headline

## BLOCKED
- 없음

## DECISIONS 누적
- 13건 (`conf/DECISIONS.md`)

## 마지막 커밋
- de46d6e
