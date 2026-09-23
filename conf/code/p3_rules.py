"""conf/code/p3_rules.py -- review_next P3 judgement: the loop rules of NEXT_EXPERIMENTS_P3 (pre-registration v2, frozen
d7e404ff) applied OFFLINE to one 32-iteration run and checked against the 16-iteration reference run.  Prints numbers
and the pre-registered rule outcomes, never a reading.  Raw directories are read only.

Inputs    conf/raw_review_next_P3ref (iters 16: V1, b*, R5-genie) and conf/raw_review_next_P3 (iters 32 + r_t: V1, b*,
          V1-b05, bstar-b05, V1-fb05, bstar-fb05), D2 / S2, trials skip 3200.. of each point's stream.
Acceptance (else the point is INVALID and nothing is judged):
          chunk set exactly {(3200 + 40k, 40)} (k < 32 at the judging point C2 -3 dB, k < 16 at the report-only points)
          in BOTH tags; every chunk's run|skip/n/snr match its file name, run|seed/beta/t_in/dtype are the frozen ones,
          run|iters = 16 (P3ref) / 32 (P3); one Stage C checkpoint = ckpt/d2sx_N160000_a1.pt, b* = kron K=1024,
          N_train 1.6e5; every arm present; r_t present for all six P3 arms; the variants' recorded beta / beta_fb are
          the registered ones; iterations 1..16 of V1 and b* in P3 BIT-IDENTICAL to P3ref in every raw field of
          common.KEYS_RAW (a trial that raised only in the 32-iteration run is allowed: it raised after iteration 16).
Rules     per block, offline (§2):  R16 = iteration 16;  R32 = iteration 32;  R-adapt = first t in [16, 32] with
          r_{t-1} < 1e-3 and r_t < 1e-3, else 32 (cost = t);  S-res = among {base, b05, fb05} the run with the smallest
          r_32 (tie or all +inf -> base);  S-conf = smallest alphaD_32 (report only; tie -> base; non-finite = +inf);
          the tie clause has two readings (NEXT_EXPERIMENTS_P3 §5.1, fixed before the judging data were opened):
          PRIMARY = the smallest, base first among tied minimisers then b05, fb05 (all +inf -> base); LITERAL = any tie
          at the minimum -> base.  Both are computed; a verdict that differs between them is printed READING-DEPENDENT.
          oracle = any of the three succeeds at 32 (true bits; not an arm).  r_t non-finite -> +inf.  A trial whose run
          raised: R32 / R-adapt fail with cost 32; the base arm's R16 is then the P3ref value (§1 "비정상 값"); a variant
          has no reference run, so its R16 counts as a failure and the count is printed.  Divergence per rule is
          recomputed on nmse[:, :t] (bigamp.DIVERGE_NMSE, non-finite = diverged); reported, never removed.
Tests     house test: exact two-sided sign test on the discordant pairs (analysis.sign_p), p < 0.05, n_d < 6 -> UNDECIDED.
          Per prior (V1, b*): H6a R32 vs R16, H6b R-adapt vs R16, H7 variant R16 vs base R16 (b05, fb05), H8 S-res vs each
          of the base / b05 / fb05 R32 (all three must be supported); §2.4 interaction for R32 / R-adapt / S-res:
          d = (fV1^rule - fV1^R16) - (fb*^rule - fb*^R16), sign test on sign(d).  17 tests, alpha 0.05, no correction.
          Outcomes: 지지 (p < 0.05, fewer failures) / 판정 불가 (p >= 0.05, n_d >= 6) / UNDECIDED (n_d < 6); a significant
          result in the OTHER direction is printed as such ("반대 방향") and is not support.
Adoption  §3: R-adapt if H6b is supported for BOTH priors and net(R-adapt - R32) <= +3 for both; else R32 if H6a is
          supported for both; else none.  Judging point only.
Output    results/review_next/p3_rules_<point>.{txt,npz} (npz = per-trial rule outcomes, for audit).

    ~/miniforge3/envs/torch/bin/python conf/code/p3_rules.py            # all three points
    ~/miniforge3/envs/torch/bin/python conf/code/p3_rules.py --selftest
"""
import argparse
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C                                             # first: one BLAS thread (env set before numpy)
import numpy as np
import bigamp
from analysis import sign_p, MIN_DISC
from pair_tags import mdd

OUT = os.path.join(C.CONF, "results", "review_next")
TAG_REF, TAG_P3 = "review_next_P3ref", "review_next_P3"
# ---- fixed by NEXT_EXPERIMENTS_P3 v2 (§1-§3) -- pre-registered, not hyper-parameters
ALPHA, R_TOL, T_REF, T_MAX = 0.05, 1e-3, 16, 32
NET_MAX = 3                                                    # §3 adoption: net(R-adapt - R32) <= +3
CHUNK = 40                                                     # §1 acceptance: chunks of 40 from P3_SKIP0
POINTS = (("C2", -3.0, 1280, True), ("C2", 6.0, 640, False), ("C5", -3.0, 640, False))   # (cell, snr, n, judging)
CKPT = os.path.join(C.CONF, "ckpt", "d2sx_N160000_a1.pt")
NTRAIN, BSTAR_K = 160000, 1024
PRIORS = ("V1", "bstar")
BASE = {"V1": "M-ours-dscore-C-V1", "bstar": "M-ours-bstar"}
RUNS = ("base", "b05", "fb05")
ARM = {X: {"base": BASE[X], "b05": f"{X}-b05", "fb05": f"{X}-fb05"} for X in PRIORS}
VAR_CFG = {"b05": ("0.5", "None"), "fb05": ("0.7", "0.5")}     # registered (beta, beta_fb) of each variant
GENIE = "R5-genie"
# report only: real-path block time per 16-iteration block, C2 -3 dB (results/review_next/complexity_moduleH_ep.txt)
MS16 = {"V1": 1006.0, "bstar": 754.0}


# ----------------------------------------------------------------------------- loading + acceptance
class Invalid(Exception):
    pass


def point_glob(tag, cell, snr):
    c = C.CELLS[cell]
    pil = C.make_pilots("D2", "S2", c["Nt"], c["Tp"], c["Nr"])[0]
    return os.path.join(C.CONF, f"raw_{tag}", f"D2_{cell}_S2_Nr{c['Nr']}_T{c['T']}_Tp{c['Tp']}_{pil}_snr{int(snr)}_skip*_n*.npz")


def load(tag, cell, snr, n, iters, arms, rt=False):
    """-> {arm: {field: (n, ...)}} plus the point's meta; raises Invalid on any acceptance failure."""
    files = glob.glob(point_glob(tag, cell, snr))
    have = sorted((int(s), int(m), f) for f in files for s, m in [re.search(r"_skip(\d+)_n(\d+)\.npz$", f).groups()])
    plan = [(C.P3_SKIP0 + CHUNK * k, CHUNK) for k in range(n // CHUNK)]
    if [(s, m) for s, m, _ in have] != plan:
        raise Invalid(f"{tag} {cell} {snr:g} dB: chunk set {[(s, m) for s, m, _ in have]} != {plan}")
    fields = list(C.KEYS_RAW) + (["r_t"] if rt else [])
    out, meta = {a: {q: [] for q in fields + ["failed"]} for a in arms}, {}
    for s, m, f in have:
        with np.load(f) as z:
            want = dict(skip=s, n=m, snr=snr, iters=iters, seed=C.SEED, beta=C.BETA, t_in=C.T_IN)
            for k, v in want.items():
                if z[f"run|{k}"].item() != v:
                    raise Invalid(f"{os.path.basename(f)}: run|{k} = {z[f'run|{k}'].item()} != {v}")
            if str(z["run|dtype"]) != "complex128/float64":
                raise Invalid(f"{os.path.basename(f)}: run|dtype {z['run|dtype']}")
            for k in z.files:
                if k.startswith("meta|") and not k.startswith("meta|budget"):
                    meta.setdefault(k[5:], set()).add(str(z[k]))
            for a in arms:
                for q in fields:
                    if f"{a}|{q}" not in z.files:
                        raise Invalid(f"{os.path.basename(f)}: '{a}|{q}' missing")
                    x = z[f"{a}|{q}"]
                    if x.shape != (m, iters):
                        raise Invalid(f"{os.path.basename(f)}: '{a}|{q}' shape {x.shape} != {(m, iters)}")
                    out[a][q].append(x)
                out[a]["failed"].append(z[f"{a}|failed"] if f"{a}|failed" in z.files else np.zeros(m))
    one = {k: next(iter(v)) for k, v in meta.items() if len(v) == 1}
    for k in ("stagec_ckpt", "stagec_ckpt_id", "bstar", "kron_K", "ntrain"):
        if k not in one:
            raise Invalid(f"{tag} {cell} {snr:g} dB: meta|{k} not unique across chunks: {sorted(meta.get(k, []))}")
    if os.path.realpath(one["stagec_ckpt"]) != os.path.realpath(CKPT):
        raise Invalid(f"{tag}: Stage C checkpoint {one['stagec_ckpt']} != {CKPT}")
    if one["bstar"] != "kron" or int(float(one["kron_K"])) != BSTAR_K or int(float(one["ntrain"])) != NTRAIN:
        raise Invalid(f"{tag}: b* {one['bstar']} K={one['kron_K']} N_train={one['ntrain']} != kron K={BSTAR_K} N={NTRAIN}")
    return {a: {q: np.concatenate(v) for q, v in d.items()} for a, d in out.items()}, one


def check_variants(meta):
    """The P3 run must carry the registered loop constants of every variant and r_t for all six arms."""
    for X in PRIORS:
        for v, (b, bf) in VAR_CFG.items():
            s = meta.get(f"p3_cfg|{ARM[X][v]}")
            if s is None:
                raise Invalid(f"meta|p3_cfg|{ARM[X][v]} missing")
            cfg = dict(kv.split("=", 1) for kv in s.split())
            if (cfg["beta"], cfg["beta_fb"]) != (b, bf):
                raise Invalid(f"{ARM[X][v]}: beta={cfg['beta']} beta_fb={cfg['beta_fb']} != registered {b} / {bf}")
    got = meta.get("extra_log|r_t", "").split("|")[0].split()[1:]
    need = [ARM[X][r] for X in PRIORS for r in RUNS]
    if sorted(set(need) - set(got)):
        raise Invalid(f"r_t not logged for {sorted(set(need) - set(got))}")


def check_bit(p3, ref):
    """§2.1 acceptance: P3 iterations 1..16 == P3ref for V1 and b*, every KEYS_RAW field, bit for bit (NaN == NaN)."""
    late = {}
    for X in PRIORS:
        a = BASE[X]
        r3, rr = p3[a]["failed"] > 0, ref[a]["failed"] > 0
        if np.any(rr & ~r3):
            raise Invalid(f"{a}: {int(np.sum(rr & ~r3))} trials raised in the 16-iteration run but not in the 32-iteration run")
        ok = ~r3
        if not ok.any():
            raise Invalid(f"{a}: every trial raised in the 32-iteration run -- nothing to compare")
        for q in C.KEYS_RAW:
            if not np.array_equal(p3[a][q][ok, :T_REF], ref[a][q][ok], equal_nan=True):
                bad = int(np.sum(np.any(~((p3[a][q][ok, :T_REF] == ref[a][q][ok])
                                          | (np.isnan(p3[a][q][ok, :T_REF]) & np.isnan(ref[a][q][ok]))), 1)))
                raise Invalid(f"{a}|{q}: iterations 1..16 of the 32-iteration run differ from P3ref on {bad} trials")
        late[X] = int(np.sum(r3 & ~rr))
    return late


# ----------------------------------------------------------------------------- rules (pure functions, --selftest)
def fail_at(A, t):
    """0/1 failure at iteration t (1-based); a raised trial or a non-finite entry is a failure."""
    v = A["blk_err"][:, t - 1]
    return np.where((A["failed"] > 0) | ~np.isfinite(v), 1, v).astype(int)


def finite_or_inf(x):
    return np.where(np.isfinite(x), x, np.inf)


def radapt_stop(r):
    """(n, >=32) r_t -> stop iteration per block: first t in [16, 32] with r_{t-1} < R_TOL and r_t < R_TOL, else 32."""
    r = finite_or_inf(r)
    ok = (r[:, T_REF - 2:T_MAX - 1] < R_TOL) & (r[:, T_REF - 1:T_MAX] < R_TOL)       # t = 16..32
    return np.where(ok.any(1), T_REF + ok.argmax(1), T_MAX)


def select(x, literal=False):
    """(n, 3) score per run [base, b05, fb05] (non-finite = +inf) -> index of the chosen run.
    PRIMARY (§5.1): the smallest; among tied minimisers the first in RUNS order (base, b05, fb05); all +inf -> base
    (= argmin, which returns the first minimiser).  literal=True: any tie at the minimum or all +inf -> base, even
    when base is not a minimiser."""
    x = finite_or_inf(x)
    if not literal:
        return x.argmin(1)
    m = x.min(1)
    tie = (x == m[:, None]).sum(1) > 1
    return np.where(tie | ~np.isfinite(m), 0, x.argmin(1))


def diverged_upto(A, t):
    """runner's guardH rule restricted to iterations 1..t_i (t may be a per-block vector)."""
    nm = A["nmse"]
    t = np.broadcast_to(np.asarray(t), (len(nm),))
    with np.errstate(invalid="ignore"):
        bad = ~np.isfinite(nm) | (nm > bigamp.DIVERGE_NMSE)
    upto = np.arange(nm.shape[1])[None, :] < t[:, None]
    return (np.any(bad & upto, 1) | (A["failed"] > 0)).astype(int)


def verdict(a, b):
    """a = trials where only X fails, b = only Y fails -> the §1 outcome for 'X has fewer failures than Y'."""
    nd, p = a + b, sign_p(a, b)
    if nd < MIN_DISC:
        return "UNDECIDED", p
    if p >= ALPHA:
        return "판정 불가", p
    return ("지지", p) if a < b else ("반대 방향 (p < 0.05, 실패 많음) -> 지지 아님", p)


def sign_row(name, fx, fy):
    a, b = int(np.sum((fx == 1) & (fy == 0))), int(np.sum((fx == 0) & (fy == 1)))
    v, p = verdict(a, b)
    m = mdd(a + b)
    return dict(name=name, fx=int(fx.sum()), fy=int(fy.sum()), a=a, b=b, p=p, v=v, mdd=m)


def interaction(fV, fV16, fB, fB16):
    """§2.4: d = (fV - fV16) - (fB - fB16) per trial, d = 0 dropped -> (#d>0, #d<0, p, statement)."""
    d = (fV - fV16) - (fB - fB16)
    pos, neg = int(np.sum(d > 0)), int(np.sum(d < 0))
    p = sign_p(pos, neg)
    if pos + neg < MIN_DISC:
        s = f"UNDECIDED (n_d < {MIN_DISC}) -> 판정 불가"
    elif p < ALPHA and pos > neg:
        s = "이득의 일부는 루프 정체였다 (b* 가 더 많이 회복)"
    elif p < ALPHA and neg > pos:
        s = "루프와 무관한 prior 이득 (V1 이 더 많이 회복)"
    else:
        s = "판정 불가"
    return pos, neg, p, s


def apply_rules(p3, ref):
    """-> per prior: per-trial failure arrays of every rule, stop times, selections, divergence, counts."""
    R = {}
    for X in PRIORS:
        A = {r: p3[ARM[X][r]] for r in RUNS}
        f = {}
        for r in RUNS:
            f[(r, "R32")] = fail_at(A[r], T_MAX)
            f[(r, "R16")] = fail_at(A[r], T_REF)
        # base R16: a trial that raised only in the 32-iteration run takes the P3ref value (§1)
        rb, rr = A["base"]["failed"] > 0, ref[BASE[X]]["failed"] > 0
        f[("base", "R16")] = np.where(rb & ~rr, fail_at(ref[BASE[X]], T_REF), f[("base", "R16")])
        stop = {}
        for r in RUNS:
            t = np.where(A[r]["failed"] > 0, T_MAX, radapt_stop(A[r]["r_t"]))
            stop[r] = t
            be = A[r]["blk_err"][np.arange(len(t)), t - 1]
            f[(r, "R-adapt")] = np.where((A[r]["failed"] > 0) | ~np.isfinite(be), 1, be).astype(int)
        R32 = np.stack([f[(r, "R32")] for r in RUNS], 1)
        rt32 = np.stack([A[r]["r_t"][:, T_MAX - 1] for r in RUNS], 1)
        ad32 = np.stack([A[r]["alphaD"][:, T_MAX - 1] for r in RUNS], 1)
        sel = {"S-res": select(rt32), "S-res|literal": select(rt32, literal=True),
               "S-conf": select(ad32), "S-conf|literal": select(ad32, literal=True)}
        idx = np.arange(len(R32))
        for k, s_ in sel.items():
            f[k] = R32[idx, s_]
        f["oracle"] = R32.min(1)
        # where the PRIMARY reading's RUNS order (b05 before fb05) decides: base not a minimiser, b05 == fb05 < base
        x = finite_or_inf(rt32)
        order_tie = (x[:, 1] == x[:, 2]) & (x[:, 1] < x[:, 0])
        order_matters = order_tie & (R32[:, 1] != R32[:, 2])
        div = {}
        for r in RUNS:
            div[(r, "R16")] = diverged_upto(A[r], T_REF)
            div[(r, "R32")] = diverged_upto(A[r], T_MAX)
            div[(r, "R-adapt")] = diverged_upto(A[r], stop[r])
        div[("base", "R16")] = np.where(rb & ~rr, diverged_upto(ref[BASE[X]], T_REF), div[("base", "R16")])
        D32 = np.stack([div[(r, "R32")] for r in RUNS], 1)
        for k, s_ in sel.items():
            div[k] = D32[idx, s_]
        div["oracle"] = D32.min(1)                              # all three runs diverged
        R[X] = dict(f=f, stop=stop, sel=sel, div=div, order_tie=int(order_tie.sum()),
                    order_matters=int(order_matters.sum()),
                    raised={r: int(np.sum(A[r]["failed"] > 0)) for r in RUNS},
                    raised_mask={r: A[r]["failed"] > 0 for r in RUNS})
    return R


def tests(R):
    """The 17 pre-registered tests (§3), per prior, + the §2.4 interaction and the report-only V1-vs-b* gaps."""
    T = {}
    for X in PRIORS:
        f = R[X]["f"]
        T[("H6a", X)] = [sign_row("R32 vs R16", f[("base", "R32")], f[("base", "R16")])]
        T[("H6b", X)] = [sign_row("R-adapt vs R16", f[("base", "R-adapt")], f[("base", "R16")])]
        for v in ("b05", "fb05"):
            T[(f"H7-{v}", X)] = [sign_row(f"{v} R16 vs base R16", f[(v, "R16")], f[("base", "R16")])]
        T[("H8", X)] = [sign_row(f"S-res vs {r} R32", f["S-res"], f[(r, "R32")]) for r in RUNS]
        T[("H8|literal", X)] = [sign_row(f"S-res(lit) vs {r} R32", f["S-res|literal"], f[(r, "R32")]) for r in RUNS]
    fV, fB = R["V1"]["f"], R["bstar"]["f"]
    I = {}
    for rule in ("R32", "R-adapt", "S-res", "S-res|literal"):
        g = (lambda F: F[rule]) if rule.startswith("S-res") else (lambda F: F[("base", rule)])
        I[rule] = interaction(g(fV), fV[("base", "R16")], g(fB), fB[("base", "R16")])
    gap = {}
    for rule in ("R16", "R32", "R-adapt", "S-res"):
        g = (lambda F: F[rule]) if rule == "S-res" else (lambda F: F[("base", rule)])
        gap[rule] = sign_row(f"V1 vs b* ({rule})", g(fV), g(fB))
    return T, I, gap


def supported(rows):
    return all(r["v"] == "지지" for r in rows)


def adoption(R, T):
    net = {X: int(R[X]["f"][("base", "R-adapt")].sum() - R[X]["f"][("base", "R32")].sum()) for X in PRIORS}
    if all(supported(T[("H6b", X)]) and net[X] <= NET_MAX for X in PRIORS):
        return "R-adapt", net
    if all(supported(T[("H6a", X)]) for X in PRIORS):
        return "R32", net
    return "후보 없음", net


# ----------------------------------------------------------------------------- report
def fmt_row(r):
    return (f"  {r['name']:<24} fail {r['fx']:>4} vs {r['fy']:>4}   a:b = {r['a']}:{r['b']}  net {r['a'] - r['b']:+d}  "
            f"n_d {r['a'] + r['b']}  p = {r['p']:.3g}  MDD@n_d {r['mdd'] if r['mdd'] is not None else 'n/a'}  -> {r['v']}")


def report(cell, snr, n, judging, R, T, I, gap, late, genie16):
    L = [C.header("D2", extra=[
        "content     : review_next P3 judgement (NEXT_EXPERIMENTS_P3 v2, frozen d7e404ff) -- loop rules applied offline",
        f"point       : {cell} {snr:+g} dB  trials {C.P3_SKIP0}..{C.P3_SKIP0 + n - 1}  n = {n}  -> "
        + ("JUDGING point" if judging else "REPORT-ONLY point (no verdict is a judgement here)"),
        f"runs        : 32-iteration conf/raw_{TAG_P3} (r_t), 16-iteration reference conf/raw_{TAG_REF}; acceptance PASSED "
        f"(chunk plan, run params, checkpoint, b* kron K={BSTAR_K}, N_train {NTRAIN}, variant loop constants, r_t, "
        f"iterations 1..16 bit-identical to the reference)",
        f"checkpoint  : {CKPT} (last-EMA, BEST_WEIGHTS_UNAVAILABLE)",
        "house test  : exact two-sided sign test on discordant pairs, p < 0.05; n_d < 6 -> UNDECIDED; a:b = only-X : only-Y failures"])]
    w = L.append
    w(f"\nR5-genie failures @16 (reference run): {genie16}/{n}")
    w("\n## failures per rule (blocks; divergence = guardH rule on nmse[:, :t], counted, never removed)")
    w(f"  {'prior':<6} {'run':<5} {'R16':>5} {'R32':>5} {'R-adapt':>8} {'mean t':>7} {'max t':>6} {'raised':>7} "
      f"{'div16':>6} {'div32':>6} {'divAd':>6}")
    for X in PRIORS:
        f, d = R[X]["f"], R[X]["div"]
        for r in RUNS:
            st = R[X]["stop"][r]
            w(f"  {X:<6} {r:<5} {f[(r, 'R16')].sum():>5} {f[(r, 'R32')].sum():>5} {f[(r, 'R-adapt')].sum():>8} "
              f"{st.mean():>7.2f} {st.max():>6} {R[X]['raised'][r]:>7} {d[(r, 'R16')].sum():>6} {d[(r, 'R32')].sum():>6} "
              f"{d[(r, 'R-adapt')].sum():>6}")
        for k in ("S-res", "S-res|literal", "S-conf", "S-conf|literal", "oracle"):
            note = {"S-conf": " (report only)", "S-conf|literal": " (report only)",
                    "oracle": " (true bits, not an arm; div = all three runs diverged)"}.get(k, "")
            w(f"  {X:<6} {k:<15} R32-of-chosen fail {f[k].sum():>5}   div {d[k].sum():>5}{note}")
        w(f"  {X:<6} readings: blocks where S-res PRIMARY != LITERAL choice {int(np.sum(R[X]['sel']['S-res'] != R[X]['sel']['S-res|literal']))}, "
          f"S-conf {int(np.sum(R[X]['sel']['S-conf'] != R[X]['sel']['S-conf|literal']))}; b05 == fb05 < base on r_32 "
          f"{R[X]['order_tie']} blocks, of which b05/fb05 differ at 32 on {R[X]['order_matters']} (only these depend on "
          f"the b05-before-fb05 order)")
        for v in ("b05", "fb05"):
            if R[X]["raised"][v]:
                w(f"  {X:<6} {v}: {R[X]['raised'][v]} trials raised in the 32-iteration run -> R16 UNKNOWN (no reference run "
                  f"for variants), counted as failures; see the H7 sensitivity line")
    if any(late.values()):
        w(f"  trials that raised only in the 32-iteration run (base R16 taken from the reference): {late}")
    w("\n## pre-registered tests (per prior; X vs Y, 'fail X vs Y', a = only X fails)")
    for key in ("H6a", "H6b", "H7-b05", "H7-fb05", "H8", "H8|literal"):
        for X in PRIORS:
            rows = T[(key, X)]
            tag = ""
            if key.startswith("H8"):
                tag = f"  => {key} " + ("지지" if supported(rows) else "지지 아님") + f" ({X})"
                if key == "H8|literal":
                    same = supported(rows) == supported(T[("H8", X)])
                    tag += "  [reading check: same verdict as PRIMARY]" if same else "  [READING-DEPENDENT: differs from PRIMARY]"
            w(f"{key} [{X}]{tag}")
            for r in rows:
                w(fmt_row(r))
            if key.startswith("H7") and R[X]["raised"][key[3:]]:
                v = key[3:]
                ok = ~R[X]["raised_mask"][v]
                w("  sensitivity (not a verdict): " + fmt_row(sign_row(f"{v} R16 vs base R16 excl. raised",
                                                                       R[X]["f"][(v, "R16")][ok], R[X]["f"][("base", "R16")][ok])).strip())
    w("\n## §2.4 prior-gain separation: d = (fV1^rule - fV1^R16) - (fb*^rule - fb*^R16), sign test on sign(d)")
    for rule, (pos, neg, p, s) in I.items():
        chk = ""
        if rule == "S-res|literal":
            chk = "  [reading check: same statement as PRIMARY]" if s == I["S-res"][3] else "  [READING-DEPENDENT]"
        w(f"  {rule:<14} #d>0 {pos}  #d<0 {neg}  n_d {pos + neg}  p = {p:.3g}  -> {s}{chk}")
    w("  report beside it (does not replace it): V1 vs b* gap per rule")
    for rule, r in gap.items():
        w(fmt_row(r))
    rule, net = adoption(R, T)
    w("\n## §3 adoption (" + ("judging point" if judging else "REPORT-ONLY point: printed for completeness, NOT an adoption") + ")")
    w(f"  net(R-adapt - R32): " + "  ".join(f"{X} {net[X]:+d}" for X in PRIORS) + f"  (<= +{NET_MAX} required)")
    w(f"  -> test-set confirmation candidate: {rule if judging else 'n/a (report-only point)'}")
    w("\n## selection frequency (each row split by that rule's own outcome at 32: the R32 of the run it chose)")
    for X in PRIORS:
        for nm in ("S-res", "S-res|literal", "S-conf", "S-conf|literal"):
            s, fs = R[X]["sel"][nm], R[X]["f"][nm]
            w(f"  {X:<6} {nm:<15} " + "  ".join(f"{r}: {int(np.sum(s == i))} (fail {int(np.sum((s == i) & (fs == 1)))} / "
                                               f"ok {int(np.sum((s == i) & (fs == 0)))})" for i, r in enumerate(RUNS)))
    w("\n## cost (report only): iterations and real-path block time, scaled from complexity_moduleH_ep.txt "
      "(16-iteration block at C2 -3 dB: V1 1006 ms, b* 754 ms) in proportion to the iteration count")
    for X in PRIORS:
        per = MS16[X] / T_REF
        ta = R[X]["stop"]["base"]
        w(f"  {X:<6} R16 {T_REF} it = {MS16[X]:.0f} ms | R32 {T_MAX} it = {per * T_MAX:.0f} ms | R-adapt mean {ta.mean():.2f} it "
          f"(max {ta.max()}) = {per * ta.mean():.0f} ms | S-res / S-conf 3 x {T_MAX} it = {per * 3 * T_MAX:.0f} ms")
    return "\n".join(L) + "\n"


def judge(cell, snr, n, judging):
    arms3 = [ARM[X][r] for X in PRIORS for r in RUNS]
    p3, m3 = load(TAG_P3, cell, snr, n, T_MAX, arms3, rt=True)
    ref, _ = load(TAG_REF, cell, snr, n, T_REF, [BASE[X] for X in PRIORS] + [GENIE])
    check_variants(m3)
    late = check_bit(p3, ref)
    R = apply_rules(p3, ref)
    T, I, gap = tests(R)
    txt = report(cell, snr, n, judging, R, T, I, gap, late, int(fail_at(ref[GENIE], T_REF).sum()))
    name = f"p3_rules_{cell}_{'m' if snr < 0 else 'p'}{abs(int(snr))}"
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name + ".txt"), "w") as fh:
        fh.write(txt)
    np.savez_compressed(os.path.join(OUT, name + ".npz"), trial=C.P3_SKIP0 + np.arange(n),
                        **{f"{X}|{k if isinstance(k, str) else '|'.join(k)}": v for X in PRIORS
                           for k, v in R[X]["f"].items()},
                        **{f"{X}|stop|{r}": R[X]["stop"][r] for X in PRIORS for r in RUNS},
                        **{f"{X}|sel|{k}": v for X in PRIORS for k, v in R[X]["sel"].items()},
                        **{f"{X}|div|{k if isinstance(k, str) else '|'.join(k)}": v for X in PRIORS
                           for k, v in R[X]["div"].items()})
    print(txt + f"# -> {os.path.join(OUT, name)}.txt / .npz", flush=True)


# ----------------------------------------------------------------------------- selftest
def selftest():
    inf, nan = np.inf, np.nan
    r = np.full((5, 32), 1.0)
    r[0, 14:16] = 5e-4                                          # r_15, r_16 < tol -> stop 16
    r[1, 15] = 5e-4; r[1, 16] = 5e-4                           # r_15 >= tol, r_16, r_17 < tol -> stop 17
    r[2, 15] = 5e-4                                            # isolated dip -> never -> 32
    r[3, :] = nan                                              # raised row -> +inf -> 32
    r[4, 30:32] = 1e-4; r[4, 31] = inf                         # r_32 = +inf -> no stop at 32 -> 32
    r[4, 29:31] = 1e-4                                         # r_30, r_31 < tol -> stop 31
    assert list(radapt_stop(r)) == [16, 17, 32, 32, 31], radapt_stop(r)
    xs = np.array([[1, 1, 2], [3, 1, 2], [inf, inf, inf], [nan, 2, 1], [2, 1, 1], [inf, 0, 0], [0.4, 1e-6, 1e-6]], float)
    assert list(select(xs)) == [0, 1, 0, 2, 1, 1, 1], select(xs)                          # PRIMARY (§5.1)
    assert list(select(xs, literal=True)) == [0, 1, 0, 2, 0, 0, 0], select(xs, literal=True)
    fV16, fV, fB16, fB = (np.array(x) for x in ([1, 1, 0, 1, 0], [0, 1, 0, 1, 1], [1, 1, 1, 0, 0], [0, 0, 1, 0, 0]))
    # d = (fV - fV16) - (fB - fB16) = [-1-(-1), 0-(-1), 0-0, 0-0, 1-0] = [0, 1, 0, 0, 1]
    assert interaction(fV, fV16, fB, fB16)[:2] == (2, 0)
    assert verdict(2, 3)[0] == "UNDECIDED" and verdict(3, 12)[0] == "지지" and verdict(12, 3)[0].startswith("반대")
    assert verdict(6, 9)[0] == "판정 불가"
    A = dict(nmse=np.array([[0.1, 20.0, 0.1], [0.1, 0.1, nan], [0.1] * 3]), failed=np.array([0, 0, 1.0]))
    assert list(diverged_upto(A, np.array([1, 2, 1]))) == [0, 0, 1] and list(diverged_upto(A, 3)) == [1, 1, 1]
    A = dict(blk_err=np.array([[0, 1], [nan, nan], [1, 0]], float), failed=np.array([0, 1.0, 0]))
    assert list(fail_at(A, 2)) == [1, 1, 0]
    print("[p3_rules selftest] OK: R-adapt stop, S-res tie/inf rule, §2.4 sign convention, verdict mapping, divergence, raised")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    selftest()
    if a.selftest:
        return 0
    bad = []
    for cell, snr, n, judging in POINTS:
        try:
            judge(cell, snr, n, judging)
        except Invalid as ex:
            bad.append(f"{cell} {snr:+g} dB: INVALID -- {ex}")
            print(f"[p3_rules] {bad[-1]}", flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
