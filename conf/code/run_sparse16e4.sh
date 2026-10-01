#!/bin/bash
# NEXT_EXPERIMENTS_SPARSE16e4 §1: SBL-loop / SBL-pilot / OMP-pilot on the 6 static datasets (TEST trials), then acceptance (genie vs
# the base raw, meta|sparse vs the pick) and pair_baselines with the 3 new arms added to the baseline set.  CPU, GPUs hidden.  Run
# from MAIN (~/t2/conf) after the freeze commit (the raws PIL/ALD and the ALD estimates live only there; the five C2 pick/tune
# pairs come in with the freeze commit and must be git-tracked + clean).  Order = the table: the five C2 datasets first, NR16 (C6)
# last; the NR16 row starts only when results/sparse/pick_S2_C6.json exists -- if it is not in main yet, the script waits for the
# S2 C6 tuning PROCESS in the sbl worktree ($WT) to exit (never copies a half-written JSON) and copies pick + tune in if tune
# exists; if that process is gone without output, NR16 ABORTs.  Optional args: row suffixes to run (default all, e.g. `NR16`;
# an unknown suffix ABORTs).  Log logs/run_sparse16e4.log, end SPARSE_DONE; exit code = number of failed rows.
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/run_sparse16e4.log; export CUDA_VISIBLE_DEVICES=
WT=/home/HTJ/t2_wtSBL/conf
log () { echo "[sparse $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
REG=results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md
# TAG SUF CELL PR BF(base fits) BS KK LL PICK(results/sparse/pick_<prior>_<cell>.json) PSHA(pick sha256[:16], §5; '-' = made after
# the freeze, logged) BL(b* label) NONI(arms whose STATIC16e4 label is (iv); others (i))
ROWS='B16e4k B16e4k C2 S2 B16e4k kron 1024 -11.459169831224418 results/sparse/pick_S2_C2.json 2a6d79a23b6b6501 (i) -
D3B16e4 D3 C2 S2c D3B16e4 kron 4096 0.08879931165293979 results/sparse/pick_S2c_C2.json afdb48498c76b88c (i) -
SVB16e4 SV C2 SV8e SVB16e4 gmm256 - -47.80545576704972 results/sparse/pick_SV8e_C2.json 72a6500e72950141 (iv) M-ours-bstar-scalar,M-ours-gmm32,V1-pilot
U28B16e4 U28 C2 UMi28 U28B16e4 kron 4096 5.797910431000217 results/sparse/pick_UMi28_C2.json 3d27f1bb72865fa5 (i) -
MXB16e4 MX C2 MIX3 MXB16e4 kron 4096 33.7604873920761 results/sparse/pick_MIX3_C2.json baffec3e463ad6b3 (i) -
NR16B16e4 NR16 C6 S2 NR16B16e4 kron 4096 63.1751571838059 results/sparse/pick_S2_C6.json 3958df589e385522 (i) V1-pilot'
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
for f in $REG DECISIONS.md; do
  [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || { log "ABORT: $f not tracked+clean (freeze first)"; exit 1; }
done
SUFS=" $(awk '{printf "%s ", $2}' <<< "$ROWS")"         # ALD16e4 precedent: an unknown row suffix runs nothing -> ABORT
for w in "$@"; do [[ "$SUFS" == *" $w "* ]] || { log "ABORT: unknown row '$w' (rows:$SUFS)"; exit 1; }; done
H=$(git rev-parse --short HEAD); log "start (git $H) rows: ${*:-all}"; OK=0; FAIL=0
EXPARMS="M-ours-bstar-scalar M-ours-gmm32 R0-pilot@1 R1-turbo R2-ours-G R3-bigamp R4-llr R4-scvamp bstar-pilot V1-pilot ALD-pilot ALDv-pilot"
while read TAG SUF CELL PR BF BS KK LL SP PSHA BL NONI; do
  [ $# -gt 0 ] && [[ " $* " != *" $SUF "* ]] && continue
  [ -n "$(ls results/review_next/pairB_SP$SUF.txt results/review_next/SP${SUF}_accept.txt 2>/dev/null)" ] \
    && { log "$TAG ABORT: SPARSE outputs exist (re-run needs user approval)"; FAIL=$((FAIL+1)); continue; }
  if [ ! -f "$SP" ] && [ "$PSHA" = "-" ]; then          # §5.2: the S2 C6 pick = output of the running tuning, same rule
    log "$TAG waiting for the S2 C6 tuning process ($WT) to exit"
    while pgrep -f "^[^ ]*python[^ ]* code/sparse_tune.py --prior S2 --cell C6" > /dev/null; do sleep 600; done
    # anchored: a shell whose command line merely quotes the string must not match; waiting for the PROCESS (not the file) -> no race
    [ -f "$WT/${SP/pick_/tune_}" ] && cp "$WT/$SP" "$WT/${SP/pick_/tune_}" results/sparse/ && log "$TAG copied $SP + tune from $WT"
  fi
  [ -f "$SP" ] || { log "$TAG ABORT: pick file $SP missing (§5)"; FAIL=$((FAIL+1)); continue; }
  [ "$PSHA" = "-" ] || [ "$(sha256sum $SP | cut -c1-16)" = "$PSHA" ] || { log "$TAG ABORT: $SP sha256 != §5 $PSHA"; FAIL=$((FAIL+1)); continue; }
  [ "$PSHA" = "-" ] || { [ "$(git ls-files $SP ${SP/pick_/tune_} | wc -l)" = 2 ] && [ -z "$(git status --porcelain $SP ${SP/pick_/tune_})" ]; } \
    || { log "$TAG ABORT: $SP / tune JSON not tracked+clean (the freeze commit must hold both)"; FAIL=$((FAIL+1)); continue; }
  $P - $SP $CELL $PR <<'PY' >> $L 2>&1 || { log "$TAG ABORT: pick not reproduced by the rule / tune not v2b / memory short (see log)"; FAIL=$((FAIL+1)); continue; }
import sys, os, json, hashlib; sys.path.insert(0, "code"); import common as C, sparse_tune as S   # §5 rule + memory (§1 cost)
sp, cell, prior = sys.argv[1:4]; tp = sp.replace("pick_", "tune_"); pk = json.load(open(sp)); t = json.load(open(tp))
assert t["prior"] == prior and t["cell"] == cell, f"tune JSON is {t['prior']} {t['cell']}, the row wants {prior} {cell}"
assert t["n"] == 256 and t["grid"] == dict(rho=[1, 2, 4, 8, 16], n_em=list(S.NEMS), L=list(S.LS)), f"tune grid/n != v2b (§5.2: one v2b pass, never extended): {t['grid']} n {t['n']}"   # C6 is not sha-pinned; run_sparse_ext.sh would overwrite the files in place
c = C.CELLS[cell]; N = c["Nr"] * c["Nt"]; r = S.per_snr_pick(t["nmse_db"], c, N, rhos=t["grid"]["rho"])
run = lambda p: (p["rho_sbl"], p["rho_omp"], {s: (e["n_em"], e["L"]) for s, e in p["per_snr"].items()})
ok = run(r) == run(pk)            # §5.2: only the keys runner reads (edge flags / scores are not compared)
need = os.cpu_count() * (16 * (pk["rho_omp"] ** 2 * N) ** 2 / 1e9 + 0.3)   # OMP-pilot forms A^H G A (M x M, M = rho^2 N) per call
avail = int(next(l for l in open("/proc/meminfo") if l.startswith("MemAvailable")).split()[1]) / 1e6
sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
print(f"[sparse] {sp} sha256[:16]={sha(sp)} tune sha256[:16]={sha(tp)} rule-reproduced={ok} (rho, per-SNR n_em / L) "
      f"memory need ~{need:.0f} GB, available {avail:.0f} GB")
sys.exit(0 if ok and avail >= need else 1)
PY
  [ -d raw_SP$SUF ] && log "$TAG resume: raw_SP$SUF holds $(ls raw_SP$SUF | wc -l) chunk files (runner skips finished chunks)"
  ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_SP$SUF
  $P code/runner.py run --testbed D2 --prior $PR --cell $CELL --n 2560 --chunk 40 --ntrain 160000 --sparse-file $SP \
    --arm SBL-loop SBL-pilot OMP-pilot R5-genie --tag SP$SUF > logs/run_D2_SP$SUF.log 2>&1 < /dev/null \
    || { log "$TAG ABORT: run failed"; FAIL=$((FAIL+1)); continue; }
  $P code/run_manifest.py --tag SP$SUF >> $L 2>&1 < /dev/null; log "$TAG run_manifest rc=$?"
  KARG=""; [ "$KK" != "-" ] && KARG="--kron-K $KK"
  $P code/eval_accept.py --prior $PR --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw raw_$TAG --tag SP$SUF:-:-:$CELL \
    > results/review_next/SP${SUF}_accept.txt 2>&1 < /dev/null; RC=$?
  log "$TAG acceptance rc=$RC ($(head -1 results/review_next/SP${SUF}_accept.txt | cut -c1-80))"
  [ $RC -ne 0 ] && { log "$TAG INVALID: acceptance failed"; FAIL=$((FAIL+1)); continue; }
  $P - raw_SP$SUF $SP <<'PY' >> $L 2>&1 || { log "$TAG INVALID: meta|sparse differs from the pick file"; FAIL=$((FAIL+1)); continue; }
import sys, json, glob, re, numpy as np          # acceptance (SPARSE16e4 §1): every chunk's meta|sparse == the pick at its SNR
raw, pick = sys.argv[1], json.load(open(sys.argv[2])); bad = 0; ex = dict.fromkeys(("SBL-loop", "SBL-pilot", "OMP-pilot"), 0)
for f in glob.glob(f"{raw}/*.npz"):
    z = np.load(f); snr = re.search(r"_snr(-?\d+)_", f).group(1); e = pick["per_snr"][snr]
    want = dict(rho_sbl=pick["rho_sbl"], rho_omp=pick["rho_omp"], n_em=e["n_em"], L=e["L"])
    bad += json.loads(str(z["meta|sparse"])) != want
    for a in ex: ex[a] += int(z[a + "|failed"].sum()) if a + "|failed" in z.files else 0
print(f"[sparse] raised trials per new arm (= failures, 01_RULES §4; report only, §6): {ex}")
print(f"[sparse] meta|sparse check {raw}: {bad} mismatching chunks"); sys.exit(1 if bad else 0)
PY
  EX=""; for x in $EXPARMS; do l="(i)"; case ",$NONI," in *",$x,"*) l="(iv)";; esac; EX="$EX --expect $x=$l"; done
  O=results/review_next/pairB_SP$SUF.txt; echo "# run_sparse16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z')" > $O
  $P code/pair_baselines.py --base raw_$TAG --pil raw_PIL$SUF --ald raw_ALD$SUF --est PIL$SUF --extra raw_SP$SUF \
    --add-baselines SBL-loop SBL-pilot OMP-pilot --cell $CELL --prior $PR --r0 at1 --provenance manifest --expect-bstar "$BL" $EX \
    >> $O 2>&1 < /dev/null
  rc=$?; log "$TAG pair_baselines rc=$rc ($(grep -E '^SUMMARY-B' $O | cut -c1-110))"; [ $rc -eq 0 ] && OK=$((OK+1)) || FAIL=$((FAIL+1))
done <<< "$ROWS"
log "SPARSE_DONE ok=$OK fail=$FAIL"
exit $FAIL
