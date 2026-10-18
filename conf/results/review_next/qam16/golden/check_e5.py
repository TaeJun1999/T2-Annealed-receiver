"""Golden cases (golden-writer, spec only) against the runner's modulation objects in ~/t2_wtE5 (QAMCode via common.MOD_BITS)."""
import sys
sys.path.insert(0, "/home/HTJ/t2_wtE5/conf/code"); sys.path.insert(0, sys.argv[1])
import numpy as np
import common as C
import golden_qam16 as Gd
ok = True
for mod in ("qpsk", "16qam"):
    m = C.MOD_BITS[mod]; code = C.QAMCode(C.GENS, C.NU, m, 48)
    P, B = np.asarray(code.st.CONST), np.asarray(code.st.CBITS)
    idx = (B * (1 << np.arange(m - 1, -1, -1))).sum(1) if B.ndim == 2 else B      # label = MSB-first integer
    pt = {int(i): P[k] for k, i in enumerate(idx)}
    modulate = lambda bits: np.array([pt[int((b * (1 << np.arange(m - 1, -1, -1))).sum())] for b in np.asarray(bits).reshape(-1, m)])
    hard = lambda y: np.concatenate([(int(idx[np.argmin(np.abs(P - v))]) >> np.arange(m - 1, -1, -1)) & 1 for v in np.atleast_1d(y)])
    r = [Gd.check_K(m, 48, code.K), Gd.check_constellation(P, B), Gd.check_roundtrip(modulate, hard, m)]
    ok &= all(x["ok"] for x in r)
    print(mod, "K", code.K, "|", " | ".join(f"{n} {'PASS' if x['ok'] else 'FAIL ' + str(x.get('fails') or x.get('reason'))}"
                                        for n, x in zip(("K", "constellation", "roundtrip"), r)))
print("ALL PASS" if ok else "FAILURES")
