#!/bin/bash
# NEXT_EXPERIMENTS_SEEDSNR16e4 §1 (scale worktree): diffusion-seed robustness of the three SCALE16e4 new cells (Nr 16 / 32) on the TEST set.
# Seed tag <T>s<s> (s = 2, 3) = the SCALE16e4 A tag <T> with ONLY the diffusion checkpoint changed (seed s's _best.pt): same 11 arms,
# fits, trials and receiver code, but ONLY at the a1 decision SNRs (n 2560, chunk 40); CPU, GPUs hidden, C9 runs --worker-gb (SCALE16e4 G).
#   bash code/run_seedsnr16e4.sh [--resume]          in tmux, after the run commit (= §5 + results/scale/seedsnr_s5.txt)
# (0) regression check U28NR16B16e4chkS = the SCALE16e4 chk command (a1 _best, 11 arms, UMi28 C6 -3 dB, chunk 0) under this commit
#     (batch 2 = run commit 2 uses U28NR16B16e4chkS2);
#     eval_accept --ref-arms all against raw_U28NR16B16e4 must be OK, else ABORT (code / environment drift -> user).
# (1) per seed tag: run -> analysis (table B; its anchor-b* decision SNRs must equal the registered a1 ones) -> run_manifest ->
#     guard_report -> recovery_ci (paired R_dp at the decision SNRs) -> eval_accept (chunk plan on the 3 points, meta, ckpt id, genie
#     replay vs raw_<T>, grid; C9 + acceptance (k)) -> eval_accept --ref-arms all, GATE: every non-V1 arm bit-identical to raw_<T>
#     ("arms differing" within {M-ours-dscore-C-V1}, shared 2560/2560, no missing key) -> NO label (§1 statement condition only):
#     frontier_ci dR(s) = R_cell(seed s) - R_C2(a1, the registered SCALE16e4 C2 raw), --level 0.95 (prints the 90 % AND 95 % lines;
#     the transcriber reads the level SCALE16e4 §6.1 used: D2 C9 95 %, UMi28 C9 90 %, UMi28 C6 = step S1 90 %).
# §5 values are READ from results/scale/seedsnr_s5.txt (committed with §5, so conf/code stays the freeze commit's):
#   FREEZE <freeze commit>
#   SEED <tag> <ckpt_stem> <best_sha16>     e.g. SEED U28NR16B16e4s2 d2sx_UMi28NR16_N160000_a2 f956a85c82ed4fb3
#   SEED <tag> -                            training failed through fb3 (§1): no run, counted as 판정 못함
#   (comments only on their own lines).  A seed tag WITHOUT a SEED line (D2 C9 a3 while its §3d ladder is open) is PENDING: not run;
#   after SEEDSNR_DONE add its line in a §5 addendum commit (= run commit 2) and run again with --resume (batch 2).
# a1 cell values (b*, kron_K, ll_val, grids, a1 _best sha) and WGB come from results/scale/scale2_s5.txt (SCALE16e4 §5, committed).
# --resume: a complete raw is skipped (post-run steps are re-run, deterministic); a partial raw continues only when every chunk's run|git
# is HEAD (one commit per raw); without --resume any existing raw of this registration ABORTs.  Log logs/run_seedsnr16e4.log (CDT);
# end "SEEDSNR_DONE ok=<n> fail=<n> pending=<tags> trainfail=<tags>".
cd /home/HTJ/t2_wtS/conf; export CUDA_VISIBLE_DEVICES=
P=~/miniforge3/envs/torch/bin/python; L=logs/run_seedsnr16e4.log; CK=/home/HTJ/t2/conf/ckpt
REG=results/review_next/NEXT_EXPERIMENTS_SEEDSNR16e4.md; S5=results/scale/seedsnr_s5.txt; S2=results/scale/scale2_s5.txt
RUN1=b4433d3c                     # SCALE16e4 run commit: the receiver code of every a1 raw (only this script may be new since)
log () { echo "[seedsnr $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
die () { log "ABORT (precondition): $*"; exit 1; }
RESUME=0; [ "$1" = "--resume" ] && RESUME=1
exec 9> logs/run_seedsnr16e4.lock; flock -n 9 || die "another run_seedsnr16e4.sh holds logs/run_seedsnr16e4.lock"
# a1 tag, cell, Nr, prior, registered decision SNRs (SCALE16e4 §6.1, anchor b*), C2 end of dR (= SCALE16e4 spec 2); run order
A1="U28NR16B16e4 C6 16 UMi28 0,3,6    raw_U28B16e4:C2:3,6,9
U28NR32B16e4 C9 32 UMi28 -3,0,3   raw_U28B16e4:C2:3,6,9
NR32B16e4    C9 32 S2    -9,-6,-3 raw_B16e4k:C2:-3,0,3"
AARMS="M-ours-dscore-C-V1 M-ours-bstar M-ours-bstar-scalar M-ours-gmm32 R0-pilot R1-turbo R2-ours-G R3-bigamp R4-llr R4-scvamp R5-genie"
CHK=U28NR16B16e4chkS
s2c () { awk -v t=$1 '$1=="CELL" && $2==t {$1=$2=""; print}' $S2; }   # -> ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK (a1, SCALE16e4 §5)
sd () { awk -v t=$1 '$1=="SEED" && $2==t {$1=$2=""; print}' $S5; }    # -> STEM SHA | '-' | '' (pending)
nraw () { ls raw_$1/D2_*.npz 2>/dev/null | wc -l; }
WGB=$(awk '$1=="WGB"{print $2}' $S2); WGBR=${SEEDSNR_WGB:-$WGB}      # a raise only (RSS > 1.25 G or OOM -> stop, user, --resume)

# ---- preconditions (a failed one is an ORDER / RESOURCE problem: fix and resume without approval)
[ -z "$(git status --porcelain code ../Demo)" ] || die "conf/code or Demo dirty"
for f in $REG DECISIONS.md $S2 $S5; do [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || die "$f not tracked+clean"; done
[ "$(git log -1 --format=%H -- $S5)" = "$(git rev-parse HEAD)" ] || die "HEAD is not the last commit of $S5 (run commit; no commits after it)"
FREEZE=$(awk '$1=="FREEZE"{print $2}' $S5)
git merge-base --is-ancestor "$FREEZE" HEAD 2>/dev/null && git diff --quiet "$FREEZE" HEAD -- code ../Demo \
  || die "FREEZE '$FREEZE' is not an ancestor of HEAD or conf/code / Demo differ from it"
[ "$(git diff --name-status $RUN1 HEAD -- code ../Demo)" = "$(printf 'A\tconf/code/run_seedsnr16e4.sh')" ] \
  || die "receiver code differs from the SCALE16e4 run commit $RUN1 (only code/run_seedsnr16e4.sh may be new)"
[ "$($P -c "import sys; sys.path.insert(0, 'code'); import common as C; print(tuple(C.CELLS['C9']['snrs']))")" = "(-12, -9, -6, -3, 0, 3, 6)" ] \
  || die "common.CELLS C9 grid is not -12..+6"
awk -v g="$WGB" -v r="$WGBR" 'BEGIN {exit !(g + 0 > 0 && r + 0 >= g + 0)}' || die "WGB '$WGB' missing in $S2, or SEEDSNR_WGB '$WGBR' < WGB"
pgrep -f 'code/runner.py run' > /dev/null && die "another runner.py run is active (one CPU receiver job at a time)"
[ "$(awk '$1=="SEED"{print $2}' $S5 | sort | uniq -d)" = "" ] || die "$S5: duplicate SEED line"
TAGS=""
while read T CELL NR PR DP C2S; do
  read ST BSHA REST <<< "$(s2c $T)"
  [ "$(nraw $T)" -eq 448 ] || die "raw_$T: not 448 chunk files (the a1 A raw)"
  [ "$(sha256sum $CK/${ST}_best.pt 2>/dev/null | cut -c1-16)" = "$BSHA" ] || die "$T: a1 $CK/${ST}_best.pt sha256 differs from $S2"
  for s in 2 3; do
    X=${T}s$s; TAGS="$TAGS $X"; set -- $(sd $X)
    { [ $# -eq 0 ] || [ "$1" = - ]; } && continue
    [ $# -eq 2 ] && [[ $1 =~ ^d2sx_ && $2 =~ ^[0-9a-f]{16}$ ]] || die "$S5: SEED $X needs '<ckpt_stem> <sha16>' or '-'"
    [ "$(sha256sum $CK/${1}_best.pt 2>/dev/null | cut -c1-16)" = "$2" ] || die "$X: $CK/${1}_best.pt sha256 differs from §5 ($2)"
    [ "$(readlink -f results/gmm_fits_D2_$X)" = "$(readlink -f results/gmm_fits_D2_$T)" ] || die "fits link gmm_fits_D2_$X -> gmm_fits_D2_$T missing"
  done
done <<< "$A1"
for t in $(awk '$1=="SEED"{print $2}' $S5); do [[ " $TAGS " == *" $t "* ]] || die "$S5: unknown SEED tag $t"; done
gitok () {  # partial raw: every chunk's run|git must be HEAD (one clean commit per raw)
  $P - "$(git rev-parse HEAD)" raw_$1 <<'PY'
import glob, sys, numpy as np
h, g = sys.argv[1], set()
for f in glob.glob(sys.argv[2] + "/D2_*.npz"):
    with np.load(f) as z:
        g.add(str(z["run|git"]))
raise SystemExit(int(not g or any(not h.startswith(x) for x in g)))
PY
}
# one fresh chk per run commit: a complete raw_$CHK whose run|git is another commit (= a batch-1 raw) means batch 2 -> tag ${CHK}2 (own fits link)
[ "$(nraw $CHK)" -eq 1 ] && ! gitok $CHK && CHK=${CHK}2
[ "$(readlink -f results/gmm_fits_D2_$CHK)" = "$(readlink -f results/gmm_fits_D2_U28NR16B16e4)" ] || die "fits link gmm_fits_D2_$CHK -> gmm_fits_D2_U28NR16B16e4 missing"
for X in $CHK $TAGS; do
  [ -e raw_$X ] || continue
  [ $RESUME -eq 1 ] || die "raw_$X exists (resume: --resume)"
  N=192; [ $X = $CHK ] && N=1
  [ "$(nraw $X)" -eq $N ] || gitok $X || die "partial raw_$X holds chunks of another commit (mixed run|git) -> user"
done
H=$(git rev-parse --short HEAD); OK=0; FAIL=0; PEND=""; TF=""; declare -A ACC
log "start (git $H, freeze $FREEZE, resume $RESUME, chk $CHK, WGB $WGB (run $WGBR), CUDA_VISIBLE_DEVICES='$CUDA_VISIBLE_DEVICES')"
st () { local rc=$1; shift; log "$* rc=$rc"; [ $rc -eq 0 ] && OK=$((OK+1)) || FAIL=$((FAIL+1)); return $rc; }
run () {  # tag expected-chunk-files runner-args... ; a complete raw is skipped; HEAD must stay the run commit
  local X=$1 N=$2 rc; shift 2
  [ "$(git rev-parse --short HEAD)" = "$H" ] || { log "ABORT: HEAD moved from $H during the run"; exit 1; }
  [ "$(nraw $X)" -eq "$N" ] && { log "run $X skip: raw complete ($N files)"; return 0; }
  echo "# run_seedsnr16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') resume=$RESUME: runner.py run $* --tag $X" >> logs/run_D2_$X.log
  $P code/runner.py run --testbed D2 --ntrain 160000 "$@" --tag $X >> logs/run_D2_$X.log 2>&1 < /dev/null; rc=$?
  [ $rc -eq 0 ] && [ "$(nraw $X)" -ne "$N" ] && rc=99
  st $rc "run $X ($(nraw $X)/$N files)"; }
kchk () {  # acceptance (k), C9 raws: every chunk holds meta|jobs and meta|worker_gb >= WGB (value sets printed) -- run_scale2.sh kchk
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
acc () {  # key eval_accept-args... -> ACC[key], results/review_next/<key>_accept.txt; a C9 --tag also gets (k) -- run_scale2.sh acc
  local K=$1 O=results/review_next/$1_accept.txt a p= rs=; shift
  $P code/eval_accept.py --ntrain 160000 "$@" > $O 2>&1 < /dev/null; ACC[$K]=$?
  for a; do [ "$p" = --tag ] && [[ $a == *:C9 ]] && rs="$rs raw_${a%%:*}"; p=$a; done
  [ -z "$rs" ] || kchk $rs >> $O 2>&1 || ACC[$K]=1
  st ${ACC[$K]} "accept $K ($(grep -h '^ACCEPT' $O | tr '\n' ' ' | cut -c1-110))"; }
ok () { local k; for k; do [ "${ACC[$k]:-1}" = 0 ] || return 1; done; }
dp () {  # anchor-b* decision SNRs of tag $1 from its table-B line (exactly one block), integers; '' if none -- run_scale2.sh dp
  $P - "$1" <<'PY' 2>> $L
import re, sys
t = open(f"results/tables_D2_{sys.argv[1]}.txt").read()
m = re.findall(r"^  M-ours-bstar -> M-ours-dscore-C-V1 +\[decision-point anchor arm: M-ours-bstar\]\n +decision SNRs \[([^\]]*)\]", t, re.M)
print(" ".join(str(int(float(x.strip("' ")))) for x in m[0].split(",")) if len(m) == 1 and m[0].strip() else "")
PY
}
refok () {  # tag a1-tag cell output: the --ref-arms all report passes iff only V1 differs (SEEDS16e4 §1 rule; V0/V4/V4b are not run)
  local X=$1 T=$2 C=$3 O=$4
  [ "$(head -1 $O)" = "ACCEPT: OK -- $X" ] && return 0
  [ "$(head -1 $O)" = "ACCEPT: FAILED" ] && [ "$(sed 1d $O | wc -l)" -ge 1 ] && ! sed 1d $O | grep -v -E \
    "^  $X \('$C', -?[0-9]+\): replay vs raw_$T \(all\): shared 2560/2560, arms differing \['M-ours-dscore-C-V1'\] \(max \|diff\| [^)]*\)$" | grep -q .
}

# (0) regression check: the SCALE16e4 chk command under this commit (UMi28 C6, a1 _best, 11 arms, -3 dB, chunk 0), every arm bit-identical
read ST BSHA LSHA BS KK LL FK KR REST <<< "$(s2c U28NR16B16e4)"
run $CHK 1 --prior UMi28 --cell C6 --stagec-ckpt $CK/${ST}_best.pt --n 40 --chunk 40 --snr -3 --arm $AARMS
acc $CHK --prior UMi28 --bstar $BS --kron-K $KK --ll-val $LL --n 40 --points C6:-3 --ref-raw raw_U28NR16B16e4 --ref-arms all \
  --tag $CHK:best:$BSHA:C6
ok $CHK || { log "ABORT: regression check $CHK is not bit-identical to raw_U28NR16B16e4 (code / environment drift) -> user"
             log "SEEDSNR_DONE ok=$OK fail=$FAIL pending=- trainfail=-"; exit 1; }

# (1) seed tags, order of A1, s2 then s3 (A1 on fd 3: no command in the loop can eat it from stdin)
while read -u 3 T CELL NR PR DP C2S; do
  read ST BSHA LSHA BS KK LL FK KR REST <<< "$(s2c $T)"
  M=""; [ $CELL = C9 ] && M="--worker-gb $WGBR"                        # memory guard (SCALE16e4 DECISIONS 5), every C9 run
  for s in 2 3; do
    X=${T}s$s; read STEM SHA <<< "$(sd $X)"
    [ -z "$STEM" ] && { PEND="$PEND $X"; log "$X PENDING: no SEED line yet (§3d ladder open) -> batch 2 (§5 addendum commit, --resume)"; continue; }
    [ "$STEM" = - ] && { TF="$TF $X"; log "$X: training failed through fb3 (§1) -> no run, counted as 판정 못함"; continue; }
    log "$X: ckpt ${STEM}_best.pt sha $SHA; $CELL $PR; a1 decision SNRs $DP; b* $BS $KK $LL; ref raw_$T"
    run $X 192 --prior $PR --cell $CELL $M --stagec-ckpt $CK/${STEM}_best.pt --n 2560 --chunk 40 --snr ${DP//,/ } --arm $AARMS || continue
    $P code/runner.py analysis --testbed D2 --tag $X > logs/analysis_$X.log 2>&1; st $? "analysis $X"
    D=$(dp $X); [ "$D" = "${DP//,/ }" ]; st $? "decision SNRs $X (anchor b*, never by hand): '${D:-none}' == a1 '${DP//,/ }'"; DOK=$?
    $P code/run_manifest.py --tag $X >> $L 2>&1; st $? "run_manifest $X"
    $P code/guard_report.py --raw raw_$X --testbed D2 > results/guard_D2_$X.txt 2>&1; st $? "guard_report $X"
    $P code/recovery_ci.py --raw raw_$X --cell $CELL --snrs ${DP//,/ } > results/review_next/recovery_$X.txt 2>&1; st $? "recovery_ci $X at $DP"
    acc $X --prior $PR --nr $NR --bstar $BS --kron-K $KK --ll-val $LL --points $CELL:$DP --ref-raw raw_$T \
      --fits-dir results/gmm_fits_D2_$X --grid "full:$FK kron:$KR" --tag $X:best:$SHA:$CELL
    O=results/review_next/${X}_refarms.txt
    $P code/eval_accept.py --ntrain 160000 --prior $PR --bstar $BS --kron-K $KK --ll-val $LL --points $CELL:$DP --ref-raw raw_$T \
      --ref-arms all --tag $X:best:$SHA:$CELL > $O 2>&1 < /dev/null
    refok $X $T $CELL $O; st $? "ref-arms all $X (gate: only V1 may differ): $(grep -o 'arms differing \[[^]]*\]' $O | sort -u | tr '\n' ' ')"; ROK=$?
    if ok $X && [ $DOK -eq 0 ] && [ $ROK -eq 0 ]; then   # §1 statement condition input (no label); same command form as SCALE16e4
      F=results/review_next/seedsnr_dR_$X.txt
      echo "# run_seedsnr16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z'): dR(s) = R_$CELL(seed) - R_C2(a1 raw); no label (§1)" > $F
      $P code/frontier_ci.py --recovery "raw_$X:$CELL:$DP" "$C2S" --level 0.95 >> $F 2>&1 < /dev/null; st $? "frontier dR $X"
    else
      st 1 "frontier dR $X SKIPPED: acceptance / decision SNRs / ref-arms gate not passed"
    fi
  done
done 3<<< "$A1"
log "SEEDSNR_DONE ok=$OK fail=$FAIL pending=${PEND:- none} trainfail=${TF:- none}"
exit $((FAIL > 0))
