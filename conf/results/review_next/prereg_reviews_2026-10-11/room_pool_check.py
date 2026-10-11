"""prereg_reviews_2026-10-11/room_pool_check.py -- read-only recomputation of the SRB / DMI pool facts quoted in
NEXT_EXPERIMENTS_ROOM16e4.md §0 (sha, split counts, tile disjointness, DMI yaw-group integrity, per-pair power, test-pool
rank-1 share) and a dry run of the plumbing (banner strings, pilots, streams, rung index, PAT).  CPU only, no BLER."""
import os, sys, hashlib, numpy as np
os.environ["OMP_NUM_THREADS"] = "16"
sys.path.insert(0, "code")
import common as C, dmimo, analysis, score, sigma

def sha16(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""): h.update(b)
    return h.hexdigest()[:16]

for pr, folder, tile in (("SRB", "~/data/sionna_rt/srb_Nr8", 1.0), ("DMI", "~/data/deepmimo/dmi_Nr8", 0.5)):
    d = os.path.expanduser(folder)
    H = np.load(f"{d}/H.npy"); sp = np.load(f"{d}/split.npy"); m = np.load(f"{d}/meta.npz", allow_pickle=True)
    print(f"== {pr}: sha H {sha16(d + '/H.npy')} split {sha16(d + '/split.npy')} | POOL_SHA {dmimo.POOL_SHA[(pr, 8)]}")
    n = len(H); cnt = np.bincount(sp, minlength=3)
    print(f"   pairs {n} = fit {cnt[0]} + val {cnt[1]} + test {cnt[2]} (test share {cnt[2] / n:.4f}); H dtype {H.dtype} shape {H.shape}")
    key = m["key"]; kt = set(key[sp == 2].tolist()); kr = set(key[sp != 2].tolist())
    print(f"   tiles {len(set(key.tolist()))}, test tiles {len(kt)}, tiles on both sides {len(kt & kr)}")
    pos = m["pos"]; tl = np.floor(pos[:, :2] / tile).astype(np.int64); k2 = tl[:, 0] * 100003 + tl[:, 1]
    print(f"   key == floor(xy/{tile}) recomputed: {np.array_equal(k2, key)}")
    if pr == "DMI":
        posi = m["posi"]; st = set(posi[sp == 2].tolist()); sr = set(posi[sp != 2].tolist())
        print(f"   DMI grid positions: {len(set(posi.tolist()))}, test positions {len(st)}, positions on both sides {len(st & sr)}; yaw groups of 5: {np.all(np.bincount(posi) == 5)}")
        print(f"   DMI x range {pos[:, 0].min():.2f}..{pos[:, 0].max():.2f}, y {pos[:, 1].min():.2f}..{pos[:, 1].max():.2f}, z {pos[:, 2].min():.2f}..{pos[:, 2].max():.2f}; LoS {m['los'].mean():.4f}, mean paths {m['npath'].mean():.2f}")
    else:
        print(f"   SRB xy range {pos[:, 0].min():.3f}..{pos[:, 0].max():.3f} / {pos[:, 1].min():.3f}..{pos[:, 1].max():.3f}; BS {m['bs']}; LoS {m['los'].mean():.4f}, mean paths {m['npath'].mean():.2f}")
    p2 = (np.abs(H.astype(np.complex128)) ** 2).sum((1, 2)) / 32
    print(f"   raw per-pair ||H||^2/(NrNt): mean {p2.mean():.4f} median {np.median(p2):.4f} min {p2.min():.4f} max {p2.max():.4f}; test-side mean {p2[sp == 2].mean():.4f}")
    for nm, msk in (("all", np.ones(n, bool)), ("fit", sp == 0), ("val", sp == 1), ("test", sp == 2)):
        q = np.linalg.svd(H[msk].astype(np.complex128), compute_uv=False) ** 2; q /= q.sum(1, keepdims=True)
        er = np.exp(-(q * np.log(np.maximum(q, 1e-300))).sum(1)).mean()
        print(f"   rank-1 share (q1 >= 0.95) {nm}: {(q[:, 0] >= 0.95).mean():.4f}; 0.80-0.95: {((q[:, 0] >= 0.80) & (q[:, 0] < 0.95)).mean():.4f}; < 0.80: {(q[:, 0] < 0.80).mean():.4f}; erank {er:.3f}; median q1 {np.median(q[:, 0]):.4f}")
    # streams -> pools
    g = C.make_gen("D2", pr, 8, 4)
    print(f"   make_gen -> {type(g).__name__}; pilots make_pilots: {C.make_pilots('D2', pr, 4, 4, 8)[1] if isinstance(C.make_pilots('D2', pr, 4, 4, 8), tuple) else 'ret'}")
    b = C.banner("D2", pr)
    print(f"   banner has 'SITE-SPECIFIC RAY-TRACED TESTBED (prior {pr})': {('SITE-SPECIFIC RAY-TRACED TESTBED (prior ' + pr + ')') in b}; has 'CLAIM TESTBED -- sparse specular': {'CLAIM TESTBED -- sparse specular' in b}; has 'FIVE': {'FIVE' in b}; has 'ONE fixed BS': {'ONE fixed BS' in b}")
    print(f"   PAT parse D2_C2_{pr}_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz: {bool(analysis.PAT.match(f'D2_C2_{pr}_Nr8_T16_Tp4_dft_snr-3_skip0_n40.npz'))}; rung ix D2SX{pr}160000 = {score._rung_ix(f'D2SX{pr}160000')}; CHAT_FROM_TRAIN {pr in sigma.CHAT_FROM_TRAIN}; PID {C.PID[pr]}")
