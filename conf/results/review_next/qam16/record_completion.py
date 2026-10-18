"""Append the local execution ledger only after every required check completes."""
from pathlib import Path
import json,os,subprocess
ROOT=Path('/home/HTJ/t2_wtE5');OUT=ROOT/'conf/results/review_next/qam16'
read=lambda n:json.loads((OUT/n).read_text())
r=read('regression.json');s=read('smoke.json')
assert r['passed'] and len(r['comparisons'])==4 and len(s)==2
assert 'E5_CHECKS_DONE' in (OUT/'suite_continued.log').read_text()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
def stamp(tz):
 return subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],env={**os.environ,'TZ':tz},text=True).strip()
now, kst=stamp('America/Chicago'),stamp('Asia/Seoul')
rows=[f'\n### E5 QAM16 구현 검사 (완료 기록 {now}; {kst})\n',
      '생산 코드 기준 HEAD '+head+' + 미커밋 변경. 사용자 코드 작성 요청 §4(a)의 두 기존 청크만 QPSK test 재계산으로 승인됨. 16-QAM은 개발 시행만. GPU=없음(CUDA_VISIBLE_DEVICES=), CPU=4-5 affinity, BLAS/torch 1스레드, tmux 순차 실행. Demo 잠금 ID 3b5c0a375509 (main 잠금 경로; E5 Demo는 동일 원본 SHA 확인). 입력 파일·SHA는 conf/results/review_next/qam16/input_sha256.tsv.\n',
      '| 검사 ID | 실제 명령/인자 출처 | seed·시행 범위 | 결과 | 로그·원자료 |\n|---|---|---|---|---|']
for x in r['comparisons']:
 rows.append(f"| E5-QPSK-{x['tag']}-{x['mode']} | `checks.py regression` → runner CLI, 전체 argv는 `qam16/regression.json` | 20260926, C2 {x['argv'][x['argv'].index('--snr')+1]} dB, test 0..39 | 14×KEYS_RAW 7 = {x['arrays']} 배열 바이트 불일치 {len(x['mismatches'])}; 현재 메타 키 동일 | `conf/results/review_next/qam16/regression.continued.stdout.log`, `raw_{x['tag']}_{x['mode']}/` |")
for x in s:
 rows.append(f"| E5-QAM16-{x['prior']} | `checks.py smoke` → runner CLI, argv는 `qam16/smoke.json` | 20260926, C2 +9 dB, dev 2560..2563 | 5 arm×16반복 예외 없음; K=90·mod 메타 확인. BLER 표·출력 없음 | `conf/results/review_next/qam16/smoke.continued.stdout.log`, `raw_{x['tag']}_16qam_dev/` |")
 rows.append(f"| E5-NUQ-{x['prior']} | `diag_sigma_coverage.py --mod 16qam --prior {x['prior']} --tag {x['tag']} --snr 9 --skip0 2560 --n 1` (checkpoint/out 전체 인자는 checks.py) | 20260926, C2 +9 dB, dev 2560 | 진단 ν_q와 V1 직접 trace 동일; 직접 trace의 KEYS_RAW도 runner raw 첫 블록과 동일 | `conf/results/review_next/qam16/coverage_{x['tag']}.npz/.json`, `v1_trace_{x['tag']}.npz` |")
rows.append('\n합성/단위 검사 (난수 사용 시 seed 20261017): `checks.py unit`, `interface_checks.py`, `resume_check.py` — Gray 24축 이웃·평균 에너지1·K90 무잡음8블록·3전용arm 거부·블록별 정규화 없음·legacy diagnostic 기본 호출 보존·16qam에서 기존QPSK raw 거부. 결과/명령은 qam16/{unit,interface,resume_check}.stdout.log. 구문·diff 검사도 같은 폴더. 초기 UMi −3 dB 가정은 원 실행 로그의 최저 중앙값 +12 dB로 수정했으며 UMi 평가 전이었다. D2 explicit 부분 실행 중단 로그와 완료 omitted raw를 보존하고 이어 실행했다.\n')
marker='### E5 QAM16 구현 검사 ('
ledger=ROOT/'docs/EXPERIMENTS.md'
assert ledger.resolve().is_relative_to(ROOT)
assert marker not in ledger.read_text()
with ledger.open('a') as f:f.write('\n'.join(rows)+'\n')
dec=ROOT/'conf/DECISIONS.md'
assert dec.resolve().is_relative_to(ROOT)
line=(f'\n[{now} / {kst}] E5 코드 검사 | 사용자 요청 §4(a)에 따른 QPSK 기존 청크 재계산만 허용: B16e4k C2 −3 dB skip0 n40, U28B16e4 C2 +12 dB skip0 n40, mod 생략/명시 두 경로; UMi는 기존 로그의 최소 중앙 청크 비용 SNR로 선택 | 16qam 수신기 평가는 dev2560..2563 (+9 dB), V1 진단은 dev2560 1블록만; 성능·격자 선택 없음 | 근거 qam16/REPORT.md, regression.json, smoke.json, input_sha256.tsv; 이 worktree만 수정, 커밋·main 변경 없음.\n')
assert 'E5 코드 검사 | 사용자 요청 §4(a)' not in dec.read_text()
with dec.open('a') as f:f.write(line)
(OUT/'completion_record.txt').write_text('\n'.join([now,kst,head,'docs/EXPERIMENTS.md 및 로컬 conf/DECISIONS.md에 실행 기록 추가'])+'\n')
print('PASS completion ledger appended locally:',now)
