"""conf/code/a1c5_report.py -- helpers of NEXT_EXPERIMENTS_A1C5 (v2, frozen ad32f48b).

  ckpts    §1 "쌍의 자격" + identities of the 6 checkpoints, BEFORE any of them is evaluated:
           per attempt k and kind (aug / ctrl): last file stopped_by in {patience, max_epochs}, the training log's
           "# done" line says aborted=False, _best.pt exists with role=best and epoch == last.best_epoch, rung
           D2SX160000, attempt == k, phase_aug == (kind == aug).  The a1 pair must be the registered checkpoints
           (sha256[:16] 40c55cb294340594 / e2b22673ac91ed8f).  Writes results/review_next/a1c5_ckpts.json and appends
           one line to conf/DECISIONS.md.  Exit 0 = both new pairs (a2, a3) eligible; exit 2 = not -> H9 cannot be
           judged ("판정 불가(쌍 부족)") unless the user approves attempt 4 before any evaluation.
  gbprime  report-only GB' of one checkpoint against b* = kron K=1024 @ N_train 1.6e5 (the B16e4k fits; `runner.py
           gate --testbed D2` reads the 1e4 fits and is NOT used) -> results/review_next/gbprime_<tag>.txt

    ~/miniforge3/envs/torch/bin/python conf/code/a1c5_report.py ckpts
    CUDA_VISIBLE_DEVICES=<free> ~/miniforge3/envs/torch/bin/python conf/code/a1c5_report.py gbprime --tag T --ckpt P
"""
import argparse
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np

CK = os.path.join(C.CONF, "ckpt_review_next")
OUT = os.path.join(C.CONF, "results", "review_next")
LOGS = os.path.join(C.CONF, "logs", "review_next")
A1_SHA = {"aug": "40c55cb294340594", "ctrl": "e2b22673ac91ed8f"}     # §1: the step-3 pair
RUNG, NTRAIN = "D2SX160000", 160000


def tag_of(kind, k):
    return f"review_next_A1C5_{kind}_a{k}"


def check_one(kind, k):
    import torch
    import score
    last = os.path.join(CK, f"{kind}_N{NTRAIN}_a{k}.pt")
    best = score.best_ckpt_path(last)
    r = dict(kind=kind, attempt=k, tag=tag_of(kind, k), last=last, best=best, why=[])
    if not (os.path.isfile(last) and os.path.isfile(best)):
        r["why"].append("last or _best.pt missing")
        r["eligible"] = False
        return r
    st = torch.load(last, map_location="cpu", weights_only=False)
    bid, lid = score.ckpt_identity(best), score.ckpt_identity(last)
    log = os.path.join(LOGS, f"train_{kind}_N{NTRAIN}_a{k}.log")
    done = [l for l in open(log, errors="replace") if l.startswith("# done")] if os.path.isfile(log) else []
    m = re.search(r"aborted=(\w+)", done[-1]) if done else None
    r.update(sha256_16=bid["sha256_16"], best_epoch=bid["epoch"], best_role=bid["role"], last_epoch=lid["epoch"],
             last_best_epoch=lid["best_epoch"], last_sha256_16=lid["sha256_16"], stopped_by=st.get("stopped_by"),
             aborted=(m[1] if m else "no '# done' line"), rung=st.get("rung"), ckpt_attempt=st.get("attempt"),
             phase_aug=bool(st.get("phase_aug")), best_val=bid["best_val"])
    for ok, why in ((r["stopped_by"] in ("patience", "max_epochs"), f"stopped_by={r['stopped_by']}"),
                    (r["aborted"] == "False", f"aborted={r['aborted']}"),
                    (r["best_role"] == "best", f"best role={r['best_role']}"),
                    (r["best_epoch"] == r["last_best_epoch"], f"best epoch {r['best_epoch']} != last.best_epoch {r['last_best_epoch']}"),
                    (r["rung"] == RUNG, f"rung={r['rung']}"), (r["ckpt_attempt"] == k, f"attempt={r['ckpt_attempt']}"),
                    (r["phase_aug"] == (kind == "aug"), f"phase_aug={r['phase_aug']}")):
        if not ok:
            r["why"].append(why)
    if k == 1 and r["sha256_16"] != A1_SHA[kind]:
        r["why"].append(f"a1 sha {r['sha256_16']} != registered {A1_SHA[kind]}")
    r["eligible"] = not r["why"]
    return r


def cmd_ckpts(a):
    rows = [check_one(kind, k) for k in (1, 2, 3) for kind in ("aug", "ctrl")]
    pair_ok = {k: all(r["eligible"] for r in rows if r["attempt"] == k) for k in (1, 2, 3)}
    h9 = pair_ok[2] and pair_ok[3]
    stamp = time.strftime("%Y-%m-%d %H:%M %Z")
    res = dict(written=stamp, git=C.git_commit(), rows=rows, pair_eligible=pair_ok, h9_judgeable=h9,
               # a1 = the REGISTERED shas (§1), never the observed ones: a replaced a1 file then fails acceptance
               expect_ckpt={r["tag"]: (A1_SHA[r["kind"]] if r["attempt"] == 1 else r.get("sha256_16")) for r in rows})
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "a1c5_ckpts.json"), "w") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1, default=str)
    for r in rows:
        print(f"{r['tag']:<28} eligible={r['eligible']}  sha256[:16]={r.get('sha256_16')}  best@{r.get('best_epoch')}  "
              f"last@{r.get('last_epoch')}  stopped_by={r.get('stopped_by')}  aborted={r.get('aborted')}  "
              f"{'; '.join(r['why'])}", flush=True)
    line = (f"\n`[{stamp}] review_next A1-C5 — 체크포인트 자격·identity (NEXT_EXPERIMENTS_A1C5 §1; 평가 전, a1c5_report.py "
            f"ckpts @{C.git_commit()}) | " + "; ".join(
                f"{r['kind']}_a{r['attempt']}: sha256[:16] {r.get('sha256_16')} (_best epoch {r.get('best_epoch')}, last "
                f"{r.get('last_epoch')}, stopped_by {r.get('stopped_by')}, aborted {r.get('aborted')}) -> "
                + ("자격 있음" if r["eligible"] else "자격 없음: " + ", ".join(r["why"])) for r in rows)
            + f". 쌍 자격 a1 {pair_ok[1]} / a2 {pair_ok[2]} / a3 {pair_ok[3]} -> H9 "
            + ("판정 가능" if h9 else "판정 불가(쌍 부족) — attempt 4 는 사용자 승인이 있을 때만, 평가 전에") + ".`\n")
    with open(os.path.join(C.CONF, "DECISIONS.md"), "a") as fh:
        fh.write(line)
    print(f"[a1c5 ckpts] pair eligible {pair_ok}; H9 judgeable = {h9}; -> a1c5_ckpts.json, DECISIONS.md", flush=True)
    return 0 if h9 else 2


def cmd_gbprime(a):
    import runner as R
    import arms as A
    import score
    R._init("B16e4k")                                              # A.D2_FITS -> conf/results/gmm_fits_D2_B16e4k
    hp, _, llv, bstar, kron_K = A.module_h_priors("D2", "S2", 8, 4, ntrain=NTRAIN)
    assert bstar == "kron" and kron_K == 1024, (bstar, kron_K)
    t0 = time.time()
    G = score.gb_prime(a.ckpt, hp["kron"], "D2", 8, 4, prior="S2", device="cuda", gmm_device="cuda")
    rows = G.get("per_sigma") or []
    cols = [c for c in ("nu", "sigma", "nmse_gmm", "nmse_model", "excess") if rows and c in rows[0]]
    cid = score.ckpt_identity(a.ckpt)
    L = [C.header("D2", extra=[
        "content     : NEXT_EXPERIMENTS_A1C5 §1 report-only GB' (04_SPEC §6): held-out denoising NMSE, learned prior vs "
        "GMM b* on the same sigma grid -- NOT used for any judgement",
        f"checkpoint  : {a.ckpt}  sha256[:16]={cid['sha256_16']} epoch={cid['epoch']} best_epoch={cid['best_epoch']} role={cid['role']}",
        f"GMM b*      : kron K={kron_K} @ N_train {NTRAIN} (gmm_fits_D2_B16e4k), validation ll {llv.get('kron', float('nan')):.4f}",
        f"n_eval      : {G.get('n_eval')}  device cuda (GMM posterior on cuda, checked against the CPU loop by gb_prime)  "
        f"wall {time.time() - t0:.0f} s"]),
        f"worst excess (learned vs GMM) = {float(G.get('worst_excess', float('nan'))):+.4%}", str(G.get("note", "")), "",
        f"{'k':>3} " + " ".join(f"{c:>13}" for c in cols)]
    L += [f"{int(r.get('k', i)):>3} " + " ".join(f"{float(r.get(c, np.nan)):13.5e}" for c in cols) for i, r in enumerate(rows)]
    p = os.path.join(OUT, f"gbprime_{a.tag}.txt")
    with open(p, "w") as fh:
        fh.write("\n".join(L) + "\n")
    print("\n".join(L[-len(rows) - 4:]) + f"\n-> {p}", flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ckpts")
    g = sub.add_parser("gbprime")
    g.add_argument("--tag", required=True)
    g.add_argument("--ckpt", required=True)
    a = ap.parse_args()
    if a.cmd == "ckpts":
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        return cmd_ckpts(a)
    return cmd_gbprime(a)


if __name__ == "__main__":
    sys.exit(main())
