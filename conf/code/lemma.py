"""conf/code/lemma.py -- A3: reproduce the F2 lemma and draw the figure.

conf/03_SPEC_ourmodel.md §6: this is NOT a new experiment.  Demo/archive/exp_0915_bcjr_score_check.py is
run WITHOUT ANY MODIFICATION (and, for the figure, imported -- its work is under an  if __name__ == "__main__"
guard, so importing runs nothing).  Budget: 10 minutes.

The statement being reproduced (component A of conf/03_SPEC_ourmodel.md §0):
    the decoder's soft output IS the exact Tweedie score of the code-symbol prior,
        tanh(L_k/2) [BCJR, L_c = 2/sigma^2]  ==  E[x_k | x~]        and
        grad log p_t(x~) == (E[x|x~] - x~)/sigma^2,
    and, in the complex embedding, L_c = 4/sigma_c^2 is the correct constant while 2/sigma_c^2 is wrong.
"""
import os
import re
import subprocess
import sys

import numpy as np

import common as C

SRC = os.path.join(C.ARCHIVE, "exp_0915_bcjr_score_check.py")      # NOTE: Demo/archive/, not Demo/ (see DECISIONS)
OUT = os.path.join(C.CONF, "results", "lemma.txt")
FIG = os.path.join(C.CONF, "figs", "F2_lemma.png")


def run_unmodified(log=os.path.join(C.CONF, "logs", "lemma.log")):
    """Execute the archived script verbatim and keep its stdout."""
    before = C.file_sha(SRC)
    p = subprocess.run([sys.executable, SRC], cwd=C.ARCHIVE, capture_output=True, text=True)
    assert C.file_sha(SRC) == before, "the lemma script was modified -- forbidden"
    with open(log, "w") as f:
        f.write(p.stdout)
    return p.stdout, p.stderr, before


BLOCK = re.compile(r"\[real BPSK\] code \('133', '171'\)_8.*?\n(?:.*\n)*?(?=\n\[)")
CPLX = re.compile(r"\[complex embedding\].*?\n(?:.*\n)*?(?=\n\[)")


def parse(txt):
    """-> (max|tanh-E| over the (133,171)_8 rows, max Tweedie FD error, max Lc=4 error, min Lc=2 error)."""
    b = BLOCK.search(txt).group(0).strip().splitlines()[2:]
    rows = [[float(x) for x in l.split()] for l in b]
    tanh_err = max(r[1] for r in rows)
    tweedie = max(r[2] for r in rows)
    c = CPLX.search(txt).group(0).strip().splitlines()[2:]
    crows = [[float(x) for x in l.split()] for l in c]
    lc4 = max(r[1] for r in crows)
    lc2 = max(r[2] for r in crows)
    return tanh_err, tweedie, lc4, lc2, rows, crows


def write_results(txt):
    t, tw, lc4, lc2, rows, crows = parse(txt)
    with open(OUT, "w") as f:
        f.write(C.header("n/a (lemma reproduction)", extra=[
            f"source      : {os.path.relpath(SRC, C.REPO)} run UNMODIFIED (sha256[:16] = {C.file_sha(SRC)})",
            "content     : conf/03_SPEC_ourmodel.md §6 / conf/07_SPEC_tests.md L1, L2",
        ]) + "\n\n")
        f.write("L1  (133,171)_8, nu=6, K=8, brute force over all 2^K codewords\n")
        f.write(f"    max |tanh(L_k/2) - E[x_k | x~]|      = {t:.3e}   (criterion <= 1e-14)\n")
        f.write(f"    max Tweedie finite-difference error  = {tw:.3e}   (criterion <= 1e-9)\n")
        f.write("L2  complex embedding, noise CN(0, sigma_c^2) per entry\n")
        f.write(f"    max error with L_c = 4/sigma_c^2     = {lc4:.3e}   <- EXACT\n")
        f.write(f"    max error with L_c = 2/sigma_c^2     = {lc2:.3e}   <- WRONG (the guard for every complex\n")
        f.write("                                                       implementation in this folder)\n\n")
        f.write("full stdout of the unmodified script\n" + "=" * 100 + "\n" + txt)
    return t, tw, lc4, lc2


# ----------------------------------------------------------------------------- figure F2
def figure(sig2_list=(0.02, 0.05, 0.1, 0.3, 1.0, 3.0, 10.0), trials=4, seed=20260926):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    sys.path.insert(0, C.ARCHIVE)
    import exp_0915_bcjr_score_check as E                      # imported, never modified (main() is guarded)

    gens, nu, K = ("133", "171"), 6, 8
    nxt, out = E.make_trellis(gens, nu)
    nc = out.shape[2]
    Cw, X = E.all_codewords(K, nxt, out, nu)
    N = X.shape[1]
    rng = np.random.default_rng(seed)
    pts, errs, tw_errs = [], [], []
    for s2 in sig2_list:
        e1 = e2 = 0.0
        for _ in range(trials):
            x = X[rng.integers(X.shape[0])]
            xt = x + np.sqrt(s2) * rng.standard_normal(N)
            xb = np.tanh(E.bcjr((2.0 / s2) * xt.reshape(K + nu, nc), nxt, out, nu, K) / 2).reshape(-1)
            m, cov, _ = E.brute_real(xt, s2, X)
            pts.append(np.stack([m, xb], 1))
            e1 = max(e1, float(np.abs(xb - m).max()))
            g = E.fd_grad(lambda z: E.brute_real(z, s2, X)[2], xt)
            e2 = max(e2, float(np.abs(g - (xb - xt) / s2).max()))
        errs.append(e1)
        tw_errs.append(e2)
    P = np.concatenate(pts, 0)

    fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.8))
    ax[0].plot([-1.05, 1.05], [-1.05, 1.05], color="0.7", lw=1, zorder=0)
    ax[0].scatter(P[:, 0], P[:, 1], s=7, alpha=0.35, edgecolor="none", color="C0")
    ax[0].set_xlabel(r"brute force  $\mathbb{E}[x_k\,|\,\tilde{x}]$")
    ax[0].set_ylabel(r"BCJR  $\tanh(L_k/2)$,  $L_c=2/\sigma^2$")
    ax[0].set_title(f"(a) decoder soft output = conditional mean\n$(133,171)_8$, $\\nu$=6, K={K}, "
                    f"{len(sig2_list)} noise levels, all $2^{{{K}}}$ codewords")
    ax[0].set_xlim(-1.08, 1.08)
    ax[0].set_ylim(-1.08, 1.08)
    FLOOR = 1e-18                                              # exact zeros are drawn on the axis floor
    ax[1].loglog(sig2_list, np.maximum(errs, FLOOR), "o-", label=r"$\max_k|\tanh(L_k/2)-\mathbb{E}[x_k|\tilde x]|$")
    ax[1].loglog(sig2_list, np.maximum(tw_errs, FLOOR), "s--",
                 label=r"$\max|\nabla\log p_t(\tilde x)-(\mathbb{E}[x|\tilde x]-\tilde x)/\sigma^2|$ (FD)")
    ax[1].axhline(2.2e-16, color="0.6", lw=1, ls=":")
    ax[1].text(sig2_list[0], 2.6e-16, "float64 eps", fontsize=7, color="0.4")
    ax[1].set_xlabel(r"$\sigma^2$  (annealing level)")
    ax[1].set_ylabel("max absolute error")
    ax[1].set_title("(b) error vs noise level")
    ax[1].set_ylim(3e-19, 3e-7)
    ax[1].legend(fontsize=6.5, loc="lower right", framealpha=0.95)
    ax[1].text(sig2_list[0], 1.3e-18, "= 0 exactly", fontsize=7, color="0.4")
    ax[1].grid(True, which="both", alpha=0.25)
    fig.suptitle(f"F2 -- decoder soft output is the exact Tweedie score of the code prior "
                 f"(max error {max(errs):.1e} / Tweedie FD {max(tw_errs):.1e})", fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(FIG, dpi=160)
    plt.close(fig)
    return max(errs), max(tw_errs)
