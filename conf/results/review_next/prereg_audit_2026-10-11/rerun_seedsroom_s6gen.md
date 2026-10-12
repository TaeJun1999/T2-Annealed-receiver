### 6.1 결과 (생성기 `prereg_audit_2026-10-11/s6_seedsroom_gen.py`; 수치는 모두 기록 파일에서 읽음 — 전사만, 해석 없음)

**실행·수용** — 드라이버 로그 `logs/run_seedsroom16e4.log` 의 시작 · 태그 종료 · 끝 줄(원문):

- `[seedsroom 10-12 09:26 CDT] start (git 62c24e7e) tags: SRBB16e4s2 SRBB16e4s3 SRPB16e4s2 SRPB16e4s3 cpus 24-47,120-143,72-95,168-191`
- `[seedsroom 10-12 10:14 CDT] SRBB16e4s2 done: ACCEPT: OK -- SRBB16e4s2; ref-arms gate ok: arms differing ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] `
- `[seedsroom 10-12 11:04 CDT] SRBB16e4s3 done: ACCEPT: OK -- SRBB16e4s3; ref-arms gate ok: arms differing ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] `
- `[seedsroom 10-12 12:07 CDT] SRPB16e4s2 done: ACCEPT: OK -- SRPB16e4s2; ref-arms gate ok: arms differing ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] `
- `[seedsroom 10-12 13:16 CDT] SRPB16e4s3 done: ACCEPT: OK -- SRPB16e4s3; ref-arms gate ok: arms differing ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] `
- `[seedsroom 10-12 13:16 CDT] SEEDSROOM_DONE ok=4 fail=0`

| 태그 | runner | 수용 | `--ref-arms all` (점 7 개의 '다른 arm' 집합) | manifest git · config_hash |
|---|---|---|---|---|
| SRBB16e4s2 | 44.0 분 · 448 작업 · 192 워커 (96 스레드에 묶음) | `ACCEPT: OK -- SRBB16e4s2` | shared 2560/2560; ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] | 62c24e7e · 9a1270deac45acb6 |
| SRBB16e4s3 | 45.6 분 · 448 작업 · 192 워커 (96 스레드에 묶음) | `ACCEPT: OK -- SRBB16e4s3` | shared 2560/2560; ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] | 62c24e7e · 9a1270deac45acb6 |
| SRPB16e4s2 | 58.9 분 · 448 작업 · 192 워커 (96 스레드에 묶음) | `ACCEPT: OK -- SRPB16e4s2` | shared 2560/2560; ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] | 62c24e7e · 9a1270deac45acb6 |
| SRPB16e4s3 | 64.0 분 · 448 작업 · 192 워커 (96 스레드에 묶음) | `ACCEPT: OK -- SRPB16e4s3` | shared 2560/2560; ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b'] | 62c24e7e · 9a1270deac45acb6 |

| 태그 | 표 B `b* → V1` 판정점 a:b (p) · pooled (p) | 가드 · 방향 | 라벨 | SNR@0.1 격차 b\*−V1 [90 %] | V1 −3 dB BLER (95 % Wilson) | b\* · genie −3 dB 실패 수 | R (−3 dB) [90 %] | R (판정점 합) [90 %] |
|---|---|---|---|---|---|---|---|---|
| SRB a1 (SRBB16e4; §0 인용) | 209:86 (5.6e-13) · 65:38 (0.01) · 28:5 (6.6e-05) · 302:129 (4.5e-17) | POWERED (3/3), V1 3/3 · b\* 0/3 | (i) | +0.32 [+0.18, +0.45] | 0.275 (0.258, 0.293), 704/2560 | 827 · 299 | 0.233 [0.187, 0.279] | 0.256 [0.212, 0.299] |
| SRB a2 (SRBB16e4s2) | 211:95 (2.9e-11) · 62:30 (0.0011) · 26:5 (0.00019) · 299:130 (2e-16) | POWERED (3/3), V1 3/3 · b\* 0/3 | **(i)** | +0.35 [+0.22, +0.48] | 0.278 (0.261, 0.295), 711/2560 | 827 · 299 | 0.220 [0.174, 0.268] | 0.250 [0.208, 0.293] |
| SRB a3 (SRBB16e4s3) | 207:106 (1.2e-08) · 66:30 (0.00031) · 24:9 (0.014) · 297:145 (4e-13) | POWERED (3/3), V1 3/3 · b\* 0/3 | **(i)** | +0.37 [+0.24, +0.51] | 0.284 (0.266, 0.301), 726/2560 | 827 · 299 | 0.191 [0.141, 0.241] | 0.225 [0.178, 0.270] |
| SRP a1 (SRPB16e4; §0 인용) | 606:62 (4.3e-113) · 321:27 (5.2e-65) · 117:8 (5.9e-26) · 1044:97 (4.1e-201) | POWERED (3/3), V1 3/3 · b\* 0/3 | (i) | +2.01 [+1.78, +2.24] | 0.317 (0.299, 0.335), 812/2560 | 1356 · 428 | 0.586 [0.554, 0.618] | 0.644 [0.620, 0.667] |
| SRP a2 (SRPB16e4s2) | 591:64 (8.5e-108) · 307:18 (4.9e-69) · 112:6 (2.1e-26) · 1010:88 (3.6e-199) | POWERED (3/3), V1 3/3 · b\* 0/3 | **(i)** | +1.95 [+1.73, +2.18] | 0.324 (0.306, 0.342), 829/2560 | 1356 · 428 | 0.568 [0.536, 0.597] | 0.627 [0.603, 0.649] |
| SRP a3 (SRPB16e4s3) | 603:67 (9.2e-109) · 325:18 (5.1e-74) · 115:8 (2.1e-25) · 1043:93 (6e-204) | POWERED (3/3), V1 3/3 · b\* 0/3 | **(i)** | +2.12 [+1.90, +2.35] | 0.320 (0.303, 0.339), 820/2560 | 1356 · 428 | 0.578 [0.544, 0.607] | 0.646 [0.622, 0.668] |

**시드 강건성 라벨 (§1; 분모 3 = a1·a2·a3)**:
- **SRB: "시드 강건 (3/3 (i))"** (시드별 라벨 a1 (i) · a2 (i) · a3 (i)).
- **SRP: "시드 강건 (3/3 (i); b* = 씨앗 초기화 GMM)"** (시드별 라벨 a1 (i) · a2 (i) · a3 (i)).

**보고 전용**:
- SRB 시드 간 산포 (a1 / a2 / a3; max − min): SNR@0.1 격차 +0.32 / +0.35 / +0.37 dB (0.05); V1 −3 dB 실패 수 704 / 711 / 726 (22); R(−3 dB) 0.233 / 0.220 / 0.191 (0.042).
  - 동일예산 GB′ SRB a2 (10-12 09:13 CDT, rc 0; b\* gmm1024 (full K=1024)): median 0.6158 (min 0.5673 · max 1.0104).
  - 동일예산 GB′ SRB a3 (10-12 09:21 CDT, rc 0; b\* gmm1024 (full K=1024)): median 0.6174 (min 0.5698 · max 0.9967).
  - V0 가드 (SRBB16e4s2; `results/guard_D2_SRBB16e4s2.txt`): `C2       -3 M-ours-dscore-C-V0          2560   2560   1.000  8.632e+08`
  - V0 가드 (SRBB16e4s3; `results/guard_D2_SRBB16e4s3.txt`): `C2       -3 M-ours-dscore-C-V0          2559   2560   1.000  3.461e+10`
- SRP 시드 간 산포 (a1 / a2 / a3; max − min): SNR@0.1 격차 +2.01 / +1.95 / +2.12 dB (0.17); V1 −3 dB 실패 수 812 / 829 / 820 (17); R(−3 dB) 0.586 / 0.568 / 0.578 (0.018).
  - 동일예산 GB′ SRP a2 (10-12 10:19 CDT, rc 0; b\* kron (kron K=4096)): median 0.5860 (min 0.5008 · max 0.9740).
  - 동일예산 GB′ SRP a3 (10-12 11:39 CDT, rc 0; b\* kron (kron K=4096)): median 0.5840 (min 0.4943 · max 0.9938).
  - V0 가드 (SRPB16e4s2; `results/guard_D2_SRPB16e4s2.txt`): `C2       -3 M-ours-dscore-C-V0          2560   2560   1.000  7.113e+10`
  - V0 가드 (SRPB16e4s3; `results/guard_D2_SRPB16e4s3.txt`): `C2       -3 M-ours-dscore-C-V0          2560   2560   1.000  1.273e+11`

**§3 예측 채점**:
1. SRB a2·a3 표 B 모두 (i) → **적중** ((i) · (i); 집계 "시드 강건 (3/3 (i))").
2. SRB V1 −3 dB BLER 이 a1 의 95 % Wilson CI [0.258, 0.293] 안 → **적중** (0.278 · 0.284).
3. SRB SNR@0.1 격차의 90 % CI 가 a1 의 [+0.18, +0.45] 와 겹침 → **적중** ([+0.22, +0.48] · [+0.24, +0.51]).
4. SRP a2·a3 표 B 모두 (i) → **적중** ((i) · (i); 집계 "시드 강건 (3/3 (i); b* = 씨앗 초기화 GMM)").
5. SRP V1 −3 dB BLER 이 a1 의 95 % Wilson CI [0.299, 0.335] 안 → **적중** (0.324 · 0.320).
6. SRP SNR@0.1 격차의 90 % CI 가 a1 의 [+1.78, +2.24] 와 겹침 → **적중** ([+1.73, +2.18] · [+1.90, +2.35]).
7. 네 태그 모두 수용 통과(`SEEDSROOM_DONE ok=4 fail=0`), 다른 arm ⊆ {V0, V1, V4, V4b} → **적중** (`SEEDSROOM_DONE ok=4 fail=0`).
8. (채점 제외 — 경로 설명.)
