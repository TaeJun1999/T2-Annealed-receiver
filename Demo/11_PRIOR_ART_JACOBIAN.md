
---

## 할일 1 해소 (2026-09-22 07:35) — GMM arm 은 이미 정확히 인용돼 있다

`Demo/t2_gmm.py:7` 에 이미 있다:
> "Prior art of 'fit a GMM to channel samples, then closed-form CME':
> **Koller–Fesl–Turan–Utschick, IEEE TSP 2022 (arXiv:2112.12499)** [V: abstract]"

즉 baseline 무결성 위험은 **처음부터 없었다.** 게다가 우리 arm 은 그 폐형식 CME 에서 멈추지 않고
`GMMPriorB.ep_site` 로 **모멘트 정합 혼합-EP site** 까지 간다 — 고유값 클리핑(`lam_min`)과 clip 규칙
(`eta`/`mean`)을 갖춘 완전한 site 다. **인용된 선행연구보다 강한 baseline** 이며, 원고에서 그렇게
서술하면 된다: "우리는 GMM CME (Koller et al.) 를 mixture-EP site 로 확장한 것을 baseline 으로 쓴다."

남은 할일은 3건 — (2) 수리 (d) 의 λ 스윕, (3) 등변성 수리 명시, (4) Fesl AISTATS 2025 와의 양립.
