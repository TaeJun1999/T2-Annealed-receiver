"""conf/code/testbed_s2v.py -- testbed record for the spatially non-stationary prior S2v (NEXT_EXPERIMENTS_S2V16e4 §0, §4).
Report only (no judgement uses it).  Monte Carlo on its OWN rng (default_rng(20260928), not a pipeline stream), Nr = 16, Nt = 4:
  TV1  normalisation E||H||^2 / (Nr Nt)                                 (VIS_NORM = sqrt(8/5) makes it 1 analytically)
  TV2  per-block receive-element power: CV = std_r(p_r) / mean_r(p_r), p_r = sum_t |H_rt|^2, mean over blocks; S2 alongside
  TV3  ensemble receive covariance Rr = E[H H^H] / Nt: diagonal min / max / std (S2: flat; S2v: edge elements see fewer windows)
  TV4  window width w = #visible elements per path and start s0 (first visible element): empirical vs U{Nr/4..Nr}, U{0..Nr-w}
The analytic C_ens check of d2.py is not applicable to S2v (Rr undefined analytically) -- "Rr 미정의".
    python code/testbed_s2v.py > results/testbed_S2v.txt
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C
import numpy as np

NR, NT, N, SEED = 16, 4, 200000, 20260928


def stats(prior):
    g = C.make_gen("D2", prior, NR, NT)
    H = g.sample_vecs(np.random.default_rng(SEED), N).reshape(N, NT, NR).transpose(0, 2, 1)     # (n, Nr, Nt)
    p = (np.abs(H) ** 2).sum(-1)                                                                  # (n, Nr)
    Rr = np.einsum("nit,njt->ij", H, H.conj()) / (N * NT)
    return g, (np.abs(H) ** 2).sum((1, 2)).mean() / (NR * NT), (p.std(1) / p.mean(1)).mean(), np.real(np.diag(Rr))


def main():
    print(f"# testbed_s2v  Nr={NR} Nt={NT}  n={N} blocks per prior, rng default_rng({SEED}) (own stream), git "
          + os.popen(f"git -C {C.CONF} rev-parse --short HEAD").read().strip())
    for prior in ("S2", "S2v"):
        g, nrm, cv, d = stats(prior)
        print(f"{prior:4s} TV1 E||H||^2/(NrNt) = {nrm:.4f}   TV2 mean per-block element-power CV = {cv:.3f}   "
              f"TV3 diag(Rr) min {d.min():.3f} max {d.max():.3f} std {d.std():.3f}")
        print(f"     diag(Rr) = " + " ".join(f"{x:.3f}" for x in d))
    g = C.make_gen("D2", "S2v", NR, NT)
    al, ar, at = g._latents(np.random.default_rng(SEED + 1), 50000)
    vis = np.abs(ar) > 0                                                   # (n, L_MAX, Nr); unused paths have al = 0
    use = np.abs(al) > 0
    w = vis.sum(-1)[use]; s0 = vis.argmax(-1)[use]
    ws = np.arange(NR // 4, NR + 1)
    print(f"TV4 window width over {use.sum()} used paths: empirical freq " + " ".join(f"{k}:{(w == k).mean():.3f}" for k in ws)
          + f"  (uniform {1 / len(ws):.3f}); max |dev| {max(abs((w == k).mean() - 1 / len(ws)) for k in ws):.4f}")
    dev = max(abs((s0[w == k] == j).mean() - 1 / (NR - k + 1)) for k in ws for j in range(NR - k + 1) if (w == k).sum())
    print(f"TV4 start s0 | w: max |empirical - 1/(Nr-w+1)| over (w, s0) = {dev:.4f};  all windows inside the array: "
          f"{bool(((s0 + w) <= NR).all())};  windows contiguous: {bool((np.diff(vis.astype(int), axis=-1) != 0).sum(-1)[use].max() <= 2)}")
    print("C_ens analytic check: not applicable to S2v (Rr undefined analytically; no arm uses it -- NEXT_EXPERIMENTS_S2V16e4 §0)")


if __name__ == "__main__":
    main()
