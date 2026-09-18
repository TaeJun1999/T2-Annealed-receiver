# 작업공간 규약 — Claude ↔ GPT 교대 사용 · 2026-09-18

T2 연구를 두 작업공간에서 **번갈아** 진행한다(동시 진행 없음). 전환 사유는 주로 사용량 한도다.
repo `docs/handoff/WORKSPACES.md`로 커밋해 양쪽이 같은 규칙을 읽게 한다.

---

## 0. 대전제

**정본은 repo 하나다** — `TaeJun1999/T2-Annealed-receiver`.
두 작업공간 모두 읽기 전용이고, 파일을 바꾸는 주체는 언제나 사용자이며 방법은 언제나 push다.
push되지 않은 것은 **임시**이며 근거로 인용할 수 없다.

동시에 돌리지 않으므로 ID 충돌은 사실상 발생하지 않는다. 그래도 D-xx/Q-xx를 제안하기 직전에
repo의 마지막 ID를 다시 읽는다(대화 앞부분에서 읽은 값 재사용 금지).

---

## 1. 진짜 위험: 미push 상태에서의 급정지

한도는 예고 없이 걸린다. 따라서 **전환은 세션 중간에 일어난다고 가정한다.**

### 규칙 A — 결정은 즉시 내보낸다

결정이 확정되거나 Q의 상태가 바뀌면 **그 턴에서 바로** 붙여넣기 블록을 출력한다.
세션 끝에 몰아서 정리하지 않는다. 몰아 쓰면 끊기는 순간 그 세션의 판단이 통째로 날아간다.

```
파일: docs/logs/decision_log.md (말미에 추가)
---
### D-20 (2026-09-2x) ...
```

### 규칙 B — 스위치 노트

작업공간을 바꾸기 전, 사용자가 요청하면 **다섯 줄**을 출력한다. 전체 핸드오프가 아니라 전환용 메모다.

```
switch note (Claude → GPT, 2026-09-2x)
1. 마지막으로 읽은 커밋: XXXXXXX
2. 진행 중이던 것: (마일스톤 §6.x / Q-xx)
3. 미push 확정분: (없음 | 아래 블록 전문 — 반드시 전문, 요약 금지)
4. 다음 액션 한 개:
5. 열어둔 질문: (기본값 포함)
```

받는 쪽은 이 노트를 그대로 붙여넣는 것으로 시작한다. 3번이 "없음"이 아니면 **먼저 push부터** 한다.

### 규칙 C — 새 작업공간의 첫 행동

repo를 읽고 **커밋 해시를 대화에 적는다.** 스위치 노트의 커밋과 다르면, 그 사이에 무엇이 들어왔는지
확인한 뒤 진행한다.

---

## 2. 판정은 시작한 곳에서 끝낸다

사전 등록된 판정(kill test 판독, go/no-go 게이트)은 **한 작업공간에서 시작해 거기서 끝낸다.**
중간에 한도가 걸리면 판정을 내리지 말고 중단한 뒤, 다음 세션에서 같은 쪽으로 돌아와 이어간다.
양쪽이 같은 결과 파일을 각자 읽으면 기준이 미묘하게 갈라지고, 그건 사전 등록의 의미를 없앤다.

현재 해당: `Demo/exp_0925_results.txt` 판독 (기준 D-19 + R1~R7). **아직 한 줄도 읽지 않았다.**

## 3. 세션 핸드오프 헤더

누가 돌렸는지 한 줄로 남긴다. 나중에 결정의 출처를 되짚을 때 쓴다.

```
# T2 세션 핸드오프 #7 — (workspace: GPT · b8afa9f → XXXXXXX) 2026-09-2x
```

## 4. 업로드 파일 (양쪽 동일 원칙: 변하지 않는 것만)

| | Claude | GPT |
|---|---|---|
| 마스터 핸드오프, research companion | 유지 | 업로드 |
| 논문 7편 | 기존 업로드분 정상 동작 | **arXiv에서 새로 받아** 업로드 (기존 `.pdf`는 실제 PDF 아님) |
| 로그 3종, `Demo/*.py`, 결과 txt | **업로드 금지** — repo에서 읽는다 | **업로드 금지** |
| 세션 핸드오프 | repo에 있음 | 커넥터가 못 찾을 때만 최신 1개 |

---

## 부록. 양쪽 지시문에 공통으로 붙일 문단

```
Workspaces
This topic alternates between a Claude project and a GPT project; they are never used at the same
time. The repo TaeJun1999/T2-Annealed-receiver is the single source of truth. Both are read-only;
the user pushes.

- Start each chat by reading the repo and stating the commit hash you read.
- Emit log entries as paste-ready blocks in the turn the decision is made, never batched at the end
  of the session: the user's quota can cut a session off without warning.
- On request, produce a five-line switch note before handing over: last commit read, what was in
  progress, unpushed decisions in full (never summarised), the single next action, and the open
  question with its default.
- Anything not pushed is provisional. Do not cite it as settled.
- Append-only: never renumber or edit an existing D-xx or Q-xx. Reversals are new entries.
- A pre-registered judgement (kill test, go/no-go gate) is finished in the workspace that started
  it. If a session ends mid-reading, stop without a verdict and resume in the same workspace.
```
