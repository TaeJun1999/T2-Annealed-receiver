#!/bin/bash
# NEXT_EXPERIMENTS_FIGHSX16e4 (REPORT-ONLY figure supplement, user decision 2026-10-11 CDT "2번 해" after "15dB에서 왜 위로 튀지?"):
# the two Sionna RT room panels (priors SRB and SRP) take their +12 and +15 dB points of the 11 legend curves from n = 81920 NEW
# trials per SNR (trials common.HISNR_SKIP0 = 10000..91919, chunk 40; the first 20480 are the trials of the n = 20480 raws raw_FH*).
# This file is code/run_fighsroom16e4.sh (NEXT_EXPERIMENTS_FIGHSROOM16e4, itself code/run_fighs16e4.sh with the changes listed in
# its header -- read those headers for the rules) with ONLY these changes: the registration / log names, SNRS = "12 15" and
# N = 81920, the ROWS table (the three SRB rows of FIGHSROOM16e4 and the three SRP rows of FIGHSPATH16e4 with the tag prefix FX
# instead of FH), the tag prefix in the control / reference patterns (FH -> FX, FHC -> FXC), the ALD set name hisnr -> hisnr4
# (code/ald.py: trials 10000.., n 81920, +12/+15 dB) with the ALD records of PILSRB and PILSRP, both ALD rows in the phase C
# summary line and the fresh-run precondition, the script / registration name printed into the count-table and log headers, the
# six tags in the --resume unreadable-chunk scan, the '# split' lines of the count table (the trials of raw_FH<tag>, seen before
# this run, and the unseen rest; fighs_merge.parse does not read '#' lines), and one more precondition: FIGHSPATH16e4 has printed
# FIGHS_DONE and no runner.py run is alive.
# Usage: bash code/run_fighsx16e4.sh [--resume] [TAG ...]     log logs/run_fighsx16e4.log, end "FIGHS_DONE ok=<n> fail=<n>"
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
L=logs/run_fighsx16e4.log; OUT=results/review_next; LOGD=logs; REG=results/review_next/NEXT_EXPERIMENTS_FIGHSX16e4.md
SK=10000; N=81920; SNRS="12 15"; PTS=${SNRS// /,}
log () { echo "[fighs $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
die () { log "ABORT (precondition): $*"; exit 1; }
RESUME=0; [ "$1" = --resume ] && { RESUME=1; shift; }; WANT=" $* "
# TAG|CELL|PRIOR|FITS|CKPT|SHA16|ROLE|BSTAR|KRON_K|LL_VAL|REF (genie replay)|ORIG (control references)|PICK:SHA16|FLAGS|ARMS
#   CKPT '-' = no --stagec-ckpt (SP rows, as SPARSE16e4); PICK = --sparse-file; ALD rows: FLAGS name the new-trial estimate file
ROWS='FXSRBB16e4|C2|SRB|SRBB16e4|ckpt/d2sx_SRB_N160000_a1_best.pt|ed437f21af15c305|best|gmm1024|-|97.00871495382869|-|SRBB16e4|-||R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie
FXSPSRB|C2|SRB|SRBB16e4|-|-|-|gmm1024|-|97.00871495382869|FXSRBB16e4|SPSRB|results/sparse/pick_SRB_C2.json:4c6da315c701b9d4||SBL-loop SBL-pilot OMP-pilot R5-genie
FXALDSRB|C2|SRB|SRBB16e4|ckpt/d2sx_SRB_N160000_a1_best.pt|ed437f21af15c305|best|gmm1024|-|97.00871495382869|FXSRBB16e4|ALDSRB|-|--ald-file /home/HTJ/t2/conf/results/ald/ald_PILSRB_hisnr4.npz|ALD-pilot R5-genie
FXSRPB16e4|C2|SRP|SRPB16e4|ckpt/d2sx_SRP_N160000_a1_best.pt|ac4699c78b3e2d80|best|kron|4096|244.1932863626755|-|SRPB16e4|-||R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie
FXSPSRP|C2|SRP|SRPB16e4|-|-|-|kron|4096|244.1932863626755|FXSRPB16e4|SPSRP|results/sparse/pick_SRP_C2.json:6ae22a15de019833||SBL-loop SBL-pilot OMP-pilot R5-genie
FXALDSRP|C2|SRP|SRPB16e4|ckpt/d2sx_SRP_N160000_a1_best.pt|ac4699c78b3e2d80|best|kron|4096|244.1932863626755|FXSRPB16e4|ALDSRP|-|--ald-file /home/HTJ/t2/conf/results/ald/ald_PILSRP_hisnr4.npz|ALD-pilot R5-genie'
sel () { [ "$WANT" = "  " ] || [[ "$WANT" == *" $1 "* ]]; }
args () {  # the row's runner flags (globals of the current row): --stagec-ckpt / --sparse-file from the table, then FLAGS
  local a="--testbed D2 --prior $PR --cell $CELL --chunk 40 --ntrain 160000"
  [ "$CK" = - ] || a="$a --stagec-ckpt /home/HTJ/t2/conf/$CK"
  [ "$PICK" = - ] || a="$a --sparse-file ${PICK%%:*}"
  echo "$a $FL"; }
cmp_arms () {  # receiver control: every arm x KEYS_RAW of raw $1 == that arm in the same-named chunk file of the first raw of $2 (comma
  # list) holding it; $3 = expected number of chunk files (one per SNR)
  $P - "$@" <<'PY'
import glob, os, sys
sys.path.insert(0, "code")
import common as C, numpy as np
new, refs, nf, arms = sys.argv[1], sys.argv[2].split(","), int(sys.argv[3]), sys.argv[4:]
fs, bad, n = sorted(glob.glob(new + "/D2_*.npz")), [], 0
for f in fs:
    zs = [np.load(os.path.join(r, os.path.basename(f))) for r in refs if os.path.exists(os.path.join(r, os.path.basename(f)))]
    with np.load(f) as z:
        for a in arms:
            y = next((y for y in zs if f"{a}|blk_err" in y.files), None)
            if y is None:
                bad.append(f"{os.path.basename(f)} {a}: in no reference chunk"); continue
            for k in (f"{a}|{q}" for q in C.KEYS_RAW):
                n += 1
                if k not in z.files or k not in y.files or z[k].shape != y[k].shape or not np.array_equal(
                        np.nan_to_num(z[k], nan=1e300), np.nan_to_num(y[k], nan=1e300)):
                    bad.append(f"{os.path.basename(f)} {k}")
ok = len(fs) == nf and n > 0 and not bad
print(f"control {new} vs {refs}: {len(fs)} chunk files (expected {nf}), arms {arms}, {n} (chunk, arm, key) comparisons, {len(bad)} differ")
print("\n".join("  " + b for b in bad[:20]))
print("CONTROL: " + ("OK" if ok else "FAILED"))
sys.exit(0 if ok else 1)
PY
}
acc_extra () {  # acceptance (f): run|git == HEAD (no +dirty) in every chunk; SP rows meta|sparse == the pick; meta|rotation; meta|ald_file
  local R A; R=$(grep -o -e '--rotation [0-9.]*' <<< "$FL" | cut -d' ' -f2); A=$(grep -o '/[^ ]*_hisnr4\.npz' <<< "$FL")
  $P - "$1" "$H" "${PICK%%:*}" "${R:--}" "${A:--}" <<'PY'
import glob, hashlib, json, re, sys
import numpy as np
raw, h, pick, rot, ald = sys.argv[1:6]
pk = json.load(open(pick)) if pick != "-" else None
af = f"{ald} sha256[:16]={hashlib.sha256(open(ald, 'rb').read()).hexdigest()[:16]}" if ald != "-" else None
fs, bad, gits, ex = sorted(glob.glob(raw + "/D2_*.npz")), [], set(), {}
for f in fs:
    with np.load(f) as z:
        gits.add(str(z["run|git"]) if "run|git" in z.files else None)
        if pk:
            e = pk["per_snr"][re.search(r"_snr(-?\d+)_", f).group(1)]
            bad += [f"{f}: meta|sparse"] if json.loads(str(z["meta|sparse"])) != dict(
                rho_sbl=pk["rho_sbl"], rho_omp=pk["rho_omp"], n_em=e["n_em"], L=e["L"]) else []
        if rot != "-":
            bad += [f"{f}: meta|rotation"] if not str(z["meta|rotation"]).startswith(f"deg={float(rot)!r}:") else []
        if af:
            bad += [f"{f}: meta|ald_file"] if str(z["meta|ald_file"]) != af else []
        for k in z.files:
            if k.endswith("|failed"):
                ex[k[:-7]] = ex.get(k[:-7], 0) + int(z[k].sum())
bad += [f"run|git {sorted(map(str, gits))} != {{{h}}}"] if gits != {h} else []
print(f"  (f) {raw}: {len(fs)} chunk files, run|git {sorted(map(str, gits))}; pick {pick}; rotation {rot}; ald {ald}; "
      f"raised trials per arm (= failures, report only) {ex or 0}")
print("ACCEPT (f): " + ("OK" if fs and not bad else "FAILED " + "; ".join(bad[:10])))
sys.exit(0 if fs and not bad else 1)
PY
}
counts () {  # count table (REPORT-ONLY): failures@16 / n, BLER, 95% Wilson per SNR x arm (a raised block = failure); no test, no label
  $P - "$@" "$H" <<'PY'
import sys
sys.path.insert(0, "code")
import numpy as np
from analysis import load_raw
from hisnr_report import wilson
raw, cell, h = sys.argv[1:4]
d, _, w = load_raw("D2", root=raw)
print(f"# run_fighsx16e4 git {h} {raw} {cell}: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHSX16e4 §1); load_raw warnings {len(w)}")
print("\n".join("# " + x.strip() for x in w))
for k in sorted((k for k in d if k[0] == cell), key=lambda k: k[2]):
    for a in sorted(x for x in d[k] if getattr(d[k][x].get("blk_err"), "ndim", 0) == 2):
        e = np.asarray(d[k][a]["blk_err"], float)[:, -1]; e = np.where(np.isfinite(e), e, 1.0); f, n = int(e.sum()), len(e)
        lo, hi = wilson(f, n); print(f"SNR {k[2]:+.0f}  {a:<20} {f:6d} / {n}  BLER {f / n:.2e}  95% [{lo:.2e}, {hi:.2e}]")
        if n > 20480:   # FIGHSX16e4 §1: the trials of raw_FH<tag> (seen before this run) and the unseen rest; '#' lines are not read by fighs_merge.parse
            g, m = int(e[:20480].sum()), n - 20480; lo, hi = wilson(f - g, m)
            print(f"# split SNR {k[2]:+.0f}  {a:<20} trials 10000..30479 (seen, raw_FH*): {g} of 20480;  trials 30480..{9999 + n} (unseen): {f - g} of {m}  BLER {(f - g) / m:.2e}  95% [{lo:.2e}, {hi:.2e}]")
PY
}
ctl () {  # phase C (2) receiver control, one row (globals of the current row): its runner command on test chunk 0 at $SNRS -> cmp_arms
  local C=${TAG/FX/FXC}
  : > $OUT/${C}_control.txt                       # an early return leaves an EMPTY verdict (gate fails), never an old OK
  ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$C
  echo "# run_fighsx16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') control resume=$RESUME" >> $LOGD/run_D2_$C.log
  $P code/runner.py run $(args | sed 's/_hisnr4\.npz/.npz/') --snr $SNRS --n 40 --arm $ARMS --tag $C >> $LOGD/run_D2_$C.log 2>&1 < /dev/null \
    || { log "$TAG control runner failed ($LOGD/run_D2_$C.log)"; return 1; }
  cmp_arms raw_$C "$(sed 's/[^,]*/raw_&/g' <<< "$ORIG")" $(wc -w <<< "$SNRS") $ARMS > $OUT/${C}_control.txt 2>&1; }
ald_ctl () {  # phase C (1) ALD estimator control, one ALD row: frozen tune record + dev/test pilots copied to the FXC tag (never
  # overwriting), ald.py estimate --set test on one free GPU, hhat / b / v bit-identical to the original test estimate ald_<T0>.npz
  local C=${TAG/FX/FXC} T0 G x; T0=$(grep -o 'ald_[A-Za-z0-9]*_hisnr4' <<< "$FL"); T0=${T0#ald_}; T0=${T0%_hisnr4}
  : > $OUT/${C}_aldcontrol.txt                    # same: no stale CONTROL-ALD: OK can survive an early return
  for x in tune_%s.json pilots_%s_dev.npz pilots_%s_test.npz; do cp --update=none results/ald/$(printf $x $T0) results/ald/$(printf $x $C); done
  G=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1; exit}')
  [ -n "$G" ] || { log "$TAG ALD estimator control: no free GPU (resume later; no automatic retry)"; return 1; }
  log "$TAG ALD estimator control: ald.py estimate --tag $C --set test on GPU $G (copies of the frozen records of $T0)"
  CUDA_VISIBLE_DEVICES=$G $P code/ald.py estimate --tag $C --ckpt $CK --set test >> $L 2>&1 < /dev/null \
    || { log "$TAG ALD estimator control: estimate failed (see $L)"; return 1; }
  $P - results/ald/ald_$C.npz results/ald/ald_$T0.npz > $OUT/${C}_aldcontrol.txt 2>&1 <<'PY'
import sys
import numpy as np
new, ref = sys.argv[1:3]
a, b = np.load(new), np.load(ref)
bad, mx = [], 0.0
for k in ("hhat", "b", "v"):
    same = a[k].shape == b[k].shape
    if same and a[k].size:
        mx = max(mx, float(np.max(np.abs(a[k] - b[k]))))
    if not (same and np.array_equal(a[k], b[k])):
        bad.append(k)
print(f"ALD estimator control {new} vs {ref}: hhat {a['hhat'].shape}, keys hhat b v, max|diff| {mx:.3g}, differing {bad or 'none'}")
print("CONTROL-ALD: " + ("OK" if not bad else "FAILED"))
sys.exit(1 if bad else 0)
PY
}
ald_new () {  # --ald-file rows: the ALD estimate of the new trials (ald.py --set hisnr4 = the FIGHSX16e4 §1 code change), with the frozen tune record
  local E T V G; E=$(grep -o '/[^ ]*_hisnr4\.npz' <<< "$FL"); V=$(grep -o -e '--rotation [0-9.]*' <<< "$FL" | cut -d' ' -f2)
  T=$(basename $E .npz); T=${T#ald_}; T=${T%_hisnr4}
  if [ -f $E ]; then   # only a --resume gets here (a fresh run ABORTs on any ald_*_hisnr4.npz): reuse it only if made on this HEAD
    [ "$($P -c "import json, numpy as np; print(json.loads(str(np.load('$E')['prov']))['git'])" 2>/dev/null)" = "$H" ] \
      && { log "$TAG ALD $T: reusing $E (prov git $H)"; return 0; } \
      || { log "$TAG ABORT: $E exists but its prov git is not $H (stale estimate)"; return 1; }
  fi
  G=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1; exit}')
  [ -n "$G" ] || { log "$TAG ABORT: no free GPU for the ALD estimate (resume later; no automatic retry)"; return 1; }
  log "$TAG ALD $T: regen (CPU) + estimate (GPU $G) on trials $SK.., rotation ${V:-none} (tune record results/ald/tune_$T.json)"
  CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag $T --prior $PR --cell $CELL --fits-tag $BF ${V:+--rotation $V} --set hisnr4 >> $L 2>&1 < /dev/null \
    && CUDA_VISIBLE_DEVICES=$G $P code/ald.py estimate --tag $T --ckpt $CK --set hisnr4 >> $L 2>&1 < /dev/null && [ -f $E ] \
    || { log "$TAG ABORT: ALD regen/estimate failed (see $L)"; return 1; }; }

# ---------------------------------------------------------------- preconditions
[ -z "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] || die "conf/code or Demo dirty"  # PRE
for f in $REG DECISIONS.md; do [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || die "$f not tracked+clean (commit the registration first)"; done  # PRE
[ "$(git log -1 --format=%H -- $REG)" = "$(git rev-parse HEAD)" ] || die "HEAD is not the run commit (the last commit touching $REG); no other commit until FIGHS_DONE"  # PRE
X=$(for t in $(cut -d'|' -f1 <<< "$ROWS"); do ls -d raw_$t raw_${t/FX/FXC} 2>/dev/null; done | tr '\n' ' '); [ $RESUME = 1 ] || [ -z "$X" ] || die "FIGHS raw(s) exist: $X(an interrupted run: --resume; re-running a finished tag needs user approval)"  # PRE
[ $RESUME = 1 ] || [ -z "$(ls results/ald/ald_PILSRB_hisnr4.npz results/ald/ald_PILSRP_hisnr4.npz 2>/dev/null)" ] || die "results/ald/ald_PIL{SRB,SRP}_hisnr4.npz exists before a fresh run (stale ALD estimate)"  # PRE
[ $RESUME = 1 ] || [ -z "$(for t in $(cut -d'|' -f1 <<< "$ROWS"); do c=${t/FX/FXC}; ls $OUT/${c}_control.txt $OUT/${c}_aldcontrol.txt results/ald/*${c}* 2>/dev/null; done)" ] || die "stale FXC control artefacts of this script's rows before a fresh run"  # PRE
grep -q 'FIGHS_DONE' logs/run_fighspath16e4.log 2>/dev/null && ! pgrep -f 'code/runner[.]py run' > /dev/null || die "FIGHSPATH16e4 has not printed FIGHS_DONE (or a runner.py run is still alive) -- §1 순서·자원"  # PRE
H=$(git rev-parse --short HEAD)
[ $RESUME = 0 ] || grep -q "start (git $H)" $L 2>/dev/null || die "--resume: no logged start on this commit $H"  # PRE
for w in $WANT; do grep -q "^$w|" <<< "$ROWS" || die "unknown row '$w'"; done
while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do
  sel $TAG || continue
  [ -d results/gmm_fits_D2_$BF ] || die "$TAG: fits dir results/gmm_fits_D2_$BF missing"
  [ "$CK" = - ] || [ "$(sha256sum $CK | cut -c1-16)" = "$SHA" ] || die "$TAG: $CK sha256[:16] != $SHA"
  [ "$PICK" = - ] || { f=${PICK%%:*}; [ "$(sha256sum $f | cut -c1-16)" = "${PICK##*:}" ] && [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ]; } || die "$TAG: pick $PICK not (sha, tracked, clean)"
  for o in ${ORIG//,/ }; do [ -d raw_$o ] || die "$TAG: original raw raw_$o missing"; done
  [[ $REF == FX* ]] || [ "$REF" = - ] || [ -d raw_$REF ] || die "$TAG: genie reference raw_$REF missing"
  [[ $FL != *--ald-file* ]] || { t=$(grep -o 'ald_[A-Za-z0-9]*_hisnr4' <<< "$FL"); t=${t#ald_}; t=${t%_hisnr4}
    case $t in PILSRB) s=a3d249188f9c061a; p=97a2d08640fef383;; PILSRP) s=ebb14a8952f0ae17; p=8bfc83a43f790bbf;; *) s=unregistered; p=unregistered;; esac
    [ "$(sha256sum results/ald/ald_$t.npz 2>/dev/null | cut -c1-16)" = "$s" ] && [ -f results/ald/pilots_${t}_dev.npz ] && [ "$(sha256sum results/ald/pilots_${t}_test.npz 2>/dev/null | cut -c1-16)" = "$p" ] \
      && [ -n "$(git ls-files results/ald/tune_$t.json)" ] && [ -z "$(git status --porcelain results/ald/tune_$t.json)" ]; } \
    || die "$TAG: ALD records of $t not as registered (test estimate sha256[:16] $s, dev/test pilots present, tune record tracked+clean)"
done <<< "$ROWS"
[ $RESUME = 1 ] && $P - <<'PY' | tee -a $L
import glob, os, numpy as np
bad = 0
for f in sorted(g for t in ("FXSRBB16e4", "FXSPSRB", "FXALDSRB", "FXSRPB16e4", "FXSPSRP", "FXALDSRP") for g in glob.glob(f"raw_{t}/D2_*.npz")):
    try:
        with np.load(f) as z:
            z["run|git"]
    except Exception:
        q = os.path.dirname(f) + ".truncated"; os.makedirs(q, exist_ok=True); os.rename(f, os.path.join(q, os.path.basename(f))); bad += 1
        print(f"[fighs] resume: unreadable chunk {f} moved to {q}/ (the runner recomputes it)")
print(f"[fighs] resume: {bad} unreadable chunk file(s) moved aside")
PY
RW=$(echo $WANT); log "start (git $H) rows: ${RW:-all} resume=$RESUME skip0 $SK n $N SNR $SNRS"; OK=0; FAIL=0; declare -A ACC

# ---------------------------------------------------------------- phase C: controls on the observed test chunk 0 (parallel)
log "phase C: ALD estimator controls (sequential, one free GPU each), then receiver controls (trials 0..39 at $SNRS dB, rows in parallel)"  # CTL
while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do sel $TAG || continue; [[ $FL == *--ald-file* ]] && ald_ctl; done <<< "$ROWS"  # CTL
while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do sel $TAG || continue; ctl & done <<< "$ROWS"  # CTL
wait; log "phase C done: $(for t in $(cut -d'|' -f1 <<< "$ROWS"); do grep -lx 'CONTROL: OK' $OUT/${t/FX/FXC}_control.txt 2>/dev/null; done | wc -l) receiver control(s) OK, $(grep -lx 'CONTROL-ALD: OK' $OUT/FXCALDSRB_aldcontrol.txt $OUT/FXCALDSRP_aldcontrol.txt 2>/dev/null | wc -l) ALD estimator control(s) OK"  # CTL

# ---------------------------------------------------------------- phase R: the rows, in the registered order
while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do
  sel $TAG || continue
  [ "$(git rev-parse --short HEAD)" = "$H" ] || { log "ABORT: HEAD moved from $H during the run"; exit 1; }
  grep -qx 'CONTROL: OK' $OUT/${TAG/FX/FXC}_control.txt 2>/dev/null || { log "$TAG SKIP: control ${TAG/FX/FXC} not OK ($OUT/${TAG/FX/FXC}_control.txt)"; FAIL=$((FAIL+1)); continue; }  # CTL
  [[ $FL != *--ald-file* ]] || grep -qx 'CONTROL-ALD: OK' $OUT/${TAG/FX/FXC}_aldcontrol.txt 2>/dev/null || { log "$TAG SKIP: ALD estimator control not OK ($OUT/${TAG/FX/FXC}_aldcontrol.txt)"; FAIL=$((FAIL+1)); continue; }  # CTL
  [[ $REF == FX* ]] && [ "${ACC[$REF]}" != 0 ] && { log "$TAG SKIP: genie reference $REF not accepted"; FAIL=$((FAIL+1)); continue; }
  [[ $FL == *--ald-file* ]] && { ald_new || { FAIL=$((FAIL+1)); continue; }; }
  ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$TAG
  log "$TAG run: $(args) --snr $SNRS --n $N --skip0 $SK --arm $ARMS"
  echo "# run_fighsx16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') resume=$RESUME" >> $LOGD/run_D2_$TAG.log   # appended: a resume keeps the earlier chunk lines
  $P code/runner.py run $(args) --snr $SNRS --n $N --skip0 $SK --arm $ARMS --tag $TAG >> $LOGD/run_D2_$TAG.log 2>&1 < /dev/null \
    || { log "$TAG ABORT: run failed ($LOGD/run_D2_$TAG.log)"; FAIL=$((FAIL+1)); continue; }
  $P code/run_manifest.py --tag $TAG >> $L 2>&1 < /dev/null || log "$TAG run_manifest rc=$?"
  KARG=; [ "$KK" = - ] || KARG="--kron-K $KK"; RARG=; [ "$REF" = - ] || RARG="--ref-raw raw_$REF"; A=$OUT/${TAG}_accept.txt
  $P code/eval_accept.py --prior $PR --ntrain 160000 --bstar $BS $KARG --ll-val $LL --n $N --skip0 $SK --points $CELL:$PTS \
    --tag $TAG:$ROLE:$SHA:$CELL $RARG > $A 2>&1 < /dev/null; RC=$?
  acc_extra raw_$TAG >> $A 2>&1 || RC=1
  ACC[$TAG]=$RC; log "$TAG acceptance rc=$RC ($(grep -h '^ACCEPT' $A | tr '\n' ' ' | cut -c1-120))"
  [ $RC -eq 0 ] || { log "$TAG INVALID: acceptance failed -- no count table (cause -> §6; a re-run needs user approval)"; FAIL=$((FAIL+1)); continue; }
  counts raw_$TAG $CELL > $OUT/fighs_$TAG.txt 2>&1 && OK=$((OK+1)) || { log "$TAG count table failed rc=$?"; FAIL=$((FAIL+1)); }
done <<< "$ROWS"
log "FIGHS_DONE ok=$OK fail=$FAIL"
exit $FAIL
