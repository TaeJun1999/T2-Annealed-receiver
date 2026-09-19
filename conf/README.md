# conf/ — Conference 축소판 실험 작업 폴더

이 폴더는 **지침만** 담고 있다. 코드는 없다. 코드는 Claude Code가 이 지침을 읽고 `conf/code/`에 만든다.

## 읽는 순서 (전부 읽고 나서 착수할 것)

| # | 파일 | 내용 |
|---|---|---|
| 0 | `00_GOAL.md` | 목표, 완료 정의(DoD), 우선순위, 시간 예산 |
| 1 | `01_RULES.md` | **작업 규칙·자율성 경계·fallback 표·무결성 가드.** 막혔을 때의 행동이 전부 여기 있다 |
| 2 | `02_SPEC_baselines.md` | **baseline** R3(BiG-AMP+BCJR)·R4(3-module SC-VAMP형) 설계 + 원문 알고리즘 |
| 3 | `03_SPEC_ourmodel.md` | **우리 모델**(M-ours) 조립 지침. baseline 테스트 통과 후에 착수 |
| 4 | `04_SPEC_diffusion.md` | **diffusion/score 사다리와 품질 게이트.** 사다리의 심판은 BLER이 아니다 |
| 5 | `05_SPEC_testbed_D2.md` | **주장용 testbed** (sparse specular). D1은 순환 testbed라는 것이 여기 설명돼 있다 |
| 6 | `06_SPEC_runner.md` | arm 목록(testbed별로 다름), 실험 격자, 출력 포맷 |
| 7 | `07_SPEC_tests.md` | 사전 등록 단위 테스트 (전부 PASS해야 본 실행) |
| 8 | `08_SPEC_analysis.md` | 결과 표·그림 사양 |
| 9 | `09_PRIOR_ART_NOTE.md` | 원문 확인 기록 (2604.19061 세 질문, BiG-AMP 오타·구조적 한계). 읽기만 한다 |
| — | `PROMPT.md` | Claude Code 실행 프롬프트 사본 (사용자용) |

## 작업 순서 (절대 규칙)

**Stage A (D1, 계측):** baseline R3·R4 구현 → B·S·C PASS → 우리 모델 조립 → M1~M4 PASS → F2 lemma → $\sigma_t$ 격자 측정 → score 사다리 L1~L6 (게이트 GA~GD) → D1 전 arm 실행
**Stage B (D2, 주장):** testbed 구축·검증 (T2a~T2e, **특히 T2d**) → GMM 재적합 → score 재학습 → **D2 전 arm 실행 = headline**

**시간 제한은 없다. 게이트를 건너뛰지 않는다.** 순서도 바꾸지 않는다 — baseline을 먼저 고정해야 나중에 baseline을 약화시키는 경로가 막힌다.

## 폴더 규칙 (절대 규칙)

- **쓰기는 `conf/` 안에서만 한다.** `Demo/`, `docs/`, repo 루트의 어떤 파일도 **수정·삭제하지 않는다.**
- `Demo/`는 **읽기 전용**으로 import·참조만 한다. 특히 `t2_route_a.py`, `t2_trellis.py`, `t2_gmm.py`는 회귀 테스트 t0/t6이 의존하므로 한 글자도 바꾸지 않는다.
- 예외 단 하나: 작업 종료 시 `docs/EXPERIMENTS.md`에 **한 행만 추가**(날짜·커밋·결과 파일 경로). 기존 행은 건드리지 않는다.

## 만들 하위 폴더 (착수 시 직접 생성)

```
conf/code/      구현 코드
conf/results/   표 형식 결과 텍스트
conf/raw/       npz raw (chunk 재개용)
conf/logs/      stdout/stderr tee 로그
conf/figs/      그림 (있으면)
```

## 사용자에게 보고하는 경로

사용자는 실행 중 서버를 볼 수 없다. 유일한 통신 수단은 **git push된 파일**이다.

- `conf/STATUS.md` — 현재 상태. **최소 30분마다, 그리고 매 phase 종료 시 갱신 후 push.**
- `conf/DECISIONS.md` — 자율적으로 내린 판단을 한 줄씩 append.
- `conf/BLOCKERS.md` — 3회 시도 후에도 해결 못 한 것만. 없으면 만들지 않는다.
- `conf/LADDER.md` — **score 사다리의 모든 시도**(실패 포함) append-only. 지우지 않는다.

이 세 파일이 사용자가 휴대폰에서 읽는 전부다. 짧고 사실만 적는다.
