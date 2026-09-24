"""conf/code/fit_gpu_batched.py <fit_gpu.py arguments...> -- run fit_gpu.py with the batched exact kron M-step
(FIT_KRON_BATCHED=1) so the GPU queue (`python <script> <args>`) can launch it.  Use only after em_batched_check.py PASSED.
fit_gpu.py records kron_batched in every candidate / final file."""
import os
import runpy
import sys

os.environ["FIT_KRON_BATCHED"] = "1"
sys.argv = [os.path.join(os.path.dirname(os.path.abspath(__file__)), "fit_gpu.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
