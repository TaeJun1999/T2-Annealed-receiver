# D2 analogue of the 38.901 LSP-oracle: how much of the K1->LO gap does a LOW-DIM latent explain in D2?
# P1O = Gaussian given (L, angles of the strongest path); other paths' angles and all phases redrawn.  CPU, numpy.
import sys, numpy as np
sys.path.insert(0, "/home/HTJ/t2/conf/code"); import d2
Nr, Nt, NTE, R = int(sys.argv[1]) if len(sys.argv) > 1 else 8, 4, 1000, 400; N = Nr * Nt
g = d2.D2Gen("S2", Nr, Nt); rng = np.random.default_rng(5); vec = lambda H: H.transpose(0, 2, 1).reshape(len(H), -1)
Chat = (lambda X: X.T @ X.conj() / len(X))(g.sample_vecs(rng, 40000))
h, CL, CP = [], [], []
for b in range(NTE):
    Hs, (th, ph, p) = g.sample_angles(rng, R + 1); X = vec(Hs); h.append(X[0]); CL.append(X[1:].T @ X[1:].conj() / R)
    L = len(th); th2 = np.tile(th, (R, 1)); ph2 = np.tile(ph, (R, 1))
    th2[:, 1:] = g.lo + (g.hi - g.lo) * rng.random((R, L - 1)); ph2[:, 1:] = g.lo + (g.hi - g.lo) * rng.random((R, L - 1))
    Y = vec(g._channels(th2, ph2, np.sqrt(p) * np.exp(2j * np.pi * rng.random((R, L))))); CP.append(Y.T @ Y.conj() / R)
h = np.array(h); I = np.eye(N)
reg = lambda C: C + 1e-3 * I * (np.trace(C, axis1=1, axis2=2).real / N)[:, None, None]
CL, CP = reg(np.array(CL)), reg(np.array(CP))
for snr in (-3, 3):
    nu = 10 ** (-snr / 10) / Nt; q = h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))
    e = {"K1": q @ np.linalg.solve(Chat + nu * I, Chat).T, "LO": np.einsum("bij,bj->bi", CL @ np.linalg.inv(CL + nu * I), q),
         "P1O": np.einsum("bij,bj->bi", CP @ np.linalg.inv(CP + nu * I), q)}
    nm = {k: (np.abs(v - h) ** 2).sum() / (np.abs(h) ** 2).sum() for k, v in e.items()}
    print(f"D2 {Nr}x4 {snr:+d}dB NMSE " + " ".join(f"{k} {v:.4f}" for k, v in nm.items()) + f" | P1O closes {(nm['K1']-nm['P1O'])/(nm['K1']-nm['LO']):.2f} of K1->LO")
