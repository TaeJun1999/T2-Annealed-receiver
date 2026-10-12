# Adversarial pre-run review — NEXT_EXPERIMENTS_FIGHSX16e4.md draft v1 (uncommitted; sha256[:16] 96c10efcf72be916, mtime 2026-10-11 19:05:10 CDT) + staged script run_fighsx16e4.sh (c942848e55ac9676, 19:03:14 CDT) + staged ald.py (f81f3c0f65bed35e, 19:01:50 CDT) + uncommitted figure code (fighs_merge.py fd9e6b8c6ba7543e, paper_f21dmc.py b65bb71879ec8f74)

Reviewer: Claude Fable 5.1 subagent, report written 2026-10-11 19:52 CDT. HEAD c48ee796 (= the FIGHSPATH16e4 run commit). The SRP supplement was running throughout (tmux `fighspath`): by FILE COUNT only, `raw_FHSRPB16e4` held 1245 / 2048 chunk files at 19:25:47 CDT, 1722 at 19:44:34, 1872 at 19:48; no `raw_FHSPSRP` / `raw_FHALDSRP`; `logs/run_fighspath16e4.log` 6 lines. Nothing of that run was opened (no chunk, count table, accept file or log content). CPU only, `python -B`, at most 3 threads / 2 jobs; nothing written under `conf/code` or `Demo` (checked: no file there newer than the review start); no tracked file edited; read-only git. Method = review_FIGHSROOM16e4.md / review_FIGHSPATH16e4.md; what is unchanged from those was not re-derived.

## Verdict

- **Script + ald.py: runnable as is — yes.** No script or tool bug found. Every changed line is one of the intended changes, all six rows trace to the argument forms that passed in FIGHSROOM16e4, the `hisnr4` regen was run (staged copy, output redirected to scratch) and reproduces the n = 20480 pilots bit for bit on the shared trials, and every `# PRE` line passes once the registration, DECISIONS line, script and ald.py are HEAD. The ~8 h of CPU would not be wasted.
- **Registration: do not freeze as is — 3 MUST.** None changes what the runner computes: M-1 the registered y-axis rule cannot draw an n = 81920 point with 1 or 2 failures (the figure script stops) and silently drops the Perfect CSI arrow at 0 / 81920; M-2 the bit-identity claim / prediction 8 is false by construction for the ALD-pilot arm; M-3 the "only these changes" list is incomplete (the FIGHSPATH16e4 M-1 regression).
- Strongly advised before the commit: S-1 (report the 61440 unseen trials separately — 2 lines in `counts`, tested) and S-5 (1-minute GPU smoke of the B = 81920 ALD batch, because an ald.py fault cannot be repaired under the run commit).

## MUST

### M-1  §1 "그림 규칙" + `paper_f21dmc.py` `__main__`: the y rule (2e-4 → 3e-5) is too high for n = 81920
- What: the rule inherited from FIGHSROOM16e4 gives y ≥ 3e-5 at the lowest. At n = 81920 one failure is 1.22e-5 and two are 2.44e-5; a Perfect CSI zero-failure point puts its cap at 4.69e-5 and its arrow tip at 2.76e-5.
- Evidence (scratch harness feeding synthetic n = 81920 counts to the uncommitted script, `fighsx_review/harness.py`): Perfect CSI 1 / 81920 and 2 / 81920 → `AssertionError` at `paper_f21dmc.py:92` (`p >= YLIM[0]`), no figure; Proposed 2 / 81920 → the same; Perfect CSI 0 / 81920 → rc 0 but both arrows are NOT drawn (`Annotation._check_xy` False: tip 2.76e-05 below ylim 3e-05; matplotlib drops an annotation whose xy is outside the axes), although the record still says "Perfect CSI: fighs_merge.zero_arrows". SRB Perfect CSI is 1 / 20480 at both SNRs, so a count of 1 or 2 in 81920 is likely (≈ 20 % per SNR if the rate is 1 / 20480); on SRP the n = 2560 counts at +9..+15 dB are 0 for Proposed and Perfect CSI, so 0, 1 or 2 are the expected outcomes there.
- Why MUST: the rule has to be fixed before the data are seen; otherwise the y axis is chosen after the result.
- Replacement text (그림 규칙, in place of "y 축 `ROOM` 분기 규칙을 그려지는 값에 적용"): "y 축: `ROOM` 분기 규칙을 그려지는 값에 적용하되 한 단계를 더한다 — (2e-4, 1.2) [0 실패 점이 없고 모든 점·막대 끝이 2e-4 위], 아니면 (3e-5, 1.2) [그려지는 모든 점이 3e-5 이상이고 Perfect CSI 에 n = 81920 의 0 실패 점이 없을 때], 아니면 **(7.5e-6, 1.2)** = FIGHS16e4 의 한계 3e-5 를 n = 20480 → 81920 와 같은 비율로 내린 값(n = 81920 에서 실패 1 건 1.22e-5 · 2 건 2.44e-5, 0 실패 화살표는 4.69e-5 에서 2.76e-5 까지). 결과를 보기 전에 정한 규칙이다."
- Replacement code (after the existing `YLIM, YTICKS = ...` line of the `ROOM` branch; tested on a scratch copy — the three failing cases render with ylim (7.5e-06, 1.2) and drawn arrows, a case with every count ≥ 3 keeps (3e-05, 1.2), and the `SRB` / `SRB hs` records stay byte-identical):
```python
            if HSX and YLIM[0] == Q.YLO_RULE and min(             # FIGHSX16e4 §1: at n = 81920 one failure is 1.22e-5 and the Perfect CSI
                    [float(x) for k, n in KN.values() for x in (k / n)[k > 0]]         # zero-failure arrow ends at 2.76e-5: both below 3e-5
                    + [1.96 ** 2 / (x + 1.96 ** 2) / 1.7 for x in KN[GE][1][KN[GE][0] == 0]]) < Q.YLO_RULE:
                YLIM = (Q.YLO_RULE / 4, 1.2)                       # the FIGHS16e4 §1 limit scaled from n = 20480 to n = 81920: 7.5e-6
```
  Lazier alternative (one line, costs up to 0.6 decade of empty axis): `if HSX and YLIM[0] == Q.YLO_RULE: YLIM = (Q.YLO_RULE / 4, 1.2)`.

### M-2  Header bullet "시행" and prediction 8: bit identity with `raw_FH*` is false by construction for ALD-pilot
- Claim: "새 raw 의 처음 512 청크는 그 raw 의 배열을 비트 단위로 재현해야 한다" and "8. … 모든 arm 의 배열이 비트 동일하다(여섯 raw 모두)".
- Evidence: `ald.py` `cmd_estimate` seeds each SNR by its INDEX in the pilots file — `for k, s in enumerate(z["snrs"]): gen = torch.Generator(device="cuda").manual_seed(SEED + 1000 + 17 * k)` — and draws `torch.randn(B, 2 * N, generator=gen)` for the whole batch. In `pilots_*_hisnr.npz` +12 / +15 dB are k = 2 / 3 with B = 20480; in `pilots_*_hisnr4.npz` they are k = 0 / 1 with B = 81920. The ALD estimate ĥ of the same trial is therefore a different posterior sample, so the ALD-pilot arrays of `raw_FXALD*` (certainly `nmse`, possibly `blk_err`) will not equal `raw_FHALD*`'s. Same channels, pilots and noise (regen verified bit-identical on trials 10000..30479, below); R5-genie of the ALD raws is deterministic and must match.
- Replacement (header bullet, the sentence starting "처음 20480 시행"): "처음 20480 시행(10000..30479)은 n = 20480 raw (`raw_FH*`)의 +12 · +15 dB 시행과 같은 스트림의 같은 시행(같은 채널·파일럿·잡음)이라, 새 raw 의 처음 512 청크(SNR 마다)는 **ALD-pilot 을 뺀 모든 arm** 에서 그 raw 의 배열을 비트 단위로 재현해야 한다 — 스크립트의 관문은 아니고 기록 감사가 확인한다(§3 예측 8). **ALD-pilot 은 예외다**: ALD 추정은 사후 표본이고 `ald.py estimate` 의 씨앗이 파일 안 SNR 순번(`SEED + 1000 + 17k`)과 배치에 묶여 있어 — `hisnr` 파일에서 +12 / +15 dB 는 k = 2 / 3 · 배치 20480, `hisnr4` 에서는 k = 0 / 1 · 배치 81920 — 같은 시행에서도 추정 ĥ 이 다른 표본이다. FXALD 행의 처음 20480 시행의 ALD-pilot 실패 수는 FHALD 의 값(SRB 7 / 11)과 같을 필요가 없다."
- Replacement (prediction 8; mark it in §5 as a review correction, since §3 is otherwise frozen): "8. 새 raw 의 처음 20480 시행(청크 skip 10000..30440)은 +12 · +15 dB 에서 `raw_FH*` 의 같은 이름 청크와 **ALD-pilot 을 뺀 모든 arm × `common.KEYS_RAW`** 배열이 비트 동일하다(여섯 raw 모두 — FXALD 두 raw 에서는 R5-genie 만; 기록 감사가 확인). ALD-pilot 은 씨앗·배치가 달라 대상이 아니다(머리말 '시행')."

### M-3  §1 "스크립트" and the script header: the "다음만 바꾼 것" list is incomplete (FIGHSPATH16e4 M-1 again)
- Evidence (`diff code/run_fighsroom16e4.sh <staged>`, new-file line numbers): hunks at 2–11, 13–14, 20–25, 60, 98, 107, 110–111, 116, 141–144, 152–153, 160–162, 172–174, 182, 197, 203–205, 209. Not in the list: **98 / 110 / 209** (the script and registration names printed into the count-table header and the two log headers: `run_fighsroom16e4` → `run_fighsx16e4`, `FIGHSROOM16e4 §1` → `FIGHSX16e4 §1`) and **182** (the `--resume` unreadable-chunk scan: three tags → six; behaviour on a resume). Everything else is in the list; nothing unintended changed.
- Replacement (§1 스크립트, the parenthesis list): "… 다음만 바꾼 것(머리말에 원문; 검토가 diff 로 확인): 머리말 주석(2–11 행), 등록·로그 파일 이름(13 행), `SNRS="12 15"` · `N=81920` (14 행), `ROWS` 표(20–25 행), 대조·기준 패턴의 태그 접두사 FH → FX · FHC → FXC (107 · 116 · 160 · 162 · 172 · 197 · 203–205 행), ALD 세트 이름 `hisnr` → `hisnr4` (60 · 111 · 116 · 141–144 · 152–153 · 161 · 173 행)와 `PILSRP` 의 ALD 기록(174 행), 단계 C 요약 줄과 새 실행 전제의 ALD 행 둘(161 · 197 행), 집계표 머리글과 두 로그 머리글에 찍히는 스크립트·등록 이름(98 · 110 · 209 행), `--resume` 의 읽을 수 없는 청크 검사가 도는 태그 목록(셋 → 여섯; 182 행). 동작이 다른 줄은 14 · 20–25 · 174 · 182 행과 `hisnr4` 가 들어간 줄뿐이다." Add the last two items to the script header too (after "and both ALD rows in the phase C summary line and the fresh-run precondition"): ", the script / registration name printed into the count-table and log headers, and the six tags in the --resume unreadable-chunk scan". If S-1 / S-7 are adopted, list them as well.

## SHOULD

### S-1  Disclosure: the n = 81920 point contains the 20480 trials that triggered the extension — report the 61440 unseen trials separately
- The draft says the trials are the same, but not the consequence: the extension was decided after seeing those outcomes (the trigger was Proposed 3 → 4 in exactly these trials), they make up a quarter of the new point, and the Wilson interval at n = 81920 is therefore nominal. A reader cannot separate the fresh evidence. This is report-only, so no test is affected, but the record should let the fresh 61440 trials be read alone.
- Where: the script's count table (written under the run commit by the registered code, every arm), as `#` lines so that `fighs_merge.parse` does not read them; the figure record cites it.
- Code (staged script, inside `counts`, directly after the line that prints `SNR … BLER … 95% […]`; tested on `raw_FHSRBB16e4` with the boundary set to 5120 — rc 0, and `fighs_merge.parse` of the output equals `parse` of the committed table, 32 entries):
```python
        if n > 20480:   # FIGHSX16e4 §1: the trials of raw_FH<tag> (seen before this run) and the unseen rest; '#' lines are not read by fighs_merge.parse
            g, m = int(e[:20480].sum()), n - 20480; lo, hi = wilson(f - g, m)
            print(f"# split SNR {k[2]:+.0f}  {a:<20} trials 10000..30479 (seen, raw_FH*): {g} of 20480;  trials 30480..{9999 + n} (unseen): {f - g} of {m}  BLER {(f - g) / m:.2e}  95% [{lo:.2e}, {hi:.2e}]")
```
  (`analysis.load_raw` concatenates the chunks in numeric skip order, so `e[:20480]` is trials 10000..30479.)
- Text, add to the 작성 시점 공개 bullet: "**n = 81920 점은 n = 20480 점과 독립이 아니다**: 처음 20480 시행의 결과를 본 뒤에 늘리기로 했고(계기가 그 시행에서 보인 V1 의 3 → 4 건), 그 시행이 새 점의 4 분의 1 이다. 그래서 n = 81920 의 Wilson 구간은 명목값이며, **보지 않은 시행 30480..91919 (n = 61440) 만의 실패 수·BLER·Wilson 구간을 집계표에 arm · SNR 마다 따로 적는다**(`fighs_FX*.txt` 의 `# split` 줄). 그림의 점은 등록대로 n = 81920 전체이고, 기록·캡션·§6 은 두 수를 나란히 적는다; ALD-pilot 의 '본 시행' 줄은 새 사후 표본이다(머리말 '시행')."
- Text, add to §1 수용: "집계표에는 arm · SNR 마다 `# split` 줄이 붙는다(시행 10000..30479 / 30480..91919; `fighs_merge.parse` 는 `#` 줄을 읽지 않는다)." And to §3: "예측 1 · 3 · 5 · 6 은 n = 81920 으로 채점하고 n = 61440 의 수를 옆에 적는다."
- Figure record (`paper_f21dmc.py`, hsx string): replace `"20480 trials are the same trials as the n = 20480 raw's; one point = one raw, never pooled).  "` with `"20480 trials are the same trials as the n = 20480 raw's -- Annealed Langevin: the same trials with a new posterior sample; the unseen trials 30480..91919 alone are the '# split' lines of results/review_next/fighs_FX<tag>.txt; one point = one raw, never pooled).  "`.

### S-2  Prediction 4: state it in counts; the rounded intervals change the score at one value
- Exact Wilson (`hisnr_report.wilson`): 3 / 20480 → [4.981913e-05, 4.306307e-04], 4 / 20480 → [7.595576e-05, 5.021320e-04]. With the exact bounds k / 81920 is inside for k = 5..35 (+12 dB) and k = 7..41 (+15 dB); with the draft's rounded "[7.6e-05, 5.0e-04]" k = 41 is outside.
- Replacement: "4. SRB: V1 의 n = 81920 실패 수가 +12 dB 에서 5..35, +15 dB 에서 7..41 이다(= k / 81920 이 n = 20480 의 95 % Wilson 구간 [4.98e-05, 4.31e-04] · [7.60e-05, 5.02e-04] 안; 4a · 4b 따로 채점). 이 수에는 이미 본 실패 3 · 4 건이 들어 있다."
- Prediction 2 is scoreable from the hsx record's 'rising' lines; add "(hsx 기록의 rising 줄; +9 → +12 dB 칸은 n = 20480 대 n = 81920)". Predictions 1, 3, 5, 6, 7 are scoreable as written (6 is a trivial hit if both counts are 0).

### S-3  No DECISIONS.md line for the user decision
- Evidence: `grep -n -E 'FIGHSX|81920|2번 해|위로 튀' DECISIONS.md` → nothing. The script requires DECISIONS.md tracked + clean at the run commit, so the line goes in with v2.
- Text (dates via `date`): "`[<date> KST] FIGHSX16e4: Sionna 방 그림 둘(SRB · SRP)의 +12 · +15 dB 점을 새 시행 n = 81920 으로 (보고 전용; 텍사스 <date> CDT) | 사용자 질문 (10-11 CDT, 원문): '15dB에서 왜 위로 튀지?' → 사후 진단(FIGHSROOM16e4 §6.6)과 두 선택지(① 그대로 ② +12 · +15 dB 만 4 배) → '2번 해. 가용 가능한 모든 GPU를 사용해'. GPU 지시의 처리: 수신기 BLER 은 CPU (01_RULES §9.1 · §9.3 · §9.4; `runner.py run` 이 `--device cuda` 를 거부) → GPU 는 ALD 추정에만; 사용자에게 보고함. 판정·라벨 불변; n = 81920 점은 이미 본 20480 시행을 포함한다(새 61440 시행은 집계표에 따로). FIGHSPATH16e4 의 FIGHS_DONE 뒤에 실행.`"

### S-4  Cost line: two of the "× 2" figures are off; total ≈ 8 h, not 7.5 h
- Regeneration overhead (the question asked): measured on this loaded machine with the runner's own skip loop (`ald._regen_one`, n = 0): **0.12 ms per skipped trial** on both priors (SRB 40000 trials 4.98 s, SRP 4.72 s). A chunk at skip 91880 pays ≈ 11 s against ≈ 3.7 s at skip 30440; the mean chunk pays 6.1 s against 2.4 s, i.e. +3.7 s per chunk = +1.7 % (base), +1.3 % (SP), +45 % of the 8 s ALD chunk. Negligible except on the ALD row. (The per-chunk seconds in `logs/run_D2_FH*.log` cannot show this: the runner sorts tasks by skip, so skip is confounded with time in the run — the fitted slope is even negative, −1.8 ms / trial.)
- What does matter: the SP row costs more at exactly these two SNRs. `logs/run_D2_FHSPSRB.log` per-chunk mean 177 / 180 / 277 / 280 s at +6 / +9 / +12 / +15 dB (pick: n_em 10 at +12 dB, L 32 at +15 dB), against the all-SNR mean 228.5 s behind the 41.6 min. The base row has no SNR effect (216 / 216 / 214 / 213 s).
- SRP base: by file-count slope (477 files in 1127 s on 192 workers) FHSRPB16e4 finishes in ≈ 79 min, not 90.
- Replacement (비용): "비용 [추정; 검토 S-4] 단계 C ≈ 10 분; SRB: FXSRBB16e4 ≈ 80 분(실측 39.0 분 × 2, 건너뛰는 시행 재생성 +1.7 %), FXSPSRB ≈ 103 분(41.6 분 × 2 × 1.22 — +12 · +15 dB 청크가 278 s 로 네 SNR 평균 228.5 s 보다 길다), FXALDSRB ≈ 13 분(재생성 ≈ 2 분 [검토 실측 106 s], GPU 추정 ≈ 6–7 분, runner ≈ 4.5 분); SRP: FXSRPB16e4 ≈ 160 분(FIGHSPATH16e4 실측 × 2; v2 에서 적는다), FXSPSRP ≈ 90 분, FXALDSRP ≈ 13 분. 합 ≈ 8 시간(7.5–8.5). 건너뛰는 시행의 재생성은 시행당 0.12 ms (skip 91880 에서 청크당 ≈ 11 s)."
- Memory: unchanged from the n = 20480 runs — a worker holds one 40-trial chunk, the skip loop keeps nothing, and the hisnr4 ALD file has the same row count as the hisnr file (2 × 81920 = 4 × 20480; ≈ 168 MB per load). `counts` / `load_raw` on 2048 files: 19 s, 0.64 GiB peak, so ≈ 40 s and ≈ 1.3 GiB on 4096.

### S-5  The B = 81920 ALD batch is first executed ≈ 3 h into the unattended run — smoke it before the commit
- `cmd_estimate` hands the whole SNR to `ald_run` as one batch; phase C only exercises B = 2560 and the supplements B = 20480. The network is a DiT (width 64, depth 6, 8 heads, 32 tokens; Linear / LayerNorm / explicit softmax attention): the largest single tensor is 32 kB per block = 2.5 GiB at B = 81920, so a 96 GiB card should hold it, and I found no op with a batch limit. Risk is low but untested, and it cannot be repaired afterwards: a change to ald.py moves HEAD, and `--resume` then refuses ("no logged start on this commit").
- Fix: run the ready smoke once on a free GPU before the run commit (synthetic input = the SRB test pilots tiled to 81920 rows, 6 steps, nothing written, no new trial touched; verified on CPU with B = 512):
  `cd ~/t2/conf && CUDA_VISIBLE_DEVICES=<free GPU> ~/miniforge3/envs/torch/bin/python -B results/review_next/prereg_reviews_2026-10-11/review_FIGHSX16e4_gpu_smoke.py <staged ald.py path>` — it prints OK, the same-seed bit identity, s / step and peak GPU memory. If it fails, batch `cmd_estimate` in 20480-row slices (then §1 "추정 경로는 건드리지 않는다" must be reworded).
- Related, operational: at 19:48 CDT only GPU 1 was free (0 and 2 hold this container's `seedsrb2` / `seedsrb3` jobs, 3–5 are held from outside). The script needs one free GPU at the start, at ≈ 3.2 h and at ≈ 7.7 h; with none it fails that ALD row without retry. Keep one GPU free overnight; if an ALD row fails for this reason, `bash code/run_fighsx16e4.sh --resume` works only **before any further commit**.

### S-6  The record says something false when an FX row is unaccepted (`FIGHS_N2560=<FX tag>`)
- Evidence (`FIGHS_N2560=FXSRBB16e4 FIGHS_ALLOW_MISSING=1 … SRB hsx`, uncommitted code): `M-ours-dscore-C-V1 @16 45/20480 10/20480 3/20480 4/20480 (raw_SRBB16e4 at every SNR -- this curve is n = 2560 over the whole range: FXSRBB16e4 invalid / unrun (§1))` — n = 2560 stated next to n = 20480 counts, and the FH source is not named. The draft admits this in a parenthesis; it is cheaper to fix. The same `merged()` line would also name `raw_FH<tag>` for +6 / +9 dB when that FH tag itself was declared invalid.
- Code, `fighs_merge.merge` (replace the `print(...)` / `src = ...` pair of the `if tag in N2560:` branch; the `pre == "FH"` path is unchanged):
```python
        if pre != "FH":                                   # FIGHSX16e4 §1: the points handed in (the FH merge's) stay as they are
            print(f"NOTE FIGHSX16e4: curve {arm} ({cell} {prior}) keeps the points of the previous merge at {'/'.join(f'{s:+.0f}' for s in hs)} dB: "
                  f"{tag} declared invalid / unrun (FIGHS_N2560) -- the caption must say so (§1)", file=sys.stderr)
            src = f"unchanged, {tag} invalid / unrun (FIGHSX16e4 §1)"
        else:
            print(f"NOTE FIGHS16e4: curve {arm} ({cell} {prior}) keeps raw_{orig} (n = 2560) at every SNR: {tag} declared invalid / "
                  "unrun (FIGHS_N2560) -- the caption must say so (§1)", file=sys.stderr)
            src = f"raw_{orig} at every SNR -- this curve is n = 2560 over the whole range: {tag} invalid / unrun (§1)"
```
- Code, `paper_f21dmc.merged` (replace the `if HSX:` body):
```python
    if HSX:
        s1 = re.search(r"   \((.*?)\)(   rising: .*)?$", line)[1]                      # the source text of the FH pass, whatever it was
        k, n, line = M.merge(SNRS, k, n, o, CELL, PRIOR, a, pre="FX", hs=M.HS[2:], n_hs=4 * M.N_HS)
        line = line.replace("   (", f"   (+6..+15 dB: {s1}; then +12/+15 dB: ", 1)
```
- Tested on scratch copies: the failure case prints `(+6..+15 dB: raw_FHSRBB16e4; then +12/+15 dB: unchanged, FXSRBB16e4 invalid / unrun (FIGHSX16e4 §1))`, a synthetic success case prints `(+6..+15 dB: raw_FHSRBB16e4; then +12/+15 dB: raw_FXSRBB16e4)`, and the `SRB hs` record and PDF stay byte-identical. Then replace the draft's parenthesis "(`FIGHS_N2560=<FX 태그>` — 그 경우 기록의 안내 문구는 … n = 20480 값이다)" with "(`FIGHS_N2560=<FX 태그>`; 기록 줄에 'unchanged, <FX 태그> invalid / unrun' 으로 나온다)".

### S-7  §1 says the run starts only after FIGHSPATH16e4's FIGHS_DONE — the script does not check it
- A too-early start shares the 192 cores, and the run commit itself (HEAD moves, `conf/code/ald.py` replaced) makes the running SRP script abort its remaining rows ("HEAD moved"). One line protects both; tested from a script file (dies while a runner is alive, dies on a missing log, silent on a finished log with no runner):
```bash
grep -q 'FIGHS_DONE' logs/run_fighspath16e4.log 2>/dev/null && ! pgrep -f 'code/runner[.]py run' > /dev/null || die "FIGHSPATH16e4 has not printed FIGHS_DONE (or a runner.py run is still alive) -- §1 순서·자원"  # PRE
```
  Put it after the `# PRE` line that checks the stale control artefacts, and list it in the header and §1. The commit itself still has to wait for FIGHS_DONE by hand.

### S-8  GPU paragraph: 01_RULES §9.3 does not say "every arm is CPU"
- §9.3 is "GPU를 쓸 때의 필수 조건" (equal precision for every arm, one path for every arm, determinism, recorded), with the G1 / G2 equivalence tests in §9.4; the CPU default is §9.1. The refusal is real: `runner.py` 1278–1280 exits on `--device cuda` for `run`, citing §9.1 and §9.3. Since this paragraph explains a departure from a verbatim user instruction, cite what the rule says.
- Replacement (first sentence): "수신기 BLER 은 CPU · complex128 로만 잰다 — 01_RULES §9.1 (CPU 기본)과 §9.3 (GPU 경로는 전 arm 같은 정밀도·같은 경로·결정론이 조건이고 §9.4 의 G1 · G2 동등성 검사를 통과해야 한다)에 따라 그렇게 검증된 GPU 수신기 경로는 이 프로젝트에 없고, `runner.py run` 은 `--device cuda` 를 거부한다;" (the rest of the paragraph stands).

## NIT
- N-1 hsx record block title is still "`FIGHSROOM16e4 merge (REPORT-ONLY, NEXT_EXPERIMENTS_FIGHSROOM16e4 §1)`": in hsx mode write `f"{HSREG[PRIOR]} + FIGHSX16e4 merge (REPORT-ONLY, NEXT_EXPERIMENTS_{HSREG[PRIOR]} §1 and NEXT_EXPERIMENTS_FIGHSX16e4 §1)"`.
- N-2 §1 says the figure-code change is the hsx mode plus one hs wording; `fighs_merge.merge` also changes the error / WARNING text of every caller ("takes +6..+15 dB from" → "takes +6/+9/+12/+15 dB from"; stderr only, no record). Add "과 `fighs_merge.merge` 의 오류 문구(stderr)".
- N-3 Staged script, two stale words: line 114 comment "copied to the FHC tag" and line 162 `die "stale FHC control artefacts …"` → "FXC".
- N-4 Under `FIGHS_ALLOW_MISSING=1` the FX pass prints "kept the original raw_<orig> points (n = 2560) at +6..+15 dB" although the n = 20480 points are kept (test renders only).
- N-5 `fighs_merge.zero_arrows` docstring lists the cap for 2560 and 20480 only; add "81920 -> 4.69e-5".
- N-6 Three figures now exist per prior (`F21sr?_col`, `…hs_col`, `…hsx_col`). One sentence avoids a later "nicer curve" reading: "원고에 hs · hsx 가운데 어느 것을 쓰는지는 사용자가 정하되, hsx 를 본 뒤 hs 로 돌아가면 그 사실과 두 그림의 +12 · +15 dB 계수를 캡션이나 본문에 적는다."
- N-7 Record audit items worth naming in §1: the "raised trials per arm" of the (f) line is 0 for ALD-pilot (a pilot-site mismatch raises and would be counted as a failure, not stop the run), and the `# split` "seen" counts equal the `fighs_FH*.txt` counts for every arm but ALD-pilot.
- N-8 Inherited memos, not regressions: the tune-record sha is not in the `case` line (tracked + clean is equivalent; both shas verified), and the record's "Counts:" suffix `raw_<orig>`.

## Duration estimate (192 workers; evidence in S-4)

| step | estimate | basis |
|---|---|---|
| phase C | ≈ 10 min | two ALD estimator controls ≈ 1 min each, six receiver controls in parallel (slowest: SRP base, 4096-component b\*) |
| FXSRBB16e4 | ≈ 80 min (78–84) | 39.0 min × 2 × 1.017 |
| FXSPSRB | ≈ 103 min (98–108) | 41.6 min × 2 × (278.2 + 3.7) / 228.5 |
| FXALDSRB | ≈ 13 min | regen 1–2 min (106 s measured under load), GPU estimate 6–7 min (2.4 × the block-steps of the n = 20480 run), runner 4.4 min |
| FXSRPB16e4 | ≈ 160 min (150–170) | FHSRPB16e4 ≈ 79 min by file-count slope × 2 × 1.02 |
| FXSPSRP | ≈ 90 min (80–100) | SRB +12 / +15 dB chunk 278 s × 0.88 (original-run SRP / SRB ratio at these SNRs: 253.5 / 288.5) |
| FXALDSRP | ≈ 13 min | as SRB |
| acceptance + count tables | ≈ 6 min | ≤ 1 min per row at n = 20480 |
| **total** | **≈ 8 h (7.5–8.5)** | |

## Verified (how)
- **Script** (`bash -n` clean; `diff` against `run_fighsroom16e4.sh`; a dry trace of the ROWS loop that builds every string without running anything): tags FXSRBB16e4 / FXSPSRB / FXALDSRB / FXSRPB16e4 / FXSPSRP / FXALDSRP → controls FXCSRBB16e4 / FXCSPSRB / FXCALDSRB / FXCSRPB16e4 / FXCSPSRP / FXCALDSRP ("FX" occurs once, at position 0, in every tag); `[[ $REF == FX* ]]` true for the four dependent rows; `ACC[$REF]` is set only by the same prior's base row, so an unaccepted or skipped base row skips its own SP / ALD rows and leaves the other prior alone. `_hisnr4` patterns: `acc_extra` A = the absolute `ald_PIL{SRB,SRP}_hisnr4.npz`; T0 / T = PILSRB / PILSRP; the control's `sed` yields `--ald-file …/ald_PIL{SRB,SRP}.npz`, the TEST estimate that the original `raw_ALD{SRB,SRP}` chunks carry in `meta|ald_file`; regen / estimate get `--set hisnr4`; the `case` shas match the files (a3d249188f9c061a / 97a2d08640fef383, ebb14a8952f0ae17 / 8bfc83a43f790bbf); tune `ckpt` == `$CK` for both. Phase C: distinct symlink, raw dir, log and `results/ald` copies per row, so six parallel controls share no written file; `cmp_arms` expects 2 files and each original raw has the `snr12` / `snr15` `skip0_n40` chunks with every ROWS arm. Acceptance strings as intended (`--points C2:12,15 --n 81920 --skip0 10000`; SRP rows with `--kron-K 4096`; SP rows `-:-`). `eval_accept.py` read: a point list that is a subset of the cell's SNRs and n = 81920 are both handled (`plan` = 2048 chunks per SNR, `shared != a.n`). `runner.py` read: no check rejects `--n 81920`; tasks sorted by skip, `imap_unordered`, finished chunks skipped. The SRP ROWS equal the running script's after FH → FX and hisnr → hisnr4.
- **Preconditions / files**: checkpoints ed437f21af15c305 / ac4699c78b3e2d80; picks 4c6da315c701b9d4 / 6ae22a15de019833 (tracked + clean, `per_snr` has "12" and "15"); tune records e0adb06cce792093 / 858087f53952bcbf (tracked + clean, `stop` and `v` have "12.0" / "15.0"); `ll_val` 97.00871495382869 / 244.1932863626755 = `repr` of the fit files; both fits dirs, six original raws (448 files, max skip 2520), both dev pilots present; `git status --porcelain conf/code Demo` empty; DECISIONS.md tracked + clean; no `raw_FX*`, `*FX*` control / count / log file or `*hisnr4*` exists.
- **ald.py**: the diff is the four lines described. `regen --set hisnr4` run from the STAGED copy with `OUT` pointed at the scratch folder and a throw-away tag: 2 SNR × 81920 trials, skip 10000, 106 s, rotation −1.0; on trials 10000..30479 `b`, `H`, `G`, `sigma2` are bit-identical to `pilots_PILSRB_hisnr.npz` at +12 and +15 dB. `estimate` read: output `ald_<tag>_hisnr4.npz`; the control (`--set test` on copies) executes the patched file's unchanged estimate path. No other code keys on the literal "hisnr" (`runner._ald_table` picks the row by `np.isclose(z["snrs"], snr)` and `ALDSitePrior` subtracts the file's `skip`). `ald_py_sha` is written to the records only; nothing compares it.
- **Figure code**: `fighs_merge.py` self-check OK. `paper_f21dmc.py SRB` and `SRP` records byte-identical to `records/paper_f21{srb,srp}.txt`. `SRB hs`: PDF and PNG byte-identical to HEAD's `F21srbhs_col`; the record differs from HEAD's only in the "Asserts passed: counts before the merge …" line and equals the working-tree record. `FIGHS_ALLOW_MISSING=1 … SRB hsx` → rc 0, 22 WARNINGs, `F21srbhsx_col.{pdf,png}`. A half-finished FX raw cannot pass: no count table before acceptance, `load_raw` holes stop it, `nn != n_hs`, and the count-table assert.
- **Registration facts**: the eleven SRB counts at +12 / +15 dB = `fighs_FH{SRBB16e4,SPSRB,ALDSRB}.txt`; "max skip 30440" (file-name scan of every `raw_*` holding SRB / SRP chunks: none above); pools 52,353 / 52,200 (`dmimo.py`); expected distinct draws 41,404 (79.1 %) and 41,333 (79.2 %); R3-bigamp and R4-llr are the only baselines with +12 or +15 dB among their decision SNRs, on both priors (`pairB_SPSRB.txt`, `pairB_SPSRP.txt`); `runner.py run --device cuda` is refused; FIGHSROOM16e4 §6.6 exists (uncommitted) and says what the draft quotes.
- Inherited review items that held: finite-pool disclosure, record command with the absolute python path, absolute `--ald-file` path, split predictions, timing disclosure, GMM caveat citation.

## Not verified
- Anything on a GPU: `estimate --set hisnr4` at B = 81920 (S-5), its run time, GPU availability overnight.
- Any result or log content of the running SRP supplement; its real row durations (file-count projection only). `regen --set hisnr4` was run for SRB only (SRP: the skip loop was timed, not the regen).
- The six-way parallel phase C and the n = 81920 acceptance were read and traced, not executed.
- That the user was told how the GPU instruction was handled; what the v2 commit will contain and that nothing is committed before FIGHSPATH16e4's FIGHS_DONE.

## Scratch artefacts left by this review
`/tmp/claude-1005/-home-HTJ-t2/b187bcb3-67a6-4fa2-86ce-8a8ed017508c/scratchpad/fighsx_review/`: test renders, harness scripts, the patched scratch copies (`paper_f21dmc_fix.py`, `paper_f21dmc_fix2.py`, `fighs_merge_fix.py`) and `pilots_ZZREVIEW_hisnr4.npz` (168 MB). That last file holds the pilot observations and channels of SRB trials 10000..91919 at +12 / +15 dB — inputs only, no ALD or receiver output; only rows 0..20479 were compared, plus one "differs" boolean on the next 20480. Nothing was deleted; it can go.
