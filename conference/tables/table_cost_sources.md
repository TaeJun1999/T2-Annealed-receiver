# table_cost.tex — 수치 출처 (E4 COST1022)

모든 값은 `conf/results/review_next/cost/` 의 출력 표 줄에서 옮겼다 (−3 dB 행). 반올림: 시간은 D2 두 자리 (s), UMi 한 자리 (s), SBL 두 자리; H 비중은 소수 한 자리 (K 8192 만 99.850 % 를 그대로 99.85 %).

| 표의 값 | 출처 (파일:줄) | 원 값 |
|---|---|---|
| Sparse specular 8×4 · Proposed 1.02 s · 95.9 % · 32 fwd, 1024 VJP | `cost_COST1022_D2.txt:740` | 1015.003 ms · 95.940 % · 32/1024 |
| Sparse specular 8×4 · Matched-scalar 1.01 s · 95.9 % | `cost_COST1022_D2.txt:743` | 1012.897 ms · 95.899 % · 32/1024 |
| Sparse specular 8×4 · GMM K 1024 0.76 s · 94.6 % | `cost_COST1022_D2.txt:742` | 759.228 ms · 94.567 % · K 1024 |
| UMi 32×4 · Proposed 84.9 s · 99.7 % · 32 fwd, 4096 VJP | `cost_COST1022_U32.txt:662` | 84890.042 ms · 99.652 % · 32/4096 |
| UMi 32×4 · GMM K 4096 90.0 s · 99.7 % | `cost_COST1022_U32.txt:664` | 90022.608 ms · 99.692 % |
| UMi 32×4 · GMM K 8192 183.9 s · 99.85 % | `cost_COST1022_U32.txt:665` | 183947.251 ms · 99.850 % |
| UMi 32×4 · SBL (in loop) 0.99 s · 74.7 % · 48 EM | `cost_COST1022_U32.txt:666` | 993.343 ms · 74.728 % · EM=48 |
| 다른 SNR 의 차이 ≤ 1.9 % (최대 1.85 %) | 같은 파일 `:745,747,748` (D2 +6), `:667,669,670,671` (UMi +3) | 최대 b\* 759.228 → 773.246 ms (+1.85 %) |
| 주석 a: UMi 70–91 s · 77–114 s, D2 ≤ 5 % | `cost_{D2,U32}_20261018_222512_CDT.txt` (10-18 확인 실행), `cost_COST1022_*.txt`, `numa_check/cost_NUMA_{a24,b6667}.txt`; DECISIONS 의 E4 NUMA 대조 줄 | V1 70.3–90.6 s, K 4096 76.8–114.1 s; D2 −4.9 … +4.3 % |
| 주석 a: 배치를 기록한 두 대조 실행에서 원격 메모리가 많은 쪽이 10–11 % · 22–30 % 느림, 원인 미분리 | `conf/logs/cost/numa_check.log` (30 s 마다 numa_maps 표본), `numa_check/` 두 출력 | (a) CPU 24: 로컬 node1 64.5–90.9 % (끝 무렵 90 %) — V1 80.8 · 82.0 s, K 4096 87.5 · 86.7 s; (b) CPU 66-67: 로컬 node2 5.3–26.9 % — V1 90.0 · 90.6 s (+11.4 · +10.4 %), K 4096 114.1 · 105.5 s (+30.3 · +21.7 %) (−3 · +3 dB) |
| 주석 b: fwd 32 = 호출당 2 (Jacobian 안 1 + 평균 1) | `conf/code/score.py:1120–1121`; 출력의 COUNT_CHECK 줄 | backbone_forward=32, denoise_calls=16 |

- 조건 (주석 a): `cost_COST1022_*.txt` metadata — affinity [24], torch · BLAS 1 스레드, 개발 시행 2561..2584, CPU 모델 Intel(R) Xeon(R) 6740P.
- 이 표는 판정이 아니다. 성능–시간을 함께 말할 때는 등록 test BLER 이 있는 arm 만 쓴다 (과제 규칙).
