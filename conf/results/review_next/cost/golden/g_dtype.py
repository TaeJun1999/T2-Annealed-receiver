"""golden helper: runtime dtypes of the V1 network (after load) and of the b* GMM / receiver arrays (D2)."""
import os, sys
os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import numpy as np, torch
torch.set_num_threads(1)
import common as C, arms as A, score as S
A.D2_FITS = "/home/HTJ/t2/conf/results/gmm_fits_D2_B16e4k"
sp = S.load_prior("D2", "S2", 8, 4, ckpt="/home/HTJ/t2/conf/ckpt/d2sx_N160000_a1.pt", device="cpu", psd_project=True, ntrain=160000)
print("network param dtypes:", sorted({str(p.dtype) for p in sp.model.parameters()}), " buffer M dtype:", sp.model.M.dtype, " device:", sp.device)
print("ScorePrior C dtype:", sp.C.dtype, " psd_project:", sp.psd_project, " psd_floor:", sp.psd_floor, " torch threads:", torch.get_num_threads())
hp, fits, llv, bstar, kron_K = A.module_h_priors("D2", "S2", 8, 4, 160000)
g = hp[bstar].view("eta")
print("b* GMM covs/covinv/U dtypes:", g.covs.dtype, g.covinv.dtype, g.U.dtype, " K:", g.K, " clip:", g.clip)
