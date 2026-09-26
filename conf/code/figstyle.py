"""conf/code/figstyle.py -- shared colour/marker roles for the manuscript figures (F16-F18).

Categorical slots are the dataviz reference palette (blue / orange / aqua / violet), validated all-pairs on a white
surface with the dataviz validator (CVD dE >= 9.2, normal-vision dE >= 16.3; aqua is 2.74:1 against white, so every
aqua series also carries a legend entry and a direct label or tick label).  Colour follows the ENTITY: the same arm keeps
the same colour in every figure.  Neutral references (genie, Gaussian) are ink / grey, not categorical hues.  Text is
always ink (INK / INK2), never a series colour.
"""
INK, INK2, SHADE = "#0b0b0b", "#52514e", "#f0efec"
V1 = dict(color="#2a78d6", marker="s", ls="-")               # learned diffusion prior (proposed), incl. frozen V1 in F18
GMM = dict(color="#eb6834", marker="D", ls="-")              # GMM b*; GMM variants reuse the colour with other markers
GENIE = dict(color=INK, marker="*", ls="-.")                 # known-channel reference (R5)
GAUSS = dict(color="#7a7974", marker="o", ls="--")           # Gaussian sample-covariance prior (R2)
EDGE = dict(color="#1baf7a", marker="o", ls="-")             # V1-edge (registered out-of-grid rule); V1-clamp = hollow, dashed
CELL_C2 = dict(color="#3d3c39", ls="-")                      # cell identity in budget/recovery panels
CELL_C6 = dict(color="#4a3aa7", ls="--")
