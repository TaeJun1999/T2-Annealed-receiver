"""Independent re-derivation for the SEEDS3_16e4 record audit (2026-09-30, Fable 5.1): NEXT_EXPERIMENTS_SEEDS3_16e4.md
§0 (a1 rows), §5 (checkpoints), §6.1 (six seed tags), the docs/EXPERIMENTS.md row and the DECISIONS line.

Reads ONLY raw npz files, checkpoints, logs, manifests and git.  Reuses the helpers of prereg_audit_2026-09-27/recompute.py
(decision points anchored on b*, exact sign test, POWERED / 2/3 rule, paired bootstrap gap seed 20260925, recovery bootstrap
seed 20260926, KEYS_RAW identity) -- it does NOT call analysis table code, pair scripts, recovery_ci.py or eval_accept.py.
Bootstraps use the registered seeds, so digit-level agreement is a reproduction, not an independent sample.

    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python \
        conf/results/review_next/prereg_audit_2026-09-30/recompute_seeds3.py > .../recompute_seeds3.out
"""
import datetime
import glob
import hashlib
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, "/home/HTJ/t2/conf/results/review_next/prereg_audit_2026-09-27")
import recompute as R  # noqa: E402  (helpers only; its main() is not run)

CONF, P = R.CONF, R.P
SETS = (("D3", "S2c", "D3B16e4"), ("SV8e", "SV8e", "SVB16e4"), ("MIX3", "MIX3", "MXB16e4"))
TAGS = [f"{t}s{s}" for _, _, t in SETS for s in (2, 3)]


def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def main():
    P("# recompute_seeds3.py -- SEEDS3_16e4 record audit 2026-09-30 (Fable 5.1); git HEAD", R.git("rev-parse", "--short", "HEAD"),
      "| now", f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} KST")

    P("\n## 0. git: freeze 73a93547 -> §5 fill dbe0bdb3 -> run commit 6b1de688 -> HEAD; working tree")
    for h in ("73a93547", "dbe0bdb3", "6b1de688"):
        P(f"  {h}: {R.git('show', '-s', '--format=%ci %s', h)[:120]}  (KST; CDT = KST - 14 h)")
    REC = "results/review_next/NEXT_EXPERIMENTS_SEEDS3_16e4.md"
    P("  record 73a93547..dbe0bdb3 numstat:", R.git("diff", "--numstat", "73a93547", "dbe0bdb3", "--", REC) or "(empty)")
    P("  record dbe0bdb3..HEAD:", R.git("diff", "--stat", "dbe0bdb3", "HEAD", "--", REC) or "(empty)")
    P("  record HEAD..worktree numstat:", R.git("diff", "--numstat", "HEAD", "--", REC) or "(empty)")
    P("  conf/code 73a93547..6b1de688 numstat:\n    " + (R.git("diff", "--numstat", "73a93547", "6b1de688", "--", "code").replace("\n", "\n    ") or "(empty)"))
    P("  conf/code 73a93547..6b1de688 -- score.py arms.py runner.py receiver*.py stagec*.py gmm*.py chan*.py analysis.py(table code?):",
      R.git("diff", "--stat", "73a93547", "6b1de688", "--", "code/score.py", "code/arms.py", "code/runner.py") or "(empty: Stage C / receiver / runner unchanged)")
    P("  conf/code 6b1de688..HEAD:", R.git("diff", "--stat", "6b1de688", "HEAD", "--", "code") or "(empty)")
    P("  conf/code worktree dirty:", R.git("status", "--porcelain", "code") or "(clean)")

    P("\n## 1. checkpoints (§5): sha256[:16], fields of _best.pt and last .pt, log header/done, mtime - wall")
    import torch
    for name, pr, tag in SETS:
        for s in (2, 3):
            rows = {}
            for role, f in (("best", f"d2sx_{pr}_N160000_a{s}_best.pt"), ("last", f"d2sx_{pr}_N160000_a{s}.pt")):
                p = os.path.join(CONF, "ckpt", f); z = torch.load(p, map_location="cpu", weights_only=False); rows[role] = z
                P(f"  {f}: sha {R.sha16(p)} epoch={z.get('epoch')} best_epoch={z.get('best_epoch')} best_val={z.get('best_val')!r} "
                  f"stopped_by={z.get('stopped_by')} role={z.get('role')} prior={z.get('prior')} sigma_tag={z.get('sigma_tag')} rung={z.get('rung')} "
                  f"attempt={z.get('attempt')} split_hash={z.get('split_hash')} wall_sec={z.get('wall_sec')} mtime {datetime.datetime.fromtimestamp(os.path.getmtime(p)):%m-%d %H:%M:%S} KST")
            P(f"    check best.epoch == last.best_epoch: {rows['best']['epoch']} == {rows['last']['best_epoch']} -> {rows['best']['epoch'] == rows['last']['best_epoch']}; "
              f"best.best_val == last.best_val: {rows['best']['best_val'] == rows['last']['best_val']}")
            lines = open(os.path.join(CONF, f"logs/train_d2sx_{pr}_N160000_a{s}.log")).read().splitlines()
            heads = [(i + 1, l[8:28]) for i, l in enumerate(lines) if l.startswith("# =====")]
            done = [l for l in lines if l.startswith("# done")][-1]
            wall = float(done.split("wall ")[1].split(" s")[0])
            ep_before = {}
            for ln, _ in heads[1:]:
                prev = [l for l in lines[:ln - 1] if l.startswith("epoch")]; nxt = [l for l in lines[ln:] if l.startswith("epoch")]
                ep_before[ln] = (int(prev[-1].split()[1]) if prev else None, int(nxt[0].split()[1]) if nxt else None)
            mt = os.path.getmtime(os.path.join(CONF, f"ckpt/d2sx_{pr}_N160000_a{s}.pt"))
            P(f"    log headers {heads} (KST) resume epochs (last before -> first after) {ep_before}; {done[:110]}")
            P(f"    last ckpt mtime - wall = process start {datetime.datetime.fromtimestamp(mt - wall):%m-%d %H:%M:%S} KST (= CDT + 14 h)")

    P("\n## 2. raws: a1 vs a2 / a3 per dataset (identity over KEYS_RAW, table B, gap, -3 dB, Wilson, R, guard)")
    for name, pr, tag in SETS:
        da = R.raw(tag)
        for s, t in (("a1", tag), ("a2", f"{tag}s2"), ("a3", f"{tag}s3")):
            d = R.raw(t); keys = R.points(d, "C2"); k3 = keys[0]
            P(f"\n### {name} {s} raw_{t}: meta {R.meta_line(t, 'C2')}")
            P(f"  n per arm {sorted({n for _, n in R.n_per_arm(d, 'C2')})}; arms {len([a for a in d[keys[0]] if a != 'run'])}; points {[k[2] for k in keys]}")
            if s != "a1":
                P(f"  arms differing from a1 (all KEYS_RAW, 7 points): {R.identity(d, da, 'C2')}")
            nb = len(R.fails(d, keys[0], R.BSTAR))
            P("  b* BLER@16 per SNR: " + " ".join(f"{k[2]:+.0f}:{R.bler(d, k, R.BSTAR):.4f}" for k in keys) + f"  (in [0.005, 0.9]: {[f'{k[2]:+.0f}' for k in keys if 0.005 <= max(R.bler(d, k, R.BSTAR), 0.5 / nb) <= 0.9]})")
            P(f"  table B b*->V1: {R.fmt_b(R.table_b(d, 'C2', R.BSTAR, R.V1))}")
            P(f"  gap b*-V1 2dp {R.paired_gap(d, 'C2', R.BSTAR, R.V1)[1]} | 4dp {R.paired_gap(d, 'C2', R.BSTAR, R.V1, digits=4)[1]}")
            kv = R.nfail(d, k3, R.V1); lo, hi = wilson(kv, nb)
            P(f"  -3 dB: V1 {R.bler(d, k3, R.V1):.3f} ({kv}/{nb}) Wilson95 ({lo:.3f}, {hi:.3f})  V0 {R.bler(d, k3, R.V0):.3f} ({R.nfail(d, k3, R.V0)})  "
              f"b* {R.bler(d, k3, R.BSTAR):.3f} ({R.nfail(d, k3, R.BSTAR)})  genie {R.bler(d, k3, R.GENIE):.3f} ({R.nfail(d, k3, R.GENIE)})")
            P(f"  V1 failures -3..+15: {' '.join(str(R.nfail(d, k, R.V1)) for k in keys)} | b*: {' '.join(str(R.nfail(d, k, R.BSTAR)) for k in keys)} | genie: {' '.join(str(R.nfail(d, k, R.GENIE)) for k in keys)}")
            cand = R.decision_points(d, "C2", R.BSTAR)
            P(f"  R(-3): {R.recovery(d, 'C2', (-3.0,))} | R(decision {cand}): {R.recovery(d, 'C2', tuple(float(c) for c in cand))}")
            nm = np.asarray(d[k3][R.V0]["nmse"]); P(f"  V0 guard fire rate -3 dB: {np.any(~np.isfinite(nm) | (nm > 10.0), axis=1).mean():.3f}")

    P("\n## 3. manifests, tables headers, run logs, chain log, fits links, accept / refarms files")
    for t in TAGS:
        j = json.load(open(os.path.join(CONF, "results/review_next", f"run_manifest_{t}.json")))
        P(f"  manifest {t}: git {j['git_commit']} config_hash {j['config_hash']} n_raw {j['n_raw_files']} ckpt {str(j.get('stagec_ckpt_id'))[:70]} arms {len(j.get('arms', []))} split '{j.get('trial_stream', {}).get('split', '')}'")
        P(f"  tables_D2_{t}.txt: " + " | ".join(l for l in open(os.path.join(CONF, "results", f"tables_D2_{t}.txt")).read().splitlines()[:2]))
        acc = open(os.path.join(CONF, "results/review_next", f"{t}_accept.txt")).read().splitlines()
        ref = open(os.path.join(CONF, "results/review_next", f"{t}_refarms.txt")).read()
        diff = sorted({l.split("arms differing ")[1].split(" (")[0] for l in ref.splitlines() if "arms differing" in l})
        P(f"  {t}_accept.txt line 1: {acc[0]} ({len(acc)} lines); refarms: {len([l for l in ref.splitlines() if 'arms differing' in l])} points, differing sets {diff}")
    for f in ("run_seeds3_eval.log", "cpu_chain.log"):
        P(f"  --- logs/{f}"); [P("    " + l[:160]) for l in open(os.path.join(CONF, "logs", f)).read().splitlines()]
    for t in TAGS:
        ls = open(os.path.join(CONF, "logs", f"run_seeds16e4_{t}.log")).read().splitlines()
        P(f"  run_seeds16e4_{t}.log: " + " | ".join(l.split("] ", 1)[1][:60] for l in ls if l.startswith("[") and ("start" in l or "decision" in l or "acceptance" in l or "DONE" in l)))
    P("  fits links (mtime KST): " + " ".join(f"{os.path.basename(d)}->{os.readlink(d)} {datetime.datetime.fromtimestamp(os.lstat(d).st_mtime):%m-%d %H:%M:%S}"
                                             for d in sorted(glob.glob(os.path.join(CONF, "results/gmm_fits_D2_*B16e4s[23]")) ) if os.path.islink(d) and any(x in d for x in ("D3B16e4s", "SVB16e4s", "MXB16e4s"))))
    st1 = [l for l in open("/home/HTJ/t2_wtS/conf/logs/stage1.log").read().splitlines() if "STAGE1_C6_DONE" in l]
    P("  stage1.log STAGE1_C6_DONE:", st1)
    tl = os.path.join(CONF, "logs/seeds3_train.log")
    P(f"  seeds3_train.log: {open(tl).read().splitlines()} mtime {datetime.datetime.fromtimestamp(os.path.getmtime(tl)):%m-%d %H:%M:%S} KST")


if __name__ == "__main__":
    main()
