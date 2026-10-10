#!/bin/bash
# NEXT_EXPERIMENTS_DMCBASE16e4 §1 (after its freeze commit AND after PRIOR_EVAL_DONE of DMCB16e4): the remaining registered
# baselines on DeepMIMO (prior DMC, cell C2, TEST trials 0..2559 = the trials of raw_DMCB16e4, paired by trial stream), with the
# SAME weights (V1 _best), fits (b* of DMCB16e4) and per-dataset procedures as run_pilot16e4.sh / run_ald16e4.sh /
# run_sparse16e4.sh -- one dataset row, no new rule:
#   PIL  (PILOT16e4 §1)  V1-pilot bstar-pilot R5-genie                      -> raw_PILDMC -> manifest, eval_accept, pair_cross
#   ALD  (ALD16e4 §1)    regen test sites (CPU) -> estimate (ONE free GPU) -> ALD-pilot ALDv-pilot R5-genie -> raw_ALDDMC ->
#                        manifest, eval_accept, pair_ald        [results/ald/tune_PILDMC.json must exist: ald.py tune, §4]
#   SP   (SPARSE16e4 §1) SBL-loop SBL-pilot OMP-pilot R5-genie (--sparse-file pick) -> raw_SPDMC -> manifest, eval_accept,
#                        meta|sparse == pick
#   then pair_baselines over the 15 baselines (12 + the 3 sparse arms), R0-pilot read at iteration 1.
# CPU receiver, GPUs hidden except the ALD estimate.  Each stage is skipped when its output file exists (resume); a failed
# stage stops the script.  Log logs/run_dmc_base.log, end marker "DMC_BASE_DONE".
# Usage: run_dmc_base.sh <ckpt_stem> <best_sha16> <pick_sha16> <tune_ald_sha16>
#   e.g. run_dmc_base.sh d2sx_DMC_N160000_a1 <sha> <sha of results/sparse/pick_DMC_C2.json> <sha of results/ald/tune_PILDMC.json>
cd /home/HTJ/t2/conf || exit 1
P=~/miniforge3/envs/torch/bin/python; L=logs/run_dmc_base.log
PR=DMC; CELL=C2; BT=DMCB16e4; BASE=raw_$BT; BS=kron; KK=4096; LL=122.37953759128766      # b* of DMC16e4 §5 (kron 4096, grid edge)
ST=$1; SHA=$2; PSHA=$3; TSHA=$4; CK=ckpt/${ST}_best.pt; SP=results/sparse/pick_${PR}_$CELL.json; TJ=results/ald/tune_PILDMC.json
REG=results/review_next/NEXT_EXPERIMENTS_DMCBASE16e4.md
log () { echo "[dmc_base $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L >> logs/queue.log; }
die () { log "ABORT: $*"; exit 1; }
[ $# -eq 4 ] || die "usage (4 arguments)"
[ -n "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] && die "conf/code or Demo dirty"
for f in $REG DECISIONS.md $SP ${SP/pick_/tune_} $TJ; do
  [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || die "$f not tracked+clean (freeze first)"
done
grep -q PRIOR_EVAL_DONE logs/run_prior_eval_$BT.log 2>/dev/null || die "the base run $BT is not finished"
[ "$(head -1 results/review_next/${BT}_accept.txt | cut -c1-10)" = "ACCEPT: OK" ] || die "the base run $BT did not pass acceptance"
[ "$(sha256sum $CK | cut -c1-16)" = "$SHA" ] || die "ckpt sha differs"
[ "$(sha256sum $SP | cut -c1-16)" = "$PSHA" ] || die "pick sha differs from §5"
[ "$(sha256sum $TJ | cut -c1-16)" = "$TSHA" ] || die "ALD tune sha differs from §5"
export CUDA_VISIBLE_DEVICES=
COMMON="--testbed D2 --prior $PR --cell $CELL --n 2560 --chunk 40 --ntrain 160000"
KARG="--kron-K $KK"
log "start (git $(git rev-parse --short HEAD)) ckpt=$ST best=$SHA pick=$PSHA ald_tune=$TSHA"

# ---------------------------------------------------------------- PIL (run_pilot16e4.sh body)
T=PILDMC
if [ ! -f results/review_next/pair_$T.txt ]; then
  ln -sfn gmm_fits_D2_$BT results/gmm_fits_D2_$T
  $P code/runner.py run $COMMON --stagec-ckpt /home/HTJ/t2/conf/$CK --pilot-arms --arm V1-pilot bstar-pilot R5-genie --tag $T \
    > logs/run_D2_$T.log 2>&1 || die "PIL run failed"
  $P code/run_manifest.py --tag $T >> $L 2>&1
  $P code/eval_accept.py --prior $PR --tag $T:best:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE \
    > results/review_next/${T}_accept.txt 2>&1 || die "PIL acceptance failed ($(head -1 results/review_next/${T}_accept.txt))"
  log "PIL acceptance ($(head -1 results/review_next/${T}_accept.txt))"
  $P code/pair_cross.py --base $BASE --pilot raw_$T --cell $CELL --prior $PR > results/review_next/pair_$T.txt 2>&1 \
    || die "PIL pair_cross integrity failed"
  log "PIL pair_cross ($(head -1 results/review_next/pair_$T.txt | cut -c1-160))"
fi

# ---------------------------------------------------------------- ALD (run_ald16e4.sh body)
ET=PILDMC; RT=ALDDMC; E=results/ald/ald_$ET.npz
if [ ! -f results/review_next/pair_$RT.txt ]; then
  [ -f results/ald/pilots_${ET}_test.npz ] || $P code/ald.py regen --tag $ET --prior $PR --cell $CELL --fits-tag $BT --set test >> $L 2>&1 \
    || die "ALD regen (test sites) failed"
  if [ ! -f $E ] || [ ! $E -nt $TJ ]; then           # an estimate older than its tune record is recomputed
    G=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1; exit}')
    [ -n "$G" ] || die "no free GPU for the ALD estimate (GPUs are exclusive; no retry)"
    CUDA_VISIBLE_DEVICES=$G $P code/ald.py estimate --tag $ET --ckpt $CK --set test >> $L 2>&1 || die "ALD estimate failed"
    log "ALD estimate on GPU $G done"
  fi
  ln -sfn gmm_fits_D2_$BT results/gmm_fits_D2_$RT
  $P code/runner.py run $COMMON --stagec-ckpt /home/HTJ/t2/conf/$CK --ald-file /home/HTJ/t2/conf/$E \
    --arm ALD-pilot ALDv-pilot R5-genie --tag $RT > logs/run_D2_$RT.log 2>&1 || die "ALD run failed"
  $P code/run_manifest.py --tag $RT >> $L 2>&1
  $P code/eval_accept.py --prior $PR --tag $RT:best:$SHA:$CELL --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE \
    > results/review_next/${RT}_accept.txt 2>&1 || die "ALD acceptance failed ($(head -1 results/review_next/${RT}_accept.txt))"
  log "ALD acceptance ($(head -1 results/review_next/${RT}_accept.txt))"
  $P code/pair_ald.py --base $BASE --pil raw_PILDMC --ald raw_$RT --est $ET --cell $CELL --prior $PR \
    > results/review_next/pair_$RT.txt 2>&1 || die "ALD pair_ald integrity failed"
  log "ALD pair_ald ($(head -1 results/review_next/pair_$RT.txt | cut -c1-160))"
fi

# ---------------------------------------------------------------- SP (run_sparse16e4.sh body)
T=SPDMC
if [ ! -f results/review_next/${T}_accept.txt ]; then
  $P - $SP $CELL $PR <<'PY' >> $L 2>&1 || die "pick not reproduced by the rule / tune not v2b / memory short (see log)"
import sys, os, json, hashlib; sys.path.insert(0, "code"); import common as C, sparse_tune as S   # SPARSE16e4 §5 rule + memory (§1 cost)
sp, cell, prior = sys.argv[1:4]; tp = sp.replace("pick_", "tune_"); pk = json.load(open(sp)); t = json.load(open(tp))
assert t["prior"] == prior and t["cell"] == cell, f"tune JSON is {t['prior']} {t['cell']}, the row wants {prior} {cell}"
assert t["n"] == 256 and t["grid"] == dict(rho=[1, 2, 4, 8, 16], n_em=list(S.NEMS), L=list(S.LS)), f"tune grid/n != v2b: {t['grid']} n {t['n']}"
c = C.CELLS[cell]; N = c["Nr"] * c["Nt"]; r = S.per_snr_pick(t["nmse_db"], c, N, rhos=t["grid"]["rho"])
run = lambda p: (p["rho_sbl"], p["rho_omp"], {s: (e["n_em"], e["L"]) for s, e in p["per_snr"].items()})
ok = run(r) == run(pk)
need = os.cpu_count() * (16 * (pk["rho_omp"] ** 2 * N) ** 2 / 1e9 + 0.3)   # OMP-pilot forms A^H G A (M x M, M = rho^2 N) per call
avail = int(next(l for l in open("/proc/meminfo") if l.startswith("MemAvailable")).split()[1]) / 1e6
sha = lambda f: hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
print(f"[sparse] {sp} sha256[:16]={sha(sp)} tune sha256[:16]={sha(tp)} rule-reproduced={ok} (rho, per-SNR n_em / L) "
      f"memory need ~{need:.0f} GB, available {avail:.0f} GB")
sys.exit(0 if ok and avail >= need else 1)
PY
  ln -sfn gmm_fits_D2_$BT results/gmm_fits_D2_$T
  $P code/runner.py run $COMMON --sparse-file $SP --arm SBL-loop SBL-pilot OMP-pilot R5-genie --tag $T \
    > logs/run_D2_$T.log 2>&1 < /dev/null || die "SP run failed"
  $P code/run_manifest.py --tag $T >> $L 2>&1 < /dev/null
  $P - raw_$T $SP <<'PY' >> $L 2>&1 || die "SP meta|sparse differs from the pick file"
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
  $P code/eval_accept.py --prior $PR --ntrain 160000 --bstar $BS $KARG --ll-val $LL --ref-raw $BASE --tag $T:-:-:$CELL \
    > results/review_next/${T}_accept.txt 2>&1 < /dev/null || die "SP acceptance failed ($(head -1 results/review_next/${T}_accept.txt | cut -c1-80))"
  log "SP acceptance ($(head -1 results/review_next/${T}_accept.txt | cut -c1-80))"
fi

# ---------------------------------------------------------------- pair_baselines (15 baselines + b*; R0-pilot at iteration 1)
O=results/review_next/pairB_SPDMC.txt
echo "# run_dmc_base git $(git rev-parse --short HEAD) $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z')" > $O
$P code/pair_baselines.py --base $BASE --pil raw_PILDMC --ald raw_ALDDMC --est PILDMC --extra raw_SPDMC \
  --add-baselines SBL-loop SBL-pilot OMP-pilot --cell $CELL --prior $PR --r0 at1 --provenance manifest >> $O 2>&1 < /dev/null
rc=$?; log "pair_baselines rc=$rc ($(grep -E '^SUMMARY-B' $O | cut -c1-110))"
log "DMC_BASE_DONE rc=$rc"
exit $rc
