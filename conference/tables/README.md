# 논문 표

| 파일 | 내용 |
|---|---|
| `table1_compact.tex` | 표 I 본문용 — 한 단 (`table`, \footnotesize), 단 높이의 약 0.89. 더 줄이려면 (D) 시드를 본문 한 문장으로 (약 75 pt), a:b 열 삭제 (주석 한 줄) |
| `table1.tex` | 표 I 전체판 — `table*`, 쪽 높이의 약 0.92 → arXiv 확장판용 |
| `table1_sources.md` | 모든 수치의 출처 (값 → 내부 이름 → `docs/RESULTS.md` 절·줄 → 기록 파일:줄; 줄 번호는 main 5f02c87e 기준), 용어 대응, 표에 넣지 않은 캐비엇 |

- **상태: Fable 대조 끝 (2026-10-06 01:41 CDT)** — 수치는 전부 기록과 일치 (작성자 산술 3 곳 재계산 포함). 반드시 2 건 (한 단 판 주석 a 의 32×4 SNR 격자, 시드 3 폴백 주석의 'insuff.' 오용) 과 권고 8 건 (Gaussian prior 사전 등록 표기, UMi SBL ρ 8, GMM tol 정지, 평가 가중치 last-EMA/best, 다중성 문장, 'optimal GMM 아님', 16×4/32×4 R 의 정의 표시 †, 게이트 주석 범위) 을 반영했고, 사소한 지적 7 건 중 5 건을 반영했다. 반영 뒤 두 판 모두 tectonic 컴파일, overfull 0 (한 단 판 252 pt 폭 · 약 595 pt 높이 = 단의 0.89).
- 작성자 판단으로 남긴 것: 표 주석의 '3/3'·'report-only'·'decision SNRs' 는 TERMS.md 의 '그림에서 지우는 것' 목록에 있으나 정의된 표 주석이라 허용 범위; 캡션에 'Kronecker GMM' 을 한 번 밝힐지 (clustered SV 는 full K=256).
- 캡션은 자리표시다 (작성자가 다시 쓴다). 체크 표시는 `\surd` (추가 패키지 없음). tectonic (XeTeX, T1 글꼴 인코딩) 으로 컴파일·폭 확인.
- 정의 주의: 표의 헤드라인 회수율 R = 0.470 은 −3 dB 한 점의 값이고, 그림 F30 / F30top (a) 의 0.509 는 판정점을 합한 R 이다 — 둘이 함께 나오면 본문에서 정의를 구별한다.
