"""NUMERIC re-derivation of every number in NEXT_EXPERIMENTS_SEEDS3_16e4.md §6.1 (+ §0 a1 citations, §3 scoring, §5 ckpt
fields), the matching docs/EXPERIMENTS.md row and the DECISIONS.md line (record audit, 2026-09-30, numeric auditor).
(`recompute_seeds3.py` in this folder is the parallel provenance auditor's script; this file is kept separate so neither
overwrites the other.)

Reads ONLY raw npz, checkpoints, logs, manifests and git.  Reuses the independent helpers of
prereg_audit_2026-09-27/recompute.py (table B anchored on the first arm, scipy binomtest exact sign test, POWERED / 2-of-3
rule, paired bootstrap gap seed 20260925, recovery bootstrap seed 20260926); does NOT call analysis.py table code,
recovery_ci.py or any pair script.  analysis.load_raw is used as the raw reader only (through the 09-27 module).
Every quoted document value is checked programmatically (doc dict below) and the mismatches are listed in §4.

    CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=2 ~/miniforge3/envs/torch/bin/python \
        conf/results/review_next/prereg_audit_2026-09-30/recompute_seeds3_numeric.py > .../recompute_seeds3_numeric.out
"""
import datetime
import importlib.util
import json
import math
import os

import numpy as np

CONF = "/home/HTJ/t2/conf"
_spec = importlib.util.spec_from_file_location("rc0927", os.path.join(CONF, "results/review_next/prereg_audit_2026-09-27/recompute.py"))
rc = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(rc)
P, raw, points, bler, nfail, table_b, fmt_b, paired_gap, recovery, meta_line, identity, same, sha16, git = (
    rc.P, rc.raw, rc.points, rc.bler, rc.nfail, rc.table_b, rc.fmt_b, rc.paired_gap, rc.recovery, rc.meta_line, rc.identity, rc.same, rc.sha16, rc.git)
BSTAR, V1, GENIE, V0 = rc.BSTAR, rc.V1, rc.GENIE, rc.V0

SETS = (("D3", "S2c", "D3B16e4", ("D3B16e4s2", "D3B16e4s3")), ("SV8e", "SV8e", "SVB16e4", ("SVB16e4s2", "SVB16e4s3")),
        ("MIX3", "MIX3", "MXB16e4", ("MXB16e4s2", "MXB16e4s3")))
# §6.1 table as written (a:b per decision point, pooled, label, gap, V1 -3 dB fails, R)
DOC = {
    "D3B16e4":   ("221:39 116:19 56:9", "393:67", "(i)", "+1.41 [+1.19, +1.67]", 1000, "0.367 [0.335, 0.399]"),
    "D3B16e4s2": ("223:31 117:23 57:12", "397:66", "(i)", "+1.42 [+1.20, +1.69]", 1024, "0.337 [0.306, 0.370]"),
    "D3B16e4s3": ("224:34 118:18 59:10", "401:62", "(i)", "+1.46 [+1.24, +1.74]", 1019, "0.343 [0.312, 0.375]"),
    "SVB16e4":   ("124:62 24:10", "148:72", "(iv)", "+0.25 [+0.16, +0.33]", 402, "0.143 [0.095, 0.188]"),
    "SVB16e4s2": ("120:65 27:12", "147:77", "(iv)", "+0.24 [+0.15, +0.32]", 409, "0.127 [0.079, 0.175]"),
    "SVB16e4s3": ("126:62 28:6", "154:68", "(iv)", "+0.30 [+0.22, +0.39]", 400, "0.148 [0.098, 0.192]"),
    "MXB16e4":   ("85:39 71:21 42:11", "198:71", "(i)", "+0.98 [+0.68, +1.31]", 1354, "0.090 [0.062, 0.117]"),
    "MXB16e4s2": ("79:38 62:28 41:15", "182:81", "(i)", "+0.72 [+0.44, +1.03]", 1363, "0.078 [0.052, 0.106]"),
    "MXB16e4s3": ("79:40 66:24 41:12", "186:76", "(i)", "+0.83 [+0.54, +1.15]", 1358, "0.085 [0.058, 0.112]"),
}
DOC_DP = {"D3": ["+0", "+3", "+6"], "SV8e": ["-3", "+0"], "MIX3": ["+3", "+6", "+9"]}
DOC_BG = {"D3": (1298, 485), "SV8e": (464, 31), "MIX3": (1421, 679)}          # b*/genie -3 dB fails, "same in all three seeds"
DOC_BSTAR_M3 = {"D3": 0.507, "SV8e": 0.181, "MIX3": 0.555}; DOC_GENIE_M3 = {"D3": 0.189, "SV8e": 0.012, "MIX3": 0.265}   # §0 row 3
DOC_SPREAD = {"D3": "0.391-0.400", "SV8e": "0.156-0.160", "MIX3": "0.529-0.532"}
DOC_CKPT = {  # §5: sha16, epoch(=best_epoch), last epoch, best val
    "S2c_a2": ("4e9a6ca2c3197004", 386, 406, 0.3548574447631836), "S2c_a3": ("3e4e36945a9314c3", 449, 469, 0.3555413484573364),
    "SV8e_a2": ("b05d92632e611494", 236, 256, 0.7134526968002319), "SV8e_a3": ("5e1ff49f455f110a", 299, 319, 0.7135599255561829),
    "MIX3_a2": ("d7a6b1a199c51637", 433, 453, 0.4829578399658203), "MIX3_a3": ("128b8090036332bc", 351, 371, 0.48177969455718994)}
DOC_A1 = {"S2c": (0.3534156, 494), "SV8e": (0.7134662, 240), "MIX3": (0.4814744, 464)}   # §0 last row
PRED = {"D3": ((0.372, 0.410), (1.19, 1.67)), "SV8e": ((0.143, 0.172), (0.16, 0.33)), "MIX3": ((0.510, 0.548), None)}
REFSET = ['M-ours-dscore-C-V0', 'M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b']


def wilson(k, n, z=1.959963984540054):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


def ci_of(txt):
    """'+1.42 [+1.20, +1.69]' -> (1.20, 1.69)"""
    a, b = txt.split("[")[1].rstrip("]").split(",")
    return float(a), float(b)


def main():
    mism = []

    def check(where, doc, got):
        ok = str(doc) == str(got)
        if not ok:
            mism.append(f"{where}: doc {doc!r} != recomputed {got!r}")
        return "OK" if ok else "MISMATCH"

    P("# recompute_seeds3_numeric.py -- record audit 2026-09-30 (Fable 5.1, numeric); raw/ckpt/logs/manifest/git only; git HEAD",
      git("rev-parse", "--short", "HEAD"), "| run", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S KST"))
    P("  commits: " + " | ".join(f"{h} {git('show', '-s', '--format=%ci', h)[:19]} KST" for h in ("73a93547", "dbe0bdb3", "6b1de688")))
    P("  conf/code worktree: " + (git("status", "--porcelain", "code") or "(clean)"))

    P("\n## 0. §5 checkpoints (sha256[:16] of _best.pt, stored epoch/best_epoch/best_val; last .pt epoch/best_epoch/stopped_by) + §0 a1 best val")
    import torch
    for pr in ("S2c", "SV8e", "MIX3"):
        for s in ("2", "3"):
            fb, fl = f"d2sx_{pr}_N160000_a{s}_best.pt", f"d2sx_{pr}_N160000_a{s}.pt"
            zb = torch.load(os.path.join(CONF, "ckpt", fb), map_location="cpu", weights_only=False)
            zl = torch.load(os.path.join(CONF, "ckpt", fl), map_location="cpu", weights_only=False)
            sha = sha16(os.path.join(CONF, "ckpt", fb)); d = DOC_CKPT[f"{pr}_a{s}"]
            P(f"  {fb}: sha {sha} epoch={zb.get('epoch')} best_epoch={zb.get('best_epoch')} best_val={zb.get('best_val')!r} attempt={zb.get('attempt')} rung={zb.get('rung')} "
              f"| last {fl}: epoch={zl.get('epoch')} best_epoch={zl.get('best_epoch')} stopped_by={zl.get('stopped_by')}")
            P(f"    vs §5: sha {check(f'§5 {pr} a{s} sha', d[0], sha)} epoch {check(f'§5 {pr} a{s} epoch', d[1], zb.get('epoch'))} "
              f"best_epoch {check(f'§5 {pr} a{s} best_epoch', d[1], zb.get('best_epoch'))} last.epoch {check(f'§5 {pr} a{s} last epoch', d[2], zl.get('epoch'))} "
              f"last.best_epoch==best.epoch {check(f'§5 {pr} a{s} last.best_epoch', d[1], zl.get('best_epoch'))} best_val {check(f'§5 {pr} a{s} best_val', repr(d[3]), repr(float(zb.get('best_val'))))} "
              f"stopped_by=patience {check(f'§5 {pr} a{s} stopped_by', 'patience', zl.get('stopped_by'))}")
            done = [l for l in open(os.path.join(CONF, f"logs/train_d2sx_{pr}_N160000_a{s}.log"), errors="replace").read().splitlines() if l.startswith("# done")]
            P(f"    log: {done[-1] if done else '(no done line)'}")
        z = torch.load(os.path.join(CONF, "ckpt", f"d2sx_{pr}_N160000_a1_best.pt"), map_location="cpu", weights_only=False)
        P(f"  a1 {pr}: best_val={float(z.get('best_val')):.7f} @{z.get('best_epoch')} vs §0 {DOC_A1[pr]} -> {check(f'§0 {pr} a1 best val', DOC_A1[pr], (round(float(z.get('best_val')), 7), z.get('best_epoch')))}")

    P("\n## 1. run log / chain log / stage-1 log / manifests / acceptance files")
    for l in open(os.path.join(CONF, "logs/run_seeds3_eval.log"), errors="replace").read().splitlines():
        if l.startswith("[seeds3"):
            P("  " + l[:160])
    P("  cpu_chain.log: " + " || ".join(l[:80] for l in open(os.path.join(CONF, "logs/cpu_chain.log"), errors="replace").read().splitlines() if "SEEDS3" in l or "stage 1" in l))
    s1 = "/home/HTJ/t2_wtS/conf/logs/stage1.log"
    P("  stage1.log: " + " || ".join(l[:80] for l in open(s1, errors="replace").read().splitlines() if "STAGE1_C6_DONE" in l) if os.path.exists(s1) else "  stage1.log missing")
    for _, _, a1, seeds in SETS:
        for t in seeds:
            j = json.load(open(os.path.join(CONF, "results/review_next", f"run_manifest_{t}.json")))
            acc = open(os.path.join(CONF, "results/review_next", f"{t}_accept.txt")).read().strip().splitlines()
            ref = open(os.path.join(CONF, "results/review_next", f"{t}_refarms.txt")).read()
            arms = sorted({a.strip(" '") for l in ref.splitlines() if "arms differing" in l for a in l.split("arms differing ")[1].split("]")[0].strip("[").split(",")})
            P(f"  {t}: manifest git {j['git_commit']} written {j['written']} n_raw {j['n_raw_files']} ckpt {str(j.get('stagec_ckpt_id'))[:70]} | accept: {acc[-1]} "
              f"{check(f'{t} ACCEPT', f'ACCEPT: OK -- {t}', acc[-1])} | refarms differing (union, 7 points): {arms} {check(f'{t} refarms file set', REFSET, arms)}")

    P("\n## 2. per-dataset re-derivation (a1 cited from §0 + seeds a2, a3)")
    labels = {}
    for name, pr, a1, seeds in SETS:
        P(f"\n### {name} (prior {pr}; a1 raw_{a1}; seeds {seeds})")
        da = raw(a1)
        b_fails = {}; g_fails = {}
        for s, tag in (("a1", a1), ("a2", seeds[0]), ("a3", seeds[1])):
            d = raw(tag); keys = points(d, "C2"); k3 = keys[0]
            P(f"  -- {s} raw_{tag}: meta {meta_line(tag, 'C2')}")
            P(f"     points {[k[2] for k in keys]} n per arm {sorted({n for _, n in rc.n_per_arm(d, 'C2')})} arms {len([a for a in d[keys[0]] if a != 'run'])}")
            if s != "a1":
                diff = identity(d, da, "C2")
                P(f"     arms differing from a1 (7 KEYS_RAW x 7 points): {diff} -> {check(f'{tag} refarms set (recomputed)', REFSET, diff)}")
                gen_same = all(same(d[k][GENIE][q], da[k][GENIE][q]) for k in keys for q in rc.KEYS_RAW if q in d[k][GENIE])
                bs_same = all(same(d[k][BSTAR][q], da[k][BSTAR][q]) for k in keys for q in rc.KEYS_RAW if q in d[k][BSTAR])
                P(f"     genie all keys == a1: {gen_same}; b* all keys == a1: {bs_same} -> {check(f'{tag} b*/genie bit-identical', True, gen_same and bs_same)}")
            tb = table_b(d, "C2", BSTAR, V1); cand, res, pooled, powered, wx, wy, label = tb
            P(f"     table B b*->V1: {fmt_b(tb)}")
            doc = DOC[tag]
            got_ab = " ".join(f"{a}:{b}" for a, b, _ in res); got_pool = f"{pooled[0]}:{pooled[1]}"; got_lab = label.split()[0]
            P(f"     vs §6.1: decision {check(f'{tag} decision pts', DOC_DP[name], [f'{c:+.0f}' for c in cand])} a:b {check(f'{tag} a:b', doc[0], got_ab)} "
              f"pooled {check(f'{tag} pooled', doc[1], got_pool)} label {check(f'{tag} label', doc[2], got_lab)} (wy={wy}/{len(cand)}, POWERED={powered})")
            est, gtxt = paired_gap(d, "C2", BSTAR, V1); _, gtxt4 = paired_gap(d, "C2", BSTAR, V1, digits=4)
            g2 = gtxt.split(" censored")[0]
            P(f"     gap b*-V1: {gtxt} | 4dp {gtxt4} -> {check(f'{tag} gap', doc[3], g2)}")
            nv = nfail(d, k3, V1); lo, hi = wilson(nv, 2560)
            P(f"     V1 -3 dB: {nv}/2560 = {nv / 2560:.4f} -> {nv / 2560:.3f} (95% Wilson {lo:.3f}, {hi:.3f}) -> fails {check(f'{tag} V1 -3 fails', doc[4], nv)}")
            if s == "a1":
                a1_ci = PRED[name][0]
                P(f"       a1 Wilson vs §0/§6.1/§3 {a1_ci}: {check(f'{tag} Wilson', a1_ci, (round(lo, 3), round(hi, 3)))}; "
                  f"b* -3 dB {bler(d, k3, BSTAR):.3f} {check(f'{tag} b* -3 BLER', DOC_BSTAR_M3[name], round(bler(d, k3, BSTAR), 3))} genie {bler(d, k3, GENIE):.3f} {check(f'{tag} genie -3 BLER', DOC_GENIE_M3[name], round(bler(d, k3, GENIE), 3))}")
            rtxt = recovery(d, "C2", (-3.0,)); r_short = rtxt.split("R=")[1].split(" undefined")[0].replace("[90% ", "[")
            P(f"     R(-3 dB): {rtxt} -> {check(f'{tag} R', doc[5], r_short)} | R(decision pts {cand}): {recovery(d, 'C2', tuple(float(c) for c in cand))}")
            P(f"     -3 dB: b* {nfail(d, k3, BSTAR)} ({bler(d, k3, BSTAR):.3f}) V1 {nv} ({nv / 2560:.3f}) V0 {nfail(d, k3, V0)} ({bler(d, k3, V0):.3f}) genie {nfail(d, k3, GENIE)} ({bler(d, k3, GENIE):.3f})")
            P(f"     fails -3..+15 V1: {' '.join(str(nfail(d, k, V1)) for k in keys)} | b*: {' '.join(str(nfail(d, k, BSTAR)) for k in keys)} | genie: {' '.join(str(nfail(d, k, GENIE)) for k in keys)}")
            nm = np.asarray(d[k3][V0]["nmse"]); P(f"     V0 guard fire rate -3 dB: {np.any(~np.isfinite(nm) | (nm > 10.0), axis=1).mean():.3f}")
            b_fails[s] = nfail(d, k3, BSTAR); g_fails[s] = nfail(d, k3, GENIE)
            labels[(name, s)] = (got_lab, nv / 2560, ci_of(doc[3]), (round(lo, 3), round(hi, 3)), ci_of(g2))
        eq = len(set(b_fails.values())) == 1 and len(set(g_fails.values())) == 1
        P(f"  b*/genie -3 dB fails across seeds: {b_fails} / {g_fails} -> equal {eq} {check(f'{name} b*/genie equal across seeds', True, eq)}; "
          f"vs §6.1 {DOC_BG[name]}: {check(f'{name} b*/genie -3 counts', DOC_BG[name], (b_fails['a1'], g_fails['a1']))}")
        labs = [labels[(name, s)][0] for s in ("a1", "a2", "a3")]
        k = labs.count("(i)"); m = sum(1 for l in labs if l in ("(ii)", "(iii)")); j = sum(1 for l in labs if l == "(iv)")
        agg = "시드 강건 (3/3 (i))" if k == 3 else f"시드 의존 ({k}/3 (i), {m} 다름)" if m else f"판정하지 못함 ({k}/3 (i), {j} 판정 못함)"
        exp = {"D3": "시드 강건 (3/3 (i))", "SV8e": "판정하지 못함 (0/3 (i), 3 판정 못함)", "MIX3": "시드 강건 (3/3 (i))"}[name]
        P(f"  seed labels a1/a2/a3 = {labs} -> aggregate \"{agg}\" -> {check(f'{name} aggregate label', exp, agg)}")
        v = [labels[(name, s)][1] for s in ("a1", "a2", "a3")]
        P(f"  spread V1 -3 dB (3 seeds): {min(v):.3f}-{max(v):.3f} -> {check(f'{name} spread', DOC_SPREAD[name], f'{min(v):.3f}-{max(v):.3f}')}")

    P("\n## 3. §3 prediction scoring (recomputed values; closed intervals; 3-digit BLER; CI overlap = non-empty intersection incl. endpoints)")
    def ok3(x, lo, hi):
        return lo <= round(x, 3) <= hi
    def overlap(ci, ref):
        return max(ci[0], ref[0]) <= min(ci[1], ref[1])
    r = {}
    r[1] = all(labels[("D3", s)][0] == "(i)" for s in ("a2", "a3"))
    r[2] = all(ok3(labels[("D3", s)][1], *PRED["D3"][0]) for s in ("a2", "a3"))
    r[3] = all(overlap(labels[("D3", s)][4], PRED["D3"][1]) for s in ("a2", "a3"))
    r[4] = all(ok3(labels[("SV8e", s)][1], *PRED["SV8e"][0]) for s in ("a2", "a3"))
    r[5] = all(overlap(labels[("SV8e", s)][4], PRED["SV8e"][1]) for s in ("a2", "a3"))
    r[6] = all(labels[("MIX3", s)][0] == "(i)" for s in ("a2", "a3"))
    r[7] = all(ok3(labels[("MIX3", s)][1], *PRED["MIX3"][0]) for s in ("a2", "a3"))
    r[8] = not [m for m in mism if "stopped_by" in m]
    for i in range(1, 9):
        P(f"  pred {i}: {'✓' if r[i] else '✗'}")
    P(f"  total hits {sum(r.values())}/8 -> {check('§3 score', '8/8', f'{sum(r.values())}/8')}")
    for name in ("D3", "SV8e", "MIX3"):
        for s in ("a2", "a3"):
            l = labels[(name, s)]
            P(f"    {name} {s}: V1 -3 {l[1]:.3f} Wilson {l[3]}, gap CI (doc {l[2]}, recomputed {l[4]})")

    P("\n## 4. summary")
    P(f"  mismatches: {len(mism)}")
    for m in mism:
        P("   - " + m)


if __name__ == "__main__":
    main()
