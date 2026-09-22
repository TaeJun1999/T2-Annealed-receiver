"""conf/code/pair_tags.py -- paired sign tests ACROSS raw directories (tags): NEXT_EXPERIMENTS v3 §3.1 step 2,
§3.1 step 4 and §3.2 (the §6 prerequisite "pair_tags.py").  Prints numbers and the pre-registered rule outcomes,
never a reading (08_SPEC §5).  Demo/ and every raw dir are read only.

Loading   each tag's raw dir with analysis.load_raw: a trial whose arm RAISED has a non-finite blk_err row and is
          counted as a failure and KEPT.  Failure indicator of a trial = blk_err[:, -1] (BLER@16, §0 / §3.1).
Matching  trials are matched by (cell, prior, snr, skip): at every requested point the (skip, n) chunk list must be
          IDENTICAL in every tag involved, else the script refuses.  load_raw concatenates chunks in skip order, so
          equal chunk lists put the same trial on the same row in every tag.  A chunk list that straddles
          C.DEV_SKIP0 (test and development trials mixed) is refused as well.  An arm missing from a chunk (load_raw
          would fill NaN -> a fake failure) is refused.  Every chunk is opened: its run|skip/n/snr must match its
          file name, run|seed/iters/beta/t_in/dtype must agree across all chunks and tags (iters = C.N_ITER), and
          one tag's chunks of a point must name ONE Stage C checkpoint (else refused).  Overlapping chunks are
          refused; §0 acceptance (dev = 16 x 40 from DEV_SKIP0, test = whole skip [0, DEV_SKIP0)) else INVALID.
House test (§0, 08_SPEC §2): exact two-sided sign test on the discordant pairs = exp_0921_analysis.sign_p, p < 0.05;
          fewer than MIN_DISC = 6 discordant pairs -> UNDECIDED; MDD = smallest net |a-b| reaching p < 0.05 at the
          observed n_d (report only, already implied by p).  p >= 0.05 reads "not decided by this design".
Modes
  pair         arm X of tag A vs arm Y of tag B per point: failures, a:b (a = only X fails), net, p, MDD.
  group        §3.1 step 2: per trial, mean failure over the 'aug' members minus mean over the 'ctrl' members,
               d = 0 dropped, ONE sign test on sign(d) per point (attempts share the trials -> never pooled into n).
               Secondary ("부차"): aug member i vs ctrl member i when the counts match, and "k of m" counts.
  rule3        §3.1 step 4: aug vs ctrl at the decision points given.  PASS iff at >= 2 of the 3 points aug has fewer
               failures with p < 0.05 AND the power guard holds (all 3 points present, >= 6 discordant pairs at >= 2
               of them).  Pooled p is report only.
  interaction  §3.2: d = (fail_V1mean - fail_V1eta) - (fail_gmmBmean - fail_gmmBeta) per trial, d = 0 dropped, sign
               test on sign(d); the two within-prior pairs (H5 = V1-mean vs V1-eta, and the GMM pair) beside it.
  selftest     asserts the §0 MDD table and the exact sign bookkeeping of group / interaction.
Members are TAG:ARM; TAG is a runner tag (conf/raw_<TAG>, '' = conf/raw) or a directory when it contains '/'.
Output: stdout, plus results/review_next/<--out>.txt when --out is given.
"""
import argparse, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C, analysis as AN
from analysis import sign_p, MIN_DISC

OUT = os.path.join(C.CONF, "results", "review_next")
# ---- fixed by NEXT_EXPERIMENTS v3 -- pre-registered, not hyper-parameters
ALPHA = 0.05                                                   # §0 house test
DEV_CHUNKS = [(C.DEV_SKIP0 + 40 * k, 40) for k in range(16)]   # §0 acceptance: exactly 16 chunks x 40 = 640 trials
N_POINTS, WIN_MIN, DISC_PTS = 3, 2, 2                          # §3.1 step 4: 3 decision points, >= 2 wins, guard >= 2
DECISION = ("C2", [-3.0, 0.0, 3.0])                            # §3.1 step 4: 판정점 C2 -3/0/+3 dB, TEST set
RUN_KEYS = ("seed", "iters", "beta", "t_in", "dtype")          # runner run|<k>: must agree in every chunk of every tag
SECTION = {"pair": "§0 house test", "group": "§3.1 step 2", "rule3": "§3.1 step 4", "interaction": "§3.2"}


# ----------------------------------------------------------------------------- statistics
def mdd(nd):
    """§0: smallest net |a-b| (same parity as n_d) with sign_p < ALPHA at n_d discordant pairs; None if unreachable."""
    return next((k for k in range(nd % 2, nd + 1, 2) if sign_p((nd + k) // 2, (nd - k) // 2) < ALPHA), None)


def test_line(a, b, a_less, b_less):
    """a, b = the two discordant counts; a_less / b_less = what 'fewer' means when a < b / b < a."""
    nd, p, m = a + b, sign_p(a, b), mdd(a + b)
    st = (f"UNDECIDED (n_d < {MIN_DISC})" if nd < MIN_DISC else
          "p >= 0.05: not decided by this design" if p >= ALPHA else
          f"p < 0.05: {a_less if a < b else b_less}")
    return f"a:b={a}:{b}  net(a-b)={a - b:+d}  n_d={nd}  p={p:.3g}  MDD@n_d={m if m is not None else 'n/a'}  -> {st}"


def disc(fx, fy):
    """(only X fails, only Y fails) over the same trials."""
    return int(np.sum((fx == 1) & (fy == 0))), int(np.sum((fx == 0) & (fy == 1)))


def group_counts(fa, fc):
    """§3.1 step 2.  fa (n_aug, n), fc (n_ctrl, n) 0/1 -> (#d>0, #d<0, #d==0) for d = mean(fa) - mean(fc).
    Compared in integers (sum_a * n_ctrl vs sum_c * n_aug): d == 0 is exact for any member counts."""
    s = np.sign(fa.sum(0) * len(fc) - fc.sum(0) * len(fa))
    return int(np.sum(s > 0)), int(np.sum(s < 0)), int(np.sum(s == 0))


def interaction_counts(v1m, v1e, gm, ge):
    """§3.2: d = (v1m - v1e) - (gm - ge) per trial -> (#d>0, #d<0, #d==0)."""
    d = (v1m - v1e) - (gm - ge)
    return int(np.sum(d > 0)), int(np.sum(d < 0)), int(np.sum(d == 0))


# ----------------------------------------------------------------------------- loading
def root_of(tag):
    """runner tag -> raw dir (analysis.main's convention: conf/raw_<tag>, '' = conf/raw); '/' in it -> a directory."""
    return tag if "/" in tag else AN.RAW + (f"_{tag}" if tag else "")


def chunk_lists(root, testbed):
    """{(cell, prior, snr): sorted [(skip, n, path)]}, grouped from the filenames exactly as load_raw groups them."""
    pts = {}
    for f in glob.glob(os.path.join(root, f"{testbed}_*.npz")):
        m = AN.PAT.match(os.path.basename(f))
        if m:
            pts.setdefault((m[2], m[3], float(m[8])), []).append((int(m[9]), int(m[10]), f))
    return {k: sorted(v) for k, v in pts.items()}


def chunk_ids(key, chunks):
    """Reads every chunk's run|<k> and Stage C checkpoint identity.  A file whose run|skip/n/snr contradicts its
    name (renamed / relabelled) is refused -> (set of RUN_KEYS tuples, set of checkpoint ids)."""
    runs, ids = set(), set()
    for skip, n, f in chunks:
        with np.load(f) as z:
            r = {k[4:]: z[k].item() for k in z.files if k.startswith("run|")}
            ids.add(next((str(z[k].item()) for k in ("meta|stagec_ckpt_id", "meta|stagec_ckpt") if k in z.files),
                         "none (no Stage C checkpoint recorded)"))
        if (r.get("skip"), r.get("n"), r.get("snr")) != (skip, n, key[2]):
            sys.exit(f"REFUSED: {f}: run|skip/n/snr = {r.get('skip')}/{r.get('n')}/{r.get('snr')} contradicts the "
                     "file name (renamed or relabelled chunk)")
        runs.add(tuple(r.get(k) for k in RUN_KEYS))
    return runs, ids


def split_of(ch):
    """-> (text, accepted, is_test).  Split by C.DEV_SKIP0.  §0 acceptance: a development point is exactly
    DEV_CHUNKS; a test point is exactly the contiguous skip [0, DEV_SKIP0).  Overlapping chunks are refused."""
    lo, hi = ch[0][0], ch[-1][0] + ch[-1][1]
    contig = all(a[0] + a[1] == b[0] for a, b in zip(ch, ch[1:]))
    rng = f"skip [{lo}, {hi}) in {len(ch)} chunks, n={sum(n for _, n in ch)}" + ("" if contig else " (NOT CONTIGUOUS)")
    if lo < C.DEV_SKIP0 < hi:
        sys.exit(f"REFUSED: chunk list straddles DEV_SKIP0={C.DEV_SKIP0} (test and development trials mixed): {ch}")
    if any(a[0] + a[1] > b[0] for a, b in zip(ch, ch[1:])):
        sys.exit(f"REFUSED: overlapping chunks (the same trial would be counted twice): {ch}")
    if hi <= C.DEV_SKIP0:
        ok = contig and lo == 0 and hi == C.DEV_SKIP0
        return f"TEST        {rng}  §0 test set " + ("OK" if ok else "INCOMPLETE -> this run is INVALID"), ok, True
    ok = ch == DEV_CHUNKS
    return f"DEVELOPMENT {rng}  §0 acceptance " + ("OK" if ok else "FAILED -> this run is INVALID"), ok, False


def fail_vec(v):
    f = v["blk_err"][:, -1]                  # load_raw already turned a raised trial's NaN row into 1.0
    if "failed" in v:
        f = np.maximum(f, np.asarray(v["failed"], float))
    assert np.isin(f, (0.0, 1.0)).all(), "blk_err@16 is not 0/1"
    return f.astype(np.int64)


def load(members, testbed, cell, prior, snrs, allow_missing=False):
    """members [(tag, arm)] -> (F {(tag, arm, snr): int (n,)}, header lines, missing snrs, invalid snrs, test snrs).
    A point absent from some tag is fatal unless allow_missing (rule3: it then fails the power guard).
    Every chunk must carry the same run parameters (RUN_KEYS, iters = C.N_ITER) in every tag, and one tag's
    chunks of a point must share ONE Stage C checkpoint (a resume with another --stagec-ckpt is refused)."""
    tags = list(dict.fromkeys(t for t, _ in members))
    chs = {t: chunk_lists(root_of(t), testbed) for t in tags}
    lines, missing, invalid, test, keep, runs, ids = [], [], [], [], [], set(), {t: set() for t in tags}
    for s in snrs:
        key = (cell, prior, float(s))
        absent = [t for t in tags if key not in chs[t]]
        if absent:
            if not allow_missing:
                sys.exit(f"REFUSED: point {key} is absent from tag(s) {absent}")
            missing.append(s)
            lines.append(f"point {s:+g} dB: ABSENT from tag(s) {absent}")
            continue
        sn = {t: [(k, n) for k, n, _ in chs[t][key]] for t in tags}
        ref = sn[tags[0]]
        for t in tags[1:]:
            if sn[t] != ref:
                sys.exit(f"REFUSED: chunk sets differ at {key}:\n  {tags[0]!r}: {ref}\n  {t!r}: {sn[t]}"
                         f"\n  only in {tags[0]!r}: {sorted(set(ref) - set(sn[t]))}"
                         f"\n  only in {t!r}: {sorted(set(sn[t]) - set(ref))}")
        txt, ok, is_test = split_of(ref)
        invalid += [] if ok else [s]
        test += [s] if is_test else []
        for t in tags:
            r, i = chunk_ids(key, chs[t][key])
            if len(i) > 1:
                sys.exit(f"REFUSED: tag {t!r} mixes Stage C checkpoints across the chunks of {key}: {sorted(i)}")
            runs |= r
            ids[t] |= i
        lines.append(f"point {s:+g} dB: {txt}; identical (skip, n) chunk list in all {len(tags)} tag(s)")
        keep.append(key)
    if len(runs) > 1:
        sys.exit(f"REFUSED: run parameters {RUN_KEYS} differ between chunks/tags: {sorted(runs, key=str)}")
    if runs and dict(zip(RUN_KEYS, next(iter(runs))))["iters"] != C.N_ITER:
        sys.exit(f"REFUSED: run|iters != {C.N_ITER}: blk_err[:, -1] would not be BLER@{C.N_ITER} (§0): {runs}")
    lines += ["run params  : " + "  ".join(f"{k}={v}" for k, v in zip(RUN_KEYS, r)) + "  (every chunk, every tag)"
              for r in runs]
    lines += [f"stage C ckpt: [{t}] {' || '.join(sorted(ids[t]))}" for t in tags]
    F = {}
    for t in tags:
        data, _, warns = AN.load_raw(testbed, root_of(t))
        arms = [a for tt, a in members if tt == t]
        for key in keep:
            for a in arms:
                if a not in data[key]:
                    sys.exit(f"REFUSED: arm {a!r} absent from tag {t!r} at {key}")
                bad = [w for w in warns if str(key) in w and f"'{a}|blk_err'" in w]
                if bad:
                    sys.exit(f"REFUSED: arm {a!r} missing from a chunk of tag {t!r} at {key}:\n" + "\n".join(bad))
                F[(t, a, key[2])] = fail_vec(data[key][a])
        lines += [f"load_raw [{t}]: {w.strip()}" for w in warns if any(str(k) in w for k in keep)]
        del data
    return F, lines, missing, invalid, test


def member(s):
    if ":" not in s:
        raise argparse.ArgumentTypeError(f"member must be TAG:ARM, got {s!r}")
    return tuple(s.split(":", 1))


def lbl(m):
    return f"{m[0] or '(raw)'}:{m[1]}"


def fails_line(F, ms, s):
    n = len(F[ms[0] + (s,)])
    return "  failures " + "  ".join(f"{lbl(m)}={int(F[m + (s,)].sum())}/{n} ({F[m + (s,)].mean():.4f})" for m in ms)


# ----------------------------------------------------------------------------- modes
def run_pair(F, a, snrs, out):
    x, y = a.x, a.y
    out.append(f"\nPAIR  X = {lbl(x)}   Y = {lbl(y)}   (a = only X fails, b = only Y fails)")
    for s in snrs:
        out.append(f" {s:+g} dB" + fails_line(F, [x, y], s))
        out.append("   " + test_line(*disc(F[x + (s,)], F[y + (s,)]), "X fewer failures", "Y fewer failures"))


def run_group(F, a, snrs, out):
    out.append(f"\nGROUP (§3.1 step 2)  aug = {[lbl(m) for m in a.aug]}   ctrl = {[lbl(m) for m in a.ctrl]}")
    out.append("  d = mean_aug(fail) - mean_ctrl(fail) per trial; d = 0 dropped; a = #d>0 (aug worse), b = #d<0 (aug better)")
    for s in snrs:
        fa = np.stack([F[m + (s,)] for m in a.aug])
        fc = np.stack([F[m + (s,)] for m in a.ctrl])
        npos, nneg, nz = group_counts(fa, fc)
        out.append(f" {s:+g} dB" + fails_line(F, a.aug + a.ctrl, s))
        out.append(f"   group mean failures aug={fa.mean(0).sum():.2f} ctrl={fc.mean(0).sum():.2f} of n={fa.shape[1]}"
                   f"   d=0 dropped: {nz}")
        out.append("   PRIMARY  " + test_line(npos, nneg, "aug fewer failures", "ctrl fewer failures"))
        if len(a.aug) != len(a.ctrl):
            out.append("   secondary (member i vs member i): n/a -- member counts differ")
            continue
        fewer = sig = 0
        for i, (ma, mc) in enumerate(zip(a.aug, a.ctrl)):
            x, y = disc(F[ma + (s,)], F[mc + (s,)])
            fewer += x < y
            sig += x < y and sign_p(x, y) < ALPHA
            out.append(f"   secondary {i + 1}: {lbl(ma)} vs {lbl(mc)}  "
                       + test_line(x, y, "aug fewer failures", "ctrl fewer failures"))
        out.append(f"   secondary: aug fewer failures in {fewer}/{len(a.aug)} pairs, with p < 0.05 in {sig}/{len(a.aug)}")


def run_rule3(F, a, snrs, missing, test, out):
    x, y = a.aug, a.ctrl
    out.append(f"\nRULE3 (§3.1 step 4)  aug = {lbl(x)}   ctrl = {lbl(y)}   decision points {[f'{s:+g}' for s in snrs]}")
    out.append("  a = only aug fails, b = only ctrl fails")
    res = []
    for s in snrs:
        if s in missing:
            out.append(f" {s:+g} dB  ABSENT")
            continue
        ab = disc(F[x + (s,)], F[y + (s,)])
        res.append(ab)
        out.append(f" {s:+g} dB" + fails_line(F, [x, y], s))
        out.append("   " + test_line(*ab, "aug fewer failures", "ctrl fewer failures"))
    A, B = sum(r[0] for r in res), sum(r[1] for r in res)
    nd = [p + q for p, q in res]
    wins = sum(1 for p, q in res if p < q and sign_p(p, q) < ALPHA)
    loss = sum(1 for p, q in res if q < p and sign_p(p, q) < ALPHA)
    guard = len(snrs) == N_POINTS and not missing and sum(d >= MIN_DISC for d in nd) >= DISC_PTS
    out.append(f"  pooled (REPORT ONLY) a:b={A}:{B}  p={sign_p(A, B):.3g}")
    out.append(f"  power guard: {len(snrs) - len(missing)}/{len(snrs)} points present (needs all {N_POINTS}), discordant "
               f"counts {nd} (needs >= {MIN_DISC} at >= {DISC_PTS}) -> " + ("POWERED" if guard else "UNDECIDED"))
    out.append(f"  aug fewer failures with p < 0.05 at {wins}/{len(snrs)} points; ctrl fewer failures with p < 0.05 at "
               f"{loss}/{len(snrs)} points")
    prereg = a.cell == DECISION[0] and sorted(snrs) == DECISION[1] and sorted(test) == DECISION[1]
    out.append(("  §3.1 step 4 verdict: " if prereg else
                f"  rule outcome (NOT the §3.1 step 4 verdict: its decision points are {DECISION[0]} "
                f"{DECISION[1]} dB on the TEST set): ")
               + ("PASS" if guard and wins >= WIN_MIN else
                  "NOT PASSED (power guard failed)" if not guard else "NOT PASSED"))


def run_interaction(F, a, snrs, out):
    v1m, v1e, gm, ge = a.v1_mean, a.v1_eta, a.gmm_mean, a.gmm_eta
    out.append(f"\nINTERACTION (§3.2)  V1-mean={lbl(v1m)}  V1-eta={lbl(v1e)}  gmmB-mean={lbl(gm)}  gmmB-eta={lbl(ge)}")
    out.append("  d = (fail_V1mean - fail_V1eta) - (fail_gmmBmean - fail_gmmBeta); d = 0 dropped; a = #d>0, b = #d<0")
    for s in snrs:
        f = [F[m + (s,)] for m in (v1m, v1e, gm, ge)]
        npos, nneg, nz = interaction_counts(*f)
        out.append(f" {s:+g} dB" + fails_line(F, [v1m, v1e, gm, ge], s))
        out.append("   H5 pair  V1-mean vs V1-eta (a = only V1-mean fails):  "
                   + test_line(*disc(f[0], f[1]), "V1-mean fewer failures", "V1-eta fewer failures"))
        out.append("   GMM pair gmmB-mean vs gmmB-eta (a = only gmmB-mean fails):  "
                   + test_line(*disc(f[2], f[3]), "gmmB-mean fewer failures", "gmmB-eta fewer failures"))
        out.append(f"   INTERACTION  d=0 dropped: {nz}  |d|=2: {int(np.sum(np.abs((f[0] - f[1]) - (f[2] - f[3])) == 2))}  "
                   + test_line(npos, nneg, "V1 improvement (mean vs eta) larger", "gmmB improvement (mean vs eta) larger"))
        met = npos + nneg >= MIN_DISC and sign_p(npos, nneg) < ALPHA and nneg > npos
        out.append(f"   §3.2 attribution condition (n_d >= {MIN_DISC}, p < 0.05 AND #d<0 > #d>0): "
                   + ("met" if met else "not met"))


def selftest():
    for nd, k in {19: 11, 26: 12, 32: 14, 38: 14, 45: 15, 51: 15}.items():        # §0's quoted MDD values
        assert mdd(nd) == k, (nd, mdd(nd), k)
    assert mdd(5) is None and mdd(6) == 6 and sign_p(6, 0) < ALPHA <= sign_p(5, 0)
    assert "UNDECIDED" in test_line(5, 0, "", "") and "p < 0.05: X" in test_line(0, 6, "X", "Y")
    fa = np.array([[1, 1, 0, 1], [1, 0, 0, 0], [0, 0, 0, 1]])                     # 3 aug members, 4 trials
    fc = np.array([[1, 0, 0, 1], [0, 1, 0, 1]])                                   # 2 ctrl members
    assert group_counts(fa, fc) == (1, 2, 1), group_counts(fa, fc)                # 2/3>1/2, 1/3<1/2, 0=0, 2/3<1
    fb = np.array([[1, 0], [0, 1], [1, 1]])                                       # equal sums -> d == 0 exactly
    assert group_counts(fb, fb[::-1]) == (0, 0, 2)
    o = np.array
    assert interaction_counts(o([1, 0, 0, 1]), o([0, 1, 0, 1]), o([0, 0, 1, 0]), o([0, 0, 1, 1])) == (2, 1, 1)
    assert disc(o([1, 1, 0, 0]), o([1, 0, 1, 1])) == (1, 2)
    tst = [(40 * k, 40) for k in range(C.DEV_SKIP0 // 40)]
    assert split_of(tst)[1:] == (True, True) and split_of(tst[:-1])[1:] == (False, True)          # test set / short
    assert split_of(tst[:3] + tst[4:])[1:] == (False, True)                                        # hole -> INVALID
    assert split_of(DEV_CHUNKS)[1:] == (True, False) and split_of(DEV_CHUNKS[1:])[1:] == (False, False)
    for bad in ([(0, 40), (20, 40)], [(2520, 40), (2560, 40)]):                                    # overlap, straddle
        try:
            split_of(bad)
            raise AssertionError(bad)
        except SystemExit:
            pass
    return ("selftest OK -- §0 MDD table, MIN_DISC, exact group d==0 with unequal member counts, interaction signs, "
            "§0 split acceptance")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="mode", required=True)
    com = argparse.ArgumentParser(add_help=False)
    com.add_argument("--testbed", default="D2", choices=("D1", "D2"))
    com.add_argument("--cell", default="C2")
    com.add_argument("--prior", default=None, help="default common.PRIOR_OF[testbed]")
    com.add_argument("--snr", type=float, nargs="+", required=True, help="SNR points (dB); rule3: the 3 decision points")
    com.add_argument("--out", default=None, help="also write results/review_next/<OUT>.txt")
    com.add_argument("--overwrite", action="store_true")
    p = sub.add_parser("pair", parents=[com])
    p.add_argument("--x", type=member, required=True)
    p.add_argument("--y", type=member, required=True)
    p = sub.add_parser("group", parents=[com])
    p.add_argument("--aug", type=member, nargs="+", required=True)
    p.add_argument("--ctrl", type=member, nargs="+", required=True)
    p = sub.add_parser("rule3", parents=[com])
    p.add_argument("--aug", type=member, required=True)
    p.add_argument("--ctrl", type=member, required=True)
    p = sub.add_parser("interaction", parents=[com])
    for k in ("--v1-mean", "--v1-eta", "--gmm-mean", "--gmm-eta"):
        p.add_argument(k, type=member, required=True)
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.mode == "selftest":
        print(selftest())
        return
    prior = a.prior or C.PRIOR_OF[a.testbed]
    members = {"pair": lambda: [a.x, a.y], "group": lambda: a.aug + a.ctrl, "rule3": lambda: [a.aug, a.ctrl],
               "interaction": lambda: [a.v1_mean, a.v1_eta, a.gmm_mean, a.gmm_eta]}[a.mode]()
    if len(set(a.snr)) != len(a.snr) or len(set(members)) != len(members):
        sys.exit(f"REFUSED: a point or a member is given twice (it would be counted twice): {a.snr} {members}")
    path = os.path.join(OUT, os.path.basename(a.out) + ".txt") if a.out else None
    if path and os.path.exists(path) and not a.overwrite:
        sys.exit(f"REFUSED: {path} exists (pass --overwrite)")
    F, lines, missing, invalid, test = load(members, a.testbed, a.cell, prior, a.snr, allow_missing=a.mode == "rule3")
    snrs = [s for s in a.snr if s not in missing] if a.mode != "rule3" else a.snr
    tags = list(dict.fromkeys(t for t, _ in members))
    out = [C.header(a.testbed, [
        f"script      : conf/code/pair_tags.py {a.mode}  (NEXT_EXPERIMENTS v3 {SECTION[a.mode]})",
        f"points      : testbed {a.testbed}  cell {a.cell}  prior {prior}  SNR {[f'{s:+g}' for s in a.snr]} dB",
        f"house test  : exact two-sided sign test on discordant pairs (exp_0921_analysis.sign_p), p < {ALPHA}; n_d < "
        f"{MIN_DISC} -> UNDECIDED; MDD = smallest net |a-b| with p < {ALPHA} at the observed n_d (report only)",
        "failure     : blk_err[:, -1] (BLER@16) via analysis.load_raw; a trial whose arm RAISED is a failure and is kept",
        f"split       : DEVELOPMENT = skip >= C.DEV_SKIP0 = {C.DEV_SKIP0} (§0 acceptance = exactly 16 chunks (2560+40k, 40)),"
        f" TEST = skip < {C.DEV_SKIP0}",
    ] + [f"tag         : {t!r:<16} -> {root_of(t)}" for t in tags]
      + [f"member      : {lbl(m)}" for m in members] + lines)]
    {"pair": lambda: run_pair(F, a, snrs, out), "group": lambda: run_group(F, a, snrs, out),
     "rule3": lambda: run_rule3(F, a, snrs, missing, test, out),
     "interaction": lambda: run_interaction(F, a, snrs, out)}[a.mode]()
    if invalid:
        out.append(f"\n!!! §0 acceptance FAILED at {[f'{s:+g}' for s in invalid]} dB -> every number above comes from an "
                   "INVALID run (development: not exactly 16 x 40 from DEV_SKIP0; test: not the whole skip [0, DEV_SKIP0))")
    txt = "\n".join(out) + "\n"
    print(txt, end="")
    if path:
        os.makedirs(OUT, exist_ok=True)
        with open(path, "w") as f:
            f.write(txt)
        print(f"# written: {path}")


if __name__ == "__main__":
    main()
