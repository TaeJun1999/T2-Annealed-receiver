"""Re-run the conference figure scripts (conf/code/figure_f*.py, unchanged) with plot titles removed, for LaTeX captions.
Monkeypatches matplotlib before each script runs: Axes.set_title keeps only a leading panel label such as "(a)" (bold, top
left) and drops the rest; Figure.suptitle is a no-op; a multi-panel figure whose titles had no "(x)" label at all gets
(a), (b), ... by panel position at savefig time.  Everything else (data, axes, legends, annotations, file names) is
the scripts' own.  The scripts live in the frozen conf/code (NSCALE run), so they are executed, not edited.
    ~/miniforge3/envs/torch/bin/python conference/tools/regen_notitle.py conf/code/figure_f16.py [...]
Outputs go where the scripts write them (conf/figs/); copy the F16-F32 files to conf/conference_plot/ afterwards.
"""
import re
import runpy
import sys

import matplotlib
matplotlib.use("Agg")
from matplotlib.axes import Axes
from matplotlib.figure import Figure

_set_title = Axes.set_title


def set_title(self, label="", fontdict=None, loc=None, pad=None, **kw):
    m = re.match(r"\s*(\([a-z]\))", str(label))
    size = kw.get("fontsize", (fontdict or {}).get("fontsize", 9))
    self._notitle_state = ("explicit" if m else ("pending" if str(label).strip() else "none"), size)
    return _set_title(self, m.group(1) if m else "", loc="left", fontweight="bold", fontsize=size)


_savefig = Figure.savefig


def savefig(self, *a, **k):
    """A multi-panel figure whose titles carried no "(x)" label at all (e.g. condition names only) gets (a), (b), ...
    by panel position (top row first, then left to right), so the caption can still refer to its panels."""
    st = [(ax, getattr(ax, "_notitle_state", ("none", 9))) for ax in self.axes]
    pend = [(ax, sz) for ax, (kind, sz) in st if kind == "pending"]
    if len(pend) >= 2 and not any(kind == "explicit" for _, (kind, _) in st):
        pend.sort(key=lambda t: (-round(t[0].get_position().y1, 3), round(t[0].get_position().x0, 3)))
        for i, (ax, sz) in enumerate(pend):
            _set_title(ax, f"({chr(97 + i)})", loc="left", fontweight="bold", fontsize=sz)
            ax._notitle_state = ("explicit", sz)
    return _savefig(self, *a, **k)


Axes.set_title = set_title
Figure.suptitle = lambda self, *a, **k: None
Figure.savefig = savefig

for script in sys.argv[1:]:
    print(f"[regen_notitle] {script}", flush=True)
    sys.argv = [script]
    runpy.run_path(script, run_name="__main__")
