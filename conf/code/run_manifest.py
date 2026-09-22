"""(review_next, handoff §13) run_manifest.json for one raw directory: everything a reader needs to know what
was ACTUALLY run -- git commit, config hash, checkpoint identity (file hash, stored epoch, best epoch, role),
sample counts and split hashes, channel model, cells/SNRs/pilots, GMM family/K/selection rule, network, receiver
loop, dtype/device/threads/library versions, output paths.  Read-only: it opens raw/ckpt/result files, writes
ONE json next to the raw dir's tables file (results/review_next/run_manifest_<tag>.json).

    ~/miniforge3/envs/torch/bin/python conf/code/run_manifest.py --tag NR16run2 [--testbed D2]
"""
import argparse
import glob
import hashlib
import json
import os
import platform
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import common as C
import d2
import score


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--testbed", default="D2")
    a = ap.parse_args()
    raw_dir = os.path.join(C.CONF, "raw" + (f"_{a.tag}" if a.tag else ""))
    files = sorted(glob.glob(os.path.join(raw_dir, f"{a.testbed}_*.npz")))
    assert files, f"no raw files in {raw_dir}"
    points, meta, run, arms, skips, skips_end = {}, {}, {}, set(), [], []
    for f in files:
        z = np.load(f, allow_pickle=False)
        for k in z.files:
            if k.startswith("meta|"):
                meta.setdefault(k[5:], set()).add(str(z[k].item() if z[k].shape == () else z[k]))
            elif k.startswith("run|"):
                run.setdefault(k[4:], set()).add(str(z[k].item() if z[k].shape == () else z[k]))
            elif "|" in k and k.split("|")[1] == "blk_err":
                arms.add(k.split("|")[0])
        sk, nn = os.path.basename(f).rsplit("_skip", 1)[1][:-4].split("_n")
        skips.append(int(sk)); skips_end.append(int(sk) + int(nn))
        pt = os.path.basename(f).rsplit("_skip", 1)[0]
        points[pt] = points.get(pt, 0) + int(z["R5-genie|blk_err"].shape[0])      # trials in this chunk, once
    one = lambda s: sorted(s)[0] if len(s) == 1 else sorted(s)
    ck = one(meta.get("stagec_ckpt", {"(none)"}))
    ckpt = None
    if isinstance(ck, str) and os.path.isfile(ck):
        cid = score.ckpt_identity(ck)
        st = __import__("torch").load(ck, map_location="cpu", weights_only=False)
        ckpt = dict(path=ck, sha256_16=cid["sha256_16"], stored_epoch=cid["epoch"], best_epoch=cid["best_epoch"],
                    best_val=cid["best_val"], role=cid["role"],
                    evaluated_weights=("last-epoch EMA (best weights NOT stored: BEST_WEIGHTS_UNAVAILABLE)"
                                       if cid["role"] == "legacy-last" and cid["epoch"] != cid["best_epoch"]
                                       else f"{cid['role']} EMA @{cid['epoch']}"),
                    best_pt=(score.best_ckpt_path(ck) if os.path.isfile(score.best_ckpt_path(ck)) else None),
                    hp=st["hp"], params=score.n_params(score.make_model(st["rung"], st["hp"], st["Nr"], st["Nt"])),
                    rung=st["rung"], attempt=int(st["attempt"]), Nr=int(st["Nr"]), Nt=int(st["Nt"]),
                    split_hash=st.get("split_hash"), sigma_tag=st.get("sigma_tag", ""),
                    train_epochs=int(st["epoch"]), stopped_by=st.get("stopped_by", "(legacy: not recorded)"),
                    train_wall_sec=float(st.get("wall_sec", float("nan"))), train_device=st.get("device"),
                    val_frac=score.VAL_FRAC, seeds=dict(split=score.SEED_SPLIT, val=score.SEED_VAL,
                                                       train=score.SEED_TRAIN, gate=score.SEED_GATE))
    ntrain = float(one(meta.get("ntrain", {"nan"})))
    cells = sorted({p.split("_")[1] for p in points})
    man = dict(
        manifest_version=1, written=time.strftime("%Y-%m-%d %H:%M:%S %Z"), git_commit=C.git_commit(),
        result_tag=a.tag, testbed=a.testbed, raw_dir=raw_dir, n_raw_files=len(files),
        config_hash=hashlib.sha256(json.dumps(dict(sorted((k, sorted(v)) for k, v in run.items())) | dict(
            cells=cells, ntrain=ntrain, iters=C.N_ITER), sort_keys=True).encode()).hexdigest()[:16],
        code_hashes=dict(Demo=C.demo_hashes(), conf_code={f: sha16(os.path.join(C.CONF, "code", f)) for f in
                                                          ("runner.py", "arms.py", "score.py", "common.py", "d2.py",
                                                           "analysis.py") if os.path.isfile(os.path.join(C.CONF, "code", f))}),
        channel_model=dict(testbed=a.testbed, prior=one(meta.get("prior", set()) or {"S2"}),
                           description=("D2 sparse specular: L ~ Unif{%d..%d} per block, continuous AoA/AoD (S2: +-pi/3), "
                                        "|alpha_l| = sqrt(p_l) deterministic, p_l ∝ exp(-l/%.1f), psi_l ~ Unif[0,2pi), "
                                        "H = sqrt(Nr Nt) sum_l alpha_l a_r a_t^H" % (d2.L_MIN, d2.L_MAX, d2.TAU))
                           if a.testbed == "D2" else "D1 grid GMM (see 05_SPEC)"),
        cells={c: dict(C.CELLS[c]) for c in cells}, points={k: v for k, v in sorted(points.items())},
        trial_stream=dict(rule=f"default_rng([{C.SEED}, TBID[testbed], PID[prior], Nr, T, Tp, int(snr)+100])",
                          skip_min=min(skips), skip_max_end=max(skips_end),
                          split=("DEVELOPMENT set (review_next, trials >= %d)" % C.DEV_SKIP0 if min(skips) >= C.DEV_SKIP0
                                 else "TEST set (trials from 0; paired across arms)")),
        run_params={k: one(v) for k, v in sorted(run.items()) if k != "skip"} | dict(n_chunks=len(files)),
        receiver=dict(outer_iterations=C.N_ITER, beta=C.BETA, t_in_bigamp=C.T_IN, n_inner_routeA=1,
                      dtype="complex128/float64", device="CPU, one thread per worker", code=f"conv ({C.GENS[0]},{C.GENS[1]})_8 nu={C.NU} terminated, QPSK"),
        gmm=dict(bstar=one(meta.get("bstar", {"?"})), kron_K=one(meta.get("kron_K", {"?"})), ntrain=ntrain,
                 selection="validation log-likelihood over the pre-registered K grid (BLER never consulted)",
                 fits_dir=os.path.join(C.CONF, "results", f"gmm_fits_{a.testbed}_{a.tag}"),
                 em_sec=one(meta.get("em_sec", {"?"}))),
        sample_counts=dict(train_channels=int(ntrain) if ntrain == ntrain else None,
                           score_train=int(round((1 - score.VAL_FRAC) * ntrain)) if ntrain == ntrain else None,
                           score_val=int(round(score.VAL_FRAC * ntrain)) if ntrain == ntrain else None,
                           test_trials_per_point=sorted(set(points.values()))),
        stagec_checkpoint=ckpt, stagec_status=one(meta.get("stagec_status", {"(none)"})),
        stagec_gate=one(meta.get("stagec_gate", {"(none)"})), stagec_ckpt_id=one(meta.get("stagec_ckpt_id", {"(none)"})),
        arms=sorted(arms),
        versions=dict(python=platform.python_version(), numpy=np.__version__, torch=__import__("torch").__version__,
                      host=platform.node(), cpu_count=os.cpu_count()),
        output_paths=dict(tables=os.path.join(C.CONF, "results", f"tables_{a.testbed}_{a.tag}.txt"),
                          guard=os.path.join(C.CONF, "results", f"guard_{a.testbed}_{a.tag}.txt"),
                          log=os.path.join(C.CONF, "logs", f"run_{a.testbed}_{a.tag}.log")),
    )
    out_dir = os.path.join(C.CONF, "results", "review_next")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"run_manifest_{a.tag}.json")
    with open(out, "w") as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: man[k] for k in ("git_commit", "result_tag", "config_hash", "n_raw_files", "arms")}, ensure_ascii=False))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
