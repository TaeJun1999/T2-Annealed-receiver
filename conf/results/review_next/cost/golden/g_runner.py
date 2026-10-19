"""golden helper: runner-side values (no runner command is executed; module import only)."""
import os, sys
os.environ["CUDA_VISIBLE_DEVICES"] = ""
sys.path.insert(0, "/home/HTJ/t2/conf/code")
import common as C
import runner as R
for v in ("4,3,1,1", "4,3,1,1,0", "4,3,1,1,1"):
    print(f"parse_sparse_arms({v!r}) = {R.parse_sparse_arms(v)!r}")
for bad in ("4,3,1", "4,3,1,1,2"):
    try:
        R.parse_sparse_arms(bad); print(bad, "accepted (unexpected)")
    except ValueError as e:
        print(f"parse_sparse_arms({bad!r}) -> ValueError: {e}")
R.SPARSE = R.parse_sparse_arms("4,3,1,1")
print("_sparse_at(-3) =", R._sparse_at(-3.0), " _sparse_at(3) =", R._sparse_at(3.0))
for tag in ("COSTD2", "COSTU32K4096", "COSTU32GCAP"):
    R._init(tag); print(f"_init({tag!r}) -> arms.D2_FITS = {R.A.D2_FITS}")
print("N_ITER", C.N_ITER, "DEV_SKIP0", C.DEV_SKIP0, "C2", C.CELLS["C2"], "C9", C.CELLS["C9"])
