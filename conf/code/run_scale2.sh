#!/bin/bash
# NEXT_EXPERIMENTS_SCALE16e4 (array-scaling stage 2; D2 · UMi28, Nr 8 -> 16 -> 32 at N' = 1.6e5): TEST-set BLER of the three new cells
# NR32B16e4 (D2 C9) / U28NR16B16e4 (UMi28 C6) / U28NR32B16e4 (UMi28 C9) + reuse-cell K2 / bridge tags, trend, pair_baselines.
#   bash code/run_scale2.sh tune          after the freeze, GPU: ALD dev tuning per new cell (records go into §5)
#   bash code/run_scale2.sh estimate      after the §5 commit, GPU: ALD test pilots + estimates
#        tune / estimate run the GPU step on CUDA_VISIBLE_DEVICES=<one free GPU> given by the caller (nvidia-smi first), e.g. the
#        gpu_sched.sh queue line  "95 GPU ald_scale2 bash code/run_scale2.sh tune"; the pilot regeneration stays CPU (GPUs hidden)
#   bash code/run_scale2.sh [--resume]    after the §5 commit, CPU, GPUs hidden, after HISNR + SPARSE16e4 on main (DECISIONS 8), in tmux
# ALD command text (integ must 6): CUDA_VISIBLE_DEVICES= ald.py regen --tag PIL<suf> --prior <p> --cell <C> --fits-tag <T> --set dev ->
#   CUDA_VISIBLE_DEVICES=<g> ald.py tune --tag PIL<suf> --ckpt <best> -> ... regen --set test -> ... estimate --tag PIL<suf> --ckpt <best>
#   --set test -> runner.py run ... --ald-file results/ald/ald_PIL<suf>.npz --arm ALD-pilot ALDv-pilot R5-genie --tag ALD<suf>.
# CPU order (§1): reuse K2 x2 -> reuse bridges x3 (+ acceptance) -> per new cell UMi28 C6, UMi28 C9, D2 C9: A -> analysis -> PIL -> ALD
#   -> K2 (only when K_max is the grid edge) -> chk -> <T>last (REPORT-ONLY last-EMA {V1, b*, genie} at the A tag's 3 decision points,
#   DECISIONS 2 / 13; paired recovery_ci + the report-only line "b* last == A") -> run_manifest / guard / recovery_ci -> eval_accept
#   (A ALONE with the grid + <T>chk replay = TREND gate; those two + A+PIL+ALD one call = PAIR gate; chk, K2, last separate calls; every C9 tag also acceptance (k))
#   -> trend frontier_ci, one gate PER LINE (the line's new cells have exactly 3 decision SNRs and all its inputs passed acceptance):
#   primary at 0.95 AND 0.90 (both Holm levels), each as Q-K run (a) both ends + (b) C9 end only (_qkC9) + (c) C2 end only (_qkC2);
#   steps at 0.90; report-only C6 dF_K -> pair_baselines (A + PIL/ALD accepted cells only).
# The §5 values (known only after the freeze) are READ from results/scale/scale2_s5.txt, committed WITH §5, so conf/code stays the
# freeze commit's (DECISIONS 7: git diff <freeze> <§5 commit> -- conf/code Demo empty).  Format (whitespace, '#' comments):
#   FREEZE <freeze commit>
#   WGB <G>     runner --worker-gb G for every C9 run (the §5 K=4096 Nr32 RSS smoke; DECISIONS 5)
#   CELL <tag> <ckpt_stem> <best_sha16> <last_sha16> <bstar> <kron_K|-> <ll_val> <full Ks> <kron Ks> <K2_K|-> <K2_ll|-> <c_K|->
#     e.g. CELL NR32B16e4 d2sx_NR32_N160000_a1 <16 hex> <16 hex> kron 4096 <ll> 16,32,64,128,256,512 16,...,2048,4096 2048 <ll> <c_K>
#     (Ks comma-separated; kron Ks end at K_max; K2_K = K_max/2 only when K_max is the grid edge, else '-' in the last three)
#     CELL <tag> -   = training failed through fb3 (§1 학습 실패 -> (T-iv)): that cell is skipped entirely (no runs, no acceptance); the other cells / dataset run
# Log logs/run_scale2.log (CDT), every step's rc; end "SCALE2_DONE ok=<n> fail=<n>" (tune/estimate: SCALE2_TUNE_DONE / _ESTIMATE_DONE).
# --resume: a complete raw is skipped (the runner skips finished chunks of a partial one); without it an existing stage-2 raw ABORTs
# (re-running a finished tag needs user approval).  Post-run steps (manifest, acceptance, trend, pair) are re-run every time.
cd /home/HTJ/t2_wtS/conf
G=$CUDA_VISIBLE_DEVICES; export CUDA_VISIBLE_DEVICES=          # all CPU; only ald tune / estimate get the caller's GPU $G
P=~/miniforge3/envs/torch/bin/python; L=logs/run_scale2.log; CK=/home/HTJ/t2/conf/ckpt; W=/home/HTJ/t2_wtS/conf
REG=results/review_next/NEXT_EXPERIMENTS_SCALE16e4.md; S5=results/scale/scale2_s5.txt
WGB=$(awk '$1=="WGB"{print $2}' $S5 2>/dev/null)   # <<< §5 value of runner --worker-gb G (C9 cells); acceptance (k): every C9 chunk's meta|worker_gb >= WGB
WGBR=${SCALE2_WGB:-$WGB}   # a raise after the first K=4096 chunk's RSS (§1 memory guard): SCALE2_WGB=<G'> bash code/run_scale2.sh --resume; S5 and HEAD stay (DECISIONS 7)
log () { echo "[scale2 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
die () { log "ABORT (precondition): $*"; exit 1; }
MODE=eval; case $1 in tune|estimate) MODE=$1; shift;; esac; RESUME=0; [ "$1" = "--resume" ] && RESUME=1
exec 9> logs/run_scale2.lock; flock -n 9 || die "another run_scale2.sh holds logs/run_scale2.lock"
# new cells (§1), CPU order: tag suf cell prior
NEW="U28NR16B16e4 U28NR16 C6 UMi28
U28NR32B16e4 U28NR32 C9 UMi28
NR32B16e4    NR32    C9 S2"
# reuse cells (no re-run; §0.1, read-only raws): raw base_fits cell prior ckpt sha role kron_K ll_val decision-SNRs bridge bridge-SNR K2 K2_ll
RU="raw_B16e4k    B16e4k    C2 S2    d2sx_N160000_a1.pt               4443921ce8d5c4a1 legacy-last 1024 -11.459169831224418 -3,0,3 BRB16e4k -3 -           -
raw_NR16B16e4 NR16B16e4 C6 S2    d2sx_NR16_N160000_a1_fb2_best.pt c050d611b2c714a6 best        4096 63.1751571838059    -3,0,3 BRNR16   -3 K2NR16B16e4 61.982398757574266
raw_U28B16e4  U28B16e4  C2 UMi28 d2sx_UMi28_N160000_a1_best.pt    6f3a1b9490864af1 best        4096 5.797910431000217   3,6,9  BRU28    3  K2U28B16e4  5.539276756851168"
RG="full:16,32,64,128,256,512 kron:16,32,64,128,256,512,1024,2048"      # reuse K2 acceptance grid (K_max 4096 left out, ⑥)
# D2 C2 K/2 = raw_B16e4 (kron 512, no run).  c_K = max(1, r/(1-r)), r = dll(1024-512)/dll(512-256) of gmm_fits_D2_B16e4k kron ll_val
# -11.459169831224418 / -14.636106156749378 / -18.416598133332922 -> r 0.8403499716975932; UMi28 C2: 4096/2048/1024 -> r 0.434 -> c_K 1
CK_D2C2=5.2637007373767215; CK_U28C2=1
AARMS="M-ours-dscore-C-V1 M-ours-bstar M-ours-bstar-scalar M-ours-gmm32 R0-pilot R1-turbo R2-ours-G R3-bigamp R4-llr R4-scvamp R5-genie"
CHKARMS="$AARMS"   # chk = the A arm list: eval_accept --ref-arms all takes its key list from raw_<T>, a 3-arm chk would fail by construction
LASTARMS="M-ours-dscore-C-V1 M-ours-bstar R5-genie"   # <T>last = {V1 last-EMA, b*, genie} (DECISIONS 2 / 13): paired R_dp(last) CI
FULL="--n 2560 --chunk 40"; ONE="--n 40 --chunk 40"
s5 () { awk -v t=$1 '$1=="CELL" && $2==t {$1=$2=""; print}' $S5; }   # -> ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK
cellinfo () { $P -c "import sys; sys.path.insert(0, 'code'); import common as C; c = C.CELLS['$1']; print(c['Nr'], len(c['snrs']), c['snrs'][0])"; }
csv () { echo $* | tr ' ' ,; }

# ---- preconditions (a failed one is an ORDER / RESOURCE problem: fix and resume without approval)
[ -z "$(git status --porcelain code ../Demo)" ] || die "conf/code or Demo dirty"
for f in $REG DECISIONS.md; do [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || die "$f not tracked+clean (freeze first)"; done
[ "$($P -c "import sys; sys.path.insert(0, 'code'); import common as C; print(tuple(C.CELLS['C9']['snrs']))")" = "(-12, -9, -6, -3, 0, 3, 6)" ] \
  || die "common.CELLS C9 grid is not the registered -12..+6 (freeze item ①)"
[ -f $S5 ] || die "$S5 missing"
FREEZE=$(awk '$1=="FREEZE"{print $2}' $S5)
git merge-base --is-ancestor "$FREEZE" HEAD 2>/dev/null && git diff --quiet "$FREEZE" HEAD -- code ../Demo \
  || die "FREEZE '$FREEZE' is not an ancestor of HEAD or conf/code / Demo differ from it (DECISIONS 7)"
while read T SUF CELL PR; do
  set -- $(s5 $T)
  [ "$1" = - ] && { log "$T: CELL stem '-' = training failed (§1 학습 실패 -> (T-iv)); the cell is skipped"; continue; }
  [[ $1 =~ ^d2sx_ && $2 =~ ^[0-9a-f]{16}$ ]] || die "$S5: CELL $T ckpt stem / best sha not filled"
  [ "$(sha256sum $CK/${1}_best.pt 2>/dev/null | cut -c1-16)" = "$2" ] || die "$T: $CK/${1}_best.pt sha256 differs from §5 ($2)"
  [ $MODE = tune ] && continue
  [ $# -eq 11 ] && [[ $3 =~ ^[0-9a-f]{16}$ ]] || die "$S5: CELL $T needs 11 filled fields (has $#)"
  [ "$(sha256sum $CK/$1.pt 2>/dev/null | cut -c1-16)" = "$3" ] || die "$T: last-EMA $CK/$1.pt sha256 differs from §5 ($3)"
  [ "$9" = - ] || { [ "$4" = kron ] && [ "${8##*,}" = "$5" ] && [ $(($9 * 2)) -eq $5 ]; } || die "$T: K2_K $9 is not K_max/2 of the kron grid $8 (b* $4 $5)"
  if [ "$9" = - ]; then [ "${10}${11}" = -- ]; else awk -v c="${11}" 'BEGIN {exit !(c == "inf" || c + 0 >= 1)}'; fi || die "$T: K2_ll / c_K '${10}' '${11}' (c_K >= 1 or inf with K2, '-' without)"
  [ $MODE = estimate ] && { [ -f results/ald/tune_PIL$SUF.json ] || die "no ALD tuning record tune_PIL$SUF.json (run 'tune')"; continue; }
  [ -d results/gmm_fits_D2_$T ] || die "fits dir gmm_fits_D2_$T missing"
  for x in PIL$SUF ALD$SUF ${T}chk ${T}last; do
    [ "$(readlink -f results/gmm_fits_D2_$x)" = "$(readlink -f results/gmm_fits_D2_$T)" ] || die "fits link gmm_fits_D2_$x -> gmm_fits_D2_$T missing"
  done
  [ "$9" = - ] || [ -d results/gmm_fits_D2_K2$T ] || die "K/2 fits link set gmm_fits_D2_K2$T missing (⑥)"
  [ results/ald/ald_PIL$SUF.npz -nt results/ald/tune_PIL$SUF.json ] || die "no ALD estimate ald_PIL$SUF.npz newer than its tune record (run 'estimate')"
done <<< "$NEW"
if [ $MODE != tune ]; then
  [ -n "$(git ls-files $S5)" ] && [ -z "$(git status --porcelain $S5)" ] || die "$S5 not tracked+clean (§5 commit first)"
  [ "$(git log -1 --format=%H -- $S5)" = "$(git rev-parse HEAD)" ] || die "HEAD is not the §5 commit (no scale commits after §5: DECISIONS 7)"
fi
if [ $MODE = eval ]; then
  awk -v g="$WGB" -v r="$WGBR" 'BEGIN {exit !(g + 0 > 0 && r + 0 >= g + 0)}' || die "WGB '$WGB' (runner --worker-gb for C9) not set in $S5, or SCALE2_WGB '$WGBR' < WGB (a raise only)"
  pgrep -f 'code/runner.py run' > /dev/null && die "another runner.py run is active (HISNR / SPARSE16e4 first: DECISIONS 8)"
  while read RAW BF CELL PR CKF SHA ROLE KK LL DPS BR S0 K2 K2LL; do
    [ "$(ls $RAW/D2_${CELL}_*.npz 2>/dev/null | wc -l)" -eq 448 ] || die "$RAW: not 448 $CELL chunk files (link /home/HTJ/t2/conf/$RAW)"
    [ "$(sha256sum $CK/$CKF | cut -c1-16)" = "$SHA" ] || die "$CKF sha256 differs from $SHA"
    [ -d results/gmm_fits_D2_$BF ] && [ "$(readlink -f results/gmm_fits_D2_$BR)" = "$(readlink -f results/gmm_fits_D2_$BF)" ] \
      || die "fits link gmm_fits_D2_$BR -> gmm_fits_D2_$BF missing"
    [ "$K2" = - ] || [ -d results/gmm_fits_D2_$K2 ] || die "K/2 fits link set gmm_fits_D2_$K2 missing (⑥)"
  done <<< "$RU"
  [ "$(ls raw_B16e4/D2_C2_*.npz 2>/dev/null | wc -l)" -eq 448 ] || die "raw_B16e4 (D2 C2 K/2) not 448 C2 chunk files"
  EX=$(for t in K2NR16B16e4 K2U28B16e4 BRB16e4k BRNR16 BRU28; do echo raw_$t; done
       while read T SUF CELL PR; do for t in $T PIL$SUF ALD$SUF K2$T ${T}chk ${T}last; do echo raw_$t; done; done <<< "$NEW")
  X=$(for r in $EX; do [ -e $r ] && echo $r; done | tr '\n' ' ')
  [ $RESUME -eq 1 ] || [ -z "$X" ] || die "stage-2 raw(s) exist: $X(resume: --resume)"
fi
H=$(git rev-parse --short HEAD); OK=0; FAIL=0; declare -A ACC DP
log "start $MODE (git $H, freeze $FREEZE, resume $RESUME, WGB ${WGB:-unset} (run ${WGBR:-unset}), GPU '${G}')"
st () { local rc=$1; shift; log "$* rc=$rc"; [ $rc -eq 0 ] && OK=$((OK+1)) || FAIL=$((FAIL+1)); return $rc; }

# ---- GPU modes (ALD; 01_RULES §9.3 precompute exception): pilots on CPU, the Langevin step on GPU $G
if [ $MODE != eval ]; then
  [[ $G =~ ^[0-9]$ ]] || die "set CUDA_VISIBLE_DEVICES=<one free GPU index> for '$MODE' (nvidia-smi; or queue it on logs/gpuq.txt)"
  while read T SUF CELL PR; do
    read ST BSHA REST <<< "$(s5 $T)"; [ "$ST" = - ] && continue; E=PIL$SUF; CKB=ckpt/${ST}_best.pt      # the SAME --ckpt string for tune and estimate (ald.py asserts); '-' = training failed, skipped
    if [ $MODE = tune ]; then
      [ -f results/ald/tune_$E.json ] && { log "$E skip: tune record exists"; continue; }
      [ -f results/ald/pilots_${E}_dev.npz ] || { CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag $E --prior $PR --cell $CELL --fits-tag $T \
        --set dev >> $L 2>&1; st $? "ald regen dev $E"; } || continue
      CUDA_VISIBLE_DEVICES=$G $P code/ald.py tune --tag $E --ckpt $CKB >> logs/ald_tune_$E.log 2>&1
      st $? "ald tune $E on GPU $G ($(grep -h '"c":' logs/ald_tune_$E.log | tail -1 | cut -c1-90))"
    else
      [ -f results/ald/ald_$E.npz ] && [ results/ald/ald_$E.npz -nt results/ald/tune_$E.json ] && { log "$E skip: estimate newer than its tune record"; continue; }
      [ -f results/ald/pilots_${E}_test.npz ] || { CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag $E --prior $PR --cell $CELL --fits-tag $T \
        --set test >> $L 2>&1; st $? "ald regen test $E"; } || continue
      CUDA_VISIBLE_DEVICES=$G $P code/ald.py estimate --tag $E --ckpt $CKB --set test >> $L 2>&1; st $? "ald estimate $E on GPU $G"
    fi
  done <<< "$NEW"
  log "SCALE2_${MODE^^}_DONE ok=$OK fail=$FAIL"; exit $((FAIL > 0))
fi

# ---- CPU (GPUs hidden)
nraw () { ls raw_$1/D2_*.npz 2>/dev/null | wc -l; }
run () {  # tag expected-chunk-files runner-args... ; a complete raw is skipped (resume); HEAD must stay the §5 commit (DECISIONS 7)
  local T=$1 N=$2 rc; shift 2
  [ "$(git rev-parse --short HEAD)" = "$H" ] || { log "ABORT: HEAD moved from $H during the run (DECISIONS 7)"; exit 1; }
  [ "$(nraw $T)" -eq "$N" ] && { log "run $T skip: raw complete ($N files)"; return 0; }
  echo "# run_scale2 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') resume=$RESUME: runner.py run $* --tag $T" >> logs/run_D2_$T.log
  $P code/runner.py run --testbed D2 --ntrain 160000 "$@" --tag $T >> logs/run_D2_$T.log 2>&1 < /dev/null; rc=$?
  [ $rc -eq 0 ] && [ "$(nraw $T)" -ne "$N" ] && rc=99
  st $rc "run $T ($(nraw $T)/$N files)"; }
kchk () {  # acceptance (k), C9 raws: every chunk holds meta|jobs and meta|worker_gb >= WGB (a raise via SCALE2_WGB allowed; value set printed) (memory guard, DECISIONS 5)
  $P - "$WGB" "$@" <<'PY'
import glob, sys, numpy as np
g, bad = float(sys.argv[1]), []
v = lambda z, k: str(z[k].item() if z[k].shape == () else z[k]) if k in z.files else None
for r in sys.argv[2:]:
    wg, jb = set(), set()
    for f in sorted(glob.glob(r + "/D2_*.npz")):
        with np.load(f) as z:
            wg.add(v(z, "meta|worker_gb")); jb.add(v(z, "meta|jobs"))
    print(f"  (k) {r}: meta|worker_gb {sorted(wg, key=str)}  meta|jobs {sorted(jb, key=str)}")
    if not wg or None in wg or None in jb or any(float(x) < g for x in wg):
        bad.append(r)
print("ACCEPT (k): " + ("OK" if not bad else "FAILED " + " ".join(bad)))
raise SystemExit(int(bool(bad)))
PY
}
acc () {  # key eval_accept-args... -> ACC[key], output results/review_next/<key>_accept.txt; a C9 --tag also gets acceptance (k)
  local K=$1 O=results/review_next/$1_accept.txt a p= rs=; shift
  $P code/eval_accept.py --ntrain 160000 "$@" > $O 2>&1 < /dev/null; ACC[$K]=$?
  for a; do [ "$p" = --tag ] && [[ $a == *:C9 ]] && rs="$rs raw_${a%%:*}"; p=$a; done
  [ -z "$rs" ] || kchk $rs >> $O 2>&1 || ACC[$K]=1
  st ${ACC[$K]} "accept $K ($(grep -h '^ACCEPT' $O | tr '\n' ' ' | cut -c1-110))"; }
ok () { local k; for k; do [ "${ACC[$k]:-1}" = 0 ] || return 1; done; }
man () { local t; for t; do [ -d raw_$t ] && { $P code/run_manifest.py --tag $t >> $L 2>&1; st $? "run_manifest $t"; }; done; }
dp () {  # decision SNRs (anchor b*) of tag $1 from the table-B line of the pair (anchored; exactly one block), integers; '' if none
  $P - "$1" <<'PY' 2>> $L
import re, sys
t = open(f"results/tables_D2_{sys.argv[1]}.txt").read()
m = re.findall(r"^  M-ours-bstar -> M-ours-dscore-C-V1 +\[decision-point anchor arm: M-ours-bstar\]\n +decision SNRs \[([^\]]*)\]", t, re.M)
print(" ".join(str(int(float(x.strip("' ")))) for x in m[0].split(",")) if len(m) == 1 and m[0].strip() else "")
PY
}
bsl () {  # REPORT-ONLY integrity line (DECISIONS 13): b* of raw_<T>last == b* of raw_<T> (same trials, fits, code), every KEYS_RAW key
  $P - raw_$1 raw_$1last <<'PY'
import glob, os, sys
sys.path.insert(0, "code")
import common as C, numpy as np
a, l = sys.argv[1:]; bad = n = 0
for f in sorted(glob.glob(l + "/D2_*.npz")):
    with np.load(f) as y, np.load(os.path.join(a, os.path.basename(f))) as z:
        for k in (f"M-ours-bstar|{q}" for q in C.KEYS_RAW):
            if k in y.files or k in z.files:
                n += 1
                bad += k not in y.files or k not in z.files or not np.array_equal(np.nan_to_num(y[k], nan=1e300), np.nan_to_num(z[k], nan=1e300))
print(f"b* last == A (report-only integrity, not a gate; {l} vs {a}): {bad} of {n} (chunk, key) pairs differ -> {'OK' if n and not bad else 'FAIL'}")
raise SystemExit(int(bad > 0 or n == 0))
PY
}

# (1) reuse K2 x2 (b*@K/2 + genie at the recorded decision points), (2) reuse bridges x3 (chunk 0, every arm, current code)
while read RAW BF CELL PR CKF SHA ROLE KK LL DPS BR S0 K2 K2LL; do
  [ "$K2" = - ] || run $K2 192 --prior $PR --cell $CELL --stagec-ckpt $CK/$CKF $FULL --snr ${DPS//,/ } --arm M-ours-bstar R5-genie
done <<< "$RU"
while read RAW BF CELL PR CKF SHA ROLE KK LL DPS BR S0 K2 K2LL; do
  run $BR 1 --prior $PR --cell $CELL --stagec-ckpt $CK/$CKF $ONE --snr $S0
done <<< "$RU"
while read RAW BF CELL PR CKF SHA ROLE KK LL DPS BR S0 K2 K2LL; do
  read NR NS S00 <<< "$(cellinfo $CELL)"; man $K2 $BR
  [ "$K2" = - ] || acc $K2 --prior $PR --nr $NR --bstar kron --kron-K $((KK / 2)) --ll-val $K2LL --points $CELL:$DPS --ref-raw $RAW \
    --fits-dir results/gmm_fits_D2_$K2 --grid "$RG" --tag $K2:$ROLE:$SHA:$CELL
  acc $BR --prior $PR --bstar kron --kron-K $KK --ll-val $LL --n 40 --points $CELL:$S0 --ref-raw $RAW --ref-arms all --tag $BR:$ROLE:$SHA:$CELL
done <<< "$RU"
# D2 C2's K/2 raw_B16e4 (legacy: no run|git / ckpt id -> (c)(f) not applicable): meta kron_K 512, ll_val, genie 4 keys = raw_B16e4k
$P - <<'PY' >> $L 2>&1
import glob, os, numpy as np
bad = 0
for f in sorted(glob.glob("raw_B16e4/D2_C2_*.npz")):
    with np.load(f) as z, np.load("raw_B16e4k/" + os.path.basename(f)) as y:
        bad += int(float(z["meta|kron_K"])) != 512 or abs(float(z["meta|ll_val|kron"]) + 14.636106156749378) > 1e-9
        bad += any(not np.array_equal(np.nan_to_num(z[k], nan=1e300), np.nan_to_num(y[k], nan=1e300))
                   for k in ("R5-genie|blk_err", "R5-genie|ber", "R5-genie|tauL_gmean", "R5-genie|alphaD"))
print(f"raw_B16e4 (D2 C2 K/2 = kron 512 -14.636106156749378): {bad} bad of 448 C2 files")
raise SystemExit(int(bad > 0))
PY
ACC[B16e4]=$?; st ${ACC[B16e4]} "check raw_B16e4 (D2 C2 K/2)"

# (3) new cells
while read T SUF CELL PR; do
  read ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK <<< "$(s5 $T)"; read NR NS S0 <<< "$(cellinfo $CELL)"
  [ "$ST" = - ] && { st 1 "cell $T SKIPPED: training failed through fb3 (§1 학습 실패 -> (T-iv); no runs, no acceptance)"; DP[$T]=""; continue; }
  M=""; [ $CELL = C9 ] && M="--worker-gb $WGBR"                         # memory guard (DECISIONS 5), every C9 run
  B="--prior $PR --cell $CELL $M"; BEST="--stagec-ckpt $CK/${ST}_best.pt"; KARG="--bstar $BS"; [ "$KK" = - ] || KARG="$KARG --kron-K $KK"
  log "$T: ckpt $ST best $BSHA last $LSHA, b* $BS $KK $LL, grid full:$FK kron:$KR, K2 $K2K $K2LL c_K $CKK"
  DP[$T]=""
  if run $T $((NS * 64)) $B $BEST $FULL --arm $AARMS; then
    $P code/runner.py analysis --testbed D2 --tag $T > logs/analysis_$T.log 2>&1 && DP[$T]=$(dp $T)
    st $? "analysis $T"
  fi
  [ "$(echo ${DP[$T]} | wc -w)" -eq 3 ] || { [ -z "${DP[$T]}" ] || log "$T: decision SNRs '${DP[$T]}' != 3 -> guard (T-iv) /" \
    "판정하지 못함 (§1 가드): K2 / last / the trend lines using $T are skipped"; DP[$T]=""; }   # exactly 3 or none
  N3=$(( $(echo ${DP[$T]} | wc -w) * 64 )); log "$T decision SNRs (anchor b*, never by hand): ${DP[$T]:-none}"
  run PIL$SUF $((NS * 64)) $B $BEST $FULL --pilot-arms --arm V1-pilot bstar-pilot R5-genie
  run ALD$SUF $((NS * 64)) $B $BEST $FULL --ald-file $W/results/ald/ald_PIL$SUF.npz --arm ALD-pilot ALDv-pilot R5-genie
  [ -n "${DP[$T]}" ] || st 1 "run K2$T / ${T}last: no decision SNRs"
  [ -n "${DP[$T]}" ] && [ "$K2K" != - ] && run K2$T $N3 $B $BEST $FULL --snr ${DP[$T]} --arm M-ours-bstar R5-genie
  run ${T}chk 1 $B $BEST $ONE --snr $S0 --arm $CHKARMS
  [ -n "${DP[$T]}" ] && run ${T}last $N3 $B --stagec-ckpt $CK/$ST.pt $FULL --snr ${DP[$T]} --arm $LASTARMS   # report-only
  man $T PIL$SUF ALD$SUF K2$T ${T}chk ${T}last
  $P code/guard_report.py --raw raw_$T --testbed D2 > results/guard_D2_$T.txt 2>&1; st $? "guard_report $T"
  $P code/recovery_ci.py --raw raw_$T --cell $CELL --snrs -3 > results/review_next/recovery_$T.txt 2>&1; st $? "recovery_ci $T -3 dB (report-only)"
  if [ -n "${DP[$T]}" ]; then
    $P code/recovery_ci.py --raw raw_$T --cell $CELL --snrs ${DP[$T]} >> results/review_next/recovery_$T.txt 2>&1; st $? "recovery_ci $T at ${DP[$T]}"
    $P code/recovery_ci.py --raw raw_${T}last --cell $CELL --snrs ${DP[$T]} > results/review_next/recovery_${T}last.txt 2>&1
    st $? "recovery_ci ${T}last at ${DP[$T]} (report-only, paired)"
    bsl $T >> results/review_next/recovery_${T}last.txt 2>&1; st $? "b* ${T}last == $T (report-only integrity line, not a gate)"
  fi
  acc $T --prior $PR --nr $NR $KARG --ll-val $LL --fits-dir results/gmm_fits_D2_$T --grid "full:$FK kron:$KR" \
    --tag $T:best:$BSHA:$CELL                                           # A ALONE: grid (a), meta, ckpt id -> TREND gate
  acc ${T}pa --prior $PR $KARG --ll-val $LL --ref-raw raw_$T \
    --tag $T:best:$BSHA:$CELL --tag PIL$SUF:best:$BSHA:$CELL --tag ALD$SUF:best:$BSHA:$CELL   # (b) same fits/em_sec + (d) genie -> PAIR gate
  acc ${T}chk --prior $PR $KARG --ll-val $LL --n 40 --points $CELL:$S0 --ref-raw raw_$T --ref-arms all --tag ${T}chk:best:$BSHA:$CELL
  if [ -n "${DP[$T]}" ]; then
    [ "$K2K" = - ] || acc K2$T --prior $PR --nr $NR --bstar kron --kron-K $K2K --ll-val $K2LL --points $CELL:$(csv ${DP[$T]}) --ref-raw raw_$T \
      --fits-dir results/gmm_fits_D2_K2$T --grid "full:$FK kron:${KR%,*}" --tag K2$T:best:$BSHA:$CELL
    acc ${T}last --prior $PR $KARG --ll-val $LL --points $CELL:$(csv ${DP[$T]}) --ref-raw raw_$T --tag ${T}last:last:$LSHA:$CELL
  fi
done <<< "$NEW"

# (4) trend (frontier_ci, unpaired bootstrap B 2000 seed 20260926): ONE GATE PER LINE (stats2-2 / integ M1) -- a line runs iff every
# new cell it uses has exactly 3 decision SNRs (§1 guard) and every input passed acceptance; a skipped line counts as fail, the others run
declare -A NOTE                                     # extra header line of an output file (forced Q-K qualifier, report-only note)
fci () {  # output-name accepted-keys(comma) frontier_ci-args...
  local F=$1 O=results/review_next/$1.txt N=$2; shift 2
  ok ${N//,/ } || { st 1 "frontier $F SKIPPED: acceptance not passed for one of $N"; return; }
  echo "# run_scale2 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z'): frontier_ci.py $*" > $O
  [ -z "${NOTE[$F]}" ] || echo "${NOTE[$F]}" >> $O
  $P code/frontier_ci.py "$@" >> $O 2>&1 < /dev/null; st $? "frontier $F ($*)"; }
trend () {  # "new cells" output-name accepted-keys frontier_ci-args... : the line runs only if each named cell has exactly 3 decision SNRs
  local CS=$1 c; shift
  for c in $CS; do [ "$(echo ${DP[$c]} | wc -w)" -eq 3 ] || { st 1 "frontier $1 SKIPPED (guard: $c decision SNRs '${DP[$c]}' != 3 -> (T-iv) / 판정하지 못함)"; return; }; done
  fci "$@"; }
qk () {  # C9 tag, C2 K/2 raw, its acceptance key, its c_K -> Q-K args of run (a) ('' = Q-K undefined: a K/2 tag failed acceptance)
  local T=$1 ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK; read ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK <<< "$(s5 $T)"
  if [ "$K2K" = - ]; then ok $3 && echo "--extrap - $2 --ck - $4"; else ok K2$T $3 && echo "--extrap raw_K2$T $2 --ck $CKK $4"; fi; }
qkv () {  # qkC9 | qkC2, run (a)'s "--extrap E1 E2 --ck C1 C2" -> run (b) C9 end only / run (c) C2 end only (the other end '-')
  set -- $1 $2; if [ $1 = qkC9 ]; then echo "$2 $3 - $5 $6 -"; else echo "$2 - $4 $5 - $7"; fi; }
Q_D2=$(qk NR32B16e4 raw_B16e4 B16e4 $CK_D2C2); Q_U28=$(qk U28NR32B16e4 raw_K2U28B16e4 K2U28B16e4 $CK_U28C2)
FQ="# Q-K: [K 상한 민감: 외삽 불가] (forced, §2.1 Q-K (1): a K/2 tag failed acceptance -> this primary runs without --extrap)"
SD2="raw_NR32B16e4:C9:$(csv ${DP[NR32B16e4]})"; SU9="raw_U28NR32B16e4:C9:$(csv ${DP[U28NR32B16e4]})"
SU6="raw_U28NR16B16e4:C6:$(csv ${DP[U28NR16B16e4]})"
[ -n "$Q_D2" ] || log "Q-K D2: undefined (a K/2 tag failed acceptance, or the C9 cell is CELL - = training failed: its lines are skipped anyway) -> forced qualifier in the primary files, no runs (b)(c)"
[ -n "$Q_U28" ] || log "Q-K UMi28: undefined (a K/2 tag failed acceptance, or the C9 cell is CELL - = training failed: its lines are skipped anyway) -> forced qualifier in the primary files, no runs (b)(c)"
for LV in 0.95 0.90; do   # both Holm levels printed (first test 95 %, second 90 %; the Holm order from the p on either file, §1 다중성)
  V=L${LV#0.}
  [ -n "$Q_D2" ] || NOTE[scale2_primary_D2_$V]=$FQ; [ -n "$Q_U28" ] || NOTE[scale2_primary_U28_$V]=$FQ
  trend NR32B16e4 scale2_primary_D2_$V NR32B16e4,NR32B16e4chk,BRB16e4k --recovery "$SD2" "raw_B16e4k:C2:-3,0,3" $Q_D2 --rstar 0.05 --level $LV
  trend U28NR32B16e4 scale2_primary_U28_$V U28NR32B16e4,U28NR32B16e4chk,BRU28 --recovery "$SU9" "raw_U28B16e4:C2:3,6,9" $Q_U28 --rstar 0.05 --level $LV
  for q in qkC9 qkC2; do  # Q-K runs (b) C9 end only / (c) C2 end only; '[K 상한 강건]' only when (a)(b)(c) all give the primary label
    [ -z "$Q_D2" ] || trend NR32B16e4 scale2_primary_D2_${V}_$q NR32B16e4,NR32B16e4chk,BRB16e4k --recovery "$SD2" "raw_B16e4k:C2:-3,0,3" \
      $(qkv $q "$Q_D2") --level $LV
    [ -z "$Q_U28" ] || trend U28NR32B16e4 scale2_primary_U28_${V}_$q U28NR32B16e4,U28NR32B16e4chk,BRU28 --recovery "$SU9" "raw_U28B16e4:C2:3,6,9" \
      $(qkv $q "$Q_U28") --level $LV
  done
done
trend NR32B16e4 scale2_step_D2_S2 NR32B16e4,NR32B16e4chk,BRNR16 --recovery "$SD2" "raw_NR16B16e4:C6:-3,0,3" --rstar 0.05
trend U28NR16B16e4 scale2_step_U28_S1 U28NR16B16e4,U28NR16B16e4chk,BRU28 --recovery "$SU6" "raw_U28B16e4:C2:3,6,9" --rstar 0.05
trend "U28NR32B16e4 U28NR16B16e4" scale2_step_U28_S2 U28NR32B16e4,U28NR32B16e4chk,U28NR16B16e4,U28NR16B16e4chk --recovery "$SU9" "$SU6" --rstar 0.05
# report-only dF_K of the two C6 cells (§1 보고 전용; no label): D2 C6 K/2 = K2NR16B16e4, UMi28 C6 K/2 = K2U28NR16B16e4 (grid edge only)
read _ _ _ _ _ _ _ _ K26 _ CK6 <<< "$(s5 U28NR16B16e4)"
if [ "$K26" = - ]; then E6="- raw_K2NR16B16e4"; CK6S="- 1"; G6=U28NR16B16e4,U28NR16B16e4chk,K2NR16B16e4,BRNR16
else E6="raw_K2U28NR16B16e4 raw_K2NR16B16e4"; CK6S="$CK6 1"; G6=U28NR16B16e4,U28NR16B16e4chk,K2U28NR16B16e4,K2NR16B16e4,BRNR16; fi
NOTE[scale2_report_C6_dFK]="# REPORT-ONLY (§1 보고 전용 ΔF_K, C6 cells): read ONLY the R1+ / R2+ lines (b*(K/2), dF); R1 - R2 compares two datasets, no label"
trend U28NR16B16e4 scale2_report_C6_dFK $G6 --recovery "$SU6" "raw_NR16B16e4:C6:-3,0,3" --extrap $E6 --ck $CK6S

# (5) pair_baselines (table B `X -> V1` for the registered 13; SUPP16e4 §1 X*, R_X*): PAIR gate = A alone + A+PIL+ALD accepted
while read T SUF CELL PR; do
  ok $T ${T}chk ${T}pa || { st 1 "pair_baselines $T SKIPPED: acceptance A / chk / A+PIL+ALD failed (no pair on a failed tag)"; continue; }
  O=results/review_next/pairB_$T.txt; echo "# run_scale2 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z')" > $O
  $P code/pair_baselines.py --base raw_$T --pil raw_PIL$SUF --ald raw_ALD$SUF --est PIL$SUF --cell $CELL --prior $PR --r0 at1 >> $O 2>&1 < /dev/null
  st $? "pair_baselines $T ($(grep -E '^SUMMARY-B' $O | cut -c1-110))"
done <<< "$NEW"
log "SCALE2_DONE ok=$OK fail=$FAIL"
exit $((FAIL > 0))
