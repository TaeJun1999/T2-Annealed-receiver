# check: GPU EM port == CPU Demo/t2_gmm.fit_gmm_em on D2 8x4 (same rng, same data)
import time, numpy as np, torch, tb, d2
from t2_gmm import fit_gmm_em
X = d2.D2Gen("S2", 8, 4).sample_vecs(np.random.default_rng(3), 10000)
for K in (16, 64):
    t0 = time.time(); a = fit_gmm_em(X[:8000], K, np.random.default_rng(K), n_iter=60, Xval=X[8000:], patience=40); t1 = time.time()
    b = fit_gmm_em_t = tb.fit_gmm_em_t(X[:8000], K, np.random.default_rng(K), n_iter=60, Xval=X[8000:], patience=40); t2 = time.time()
    rel = np.linalg.norm(a["covs"] - b["covs"].cpu().numpy()) / np.linalg.norm(a["covs"])
    print(K, "cpu", round(t1-t0,1), "s gpu", round(t2-t1,1), "s | rel cov diff", rel, "pi diff", np.abs(a["pi"]-b["pi"].cpu().numpy()).max(),
          "it_best", a["it_best"], b["it_best"], "reseed", a["n_reseed"], b["n_reseed"], "ll_val", a["ll_val"], b["ll_val"])
    assert rel < 1e-6
