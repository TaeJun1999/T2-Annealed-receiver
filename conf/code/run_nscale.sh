#!/bin/bash
# NEXT_EXPERIMENTS_NSCALE (equal-budget N-scaling "A2 + C6 6.4e5", user decisions 2026-10-04 CDT): TEST-set CPU BLER on MAIN ~/t2.
#   D2 C2 (Nr 8)  N' 6.4e5 B64e4, 1.28e6 B128e4: A = every arm (B32e4 run ① form, _best) + <T>chk + <T>last (every arm, last-EMA)
#                 + K2<T> (b*@K/2 + genie at -3/0/+3, only when b* = kron 4096 = the cap); base 3.2e5: K2B32e4 + bridge BRB32e4
#   D2 C6 (Nr 16) N' 6.4e5 NR16B64e4: A = 11 arms (SCALE16e4 A form) + chk + last ({V1, b*, genie} at -3/0/+3) + K2NR16B64e4;
#                 base 1.6e5: bridge BRNR16B16e4, K/2 = raw_K2NR16B16e4 (SCALE16e4 raw, linked read-only from ~/t2_wtS)
#   report-only   B64e4k8 = b* of the B64e4 grid PLUS the separate kron 8192 fit (fits tag K8B64e4), {V1, b*, genie} at -3/0/+3;
#                 the 8192 fit never enters any registered b* (it lives only in the link set gmm_fits_D2_B64e4k8)
# Then acceptance (eval_accept + run|git), P1 (table B per new point), P2 (paired trend frontier_ci --paired, Holm m = 2 helper),
# Q-K / Q-OP (frontier_ci --recovery, unpaired; qualifiers compare with L0 = run (a)'s unpaired 'R1 - R2' line, §2.2), secondaries (steps, data efficiency), report-only lines.
#   bash code/run_nscale.sh prep            read-only §5 helper: batched-check verdicts, grids (ll_val / n_iter / it_best / reseeds /
#                                           path / stop), b*, r, c_K, K2 b*, K8, ckpt identity + '# =====' / '# done' / '# resume' lines
#                                           (attempt 1 and every §3d _fb<k> stem), D1 gates, GB' lines,
#                                           base raws -> draft PT / K8 lines for results/nscale/nscale_s5.txt.  No runs, no writes.
#   bash code/run_nscale.sh links           the fits / raw symlinks the runs read (reads the uncommitted S5 draft; creates only,
#                                           never removes or replaces; an existing path that resolves elsewhere ABORTs)
#   bash code/run_nscale.sh [--resume]      eval: after the §5 commit (= run commit), CPU, GPUs hidden, tmux, after SEEDSNR16e4's CPU run
# S5 = results/nscale/nscale_s5.txt (committed WITH §5; conf/code stays the freeze commit's).  Whitespace-separated, '#' comment lines:
#   FREEZE <freeze commit>
#   FALLBACK 0|1     1 = the 1.28e6 point failed (§1 대체 규칙 F1): B128e4* not run, the D2 primary becomes R(6.4e5) - R(3.2e5)
#   PT <tag> <cell> <ntrain> <ckpt_stem> <best_sha16> <last_sha16> <bstar> <kron_K|-> <ll_val> <full Ks> <kron Ks> <K2_K|-> <K2_ll|-> <c_K|-> <gate>
#      gate = PASS | FAIL (D1 sibling, C2) | UNGATED (C6); K2_K / K2_ll / c_K only when b* = kron 4096 (the cap), else '-' '-' '-'
#      ('- - -' WITH b* = kron 4096 = K2 구성 불가 (the K/2 set's b* is not kron 2048) -> forced Q-K qualifier, §1 Q-K)
#   PT <tag> -       that point failed (§3d attempt 3 / fit, §1 대체 규칙): skipped, its lines are (T-iv) / 판정하지 못함
#                    (exactly two fields after PT: 'PT B128e4 -'; 'PT B128e4 C2 1280000 -' ABORTs at the FALLBACK / 14-field checks)
#   K8 <kron_K of the B64e4k8 set's b*> <its ll_val> <run 1|0>     run = 1 only when that b* is kron 8192 (§1 보고 전용)
# Log logs/run_nscale.log (CDT); end "NSCALE_DONE ok=<n> fail=<n>".  --resume: a complete raw is skipped (the runner skips the finished
# chunks of a partial one); without it an existing NSCALE raw ABORTs.  Post-run steps are re-run every time.
# S5 is SINGLE-SHOT (§1 실행 위치·커밋; SCALE16e4 결정 7 analogue): the first eval start writes "<sha256 of S5> <HEAD>" to
# logs/nscale/nscale_s5.start; every later start (--resume or not) ABORTs unless both are identical (a new §5 = user approval + DECISIONS).
cd /home/HTJ/t2/conf
export CUDA_VISIBLE_DEVICES=                        # CPU only (receiver rule); the GPUs belong to the NSCALE GPU queue
P=~/miniforge3/envs/torch/bin/python; CK=/home/HTJ/t2/conf/ckpt; L=logs/run_nscale.log; RV=results/review_next
REG=$RV/NEXT_EXPERIMENTS_NSCALE.md; S5=results/nscale/nscale_s5.txt
log () { echo "[nscale $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $L; }
die () { log "ABORT (precondition): $*"; exit 1; }
MODE=eval; case $1 in prep|links) MODE=$1; shift;; esac; RESUME=0; [ "$1" = "--resume" ] && RESUME=1
GF="16,32,64,128,256,512"; GK="16,32,64,128,256,512,1024,2048,4096"         # registered grid (§1): full / kron, cap 4096
ARM11="M-ours-dscore-C-V1 M-ours-bstar M-ours-bstar-scalar M-ours-gmm32 R0-pilot R1-turbo R2-ours-G R3-bigamp R4-llr R4-scvamp R5-genie"
ARM3="M-ours-dscore-C-V1 M-ours-bstar R5-genie"; ARMK2="M-ours-bstar R5-genie"
FULL="--n 2560 --chunk 40"; ONE="--n 40 --chunk 40"; D3="-3 0 3"
# new points (§1): tag cell Nr N' ckpt_stem (attempt 1; a §3d stem _fb2/_fb3 is what S5 names)
NEW="B64e4     C2 8  640000  d2sx_N640000_a1
B128e4    C2 8  1280000 d2sx_N1280000_a1
NR16B64e4 C6 16 640000  d2sx_NR16_N640000_a1"
# base points (§0, read-only raws; B32e4 §5 / C6B16e4 §5 / SCALE16e4 §5): tag cell N' ckpt_stem best_sha16 kron_K ll_val K2_ll c_K
#   c_K = max(1, r/(1-r)), r = dll(4096-2048)/dll(2048-1024) of the merged kron ll_val: B32e4 r 0.6690245283771841, NR16B16e4 r 0.3816292958923848
BASE="B32e4     C2 320000 d2sx_N320000_a1          035744cbe955984d 4096 -5.942083265612076 -7.792724507139091 2.021371931572057
NR16B16e4 C6 160000 d2sx_NR16_N160000_a1_fb2 c050d611b2c714a6 4096 63.1751571838059   61.982398757574266 1"
s5 () { awk -v t=$1 '$1=="PT" && $2==t {$1=$2=""; print}' $S5 2>/dev/null; }   # -> CELL N STEM BSHA LSHA BS KK LL FK KR K2K K2LL CKK GATE
pt () { [ -n "$(s5 $1)" ] && [ "$(s5 $1 | xargs)" != - ]; }       # the point is in S5 and did not fail

# ================================================================ prep (read-only)
if [ $MODE = prep ]; then
  $P - "$NEW" "$BASE" <<'PY'
import csv, glob, hashlib, os, re, sys
sys.path.insert(0, "code")
import numpy as np
GF, GK = [16, 32, 64, 128, 256, 512], [16, 32, 64, 128, 256, 512, 1024, 2048, 4096]
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()[:16] if os.path.exists(p) else "MISSING"
def grid(d, nr, n):
    out = {}
    for f in sorted(glob.glob(f"{d}/fit_S2_Nr{nr}_*K*_n{n}.npz")):
        m = re.search(r"_(full|kron)K(\d+)_n\d+\.npz$", f)                 # merged files only (candidates end .k0r<r>.npz)
        if m: out[(m[1], int(m[2]))] = f
    return out
def show(d, nr, n, check=True, pr=True):
    g = grid(d, nr, n); ll = {}
    for (fam, K), f in sorted(g.items()):
        z = np.load(f, allow_pickle=True); ll[(fam, K)] = float(z["ll_val"])
        if not pr: continue
        ni, ib = int(z["n_iter"]), int(z["it_best"])
        stop = "cap500" if ni >= 500 else ("patience" if ni - ib >= 40 else "tol")   # §1 정지 사유 규칙 (patience 40, val_every 10)
        path = ("sparse " + str(z["sparse_tol"].tolist())) if "sparse_tol" in z.files and np.isfinite(z["sparse_tol"]).any() else \
               ("batched " + str(z["kron_batched"].tolist()) if "kron_batched" in z.files else "exact (no flag)")
        nc = len(glob.glob(f[:-4] + ".k0r*.npz"))
        print(f"    {fam:4s} K={K:<5d} ll_val {ll[(fam, K)]!r:22s} r{int(z['restart'])} kappa {z['kappa'].item()} n_iter {ni} it_best {ib} "
              f"stop {stop} reseed {int(z['n_reseed'])} sec {float(z['sec']):.0f} {path if fam == 'kron' else ''} cand {nc}"
              f"{' (K>=1024 needs 3)' if fam == 'kron' and K >= 1024 and nc != 3 else ''}")
    miss = [f"{fam}{K}" for fam, Ks_ in (("full", GF), ("kron", GK)) for K in Ks_ if (fam, K) not in g]
    if check and pr: print(f"    grid missing: {miss or 'none'}")
    return ll
def bstar(ll):                                  # arms.gmm_selection on the merged files present (validation ll only)
    llv = {f"gmm{K}": v for (fam, K), v in ll.items() if fam == "full"}
    kr = [(K, v) for (fam, K), v in ll.items() if fam == "kron"]
    kK = max(kr, key=lambda t: t[1])[0] if kr else None
    if kK is not None: llv["kron"] = ll[("kron", kK)]
    b = max(llv, key=llv.get) if llv else None
    return b, (kK if b == "kron" else None), (llv[b] if b else None)
def ident(p):
    if not os.path.exists(p): return f"{os.path.basename(p)}: MISSING"
    import score
    c = score.ckpt_identity(p)
    return f"{os.path.basename(p)}: sha256[:16] {c['sha256_16']} epoch {c['epoch']} best_epoch {c['best_epoch']} role {c['role']} best_val {c['best_val']:.6e}", c
def done(stem):                                 # EVERY '# =====' run header + '# done' / '# resume' line, in log order.  The GB' re-run is the
    lg = f"logs/train_{stem}.log"               # segment holding '# resume ... no epoch trained' (its '# done' wall = the resume's); every other
    l = [x.strip() for x in open(lg)] if os.path.exists(lg) else []   # segment is training (interrupted run = aborted=True '# done', then a new header)
    d = [x for x in l if x.startswith(("# done", "# resume", "# ====="))]
    return " || ".join(d) if d else f"(no '# done' line in {lg})"
print("# NSCALE prep (read-only; §5 helper).  The registered rules are in NEXT_EXPERIMENTS_NSCALE.md §1; these lines only gather the values.")
for row in sys.argv[1].strip().split("\n"):
    T, cell, nr, n, stem = row.split(); nr, n = int(nr), int(n)
    print(f"\n== {T} ({cell}, Nr {nr}, N' {n})")
    vf = f"results/nr{nr}b_batched_check_S2_n{n}.txt"
    print(f"  batched check {vf}: " + (([x.strip() for x in open(vf) if x.startswith("VERDICT")] or ["no VERDICT line"])[-1] if os.path.exists(vf) else "MISSING"))
    oom = [f for f in glob.glob(f"logs/nscale/fit_{T}_*.log") if re.search(r"out of memory|OutOfMemory", open(f, errors="ignore").read())]
    print(f"  fit logs with OOM: {oom or 'none'}")
    ll = show(f"results/gmm_fits_D2_{T}", nr, n)
    b, kK, lv = bstar(ll)
    edge = b == "kron" and kK == 4096
    print(f"  b* = {b} kron_K {kK} ll_val {lv!r}  ({'GRID EDGE = cap 4096' if edge else 'interior'})")
    K2K = K2LL = cK = "-"
    if edge and all(("kron", K) in ll for K in (1024, 2048)):
        r = (ll[("kron", 4096)] - ll[("kron", 2048)]) / (ll[("kron", 2048)] - ll[("kron", 1024)])
        cK = "inf" if r >= 1 else repr(max(1.0, r / (1 - r)))
        b2 = bstar({k: v for k, v in ll.items() if k != ("kron", 4096)})
        ok2 = b2[0] == "kron" and b2[1] == 2048
        cKr = cK                                   # r / c_K stay in the record line even when K2 cannot be built
        if ok2: K2K, K2LL = "2048", repr(b2[2])
        else:   K2K = K2LL = cK = "-"              # S5 '- - -' with b* = kron 4096 = K2 구성 불가 (§1 Q-K 강제 조건) -> qk forces the qualifier
        print(f"  Q-K: r {r!r} -> c_K {cKr};  K2 set b* = {b2[0]} {b2[1]} {b2[2]!r} -> {'kron 2048 OK' if ok2 else 'K2 구성 불가 (forced Q-K qualifier)'}")
    last = f"ckpt/{stem}.pt"
    fbs = sorted({os.path.basename(p)[:-3].removesuffix("_best") for p in glob.glob(f"ckpt/{stem}_fb*.pt")})
    for st in [stem] + fbs:                        # attempt 1, then every §3d stem (_fb<k>) with the same lines (§5 체크포인트 행: 'prep 출력 그대로')
        pre = "" if st == stem else f"[§3d {st}] "
        ib, il = ident(f"ckpt/{st}_best.pt"), ident(f"ckpt/{st}.pt")
        for x in (ib, il): print(f"  {pre}ckpt " + (x if isinstance(x, str) else x[0]))
        if not isinstance(ib, str) and not isinstance(il, str):
            print(f"  {pre}best.epoch == last.best_epoch: {ib[1]['epoch'] == il[1]['best_epoch']}; roles {ib[1]['role']}/{il[1]['role']}")
        if st == stem: print(f"  other attempts of this stem: {sorted(os.path.basename(p) for p in glob.glob(f'ckpt/{stem}_fb*.pt')) or 'none'}")
        print(f"  {pre}training: {done(st)}")
    gate = "UNGATED"
    if cell == "C2":
        rows = [r for r in csv.DictReader(open("results/samplecx.csv")) if int(float(r["N_train"])) == n]
        for r in rows:
            g = {k: float(r[k]) for k in ("GA", "GB", "GC", "GD")}
            ok = g["GA"] <= 1e-6 and g["GB"] <= 0.05 and g["GC"] <= 0.15 and g["GD"] <= 0.20
            print(f"  D1 sibling (samplecx.csv row; last file sx_N{n}_D1[_fb<k>].pt): epochs {r['epochs']} val_loss {r['val_loss']} "
                  f"GA {g['GA']:.3e} GB {g['GB']:.5f} GC {g['GC']:.5f} "
                  f"GD {g['GD']:.5f} csv passed={r['passed']} -> thresholds {'PASS' if ok else 'FAIL'}")
            gate = "PASS" if ok else "FAIL"
        if not rows: print(f"  D1 sibling: no samplecx.csv row for N_train {n}"); gate = "?"
        if len(rows) > 1:                          # resume / re-measure / §3d _fb<k>: the csv has no stem column -> never pick silently
            print(f"  D1 sibling: {len(rows)} samplecx.csv rows for N_train {n} -> gate '?' (the main session resolves it from the row of "
                  f"the ckpt actually used: its '# done' epochs / best val vs the csv epochs / val_loss; §1 자격)"); gate = "?"
        for p in sorted(p for p in glob.glob(f"ckpt/sx_N{n}_D1*.pt") if not p.endswith("_best.pt")):   # last files (D1 gate), _fb<k> included
            print(f"  D1 ckpt {os.path.basename(p)}: sha256[:16] {sha(p)}; training: {done(os.path.basename(p)[:-3])}")
        for r in csv.DictReader(open("results/d2_gbprime.csv")):
            if int(r["ntrain"]) == n:
                print(f"  GB' csv: gmm_ntrain {r['gmm_ntrain']} equal_budget {r['equal_budget']} {r['gmm_bstar']} K {r['gmm_K']} "
                      f"ratio min/max/median {r['ratio_min']}/{r['ratio_max']}/{r['ratio_median']} worst_excess {r['worst_excess']}")
    gl = [f"{os.path.basename(f)}: {x.strip()}" for f in sorted(glob.glob("logs/nscale/*.log")) for x in open(f, errors="ignore")
          if "GMM b* =" in x and f"@N={n}" in x]               # file name: B64e4 and NR16B64e4 both print @N=640000
    print(f"  GB' log lines @N={n}: {gl or 'none'}")
    for f in sorted(glob.glob(f"results/d2_gbprime_{'NR16_' if cell == 'C6' else ''}N{n}_*.npz")):
        m4 = f"results/gmm_fits_D2_{T}/fit_S2_Nr{nr}_kronK4096_n{n}.npz"
        print(f"  GB' npz {f}: newer than the kron 4096 merge: {os.path.exists(m4) and os.path.getmtime(f) > os.path.getmtime(m4)}")
    print(f"  DRAFT  PT {T} {cell} {n} {stem} {sha('ckpt/' + stem + '_best.pt')} {sha(last)} {b} {kK if kK else '-'} {lv!r} "
          f"{','.join(str(K) for (f_, K) in sorted(ll) if f_ == 'full')} {','.join(str(K) for (f_, K) in sorted(ll) if f_ == 'kron')} "
          f"{K2K} {K2LL} {cK} {gate}")
    if T == "B64e4":
        ll8 = show("results/gmm_fits_D2_K8B64e4", 8, n, check=False)
        if ("kron", 8192) in ll8:
            b8 = bstar({**ll, **ll8})
            print(f"  K8: B64e4 grid + kron 8192 -> b* {b8[0]} {b8[1]} {b8[2]!r}; dll(8192-4096) "
                  f"{ll8[('kron', 8192)] - ll.get(('kron', 4096), float('nan')):+.4f}")
            print(f"  DRAFT  K8 {b8[1] if b8[1] else '-'} {b8[2]!r} {int(b8[1] == 8192)}")
        else:
            print("  DRAFT  K8 - - 0   (no merged kron 8192 fit)")
print("\n== base points (read-only)")
for row in sys.argv[2].strip().split("\n"):
    T, cell, n, stem, bsha = row.split()[:5]
    nf = len(glob.glob(f"raw_{T}/D2_{cell}_*.npz"))
    print(f"  raw_{T}: {nf} {cell} files (448 expected); ckpt {stem}_best.pt sha {sha('ckpt/' + stem + '_best.pt')} (expected {bsha})")
for r, c, k in (("raw_K2NR16B16e4", "C6", 192), ("raw_B16e4k", "C2", 448), ("raw_B1e4", "C2", 448)):
    print(f"  {r}: {len(glob.glob(f'{r}/D2_{c}_*.npz'))} {c} files ({k} expected){' -> ' + os.path.realpath(r) if os.path.islink(r) else ''}")
print(f"  results/review_next/K2NR16B16e4_accept.txt: {open('results/review_next/K2NR16B16e4_accept.txt').readline().strip()}")
ll = show("results/gmm_fits_D2_B32e4", 8, 320000, pr=False)
print(f"  K2B32e4 set (B32e4 grid without kron 4096): b* = {bstar({k: v for k, v in ll.items() if k != ('kron', 4096)})}")
PY
  exit $?
fi

# ================================================================ links (creates symlinks only)
lnk () {  # target linkpath (target relative to the link's directory, or absolute): create unless it already resolves there; never replace
  local want; want=$(cd "$(dirname "$2")" && readlink -f "$1")
  [ -e "$want" ] || die "link target $1 (from $(dirname "$2")) does not exist"
  if [ -e "$2" ] || [ -L "$2" ]; then [ "$(readlink -f "$2")" = "$want" ] || die "$2 exists and does not resolve to $1"
  else ln -s "$1" "$2" && log "link $2 -> $1"; fi; }
lset () {  # set-dir source-dir exclude-regex(or '') [extra-file]: per-file symlinks to EVERY fit file of source-dir (merged + .k0r* candidates;
           # eval_accept --grid looks for the kron K >= 1024 candidates in --fits-dir) except those matching the regex (K_max merged file AND its candidates)
  local D=results/gmm_fits_D2_$1 S=gmm_fits_D2_$2 f; shopt -s nullglob
  [ -n "$(echo results/$S/fit_*.npz)" ] || die "lset $1: no fit files in results/$S"; mkdir -p $D
  for f in results/$S/fit_*.npz; do
    [ -n "$3" ] && [[ $(basename $f) =~ $3 ]] && continue
    lnk ../$S/$(basename $f) $D/$(basename $f)
  done
  [ -z "$4" ] || lnk ../$4 $D/$(basename $4); }
if [ $MODE = links ]; then
  [ -f $S5 ] || die "$S5 (draft) missing: write it from 'prep' first"
  lnk gmm_fits_D2_B32e4 results/gmm_fits_D2_BRB32e4
  lnk gmm_fits_D2_NR16B16e4 results/gmm_fits_D2_BRNR16B16e4
  lset K2B32e4 B32e4 'kronK4096_'
  lnk /home/HTJ/t2_wtS/conf/raw_K2NR16B16e4 raw_K2NR16B16e4
  while read T C NR N STEM; do
    read CELL NN ST BSHA LSHA BS KK LL FK KR K2K REST <<< "$(s5 $T)"
    [ -z "$CELL" ] || [ "$CELL" = - ] && { log "links: PT $T absent or '-' -> no links"; continue; }
    for x in ${T}last ${T}chk; do lnk gmm_fits_D2_$T results/gmm_fits_D2_$x; done
    [ "$K2K" = - ] || lset K2$T $T "kronK${KK}_"
  done <<< "$NEW"
  read _ _ K8RUN <<< "$(awk '$1=="K8"{$1=""; print}' $S5)"
  [ "$K8RUN" = 1 ] && lset B64e4k8 B64e4 '' gmm_fits_D2_K8B64e4/fit_S2_Nr8_kronK8192_n640000.npz
  log "NSCALE_LINKS_DONE"; exit 0
fi

# ================================================================ eval: preconditions (a failed one is an ORDER / RESOURCE problem)
exec 9> logs/run_nscale.lock; flock -n 9 || die "another run_nscale.sh holds logs/run_nscale.lock"
[ -z "$(git status --porcelain code ../Demo)" ] || die "conf/code or Demo dirty"
for f in $REG DECISIONS.md $S5; do [ -n "$(git ls-files $f)" ] && [ -z "$(git status --porcelain $f)" ] || die "$f not tracked+clean"; done
[ "$(git log -1 --format=%H -- $S5)" = "$(git rev-parse HEAD)" ] || die "HEAD is not the §5 commit (no main commits after §5 until NSCALE_DONE)"
M5=logs/nscale/nscale_s5.start; S5ID="$(sha256sum $S5 | cut -d' ' -f1) $(git rev-parse HEAD)"   # single-shot S5 (§1 실행 위치·커밋)
if [ -s $M5 ]; then [ "$(cat $M5)" = "$S5ID" ] || die "S5 is single-shot: the first eval started on '$(cat $M5)' ($M5), now '$S5ID' (--resume only on the same S5 + HEAD; a new §5 needs user approval + DECISIONS)"
else ! grep -q '\] start eval' $L 2>/dev/null || die "an earlier eval started ($L) but the single-shot marker $M5 is missing"; fi
FREEZE=$(awk '$1=="FREEZE"{print $2}' $S5); FB=$(awk '$1=="FALLBACK"{print $2}' $S5)
git merge-base --is-ancestor "$FREEZE" HEAD 2>/dev/null && git diff --quiet "$FREEZE" HEAD -- code ../Demo \
  || die "FREEZE '$FREEZE' is not an ancestor of HEAD or conf/code / Demo differ from it"
[[ $FB =~ ^[01]$ ]] || die "$S5: FALLBACK 0|1 missing"
[ "$(s5 B128e4 | xargs)" = - ] && FBX=1 || FBX=0
[ $FB = $FBX ] || die "$S5: FALLBACK $FB but PT B128e4 is $([ $FBX = 1 ] && echo "'-'" || echo filled) (F1: FALLBACK 1 <=> PT B128e4 -)"
pgrep -f 'code/runner.py run' > /dev/null && die "another runner.py run is active (one registered CPU run at a time; SEEDSNR16e4 first)"
while read T C N ST SHA KK LL K2LL CKK; do
  [ "$(ls raw_$T/D2_${C}_*.npz 2>/dev/null | wc -l)" -eq 448 ] || die "raw_$T: not 448 $C chunk files"
  [ "$(sha256sum $CK/${ST}_best.pt | cut -c1-16)" = "$SHA" ] || die "$CK/${ST}_best.pt sha256 differs from $SHA"
  [ "$(readlink -f results/gmm_fits_D2_BR$T)" = "$(readlink -f results/gmm_fits_D2_$T)" ] || die "bridge fits link gmm_fits_D2_BR$T missing (links)"
done <<< "$BASE"
k2set () { [ -n "$(ls results/gmm_fits_D2_$1 2>/dev/null)" ] && ! ls results/gmm_fits_D2_$1 | grep -q 'kronK4096_' \
  || die "K2 link set gmm_fits_D2_$1 missing / empty / holds kronK4096_* files (links; acceptance (g))"; }
k2set K2B32e4
[ "$(ls raw_K2NR16B16e4/D2_C6_*.npz 2>/dev/null | wc -l)" -eq 192 ] || die "raw_K2NR16B16e4 (SCALE16e4) link missing or not 192 files (links)"
for r in raw_B16e4k raw_B1e4; do [ "$(ls $r/D2_C2_*.npz 2>/dev/null | wc -l)" -eq 448 ] || die "$r: not 448 C2 files"; done
while read T C NR N STEM; do
  set -- $(s5 $T)
  [ "$1" = - ] && { log "$T: PT '-' = point failed (§1 대체 규칙) -> skipped, its lines (T-iv) / 판정하지 못함"; continue; }
  [ $# -eq 14 ] || die "$S5: PT $T needs 14 fields (has $#)"
  [ "$1" = $C ] && [ "$2" = $N ] && [[ $3 =~ ^$STEM(_fb[23])?$ ]] || die "$S5: PT $T cell / ntrain / stem '$1 $2 $3' do not match $C $N $STEM[_fb2|_fb3]"
  [ "$(sha256sum $CK/${3}_best.pt 2>/dev/null | cut -c1-16)" = "$4" ] || die "$T: $CK/${3}_best.pt sha256 differs from §5 ($4)"
  [ "$(sha256sum $CK/$3.pt 2>/dev/null | cut -c1-16)" = "$5" ] || die "$T: last-EMA $CK/$3.pt sha256 differs from §5 ($5)"
  TL=$(awk '/^# =====/{s++; r[s]=0} /^# resume/{r[s]=1} /^# done/{if (!r[s]) l=$0} END {print l}' logs/train_$3.log 2>/dev/null)   # last '# done' of a training segment (§5 체크포인트 행 구간 규칙; '# resume' segments = GB' re-runs)
  [[ $TL == *"aborted=False"* && $TL != *"stopped_by=diverged"* ]] || die "$T: logs/train_$3.log final training '# done' = '${TL:-missing}' (a diverged / interrupted / unfinished attempt is never evaluated; §1 학습 실패)"
  [ "$9" = $GF ] && [ "${10}" = $GK ] || die "$T: grid '$9' / '${10}' is not the registered full:$GF kron:$GK"
  case "$C:${14}" in C2:PASS|C2:FAIL|C6:UNGATED) ;; *) die "$T: gate '${14}' (C2: PASS|FAIL, C6: UNGATED)";; esac
  if [ "${11}" = - ]; then [ "${12}${13}" = -- ] || die "$T: K2_ll / c_K must be '-' without K2"
  else [ "$6" = kron ] && [ "$7" = 4096 ] && [ "${11}" = 2048 ] && awk -v c="${13}" 'BEGIN {exit !(c == "inf" || c + 0 >= 1)}' \
         || die "$T: K2 '${11} ${12} ${13}' needs b* = kron 4096, K2_K 2048, c_K >= 1 or inf"
       k2set K2$T; fi
  [ -d results/gmm_fits_D2_$T ] || die "fits dir gmm_fits_D2_$T missing"
  for x in ${T}last ${T}chk; do [ "$(readlink -f results/gmm_fits_D2_$x)" = "$(readlink -f results/gmm_fits_D2_$T)" ] || die "fits link gmm_fits_D2_$x missing (links)"; done
done <<< "$NEW"
read K8K K8LL K8RUN <<< "$(awk '$1=="K8"{$1=""; print}' $S5)"
[[ $K8RUN =~ ^[01]$ ]] || die "$S5: K8 line missing (K8 <kron_K> <ll_val> <1|0>)"
[ "$K8RUN" = 1 ] && { [ "$K8K" = 8192 ] && [ -e results/gmm_fits_D2_B64e4k8/fit_S2_Nr8_kronK8192_n640000.npz ] && pt B64e4 \
  || die "K8 run 1 needs kron 8192, gmm_fits_D2_B64e4k8/fit_S2_Nr8_kronK8192_n640000.npz and a B64e4 point (F5: PT B64e4 - -> K8 run 0)"; }
NEWRAW="BRB32e4 BRNR16B16e4 B64e4 B128e4 B64e4chk B128e4chk B64e4last B128e4last K2B32e4 K2B64e4 K2B128e4 NR16B64e4 NR16B64e4chk NR16B64e4last K2NR16B64e4 B64e4k8"
X=$(for t in $NEWRAW; do [ -e raw_$t ] && echo raw_$t; done | tr '\n' ' ')
[ $RESUME -eq 1 ] || [ -z "$X" ] || die "NSCALE raw(s) exist: $X(resume: --resume)"
H=$(git rev-parse --short HEAD); OK=0; FAIL=0; declare -A ACC
[ -s $M5 ] || { echo "$S5ID" > $M5 || die "cannot write the single-shot marker $M5"; log "single-shot marker $M5 written (first eval start)"; }
log "start eval (git $H, freeze $FREEZE, fallback $FB, K8 run ${K8RUN:-0}, resume $RESUME, S5+HEAD $S5ID)"
st () { local rc=$1; shift; log "$* rc=$rc"; [ $rc -eq 0 ] && OK=$((OK+1)) || FAIL=$((FAIL+1)); return $rc; }

# ---------------------------------------------------------------- helpers
nraw () { ls raw_$1/D2_*.npz 2>/dev/null | wc -l; }
run () {  # tag expected-chunk-files runner-args...; a complete raw is skipped (resume); HEAD must stay the §5 commit
  local T=$1 N=$2 rc; shift 2
  [ "$(git rev-parse --short HEAD)" = "$H" ] || { log "ABORT: HEAD moved from $H during the run"; exit 1; }
  [ "$(nraw $T)" -eq "$N" ] && { log "run $T skip: raw complete ($N files)"; return 0; }
  echo "# run_nscale git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z') resume=$RESUME: runner.py run --testbed D2 $* --tag $T" >> logs/run_D2_$T.log
  $P code/runner.py run --testbed D2 "$@" --tag $T >> logs/run_D2_$T.log 2>&1 < /dev/null; rc=$?
  [ $rc -eq 0 ] && [ "$(nraw $T)" -ne "$N" ] && rc=99
  st $rc "run $T ($(nraw $T)/$N files)"; }
gitchk () {  # acceptance (f): every chunk of each raw carries run|git == the §5 commit (no +dirty)
  $P - "$H" "$@" <<'PY'
import glob, sys, numpy as np
h, bad = sys.argv[1], []
for r in sys.argv[2:]:
    g = set()
    for f in glob.glob(r + "/D2_*.npz"):
        with np.load(f) as z:
            g.add(str(z["run|git"]) if "run|git" in z.files else None)
    print(f"  (f) {r}: run|git {sorted(map(str, g))}")
    bad += [r] if g != {h} else []
print("ACCEPT (f): " + ("OK" if not bad else "FAILED " + " ".join(bad)))
raise SystemExit(int(bool(bad)))
PY
}
acc () {  # key ntrain eval_accept-args... -> ACC[key]; output $RV/<key>_accept.txt; every --tag raw also gets acceptance (f)
  local K=$1 N=$2 O=$RV/$1_accept.txt a p= rs=; shift 2
  $P code/eval_accept.py --ntrain $N "$@" > $O 2>&1 < /dev/null; ACC[$K]=$?
  for a; do [ "$p" = --tag ] && rs="$rs raw_${a%%:*}"; p=$a; done
  gitchk $rs >> $O 2>&1 || ACC[$K]=1
  st ${ACC[$K]} "accept $K ($(grep -h '^ACCEPT' $O | tr '\n' ' ' | cut -c1-110))"; }
ok () { local k; for k; do [ "${ACC[$k]:-1}" = 0 ] || return 1; done; }
same () {  # REPORT-ONLY integrity line (not a gate): arm $1 of raw $3 == arm $1 of raw $2 at every shared chunk file, every KEYS_RAW key
  $P - "$@" <<'PY'
import glob, os, sys
sys.path.insert(0, "code")
import common as C, numpy as np
arm, a, l = sys.argv[1:]; bad = n = 0
for f in sorted(glob.glob(l + "/D2_*.npz")):
    with np.load(f) as y, np.load(os.path.join(a, os.path.basename(f))) as z:
        for k in (f"{arm}|{q}" for q in C.KEYS_RAW):
            if k in y.files or k in z.files:
                n += 1
                bad += k not in y.files or k not in z.files or not np.array_equal(np.nan_to_num(y[k], nan=1e300), np.nan_to_num(z[k], nan=1e300))
print(f"{arm} {l} == {a} (report-only integrity, not a gate): {bad} of {n} (chunk, key) pairs differ -> {'OK' if n and not bad else 'FAIL'}")
raise SystemExit(int(bad > 0 or n == 0))
PY
}
p1 () {  # P1 record of tag $1 (cell $2): the two table-B blocks verbatim + an auto helper label (§2.1 governs) -> $RV/nscale_P1_<T>.txt
  $P - "$1" "$2" > $RV/nscale_P1_$1.txt 2>&1 <<'PY'
import re, sys
T, cell = sys.argv[1:]
t = open(f"results/tables_D2_{T}.txt").read().split("\n")
print(f"# NSCALE P1 {T} ({cell}): table-B blocks from results/tables_D2_{T}.txt; the label line is an auto helper, NEXT_EXPERIMENTS_NSCALE §2.1 governs")
rc = 1
for pair in ("M-ours-bstar -> M-ours-dscore-C-V1", "M-ours-bstar -> M-ours-bstar-scalar"):
    idx = [i for i, l in enumerate(t) if l.startswith("  " + pair + " ")]
    if len(idx) != 1:
        print(f"{pair}: {len(idx)} blocks (exactly 1 expected) -> no label"); continue
    blk = t[idx[0]:idx[0] + 6]; print("\n".join(blk))
    if pair.endswith("V1"):
        pw = any(l.strip().startswith("power guard") and l.rstrip().endswith("-> POWERED") for l in blk)
        m = next((re.search(r"second arm fewer failures at (\d)/3 points, first arm fewer failures at (\d)/3 points", l) for l in blk
                  if "second arm fewer" in l), None)
        k, j = (int(m[1]), int(m[2])) if m else (0, 0)
        if cell == "C2":
            lab = "통과 (POWERED, second arm fewer >= 2/3)" if pw and k >= 2 else "통과 못함"
        else:
            lab = "(i)" if pw and k >= 2 else "(ii)" if pw and j >= 2 else "(iii)" if pw else "(iv) 검정력 미달"
        print(f"AUTO-LABEL {T}: {lab}  (POWERED={pw}, second {k}/3, first {j}/3)"); rc = 0
raise SystemExit(rc)
PY
  st $? "P1 $1 ($(grep -h '^AUTO-LABEL' $RV/nscale_P1_$1.txt | cut -c1-90))"; }
fci () {  # output-name accepted-keys(comma) frontier_ci-args... (a line runs only if all its inputs passed acceptance)
  local F=$1 O=$RV/$1.txt N=$2; shift 2
  ok ${N//,/ } || { st 1 "frontier $F SKIPPED: acceptance not passed for one of $N"; return 1; }
  echo "# run_nscale git $H $(TZ=America/Chicago date '+%Y-%m-%d %H:%M %Z'): frontier_ci.py $*" > $O
  [ -z "$NOTE" ] || echo "$NOTE" >> $O
  $P code/frontier_ci.py "$@" >> $O 2>&1 < /dev/null; st $? "frontier $F ($*)"; }

# ---------------------------------------------------------------- (1) bridges: the base raws reproduced by the frozen code
run BRB32e4 1 --prior S2 --cell C2 --ntrain 320000 --stagec-ckpt $CK/d2sx_N320000_a1_best.pt $ONE --snr -3
run BRNR16B16e4 1 --prior S2 --cell C6 --ntrain 160000 --stagec-ckpt $CK/d2sx_NR16_N160000_a1_fb2_best.pt $ONE --snr -3
# ---------------------------------------------------------------- (2)-(5) D2 C2: A -> analysis, chk, last, K2 (base K2B32e4 first)
C2PTS=""; for T in B64e4 B128e4; do pt $T && C2PTS="$C2PTS $T"; done
for T in $C2PTS; do
  read CELL N ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK GATE <<< "$(s5 $T)"
  run $T 448 --prior S2 --cell C2 --ntrain $N --stagec-ckpt $CK/${ST}_best.pt $FULL \
    && { $P code/runner.py analysis --testbed D2 --tag $T > logs/analysis_$T.log 2>&1; st $? "analysis $T"; }
done
for T in $C2PTS; do read CELL N ST REST <<< "$(s5 $T)"; run ${T}chk 1 --prior S2 --cell C2 --ntrain $N --stagec-ckpt $CK/${ST}_best.pt $ONE --snr -3; done
for T in $C2PTS; do read CELL N ST REST <<< "$(s5 $T)"
  run ${T}last 448 --prior S2 --cell C2 --ntrain $N --stagec-ckpt $CK/$ST.pt $FULL \
    && { $P code/runner.py analysis --testbed D2 --tag ${T}last > logs/analysis_${T}last.log 2>&1; st $? "analysis ${T}last"; }
done
run K2B32e4 192 --prior S2 --cell C2 --ntrain 320000 --stagec-ckpt $CK/d2sx_N320000_a1_best.pt $FULL --snr $D3 --arm $ARMK2
for T in $C2PTS; do read CELL N ST BSHA LSHA BS KK LL FK KR K2K REST <<< "$(s5 $T)"
  [ "$K2K" = - ] || run K2$T 192 --prior S2 --cell C2 --ntrain $N --stagec-ckpt $CK/${ST}_best.pt $FULL --snr $D3 --arm $ARMK2; done
# ---------------------------------------------------------------- (6) D2 C6: A -> analysis -> chk -> last -> K2
if pt NR16B64e4; then
  read CELL N ST BSHA LSHA BS KK LL FK KR K2K REST <<< "$(s5 NR16B64e4)"; B6="--prior S2 --cell C6 --ntrain $N"
  run NR16B64e4 448 $B6 --stagec-ckpt $CK/${ST}_best.pt $FULL --arm $ARM11 \
    && { $P code/runner.py analysis --testbed D2 --tag NR16B64e4 > logs/analysis_NR16B64e4.log 2>&1; st $? "analysis NR16B64e4"; }
  run NR16B64e4chk 1 $B6 --stagec-ckpt $CK/${ST}_best.pt $ONE --snr -3 --arm $ARM11
  run NR16B64e4last 192 $B6 --stagec-ckpt $CK/$ST.pt $FULL --snr $D3 --arm $ARM3
  [ "$K2K" = - ] || run K2NR16B64e4 192 $B6 --stagec-ckpt $CK/${ST}_best.pt $FULL --snr $D3 --arm $ARMK2
fi
# ---------------------------------------------------------------- (7) report-only kron 8192
[ "$K8RUN" = 1 ] && { read CELL N ST REST <<< "$(s5 B64e4)"
  run B64e4k8 192 --prior S2 --cell C2 --ntrain 640000 --stagec-ckpt $CK/${ST}_best.pt $FULL --snr $D3 --arm $ARM3; }

# ---------------------------------------------------------------- (8) manifests, guards, recovery, acceptance
for t in $NEWRAW; do [ -d raw_$t ] && { $P code/run_manifest.py --tag $t >> $L 2>&1; st $? "run_manifest $t"; }; done
acc BRB32e4 320000 --bstar kron --kron-K 4096 --ll-val -5.942083265612076 --n 40 --points C2:-3 --ref-raw raw_B32e4 --ref-arms all \
  --tag BRB32e4:best:035744cbe955984d:C2
acc BRNR16B16e4 160000 --bstar kron --kron-K 4096 --ll-val 63.1751571838059 --n 40 --points C6:-3 --ref-raw raw_NR16B16e4 --ref-arms all \
  --tag BRNR16B16e4:best:c050d611b2c714a6:C6
acc K2B32e4 320000 --nr 8 --bstar kron --kron-K 2048 --ll-val -7.792724507139091 --points C2:-3,0,3 --fits-dir results/gmm_fits_D2_K2B32e4 \
  --cand-dir results/gmm_fits_D2_B32e4 --grid "full:$GF kron:${GK%,*}" --ref-raw raw_B32e4 --tag K2B32e4:best:035744cbe955984d:C2
grep -q '^ACCEPT: OK' $RV/K2NR16B16e4_accept.txt; ACC[K2NR16B16e4]=$?      # SCALE16e4 acceptance of the linked base K/2 raw (recorded)
for T in $C2PTS NR16B64e4; do pt $T || continue
  read CELL N ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK GATE <<< "$(s5 $T)"; NR=8; BASE_T=B32e4; [ $CELL = C6 ] && { NR=16; BASE_T=NR16B16e4; }
  KARG="--bstar $BS"; [ "$KK" = - ] || KARG="$KARG --kron-K $KK"
  $P code/guard_report.py --raw raw_$T --testbed D2 > results/guard_D2_$T.txt 2>&1; st $? "guard_report $T"
  { $P code/recovery_ci.py --raw raw_$T --cell $CELL --snrs -3; $P code/recovery_ci.py --raw raw_$T --cell $CELL --snrs $D3; } \
    > $RV/recovery_$T.txt 2>&1; st $? "recovery_ci $T (-3 dB; -3/0/+3)"
  $P code/recovery_ci.py --raw raw_${T}last --cell $CELL --snrs $D3 > $RV/recovery_${T}last.txt 2>&1; st $? "recovery_ci ${T}last (report-only)"
  same M-ours-bstar raw_$T raw_${T}last >> $RV/recovery_${T}last.txt 2>&1; st $? "b* ${T}last == $T (report-only integrity line)"
  acc $T $N --prior S2 --nr $NR $KARG --ll-val $LL --fits-dir results/gmm_fits_D2_$T --grid "full:$FK kron:$KR" --ref-raw raw_$BASE_T \
    --tag $T:best:$BSHA:$CELL                                                  # A: grid (a), meta (b), genie replay vs the base raw (d)
  acc ${T}chk $N --prior S2 $KARG --ll-val $LL --n 40 --points $CELL:-3 --ref-raw raw_$T --ref-arms all --tag ${T}chk:best:$BSHA:$CELL
  LP=""; [ $CELL = C6 ] && LP="--points C6:-3,0,3"
  acc ${T}last $N --prior S2 $KARG --ll-val $LL $LP --ref-raw raw_$T --tag ${T}last:last:$LSHA:$CELL
  [ "$K2K" = - ] || acc K2$T $N --prior S2 --nr $NR --bstar kron --kron-K $K2K --ll-val $K2LL --points $CELL:-3,0,3 \
    --fits-dir results/gmm_fits_D2_K2$T --cand-dir results/gmm_fits_D2_$T --grid "full:$FK kron:${KR%,*}" --ref-raw raw_$T --tag K2$T:best:$BSHA:$CELL
  if ok $T; then p1 $T $CELL; else st 1 "P1 $T SKIPPED: acceptance of $T failed (label: 수용 실패)"; fi
done
if [ "$K8RUN" = 1 ]; then read CELL N ST BSHA REST <<< "$(s5 B64e4)"
  acc B64e4k8 640000 --bstar kron --kron-K 8192 --ll-val $K8LL --points C2:-3,0,3 --ref-raw raw_B64e4 --tag B64e4k8:best:$BSHA:C2
  same M-ours-dscore-C-V1 raw_B64e4 raw_B64e4k8 > $RV/nscale_K8_V1.txt 2>&1; st $? "V1 B64e4k8 == B64e4 (report-only integrity line)"
fi

# ---------------------------------------------------------------- (9) P2 paired trend (Holm m = 2), Q-K / Q-OP, secondaries, report-only
N2=B128e4; [ $FB = 1 ] && N2=B64e4                                            # F1: D2 primary contrast R(6.4e5) - R(3.2e5)
NOTE=""
fci nscale_P2_C2 $N2,${N2}chk,BRB32e4 --paired "raw_$N2:C2:-3,0,3" "raw_B32e4:C2:-3,0,3"; RS2=$?
fci nscale_P2_C6 NR16B64e4,NR16B64e4chk,BRNR16B16e4 --paired "raw_NR16B64e4:C6:-3,0,3" "raw_NR16B16e4:C6:-3,0,3"; RS6=$?
why () {  # tag A-key chk-key bridge-key fci-rc output -> (T-iv) reason ('' = none): failed point / acceptance / --paired genie assert / other rc
  pt $1 || { echo "학습 실패 / 적합 실패 (§5)"; return; }
  ok $2 $3 $4 || { echo "수용 실패"; return; }
  grep -q 'genie differs' $6 2>/dev/null && { echo "수용 실패 (--paired genie assert)"; return; }
  [ "$5" = 0 ] || echo "정의 불가 (frontier_ci rc $5)"; }
$P - "$RV/nscale_P2_C2.txt" "$(why $N2 $N2 ${N2}chk BRB32e4 $RS2 $RV/nscale_P2_C2.txt)" \
  "$RV/nscale_P2_C6.txt" "$(why NR16B64e4 NR16B64e4 NR16B64e4chk BRNR16B16e4 $RS6 $RV/nscale_P2_C6.txt)" > $RV/nscale_P2_holm.txt 2>&1 <<'PY'
import math, re, sys
def parse(path, why):
    if why: return dict(p=1.0, why=why)
    t = open(path).read()
    R = re.findall(r"R\d: .*?b\* (\d+) V1 (\d+) genie (\d+)  R = (\S+)", t)
    m = re.search(r"dR = R1 - R2 = (\S+)  \[90% paired (\S+), (\S+)\]  \[95% paired (\S+), (\S+)\]  bootstrap two-sided p = (\S+)"
                  r"  undefined replicates (\d+)", t)
    if len(R) != 2 or not m: return dict(p=1.0, why="정의 불가 (출력 형식)")
    d = dict(dR=float(m[1]), ci={95: (float(m[4]), float(m[5])), 90: (float(m[2]), float(m[3]))}, p=float(m[6]), why="")
    for b, v, g, r in R:
        if int(b) <= int(g) or r == "nan": d["why"] = "정의 불가 (ΣF_b* ≤ ΣF_g)"
        elif int(g) >= int(v): d["why"] = d["why"] or "범위 밖 (ΣF_g ≥ ΣF_V1, genie 가드)"
    if int(m[7]) > 100: d["why"] = d["why"] or "정의 불가 (정의 불가 복제 > 5 %)"
    if d["why"] or not math.isfinite(d["p"]): d.update(p=1.0, why=d["why"] or "정의 불가 (p)")
    return d
c = {"C2": parse(sys.argv[1], sys.argv[2]), "C6": parse(sys.argv[3], sys.argv[4])}
order = sorted(c, key=lambda k: (bool(c[k]["why"]), c[k]["p"], k != "C2"))   # (T-iv) last; smaller p first; tie -> C2 first
print("# NSCALE P2 Holm m = 2 (auto helper; NEXT_EXPERIMENTS_NSCALE §1 다중성 / §2.2 govern): first 95 % CI, second 90 % CI")
lab = lambda lo, hi: "(T+)" if lo > 0 else "(T−)" if hi < 0 else "(T0)"
first = None
for i, k in enumerate(order):
    d, lv = c[k], (95 if i == 0 else 90)
    if d["why"]: L = f"(T-iv) {d['why']}"
    elif i == 1 and first not in ("(T+)", "(T−)"): L = f"(T0-Holm)  [own 90% CI {d['ci'][90][0]:+.3f}, {d['ci'][90][1]:+.3f} = report-only]"
    else: L = lab(*d["ci"][lv])
    if i == 0: first = L.split()[0]
    print(f"{'first ' if i == 0 else 'second'} {k}: " + (f"dR {d['dR']:+.3f}  [{lv}% {d['ci'][lv][0]:+.3f}, {d['ci'][lv][1]:+.3f}]  p {d['p']:.4f}  "
          if not d["why"] else "p := 1  ") + f"-> AUTO-LABEL {L}")
PY
st $? "P2 Holm helper ($(grep -h AUTO-LABEL $RV/nscale_P2_holm.txt | sed 's/.*AUTO-LABEL //' | tr '\n' ';' | cut -c1-100))"
qk () {  # cell new-tag base-K2-raw base-K2-key base-c_K base-tag: Q-K runs (a) both ends + Q-OP, (b) new end only, (c) base end only
  local C=$1 T=$2 E1=- C1=- G X LV V FORCE; read CELL N ST BSHA LSHA BS KK LL FK KR K2K K2LL CKK GATE <<< "$(s5 $T)"
  G=$T,${T}chk,BR$6; [ "$K2K" = - ] || { E1=raw_K2$T; C1=$CKK; }
  if [ "$BS" = kron ] && [ "$KK" = 4096 ] && [ "$K2K" = - ]; then FORCE="K2 구성 불가 (b* = kron 4096, K/2 집합 b* != kron 2048)"   # §1 Q-K 강제 조건
  elif ! ok $4; then FORCE="기준 K/2 태그 수용 실패 ($4)"
  elif [ "$K2K" != - ] && ! ok K2$T; then FORCE="새 K/2 태그 수용 실패 (K2$T)"
  elif [ "$C1" = inf ]; then FORCE="r >= 1"; else FORCE=""; fi
  if [ -z "$FORCE" ]; then NOTE=""; X="--extrap $E1 $3 --ck $C1 $5"; G=$G,$4; [ "$K2K" = - ] || G=$G,K2$T
  else NOTE="# Q-K: [K 상한 민감: 외삽 불가] (forced, §2.2 Q-K (1): $FORCE -> run (a) without --extrap, no (b)(c))"; X=""; fi
  for LV in 0.95 0.90; do V=L${LV#0.}
    fci nscale_qk_${C}_$V $G --recovery "raw_$T:$C:-3,0,3" "raw_$6:$C:-3,0,3" $X --rstar 0.05 --level $LV
    [ -n "$NOTE" ] && continue
    fci nscale_qk_${C}_${V}_qkN $G --recovery "raw_$T:$C:-3,0,3" "raw_$6:$C:-3,0,3" --extrap $E1 - --ck $C1 - --level $LV
    fci nscale_qk_${C}_${V}_qkB $G --recovery "raw_$T:$C:-3,0,3" "raw_$6:$C:-3,0,3" --extrap - $3 --ck - $5 --level $LV
  done; NOTE=""; }
pt $N2 && [ $RS2 = 0 ] && qk C2 $N2 raw_K2B32e4 K2B32e4 2.021371931572057 B32e4
pt NR16B64e4 && [ $RS6 = 0 ] && qk C6 NR16B64e4 raw_K2NR16B16e4 K2NR16B16e4 1 NR16B16e4
if [ $FB = 0 ]; then                                                          # 2차 D2 steps (90 %, uncorrected); under F1 S1 is the primary
  fci nscale_S1_C2 B64e4,B64e4chk,BRB32e4 --paired "raw_B64e4:C2:-3,0,3" "raw_B32e4:C2:-3,0,3"
  fci nscale_S2_C2 B128e4,B128e4chk,B64e4,B64e4chk --paired "raw_B128e4:C2:-3,0,3" "raw_B64e4:C2:-3,0,3"
fi
fci nscale_eff_C2 $N2,${N2}chk --pair "A=raw_$N2:C2:M-ours-bstar" "B=raw_B16e4k:C2:M-ours-dscore-C-V1"        # 2차 data efficiency
fci nscale_eff128_C2 $N2,${N2}chk --pair "A=raw_$N2:C2:M-ours-bstar" "B=raw_B1e4:C2:M-ours-dscore-C-V1"     # report-only
[ "$K8RUN" = 1 ] && fci nscale_K8 B64e4k8,B64e4 --paired "raw_B64e4k8:C2:-3,0,3" "raw_B64e4:C2:-3,0,3"      # report-only
log "NSCALE_DONE ok=$OK fail=$FAIL"
exit $((FAIL > 0))
