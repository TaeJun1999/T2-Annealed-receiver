# Would a GMM be near-correct on 38.901 UMi? Pilot-level denoising NMSE: K=1 Gaussian vs EM-GMM (K=16/64 full) vs
# latent oracle LO (Gaussian with the block's TRUE conditional 2nd moment, latents fixed, path/ray phases free) -- D2-S2 vs UMi-28GHz (yaw-only UT orientation).
import sys, copy, time, numpy as np, torch
sys.path.insert(0, "/home/HTJ/t2/conf/code"); sys.path.insert(0, "/home/HTJ/t2/Demo")
import d2
from t2_gmm import fit_gmm_em
from sionna.phy.channel.tr38901 import UMi, PanelArray
from sionna.phy.channel import gen_single_sector_topology
NTR, NTE, R = 40000, 500, 400
vec = lambda H: H.transpose(0, 2, 1).reshape(len(H), -1)            # column-major
torch.manual_seed(0); fc = 28e9
mk = lambda n: PanelArray(num_rows_per_panel=1, num_cols_per_panel=n, polarization="single", polarization_type="V",
                          antenna_pattern="omni", carrier_frequency=fc, device="cpu")
def umi_model(B, los=None):
    m = UMi(carrier_frequency=fc, o2i_model="low", ut_array=mk(4), bs_array=mk(8), direction="uplink",
            enable_pathloss=False, enable_shadow_fading=False, device="cpu")
    tp = list(gen_single_sector_topology(B, 1, "umi", indoor_probability=0.0, device="cpu"))
    o = torch.zeros_like(tp[2]); o[..., 0] = (torch.rand(o[..., 0].shape) * 2 - 1) * torch.pi; tp[2] = o
    m.set_topology(*tp, los=los); return m
draw = lambda m, B: m(1, 1.0)[0][..., 0].sum(-1).reshape(B, 8, 4).numpy().astype(np.complex128)
# ---- UMi train + test with conditional samples
m = umi_model(NTR); Htr_u = draw(m, NTR)
m = umi_model(NTE); orig = m._ray_sampler; box = {}
def cap(lsp):
    r = orig(lsp); box["r"] = copy.deepcopy(r); return r
object.__setattr__(m, "_ray_sampler", cap); m(1, 1.0)
object.__setattr__(m, "_ray_sampler", lambda lsp: copy.deepcopy(box["r"]))
los_u = m._scenario.los.reshape(NTE).numpy()
Hc_u = np.stack([vec(draw(m, NTE)) for _ in range(R + 1)], 1)       # (NTE, R+1, 32)
s_u = np.sqrt(32 / (np.abs(Htr_u) ** 2).sum((1, 2)).mean())
Xtr_u, Hc_u = vec(Htr_u) * s_u, Hc_u * s_u
# ---- D2 train + test with conditional samples
g = d2.D2Gen("S2", 8, 4); rng = np.random.default_rng(1)
Xtr_d = g.sample_vecs(rng, NTR)
Hc_d = []
for b in range(NTE):
    Hs, ang = g.sample_angles(rng, R + 1); Hc_d.append(vec(Hs))
Hc_d = np.stack(Hc_d)
def run(name, Xtr, Hc, strata):
    h = Hc[:, 0]; Cc = np.einsum("bri,brj->bij", Hc[:, 1:], Hc[:, 1:].conj()) / R        # LO covariance from the OTHER draws
    Cc += 1e-3 * np.eye(32) * (np.trace(Cc, axis1=1, axis2=2).real / 32)[:, None, None]
    Chat = Xtr.T @ Xtr.conj() / len(Xtr)
    gm = {}
    for K in (16, 64):
        t0 = time.time(); r = fit_gmm_em(Xtr[:36000], K, np.random.default_rng(K), n_iter=200, Xval=Xtr[36000:], patience=40)
        covs, w = r["covs"], r["pi"]; gm[K] = (np.asarray(covs), np.asarray(w)); print(f"  [{name}] GMM K={K} fit {time.time()-t0:.0f}s", flush=True)
    rng = np.random.default_rng(99)
    for snr in (-3, 3):
        nu = 10 ** (-snr / 10) / 4                                             # sigma^2 / Tp  (Tp = 4 orthogonal pilots)
        q = h + np.sqrt(nu / 2) * (rng.standard_normal(h.shape) + 1j * rng.standard_normal(h.shape))
        est = {"K1": q @ np.linalg.solve(Chat + nu * np.eye(32), Chat).T}
        est["LO"] = np.einsum("bij,bj->bi", Cc @ np.linalg.inv(Cc + nu * np.eye(32)), q)
        for K, (C, w) in gm.items():
            A = C + nu * np.eye(32); Ai = np.linalg.inv(A); _, ld = np.linalg.slogdet(A)
            ll = -np.einsum("bi,kij,bj->bk", q.conj(), Ai, q).real - ld[None] + np.log(w)[None]
            gam = np.exp(ll - ll.max(1, keepdims=True)); gam /= gam.sum(1, keepdims=True)
            est[f"GMM{K}"] = np.einsum("bk,kij,bj->bi", gam, C @ Ai, q)
        for sname, msk in strata.items():
            nm = {k: (np.abs(v[msk] - h[msk]) ** 2).sum() / (np.abs(h[msk]) ** 2).sum() for k, v in est.items()}
            clo = {K: (nm["K1"] - nm[f"GMM{K}"]) / (nm["K1"] - nm["LO"]) for K in gm}
            print(f"{name:4s} {sname:5s} n={msk.sum():3d} {snr:+d}dB NMSE  K1 {nm['K1']:.4f}  GMM16 {nm['GMM16']:.4f}  GMM64 {nm['GMM64']:.4f}  LO {nm['LO']:.4f}"
                  f"  | gap K1->LO closed by GMM16 {clo[16]:.2f}, GMM64 {clo[64]:.2f}", flush=True)
run("D2", Xtr_d, Hc_d, {"all": np.ones(NTE, bool)})
run("UMi", Xtr_u, Hc_u, {"all": np.ones(NTE, bool), "LOS": los_u, "NLOS": ~los_u})
