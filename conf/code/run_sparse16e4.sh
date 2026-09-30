#!/bin/bash
# NEXT_EXPERIMENTS_SPARSE16e4 §1: SBL-loop / SBL-pilot / OMP-pilot on the 6 static datasets (TEST trials), then acceptance (genie vs
# the base raw) and pair_baselines with the 3 new arms added to the baseline set.  CPU, GPUs hidden.  Run from MAIN (~/t2/conf)
# after the freeze commit (the raws PIL/ALD and the ALD estimates live only there).  Log logs/run_sparse16e4.log, end SPARSE_DONE.
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; L=logs/run_sparse16e4.log; export CUDA_VISIBLE_DEVICES=
log () { echo "[sparse $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
REG=results/review_next/NEXT_EXPERIMENTS_SPARSE16e4.md
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && { log "ABORT: conf/code or Demo dirty"; exit 1; }
for f in $REG DECISIONS.md; do
  [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || { log "ABORT: $f not tracked+clean (freeze first)"; exit 1; }
done
ls results/review_next/pairB_SP*.txt results/review_next/SP*_accept.txt >/dev/null 2>&1 && { log "ABORT: SPARSE outputs exist (re-run needs user approval)"; exit 1; }
H=$(git rev-parse --short HEAD); log "start (git $H)"; OK=0; FAIL=0
# TAG SUF CELL PR BF(base fits) BS KK LL SHA ROLE PICK(results/sparse/pick_<prior>_<cell>.json) BL(b* label) NONI(arms whose STATIC16e4 label is (iv); others (i))
EXPARMS="M-ours-bstar-scalar M-ours-gmm32 R0-pilot@1 R1-turbo R2-ours-G R3-bigamp R4-llr R4-scvamp bstar-pilot V1-pilot ALD-pilot ALDv-pilot"
while read TAG SUF CELL PR BF BS KK LL SHA ROLE SP BL NONI; do
  [ -f "$SP" ] || { log "$TAG ABORT: pick file $SP missing (§5)"; FAIL=$((FAIL+1)); continue; }
  ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_SP$SUF
  $P code/runner.py run --testbed D2 --prior $PR --cell $CELL --n 2560 --chunk 40 --ntrain 160000 --sparse-file $SP \
    --arm SBL-loop SBL-pilot OMP-pilot R5-genie --tag SP$SUF > logs/run_D2_SP$SUF.log 2>&1 < /dev/null \
    || { log "$TAG ABORT: run failed"; FAIL=$((FAIL+1)); continue; }
  $P code/run_manifest.py --tag SP$SUF >> $L 2>&1
  KARG=""; [ "$KK" != "-" ] && KARG="--kron-K $KK"
  $P code/eval_accept.py --prior $PR --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw raw_$TAG --tag SP$SUF:$ROLE:$SHA:$CELL \
    > results/review_next/SP${SUF}_accept.txt 2>&1; RC=$?; log "$TAG acceptance rc=$RC ($(head -1 results/review_next/SP${SUF}_accept.txt | cut -c1-80))"
  [ $RC -ne 0 ] && { log "$TAG INVALID: acceptance failed"; FAIL=$((FAIL+1)); continue; }
  $P - raw_SP$SUF $SP <<'PY' >> $L 2>&1 || { log "$TAG INVALID: meta|sparse differs from the pick file"; FAIL=$((FAIL+1)); continue; }
import sys, json, glob, re, numpy as np          # acceptance (SPARSE16e4 §1): every chunk's meta|sparse == the pick at its SNR
raw, pick = sys.argv[1], json.load(open(sys.argv[2])); bad = 0
for f in glob.glob(f"{raw}/*.npz"):
    snr = re.search(r"_snr(-?\d+)_", f).group(1); e = pick["per_snr"][snr]
    want = dict(rho_sbl=pick["rho_sbl"], rho_omp=pick["rho_omp"], n_em=e["n_em"], L=e["L"])
    bad += json.loads(str(np.load(f)["meta|sparse"])) != want
print(f"[sparse] meta|sparse check {raw}: {bad} mismatching chunks"); sys.exit(1 if bad else 0)
PY
  EX=""; for x in $EXPARMS; do l="(i)"; case ",$NONI," in *",$x,"*) l="(iv)";; esac; EX="$EX --expect $x=$l"; done
  O=results/review_next/pairB_SP$SUF.txt; echo "# run_sparse16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z')" > $O
  $P code/pair_baselines.py --base raw_$TAG --pil raw_PIL$SUF --ald raw_ALD$SUF --est PIL$SUF --extra raw_SP$SUF \
    --add-baselines SBL-loop SBL-pilot OMP-pilot --cell $CELL --prior $PR --r0 at1 --provenance manifest --expect-bstar "$BL" $EX \
    >> $O 2>&1 < /dev/null
  rc=$?; log "$TAG pair_baselines rc=$rc ($(grep -E '^SUMMARY-B' $O | cut -c1-110))"; [ $rc -eq 0 ] && OK=$((OK+1)) || FAIL=$((FAIL+1))
done <<'T'
B16e4k B16e4k C2 S2 B16e4k kron 1024 -11.459169831224418 4443921ce8d5c4a1 legacy-last results/sparse/pick_S2_C2.json (i) -
D3B16e4 D3 C2 S2c D3B16e4 kron 4096 0.08879931165293979 7ebf4e6647d4413f best results/sparse/pick_S2c_C2.json (i) -
SVB16e4 SV C2 SV8e SVB16e4 gmm256 - -47.80545576704972 d2d78962c2846364 best results/sparse/pick_SV8e_C2.json (iv) M-ours-bstar-scalar,M-ours-gmm32,V1-pilot
U28B16e4 U28 C2 UMi28 U28B16e4 kron 4096 5.797910431000217 6f3a1b9490864af1 best results/sparse/pick_UMi28_C2.json (i) -
MXB16e4 MX C2 MIX3 MXB16e4 kron 4096 33.7604873920761 b591ae24ae3c5f31 best results/sparse/pick_MIX3_C2.json (i) -
NR16B16e4 NR16 C6 S2 NR16B16e4 kron 4096 63.1751571838059 c050d611b2c714a6 best results/sparse/pick_S2_C6.json (i) V1-pilot
T
log "SPARSE_DONE ok=$OK fail=$FAIL"
