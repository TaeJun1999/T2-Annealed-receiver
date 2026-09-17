# 실험 로그

한 실험 = 한 행. 실행이 끝나면 즉시 추가한다. logs/는 커밋되지 않으므로 이 표가 유일한 영구 기록이다.

| 날짜(KST) | 설정 파일 | seed | 커밋 | GPU | 핵심 지표 | 로그 | 메모 |
|---|---|---|---|---|---|---|---|
| 2026-09-16 14:03 | configs/smoke.yaml | 42 | 03ebd24 | 0 (RTX PRO 6000 Blackwell, sm_120) | loss 2.3325 (1 step), peak mem 64.2 MiB, out.dtype bfloat16 | logs/20260916_1403.log | 환경 검증용 스모크. torch 2.14.0+cu130 / py3.12.14, arch_list에 sm_120 포함 확인. SMOKE OK |
