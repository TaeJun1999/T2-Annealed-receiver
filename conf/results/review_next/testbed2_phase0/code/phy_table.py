import json, glob, os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
print("cfg | seed | -3dB: K1 LO gap | closed K16/64/256 | +3dB gap | closed K16/64/256 | LSPO closed -3/+3 | LOS | cl/paths | erank ens, cond | beam top4/top8 | outage-3dB, MImed | leak iid frac<0.1, med | leak block frac, med | gen min/182920")
for f in sorted(glob.glob(os.path.join(D, "*.json"))):
    r = json.load(open(f)); h = r["headroom"]; a, b = h["all@-3dB"], h["all@+3dB"]
    cl = lambda x: "/".join(f"{x['closed'][k]:.2f}" for k in ("16", "64", "256"))
    lspo = f"{a['closed_LSPO']:.2f}/{b['closed_LSPO']:.2f}" if "closed_LSPO" in a else "-"
    lb = r.get("leak_block"); lbs = f"{lb['frac_lt01']:.3f}, {lb['med']:.2f}" if lb else "n/a"
    los = "-" if r["los_frac"] is None else f"{r['los_frac']:.2f}"; pc = "-" if r["paths_or_clusters"] is None else f"{r['paths_or_clusters']:.1f}"
    print(f"{r['cfg']}{'(lspo run)' if 'lspo' in f else ''} | {r['seed']} | {a['nmse']['K1']:.3f} {a['nmse']['LO']:.3f} {a['gap_K1_LO']:.3f} | {cl(a)} | {b['gap_K1_LO']:.3f} | {cl(b)} | {lspo} | {los} | {pc} | "
          f"{r['erank_ens']:.1f}, {r['cond_erank_LO']:.2f} | {r['beam_top4']:.2f}/{r['beam_top8']:.2f} | {r['outage_m3dB']:.3f}, {r['MI_m3dB_med']:.2f} | "
          f"{r['leak_iid']['frac_lt01']:.3f}, {r['leak_iid']['med']:.2f} | {lbs} | {r['gen_min_for_182920']:.2f}")
