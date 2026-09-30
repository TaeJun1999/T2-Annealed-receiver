#!/bin/bash
# OBSOLETE (2026-09-29 CDT): written for the ROT16e4 / S2v / S2d runs, all finished and recorded. It does NOT handle SUPP16e4 or
# later runs -- after a reboot, resume each job with its own script (e.g. run_supp16e4.sh eval <remaining conds>). Kept as a record.
# review_next: resume every interrupted job after a server reboot (written 2026-09-27 CDT).  Idempotent: a job whose tmux
# session is alive or whose end marker is logged is left alone, so running it twice (or with nothing to do) is harmless.
# Lives OUTSIDE conf/code on purpose: runner.py writes `git status --porcelain code ../Demo` (+dirty) into every raw chunk and
# pair_rot requires one clean commit, so no file may appear in main conf/code while ROT16e4 runs.
#   bash ~/t2/resume_after_reboot.sh          (log: ~/t2/conf/logs/resume_after_reboot.log)
# What it does:
#   0. deletes truncated .npz (a kill mid np.savez): ROT raw chunks, S2v / S2d GMM fit dirs
#   1. ROT16e4 (main):   re-runs code/run_rot16e4.sh for the datasets without both pair_rot lines (runner skips finished chunks)
#   2. S2v queue (~/t2_wtC): jobs logged "start" without "done" go back to the FRONT of the queue file, then run_s2v.sh
#   3. B' S2d queue (~/t2_wtB): same, then run_s2d.sh (it waits until the S2v queue file is empty)
# A dataset / job with an INVALID or ABORT line is NOT re-run (re-runs of failed registered tags need the user).
P=~/miniforge3/envs/torch/bin/python
LOG=~/t2/conf/logs/resume_after_reboot.log
log () { echo "[resume $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] $*" | tee -a $LOG; }
alive () { tmux has-session -t "$1" 2>/dev/null; }

# ---- 0. truncated npz
$P - ~/t2/conf/raw_ROT* ~/t2_wtC/conf/results/gmm_fits_D2_S2vB16e4 ~/t2_wtB/conf/results/gmm_fits_D2_S2dB16e4 <<'EOF' | tee -a $LOG
import sys, glob, os, zipfile
n = 0
for d in sys.argv[1:]:
    for f in glob.glob(os.path.join(d, "*.npz")):
        n += 1
        try:
            with zipfile.ZipFile(f) as z:
                bad = z.testzip()
        except Exception as e:
            bad = repr(e)
        if bad:
            print(f"[resume] REMOVE truncated {f} ({bad})"); os.remove(f)
print(f"[resume] npz checked: {n}")
EOF

# ---- 1. ROT16e4
R=~/t2/conf/logs/run_rot16e4.log
if alive rot; then log "ROT: tmux 'rot' alive -> left alone"
elif grep -q ROT_EVAL_DONE $R 2>/dev/null && ! grep -q "resume re-run" $R; then log "ROT: ROT_EVAL_DONE logged -> nothing to do"
else
  todo=""
  for d in D2C2 D2C6 D3 SV8e UMi28 MIX3; do
    grep -qE "\] $d .*(INVALID|ABORT)" $R && { log "ROT: $d has INVALID/ABORT -> NOT re-run (user decision)"; continue; }
    [ "$(grep -cE "\] $d deg=[0-9]+ pair_rot rc=0" $R)" -ge 2 ] || todo="$todo $d"
  done
  if [ -z "$todo" ]; then log "ROT: every dataset has both pair_rot lines -> nothing to do"
  else
    echo "[rot16e4 $(TZ=America/Chicago date '+%m-%d %H:%M %Z')] resume re-run after reboot:$todo" >> $R
    tmux new -d -s rot "cd ~/t2/conf && bash code/run_rot16e4.sh$todo"; log "ROT: restarted tmux 'rot' for:$todo"
  fi
fi

# ---- 2./3. GPU queues: put in-flight jobs back at the front, restart the queue script
requeue () {   # $1 tmux  $2 conf dir  $3 log  $4 queue file  $5 end marker  $6 script
  if alive $1; then log "$1: tmux alive -> left alone"; return; fi
  if grep -q "$5" $2/$3 2>/dev/null; then log "$1: $5 logged -> nothing to do"; return; fi
  $P - $2/$3 $2/$4 <<'EOF' | tee -a $LOG
import sys, re
log, q = sys.argv[1:]
live = {}
for line in open(log):
    m = re.search(r"GPU (\d+) (start|done rc=.*): (@train|code/.*)$", line)
    if m:
        live[m.group(3).strip()] = m.group(2) == "start"
back = [j for j, s in live.items() if s]
rest = [l.rstrip("\n") for l in open(q) if l.strip()] if __import__("os").path.exists(q) else []
open(q, "w").write("".join(j + "\n" for j in back + [r for r in rest if r not in back]))
print(f"[resume] {q}: re-queued in-flight {back or 'none'}; queue now {len(back) + len(rest)} jobs")
EOF
  declare -F pre_$1 >/dev/null && pre_$1              # per-queue fix-up between re-queue and restart
  tmux new -d -s $1 "cd $2 && bash $6"; log "$1: restarted tmux '$1' ($6)"
}
pre_s2v () {
  # S2v kron K=512 (DECISIONS 2026-09-27 CDT): the slow non-batched fit_gpu.py job is replaced by batched restarts 0-2 (tmux s2v512).
  # If the re-queue put the slow job back, swap it for the batched restarts whose candidate file is missing (merge by hand after).
  local F=~/t2_wtC/conf/results/gmm_fits_D2_S2vB16e4/fit_S2v_Nr16_kronK512_n160000 Q=~/t2_wtC/conf/logs/s2v_queue.txt r add=""
  local SLOW="code/fit_gpu.py 16 kron 512 160000 S2vB16e4 --prior S2v"
  K512_HANDLED=1
  grep -qxF "$SLOW" $Q 2>/dev/null || return 0
  if [ ! -f $F.npz ]; then
    for r in 0 1 2; do [ -f $F.k0r$r.npz ] || add="$add"$'\n'"code/fit_gpu_batched.py 16 kron 512 160000 S2vB16e4 --restart $r --prior S2v"; done
  fi
  { [ -n "$add" ] && echo "${add#$'\n'}"; grep -vxF "$SLOW" $Q; } > $Q.new; mv $Q.new $Q
  log "s2v: slow kron 512 job replaced by batched restarts [${add//$'\n'/ | }]; merge by hand: code/fit_gpu.py 16 kron 512 160000 S2vB16e4 --merge --prior S2v"
}
requeue s2v ~/t2_wtC/conf logs/s2v.log logs/s2v_queue.txt S2V_QUEUE_DONE code/run_s2v.sh
# kron 512 batched restarts (tmux s2v512) lost to the reboot while the queue itself was not restarted above (e.g. S2V_QUEUE_DONE
# already logged): put the missing restarts at the queue front and (re)start the queue.  Merge by hand afterwards.
F512=~/t2_wtC/conf/results/gmm_fits_D2_S2vB16e4/fit_S2v_Nr16_kronK512_n160000; Q2=~/t2_wtC/conf/logs/s2v_queue.txt
if [ -z "$K512_HANDLED" ] && [ ! -f $F512.npz ] && ! alive s2v512; then
  miss=""; for r in 0 1 2; do [ -f $F512.k0r$r.npz ] || miss="$miss $r"; done
  if [ -n "$miss" ]; then
    { printf "code/fit_gpu_batched.py 16 kron 512 160000 S2vB16e4 --restart %s --prior S2v\n" $miss; cat $Q2 2>/dev/null; } > $Q2.new; mv $Q2.new $Q2
    log "s2v: kron 512 restarts missing:$miss -> queued (merge by hand: code/fit_gpu.py 16 kron 512 160000 S2vB16e4 --merge --prior S2v)"
    alive s2v || { tmux new -d -s s2v "cd ~/t2_wtC/conf && bash code/run_s2v.sh"; log "s2v: restarted tmux 's2v' for kron 512"; }
  fi
fi
sleep 5                                       # let the S2v workers claim their GPUs first
requeue s2d ~/t2_wtB/conf logs/s2d.log logs/s2d_queue.txt S2D_QUEUE_DONE code/run_s2d.sh
log "done. Claude side: re-create the 30-min briefing cron and the end-marker watches (memory review-next-status)."
