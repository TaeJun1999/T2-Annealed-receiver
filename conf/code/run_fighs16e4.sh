#!/bin/bash
# NEXT_EXPERIMENTS_FIGHS16e4 (REPORT-ONLY figure supplement, user decision 2026-10-06 CDT): the paper BLER-vs-SNR panels F16 (a),
# F17 (a)(b), F20 (b), F21, F22, F24 (c)(d), F31 (b) take their +6..+15 dB points from n = 20480 NEW trials per SNR (trials
# common.HISNR_SKIP0 = 10000..30479, chunk 40) instead of the original test trials 0..2559.  The D2 C2 / C6 arms already in
# raw_HSB16e4k / raw_HSNR16 (HISNR16e4: V1 b* R2 R1 R3 genie, same trials) are reused; this script runs only the MISSING arms, with
# the original raws' checkpoints / GMM fits / tuned hyper-parameters / runner flags (table ROWS, 24 rows, registered order).
#   phase C  controls on already-observed TEST data.  (1) ALD rows, one after the other on one free GPU: ESTIMATOR control -- the
#            frozen tune record and dev/test pilots copied under the FHC... tag, ald.py estimate --set test, hhat / b / v bit-identical
#            to the original test estimate (results/review_next/FHC..._aldcontrol.txt, CONTROL-ALD).  (2) every row, in parallel:
#            RECEIVER control -- the row's own runner command on test chunk 0 (trials 0..39) at +6/+9/+12/+15 dB, every arm x
#            common.KEYS_RAW bit-identical to the original raw(s) ORIG (ALD rows read the original test-set ALD file here)
#            (results/review_next/FHC..._control.txt, CONTROL).  A row whose controls are not OK is not run.
#   phase R  per row: [--ald-file rows: ald.py regen (CPU) + estimate (GPU, one free GPU) on the new trials -- needs the §4 ald.py
#            change] -> runner (CPU, GPUs hidden) -> run_manifest -> eval_accept (--skip0 10000 --n 20480 --points <cell>:6,9,12,15:
#            chunk plan, meta ntrain/bstar/kron_K/ll_val, ckpt sha/role, iters 16; genie replay vs REF) + (f) run|git == HEAD (no
#            +dirty), meta|sparse == pick (SP rows), meta|rotation, meta|ald_file -> results/review_next/<TAG>_accept.txt ->
#            count table results/review_next/fighs_<TAG>.txt (failures / n, 95% Wilson; no test, no label)
# Usage: bash code/run_fighs16e4.sh [--resume] [TAG ...]   (all 24 rows are run and reported, §1; a TAG subset only to RESUME,
# and it must include the REF row of each of its rows -- that row is re-accepted, its finished chunks are skipped)
# Preconditions (a failed one = ABORT before any run; resume without approval once fixed): conf/code + Demo clean; the registration and
# DECISIONS tracked + clean; HEAD = the run commit (= the last commit touching the registration); raw_FH* absent unless --resume
# (then: same commit as a logged start; unreadable chunk files are moved to raw_<TAG>.truncated/, never deleted); raw_HSB16e4k /
# raw_HSNR16 complete; checkpoint / pick / original ALD test-estimate sha256[:16] as registered; no results/ald/ald_*_hisnr.npz on a
# fresh run (--resume reuses one only if its prov git = HEAD).  Log logs/run_fighs16e4.log (CDT), end "FIGHS_DONE ok=<n> fail=<n>".
cd /home/HTJ/t2/conf; P=~/miniforge3/envs/torch/bin/python; export CUDA_VISIBLE_DEVICES=
L=logs/run_fighs16e4.log; OUT=results/review_next; LOGD=logs; REG=results/review_next/NEXT_EXPERIMENTS_FIGHS16e4.md
SK=10000; N=20480; SNRS="6 9 12 15"; PTS=${SNRS// /,}
log () { echo "[fighs $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
die () { log "ABORT (precondition): $*"; exit 1; }
RESUME=0; [ "$1" = --resume ] && { RESUME=1; shift; }; WANT=" $* "
# TAG|CELL|PRIOR|FITS|CKPT|SHA16|ROLE|BSTAR|KRON_K|LL_VAL|REF (genie replay)|ORIG (control references)|PICK:SHA16|FLAGS|ARMS
#   CKPT '-' = no --stagec-ckpt (SP rows, as SPARSE16e4); PICK = --sparse-file; ALD rows: FLAGS name the new-trial estimate file
ROWS='FHSPB16e4k|C2|S2|B16e4k|-|-|-|kron|1024|-11.459169831224418|HSB16e4k|SPB16e4k|results/sparse/pick_S2_C2.json:2a6d79a23b6b6501||SBL-loop SBL-pilot OMP-pilot R5-genie
FHPILB16e4k|C2|S2|B16e4k|ckpt/d2sx_N160000_a1.pt|4443921ce8d5c4a1|legacy-last|kron|1024|-11.459169831224418|HSB16e4k|PILB16e4k|-|--pilot-arms|V1-pilot bstar-pilot R5-genie
FHB16e4k|C2|S2|B16e4k|ckpt/d2sx_N160000_a1.pt|4443921ce8d5c4a1|legacy-last|kron|1024|-11.459169831224418|HSB16e4k|B16e4k|-||R0-pilot R5-genie
FHD3B16e4|C2|S2c|D3B16e4|ckpt/d2sx_S2c_N160000_a1_best.pt|7ebf4e6647d4413f|best|kron|4096|0.08879931165293979|-|D3B16e4|-||R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie
FHSPD3|C2|S2c|D3B16e4|-|-|-|kron|4096|0.08879931165293979|FHD3B16e4|SPD3|results/sparse/pick_S2c_C2.json:afdb48498c76b88c||SBL-loop SBL-pilot OMP-pilot R5-genie
FHPILD3|C2|S2c|D3B16e4|ckpt/d2sx_S2c_N160000_a1_best.pt|7ebf4e6647d4413f|best|kron|4096|0.08879931165293979|FHD3B16e4|PILD3|-|--pilot-arms|V1-pilot bstar-pilot R5-genie
FHSVB16e4|C2|SV8e|SVB16e4|ckpt/d2sx_SV8e_N160000_a1_best.pt|d2d78962c2846364|best|gmm256|-|-47.80545576704972|-|SVB16e4|-||R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie
FHSPSV|C2|SV8e|SVB16e4|-|-|-|gmm256|-|-47.80545576704972|FHSVB16e4|SPSV|results/sparse/pick_SV8e_C2.json:72a6500e72950141||SBL-loop SBL-pilot OMP-pilot R5-genie
FHPILSV|C2|SV8e|SVB16e4|ckpt/d2sx_SV8e_N160000_a1_best.pt|d2d78962c2846364|best|gmm256|-|-47.80545576704972|FHSVB16e4|PILSV|-|--pilot-arms|V1-pilot bstar-pilot R5-genie
FHU28B16e4|C2|UMi28|U28B16e4|ckpt/d2sx_UMi28_N160000_a1_best.pt|6f3a1b9490864af1|best|kron|4096|5.797910431000217|-|U28B16e4|-||R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie
FHSPU28|C2|UMi28|U28B16e4|-|-|-|kron|4096|5.797910431000217|FHU28B16e4|SPU28|results/sparse/pick_UMi28_C2.json:3d27f1bb72865fa5||SBL-loop SBL-pilot OMP-pilot R5-genie
FHPILU28|C2|UMi28|U28B16e4|ckpt/d2sx_UMi28_N160000_a1_best.pt|6f3a1b9490864af1|best|kron|4096|5.797910431000217|FHU28B16e4|PILU28|-|--pilot-arms|V1-pilot bstar-pilot R5-genie
FHMXB16e4|C2|MIX3|MXB16e4|ckpt/d2sx_MIX3_N160000_a1_best.pt|b591ae24ae3c5f31|best|kron|4096|33.7604873920761|-|MXB16e4|-||R0-pilot R1-turbo R2-ours-G R3-bigamp M-ours-bstar M-ours-dscore-C-V1 R5-genie
FHSPMX|C2|MIX3|MXB16e4|-|-|-|kron|4096|33.7604873920761|FHMXB16e4|SPMX|results/sparse/pick_MIX3_C2.json:baffec3e463ad6b3||SBL-loop SBL-pilot OMP-pilot R5-genie
FHPILMX|C2|MIX3|MXB16e4|ckpt/d2sx_MIX3_N160000_a1_best.pt|b591ae24ae3c5f31|best|kron|4096|33.7604873920761|FHMXB16e4|PILMX|-|--pilot-arms|V1-pilot bstar-pilot R5-genie
FHROTaB16e4k|C2|S2|B16e4k|ckpt/d2sx_N160000_a1.pt|4443921ce8d5c4a1|legacy-last|kron|1024|-11.459169831224418|-|ROTaB16e4k,XLROTaB16e4k|-|--rotation 15|M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R1-turbo R3-bigamp R5-genie
FHXPROTaB16e4k|C2|S2|B16e4k|ckpt/d2sx_N160000_a1.pt|4443921ce8d5c4a1|legacy-last|kron|1024|-11.459169831224418|FHROTaB16e4k|XPROTaB16e4k|-|--rotation 15 --pilot-arms|V1-pilot R5-genie
FHXAROTaB16e4k|C2|S2|B16e4k|ckpt/d2sx_N160000_a1.pt|4443921ce8d5c4a1|legacy-last|kron|1024|-11.459169831224418|FHROTaB16e4k|XAROTaB16e4k|-|--rotation 15 --ald-file /home/HTJ/t2/conf/results/ald/ald_XAROTaB16e4k_hisnr.npz|ALD-pilot R5-genie
FHROTbB16e4k|C2|S2|B16e4k|ckpt/d2sx_N160000_a1.pt|4443921ce8d5c4a1|legacy-last|kron|1024|-11.459169831224418|-|ROTbB16e4k,XLROTbB16e4k|-|--rotation 30|M-ours-dscore-C-V1 M-ours-bstar R2-ours-G R1-turbo R3-bigamp R5-genie
FHXPROTbB16e4k|C2|S2|B16e4k|ckpt/d2sx_N160000_a1.pt|4443921ce8d5c4a1|legacy-last|kron|1024|-11.459169831224418|FHROTbB16e4k|XPROTbB16e4k|-|--rotation 30 --pilot-arms|V1-pilot R5-genie
FHXAROTbB16e4k|C2|S2|B16e4k|ckpt/d2sx_N160000_a1.pt|4443921ce8d5c4a1|legacy-last|kron|1024|-11.459169831224418|FHROTbB16e4k|XAROTbB16e4k|-|--rotation 30 --ald-file /home/HTJ/t2/conf/results/ald/ald_XAROTbB16e4k_hisnr.npz|ALD-pilot R5-genie
FHPILNR16|C6|S2|NR16B16e4|ckpt/d2sx_NR16_N160000_a1_fb2_best.pt|c050d611b2c714a6|best|kron|4096|63.1751571838059|HSNR16|PILNR16|-|--pilot-arms|V1-pilot bstar-pilot R5-genie
FHNR16B16e4|C6|S2|NR16B16e4|ckpt/d2sx_NR16_N160000_a1_fb2_best.pt|c050d611b2c714a6|best|kron|4096|63.1751571838059|HSNR16|NR16B16e4|-||R0-pilot R5-genie
FHSPNR16|C6|S2|NR16B16e4|-|-|-|kron|4096|63.1751571838059|HSNR16|SPNR16|results/sparse/pick_S2_C6.json:3958df589e385522||SBL-loop SBL-pilot OMP-pilot R5-genie'
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
  local R A; R=$(grep -o -e '--rotation [0-9.]*' <<< "$FL" | cut -d' ' -f2); A=$(grep -o '/[^ ]*_hisnr\.npz' <<< "$FL")
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
print(f"# run_fighs16e4 git {h} {raw} {cell}: failures@16 / n, BLER, 95% Wilson -- REPORT-ONLY (FIGHS16e4 §1); load_raw warnings {len(w)}")
print("\n".join("# " + x.strip() for x in w))
for k in sorted((k for k in d if k[0] == cell), key=lambda k: k[2]):
    for a in sorted(x for x in d[k] if getattr(d[k][x].get("blk_err"), "ndim", 0) == 2):
        e = np.asarray(d[k][a]["blk_err"], float)[:, -1]; e = np.where(np.isfinite(e), e, 1.0); f, n = int(e.sum()), len(e)
        lo, hi = wilson(f, n); print(f"SNR {k[2]:+.0f}  {a:<20} {f:6d} / {n}  BLER {f / n:.2e}  95% [{lo:.2e}, {hi:.2e}]")
PY
}
ctl () {  # phase C (2) receiver control, one row (globals of the current row): its runner command on test chunk 0 at $SNRS -> cmp_arms
  local C=${TAG/FH/FHC}
  : > $OUT/${C}_control.txt                       # an early return leaves an EMPTY verdict (gate fails), never an old OK
  ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$C
  echo "# run_fighs16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') control resume=$RESUME" >> $LOGD/run_D2_$C.log
  $P code/runner.py run $(args | sed 's/_hisnr\.npz/.npz/') --snr $SNRS --n 40 --arm $ARMS --tag $C >> $LOGD/run_D2_$C.log 2>&1 < /dev/null \
    || { log "$TAG control runner failed ($LOGD/run_D2_$C.log)"; return 1; }
  cmp_arms raw_$C "$(sed 's/[^,]*/raw_&/g' <<< "$ORIG")" $(wc -w <<< "$SNRS") $ARMS > $OUT/${C}_control.txt 2>&1; }
ald_ctl () {  # phase C (1) ALD estimator control, one ALD row: frozen tune record + dev/test pilots copied to the FHC tag (never
  # overwriting), ald.py estimate --set test on one free GPU, hhat / b / v bit-identical to the original test estimate ald_<T0>.npz
  local C=${TAG/FH/FHC} T0 G x; T0=$(grep -o 'ald_[A-Za-z0-9]*_hisnr' <<< "$FL"); T0=${T0#ald_}; T0=${T0%_hisnr}
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
ald_new () {  # --ald-file rows: the ALD estimate of the new trials (ald.py --set hisnr = §4 code change), with the frozen tune record
  local E T V G; E=$(grep -o '/[^ ]*_hisnr\.npz' <<< "$FL"); V=$(grep -o -e '--rotation [0-9.]*' <<< "$FL" | cut -d' ' -f2)
  T=$(basename $E .npz); T=${T#ald_}; T=${T%_hisnr}
  if [ -f $E ]; then   # only a --resume gets here (a fresh run ABORTs on any ald_*_hisnr.npz): reuse it only if made on this HEAD
    [ "$($P -c "import json, numpy as np; print(json.loads(str(np.load('$E')['prov']))['git'])" 2>/dev/null)" = "$H" ] \
      && { log "$TAG ALD $T: reusing $E (prov git $H)"; return 0; } \
      || { log "$TAG ABORT: $E exists but its prov git is not $H (stale estimate)"; return 1; }
  fi
  G=$(nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits | awk -F', ' '$2 < 100 {print $1; exit}')
  [ -n "$G" ] || { log "$TAG ABORT: no free GPU for the ALD estimate (resume later; no automatic retry)"; return 1; }
  log "$TAG ALD $T: regen (CPU) + estimate (GPU $G) on trials $SK.., rotation $V (tune record results/ald/tune_$T.json)"
  CUDA_VISIBLE_DEVICES= $P code/ald.py regen --tag $T --prior $PR --cell $CELL --fits-tag $BF --rotation $V --set hisnr >> $L 2>&1 < /dev/null \
    && CUDA_VISIBLE_DEVICES=$G $P code/ald.py estimate --tag $T --ckpt $CK --set hisnr >> $L 2>&1 < /dev/null && [ -f $E ] \
    || { log "$TAG ABORT: ALD regen/estimate failed (see $L)"; return 1; }; }

# ---------------------------------------------------------------- preconditions
[ -z "$(git -C /home/HTJ/t2 status --porcelain conf/code Demo)" ] || die "conf/code or Demo dirty"  # PRE
for f in $REG DECISIONS.md; do [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || die "$f not tracked+clean (commit the registration first)"; done  # PRE
[ "$(git log -1 --format=%H -- $REG)" = "$(git rev-parse HEAD)" ] || die "HEAD is not the run commit (the last commit touching $REG); no other commit until FIGHS_DONE"  # PRE
X=$(ls -d raw_FH* 2>/dev/null | tr '\n' ' '); [ $RESUME = 1 ] || [ -z "$X" ] || die "FIGHS raw(s) exist: $X(an interrupted run: --resume; re-running a finished tag needs user approval)"  # PRE
[ $RESUME = 1 ] || [ -z "$(ls results/ald/ald_*_hisnr.npz 2>/dev/null)" ] || die "results/ald/ald_*_hisnr.npz exist before a fresh run: $(ls results/ald/ald_*_hisnr.npz | tr '\n' ' ')(stale ALD estimates)"  # PRE
[ $RESUME = 1 ] || [ -z "$(ls $OUT/FHC*_control.txt $OUT/FHC*_aldcontrol.txt results/ald/*FHC* 2>/dev/null)" ] || die "stale FHC control artefacts before a fresh run"  # PRE
H=$(git rev-parse --short HEAD)
[ $RESUME = 0 ] || grep -q "start (git $H)" $L 2>/dev/null || die "--resume: no logged start on this commit $H"  # PRE
for r in HSB16e4k HSNR16; do [ "$(ls raw_$r | wc -l)" = 2048 ] || die "raw_$r incomplete"; done  # PRE
for w in $WANT; do grep -q "^$w|" <<< "$ROWS" || die "unknown row '$w'"; done
while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do
  sel $TAG || continue
  [ -d results/gmm_fits_D2_$BF ] || die "$TAG: fits dir results/gmm_fits_D2_$BF missing"
  [ "$CK" = - ] || [ "$(sha256sum $CK | cut -c1-16)" = "$SHA" ] || die "$TAG: $CK sha256[:16] != $SHA"
  [ "$PICK" = - ] || { f=${PICK%%:*}; [ "$(sha256sum $f | cut -c1-16)" = "${PICK##*:}" ] && [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ]; } || die "$TAG: pick $PICK not (sha, tracked, clean)"
  for o in ${ORIG//,/ }; do [ -d raw_$o ] || die "$TAG: original raw raw_$o missing"; done
  [[ $REF == FH* ]] || [ "$REF" = - ] || [ -d raw_$REF ] || die "$TAG: genie reference raw_$REF missing"
  [[ $FL != *--ald-file* ]] || { t=$(grep -o 'ald_[A-Za-z0-9]*_hisnr' <<< "$FL"); t=${t#ald_}; t=${t%_hisnr}
    case $t in XAROTaB16e4k) s=4d053e3e69cea6ce; p=844d55939b7bb55a;; XAROTbB16e4k) s=1ea34f2fb53df32c; p=e6c68c6af0f7b72a;; *) s=unregistered; p=unregistered;; esac
    [ "$(sha256sum results/ald/ald_$t.npz 2>/dev/null | cut -c1-16)" = "$s" ] && [ -f results/ald/pilots_${t}_dev.npz ] && [ "$(sha256sum results/ald/pilots_${t}_test.npz 2>/dev/null | cut -c1-16)" = "$p" ] \
      && [ -n "$(git ls-files results/ald/tune_$t.json)" ] && [ -z "$(git status --porcelain results/ald/tune_$t.json)" ]; } \
    || die "$TAG: ALD records of $t not as registered (test estimate sha256[:16] $s, dev/test pilots present, tune record tracked+clean)"
done <<< "$ROWS"
[ $RESUME = 1 ] && $P - <<'PY' | tee -a $L
import glob, os, numpy as np
bad = 0
for f in sorted(g for g in glob.glob("raw_FH*/D2_*.npz") if not os.path.dirname(g).endswith(".truncated")):
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
wait; log "phase C done: $(grep -lx 'CONTROL: OK' $OUT/FHC*_control.txt 2>/dev/null | wc -l) receiver control(s) OK, $(grep -lx 'CONTROL-ALD: OK' $OUT/FHC*_aldcontrol.txt 2>/dev/null | wc -l) ALD estimator control(s) OK"  # CTL

# ---------------------------------------------------------------- phase R: the rows, in the registered order
while IFS='|' read -r TAG CELL PR BF CK SHA ROLE BS KK LL REF ORIG PICK FL ARMS; do
  sel $TAG || continue
  [ "$(git rev-parse --short HEAD)" = "$H" ] || { log "ABORT: HEAD moved from $H during the run"; exit 1; }
  grep -qx 'CONTROL: OK' $OUT/${TAG/FH/FHC}_control.txt 2>/dev/null || { log "$TAG SKIP: control ${TAG/FH/FHC} not OK ($OUT/${TAG/FH/FHC}_control.txt)"; FAIL=$((FAIL+1)); continue; }  # CTL
  [[ $FL != *--ald-file* ]] || grep -qx 'CONTROL-ALD: OK' $OUT/${TAG/FH/FHC}_aldcontrol.txt 2>/dev/null || { log "$TAG SKIP: ALD estimator control not OK ($OUT/${TAG/FH/FHC}_aldcontrol.txt)"; FAIL=$((FAIL+1)); continue; }  # CTL
  [[ $REF == FH* ]] && [ "${ACC[$REF]}" != 0 ] && { log "$TAG SKIP: genie reference $REF not accepted"; FAIL=$((FAIL+1)); continue; }
  [[ $FL == *--ald-file* ]] && { ald_new || { FAIL=$((FAIL+1)); continue; }; }
  ln -sfn gmm_fits_D2_$BF results/gmm_fits_D2_$TAG
  log "$TAG run: $(args) --snr $SNRS --n $N --skip0 $SK --arm $ARMS"
  echo "# run_fighs16e4 git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') resume=$RESUME" >> $LOGD/run_D2_$TAG.log   # appended: a resume keeps the earlier chunk lines
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
