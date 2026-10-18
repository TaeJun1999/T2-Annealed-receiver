"""Render saved verification evidence only; does not run a receiver or aggregate BLER."""
from pathlib import Path
import json,subprocess
ROOT=Path('/home/HTJ/t2_wtE5'); OUT=ROOT/'conf/results/review_next/qam16'
read=lambda n:json.loads((OUT/n).read_text())
u=read('unit.json'); r=read('regression.json'); s=read('smoke.json'); inp=read('copied_inputs.json')
assert r['passed']
now=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],env={**__import__('os').environ,'TZ':'America/Chicago'},text=True).strip()
L=[f'# E5 시뮬레이터 구현·검사 보고\n\n기록 시각: {now} (`TZ=America/Chicago date` 출력).',
'''수정 위치는 `/home/HTJ/t2_wtE5`뿐이다. 커밋·삭제·push·GPU 계산을 수행하지 않았다. main과 다른 worktree에는 쓰지 않았다. main의 등록 실행은 건드리지 않았다. 검사 입력·raw·로그를 보존했다.

## 변경 사항

| 파일 | 변경과 QPSK 기본 경로 보존 근거 |
|---|---|
| `conf/code/common.py` | `MOD_BITS={qpsk:2,16qam:4}` 추가. 기존 `M_QAM=2`, QPSK 전용 도우미는 그대로 보존. |
| `conf/code/runner.py` | `--mod` 기본 qpsk → task → build_point → 동일 QAMCode를 모든 arm에 전달. receiver run 경로의 `C.M_QAM` 참조 제거. m=2에서는 생성 순서·수치 연산·메타 생성이 기존과 같다. 16qam에만 modulation/payload_bits/protocol/unsupported_arms 추가. 출력 경로·파일명은 기존 tag 규칙. 16qam이 기존 QPSK raw를 이어받는 경우는 입력 오류로 거부. 16qam run 상태에는 BLER를 출력하지 않음. 16qam smoke 기본은 개발 시행으로 이동. |
| `conf/code/arms.py` | code.m=2일 때만 R3/R4를 생성. 명시적 16qam 요청은 CLI 및 직접 run_task 호출에서 입력 로딩·시행 전에 이유와 함께 거부. |
| `conf/code/diag_sigma_coverage.py` | 기존 기본 경로를 보존하고, 명시적 checkpoint/tag/out을 받는 개발 전용 V1 경로 추가. modulation은 runner와 공유. 실제 ν_q와 σ=sqrt(ν_q/2), 체크포인트의 sigma_tag가 지정한 동결 grid, 반복별 finite/below/above/out_fraction을 저장. 기존 출력 파일은 덮어쓰지 않는다. |

로컬 `docs/EXPERIMENTS.md`와 `conf/DECISIONS.md`에는 이 검사 실행 기록만 덧붙였다. main의 같은 파일은 바꾸지 않았다.

파일럿·채널 생성·채널 정규화·SNR(σ²=10^(−SNR/10))·T=16·Tp=4는 바꾸지 않았다. Ns=48, m=4, rate 1/2, ν=6이므로 K=48·4/2−6=90이다.

## arm 지원 상태

| arm | 16-QAM 상태 | 근거 |
|---|---|---|
| V1 (`M-ours-dscore-C-V1`) | 지원, 두 셀 개발 스모크 통과 | RouteAClip → RouteA.run → code.decode. 채널 score/Jacobian은 constellation을 직접 참조하지 않는다. |
| b* (`M-ours-bstar`) | 지원, 두 셀 개발 스모크 통과 | Module H만 GMM ep_site로 교체; 동일한 code.decode/soft_symbols 경로. |
| R2 (`R2-ours-G`) | 지원, 두 셀 개발 스모크 통과 | 동일 RouteA, Module H=Gaussian. |
| R5-genie | 지원, 두 셀 개발 스모크 통과 | genie 분기는 Hc=H, R=σ²I로 검출기만 교체; 동일 일반-m decoder 사용. |
| V1-pilot | 지원, 두 셀 개발 스모크 통과 | PilotSitePrior가 채널 belief를 파일럿에서 한 번 고정; 이후 동일 일반-m 복호기. |
| R3-bigamp | 거부 | bigamp.py의 qpsk_posterior, bit_llrs_from_pmf가 두 비트 QPSK 전용. |
| R4-scvamp / R4-llr | 거부 | scvamp.py의 CONST_QPSK, qpsk_channel_llr, soft_qpsk_from_llr 및 두 비트 message. |
| 그 밖의 RouteA 기반 R0/R1·GMM·score·ablation | 코드상 일반 m 사용, 생성 시 동일 QAMCode 확인 | 추가 arm의 16-QAM 수치 검사는 수행하지 않았다. ALD 표는 modulation에 따라 달라지는 시행 스트림으로 별도 생성해야 하며, 기존 QPSK ALD 표의 재사용을 검증하지 않았다. |

`--arm` 없이 build_point(16qam)를 호출해도 위 세 QPSK 전용 arm은 생성되지 않는다. `meta|unsupported_arms`는 이름과 이유를 JSON으로 남긴다. Demo의 QAMCode.decode는 SymbolTrellis.bcjr(return_info=True) → soft_symbols(P, self.st.CONST) → Lu.reshape(-1)이며, soft_symbols는 P@CONST 및 P@abs(CONST)^2−abs(mean)^2를 사용한다. 새 복조기를 재구현하지 않았다.

## 실행으로 확인한 검사

기본 실행은 `run_checks.sh`/`continue_checks.sh`에 있고 stdout/stderr를 같은 디렉터리에 보존했다. 모든 무거운 검사는 `CUDA_VISIBLE_DEVICES=`, `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=NUMEXPR_NUM_THREADS=1`, `taskset -c 4-5 /home/HTJ/miniforge3/envs/torch/bin/python -B`로 순서대로 실행했다. 실제 환경·affinity·tmux와 GPU 프로세스 조회는 `resources.log`에 있다.

### QPSK raw 재계산 (체크포인트 재학습 아님)

회귀의 정확한 CLI argv와 출력 경로는 `regression.json`에 있다. 검사용 harness는 `d_raw` 출력 위치만 qam16 하위로 격리했다. 일반 runner의 tag 규칙이나 receiver 연산은 바꾸지 않았다.

| 기준 청크 | mod | 비교 배열 | 불일치 | 현재 HEAD 기준 메타 키 집합 |
|---|---|---:|---:|---|''']
for row in r['comparisons']:
 L.append(f"| {Path(row['reference']).name} | {row['mode']} | {row['arrays']} (14 arm × 7) | {len(row['mismatches'])} | {'동일' if row['meta_keys_equal_current_control'] else '다름'} |")
L += ['''
두 셀 각각 `--mod` 생략과 `--mod qpsk` 사이에는 KEYS_RAW 외의 모든 저장 필드도 바이트 동일했다. NaN도 array.tobytes()로 비교했다. 기존 D2 raw와 현재 메타의 차이는 이미 HEAD에 있던 `meta|stagec_ckpt_id` 한 키이고, UMi raw의 키 집합은 같다. 이번 변경으로 QPSK 메타 키는 추가되지 않았다. 현재 수정 전 메타 집합은 `control_runner.py`의 build_point로 확인했으며, 이 control을 위해 test 시행을 따로 평가하지 않았다.

UMi의 값싼 SNR은 원 실행 로그의 64개 청크/SNR 실행시간 중앙값으로 정했다. +12 dB가 최저(1203 s)였고, 그 점의 skip0 청크를 사용했다 (`umi_original_chunk_cost.json`). 처음에는 −3 dB를 가정했으나, UMi 평가를 시작하기 전에 로그를 확인해 바로잡았다. 이 과정에서 첫 D2 explicit QPSK 부분 실행을 중단하고 다시 실행했다. 완료된 D2 omitted raw는 재사용했고, 중단 로그는 `regression.stderr.log`의 KeyboardInterrupt로 남겼다. 미완료 raw는 저장되지 않았으며 기존 산출물을 삭제하지 않았다.

회귀를 시작한 뒤 추가한 생산 코드 차이는 16qam의 기존 raw 검사·신규 진단의 checkpoint-prior 검사와 legacy analysis 거부 검사다. 이들은 QPSK 수신기 수치 연산을 바꾸지 않는다. 최초 D2 omitted raw는 16qam raw 거부 검사를 추가하기 전에 계산했고, 재개한 explicit/UMi 회귀에는 그 검사와 진단 prior 검사를 포함한 코드가 로드되었다. 분석 거부 경로는 UMi 회귀 도중 추가되어 해당 회귀 모듈에 로드되지 않았으며, 별도 합성 검사로 확인했다 (analysis_guard_complete.json, 추가 수신기 실행 없음). 모든 QPSK 회귀의 수치 연산 경로는 최종 코드와 같다. 시작 시·최종 코드 SHA는 execution_context.txt/continuation_context.txt/final_code_sha256.txt에 보존했다.

### Mapping·무잡음 왕복·거부·인터페이스
''',f"- Gray 축 이웃 {u['gray_axis_edges']}쌍: 모두 Hamming distance 1. 16점 고유, bit→symbol→bit 왕복 통과.",
 f"- 평균 에너지: 유리수로 {u['exact_mean_energy']}, float64로 {u['float_mean_energy']}. 정규화는 √10 한 번이며 블록별 재정규화 없음.",
 f"- K=90, Ns=48 무잡음 encode→decode {u['noiseless_blocks']}블록: 모두 정보 비트 정확 복원. 관측에 잡음을 더하지 않았고, BCJR likelihood의 분산은 {u['bcjr_likelihood_variance']}로 지정했다. τ=0은 우도 식의 나눗셈이 정의되지 않아 사용하지 않았다.",
 '- `interface.stdout.log`: all-zero packet의 전송 블록 평균 에너지 0.20000000000000004가 그대로 보존됨. 기존 ν_q diagnostic CLI의 기본 호출/명시 qpsk 호출은 수정 전 HEAD와 같은 sentinel 호출·출력 (추가 test 시행 평가 없음).',
 '- `unit.stdout.log`: 세 전용 arm 모두 argparse exit 2, 이유 포함, raw 디렉터리 생성 전 거부. 직접 run_task도 거부.',
 '- `resume_check.stdout.log`: synthetic QPSK raw는 QPSK에서 기존처럼 skip하고, 16qam에서는 덮어쓰거나 완료로 처리하지 않고 거부.',
 '''
### 16-QAM 개발 스모크 (성능 평가 아님)

| 셀 / prior | SNR | 개발 trial | arm × 반복 | 결과 | b* |
|---|---:|---|---|---|---|''']
for row in s:
 L.append(f"| C2 / {row['prior']} | +{row['snr']} dB | {row['skip']}..{row['skip']+row['n']-1} | 5 × 16 | 예외 없음; 모든 KEYS_RAW 배열 (4,16); K=90·변조 메타 확인 | {row['bstar']} {row['kron_K']} |")
L += ['''
raw의 modulation=16qam, payload_bits=90, protocol=E5-qam16-v1 및 unsupported_arms를 확인했다. R5-genie는 채널을 추정하지 않아 NMSE가 의도적으로 NaN이며, 이 기존 규약을 확인했다. 나머지 arm의 NMSE와 모든 arm의 나머지 KEYS_RAW는 유한값을 확인했다. BLER 표를 만들거나 16-QAM BLER를 출력하지 않았다. `smoke.json`과 `raw_*_16qam_dev/`가 원자료다.

V1 진단은 셀마다 개발 trial 2560 한 블록만 실행했다. `coverage_*.npz`의 ν_q가 `v1_trace_*.npz`의 직접 기록과 정확히 같았고, 그 직접 기록의 KEYS_RAW도 runner raw 첫 블록과 바이트 동일했다. runner의 KEYS_RAW에는 ν_q가 없어 이 연결을 별도 확인했다. 이는 진단 연결의 스모크이며 범위 밖 비율의 안정된 분포를 추정한 결과가 아니다. 아래 진단 명령의 끝 파일명은 재실행할 때 새 이름을 사용해야 한다.

```bash
CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \\
taskset -c 4-5 /home/HTJ/miniforge3/envs/torch/bin/python -B conf/code/diag_sigma_coverage.py \\
  --mod 16qam --cell C2 --prior UMi28 --tag U28B16e4 --ntrain 160000 \\
  --stagec-ckpt /home/HTJ/t2_wtE5/conf/ckpt/d2sx_UMi28_N160000_a1_best.pt \\
  --snr 9 --skip0 2560 --n 1 \\
  --out /home/HTJ/t2_wtE5/conf/results/review_next/qam16/coverage_U28B16e4.npz
```

### Seed와 입력 routing

seed 식 `default_rng([20260926, TBID[D2], PID[prior], 8,16,4,int(snr)+100])`은 바뀌지 않았다. 변조 간 채널 실현은 아래 저장된 SHA 비교로 확인했다. skip 이전은 채널·비트·잡음 스트림만 재생성하고 복호하지 않았다.
''']
for row in s:
 same=row['seed']['same_channel_at_trial']
 L.append(f"- {row['prior']}: trial별 QPSK/16qam H 일치 = {same}. 채널 SHA 원값은 smoke.json. 실행으로 확인한 H 일치는 위에 열거한 trial만의 비교다. 코드 판독상 비트 길이 42→90에 따라 동일 스트림의 이후 RNG 소비 위치가 달라지며, 채널·비트·잡음을 변조 간 공통 스트림으로 따로 분리하지 않았다. 잡음 자체의 수치 일치는 별도로 검사하지 않았다. 같은 변조 안의 다섯 arm은 동일 (H,u,perm,Y)를 공유한다.")
L += ['''
체크포인트는 기존 raw의 경로 basename 및 기존 run manifest의 sha256[:16]과 대조했다. 모든 fit 입력은 main 실제 파일과 전체 SHA를 대조했고, b*·kron_K 및 모든 ll_val도 기준 raw와 일치했다. UMi8의 b*는 kron 4096이라는 기존 격자 끝의 한정도 유지했다. 새 fit이나 격자 확장은 수행하지 않았다. UMi의 last sibling은 best checkpoint의 학습 시간 메타를 읽기 위해서만 복사했으며 평가 가중치는 best이다.

| 평가 체크포인트 | 전체 SHA-256 |
|---|---|''']
for row in s:
 L.append(f"| {row['prior']} | `{row['checkpoint_sha256']}` |")
L += [f"\n입력 목록은 `input_sha256.tsv`/`copied_inputs.json`에 모든 파일과 SHA를 기록했다. 전체 {len(inp)}개 중 이번에 cp -L 복사한 파일은 {sum(x['action'].startswith('cp') for x in inp)}개, 기존 추적 파일 SHA 확인은 {sum(not x['action'].startswith('cp') for x in inp)}개다. 초기 준비한 UMi −3 dB raw 1개는 보존했지만 평가에 사용하지 않았다. 새 심볼릭 링크는 만들지 않았다.\n",
'''## 보존 확인

`verify_preserved.py` → `preservation.stdout.log` / `protected_after.json`: main HEAD·index·conf/code·Demo 보존, E5 HEAD·Demo 보존, staged diff 없음, 준비 입력 36개 전체 SHA 불변을 확인했다. 검증은 읽기 전용 git 명령(GIT_OPTIONAL_LOCKS=0)과 파일 SHA로 수행했다. 실제 생산 코드 변경은 `implementation.diff`와 `final_code_sha256.txt`로도 검토할 수 있다.

## 남은 불확실성·독립 검토

- 시행 4블록/셀과 진단 1블록/셀은 예외·shape·배선 검사다. BLER/이득/일반적 수치 안정성은 여기서 확인하지 않았다. test 2560블록 평가·격자 결정·재학습은 하지 않았다.
- 기존 UMi `budget|V1` 문자열의 N_train=28160000은 learned_budget가 rung `D2SXUMi28160000`에서 연속 숫자를 읽는 기존 표시 오류다. meta|ntrain=160000, 동결 manifest, 경로·SHA와 fit 격자를 대조했다. QPSK 메타 호환 범위 때문에 이 기존 표시 코드는 바꾸지 않았다.
- Demo/QAMCode/BCJR를 수정하지 않았다. 생산 시뮬레이터의 독립 golden 검토와 사용자 잠금은 아직 하지 않았다. 이 검사들은 구현자 검증이며 그 절차를 대신하지 않는다.
- 기존 analysis.py는 K=42를 가정하므로 16qam 성능 표 작성에 사용하지 않았다. runner에서 `--mod 16qam analysis`를 거부하며, `--mod`를 생략해도 raw 메타가 16qam이면 표를 쓰기 전에 거부한다 (analysis_guard_complete.json). 이번 작업은 표 도구의 16qam 확장을 포함하지 않는다.
- 실제 실행으로 확인한 것은 위 JSON·raw·로그가 뒷받침하는 항목뿐이다. 그 밖의 RouteA arm의 일반-m 지원은 코드 판독이며 추가 실험으로 확인한 주장으로 쓰지 않는다.
''']
copy_lines = ['### 이번에 복사한 파일과 SHA-256',
              '상대 경로는 source `/home/HTJ/t2/`와 destination `/home/HTJ/t2_wtE5/`에 공통이다. 기존 추적 입력 16개의 SHA와 실제 링크 대상은 input_sha256.tsv/copied_inputs.json에 별도로 있다.',
              '| 상대 경로 | SHA-256 | 사용 |', '|---|---|---|']
for item in inp:
    if item['action'].startswith('cp'):
        rel = Path(item['destination']).relative_to(ROOT)
        used = '사용' if item.get('used', True) else '미사용·보존'
        copy_lines.append(f"| `{rel}` | `{item['sha256']}` | {used} |")
body = '\n'.join(L)
body = body.replace('\n## 보존 확인', '\n' + '\n'.join(copy_lines) + '\n\n## 보존 확인', 1)
(OUT/'REPORT.md').write_text(body+'\n')
print(OUT/'REPORT.md')
