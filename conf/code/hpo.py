"""conf/code/hpo.py -- hyper-parameter optimisation over the score-model design space.

*** THIS IS NOT PART OF THE PRE-REGISTERED LADDER. ***
The ladder (04_SPEC_diffusion.md §4, rungs L1-L6, 18 attempts) is a FINISHED, already-reported result and
nothing here modifies it.  Its point was to try a fixed, pre-declared sequence of models under gates frozen
before any model existed.  Its weakness is sample size: three attempts per rung, varying only lr / width /
depth / EMA, is thin evidence for a statement like "conv beats U-Net".  This module answers that by
searching the space properly.  The two are reported SEPARATELY and never merged
(conf/results/hpo_*.txt vs conf/LADDER.md + conf/results/gate_D1.txt).

Integrity constraints, all of them inherited unchanged:
  * OBJECTIVE = the pre-registered GATE SCORE, never BLER (01_RULES §5).  gate_score = max_g G[g]/tol[g]
    over GA..GD with the frozen tolerances, so "better" means "closer to passing the gates that were
    fixed before any of this existed".
  * IDENTICAL DATA BUDGET: the same 1e4 channel samples the GMM fit received, the same 9:1 split, the same
    frozen sigma grid (04_SPEC §2-3).  HPO gets no extra data and no extra samples.
  * GATE-OVERFITTING GUARD: the search scores trials on held-out stream 11.  The reported gate uses
    stream 10.  A few hundred trials tuned against stream 11 therefore cannot inflate the number we
    report, and the winner is RE-TRAINED at the full ladder budget and RE-GATED on stream 10 before any
    of it counts.  Without this split, searching N configs against the reported set is just N-fold
    multiple testing on the thing being reported.
  * Every trial is logged, including failures and pruned trials (conf/results/hpo_trials.csv).

Usage
  python hpo.py search  --trials 300 --gpus 0 1 2 3 4 5      # parallel workers, one per GPU
  python hpo.py report                                        # study -> conf/results/hpo_D1.txt
  python hpo.py final   --top 5                               # retrain+regate the best on stream 10
"""
import argparse
import csv
import os
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import common as C            # noqa: E402
import score                  # noqa: E402

STORAGE = "sqlite:///" + os.path.join(C.CONF, "results", "hpo_D1.db")
STUDY = "conf_score_D1_8x4"
TRIALS_CSV = os.path.join(C.CONF, "results", "hpo_trials.csv")
STRAT_CSV = os.path.join(C.CONF, "results", "hpo_strat_trials.csv")
CKPT_DIR = os.path.join(C.CONF, "ckpt_hpo")
LOG_DIR = os.path.join(C.CONF, "logs", "hpo")

SEARCH_STREAM, REPORT_STREAM = 11, 10          # see GATE-OVERFITTING GUARD above
NR, NT, PRIOR, TESTBED = 8, 4, "S", "D1"

# Search-phase budget: shorter than a ladder attempt because it is a SEARCH, not an attempt.  The winner is
# retrained at the full ladder budget in `final`, so nothing reported ever rests on the short budget.
S_MAX_EPOCH, S_PATIENCE, S_MIN_EPOCH = 600, 15, 0
S_NEVAL, S_NJAC = 256, 24
F_MAX_EPOCH, F_PATIENCE, F_MIN_EPOCH = 3000, 20, 200
F_NEVAL, F_NJAC = 512, 64


ARCHS = ["mlp", "conv", "unet", "dit", "uvit", "adm"]


def suggest(t, fix_arch=None):
    """The design space.  Architecture and parameterisation are the axes the ladder could only sample at
    n=3; everything else is the usual continuous nuisance."""
    arch = fix_arch if fix_arch else t.suggest_categorical("arch", ARCHS)
    param = t.suggest_categorical("param", ["ve", "vp", "edm"])
    domain = t.suggest_categorical("domain", ["pixel", "angle"])
    hp = dict(arch=arch, param=param, domain=domain,
              lr=t.suggest_float("lr", 5e-5, 5e-3, log=True),
              ema=t.suggest_categorical("ema", [0.99, 0.999, 0.9995, 0.9999]),
              batch=t.suggest_categorical("batch", [128, 256, 512]),
              emb=t.suggest_categorical("emb", [64, 128, 256]))
    if arch in ("dit", "uvit"):
        hp["width"] = t.suggest_categorical("width_tf", [64, 128, 192, 256])
        hp["depth"] = t.suggest_int("depth_tf", 2, 8)
        hp["heads"] = t.suggest_categorical("heads", [2, 4, 8])
        hp["patch"] = t.suggest_categorical("patch", [1, 2])
    elif arch in ("conv", "unet", "adm"):
        hp["width"] = t.suggest_categorical("width_cnn", [16, 32, 48, 64, 96, 128])
        hp["depth"] = t.suggest_int("depth_cnn", 2, 8)
        if arch == "adm":
            hp["heads"] = t.suggest_categorical("heads_adm", [2, 4])
            hp["attn_at"] = 8
    else:                                                     # mlp
        hp["width"] = t.suggest_categorical("width_mlp", [128, 256, 384, 512])
        hp["depth"] = t.suggest_int("depth_mlp", 2, 8)
    return hp


def _row(trial_no, hp, res, G, gs, sec, err="", path=None):
    r = dict(trial=trial_no, gate_score=gs, sec=round(sec, 1), err=err,
             **{k: hp.get(k) for k in ("arch", "param", "domain", "width", "depth", "lr", "ema",
                                       "batch", "emb", "heads", "patch")})
    r.update(params=(res or {}).get("params"), epochs=(res or {}).get("epochs"),
             val_loss=(res or {}).get("val_loss"), stopped_by=(res or {}).get("stopped_by"))
    for g in ("GA", "GB", "GC", "GD", "GD_trace"):
        r[g] = (G or {}).get(g)
    path = path or TRIALS_CSV
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(r))
        if new:
            w.writeheader()
        w.writerow(r)
    return r


def objective(trial, device, fix_arch=None, csv_path=None):
    os.makedirs(CKPT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    hp = suggest(trial, fix_arch)
    tag = f"{fix_arch}_" if fix_arch else ""
    ck = os.path.join(CKPT_DIR, f"{tag}t{trial.number:05d}.pt")
    lg = os.path.join(LOG_DIR, f"{tag}t{trial.number:05d}.log")
    t0 = time.time()
    try:
        res = score.train("HPO", trial.number, TESTBED, PRIOR, NR, NT, device=device, hp=hp, resume=False,
                          max_epochs=S_MAX_EPOCH, patience=S_PATIENCE, min_epochs=S_MIN_EPOCH,
                          log_path=lg, ckpt=ck, verbose=False)
        G = score.gates_D1(ck, NR, NT, prior=PRIOR, n_eval=S_NEVAL, device=device, n_jac=S_NJAC,
                           stream=SEARCH_STREAM)
        gs = score.gate_score(G)
        _row(trial.number, hp, res, G, gs, time.time() - t0, path=csv_path)
        for k in ("GA", "GB", "GC", "GD", "GD_trace"):
            trial.set_user_attr(k, float(G[k]))
        trial.set_user_attr("params", int(res["params"]))
        trial.set_user_attr("epochs", int(res["epochs"]))
        trial.set_user_attr("val_loss", float(res["val_loss"]))
        trial.set_user_attr("ckpt", ck)
        return gs
    except Exception as ex:                                   # a crashing config is a FINDING, not a gap
        _row(trial.number, hp, None, None, float("inf"), time.time() - t0,
             err=f"{type(ex).__name__}: {ex}".replace("\n", " ")[:300], path=csv_path)
        if os.environ.get("HPO_TRACE"):
            traceback.print_exc()
        return float("inf")


def cmd_search(a):
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    dev = "cuda" if a.gpu is not None else "cpu"
    if a.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(a.gpu)
    st = optuna.create_study(study_name=STUDY, storage=STORAGE, direction="minimize",
                             load_if_exists=True,
                             sampler=optuna.samplers.TPESampler(seed=C.SEED + (a.gpu or 0), n_startup_trials=24))
    st.optimize(lambda t: objective(t, dev), n_trials=a.trials, catch=())
    print(f"[hpo] worker gpu={a.gpu} finished {a.trials} trials; study has {len(st.trials)}", flush=True)


def cmd_strat(a):
    """CONTROLLED architecture comparison: EQUAL trials per architecture, RANDOM sampling.

    The TPE search answers "what is the best configuration I can find", and it deliberately spends its
    budget where things look good -- after 720 trials it had given dit/adm ~270 trials each and unet 47.
    A "best per architecture" read off that is confounded by how many chances each architecture got.
    This command fixes the architecture, draws the REST of the space uniformly at random, and gives every
    architecture the SAME number of trials, so best-of-n and the quantiles are comparable across rows.
    Same objective, same frozen gates, same data budget, same search stream (11)."""
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    dev = "cuda" if a.gpu is not None else "cpu"
    if a.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(a.gpu)
    st = optuna.create_study(study_name=f"conf_strat_{a.arch}", storage=STORAGE, direction="minimize",
                             load_if_exists=True,
                             sampler=optuna.samplers.RandomSampler(seed=C.SEED + ARCHS.index(a.arch)))
    st.optimize(lambda t: objective(t, dev, fix_arch=a.arch, csv_path=STRAT_CSV), n_trials=a.trials, catch=())
    print(f"[strat] {a.arch}: {len(st.trials)} trials done", flush=True)


def cmd_stratreport(a):
    """Equal-n is enforced HERE, not by hoping every worker stops at the same count: trials are ordered by
    their (per-architecture) trial number and the FIRST n_eq of each architecture are used, n_eq = the
    smallest per-architecture count.  The sampler is uniform-random, so trial order is independent of
    quality and truncating to a common prefix is unbiased.  Extra trials beyond n_eq are kept in the CSV
    and reported as surplus, never silently folded into a best-of-n."""
    import collections
    rows = [r for r in csv.DictReader(open(STRAT_CSV))
            if r["gate_score"] and np.isfinite(float(r["gate_score"]))]
    order = collections.defaultdict(list)
    for r in rows:
        order[r["arch"]].append((int(r["trial"]), float(r["gate_score"])))
    raw_n = {k: len(v) for k, v in order.items()}
    n_eq = a.neq or (min(raw_n.values()) if raw_n else 0)
    by = {k: [g for _, g in sorted(v)[:n_eq]] for k, v in order.items()}
    out = os.path.join(C.CONF, "results", "hpo_strat_D1.txt")
    L = [C.header("D1", extra=[
        "content     : CONTROLLED architecture comparison -- EQUAL trials per architecture, RANDOM sampling.",
        "why         : the TPE study (hpo_D1.txt) allocates its budget adaptively, so its per-architecture",
        "              'best' is confounded by trial count.  This table is the comparable one.",
        "objective   : the pre-registered gate score, minimised.  Never BLER.  Search stream 11.",
    ]), C.D1_WARNING, "",
        f"  equal-n comparison: the first {n_eq} trials of each architecture "
        f"(collected: {dict(sorted(raw_n.items()))})", "",
        f"  {'arch':<6} {'n':>4} {'best':>8} {'p25':>8} {'median':>8} {'worst':>8}", "  " + "-" * 50]
    for k, v in sorted(by.items(), key=lambda kv: min(kv[1])):
        v = np.array(v)
        L.append(f"  {k:<6} {len(v):>4} {v.min():>8.3f} {np.percentile(v, 25):>8.3f} "
                 f"{np.median(v):>8.3f} {v.max():>8.3f}")
    ns = {k: len(v) for k, v in by.items()}
    if len(set(ns.values())) > 1 or n_eq == 0:
        L += ["", f"  WARNING: equal-n truncation failed {ns} -- best-of-n is NOT comparable."]
    if len(by) < len(ARCHS):
        L += ["", f"  WARNING: only {sorted(by)} present; {sorted(set(ARCHS) - set(by))} have no completed trials."]
    txt = "\n".join(L) + "\n"
    with open(out, "w") as f:
        f.write(txt)
    print(txt)
    print(f"[strat] -> {out}")


def _fmt(v, f="{:.4g}"):
    return "-" if v is None or (isinstance(v, float) and not np.isfinite(v)) else f.format(v)


def cmd_report(a):
    import optuna
    st = optuna.load_study(study_name=STUDY, storage=STORAGE)
    done = [t for t in st.trials if t.value is not None and np.isfinite(t.value)]
    done.sort(key=lambda t: t.value)
    out = os.path.join(C.CONF, "results", "hpo_D1.txt")
    L = [C.header("D1", extra=[
        "content     : HYPER-PARAMETER OPTIMISATION over the score-model design space.",
        "NOT the pre-registered ladder.  conf/LADDER.md and conf/results/gate_D1.txt hold that, unchanged.",
        f"objective   : the pre-registered GATE SCORE = max_g G[g]/tol[g], MINIMISED.  Never BLER (01_RULES §5).",
        f"data        : the identical N_train=1e4 samples and 9:1 split every ladder rung used (04_SPEC §2).",
        f"guard       : search scored on held-out stream {SEARCH_STREAM}; the REPORTED gate uses stream "
        f"{REPORT_STREAM}, and the winner is retrained at the full ladder budget and re-gated there.",
        f"search budget: max_epochs={S_MAX_EPOCH} patience={S_PATIENCE} n_eval={S_NEVAL} n_jac={S_NJAC}",
        f"trials      : {len(st.trials)} total, {len(done)} completed, "
        f"{len(st.trials) - len(done)} failed/infeasible (all kept, see hpo_trials.csv)",
    ]), C.D1_WARNING, "",
        "gate_score < 1.0 would mean ALL FOUR gates pass.  The ladder's best was L4 a1 at 2.109.", ""]
    L += [f"  {'#':>5} {'gate_sc':>8} {'arch':<5} {'param':<5} {'dom':<5} {'w':>4} {'d':>2} "
          f"{'lr':>9} {'ema':>7} {'bat':>4} {'params':>10} {'ep':>4} {'GB':>9} {'GC':>9} {'GD':>9}",
          "  " + "-" * 118]
    for t in done[:a.top]:
        p = t.params
        u = t.user_attrs
        L.append(f"  {t.number:>5} {t.value:>8.3f} {p.get('arch',''):<5} {p.get('param',''):<5} "
                 f"{p.get('domain',''):<5} "
                 f"{p.get('width_tf') or p.get('width_cnn') or p.get('width_mlp',''):>4} "
                 f"{p.get('depth_tf') or p.get('depth_cnn') or p.get('depth_mlp',''):>2} "
                 f"{p.get('lr',0):>9.2e} {p.get('ema',0):>7} {p.get('batch',0):>4} "
                 f"{u.get('params',0):>10,} {u.get('epochs',0):>4} "
                 f"{_fmt(u.get('GB')):>9} {_fmt(u.get('GC')):>9} {_fmt(u.get('GD')):>9}")
    # per-architecture and per-parameterisation summaries: THIS is what answers "n=3 is not enough"
    for key, lab in (("arch", "ARCHITECTURE"), ("param", "PARAMETERISATION"), ("domain", "INPUT DOMAIN")):
        L += ["", f"  best gate_score by {lab} (n = number of completed trials with that setting)",
              f"    {'value':<8} {'n':>4} {'best':>9} {'median':>9} {'p10':>9}"]
        groups = {}
        for t in done:
            groups.setdefault(t.params.get(key), []).append(t.value)
        for k, v in sorted(groups.items(), key=lambda kv: min(kv[1])):
            v = np.array(v)
            L.append(f"    {str(k):<8} {len(v):>4} {v.min():>9.3f} {np.median(v):>9.3f} "
                     f"{np.percentile(v, 10):>9.3f}")
    txt = "\n".join(L) + "\n"
    with open(out, "w") as f:
        f.write(txt)
    print(txt)
    print(f"[hpo] -> {out}   (per-trial rows: {TRIALS_CSV})")


def cmd_final(a):
    """Retrain the top-k at the FULL ladder budget and gate them on the REPORTED stream."""
    import optuna
    st = optuna.load_study(study_name=STUDY, storage=STORAGE)
    done = sorted([t for t in st.trials if t.value is not None and np.isfinite(t.value)],
                  key=lambda t: t.value)[:a.top]
    if a.rank is not None:                       # one rank per process -> parallel across GPUs, no file clash
        done = [done[a.rank]] if a.rank < len(done) else []
    dev = "cuda" if a.gpu is not None else "cpu"
    if a.gpu is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(a.gpu)
    rows = []
    for t in done:
        hp = dict(t.user_attrs.get("hp") or {})
        if not hp:                                            # rebuild from the trial's own params
            hp = _hp_from_params(t.params)
        ck = os.path.join(CKPT_DIR, f"final_t{t.number:05d}.pt")
        lg = os.path.join(LOG_DIR, f"final_t{t.number:05d}.log")
        res = score.train("HPOFINAL", t.number, TESTBED, PRIOR, NR, NT, device=dev, hp=hp, resume=False,
                          max_epochs=F_MAX_EPOCH, patience=F_PATIENCE, min_epochs=F_MIN_EPOCH,
                          log_path=lg, ckpt=ck, verbose=True)
        G = score.gates_D1(ck, NR, NT, prior=PRIOR, n_eval=F_NEVAL, device=dev, n_jac=F_NJAC,
                           stream=REPORT_STREAM)
        rows.append((t.number, hp, res, G, score.gate_score(G)))
        print(f"[final] trial {t.number}: search gate_score {t.value:.3f} -> REPORTED {score.gate_score(G):.3f} "
              f"| GB {G['GB']:.4g} GC {G['GC']:.4g} GD {G['GD']:.4g} | passed={G['passed']}", flush=True)
    out = os.path.join(C.CONF, "results",
                       f"hpo_final_r{a.rank}.txt" if a.rank is not None else "hpo_final_D1.txt")
    with open(out, "w") as f:
        f.write(C.header("D1", extra=[
            "content     : HPO winners RETRAINED at the full ladder budget and RE-GATED on the REPORTED "
            f"held-out stream {REPORT_STREAM} (the search used {SEARCH_STREAM}).",
            "This is the only HPO number that may be quoted as a gate result.",
        ]) + "\n\n" + C.D1_WARNING + "\n\n")
        for n, hp, res, G, gs in rows:
            f.write(f"=== trial {n}  gate_score {gs:.4f}  passed={G['passed']}\n    hp {hp}\n"
                    f"    epochs {res['epochs']} val {res['val_loss']:.6e} wall {res['wall_sec']:.0f}s\n"
                    + "".join(f"    {g:<9} {float(G[g]):13.5e}  <= {score.GATE_TOL.get(g, float('nan'))}\n"
                              for g in ("GA", "GB", "GC", "GD"))
                    + f"    GD_trace  {float(G['GD_trace']):13.5e}  (reported, not gated)\n\n")
    print(f"[hpo] -> {out}")


def _hp_from_params(p):
    hp = dict(arch=p["arch"], param=p["param"], domain=p["domain"], lr=p["lr"], ema=p["ema"],
              batch=p["batch"], emb=p["emb"])
    hp["width"] = p.get("width_tf") or p.get("width_cnn") or p.get("width_mlp")
    hp["depth"] = p.get("depth_tf") or p.get("depth_cnn") or p.get("depth_mlp")
    if "heads" in p:
        hp["heads"] = p["heads"]
    if "heads_adm" in p:
        hp["heads"] = p["heads_adm"]
        hp["attn_at"] = 8
    if "patch" in p:
        hp["patch"] = p["patch"]
    return hp


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["search", "report", "final", "strat", "stratreport"])
    ap.add_argument("--trials", type=int, default=50)
    ap.add_argument("--gpu", type=int, default=None)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--arch", default=None, choices=ARCHS)
    ap.add_argument("--neq", type=int, default=None, help="stratreport: trials per architecture (default: min)")
    ap.add_argument("--rank", type=int, default=None, help="final: process ONLY the k-th best trial (parallel)")
    a = ap.parse_args()
    os.makedirs(os.path.join(C.CONF, "results"), exist_ok=True)
    {"search": cmd_search, "report": cmd_report, "final": cmd_final,
     "strat": cmd_strat, "stratreport": cmd_stratreport}[a.cmd](a)
