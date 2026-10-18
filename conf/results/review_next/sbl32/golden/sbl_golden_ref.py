"""Golden cases for the SBL (MacKay) channel prior with an optional warm start.

Written from the spec only (no implementation code was read).
Two independent arithmetic paths:
  * SBLRef  : numpy complex128, literal transcription of the spec (reference implementation)
  * exact_* : exact Gaussian-rational arithmetic (fractions.Fraction), floors/eps as exact rationals
The JSON expected values come from the exact path (correctly rounded to float64);
the numpy path is checked against them.

Usage
  python sbl_golden_ref.py --write   # regenerate golden_sbl_warm.json from the exact path, then self-check
  python sbl_golden_ref.py           # self-check: numpy ref passes, every mutant fails >= 1 case

Harness for the implementation under test:
  check_impl(make_obj, set_trial, get_gamma=None) -> list of failure strings (empty = pass)
    make_obj(A, cbar, N, n_em, warm) -> object with ep_site(G, b) -> (Lambda, eta)
    set_trial(t)                      -> sets the global "current trial number"
    get_gamma(obj)                    -> gamma after the last call (optional; length M real)
"""
import json
import sys
from fractions import Fraction as F
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
JSON_PATH = HERE / "golden_sbl_warm.json"
EPS = 1e-6
FLOOR = 1e-12
RTOL_GAMMA = 1e-9    # elementwise relative, all expected gamma >= 1e-12 > 0
RTOL_LAMBDA = 1e-9   # Frobenius-relative
HERM_TOL = 1e-15     # ||L - L^H||_F <= HERM_TOL * ||L||_F (spec symmetrizes last -> exact)


# ---------------------------------------------------------------- reference implementation (numpy)
class SBLRef:
    """Spec transcription. `mutant` injects a known bug (used only to show the cases detect it)."""
    _shared = {}  # used only by the 'shared' mutant

    def __init__(self, A, cbar, N, n_em, warm=False, mutant=None):
        self.A = np.asarray(A, dtype=np.complex128)
        self.N, self.M = self.A.shape
        assert self.N == N
        self.gamma0 = np.full(self.M, cbar * N / self.M)
        self.n_em, self.warm, self.mutant = n_em, warm, mutant
        self.st = SBLRef._shared if mutant == "shared" else {}
        self.gamma = None

    def _step(self, g, G, b):
        A, mu_t = self.A, self.mutant
        Ah = A.T if mu_t == "AT" else A.conj().T
        Gu = G.T if mu_t == "Gconj" else G
        C = A @ np.diag(g) @ A.conj().T
        I = np.eye(self.N)
        K = np.linalg.inv(I + C @ Gu) if mu_t == "CG" else np.linalg.inv(I + Gu @ C)
        Kb = K.conj().T @ b if mu_t == "KH" else K @ b
        mu = g * (Ah @ Kb)
        d = np.real(np.einsum("ni,nm,mi->i", A.conj(), K @ Gu, A))
        num = np.real(mu * mu) if mu_t == "mu2" else np.abs(mu) ** 2
        den = g * d if mu_t == "noden" else np.maximum(g * d, FLOOR)
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.maximum(num / den, FLOOR)

    def ep_site(self, G, b, trial):
        G = np.asarray(G, dtype=np.complex128)
        b = np.asarray(b, dtype=np.complex128)
        s = self.st
        use_warm = self.warm and self.mutant != "warmflat"
        if use_warm and "gamma" in s and (s["trial"] == trial or self.mutant == "noreset"):
            g = s["gamma"].copy()
        else:
            g = self.gamma0.copy()
        for _ in range(self.n_em):
            g = self._step(g, G, b)
        s["gamma"], s["trial"] = g.copy(), trial
        self.gamma = g
        Cx = self.A @ np.diag(g) @ self.A.conj().T + EPS * np.eye(self.N)
        Cs = (Cx + Cx.conj().T) / 2
        L = np.linalg.inv(Cs)
        L = (L + L.conj().T) / 2
        return L, np.zeros(self.N, dtype=np.complex128)


# ---------------------------------------------------------------- exact path (Gaussian rationals)
class Q:
    __slots__ = ("r", "i")

    def __init__(s, r=0, i=0):
        s.r, s.i = F(r), F(i)

    @staticmethod
    def of(z):
        return z if isinstance(z, Q) else Q(F(complex(z).real), F(complex(z).imag))

    def __add__(s, o): o = Q.of(o); return Q(s.r + o.r, s.i + o.i)
    __radd__ = __add__
    def __sub__(s, o): o = Q.of(o); return Q(s.r - o.r, s.i - o.i)
    def __rsub__(s, o): return Q.of(o) - s
    def __mul__(s, o): o = Q.of(o); return Q(s.r * o.r - s.i * o.i, s.r * o.i + s.i * o.r)
    __rmul__ = __mul__
    def __truediv__(s, o):
        o = Q.of(o); d = o.r * o.r + o.i * o.i
        return s * Q(o.r / d, -o.i / d)
    def conj(s): return Q(s.r, -s.i)
    def abs2(s): return s.r * s.r + s.i * s.i


def mmul(X, Y):
    return [[sum((X[i][k] * Y[k][j] for k in range(len(Y))), Q()) for j in range(len(Y[0]))] for i in range(len(X))]


def herm(X):
    return [[X[j][i].conj() for j in range(len(X))] for i in range(len(X[0]))]


def inv(X):
    n = len(X)
    if n == 1:
        return [[Q(1) / X[0][0]]]
    assert n == 2
    a, b, c, d = X[0][0], X[0][1], X[1][0], X[1][1]
    det = a * d - b * c
    return [[d / det, Q() - b / det], [Q() - c / det, a / det]]


def eye(n):
    return [[Q(1) if i == j else Q() for j in range(n)] for i in range(n)]


def madd(X, Y):
    return [[X[i][j] + Y[i][j] for j in range(len(X[0]))] for i in range(len(X))]


def exact_step(A, g, G, b):
    N, M = len(A), len(A[0])
    Ah = herm(A)
    C = mmul(mmul(A, [[Q(g[i]) if i == j else Q() for j in range(M)] for i in range(M)]), Ah)
    K = inv(madd(eye(N), mmul(G, C)))
    Kb = mmul(K, [[x] for x in b])
    mu = [Q(g[i]) * mmul([Ah[i]], Kb)[0][0] for i in range(M)]
    KG = mmul(K, G)
    d = [mmul(mmul([Ah[i]], KG), [[A[n][i]] for n in range(N)])[0][0].r for i in range(M)]
    fl = F(1, 10**12)
    return [max(mu[i].abs2() / max(g[i] * d[i], fl), fl) for i in range(M)]


def exact_lambda(A, g):
    N, M = len(A), len(A[0])
    Cx = mmul(mmul(A, [[Q(g[i]) if i == j else Q() for j in range(M)] for i in range(M)]), herm(A))
    Cx = madd(Cx, [[Q(F(1, 10**6)) if i == j else Q() for j in range(N)] for i in range(N)])
    Cs = [[(Cx[i][j] + Cx[j][i].conj()) * Q(F(1, 2)) for j in range(N)] for i in range(N)]
    L = inv(Cs)
    return [[(L[i][j] + L[j][i].conj()) * Q(F(1, 2)) for j in range(N)] for i in range(N)]


def exact_run(spec_objs, calls):
    """Simulate the spec exactly. Returns per-call (gamma_start, gamma_end, Lambda) as Fractions/Q."""
    state, out = {}, []
    for c in calls:
        o = spec_objs[c["obj"]]
        A = [[Q.of(z) for z in row] for row in o["A"]]
        N, M = len(A), len(A[0])
        g0 = [F(o["cbar"]) * N / M] * M
        st = state.get(c["obj"])
        g = list(st[0]) if (o["warm"] and st is not None and st[1] == c["trial"]) else list(g0)
        gs = list(g)
        G = [[Q.of(z) for z in row] for row in c["G"]]
        b = [Q.of(z) for z in c["b"]]
        for _ in range(o["n_em"]):
            g = exact_step(A, g, G, b)
        state[c["obj"]] = (g, c["trial"])
        out.append((gs, g, exact_lambda(A, g)))
    return out


# ---------------------------------------------------------------- case definitions
J = 1j
A2 = [[1, 0, 1], [0, 1, J]]          # N=2, M=3; a3 = (1, j)
A1 = [[1, J]]                        # N=1, M=2
G1, b1 = [[1, 0], [0, 2]], [1, 0]
G2, b2 = [[1, J], [-J, 2]], [J, 1]   # complex Hermitian PD (det 1), complex b
Z2 = [[0, 0], [0, 0]]
S2 = dict(A=A2, cbar=1.5, N=2)       # flat gamma0 = 1.5*2/3 = 1
S1 = dict(A=A1, cbar=1, N=1)         # flat gamma0 = 1*1/2 = 1/2


def obj(base, n_em, warm):
    return dict(base, n_em=n_em, warm=warm)


def call(o, t, G, b):
    return dict(obj=o, trial=t, G=G, b=b)


CASES = [
    dict(id="C1_cold_1step",
         desc="cold, n_em=1, one call. Hand-derived: gamma=(5/13, 2/39, 9/91).",
         objects=dict(P=obj(S2, 1, False)),
         calls=[call("P", 7, G1, b1)]),
    dict(id="C2_warm_same_trial_same_site",
         desc="warm n_em=1, same trial, same (G,b) twice: call 2 == cold n_em=2 (object R).",
         objects=dict(P=obj(S2, 1, True), R=obj(S2, 2, False)),
         calls=[call("P", 7, G1, b1), call("P", 7, G1, b1), call("R", 7, G1, b1)]),
    dict(id="C3_warm_trial_change",
         desc="warm n_em=1: trial 7 (G2,b2); trial 8 (G1,b1) -> == C1 (flat start); "
              "back to trial 7 (G1,b1) -> previous call was trial 8, so flat again -> == C1.",
         objects=dict(P=obj(S2, 1, True)),
         calls=[call("P", 7, G2, b2), call("P", 8, G1, b1), call("P", 7, G1, b1)]),
    dict(id="C4_warm_same_trial_diff_site",
         desc="warm n_em=1, trial 3: (G1,b1) then (G2,b2). Call 2 starts from C1's end gamma. "
              "Object R (cold, (G2,b2)) shows the different flat-start answer.",
         objects=dict(P=obj(S2, 1, True), R=obj(S2, 1, False)),
         calls=[call("P", 3, G1, b1), call("P", 3, G2, b2), call("R", 3, G2, b2)]),
    dict(id="C5_warm_nem2_chain",
         desc="warm n_em=2, same trial, same site twice: call 2 == cold n_em=4 (object R).",
         objects=dict(P=obj(S2, 2, True), R=obj(S2, 4, False)),
         calls=[call("P", 11, G1, b1), call("P", 11, G1, b1), call("R", 11, G1, b1)]),
    dict(id="B1_b_zero_floor_absorbing",
         desc="b=0 -> mu=0 -> every gamma = 1e-12 (numerator floor). Warm same-trial call with b1 "
              "stays at the floor (absorbing); new trial recovers (== C1). Cold object R with b=0 also floors.",
         objects=dict(P=obj(S2, 1, True), R=obj(S2, 1, False)),
         calls=[call("P", 1, G1, [0, 0]), call("P", 1, G1, b1), call("P", 2, G1, b1),
                call("R", 2, G1, [0, 0])]),
    dict(id="B2_G_zero_den_floor",
         desc="G=0 (no information), b=b1: K=I, d=0 -> denominator floor 1e-12 -> "
              "gamma=(1e12, 1e-12, 1e12). Degenerate input, spec-literal.",
         objects=dict(P=obj(S2, 1, False)),
         calls=[call("P", 1, Z2, b1)]),
    dict(id="B3_N1_two_objects_and_cold_state",
         desc="N=1, M=2 (M>N), hand-computable: gamma_new = gamma*K*|b|^2/g with K=1/(1+g*sum gamma|a|^2). "
              "Two warm objects P, Q interleaved: no shared state, each compares the trial with its OWN "
              "previous call. Cold object R called twice in one trial: same answer both times.",
         objects=dict(P=obj(S1, 1, True), Q=obj(S1, 1, True), R=obj(S1, 1, False)),
         calls=[call("P", 5, [[1]], [1]), call("Q", 5, [[1]], [2]), call("P", 5, [[1]], [1]),
                call("Q", 6, [[1]], [2]), call("P", 6, [[1]], [1]), call("P", 6, [[1]], [1]),
                call("R", 6, [[1]], [1]), call("R", 6, [[1]], [1])]),
    dict(id="B4_nem0_optional",
         desc="OPTIONAL (spec does not say n_em>=1; skip if the implementation rejects n_em=0): "
              "gamma stays at its start, Lambda = inv(A diag(gamma0) A^H + eps I). Warm second call: same.",
         optional=True,
         objects=dict(P=obj(S2, 0, True), R=obj(S2, 0, False)),
         calls=[call("P", 1, G1, b1), call("P", 1, G2, b2), call("R", 1, G1, b1)]),
]


# ---------------------------------------------------------------- JSON encoding
def enc(x):
    a = np.asarray(x, dtype=np.complex128)
    return {"re": a.real.tolist(), "im": a.imag.tolist()}


def dec(d):
    return np.asarray(d["re"], dtype=float) + 1j * np.asarray(d["im"], dtype=float)


def qmat_to_np(L):
    return np.array([[complex(float(z.r), float(z.i)) for z in row] for row in L])


def build_json():
    out = {"meta": {
        "spec": "SBL MacKay prior; flat gamma0=cbar*N/M; step: K=(I+G A Gam A^H)^-1, mu=Gam A^H K b, "
                "d_i=Re(a_i^H K G a_i), gamma_i<-max(|mu_i|^2/max(gamma_i d_i,1e-12),1e-12); "
                "Lambda=sym(inv(sym(A diag(gamma) A^H + 1e-6 I))), eta=0; warm: start from own previous "
                "end gamma iff global trial == trial at own previous call.",
        "encoding": "complex arrays as {re, im} nested lists; gamma real lists",
        "source": "exact Gaussian-rational arithmetic (fractions), correctly rounded to float64",
        "tolerances": {"gamma_elementwise_rtol": RTOL_GAMMA, "Lambda_frobenius_rtol": RTOL_LAMBDA,
                       "Lambda_hermitian_tol_rel": HERM_TOL, "eta": "exactly zero, length N"},
    }, "cases": []}
    for c in CASES:
        res = exact_run(c["objects"], c["calls"])
        calls = []
        for cl, (gs, ge, L) in zip(c["calls"], res):
            calls.append(dict(obj=cl["obj"], trial=cl["trial"], G=enc(cl["G"]), b=enc(cl["b"]),
                              expected=dict(gamma_start=[float(x) for x in gs],
                                            gamma_end=[float(x) for x in ge],
                                            gamma_end_exact=[str(x) for x in ge],
                                            Lambda=enc(qmat_to_np(L)),
                                            eta=enc(np.zeros(len(cl["b"]))))))
        objs = {k: dict(A=enc(v["A"]), cbar=v["cbar"], N=v["N"], n_em=v["n_em"], warm=v["warm"])
                for k, v in c["objects"].items()}
        out["cases"].append(dict(id=c["id"], desc=c["desc"], optional=c.get("optional", False),
                                 objects=objs, calls=calls))
    return out


# ---------------------------------------------------------------- comparison harness
def compare(exp, L, eta, gamma=None):
    errs = []
    Le = dec(exp["Lambda"])
    L = np.asarray(L, dtype=np.complex128)
    if L.shape != Le.shape:
        return [f"Lambda shape {L.shape} != {Le.shape}"]
    if not np.all(np.isfinite(L)):
        return ["Lambda not finite"]
    r = np.linalg.norm(L - Le) / np.linalg.norm(Le)
    if not r <= RTOL_LAMBDA:
        errs.append(f"Lambda rel err {r:.3e}")
    h = np.linalg.norm(L - L.conj().T) / np.linalg.norm(L)
    if not h <= HERM_TOL:
        errs.append(f"Lambda not Hermitian ({h:.1e})")
    eta = np.asarray(eta)
    if eta.shape != (Le.shape[0],) or np.any(eta != 0):
        errs.append("eta not exactly zero of length N")
    if gamma is not None:
        ge = np.asarray(exp["gamma_end"])
        g = np.asarray(gamma, dtype=float)
        if g.shape != ge.shape or not np.all(np.abs(g - ge) <= RTOL_GAMMA * ge):
            errs.append(f"gamma {g} != {ge}")
    return errs


def check_impl(make_obj, set_trial, get_gamma=None, include_optional=True, data=None):
    data = data or json.loads(JSON_PATH.read_text())
    fails = []
    for c in data["cases"]:
        if c["optional"] and not include_optional:
            continue
        objs = {k: make_obj(dec(v["A"]), v["cbar"], v["N"], v["n_em"], v["warm"]) for k, v in c["objects"].items()}
        for i, cl in enumerate(c["calls"]):
            set_trial(cl["trial"])
            try:
                L, eta = objs[cl["obj"]].ep_site(dec(cl["G"]), dec(cl["b"]))
                e = compare(cl["expected"], L, eta, get_gamma(objs[cl["obj"]]) if get_gamma else None)
            except Exception as ex:  # a crash is a failure of that call
                e = [f"exception {type(ex).__name__}: {ex}"]
            fails += [f"{c['id']} call{i + 1} ({cl['obj']}): {m}" for m in e]
    return fails


def ref_adapter(mutant=None):
    cur = {"t": None}

    class W:
        def __init__(s, A, cbar, N, n_em, warm):
            s.o = SBLRef(A, cbar, N, n_em, warm, mutant)

        def ep_site(s, G, b):
            return s.o.ep_site(G, b, cur["t"])

    SBLRef._shared = {}
    return W, (lambda t: cur.__setitem__("t", t)), (lambda w: w.o.gamma)


MUTANTS = ["CG", "KH", "AT", "Gconj", "mu2", "noden", "noreset", "shared", "warmflat"]

if __name__ == "__main__":
    if "--write" in sys.argv:
        JSON_PATH.write_text(json.dumps(build_json(), indent=1))
        print("wrote", JSON_PATH)
    data = json.loads(JSON_PATH.read_text())
    # JSON reproducible from the exact path
    assert json.dumps(build_json(), indent=1) == JSON_PATH.read_text(), "JSON stale vs exact path"
    mk, st, gg = ref_adapter()
    f = check_impl(mk, st, gg, data=data)
    print("numpy reference vs exact golden:", "PASS" if not f else f)
    assert not f
    for m in MUTANTS:
        mk, st, gg = ref_adapter(m)
        with np.errstate(all="ignore"):  # 'noden' mutant produces nan/inf on purpose
            f = check_impl(mk, st, gg, data=data)
        hit = sorted({x.split()[0] for x in f})
        print(f"mutant {m:9s}: {'DETECTED' if f else 'MISSED'} in {hit}")
        assert f, m
    print("ALL OK")
