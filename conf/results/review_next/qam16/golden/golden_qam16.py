#!/usr/bin/env python
"""Golden checks for the T2 receiver simulator's modulation (QPSK / 16-QAM) and block size.

Written from the spec only; no implementation code was read.
All checks are labelling-convention free (which bit goes to Re, whether 0 maps to +, bit order).

Public API
    check_K(m, Ns, K, nu=6)                       -> dict (ok, K_expected, coded_bits, reason)
    check_constellation(points, labels, atol)     -> dict (ok, fails, measured values)
    check_roundtrip(modulate, hard_demod, m, atol)-> dict (ok, fails, table check)

Self-test (reference + all Gray labellings of the 4x4 grid + negative tests + JSON values):
    taskset -c 6 ~/miniforge3/envs/torch/bin/python golden_qam16.py
"""
import itertools
import json
import math
import pathlib

import numpy as np

NU = 6  # memory of the (133,171)_8 code = number of tail bits
HERE = pathlib.Path(__file__).resolve().parent


# --------------------------------------------------------------------------- K
def check_K(m, Ns, K, nu=NU):
    """Rate-1/2 terminated CC: 2(K+nu) coded bits must fill Ns*m exactly, with K >= 1."""
    coded = Ns * m
    out = {"m": m, "Ns": Ns, "K": K, "coded_bits": coded}
    if coded % 2:
        return {**out, "ok": False, "K_expected": None,
                "reason": f"Ns*m={coded} odd: no integer K with 2(K+{nu})=Ns*m"}
    K_exp = coded // 2 - nu
    out["K_expected"] = K_exp
    if K_exp < 1:
        return {**out, "ok": False, "reason": f"K_expected={K_exp} < 1: block cannot hold {nu} tail bits + info"}
    if K != K_exp:
        return {**out, "ok": False, "reason": f"K={K} != {K_exp}: 2(K+{nu})={2 * (K + nu)} vs Ns*m={coded}"}
    return {**out, "ok": True, "reason": ""}


# ------------------------------------------------------------- constellation
def _bits(labels, m):
    """labels: (M,) ints in [0, 2^m) or (M, m) 0/1 array. Bit order is irrelevant to every check."""
    lab = np.asarray(labels)
    if lab.ndim == 2:
        return lab.astype(int)
    return (lab.astype(int)[:, None] >> np.arange(m)) & 1


def _expected_g(L):
    """1-D Hamming distance between Gray labels of two levels, as a function of |index difference|."""
    return {2: [0, 1], 4: [0, 1, 2, 1]}.get(L)


def check_constellation(points, labels, atol=1e-12):
    """points[k] carries label labels[k]. Square 2^m-QAM, m even, unit mean energy, axis Gray."""
    p = np.asarray(points, dtype=complex).ravel()
    M = p.size
    m = int(round(math.log2(M))) if M > 0 else 0
    L = int(round(math.sqrt(M)))
    if M < 4 or 2 ** m != M or L * L != M or m % 2:
        return {"ok": False, "fails": [f"M={M} is not a square QAM size (4, 16, 64, ...)"]}
    scale = math.sqrt(3.0 / (2.0 * (M - 1)))          # QPSK 1/sqrt2, 16-QAM 1/sqrt10
    dmin_exp = 2.0 * scale
    fails, res = [], {"M": M, "m": m, "L": L, "scale": scale}

    # 1. point set: every point is a grid point, all grid points used once
    ir = (p.real / scale + (L - 1)) / 2.0                # level index 0..L-1 (Re)
    ii = (p.imag / scale + (L - 1)) / 2.0
    r, i = np.rint(ir).astype(int), np.rint(ii).astype(int)
    grid = scale * ((2 * r - (L - 1)) + 1j * (2 * i - (L - 1)))
    res["max_grid_err"] = float(np.max(np.abs(p - grid)))
    on_grid = res["max_grid_err"] <= atol and r.min() >= 0 and i.min() >= 0 and r.max() < L and i.max() < L
    distinct = len(set(zip(r.tolist(), i.tolist()))) == M
    res["point_set_ok"] = bool(on_grid and distinct)
    if not res["point_set_ok"]:
        fails.append(f"point set: max_grid_err={res['max_grid_err']:.3e}, distinct={distinct}")

    # 2. energy, distance
    res["mean_energy"] = float(np.mean(np.abs(p) ** 2))
    res["Es_per_bit"] = res["mean_energy"] / m
    D = np.abs(p[:, None] - p[None, :])
    res["d_min"] = float(np.min(D[~np.eye(M, dtype=bool)]))
    if abs(res["mean_energy"] - 1.0) > atol:
        fails.append(f"mean energy {res['mean_energy']!r} != 1")
    if abs(res["d_min"] - dmin_exp) > atol:
        fails.append(f"d_min {res['d_min']!r} != {dmin_exp!r}")

    # 3. labels: bijection onto {0,1}^m
    B = _bits(labels, m)
    lab_int = np.asarray(labels)
    if lab_int.ndim == 1:
        res["labels_bijective"] = sorted(lab_int.astype(int).tolist()) == list(range(M))
    else:
        res["labels_bijective"] = B.shape == (M, m) and set(np.unique(B)) <= {0, 1} and len({tuple(b) for b in B}) == M
    if not res["labels_bijective"]:
        fails.append("labels do not use each of 0..M-1 exactly once")

    if not res["point_set_ok"]:                         # label checks below need a valid grid
        res["fails"], res["ok"] = fails + ["label/geometry checks skipped (point set invalid)"], False
        return res

    # 4. min-distance neighbours (by grid geometry, independent of the measured d_min) and Gray
    nb = (np.abs(r[:, None] - r[None, :]) + np.abs(i[:, None] - i[None, :])) == 1
    H = (B[:, None, :] != B[None, :, :]).sum(-1)
    cnt = nb.sum(1)
    res["neighbor_count_hist"] = {int(k): int(v) for k, v in zip(*np.unique(cnt, return_counts=True))}
    exp_hist = {2: 4} if L == 2 else {2: 4, 3: 4 * (L - 2), 4: (L - 2) ** 2}
    if res["neighbor_count_hist"] != exp_hist:
        fails.append(f"neighbour count histogram {res['neighbor_count_hist']} != {exp_hist}")
    a, b = np.nonzero(np.triu(nb))
    res["n_min_pairs"] = int(a.size)
    res["gray_violations"] = int(np.sum(H[a, b] != 1))
    if res["n_min_pairs"] != 2 * L * (L - 1):
        fails.append(f"n_min_pairs {res['n_min_pairs']} != {2 * L * (L - 1)}")
    if res["gray_violations"]:
        fails.append(f"Gray: {res['gray_violations']} of {res['n_min_pairs']} nearest pairs differ in != 1 bit")

    # 5. axis separation: each bit is a function of Re level only or of Im level only, m/2 each
    def depends_only_on(idx, j):
        return all(len(set(B[idx == v, j])) <= 1 for v in range(L))
    re_bits = [j for j in range(m) if depends_only_on(r, j) and not depends_only_on(i, j)]
    im_bits = [j for j in range(m) if depends_only_on(i, j) and not depends_only_on(r, j)]
    res["re_bits"], res["im_bits"] = re_bits, im_bits
    res["axis_separated"] = len(re_bits) == len(im_bits) == m // 2
    if not res["axis_separated"]:
        fails.append(f"axis separation: re_bits={re_bits}, im_bits={im_bits} (need {m // 2} each)")

    # 6. full Hamming matrix H(p,q) = g(|dr|) + g(|di|) (only fixed by geometry for L = 2, 4)
    g = _expected_g(L)
    if g is not None:
        G = np.array(g)
        Hexp = G[np.abs(r[:, None] - r[None, :])] + G[np.abs(i[:, None] - i[None, :])]
        res["hamming_matrix_mismatches"] = int(np.sum(H != Hexp))
        if res["hamming_matrix_mismatches"]:
            fails.append(f"Hamming matrix: {res['hamming_matrix_mismatches']} of {M * M} entries differ")

    res["fails"], res["ok"] = fails, not fails
    return res


# ----------------------------------------------------------------- round trip
def check_roundtrip(modulate, hard_demod, m, atol=1e-12):
    """modulate(bits (n*m,) 0/1) -> (n,) complex;  hard_demod((n,) complex) -> (n*m,) 0/1, same bit order.
    LLR demappers: wrap as hard_demod = lambda y: (llr(y) < 0).astype(int) (or > 0, per your sign rule)."""
    M = 2 ** m
    L = int(round(math.sqrt(M)))
    scale = math.sqrt(3.0 / (2.0 * (M - 1)))
    dmin = 2.0 * scale
    bits = ((np.arange(M)[:, None] >> np.arange(m)[::-1]) & 1).astype(int)   # label k, MSB first
    s = np.asarray(modulate(bits.ravel()), dtype=complex).ravel()
    fails = []
    if s.size != M:
        return {"ok": False, "fails": [f"modulate returned {s.size} symbols for {M * m} bits"]}
    table = check_constellation(s, bits, atol)          # implementation's own (point, label) table
    if not table["ok"]:
        fails.append(f"table: {table['fails']}")

    def demod(y):
        return np.asarray(hard_demod(np.asarray(y, dtype=complex)), dtype=int).reshape(-1, m)

    # (a) noiseless: bits -> symbol -> bits is identity
    n_a = int(np.sum(np.any(demod(s) != bits, axis=1)))
    # (b) perturbation 0.99 * dmin/2 along 8 directions (axis and diagonal; region is a square, so all inside)
    dirs = np.array([1, 1j, -1, -1j, 1 + 1j, 1 - 1j, -1 + 1j, -1 - 1j])
    y_b = (s[:, None] + 0.99 * (dmin / 2) * dirs[None, :]).ravel()
    n_b = int(np.sum(np.any(demod(y_b) != np.repeat(bits, dirs.size, axis=0), axis=1)))
    # (c) crossing: 51 % of the way to a nearest neighbour -> neighbour's label (1 bit away)
    r = np.rint((s.real / scale + (L - 1)) / 2).astype(int)
    i = np.rint((s.imag / scale + (L - 1)) / 2).astype(int)
    a, b = np.nonzero((np.abs(r[:, None] - r[None, :]) + np.abs(i[:, None] - i[None, :])) == 1)
    y_c = s[a] + 0.51 * (s[b] - s[a])
    d_c = demod(y_c)
    n_c = int(np.sum(np.any(d_c != bits[b], axis=1)))
    n_c1 = int(np.sum((d_c != bits[a]).sum(1) != 1))
    # (d) outward: corners x10, edge points pushed 5*dmin outward perpendicular to their edge
    out_r = (r == 0) | (r == L - 1)
    out_i = (i == 0) | (i == L - 1)
    push = np.where(out_r, np.sign(s.real), 0) + 1j * np.where(out_i, np.sign(s.imag), 0)
    keep = out_r | out_i
    y_d = np.concatenate([s[keep] + 5 * dmin * push[keep], 10 * s[out_r & out_i]])
    exp_d = np.concatenate([bits[keep], bits[out_r & out_i]])
    n_d = int(np.sum(np.any(demod(y_d) != exp_d, axis=1)))
    counts = {"noiseless": (n_a, M), "inside_0.99": (n_b, y_b.size), "cross_0.51": (n_c, y_c.size),
              "cross_not_1bit": (n_c1, y_c.size), "outward": (n_d, y_d.size)}
    for k, (bad, tot) in counts.items():
        if bad:
            fails.append(f"{k}: {bad} of {tot} wrong")
    return {"ok": not fails, "fails": fails, "errors": counts, "table": table}


# ------------------------------------------------------- reference mapper(s)
def ref_points_labels(m, conv="3gpp"):
    """One concrete convention (any other Gray square map must pass the same checks).
    3gpp: TS 38.211 5.1.3/5.1.4 form (from memory, text not re-checked):
      QPSK  d = ((1-2b0) + j(1-2b1))/sqrt2
      16QAM d = ((1-2b0)(2-(1-2b2)) + j(1-2b1)(2-(1-2b3)))/sqrt10
    alt: Re <- (b0 b1), Im <- (b2 b3), per axis 00,01,11,10 -> -3,-1,+1,+3 (MSB first)."""
    M = 2 ** m
    bits = ((np.arange(M)[:, None] >> np.arange(m)[::-1]) & 1).astype(int)   # b0 = MSB
    s = 1 - 2 * bits
    if m == 2:
        pts = (s[:, 0] + 1j * s[:, 1]) / math.sqrt(2)
    elif conv == "3gpp":
        pts = (s[:, 0] * (2 - s[:, 2]) + 1j * s[:, 1] * (2 - s[:, 3])) / math.sqrt(10)
    else:
        lv = {(0, 0): -3, (0, 1): -1, (1, 1): 1, (1, 0): 3}
        pts = np.array([lv[(b[0], b[1])] + 1j * lv[(b[2], b[3])] for b in bits]) / math.sqrt(10)
    return pts, np.arange(M)


def ref_modulate(m, conv="3gpp"):
    pts, _ = ref_points_labels(m, conv)
    w = 2 ** np.arange(m)[::-1]
    return lambda bits: pts[np.asarray(bits).reshape(-1, m) @ w]


def ref_hard_demod(m, conv="3gpp"):
    pts, lab = ref_points_labels(m, conv)
    B = ((lab[:, None] >> np.arange(m)[::-1]) & 1)
    return lambda y: B[np.argmin(np.abs(np.asarray(y)[:, None] - pts[None, :]), axis=1)].ravel()


def enumerate_gray_4x4():
    """All bijections 4x4 grid -> {0..15} with grid neighbours at Hamming distance 1."""
    sols, lab, used = [], [[-1] * 4 for _ in range(4)], [False] * 16
    cells = [(a, b) for a in range(4) for b in range(4)]

    def rec(k):
        if k == 16:
            sols.append([row[:] for row in lab])
            return
        a, b = cells[k]
        for v in range(16):
            if used[v] or (b and bin(v ^ lab[a][b - 1]).count("1") != 1) or (a and bin(v ^ lab[a - 1][b]).count("1") != 1):
                continue
            lab[a][b], used[v] = v, True
            rec(k + 1)
            lab[a][b], used[v] = -1, False
    rec(0)
    return sols


# ------------------------------------------------------------------ self-test
def _selftest():
    J = json.loads((HERE / "golden_qam16.json").read_text())
    tol = J["meta"]["tolerance"]["float64_abs"]
    C = {c["id"]: c for c in J["cases"]}
    log = []

    # C1 / B3: K
    for row in C["C1_K"]["rows"] + C["B3_K_boundary"]["rows"]:
        got = check_K(row["m"], row["Ns"], row["K_given"])
        assert got["ok"] == row["ok"], (row, got)
        assert got["coded_bits"] == row["coded_bits"] and got["K_expected"] == row["K_expected"], (row, got)
    log.append("C1/B3 check_K rows OK")

    # C2 / C3 / B1 / B2 / C5 on reference conventions
    for m, cid in [(4, "C2_qam16_geometry"), (2, "C5_qpsk")]:
        for conv in ("3gpp", "alt"):
            pts, lab = ref_points_labels(m, conv)
            got = check_constellation(pts, lab, tol)
            assert got["ok"], (m, conv, got["fails"])
            e = C[cid]["expected"]
            assert sorted(map(tuple, np.rint(np.c_[pts.real, pts.imag] / got["scale"]).astype(int).tolist())) == \
                sorted(map(tuple, e["points_times_inv_scale"]))
            assert abs(got["mean_energy"] - e["mean_energy"]) <= tol
            assert abs(got["d_min"] - e["d_min"]) <= tol
            assert abs(got["Es_per_bit"] - e["Es_per_bit"]) <= tol
            assert got["n_min_pairs"] == e["n_min_pairs"] and got["gray_violations"] == 0
            assert got["neighbor_count_hist"] == {int(k): v for k, v in e["neighbor_count_hist"].items()}
            assert got["hamming_matrix_mismatches"] == 0 and got["axis_separated"]
            # energy shells
            sh = {}
            for v in np.round(np.abs(pts) ** 2, 12):
                sh[float(v)] = sh.get(float(v), 0) + 1
            assert sh == {float(k): v for k, v in e["energy_shells"].items()}, sh
            # round trip through reference mod/demod
            rt = check_roundtrip(ref_modulate(m, conv), ref_hard_demod(m, conv), m, tol)
            assert rt["ok"], rt["fails"]
            assert {k: list(v) for k, v in rt["errors"].items()} == {k: [0, v] for k, v in C["C4_roundtrip"]["expected_trial_counts"][str(m)].items()}, rt["errors"]
    log.append("C2/C3/C4/C5/B1/B2 reference conventions (3gpp, alt) x (QPSK, 16-QAM) OK")

    for row in C["C1_K"]["rows"]:
        K = row["K_expected"]
        assert K / row["Ns"] == row["K_over_Ns"] and K / row["coded_bits"] == row["rate"]
    e2 = [check_constellation(*ref_points_labels(m), tol)["mean_energy"] for m in (2, 4)]
    assert abs(e2[0] - e2[1]) <= 2 * tol                  # B2
    pts16, lab16 = ref_points_labels(4)
    B16 = _bits(lab16, 4)
    Hh = (B16[:, None, :] != B16[None, :, :]).sum(-1)[np.triu_indices(16, 1)]
    hist = {str(k): int(v) for k, v in zip(*np.unique(Hh, return_counts=True))}
    assert hist == C["C3_gray"]["expected"]["hamming_hist_unordered"], hist
    D16 = np.abs(pts16[:, None] - pts16[None, :])[np.triu_indices(16, 1)]
    dmin = 2 / math.sqrt(10)
    assert np.sum((Hh == 1) & (np.abs(D16 - dmin) < 1e-9)) == 24 and np.sum((Hh == 1) & (np.abs(D16 - 3 * dmin) < 1e-9)) == 8

    # Hamming matrix golden (index form) from JSON
    g = C["C3_gray"]["expected"]["g_1d"]
    assert g == _expected_g(4)

    # C3 strength: every Gray labelling of the 4x4 grid
    sols = enumerate_gray_4x4()
    r, i = np.meshgrid(np.arange(4), np.arange(4), indexing="ij")
    pts = ((2 * r - 3) + 1j * (2 * i - 3)).ravel() / math.sqrt(10)
    n_ok = sum(check_constellation(pts, np.array(s).ravel(), tol)["ok"] for s in sols)
    assert len(sols) == C["C3_gray"]["expected"]["n_gray_labellings_4x4"] == n_ok, (len(sols), n_ok)
    log.append(f"C3 all {len(sols)} Gray labellings of 4x4 grid pass every check (separation + Hamming matrix implied)")

    # B4 / B5 negative tests
    neg = C["B5_negative"]["rows"]
    r1, i1 = r.ravel(), i.ravel()
    nat = (r1 << 2) | i1                                    # natural binary per axis
    got = check_constellation(pts, nat, tol)
    assert not got["ok"] and got["gray_violations"] == neg["natural_binary"]["gray_violations"]
    assert got["hamming_matrix_mismatches"] == neg["natural_binary"]["hamming_matrix_mismatches"], got
    assert got["axis_separated"]
    pts3, lab3 = ref_points_labels(4)
    dup = lab3.copy(); dup[1] = dup[0]
    got = check_constellation(pts3, dup, tol)
    assert not got["ok"] and not got["labels_bijective"]
    got = check_constellation(pts3 * math.sqrt(10), lab3, tol)
    assert not got["ok"] and abs(got["mean_energy"] - neg["unnormalized"]["mean_energy"]) <= 1e-9 and not got["point_set_ok"]
    got = check_constellation(pts3.astype(np.complex64), lab3, tol)
    assert not got["ok"], "complex64 should fail at 1e-12"
    assert check_constellation(pts3.astype(np.complex64), lab3, J["meta"]["tolerance"]["float32_abs"])["ok"]
    got = check_constellation(pts3[:15], lab3[:15], tol)
    assert not got["ok"]
    # buggy demod: decision thresholds of the unnormalised grid (0, +-2) on normalised symbols
    def bad_demod(y):
        y = np.asarray(y)
        lv = lambda x: np.select([x < -2, x < 0, x < 2], [-3, -1, 1], 3)
        z = (lv(y.real) + 1j * lv(y.imag)) / math.sqrt(10)
        return ref_hard_demod(4)(z)
    rt = check_roundtrip(ref_modulate(4), bad_demod, 4, tol)
    assert not rt["ok"] and rt["errors"]["noiseless"][0] == neg["bad_demod_thresholds"]["noiseless_symbol_errors"], rt["errors"]
    log.append("B4/B5 negative tests detected")
    print("\n".join(log))
    print("ALL GOLDEN CHECKS PASSED")


if __name__ == "__main__":
    _selftest()
