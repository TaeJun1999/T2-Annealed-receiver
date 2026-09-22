"""(review_next NEXT_EXPERIMENTS §2.5 H0, §3.1 A1) Control / phase-augmentation retrains under NEW tags.

Default (no flags) = the §2.5 H0 control, unchanged: retrain of the headline D2 score prior with the same
recipe, same rung label (-> same training seed), same split and N_train as ckpt/d2sx_N160000_a1.pt, but with
the P0-fixed score.train, so <ckpt>_best.pt (best-epoch weights) is stored next to the last-epoch file.
§3.1 A1 variants (all opt-in):
  --testbed D1   the D1 sibling: rung SX<N>, prior S, 8x4, frozen hp = the run_samplecx.py call that trained
                 ckpt/sx_N<N>_D1.pt (same rung label -> same training seed at --attempt 1)
  --phase-aug    score.train(phase_aug=True) (§3.1 구현); tag prefix aug_ instead of ctrl_
  --gate         D1 only: after training, score.gates_D1 on <ckpt>_best.pt with the arguments of the existing
                 D1 gate (run_samplecx.py / runner cmd_gate: prior S, n_eval 512, n_jac 64, stream 10), GA-GD
                 unrelaxed (04_SPEC §5) -> results/review_next/gate_<tag>.txt (never the existing gate files)
  --dry-run      resolve and check everything (tag, paths, legacy sibling recipe, phase_aug support), train nothing
Tag = <ctrl|aug>_[<testbed>_]N<N>_a<attempt>; the testbed is left out for D2 so the running §2.5 control keeps
its name ctrl_N160000_a1.  Before training, the legacy sibling checkpoint (if it exists) is read and its
rung/prior/testbed/Nr/Nt/hp must equal what is about to be trained -- else the run refuses to start.
Not a re-run of a pre-registered checkpoint: writes only under conf/ckpt_review_next/, conf/logs/review_next/,
conf/results/review_next/.  Bit-identity with a legacy checkpoint is NOT expected (GPU nondeterminism, and the
initial weights are unseeded -- §0 "초기값 차이 포함").  One training per process.

    CUDA_VISIBLE_DEVICES=<free> ~/miniforge3/envs/torch/bin/python conf/code/train_ctrl.py --ntrain 160000 --attempt 1
    CUDA_VISIBLE_DEVICES=<free> ~/miniforge3/envs/torch/bin/python conf/code/train_ctrl.py --testbed D1 --phase-aug --gate
    CUDA_VISIBLE_DEVICES=<free> ~/miniforge3/envs/torch/bin/python conf/code/train_ctrl.py --ntrain 10000 --attempt 2 [--phase-aug]
"""
import argparse
import hashlib
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import common as C
import score

HP = dict(arch="dit", param="vp", domain="angle", lr=0.002238046051591068, ema=0.999,
          batch=256, emb=256, width=64, depth=6, heads=8, patch=1)  # = run_d2_sx.HP = run_samplecx.HP (04_SPEC §6)
NR, NT = 8, 4
# rung label (fixes the training seed: SEED_TRAIN + _rung_ix(rung)*17 + attempt) and legacy sibling per testbed
TB = {"D2": dict(rung="D2SX{n}", sib="d2sx_N{n}_a{k}.pt"),     # = run_d2_sx.py
      "D1": dict(rung="SX{n}", sib="sx_N{n}_D1.pt")}           # = run_samplecx.py (always attempt 1)
GATE_KW = dict(n_eval=512, n_jac=64, stream=10)                # = run_samplecx.py / runner cmd_gate (defaults)
GATE_COLS = ("nu", "sigma", "GA", "GB", "GC", "GD", "GD_trace", "herm_res",
             "nmse_hat", "nmse_star", "alpha_hat", "alpha_star")


def check_sibling(path, want, attempt):
    """The legacy checkpoint whose recipe this run must reproduce.  A differing rung label would silently
    change the training seed; a differing hp/prior would train a different model under a 'same recipe' tag.
    The D1 sibling is always attempt 1, so a D1 run at another attempt shares the recipe but NOT the seed."""
    if not os.path.exists(path):
        print(f"[ctrl] no legacy sibling {path} -- recipe NOT cross-checked", flush=True)
        return
    st = torch.load(path, map_location="cpu", weights_only=False)
    bad = {k: (st.get(k), v) for k, v in want.items() if st.get(k) != v}
    if bad:
        raise SystemExit(f"[ctrl] recipe differs from legacy sibling {path} (stored, wanted): {bad}")
    sa = st.get("attempt")
    print(f"[ctrl] legacy sibling {os.path.relpath(path, C.CONF)} (attempt {sa}): {'/'.join(want)} identical"
          + ("" if sa == attempt else f"; this run is attempt {attempt} -> training seed NOT the sibling's"),
          flush=True)


def write_gate(G, best, tag, res, dev, out):
    idn = score.ckpt_identity(best)
    tol = score.GATE_TOL
    L = [C.header("D1", extra=[
        "content     : NEXT_EXPERIMENTS §3.1 step 1 -- the pre-registered gates GA-GD (04_SPEC §5, unrelaxed) "
        "on a review_next D1 sibling",
        f"checkpoint  : {os.path.relpath(best, C.CONF)}  sha256[:16] {idn['sha256_16']}  role {idn['role']}  "
        f"epoch {idn['epoch']} (= last file best_epoch {res['best_epoch']}: {idn['epoch'] == res['best_epoch']})",
        f"training    : tag {tag}  rung {G.get('rung')} attempt {G.get('attempt')}  "
        f"phase_aug {res.get('phase_aug', False)}  {res['epochs']} ep  stopped_by {res['stopped_by']}",
        f"gate call   : score.gates_D1(prior={G['prior']}, n_eval={G['n_eval']}, n_jac={G['n_jac']}, "
        f"stream={GATE_KW['stream']}, device={dev}) = run_samplecx.py / runner cmd_gate",
        "judgement   : A1 continues only on PASS (§3.1 step 1); no BLER is looked at before this verdict."]),
        C.D1_WARNING, "", f"    hp          {G['hp']}"]
    for g in ("GA", "GB", "GC", "GD"):
        L.append(f"    {g:<9} {G[g]:13.5e}   <= {tol[g]:<9g}  {'PASS' if G[g] <= tol[g] else 'FAIL'}")
    L += [f"    {'GD_trace':<9} {G['GD_trace']:13.5e}   relative error of tr(J)/N -- REPORTED, NOT the gate",
          f"    VERDICT   {'PASS' if G['passed'] else 'FAIL'}   (PASS = GA and GB and GC and GD, 04_SPEC §5)",
          f"    NOTE      {score.GA_NOTE}", "",
          "    per sigma grid point (FROZEN A4 grid; GD = full-matrix J_rel_fro)",
          "    " + f"{'k':>3} " + " ".join(f"{c:>13}" for c in GATE_COLS) + f" {'n_jac':>6}"]
    for r in G["per_sigma"]:
        L.append(f"    {r['k']:>3} " + " ".join(f"{float(r[c]):13.5e}" for c in GATE_COLS) + f" {r['n_jac']:>6}")
    with open(out, "w") as f:
        f.write("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--testbed", choices=sorted(TB), default="D2")
    ap.add_argument("--ntrain", type=int, default=160000)
    ap.add_argument("--attempt", type=int, default=1)
    ap.add_argument("--phase-aug", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if a.gate and a.testbed != "D1":
        ap.error("--gate: GA-GD exist only on D1 (04_SPEC §5); D2 has GB' only (§6)")
    kw = {}
    if a.phase_aug:                                       # never train an un-augmented model under an aug_ tag
        if "phase_aug" not in inspect.signature(score.train).parameters:
            raise SystemExit("[ctrl] --phase-aug: the loaded score.train has no phase_aug kwarg "
                             "(NEXT_EXPERIMENTS §6 선행 'score.train(phase_aug=True)' missing) -- refusing to start")
        kw["phase_aug"] = True
    prior, t = C.PRIOR_OF[a.testbed], TB[a.testbed]
    tag = (f"{'aug' if a.phase_aug else 'ctrl'}_{'' if a.testbed == 'D2' else a.testbed + '_'}"
           f"N{a.ntrain}_a{a.attempt}")
    ckd, lgd = os.path.join(C.CONF, "ckpt_review_next"), os.path.join(C.CONF, "logs", "review_next")
    ck, lg = os.path.join(ckd, f"{tag}.pt"), os.path.join(lgd, f"train_{tag}.log")
    gout = os.path.join(C.CONF, "results", "review_next", f"gate_{tag}.txt")
    rung = t["rung"].format(n=a.ntrain)                   # SAME label as the legacy wrapper -> same training seed
    print(f"[ctrl] {tag}: testbed {a.testbed} prior {prior} {NR}x{NT} rung {rung} attempt {a.attempt} "
          f"phase_aug {a.phase_aug} -> {ck}" + (f", gate -> {gout}" if a.gate else ""), flush=True)
    check_sibling(os.path.join(C.CONF, "ckpt", t["sib"].format(n=a.ntrain, k=a.attempt)),
                  dict(rung=rung, prior=prior, testbed=a.testbed, Nr=NR, Nt=NT, hp=HP), a.attempt)
    if a.dry_run:
        return 0
    os.makedirs(ckd, exist_ok=True); os.makedirs(lgd, exist_ok=True)
    # initial weights come from torch's global RNG (make_model is unseeded, CHANGELOG N1): record the seed and
    # the init hash by drawing the same model on a copy of the RNG state, then restoring it for score.train.
    s0 = torch.get_rng_state()
    m0 = score.make_model(rung, HP, NR, NT)
    h0 = hashlib.sha256(b"".join(v.detach().cpu().numpy().tobytes() for _, v in sorted(m0.state_dict().items())))
    torch.set_rng_state(s0)
    print(f"[ctrl] {tag}: rung {rung} (seed as legacy), torch.initial_seed={torch.initial_seed()} "
          f"init sha256[:16]={h0.hexdigest()[:16]}"
          + (" (NOT this run's init: resuming, the weights come from the checkpoint)" if os.path.exists(ck) else "")
          + f"  -> {ck}", flush=True)
    res = score.train(rung, a.attempt, a.testbed, prior, NR, NT, device="cuda", hp=HP, resume=True,
                      ntrain=a.ntrain, max_epochs=3000, patience=20, min_epochs=200, log_path=lg, ckpt=ck,
                      verbose=False, **kw)
    print(f"[ctrl] done: {res['epochs']} ep, stopped_by={res['stopped_by']}, aborted={res['aborted']}, "
          f"best val {res['val_loss']:.6e} @{res['best_epoch']}, best_ckpt={res['best_ckpt']}, "
          f"{res['wall_sec']:.0f}s", flush=True)
    if not res["best_ckpt"]:
        print("[ctrl] BEST_WEIGHTS_UNAVAILABLE -- no _best.pt, nothing gated", flush=True)
        return 1 if a.gate else 0
    b, l = score.ckpt_identity(res["best_ckpt"]), score.ckpt_identity(ck)
    ok = b["epoch"] == l["best_epoch"]
    pa = torch.load(res["best_ckpt"], map_location="cpu", weights_only=False).get("phase_aug", False)
    print(f"[ctrl] best file epoch {b['epoch']} == last file best_epoch {l['best_epoch']}: {ok}  "
          f"(best sha {b['sha256_16']}, last sha {l['sha256_16']}), stored phase_aug {pa}", flush=True)
    if not a.gate:
        return 0
    if res["aborted"] or not ok or pa != a.phase_aug:
        print(f"[ctrl] NOT gated: aborted={res['aborted']} best/last identity={ok} "
              f"stored phase_aug {pa} vs requested {a.phase_aug}", flush=True)
        return 1
    dev = "cuda" if torch.cuda.is_available() else "cpu"  # score.train's own fallback
    G = score.gates_D1(res["best_ckpt"], NR, NT, prior=prior, device=dev, **GATE_KW)
    os.makedirs(os.path.dirname(gout), exist_ok=True)
    write_gate(G, res["best_ckpt"], tag, res, dev, gout)
    print(f"[ctrl] gate {tag}: GA {G['GA']:.3e} GB {G['GB']:.5f} GC {G['GC']:.5f} GD {G['GD']:.5f} "
          f"gate_score {score.gate_score(G):.4f} -> {'PASS' if G['passed'] else 'FAIL'}  ({gout})", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
