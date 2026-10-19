"""golden helper: checkpoint metadata (rung, hp, array, role/epochs, dtype of stored EMA weights)."""
import sys, torch
for p in sys.argv[1:]:
    st = torch.load(p, map_location="cpu", weights_only=False)
    ema = st.get("ema", {})
    dts = sorted({str(v.dtype) for v in ema.values()}) if hasattr(ema, "values") else "?"
    print(p)
    for k in ("rung", "attempt", "testbed", "prior", "Nr", "Nt", "role", "epoch", "best_epoch", "sigma_tag", "ntrain"):
        print(f"   {k:<11}= {st.get(k)!r}")
    print(f"   hp         = {st.get('hp')!r}")
    print(f"   ema dtypes = {dts}, n_params = {sum(v.numel() for v in ema.values()) if hasattr(ema, 'values') else '?'}")
    print(f"   keys       = {sorted(st.keys())}")
