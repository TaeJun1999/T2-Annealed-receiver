# 적대적 사전 검토 — NEXT_EXPERIMENTS_FIGHSYDMI16e4.md 초안 v1 (미커밋; sha256[:16] af22026170f73ae5, mtime 2026-10-12 22:04:26 CDT) + `code/run_fighsydmi16e4.sh` (미추적; sha256[:16] 838b902a43cb4634, mtime 10-12 22:01:59 CDT) + `code/ald.py` 작업본 (sha256[:16] d4f8a9bc1d83eb1a; `hisnr5`)

검토자: Claude Fable 5.1 서브에이전트, 2026-10-12 22:38 CDT 종료. HEAD 42fd4e03 (검토 내내 그대로). 읽기 전용: `bash -n`, `diff`, sha256sum, 읽기 전용 git, 기존 raw · npz 읽기, `eval_accept.py` 를 기존 raw 에 읽기 전용으로(출력은 스크래치), 스크립트의 일부를 스크래치 사본·모래상자에서 실행(`# PRE` 줄, 단계 C–R 의 제어 흐름), `ald._regen_one` 의 메모리 안 호출. CPU `taskset -c 0-15`, `python -B`, GPU 미사용(`nvidia-smi` 조회만). `code/run_fighsydmi16e4.sh` 와 `runner.py run` 은 돌리지 않았다. 검토 끝에 `conf/code` · `Demo` · `DECISIONS.md` 의 `git status` 는 시작 때와 같다(` M code/ald.py`, `?? code/run_fighsydmi16e4.sh`). 근거 파일: 이 디렉토리의 `review_FIGHSYDMI16e4_*.{py,out,txt}` (스크래치 원본은 `…/scratchpad/review_fighsy/`).

## 판정

**수정 후 실행 가능** — MUST 1 · SHOULD 9 · NIT 9.

스크립트는 부모(`run_fighsdmi16e4.sh`) 대비 바뀐 줄이 모두 의도대로 동작한다: `bash -n` 통과, 18 열 `read`(빈 FLAGS 포함), 대조 태그 `FYC…`/`FZC…`, 전제 줄 가운데 지금 걸리는 것은 실행 커밋이 해결할 셋뿐, 백그라운드 EARLY 와 `wait $EP` 의 순서, 한 추정 파일을 두 ALD 행이 나눠 쓰는 경로, `--resume` 경로를 모래상자에서 확인했다. chunk 400 은 코드 판독과 `CHUNK-INVARIANCE: OK` (rc=0) 로 뒷받침된다. 비용 모형의 수는 탐침·로그에서 다시 계산해 모두 맞았다.

MUST 는 **59 시간의 맨 끝 단계**에 있다: `eval_accept.py --ref-raw raw_FZDMIB16e4` (FZALDDMI 의 genie 재생 검사)가 chunk 400 기준 raw 에서 **약 590 GiB** 를 잡는다(측정 201 KiB/시행 × 3,072,000). 연결 시험(800 시행)으로는 드러나지 않는 크기 문제다. 두 군데 고치면 28 초 · 3.7 GiB 가 된다(출력 바이트 동일 확인).

---

## MUST

### M-1 `eval_accept.py` 의 genie 재생 검사가 chunk 400 기준 raw 에서 약 590 GiB 를 쓴다 (FZALDDMI 의 수용 — 실행의 마지막 단계)
- 위치: `code/eval_accept.py` 109–113 행 · 115–127 행; 호출은 스크립트 221–223 행(`RARG="--ref-raw raw_$REF"`, FZALDDMI 의 REF = FZDMIB16e4).
- 원인: `rows[s + i] = {k: cut(z[k], i) for k in rk}`. `z` 는 `NpzFile` 이라 `z[k]` 를 부를 때마다 배열을 새로 풀고, `cut` 은 그 배열의 **view** 를 돌려준다 → 시행 하나 × 키 하나마다 청크 배열 전체가 살아남는다. chunk 40 이면 5,120 B, **chunk 400 이면 51,200 B** (× 키 4 × 기준 raw 의 모든 시행 — 겹치는 327,680 시행만이 아니라 3,072,000 시행 전부를 `rows` 에 넣는다).
- 측정(`review_FIGHSYDMI16e4_replay_mem.{py,out}`; 같은 줄을 그대로 옮겨 `raw_ZQDRY` 의 chunk-400 파일로): **201.4 KiB/시행, 623 µs/시행 → n = 3,072,000 이면 약 590 GiB, `rows` 만드는 데만 약 32 분**(한 스레드, 메모리 할당 지연 제외). chunk 40 기준은 21.8 KiB/시행 — FYALDDMI 대 `raw_FYDMIB16e4` 는 6.8 GiB · 1.2 분이라 문제없고, 지금까지의 실행도 작았다(FHALDDMI 재실행 측정 0.49 GiB; 점당 n = 81,920 이던 FIGHSX 는 계산상 1.7 GiB).
- 왜 중요한가: 서버는 총 1007 GiB(가용 990 GiB, cgroup 한도 없음)라 "들어갈 수도" 있지만 공유 서버의 RAM 59 % 를 예고 없이 잡는다. 다른 사용자의 사용량에 따라 OOM → `eval_accept` rc ≠ 0 → `FZALDDMI INVALID: acceptance failed` (§1: 다시 돌리려면 사용자 승인) — `--resume` 도 같은 벽에 다시 부딪힌다. 51 시간 행 자체(raw)는 남지만 +15 dB 의 ALD 점을 잃고, 최악에는 다른 사용자의 작업을 건드린다.
- 연결 시험이 못 본 이유: `dryrun_FIGHSYDMI.out` 의 기준 raw 는 800 시행(원본 0.21 GiB, 고친 것 0.06 GiB — `review_FIGHSYDMI16e4_eval_accept_patch_test.out`).
- **고칠 것 (A, 권장 — 등록된 코드 변경 둘째)**: 키를 시행마다가 아니라 파일당 한 번 읽는다(`review_FIGHSYDMI16e4_eval_accept_patch.txt` 가 diff).
  ```python
                  rows = {}
                  for s, n, f in ref[key]:
                      with np.load(f) as z:
                          zz = {k: z[k] for k in rk}              # one read per key and file (a per-trial z[k] kept one whole chunk array alive per trial and key)
                      for i in range(n):
                          rows[s + i] = {k: cut(zz[k], i) for k in rk}
                  worst, shared, missing = {}, 0, set()
                  for s, n, f in ch:
                      with np.load(f) as z:
                          zz = {k: z[k] for k in rk if k in z.files}
                      for i in range(n):
                          if s + i not in rows:
                              bad.append(f"{tag} {key}: trial {s + i} absent from {a.ref_raw}"); continue
                          shared += 1
                          for k in rk:
                              if k not in zz:
                                  missing.add(k); continue
                              x, y = cut(zz[k], i), rows[s + i][k]
                              d = float(np.max(np.abs(np.nan_to_num(x, nan=1e300) - np.nan_to_num(y, nan=1e300))))
                              if d != 0.0:
                                  worst[k.split("|")[0]] = max(worst.get(k.split("|")[0], 0.0), d)
  ```
  스크래치 사본으로 확인한 것: (1) `--tag FHALDDMI … --ref-raw raw_FHDMIB16e4` 의 출력이 원본과 **바이트 동일**(`ACCEPT: OK`; 40.8 s → 5.5 s, 최대 RSS 0.49 → 0.09 GiB); (2) 실패해야 하는 경우(`--ref-raw raw_FHALDSRB`)의 출력도 바이트 동일(rc 1, "arms differing ['R5-genie']"); (3) `ZQDRYA` 대 `raw_ZQDRY` (chunk 40 대 400) `ACCEPT: OK`; (4) FZ 규모(기준 7,680 파일 × 400 시행 + 태그 8,192 파일 × 40 시행, 합성 반복)에서 **28 초 · 3.7 GiB**.
  등록에 넣을 문장(§1 "ALD" 칸의 "코드 변경 하나" 를 "코드 변경 둘" 로 하고, "수용" 칸에): "**코드 변경 둘째**: `code/eval_accept.py` 의 재생 검사(109–127 행)가 청크 파일의 키를 시행마다가 아니라 파일당 한 번 읽는다 — 판정·출력 불변(검토가 FHALDDMI 의 통과 출력과 일부러 틀린 기준 raw 의 실패 출력이 바이트 동일함을 확인). 이유: chunk 400 기준 raw(FZDMIB16e4, 3,072,000 시행)에서 원래 코드는 시행마다 청크 배열을 붙들어 약 590 GiB 를 쓴다." 고친 파일의 sha 를 §5 에 적는다.
- (B, 코드를 건드리지 않는 대안 — 권하지 않음) 스크립트에서 FZALDDMI 의 `--ref-raw` 를 `raw_FZDMIB16e4` 의 처음 820 청크만 담은 보기 디렉토리로 준다: 그래도 약 63 GiB · 3–4 분이고 스크립트가 복잡해진다.

---

## SHOULD

### S-1 백그라운드 EARLY 작업이 스크립트보다 오래 살 수 있다 (스크립트 204–205 · 229 행)
- `wait $EP` 는 ALD 행이 관문을 통과했을 때만(214 행) 불린다. ALD 행이 그 앞에서 SKIP 되면(기준 행 미수용, `--resume FZALDDMI` 단독 등) 스크립트는 `FIGHS_DONE` 을 찍고 끝나는데 EARLY 의 regen / GPU 추정(약 35 분)은 계속 돈다. 모래상자 재현(`review_FIGHSYDMI16e4_checks.out` 의 flow_sim): `FIGHS_DONE ok=0 fail=1` **뒤에** `FZALDDMI ALD PILDMI: reusing …` 줄이 찍힌다.
- 왜: `FIGHS_DONE` 을 보고 시작한 `--resume` 이나 main 커밋이 아직 쓰이고 있는 `ald_PILDMI_hisnr5.npz` / 그 `prov git` 과 경합한다(반쯤 쓰인 npz 는 `np.load` 가 실패해 "stale" ABORT — 받아들여지지는 않지만 행이 멈춘다).
- 고칠 것(229 행 앞에 한 줄; 스크래치 사본 `bash -n` 통과, 모래상자에서 EARLY 줄이 `FIGHS_DONE` 앞으로 옴):
  ```
  wait $EP 2>/dev/null   # the background EARLY job never outlives the script (FIGHS_DONE is the last line of the log)
  log "FIGHS_DONE ok=$OK fail=$FAIL"
  ```

### S-2 51 시간 행을 헛돌리지 않게 하는 이른 확인 셋 (스크립트 213 행 뒤 + §1 "순서·자원")
- (a) **FYDMIB16e4 가 수용되지 않았는데 FZDMIB16e4 를 시작한다.** 두 행은 chunk 크기만 다른 같은 수신기·같은 도구다 — FY 의 수용 실패(`+dirty`, meta, 청크 계획)는 대개 FZ 에도 그대로 일어나고 51 시간 뒤에야 보인다. 213 행 뒤에 한 줄(스크래치 사본 `bash -n` 통과, 모래상자 확인):
  ```
  [ $TAG = FZDMIB16e4 ] && sel FYDMIB16e4 && [ "${ACC[FYDMIB16e4]}" != 0 ] && { log "$TAG SKIP: FYDMIB16e4 (the same receivers and tools, 5.5 h) was not accepted in this call -- the 51 h row is not started before the cause is known (--resume)"; FAIL=$((FAIL+1)); continue; }
  ```
  (스크립트를 그대로 두려면 같은 내용을 §1 의 운영 규칙으로: "FYDMIB16e4 의 수용이 rc ≠ 0 이면 FZ 를 멈추고 원인을 본다".)
- (b) **`run|git` 의 `+dirty` 는 워커가 첫 청크를 저장할 때 한 번 정해지고 그 워커의 모든 청크에 찍힌다**(`runner._git_head` 의 전역 캐시; 워커는 51 시간 내내 산다). FZ 행에서 그 시점은 행 시작 약 1.2 시간 뒤(192 워커가 거의 동시에) — 그때 `conf/code` · `Demo` 에 미추적 파일 하나만 있어도 전 청크가 `+dirty` 가 되고 수용 (f) 는 51 시간 뒤에 실패한다. §1 에 넣을 문장: "FZ 행의 첫 청크들이 나오면(행 시작 약 1.3 시간 뒤) `run|git` 만 읽어 `+dirty` 가 없는지 본다(결과 키는 읽지 않는다): `python -B -c "import glob, numpy as np; fs = sorted(glob.glob('raw_FZDMIB16e4/D2_*.npz')); print(len(fs), sorted({str(np.load(f)['run|git']) for f in fs}))"`; `+dirty` 가 있으면 멈추고 사용자에게 알린다."
- (c) **워커가 죽으면 `mp.Pool.imap_unordered` 는 끝나지 않는다**(잃은 작업이 돌아오지 않는다 — 상속된 성질이지만 51 시간 행에서는 노출이 크다). §1 에: "FZ 행의 진행 줄은 약 1.2 시간마다 192 줄씩 는다; 2.5 시간 넘게 줄이 늘지 않으면 멈춘 것으로 보고 tmux 를 끝낸 뒤 `pgrep -f 'code/runner[.]py run'` 이 비었는지 확인하고 `--resume`."

### S-3 머리말 "작성 시점 공개" 의 측정 문장이 사실과 다르다 ("모두 메모리 안에서, raw 디렉토리에 쓰지 않음")
- `dryrun_FIGHSYDMI.out` 의 연결 시험은 `runner.py run --tag ZQDRY / ZQDRYA` 로 **raw 디렉토리 둘을 썼다**(`raw_ZQDRY`: +15 dB 시행 10000..10799, chunk 400; `raw_ZQDRYA`: 10000..10079, chunk 40; `results/gmm_fits_D2_ZQDRY{,A}` 심볼릭 링크) — 문장의 목록에도 없고 §1 어디에도 인용되지 않는다. 또 `chunk_invariance_FIGHSYDMI.out` 은 시행 10000..10399 의 arm 별 실패 수 한 줄을 찍는다("결과 수치는 보지 않음" 과 글자 그대로는 어긋난다 — 이미 본 시행이라 새 정보는 없다).
- 바꿀 문장: "등록 전에 한 측정 — (가) 메모리 안에서만(raw 디렉토리에 쓰지 않음): arm 별 시간(시행 10000..10039, +15 dB), 건너뛰기 비용(Perfect CSI 만, skip 10000 과 410000 — 뒤쪽은 이 실행의 범위 안인 시행 410000..410039 를 계산했으나 결과는 출력하지 않았다), ALD 한 배치의 시간·GPU 메모리(…, 출력은 버림), chunk 불변성 확인(§1; 이미 본 시행 10000..10399 의 arm 별 실패 수 한 줄을 출력한다 — 새 정보 없음). (나) 스크래치 태그로 raw 를 쓴 연결 시험 `prereg_reviews_2026-10-11/dryrun_FIGHSYDMI.out`: Perfect CSI 만, +15 dB, 시행 10000..10799 (`raw_ZQDRY`, chunk 400) 와 10000..10079 (`raw_ZQDRYA`, chunk 40) — 모두 이미 본 시행; runner → `eval_accept --chunk 400` → chunk 가 다른 기준 raw 와의 재생 검사 → `load_raw` 를 지났다. `raw_ZQDRY*` 와 `results/gmm_fits_D2_ZQDRY*` 는 남겨 둔다(이 실행의 태그·전제와 겹치지 않는다). 시행 30480 이후의 결과 수치는 어느 측정에서도 보지 않았다."

### S-4 "사용자에게 알렸다" 는 문장 — 세션 기록에서 확인되는 범위로 (머리말 '사용자 지시' 항목)
- 확인된 것(세션 기록 `b187bcb3….jsonl`): 질문과 선택지 넷의 문구, 사용자의 답 "+15 dB까지 시도" (10-12 21:41 CDT), 질문 머리의 "CPU는 지금처럼 96 스레드 기준" — 초안의 인용과 글자까지 같다.
- 확인되지 않은 것: "'언제쯤 끝날거 같아?' 에 일정…과 두 가지(희소 곡선은 n = 20480 유지, Annealed Langevin 은 약 33 만 시행)를 알렸다". 기록에서 그 내용은 **thinking(서술) 블록 하나**(10-12 21:57 CDT)에만 있고 본문 text 블록에는 없다. 그 뒤의 본문 메시지(10-12 22:14 CDT)는 "+15 dB 행 약 51 시간, 전체 약 59 시간, 최종 10-15 10:30 CDT 쯤, +12 dB 중간 그림 10-13 06:00 CDT 쯤" 을 알렸지만 **희소 곡선 n = 20480 유지와 ALD 33 만은 적지 않았다**. 서술 블록이 사용자 화면에 보였는지는 검토가 판단할 수 없다. 사용자가 고른 선택지 문구에도 곡선마다 n 이 다르다는 말은 없다.
- 또 선택지 ① 에는 세션의 "(Recommended)" 표시가 있었다(사용자는 권장과 다른 ② 를 골랐다) — 초안은 이를 적지 않았다.
- 고칠 것: (1) 실행 시작을 알리는 본문 메시지에 "희소 세 곡선은 +12 · +15 dB 에서 n = 20480 그대로, Annealed Langevin 은 두 SNR 모두 약 33 만 시행, main 커밋은 약 2.5 일 동결(S-8)" 을 적는다. (2) 문장을: "…사용자는 **"+15 dB까지 시도"** 를 골랐다(선택지 ① 에 세션의 '(Recommended)' 표시가 있었다; 선택지 문구: …). 이어 사용자 "언제쯤 끝날거 같아?" 뒤 세션의 진행 서술(세션 기록의 서술 블록, 10-12 21:57 CDT — 화면 표시 여부는 기록으로 확인되지 않는다)에 일정(…)과 두 가지(…)가 있고, 본문 메시지(10-12 22:14 CDT)가 '전체 약 59 시간, 최종 10-15 10:30 CDT 쯤' 을 알렸다; 두 가지는 실행 시작 알림에 다시 적는다(세션 기록 기준)." 그러면 "(실행 커밋 때 다시 알린다)" 는 "(10-12 22:14 CDT 에 알렸다)" 로 바꿀 수 있다.

### S-5 `DECISIONS.md` 에 사용자의 결정 줄이 없다 — 실행 커밋에 넣어야 한다(그 뒤 약 2.5 일은 건드릴 수 없다)
- `DECISIONS.md` 의 마지막 줄(2026-10-13 11:39 KST)은 "…선택지를 보고하고 결정을 기다린다 (아직 등록하지 않음; WORK_QUEUE 사용자 결정 대기 8)" 에서 끝난다. 스크립트 163 행은 `DECISIONS.md` 가 추적+clean 일 것을 요구하므로 `FIGHS_DONE` 까지 줄을 더할 수 없다(FIGHSX16e4 의 재개가 바로 그 이유로 한 번 멈췄다).
- 실행 커밋에 넣을 줄(시각은 `date` 로): 사용자 원문 두 개("좀 더 시행을 늘려서 15dB까지 다 그리면 좋긴 하겠는데" → 선택 "+15 dB까지 시도"), 선택지 넷과 ① 의 권장 표시, n(+12 dB 327,680 · +15 dB 3,072,000 · ALD 327,680 · 희소 20480 유지), 비용 59 시간 · CPU 96 스레드, 표본 크기를 결과를 본 뒤 정했다는 것, 보고 전용, 코드 변경(`ald.py` `hisnr5` + M-1 의 `eval_accept.py`). WORK_QUEUE 의 대기 8 도 같은 커밋에서 "진행 중" 으로.
- 지금 작업 트리에 미커밋으로 있는 기록(`NEXT_EXPERIMENTS_FIGHSDMI16e4.md` +11 줄 = §6.5 감사 반영, `WORK_QUEUE.md`, `prereg_audit_2026-10-11/s6_fighsroom_gen.py`, `conference/figures/README.md`)은 **실행 커밋 전이나 실행 커밋에** 넣는다 — §1 의 "(예: FIGHSDMI16e4 §6.5 의 감사 반영 …)은 작업 트리에만 두고 `FIGHS_DONE` 뒤에 커밋한다" 는 이미 써 둔 것까지 2.5 일 묵힐 이유가 되지 않는다.

### S-6 그림 규칙의 모호한 곳 넷 (§1 "그림 규칙" — 실행 커밋 뒤에는 고칠 수 없다)
- (a) **y 축 아래 끝이 조건 없는 값으로 적혀 있다.** FIGHSX16e4 §1 의 규칙은 단계식이고(`paper_f21dmc.py` 184–188 행) 내린 한계는 "3e-5 아래로 내려가는 점·화살표가 있을 때만" 쓴다. 초안은 "2e-7" · "1.875e-6" 뿐이라 (i) FZDMIB16e4 가 수용되지 않아 +15 dB 가 n = 20480 으로 남을 때, (ii) 모든 점이 3e-5 위일 때 어느 축인지 정해지지 않는다. 바꿀 문장: "y 축 = FIGHSX16e4 §1 의 단계 규칙 그대로이되 마지막 단계의 값이 **3e-5 × 20480 / n_max, n_max = 그려지는 점의 최대 n** 이다(`hsy`: 3,072,000 → 2e-7; `hsy12` 와 FZDMIB16e4 가 수용되지 않은 `hsy`: 327,680 → 1.875e-6). n_max 에서 실패 1 건(1 / n_max = 한계의 1.63 배)과 Perfect CSI 의 0 실패 화살표 끝(한계의 3.7 배)은 축 안에 있다; Wilson 막대의 아래 끝이 축 아래면 잘린다(기록에 적는다 — n = 3,072,000 의 1 건이면 하한 5.8e-8)."
- (b) **기록의 'at or below the proposed curve' 줄은 실패 수 k 를 곡선끼리 비교한다**(`paper_f21dmc.py` 117–118 행: `cur[a] <= cur[V1]`). 지금까지는 한 SNR 에서 모든 곡선의 n 이 같았다. `hsy` 에서는 +15 dB 에 n = 20480 / 327,680 / 3,072,000 이 섞인다 — 예: SBL 1 / 20480 (4.9e-5) 대 V1 3 / 3,072,000 (9.8e-7) 이 "1 ≤ 3" 으로 "제안 곡선 이하" 에 오른다(그 줄은 §6 에 원문으로 옮겨지는 줄이다). 넣을 문장: "`hsy` · `hsy12` 의 'at or below' 줄은 실패 수가 아니라 BLER (k / n, 정수 교차곱)로 비교하고 양쪽의 k / n 을 함께 적는다; baseline 이 0 실패이고 그 n 의 해상도 1 / n 이 제안 곡선의 BLER 보다 크면 '해상도 한계(n = …)' 로 표시한다 — Annealed Langevin 의 0 / 327,680 은 3.05e-6 미만이라는 뜻이지 제안 곡선(n = 3,072,000) 이하라는 뜻이 아니다."
- (c) **희소 세 곡선을 FY / FZ merge 에서 어떻게 빼는지.** `fighs_merge.merge(pre=…)` 는 `raw_FY<SPDMI>` 가 없으면 `SystemExit` 이고, 피하는 기존 길(`FIGHS_N2560=<TAG>`)은 기록에 "invalid / unrun" 이라고 찍는다 — 이 곡선들은 무효가 아니라 등록상 다시 재지 않는 것이다. 넣을 문장: "희소 세 곡선에는 FY / FZ merge 를 부르지 않는다(기록 줄에 'not re-measured (FIGHSYDMI16e4 §1), n = 20480' 으로 적는다; `FIGHS_N2560` 은 수용되지 않은 FY / FZ 행에만 쓴다). merge 는 SNR 마다 따로: `pre="FY", hs=(12,), n_hs=327680`; `pre="FZ", hs=(15,), n_hs=3072000` (주 곡선) / `327680` (Annealed Langevin)."
- (d) **`hsy12` 가 무엇을 읽는지, FZ 가 끝난 뒤 다시 만드는지.** `hsx12` 는 +15 dB 까지 merge 한 뒤 +12 dB 까지만 그린다(기록의 Counts 에는 +15 dB 의 수가 남는다). `hsy12` 를 FZ 가 도는 중에 그리면 Counts 의 +15 dB 는 n = 20480 값이다. 넣을 문장: "`hsy12` 는 FY 두 행만 merge 한다(기록의 Counts 의 +15 dB 열은 `raw_FH*` 의 n = 20480 값이고 그려지지 않는다); FZ 가 끝난 뒤에도 `hsy12` 의 기록·그림은 다시 만들지 않는다 — +15 dB 의 큰 n 수는 `hsy` 의 기록에만 있다." (반대로 정해도 되지만 정해져 있어야 한다.)
- 사소: "Sionna 방 그림의 원고판 `hsx12` 와 같은 범위" → "같은 **SNR** 범위"(y 축은 7.5e-6 대 1.875e-6 으로 다르다).

### S-7 통계에 관한 공개 셋 (머리말 '유한 풀' · '표본 크기의 근거')
- (a) **Wilson 구간은 명목값이다.** FIGHSX16e4 §6 은 감사 S1 로 "n = 81920 점은 앞선 n = 20480 점과 독립이 아니다 … 그 결과를 본 뒤에 시행을 늘렸다. 그래서 k / n 의 Wilson 구간은 명목값이다. 새 증거는 '보지 않은 시행' 뿐" 이라고 적었다. 이 초안은 `# split` 만 말하고 그 문장이 없다(그림의 Wilson 막대 네 곡선은 합친 k / n 으로 그린다). 머리말에: "+12 · +15 dB 의 점은 처음 20480 시행(이미 본 것; 주 곡선의 V1 · Perfect CSI 는 거기서 0 건)을 포함하고 표본 크기는 그 결과를 본 뒤에 정했다 → 집계표·그림의 Wilson 구간은 명목값이고, 보지 않은 시행만의 수와 구간은 `# split` 줄에 있다(본 부분의 비중: +12 dB 6.25 %, +15 dB 0.67 %)."
- (b) **유한 풀의 해상도.** 테스트 풀의 쌍 하나의 비중은 1 / 60,700 = 1.6e-5 로, 겨냥하는 BLER (+12 dB 약 1e-5, +15 dB 약 1e-6) **이상**이다. BLER 1e-6 은 "쌍 하나가 6 % 로 실패" 와 "쌍 60 개가 0.1 % 로 실패" 를 가리지 못한다 — 이 점들은 채널 분포의 꼬리가 아니라 이 60,700 쌍의 평균이다(초안은 "이 풀에 대한 평균 BLER" 까지만 적었다). 넣을 문장: "풀의 쌍 하나의 비중(1.6e-5)이 +12 · +15 dB 의 BLER 이상이므로 이 점들의 실패는 소수의 쌍에 몰릴 수 있다; §6 에 +12 · +15 dB 에서 V1 · b\* · Perfect CSI 의 실패 시행 번호와 그 시행이 뽑은 풀 쌍의 수(서로 다른 쌍 몇 개인지)를 적는다(스트림 재생으로 구한다 — 건너뛰기 비용 약 2.5 분). 캡션에는 '고정 풀 60,700 쌍의 평균' 을 밝힌다."
- (c) **기대 3 건으로 잡은 크기에서는 점 하나의 상대 오차가 크다**(3 건이면 95 % 구간이 약 0.2–2.9 배). "매끄러운 곡선" 이 보장되지 않는다는 것은 메모에 0 건 확률로만 적혀 있다 — 한 문장 추가: "기대 실패 수 약 3 건이면 +12 · +15 dB 점의 위치는 한 자릿수 가까이 흔들린다."

### S-8 §1 "순서·자원" 에 빠진 것: 메모리, main 동결과 마감, 중단 뒤 재개, 재개 비용, CPU 배치
- **메모리 줄이 없다**(부모 등록에는 있었다). 측정·계산: ALD 두 행 — `runner.build_point` 가 청크마다 추정 파일(671 MB; `hhat` + `b`, 두 SNR 모두)을 통째로 읽고 `meta|ald_file` 의 sha256 을 위해 한 번 더 읽는다 → 워커당 0.66 GiB 상주 + 0.66 GiB 일시, **192 워커 126 GiB (첫 회전에 최대 약 250 GiB)**; 청크당 +1.5 s(등록의 0.7 h 와 맞는다 — 아래 표). `counts` · 그림의 `load_raw(raw_FZDMIB16e4)` 약 19.3 GiB · 1–2 분; `eval_accept` 재생 검사는 M-1. 가용 약 990 GiB.
- **main 동결과 마감.** 시작이 10-12 23:45 CDT 쯤이면 `FIGHS_DONE` 은 10-15 10–11 시 CDT 쯤이고(재개가 있으면 더 늦다) 그때까지 main 커밋·`conf/code`·`DECISIONS.md` 편집이 막힌다 — ICC 마감(10-16; 시간대는 검토가 확인하지 못함) 직전이다. paper 브랜치 동기화는 HEAD 를 움직이지 않는다(`sync_paper_branch.sh`: 별도 인덱스 + `commit-tree` — 확인). 사용자에게 한 줄로 알릴 것.
- **중단 뒤에는 이 등록으로 재개할 수 없다.** 사용자가 멈춘 뒤 main 에 커밋이 하나라도 올라가면 163–164 · 170 행이 `--resume` 을 막는다 → 부분 raw 는 버려진다(§1: 부분 raw 의 수를 쓰지 않는다). "멈춤" 문장에 덧붙일 것: "멈춘 뒤 main 에 커밋하면 이 등록으로는 재개할 수 없다(40 시간 넘게 돈 FZ 행도 버려진다) — 멈추기 전에 사용자에게 이 점을 알린다."
- **재개 비용과 GPU.** `--resume` 은 단계 C 를 다시 돈다(ALD 추정기 대조 둘 = 빈 GPU 가 필요; 없으면 ALD 두 행 SKIP) 그리고 끝난 행을 다시 지난다: runner 의 exists 확인(3.4 µs/파일) + 풀 기동 약 1 분, manifest 약 27 s, (f) 약 2 s, 집계 `load_raw` FY 약 30 s · FZ 1–2 분, FYALDDMI 의 재생 검사 약 2.5 분(고치면 수 초) — 행당 2–5 분. 시작 전에 `nvidia-smi` 로 빈 GPU 를 확인한다(검토 시점 6 장 모두 비어 있음); 단계 C 나 EARLY 에서 GPU 를 못 잡으면 ALD 두 행은 FZ 가 끝난 뒤의 `--resume` 까지 밀린다(주 실행 중에는 `pgrep` 전제 때문에 재개할 수 없다).
- **CPU 배치.** 실행 중의 그림 렌더·감사·서브에이전트는 NUMA 노드 0 / 2 (예: `taskset -c 0-15`)에 둔다 — 부모 실행의 그림 명령은 `taskset -c 24-39` 로 실행의 CPU 집합 안이었다(FIGHSDMI16e4 §6.4).
- **컨테이너 재생성.** tmux 와 함께 감시(cron)도 사라진다 — 발견이 늦은 만큼 그대로 밀린다. raw · 로그 · 추정 파일은 홈에 남고 재개 절은 등록에 있다(확인).

### S-9 ALD 배치 327,680 에서의 결정성 재실행은 시험되지 않았다 (`ald.py` 269–273 행의 assert)
- 탐침(`ald_batch_probe.py`)은 배치마다 **한 번** 돌려 시간·메모리를 쟀다. `estimate` 는 첫 SNR 을 같은 씨앗으로 두 번 돌려 비트 동일을 assert 한다 — 지금까지 통과한 최대 배치는 81,920 이다. 327,680 에서 깨지면 EARLY 와 단계 R 의 재시도가 둘 다 실패해 **ALD 두 행을 잃는다**(주 행은 영향 없음; 실행 중에는 코드를 고칠 수 없다).
- 고칠 것: 실행 커밋 전에 빈 GPU 한 장에서 탐침을 같은 씨앗으로 두 번 돌려 `np.array_equal` 을 본다(약 22 분; 출력은 버린다) — 통과를 §5 에 적는다. 하지 않으면 §1 에 "배치 327,680 의 결정성 재실행은 시험하지 않았다 — 실패하면 ALD 두 행은 n = 20480 점으로 남는다" 를 적는다. (GPU 메모리는 여유가 있다: 33.6 GiB / 96 GB, 재실행 때 첫 실행의 텐서는 풀려 있다 — 코드 판독.)

---

## NIT

- **N-1** §1 "새로 재지 않는 곡선": "같은 n 으로 맞추려면 그 행만 약 이틀이 더 든다" → 로그 기준 약 **75 시간(사흘)**: FHSPDMI 의 +12 / +15 dB 청크는 555 / 553 s 로 주 행 414 s 의 1.34 배 → (51 + 5.5) h × 1.34.
- **N-2** 머리말 (b) "arm 별 시간을 재 보니(아래)" — 아래에는 81 s 하나뿐이다. 수를 적는다(40 시행, +15 dB, 한 스레드): 일곱 arm 81 s · R2 + b\* + V1 + genie 77 s · b\* + V1 + genie 75 s · V1 + genie 45 s · b\* + genie 35 s · genie 4 s.
- **N-3** "작성 시점 공개" 의 n = 20480 목록에 범례 곡선 BiG-AMP (R3: 4194 / 3448 / 4530 / 4940)가 빠졌다(예측 1 에는 있다). 나머지 40 개 수는 집계표와 같다.
- **N-4** 집계표의 `# split` 줄은 ALD 행에도 "(seen, raw_FH*)" 라고 찍는다 — ALD-pilot 의 그 부분은 같은 시행의 **새 사후 표본**이다(씨앗이 파일 안 SNR 순번에 묶여 있다: `hisnr` 에서 12 dB 는 2 번, `hisnr5` 에서는 0 번). §1 의 문장은 맞다; 그림 기록 문구에 FIGHSX 와 같은 한 구절을 넣는다.
- **N-5** chunk 불변성 확인의 범위를 적는다: arm 7 × `KEYS_RAW` 7 = 49 키, 시행 10000..10399 (청크 경계 9 곳), `clip` · `guardH` · `diverged` · `beta_used` 는 비교하지 않음. 검토의 코드 판독: 시행 사이에 남는 상태는 진단용(`last_w`, `herm_res`, `n_query`)과 내용으로 찾는 캐시(`ScorePrior._cache`, `covinv`)뿐이고 BiG-AMP 의 감쇠 사다리는 시행마다 처음부터다 → 분할에 따라 결과가 달라질 경로를 찾지 못했다.
- **N-6** EARLY 는 이제 ALD 행마다 `ald_new` 를 부르므로 빈 GPU 가 없으면 `ABORT: no free GPU` 줄이 **둘** 찍힌다(모래상자 확인). 부모 등록의 "이 ABORT 줄은 행의 실패가 아니다(예측은 시작 줄 수 + `ok=4 fail=0` 으로 채점)" 를 §3 의 8 번에 그대로 적는다.
- **N-7** ALD 추정기 대조 둘(FYCALDDMI · FZCALDDMI)은 같은 계산이다(같은 동결 기록, `--set test`) — 무해한 중복(GPU 약 2 분). 적어 두면 감사가 묻지 않는다.
- **N-8** 실행 중 열람 범위를 한 문장으로: "FZ 행이 도는 동안 그 부분 raw 의 결과 키는 열지 않는다(진행 줄 수와 `run|git` 만 본다)". runner 의 진행 줄은 R2 · R3 · genie 의 청크 BLER 를 소수 둘째 자리로만 찍어 V1 · b\* 의 수는 새지 않는다(확인).
- **N-9** 그림의 `hsy` · `hsy12` 모드를 실행 커밋 뒤에 만든다면 선후의 증거를 남긴다: FY 의 집계표를 열기 전에 스크립트의 sha256 과 `date` 를 기록하고 paper 브랜치 동기화 커밋에 싣는다(main 커밋은 막혀 있다).

---

## 확인한 것

**스크립트 (부모 대비 줄 단위)**
- `bash -n` 통과; `diff` 의 모든 hunk 를 읽음. 옛 전역 `N` · `SNRS` · `PTS` 와 상수 40 이 쓰이던 곳은 30 · 116 · 118 · 197 · 200 · 216 · 218 · 222 행뿐이고 모두 행별 값으로 바뀌었다. `read -r` 은 18 변수 = 표 18 열(의뢰문의 "17 fields" 는 구분자 수다), 빈 FLAGS 열 보존, `awk` 의 `$15 $16 $17` = SNR · n · chunk (모래상자의 시작 줄로 확인).
- `${TAG:0:2}C${TAG:2}` → FYCDMIB16e4 · FYCALDDMI · FZCDMIB16e4 · FZCALDDMI; 대조는 `--chunk $CH --n 40` → `chunk_plan(0, 40, 400) = [(0, 40)]` 이라 FZ 행의 대조 파일 이름도 `…_skip0_n40.npz` (`raw_DMIB16e4` · `raw_ALDDMI` 에 +12 · +15 dB 의 그 파일이 있다).
- `# PRE` 줄을 스크래치 사본에서 실행(`die` 를 보고로 바꿈): 지금 걸리는 것은 **셋** — `conf/code` dirty (` M ald.py`, `?? run_fighsydmi16e4.sh`), 등록 미추적, HEAD ≠ 실행 커밋 — 모두 실행 커밋이 해결한다. 나머지(행별 fits · 체크포인트 sha · 원 raw · ALD 기록 sha · 새 전제 `FIGHS_DONE` + `pgrep`)는 지금 통과. `raw_F[YZ]*` · 대조 산출물 · `ald_PILDMI_hisnr5.npz` · `logs/run_D2_F[YZ]*` 없음.
- 제어 흐름(모래상자, 파이썬 · `nvidia-smi` · `git` 을 대역으로): 정상 경로 — EARLY 가 FYALDDMI 에서 추정을 한 번 만들고 FZALDDMI 는 재사용, 단계 R 의 두 ALD 행도 재사용, `ok=4`; 빈 GPU 없음 — EARLY 의 ABORT 둘 뒤 단계 R 이 행마다 한 번 더 시도; `--resume FZALDDMI` 단독 — "genie reference not accepted" SKIP; 전체 `--resume` — 네 행 재사용·통과. `EP` 는 항상 정해지고 두 번째 `wait $EP` 는 무해하다. 백그라운드 서브셸은 행 변수와 `H` · `L` · `SK` 를 제대로 본다.
- 반쯤 쓰인 `ald_PILDMI_hisnr5.npz`: `np.savez` 는 zip 의 중앙 디렉토리를 닫을 때 쓰므로 `np.load` 가 실패 → `prov` 검사가 빈 문자열 → "stale estimate" ABORT (받아들여지지 않는다). 단계 R 은 `wait $EP` 뒤에만 읽는다.

**chunk 400**
- `runner.chunk_plan(10000, 3072000, 400)` 7,680 청크(마지막 시행 3,081,999) = `eval_accept` 의 계획; FY · ALD 행 8,192 청크. 작업 정렬은 skip 숫자순, `load_raw` 는 `(int skip, n)` 로 정렬해 이어 붙이므로 `e[:20480]` 은 6–7 자리 skip 에서도 시행 10000..30479 다. 파일 핸들 한도 524,288 (한 점에 7,680–8,192 파일을 동시에 연다 — 문제없음).
- `chunk_invariance_FIGHSYDMI.out`: 400 시행 783 s, 49 키 차이 없음, `CHUNK-INVARIANCE: OK`, `rc=0` — 등록의 주장을 뒷받침한다(범위는 N-5).
- 실행 뒤 단계의 시간·메모리(`review_FIGHSYDMI16e4_checks.out`): manifest 3.4 ms/파일, (f) 0.29 ms/파일, `load_raw` 3.6 ms/파일(chunk 40) · 8.5 ms/파일(chunk 400, 합성 파일), 시행당 6,744 B → FZ 19.3 GiB; 재생 검사는 M-1.

**시행 스트림 · 풀**
- `common.trial_rng` = 점마다 한 스트림(`[SEED, TBID, PID, Nr, T, Tp, snr + 100]`), `run_task` 는 `range(skip + n)` 를 처음부터 만들고 `skip` 개를 버린다 → 3,081,999 번까지는 같은 스트림의 뒤쪽 추첨. DMI 의 raw 가운데 시행 30480 이후를 쓴 것은 없다(목록: 시험 0..2559 다섯, `raw_FH*DMI` 10000..30479 셋, 대조, 스크래치 `raw_ZQDRY*` 10000..10799). `dmimo.DMGen._draw`: 테스트 풀은 `rng.integers(0, len)` — 복원 추출; 테스트 풀 60,700 쌍(`POOL_SHA` 주석); 3,072,000 / 60,700 = 50.6.

**ALD**
- `ald.py` 작업본: 구문 OK, `hisnr5` 는 SNR 표 · (skip, n) 표 · `--set` 선택지 · 설명문 네 곳. `_regen_one` 을 메모리 안에서 불러 +12 · +15 dB 의 시행 10000..10063 이 `pilots_PILDMI_hisnr.npz` 와 b · H · G · sigma2 비트 동일(`REGEN-PREFIX: OK`). `_ald_table` 은 `np.isclose(snrs, snr)` 로 순번을 찾는다([12, 15] 파일에서 0 / 1). `tune_PILDMI.json` 에 12.0 · 15.0 의 stop(600) · v 가 있다. regen 시간: `hisnr4` (81,920) 42 s → 327,680 은 부하 없이 약 3 분.
- 탐침 수치(43 s · 2.1 GiB, 668 s · 33.6 GiB)는 세션 기록의 도구 출력과 같다(탐침의 출력 파일은 없다).

**비용 모형** (탐침·로그에서 다시 계산)

| 항목 | 등록 | 재계산 |
|---|---|---|
| 96 스레드 처리량 | 36.7 | 2048 × 81 / (75.3 × 60) = 36.7; 청크 벽시계 평균 +6 / +9 / +12 / +15 dB = 421 / 411 / 415 / 414 s (SNR 과 무관) |
| 건너뛰기 | 47.5 µs | (22 − 3) s / 400,000 (초 단위 측정이라 ±2.5 µs) |
| chunk 40 · n 3.07M | +91 % | 평균 skip 1,546,000 × 47.5 µs = 73.4 s / 81 s |
| chunk 400 | +9 % | 73.4 / 810 (불변성 확인의 783 s 기준 +9.3 %) |
| FYDMIB16e4 | +10 % · 5.5 h | 173,840 × 47.5 µs = 8.3 s; 8192 × 88.8 / 36.7 = 5.5 h |
| FZDMIB16e4 | 51 h | 7680 × (783 + 73) / 36.7 = 49.8 h (810 s 기준 51.3 h) |
| ALD 행 | 0.7 h | FHALDDMI 13.8 s 벽시계 = 2.6 s 한 스레드, + 건너뛰기 7.3 s + 추정 파일 1.5 s = 11.4 s; × 8192 / 36.7 = 0.71 h |
| 진행 중 청크 | 약 1.2 h | 856 s × 192 / 36.7 = 1.24 h |
| 디스크 | ≈ 6 GB | 0.55 + 3.34 + 2 × 0.24 + 2 × 0.62 = 5.6 GiB (chunk-400 파일 456 KiB — 합성 파일로 잼) |

**검토의 전체 시간 추정**: 단계 C 0.1 h + FY 5.5 h + FYALD 0.7–1.0 h + FZ 50–55 h + FZALD 0.7–1.0 h + 수용·집계 0.2 h ≈ **58 시간(범위 56–64 시간)**, 중단이 없고 M-1 을 고쳤을 때. 벽시계의 가장 큰 위험은 (1) 36.7 이라는 처리량이 75 분 실행에서 잰 값이라는 것(건너뛰기 재생성도 같은 2:1 과점유 아래 돈다; 다른 사용자의 부하·같은 노드의 다른 작업에 따라 ±10 %), (2) 중단(컨테이너 재생성, 죽은 워커 — S-2 (c))의 발견 지연, (3) GPU 를 못 잡아 생기는 재개다.

**등록의 사실 문장**: 사용자 인용·선택지 문구(세션 기록), n = 20480 실패 수 40 개 · 예측 1 의 '본 부분' 16 개 · 희소 6 개(집계표 셋), +3 dB 19 / 2560 (`pairB_SPDMI.txt`), 외삽(1/10 씩: +12 dB 9.8e-6 → 3.2 건, +15 dB 9.8e-7 → 3.0 건; 0 건 확률 4–5 %), 50.6, 2e-7 · 1.875e-6 · 3.3e-7, 시행 범위 337,679 · 3,081,999, 47 h(76,800 × 81 / 36.7), 초안의 스크립트 sha — 모두 맞다. 틀린 곳·빠진 곳은 S-3 · S-4 · N-1 · N-2 · N-3.

## 확인하지 못한 것 · 추론으로 적은 것

- **GPU 단계 전부**(GPU 사용 금지): ALD 추정기 대조, 배치 327,680 의 추정과 결정성 재실행(S-9), 추정의 실제 시간. 탐침이 GPU 5 에서 돌았다는 것.
- **51 시간 동안의 처리량**(추정), 192 워커가 671 MB 파일을 동시에 읽을 때의 메모리 대역 경합(추정: ALD 행 0.7–1.0 h).
- M-1 의 590 GiB 는 20,000 시행 측정의 **선형 외삽**이다(시행마다 51,200 B 배열 넷을 붙드는 구조라 선형이다 — 코드로 확인; 실제로 590 GiB 를 잡아 보지는 않았다). 고친 코드의 FZ 규모 수치는 합성 반복으로 쟀다.
- chunk 불변성: 400 시행 밖은 코드 판독에 기댄다(N-5).
- 세션의 서술 블록이 사용자에게 보였는지(S-4); ICC 마감의 시간대; 사용자가 받은 그림.
- 그림의 `hsy` · `hsy12` 모드는 아직 없다 — 규칙이 구현 가능한지는 `paper_f21dmc.py` · `fighs_merge.py` 를 읽고 판단했다(S-6 을 반영하면 구현 가능하고 한 가지로 읽힌다).
- S-2 (a) 의 관문과 S-1 의 `wait` 는 스크래치 사본의 `bash -n` 과 모래상자 흐름으로만 확인했다(실제 실행 아님). 고친 스크립트는 다시 검토받지 않는다.
