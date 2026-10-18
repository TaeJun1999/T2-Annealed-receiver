"""Golden cases (golden-writer, spec only) against the Codex implementation in ~/t2_wtE3 (arms.SparsePrior)."""
import sys, types
sys.path.insert(0, "/home/HTJ/t2_wtE3/conf/code"); sys.path.insert(0, sys.argv[1])
import numpy as np
import arms as A
import sbl_golden_ref as R

class W:
    def __init__(s, Amat, cbar, N, n_em, warm):
        s.o = A.SparsePrior(types.SimpleNamespace(cbar=cbar, N=N), 1, 1, 1, n_em, warm=warm)
        s.o.A = np.asarray(Amat, complex)            # the golden dictionary replaces dft_dict(1, 1, 1)
    def ep_site(s, G, b):
        return s.o.ep_site(G, b, 0.0)

def set_trial(t):
    A.CURRENT_TRIAL = t

def get_gamma(w):
    return w.o._gamma_last.copy() if w.o.warm and w.o._gamma_last is not None else None

for opt in (True, False):
    f = R.check_impl(W, set_trial, get_gamma, include_optional=opt)
    print(f"include_optional={opt}: {'PASS' if not f else 'FAIL'}"); [print("  ", x) for x in f]
