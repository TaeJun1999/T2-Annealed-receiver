"""conf/code/fit_gpu_sparse.py TOL <fit_gpu.py arguments...> -- run fit_gpu.py with the opt-in sparse kron M-step
(FIT_SPARSE_TOL=TOL) so the GPU queue (which runs `python <script> <args>`) can launch it.  NEXT_EXPERIMENTS_B32e4
speed-up; use only after em_sparse_check.py has PASSED.  fit_gpu.py records sparse_tol / sparse_max_dropped in every file."""
import os
import runpy
import sys

os.environ["FIT_SPARSE_TOL"] = sys.argv[1]
sys.argv = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_gpu.py")] + sys.argv[2:]
runpy.run_path(sys.argv[0], run_name="__main__")
