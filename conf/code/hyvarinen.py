"""Ground-truth-free comparison of two score models on the CLAIM testbed (D2).

THE PROBLEM.  The pre-registered gates GA-GD can only be measured on D1, because D1 is the only place where
the true prior's score is available in closed form.  But D1 is also, by construction, the place where the
GMM is correctly specified.  So the admission criterion for a D2 arm is calibrated on the one testbed that
flatters the GMM.  GB' (04_SPEC §6) partially answers this -- it compares DENOISING on D2 -- but denoising
is not what the receiver consumes; D-13/D-14 consume the score and its Jacobian.

THE TOOL.  Hyvarinen's identity gives the score-matching objective WITHOUT the true score:
    J(s) = (1/2) E_p || s(x) - grad log p(x) ||^2
         =       E_p [ tr(grad s(x)) + (1/2) ||s(x)||^2 ]  +  C,      C = (1/2) E_p||grad log p||^2,
and C depends only on p, not on s.  So for two models evaluated on the SAME samples at the SAME noise level,
    SM(s_1) - SM(s_2)  =  (1/2) ( E||s_1 - s*||^2 - E||s_2 - s*||^2 ),
i.e. the DIFFERENCE of the estimator is exactly the difference of the two score errors.  Lower is better.
That is enough to ORDER two priors by score accuracy on a testbed whose true score is unknown.

It does not give an absolute GC, so it does NOT admit an arm; the pre-registered gates still decide that.
This is a diagnostic that says which prior's score is closer to the truth on D2, and by how much.

Both models are pushed through the SAME autodiff path (score.jac_batch / score.score_real), so no
convention can differ between them -- the identical machinery is what selftest_M5 already validates.
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, torch
import common as C, score, arms as A

NR, NT = 8, 4


def sm_terms(model, X, sg, chunk=64):
    """-> (tr(grad s), ||s||^2/2) per sample, at real-domain noise std `sg`."""
    tr, q = [], []
    for i in range(0, len(X), chunk):
        x = X[i:i + chunk]
        s = torch.full((len(x),), float(sg), dtype=x.dtype, device=x.device)
        Js = score.jac_batch(lambda v, u: model.score_real(v, u), x, s)      # (b, 2N, 2N)
        tr.append(torch.diagonal(Js, dim1=-2, dim2=-1).sum(-1))
        with torch.no_grad():
            sv = model.score_real(x, s)
        q.append(0.5 * (sv ** 2).sum(-1))
    return torch.cat(tr), torch.cat(q)


def main(a):
    dev = a.device
    torch.set_default_dtype(torch.float64)
    gen = C.make_gen("D2", a.prior, NR, NT)
    nu_grid, sig_grid = __import__("sigma").load("D2")
    H = gen.sample_vecs(C.train_rng("D2", a.prior, NR, 10), a.n)             # held-out, never trained on
    rng = np.random.default_rng(score.SEED_GATE)
    E = (rng.standard_normal((a.n, NR * NT)) + 1j * rng.standard_normal((a.n, NR * NT))) / np.sqrt(2)

    fits, llv, bstar, kron_K = A.gmm_selection("D2", a.prior, NR, a.gmm_ntrain)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    gmm = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
    models = {f"GMM b*={bstar} K={K} @N={a.gmm_ntrain}": score.ExactGMMTorch(gmm).to(dev)}
    for tag, ck in a.ckpt:
        models[tag] = score._as_model(ck, NR, NT, dev)[0]

    print(f"# Hyvarinen score-matching diagnostic on D2 (prior {a.prior}), n_eval={a.n}, "
          f"held-out stream 10.  LOWER IS BETTER; only DIFFERENCES between rows are meaningful.")
    print(f"# SM = E[ tr(grad s) + ||s||^2/2 ].  SM(A)-SM(B) = (E||s_A-s*||^2 - E||s_B-s*||^2)/2.")
    hdr = f"{'k':>3} {'sigma':>10} {'nu':>10} " + " ".join(f"{t[:26]:>28}" for t in models)
    print(hdr)
    out = {t: [] for t in models}
    for k, (nu, sg) in enumerate(zip(nu_grid, sig_grid)):
        Q = torch.as_tensor(score.np_pack(H + np.sqrt(nu) * E), dtype=torch.float64, device=dev)
        row = []
        for t, m in models.items():
            tr, q = sm_terms(m, Q, sg)
            v = float((tr + q).mean())
            se = float((tr + q).std() / np.sqrt(len(Q)))
            out[t].append((v, se))
            row.append(f"{v:>20.4f}+-{se:<5.3f}")
        print(f"{k:>3} {sg:>10.4e} {nu:>10.4e} " + " ".join(row), flush=True)
    base = list(models)[0]
    print(f"\n# difference vs the GMM row (negative = that model's score is CLOSER to the truth)")
    print(f"{'k':>3} {'sigma':>10} " + " ".join(f"{t[:26]:>28}" for t in list(models)[1:]))
    for k in range(len(nu_grid)):
        d = []
        for t in list(models)[1:]:
            v = out[t][k][0] - out[base][k][0]
            se = np.hypot(out[t][k][1], out[base][k][1])
            d.append(f"{v:>20.4f}+-{se:<5.3f}")
        print(f"{k:>3} {sig_grid[k]:>10.4e} " + " ".join(d))
    np.savez_compressed(os.path.join(C.CONF, "results", f"hyvarinen_D2{a.tag}.npz"),
                        sigma=sig_grid, nu=nu_grid, names=list(models),
                        sm=np.array([[v for v, _ in out[t]] for t in models]),
                        se=np.array([[s for _, s in out[t]] for t in models]))


def validate_d1(a):
    """VALIDATION.  On D1 the true score IS available, so the identity can be checked rather than trusted:
    SM(A) - SM(B) must equal (E||s_A - s*||^2 - E||s_B - s*||^2)/2, measured directly.  If the two agree,
    the diagnostic is sound and can be read on D2 where s* does not exist."""
    dev = a.device
    torch.set_default_dtype(torch.float64)
    gen = C.make_gen("D1", "S", NR, NT)
    true = gen.prior
    nu_grid, sig_grid = __import__("sigma").load("D1")
    H = gen.sample_vecs(C.train_rng("D1", "S", NR, 10), a.n)
    rng = np.random.default_rng(score.SEED_GATE)
    E = (rng.standard_normal((a.n, NR * NT)) + 1j * rng.standard_normal((a.n, NR * NT))) / np.sqrt(2)
    fits, llv, bstar, kron_K = A.gmm_selection("D1", "S", NR)
    fam, K = ("kron", kron_K) if bstar == "kron" else ("full", int(bstar[3:]))
    gfit = C.GMMPriorB(NR, NT, fits[(fam, K)]["covs"], fits[(fam, K)]["pi"])
    exact = score.ExactGMMTorch(true).to(dev)
    models = {"GMM-fit b*": score.ExactGMMTorch(gfit).to(dev)}
    for tag, ck in a.ckpt:
        models[tag] = score._as_model(ck, NR, NT, dev)[0]
    print("# VALIDATION on D1 (true score known).  For each model:")
    print("#   dSM   = SM(model) - SM(exact)          [Hyvarinen, needs NO ground truth]")
    print("#   dErr  = E||s_model - s*||^2 / 2        [direct, needs the true score]")
    print("#   These must agree.  Ratio dSM/dErr -> 1 validates the diagnostic.")
    print(f"{'k':>3} {'sigma':>10} " + " ".join(f"{t[:14]:>16} {'dSM/dErr':>9}" for t in models))
    ratios = []
    for k in range(0, len(nu_grid), max(1, len(nu_grid) // a.npts)):
        nu, sg = nu_grid[k], sig_grid[k]
        Q = torch.as_tensor(score.np_pack(H + np.sqrt(nu) * E), dtype=torch.float64, device=dev)
        st = torch.full((len(Q),), float(sg), dtype=Q.dtype, device=dev)
        tr0, q0 = sm_terms(exact, Q, sg)
        sm0 = float((tr0 + q0).mean())
        with torch.no_grad():
            s_star = exact.score_real(Q, st)
        cells = []
        for t, m in models.items():
            tr, q = sm_terms(m, Q, sg)
            dsm = float((tr + q).mean()) - sm0
            with torch.no_grad():
                derr = float((0.5 * ((m.score_real(Q, st) - s_star) ** 2).sum(-1)).mean())
            r = dsm / derr if derr > 0 else float("nan")
            ratios.append(r)
            cells.append(f"{dsm:>16.4f} {r:>9.4f}")
        print(f"{k:>3} {sg:>10.4e} " + " ".join(cells), flush=True)
    rr = np.array([r for r in ratios if np.isfinite(r)])
    print(f"\n# dSM/dErr over all points/models: mean {rr.mean():.4f}, min {rr.min():.4f}, max {rr.max():.4f}")
    print("# (1.0 = the identity holds exactly; deviations are Monte-Carlo error at this n)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--prior", default="S2")
    ap.add_argument("--gmm-ntrain", type=int, default=10000)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--tag", default="")
    ap.add_argument("--ckpt", nargs=2, action="append", metavar=("TAG", "PATH"), default=[])
    ap.add_argument("--validate-d1", action="store_true")
    ap.add_argument("--npts", type=int, default=5)
    _a = ap.parse_args()
    (validate_d1 if _a.validate_d1 else main)(_a)
