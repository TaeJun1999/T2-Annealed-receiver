"""Independent recomputation of K1 / K2 / K2test / C6(NR16B16e4) records straight from raw npz (no analysis.py tables)."""
import glob, os, sys, numpy as np
from scipy.stats import binomtest
sys.path.insert(0, '/home/HTJ/t2/conf/code')
import common as C
from analysis import sign_p
RAW = '/home/HTJ/t2/conf'
NU_HI = 1.4285757304853552
KEYS = C.KEYS_RAW

def p2(a, b): return binomtest(a, a + b, 0.5).pvalue if a + b > 0 else float('nan')
def mdd(n):
    for d in range(n % 2, n + 1, 2):
        a = (n + d) // 2
        if p2(a, n - a) < 0.05: return d
def load(d, pat):
    rows, metas, chunks = {}, [], set()
    for f in sorted(glob.glob(os.path.join(RAW, d, pat))):
        z = np.load(f, allow_pickle=True)
        skip, n = int(z['run|skip']), int(z['run|n']); chunks.add((skip, n))
        metas.append({k: (z[k].item() if z[k].ndim == 0 else tuple(z[k].tolist())) for k in z.files if k.startswith(('meta|', 'run|'))})
        for k in z.files:
            if k.startswith(('meta|', 'run|')): continue
            v = z[k]
            for i in range(n): rows.setdefault(skip + i, {})[k] = v[i]
    return rows, metas, chunks
def fails(rows, arm, it=15):
    t = sorted(rows); v = np.array([rows[x][f'{arm}|blk_err'][it] for x in t], float)
    return np.where(np.isfinite(v), v, 1.0), t
def st(x, y):  # a = x fails & y ok ; b = x ok & y fails
    a = int(((x == 1) & (y == 0)).sum()); b = int(((x == 0) & (y == 1)).sum()); return a, b, p2(a, b), sign_p(a, b)
def ident(rows1, rows2, arms, keys=KEYS):
    worst = {}
    for arm in arms:
        w = 0.0
        for t in rows1:
            for k in keys:
                a, b = np.asarray(rows1[t][f'{arm}|{k}'], float), np.asarray(rows2[t][f'{arm}|{k}'], float)
                if a.shape != b.shape: w = np.inf; continue
                m = np.isfinite(a) | np.isfinite(b)
                if not np.array_equal(np.isfinite(a), np.isfinite(b)): w = np.inf; continue
                if m.any(): w = max(w, float(np.abs(a[m] - b[m]).max()))
        worst[arm] = w
    return worst
def meta_uniform(metas, keys):
    return {k: sorted(set(str(m.get(k)) for m in metas)) for k in keys}

print('=' * 100); print('K2 (raw_review_next_K2) + K2test')
for tag, pat, skip0, n, label in [('raw_review_next_K2', 'D2_C1_*snr-3_*', 3200, 1280, 'C1 -3 dB'), ('raw_review_next_K2', 'D2_C1_*snr0_*', 2560, 640, 'C1 0 dB'),
                                   ('raw_review_next_K2', 'D2_C5_*snr-6_*', 2560, 640, 'C5 -6 dB'), ('raw_review_next_K2test', 'D2_C1_*snr-3_*', 0, 2560, 'C1 -3 dB TEST')]:
    rows, metas, chunks = load(tag, pat)
    exp = {(skip0 + 10 * k, 10) for k in range(n // 10)}
    print(f'\n== {tag} {label}: trials {min(rows)}..{max(rows)} n={len(rows)} chunks OK={chunks == exp} ({len(chunks)})')
    print('   meta uniform:', meta_uniform(metas, ['meta|arms', 'meta|ckpt_sha', 'meta|edge_kw', 'meta|bstar', 'meta|kron_K', 'meta|ntrain', 'meta|fits_tag', 'run|iters']))
    arms = metas[0]['meta|arms'].split()
    F = {}
    for arm in arms:
        f, t = fails(rows, arm); F[arm] = f
        exc = sum(float(rows[x][f'{arm}|failed']) for x in t)
        gd = np.nansum([float(rows[x][f'{arm}|guardH']) for x in t])
        nq = np.array([np.asarray(rows[x][f'{arm}|nu_q'], float) for x in t]) > NU_HI
        oog = f'  n_oog/block {np.mean([rows[x][f"{arm}|n_oog"] for x in t]):.2f}' if f'{arm}|n_oog' in rows[t[0]] else ''
        gb, gg = F.get('M-ours-bstar'), None
        print(f'   {arm:<22} fails {int(f.sum()):5d} ({f.mean():.4f})  guard {gd:.0f}  exceptions {exc:.0f}  above-grid it1 {nq[:, 0].mean():.2f} it2-16 {nq[:, 1:].mean():.3f}{oog}')
    b, g = F['M-ours-bstar'], F['R5-genie']
    for arm in arms: print(f'   gap position {arm:<22} {(b.sum() - F[arm].sum()) / (b.sum() - g.sum()):+.3f}')
    for x, y in [('M-ours-bstar', 'V1-edge'), ('M-ours-dscore-C-V1', 'V1-edge'), ('gmmB-scorew-eta', 'V1-edge'), ('M-ours-bstar-scalar', 'V1-edge'),
                 ('M-ours-bstar', 'V1-clamp'), ('M-ours-dscore-C-V1', 'V1-clamp'), ('V1-clamp', 'V1-edge'), ('M-ours-bstar', 'M-ours-dscore-C-V1')]:
        a, bb, p, ph = st(F[x], F[y]); print(f'   {x:>20} -> {y:<20} {a}:{bb}  p_scipy={p:.3g} p_house={ph:.3g}  n_d={a + bb} MDD={mdd(a + bb)}')
    if label == 'C1 -3 dB TEST':
        rB, _, _ = load('raw_B16e4', 'D2_C1_*snr-3_*')
        print('   K2test vs raw_B16e4 (C1 -3 dB, trials 0..2559) bit-identity max|diff| over KEYS_RAW:', ident(rows, rB, ['M-ours-dscore-C-V1', 'R5-genie']))
        fb, _ = fails(rB, 'M-ours-dscore-C-V1'); print(f'   raw_B16e4 V1 fails {int(fb.sum())} ({fb.mean():.4f}); b*(K<=512) {int(fails(rB, "M-ours-bstar")[0].sum())}; genie {int(fails(rB, "R5-genie")[0].sum())}')

print('\n' + '=' * 100); print('K1 (raw_review_next_K1 + LO + P3ref)')
for pat, skip0, n, label in [('D2_C2_*snr-3_*', 3200, 1280, 'C2 -3 dB'), ('D2_C5_*snr-3_*', 3200, 640, 'C5 -3 dB')]:
    rK, mK, cK = load('raw_review_next_K1', pat); rL, mL, cL = load('raw_review_next_LO', pat); rP, mP, cP = load('raw_review_next_P3ref', pat)
    tr = sorted(rK)
    print(f'\n== {label}: K1 trials {tr[0]}..{tr[-1]} n={len(tr)} chunks OK={cK == {(skip0 + 20 * k, 20) for k in range(n // 20)}}; LO has all={all(t in rL for t in tr)} (LO iters {mL[0]["run|iters"]}); P3ref has all={all(t in rP for t in tr)}')
    print('   meta uniform:', meta_uniform(mK, ['meta|arms', 'meta|bg_kw', 'meta|ckpt_sha', 'meta|fits_tag', 'meta|ntrain', 'run|iters']))
    print('   K1 vs P3ref bit-identity (KEYS_RAW @1..16):', ident(rK, {t: rP[t] for t in tr}, ['M-ours-dscore-C-V1', 'M-ours-bstar', 'R5-genie']))
    F = {a: fails(rK, a)[0] for a in ['M-ours-bstar', 'M-ours-dscore-C-V1', 'BR-S', 'R5-genie']}
    F['LO-S-d0.001'] = np.array([rL[t]['LO-S-d0.001|blk_err'][15] for t in tr], float); F['LO-S-d0.001'] = np.where(np.isfinite(F['LO-S-d0.001']), F['LO-S-d0.001'], 1.0)
    b, g = F['M-ours-bstar'], F['R5-genie']
    for a in F: print(f'   {a:<20} fails {int(F[a].sum()):4d} ({F[a].mean():.4f}) gap pos {(b.sum() - F[a].sum()) / (b.sum() - g.sum()):+.3f}')
    for x, y in [('M-ours-dscore-C-V1', 'BR-S'), ('BR-S', 'LO-S-d0.001'), ('BR-S', 'R5-genie'), ('M-ours-bstar', 'BR-S'), ('M-ours-dscore-C-V1', 'LO-S-d0.001')]:
        a, bb, p, ph = st(F[x], F[y]); print(f'   {x:>20} -> {y:<14} {a}:{bb} p_scipy={p:.3g} p_house={ph:.3g} n_d={a + bb} MDD={mdd(a + bb)}')
    md = np.array([float(rK[t]['BR-S|mc_disagree']) for t in tr]); exc = sum(float(rK[t]['BR-S|failed']) for t in tr); gd = np.nansum([float(rK[t]['BR-S|guardH']) for t in tr])
    print(f'   BR-S exceptions {exc:.0f} guard {gd:.0f} chain spread median {np.median(md):.3g} p90 {np.percentile(md, 90):.3g}')

print('\n' + '=' * 100); print('C6 NR16B16e4 / NR16B16e4last / NR16run2')
R = {}
for tag in ['raw_NR16B16e4', 'raw_NR16B16e4last', 'raw_NR16run2']:
    R[tag] = {}
    for snr in [-3, 0, 3, 6, 9, 12, 15]:
        rows, metas, chunks = load(tag, f'D2_C6_*_snr{snr}_*')
        R[tag][snr] = (rows, metas)
        ok = chunks == {(40 * k, 40) for k in range(64)}
        if tag != 'raw_NR16run2':
            mu = meta_uniform(metas, ['meta|ntrain', 'meta|bstar', 'meta|kron_K', 'meta|ll_val|kron', 'meta|em_sec', 'meta|stagec_ckpt_id', 'run|iters'])
            print(f'   {tag} snr {snr:+d}: chunks OK={ok} n={len(rows)} meta {mu}')
        else: print(f'   {tag} snr {snr:+d}: chunks OK={ok} n={len(rows)}')
b_, l_, r_ = R['raw_NR16B16e4'], R['raw_NR16B16e4last'], R['raw_NR16run2']
print('\n-- genie bit-identity across the three raw sets (KEYS_RAW; nmse NaN-aware):')
for snr in [-3, 0, 3, 6, 9, 12, 15]:
    print(f'   snr {snr:+d}: best vs run2 {ident(b_[snr][0], r_[snr][0], ["R5-genie"])}  last vs run2 {ident(l_[snr][0], r_[snr][0], ["R5-genie"])}')
print('-- arm-wise identity best vs last (max|diff| over KEYS_RAW), -3 dB:')
arms = sorted(set(k.split('|')[0] for k in b_[-3][0][0]))
print('  ', ident(b_[-3][0], l_[-3][0], arms))
print('\n-- failures @16 and decision points (anchor b*, BLER in [0.005,0.9], smallest |log10(BLER/0.1)|):')
def F_(rows, arm): return fails(rows, arm)[0]
bl = {snr: F_(b_[snr][0], 'M-ours-bstar').mean() for snr in b_}
cand = sorted([(abs(np.log10(v / 0.1)), snr) for snr, v in bl.items() if 0.005 <= v <= 0.9])
print('   b* BLER@16:', {s: round(v, 4) for s, v in bl.items()}, '-> decision SNRs', sorted(s for _, s in cand[:3]))
for tag, D in [('best', b_), ('last', l_), ('1e4', r_)]:
    tot = {}
    for snr in [-3, 0, 3]:
        rows = D[snr][0]
        fs = {a: F_(rows, a) for a in ['M-ours-bstar', 'M-ours-dscore-C-V1', 'R5-genie', 'M-ours-bstar-scalar', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b', 'M-ours-dscore-C-V0']}
        line = f'   [{tag}] {snr:+d} dB fails ' + ' '.join(f'{a.split("-")[-1]}={int(v.sum())}' for a, v in fs.items())
        for y in ['M-ours-dscore-C-V1', 'M-ours-bstar-scalar', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b']:
            a, bb, p, ph = st(fs['M-ours-bstar'], fs[y]); tot.setdefault(y, [0, 0]); tot[y][0] += a; tot[y][1] += bb
            line += f' | b*->{y.split("-")[-1]} {a}:{bb} p={ph:.2g}'
        Rr = (fs['M-ours-bstar'].sum() - fs['M-ours-dscore-C-V1'].sum()) / (fs['M-ours-bstar'].sum() - fs['R5-genie'].sum())
        print(line + f' | R={Rr:.3f}')
    print(f'   [{tag}] pooled: ' + ', '.join(f'{y.split("-")[-1]} {v[0]}:{v[1]} p={sign_p(*v):.2g}' for y, v in tot.items()))
print('\n-- best vs last V1 paired sign test (a = best fails & last ok):')
tot = [0, 0]
for snr in [-3, 0, 3]:
    a, bb, p, ph = st(F_(b_[snr][0], 'M-ours-dscore-C-V1'), F_(l_[snr][0], 'M-ours-dscore-C-V1')); tot[0] += a; tot[1] += bb; print(f'   {snr:+d} dB {a}:{bb} p={ph:.2g}')
print(f'   pooled {tot[0]}:{tot[1]} p={sign_p(*tot):.2g}')
print('\n-- recovery paired bootstrap reproduction (B=2000, seed 20260926, rng.integers(0,n,n), pct 5/95):')
def boot(cols, B=2000, seed=20260926):
    rng = np.random.default_rng(seed); n = len(cols[0][0]); out = np.empty(B)
    for i in range(B):
        idx = rng.integers(0, n, n); bs = sum(b[idx].sum() for b, _, _ in cols); vs = sum(v[idx].sum() for _, v, _ in cols); gs = sum(g[idx].sum() for _, _, g in cols)
        out[i] = (bs - vs) / (bs - gs) if bs - gs > 0 else np.nan
    ok = np.isfinite(out); return np.percentile(out[ok], [5, 95]), int((~ok).sum())
for tag, D in [('best', b_), ('last', l_), ('1e4', r_)]:
    cols = []
    for snr in [-3, 0, 3]:
        rows = D[snr][0]; c = (F_(rows, 'M-ours-bstar'), F_(rows, 'M-ours-dscore-C-V1'), F_(rows, 'R5-genie')); cols.append(c)
        (lo, hi), nn = boot([c]); print(f'   [{tag}] {snr:+d} dB R={(c[0].sum() - c[1].sum()) / (c[0].sum() - c[2].sum()):.3f} CI90 [{lo:.3f}, {hi:.3f}] undefined={nn}')
    (lo, hi), nn = boot(cols); B_, V_, G_ = (sum(c[i].sum() for c in cols) for i in range(3)); print(f'   [{tag}] pooled R={(B_ - V_) / (B_ - G_):.3f} CI90 [{lo:.3f}, {hi:.3f}]')
print('\n-- V0 guard rate per SNR (best tag) and any other arm firing:')
for snr in [-3, 0, 3, 6, 9, 12, 15]:
    rows = b_[snr][0]; t = sorted(rows)
    g = {a: np.nansum([float(rows[x].get(f'{a}|guardH', np.nan)) for x in t]) for a in arms if f'{a}|guardH' in rows[t[0]]}
    print(f'   {snr:+d} dB V0 {g["M-ours-dscore-C-V0"] / len(t):.3f}; others firing: {[a for a, v in g.items() if v > 0 and a != "M-ours-dscore-C-V0"]}')
print('\n-- BLER@16 at -3 dB (best):', {a.split('-')[-1]: round(F_(b_[-3][0], a).mean(), 4) for a in ['M-ours-dscore-C-V1', 'M-ours-dscore-C-V4', 'M-ours-dscore-C-V4b', 'M-ours-bstar', 'M-ours-bstar-scalar', 'R5-genie']})
