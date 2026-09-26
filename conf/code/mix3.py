"""conf/code/mix3.py -- the SECOND testbed, standard-model side: 3GPP TR 38.901 "MIX3", prior id 'MIX3'.

User decisions 2026-09-26 (conf/DECISIONS.md 15:03 / 15:07 KST): the second testbed is a "boundary on both sides" mechanism
test -- SV8e (code/sv.py) on one side and 3GPP TR 38.901 MIX3 on the other, both pre-registered and reported whatever the
outcome; UNGATED checkpoints; GMM K grid stops at kron 4096.  MIX3 is the phase-0 probe configuration "MIX3_8"
(conf/results/review_next/testbed2_phase0/report_phy.md; probe code .../testbed2_phase0/code/phy_tb.py: sys_model, draw,
gen_3gpp_part).  It runs through the D2 pipeline as a prior VARIANT of testbed D2 (TBID 2), exactly like D3 = 'S2c' and
SV = 'SV8e': its own PID (7), so every MIX3 stream is a NEW stream, and 'MIX3' is in every output name (rung D2SXMIX3<N>,
ckpt d2sx_MIX3_*, fits fit_MIX3_Nr*_*, sigma grid sigma_grid_D2_MIX3).  common.make_gen / make_pilots dispatch here for
prior in C.MIX3_PRIORS; every other path is untouched (conf/code/selftest_mix3.py checks them bit for bit).

Channel model (Sionna 2.1 sionna.phy.channel.tr38901, sionna-no-rt 2.1.0) [every choice stated; = the probe]
    per block: scenario ~ Unif{UMi @ 28 GHz, UMa @ 28 GHz, RMa @ 3.5 GHz} (1/3 each), drawn from the numpy stream;
    arrays   : PanelArray 1 row x N columns (a single-column ULA), half-wavelength (PanelArray default spacing), single
               polarisation 'V', antenna_pattern 'omni'; BS Nr elements, UE Nt = 4; direction 'uplink' (UE -> BS);
    model    : UMi/UMa(o2i_model='low') / RMa, enable_pathloss=False, enable_shadow_fading=False, every other argument the
               Sionna default (spec_version 19.2, no spatial consistency, no blockage, LSPs drawn at set_topology);
    topology : gen_single_sector_topology(B, 1, scenario, indoor_probability=0.0) (one UE per drop, outdoor, BS at the
               sector-centred default yaw and scenario downtilt), then the UE orientation is OVERWRITTEN to
               yaw ~ U[-pi, pi), pitch = roll = 0; RMa in_car = False; los=None (38.901 LoS probability);
    snapshot : narrowband block fading, H = sum over the CIR paths at the first time sample (a[..., 0].sum(-1)),
               H[a, b] = BS antenna a, UE antenna b;  precision 'single' (Sionna default, as the probe), then complex128;
    norm     : ENSEMBLE normalisation E||H||_F^2 = Nr Nt: H = H_raw / sqrt(P_RAW), P_RAW = mean ||H_raw||_F^2 / (Nr Nt)
               over the TRAIN stream (common.train_rng('D2', 'MIX3', Nr, 7), n = N_CAL = 160000 = the equal-budget N'),
               measured ONCE by `python mix3.py calibrate` and frozen below as a literal (testbed_mix3.py TMXa re-derives
               it bit for bit).  Per-drop power keeps the model's K-factor / O2I variation (probe: same);
    vec      : h = vec(H) COLUMN-MAJOR, h[a + Nr b] = H[a, b]; complex128.
Probe differences (conventions only, the law is the same): the probe split its sets into exact thirds per scenario, here the
scenario is drawn per block; the probe drew the UE yaw from torch's GLOBAL generator, here from the seeded Sionna generator.

Determinism [the numpy stream is the only source of randomness].  Sionna draws every random number of this path from ONE
torch.Generator, sionna.phy.config.torch_rng('cpu') (Object.torch_rng; checked: no global torch / numpy / python RNG in
the 38.901 path).  Per CHUNK of blocks the stream gives (scenario codes, one 64-bit seed); that generator is seeded with the
seed, the chunk is generated scenario by scenario (UMi, UMa, RMa, each one batch of its blocks, each with a FRESH model so
nothing is carried between calls), and the generator state is restored afterwards.  torch runs single-threaded inside
(measured: 1 vs 96 threads changes the float32 bits); the thread count and torch's global CPU generator are restored.
Importing Sionna reseeds torch's global generator and initialises CUDA: it is imported lazily, once, with the global
generator state restored and torch.cuda.is_available() masked to False during the import (Sionna's device stays 'cpu',
no CUDA context is created).  Consequences:
    sample(rng)          = one block, a pure function of rng's state (2 draws: scenario, seed) -- independent of how many
                           blocks the process generated before (same contract as D2's sample);
    sample_vecs(rng, n)  = chunks of CHUNK blocks, a pure function of (rng state, n); CHUNK is part of the definition
                           (a Sionna batch is not batch-size invariant), and rows [0, CHUNK j) equal sample_vecs(rng, CHUNK j)
                           for every n >= CHUNK j; sample(rng) == sample_vecs(rng, 1)[0] (as a matrix).
Pilot decision: the D2 T2b rule of common.make_pilots on the transmit side Rt = E[H^H H] / Nr (and Rr = E[H H^H] / Nt),
estimated on the same N_CAL normalised training channels and frozen below (no closed form exists for 38.901).
Constants are calibrated for Nr = 8 x Nt = 4 only (cells C1/C2/C5/C7/C8); any other array raises -- it needs its own
`calibrate` and a decision.  The testbed is FROZEN by the user decision: change nothing here without a new decision and a
new prior id.
"""
import numpy as np

PRIORS = ("MIX3",)                        # == common.MIX3_PRIORS
SCEN = (("umi", 28e9), ("uma", 28e9), ("rma", 3.5e9))   # scenario code 0 / 1 / 2, drawn with probability 1/3 each
PRECISION = "single"                      # Sionna default (the probe); cast to complex128 afterwards
CHUNK = 4096                              # blocks per (scenario codes, seed) draw -- part of the stream definition
N_CAL = 160000                            # calibration set = train stream 7, the equal-budget N'

# ---- frozen calibration (python mix3.py calibrate, 2026-09-26; re-derived by testbed_mix3.py TMXa) ----------------------
P_RAW = {}                                # (Nr, Nt) -> mean ||H_raw||_F^2 / (Nr Nt) over the N_CAL training channels
RT = {}                                   # (Nr, Nt) -> Rt = mean H^H H / Nr   (normalised channels, Hermitian)
RR = {}                                   # (Nr, Nt) -> Rr = mean H H^H / Nt
TRAIN_SHA = {}                            # (Nr, Nt) -> sha256[:16] of sample_vecs(train stream 7, N_CAL) (determinism pin)
# frozen: calibrate Nr=8 x Nt=4, n=160000, 170 s  (python mix3.py calibrate 8)
P_RAW[(8, 4)] = 0.9953569092328413
TRAIN_SHA[(8, 4)] = '9f595676e0d1a032'
RT[(8, 4)] = np.array([[(1.0009332727414644+0j), (-0.27054562088274087+0.0002451063646198042j), (0.17259441930429084-0.0004109801294150752j), (-0.1280194642081623-0.0008503369308294897j)],
    [(-0.27054562088274087-0.0002451063646198042j), (1.0021623842548728+0j), (-0.2719093296670437+0.002376400298380673j), (0.17522299043441894+0.0008179034956510487j)],
    [(0.17259441930429084+0.0004109801294150752j), (-0.2719093296670437-0.002376400298380673j), (0.9990340788476292+0j), (-0.27042562184651286-0.0005263201596676682j)],
    [(-0.1280194642081623+0.0008503369308294897j), (0.17522299043441894-0.0008179034956510487j), (-0.27042562184651286+0.0005263201596676682j), (0.9978702641561333+0j)]])
RR[(8, 4)] = np.array([[(0.999736428697338+0j), (-0.007166625352446147+0.0022845227481888687j), (-0.06049177208651353-0.001348236822703462j), (0.056150877398057096+0.0016632383349925732j), (-0.04561545806741656+3.6949243885794374e-05j), (0.027018500425886015-0.0010221990199374377j), (-0.007969234443990522+0.00212636450483282j), (-0.00541527453983228-0.0005176571722800041j)],
    [(-0.007166625352446147-0.0022845227481888687j), (1.0018114123982662+0j), (-0.007160443162139199+0.002374664803387415j), (-0.060315148137301815-0.0018782236643798186j), (0.055568584260627205+0.0010990066564992766j), (-0.044927478143429934+0.0016166213189996556j), (0.027701523730895645-0.0023362838570884907j), (-0.00808731707289564+0.0023709609831948325j)],
    [(-0.06049177208651353+0.001348236822703462j), (-0.007160443162139199-0.002374664803387415j), (1.0008532819794096+0j), (-0.007089445596257415+0.00272922598804953j), (-0.06062827018884898-0.002150175133321894j), (0.054940383227647424+0.001067699918998112j), (-0.04596725162446934+0.0013187407342104723j), (0.02770421362317646-0.0017035991055400121j)],
    [(0.056150877398057096-0.0016632383349925732j), (-0.060315148137301815+0.0018782236643798186j), (-0.007089445596257415-0.00272922598804953j), (1.0013878905050857+0j), (-0.007155686304401635+0.0034206164498523017j), (-0.060363754886187455-0.0030029087157924647j), (0.05372724893360056+0.001459122477587414j), (-0.04615551840014244+0.00019437287485746263j)],
    [(-0.04561545806741656-3.6949243885794374e-05j), (0.055568584260627205-0.0010990066564992766j), (-0.06062827018884898+0.002150175133321894j), (-0.007155686304401635-0.0034206164498523017j), (1.0013395210673686+0j), (-0.0075764104103143185+0.0019377736118713562j), (-0.059948396232263806-0.0008621692327185646j), (0.055235885392043466+0.0016785524909191018j)],
    [(0.027018500425886015+0.0010221990199374377j), (-0.044927478143429934-0.0016166213189996556j), (0.054940383227647424-0.001067699918998112j), (-0.060363754886187455+0.0030029087157924647j), (-0.0075764104103143185-0.0019377736118713562j), (0.9993937772859388+0j), (-0.008024582171857373+0.0017522250973352454j), (-0.05922122858649884-0.0010042538983975734j)],
    [(-0.007969234443990522-0.00212636450483282j), (0.027701523730895645+0.0023362838570884907j), (-0.04596725162446934-0.0013187407342104723j), (0.05372724893360056-0.001459122477587414j), (-0.059948396232263806+0.0008621692327185646j), (-0.008024582171857373-0.0017522250973352454j), (0.9980497979998405+0j), (-0.007974050325738936+0.0020680437482211243j)],
    [(-0.00541527453983228+0.0005176571722800041j), (-0.00808731707289564-0.0023709609831948325j), (0.02770421362317646+0.0017035991055400121j), (-0.04615551840014244-0.00019437287485746263j), (0.055235885392043466-0.0016785524909191018j), (-0.05922122858649884+0.0010042538983975734j), (-0.007974050325738936-0.0020680437482211243j), (0.9974278900667911+0j)]])

_SL = None


def _sionna():
    """(torch, sionna.phy, {scenario: model class}, PanelArray, gen_single_sector_topology), imported once without
    touching CUDA or torch's global CPU generator (see the module docstring)."""
    global _SL
    if _SL is None:
        import torch
        from unittest import mock
        st = torch.get_rng_state()
        with mock.patch("torch.cuda.is_available", return_value=False):
            import sionna.phy as sp
            from sionna.phy.channel.tr38901 import UMi, UMa, RMa, PanelArray
            from sionna.phy.channel import gen_single_sector_topology
        torch.set_rng_state(st)
        assert sp.config.device == "cpu", sp.config.device
        _SL = (torch, sp, dict(umi=UMi, uma=UMa, rma=RMa), PanelArray, gen_single_sector_topology)
    return _SL


def _model(code, Nr, Nt):
    torch, sp, models, PanelArray, _ = _sionna()
    name, fc = SCEN[code]
    arr = lambda n: PanelArray(num_rows_per_panel=1, num_cols_per_panel=n, polarization="single", polarization_type="V",
                               antenna_pattern="omni", carrier_frequency=fc, precision=PRECISION, device="cpu")
    kw = dict(carrier_frequency=fc, ut_array=arr(Nt), bs_array=arr(Nr), direction="uplink", enable_pathloss=False,
              enable_shadow_fading=False, precision=PRECISION, device="cpu")
    if name != "rma":
        kw["o2i_model"] = "low"
    return models[name](**kw)


def _set_topology(m, code, B, G):
    """gen_single_sector_topology + the UE orientation overwrite (yaw ~ U[-pi, pi), pitch = roll = 0), as the probe."""
    torch, sp, _, _, gsst = _sionna()
    name = SCEN[code][0]
    tp = list(gsst(B, 1, name, indoor_probability=0.0, precision=PRECISION, device="cpu"))
    o = torch.zeros_like(tp[2])
    o[..., 0] = (torch.rand(o.shape[:-1], generator=G, dtype=o.dtype) * 2 - 1) * torch.pi
    tp[2] = o
    m.set_topology(*tp, los=None, **(dict(in_car=torch.zeros_like(tp[5])) if name == "rma" else {}))


def _snapshot(m, B, Nr, Nt):
    return m(1, 1.0)[0][..., 0].sum(-1).reshape(B, Nr, Nt).numpy().astype(np.complex128)


class _Seeded:
    """Seed Sionna's CPU generator, run torch single-threaded; restore the generator, the thread count and torch's global
    CPU generator on exit."""

    def __init__(self, seed):
        self.seed = seed

    def __enter__(self):
        torch, sp = _sionna()[:2]
        self.G = sp.config.torch_rng("cpu")
        self.saved = (self.G.get_state(), torch.get_num_threads(), torch.get_rng_state())
        torch.set_num_threads(1)
        self.G.manual_seed(self.seed)
        return self.G

    def __exit__(self, *exc):
        torch = _sionna()[0]
        self.G.set_state(self.saved[0])
        torch.set_num_threads(self.saved[1])
        torch.set_rng_state(self.saved[2])


def _generate(codes, seed, Nr, Nt, aux=None):
    """One chunk: codes (m,) scenario codes, seed -> (m, Nr, Nt) complex128 RAW channels.  aux (list) receives
    (code, block indices, LoS flags) per scenario batch (testbed_mix3.py)."""
    out = np.empty((len(codes), Nr, Nt), complex)
    with _Seeded(seed) as G:
        for code in range(len(SCEN)):
            ix = np.flatnonzero(codes == code)
            if len(ix):
                m = _model(code, Nr, Nt)                # FRESH model: no topology / LSP state carried between batches
                _set_topology(m, code, len(ix), G)
                out[ix] = _snapshot(m, len(ix), Nr, Nt)
                if aux is not None:
                    aux.append((code, ix, m._scenario.los.reshape(len(ix)).numpy().copy()))
    return out


class MIX3Gen:
    """MIX3 generator with the D2Gen slots the pipeline uses: .sample(rng), .sample_vecs(rng, n), .prior (None: no
    closed-form density or exact score, like D2), .name ("D2": it runs under testbed D2), .kind, .Nr/.Nt/.N."""

    name = "D2"
    prior = None

    def __init__(self, prior, Nr, Nt, raw=False):
        assert prior in PRIORS, f"MIX3 priors are {PRIORS}, got {prior!r}"
        if not raw and (Nr, Nt) not in P_RAW:
            raise ValueError(f"MIX3 is calibrated for {sorted(P_RAW)} only, not Nr={Nr} x Nt={Nt}: another array needs "
                             "`python mix3.py calibrate <Nr>` and a decision (mix3.py docstring)")
        self.kind = prior
        self.Nr, self.Nt, self.N = Nr, Nt, Nr * Nt
        self.s = 1.0 if raw else float(np.sqrt(P_RAW[(Nr, Nt)]))      # raw=True: calibration only

    def _draw(self, rng, n, aux=None):
        """n blocks (n, Nr, Nt), normalised; per CHUNK: scenario codes, then one uint64 seed, from rng."""
        out = np.empty((n, self.Nr, self.Nt), complex)
        for i in range(0, n, CHUNK):
            m = min(CHUNK, n - i)
            codes = rng.integers(0, len(SCEN), m)
            seed = int(rng.integers(0, 2 ** 64, dtype=np.uint64))
            sub = [] if aux is not None else None
            out[i:i + m] = _generate(codes, seed, self.Nr, self.Nt, sub) / self.s
            if aux is not None:
                aux += [(c, i + ix, los) for c, ix, los in sub]
        return out

    def sample(self, rng):
        return self._draw(rng, 1)[0]

    def sample_vecs(self, rng, n):
        """(n, Nr*Nt) complex128, row i = vec(H_i) column-major (== H.reshape(-1, order='F'))."""
        return self._draw(rng, n).transpose(0, 2, 1).reshape(n, self.N)


def ensemble_sides_mix3(prior, Nr, Nt):
    """(Rt, Rr, informative) -- same contract as d2.ensemble_sides_d2; Rt, Rr are the frozen training-set estimates
    (tr Rt = Nt, tr Rr = Nr up to the normalisation), informative = the T2b rule erank(Rt) < 0.9 Nt."""
    import d2
    assert prior in PRIORS, prior
    if (Nr, Nt) not in RT:
        raise ValueError(f"MIX3 ensemble sides exist for {sorted(RT)} only, not Nr={Nr} x Nt={Nt}")
    Rt = RT[(Nr, Nt)]
    return Rt, RR[(Nr, Nt)], bool(d2._erank(np.linalg.eigvalsh(Rt)) < d2.T2B_ERANK_FRAC * Nt)


def calibration_set(Nr, Nt):
    """The N_CAL RAW training channels (n, Nr, Nt) of train stream 7, exactly the draws training_set(ntrain=N_CAL) makes."""
    import common as C
    return MIX3Gen("MIX3", Nr, Nt, raw=True)._draw(C.train_rng("D2", "MIX3", Nr, 7), N_CAL)


def calibrate(Nr, Nt, H=None):
    """-> (P_RAW, Rt, Rr, sha) from the raw calibration set; sha is that of the NORMALISED vec set (= sample_vecs)."""
    import hashlib
    H = calibration_set(Nr, Nt) if H is None else H
    n = len(H)
    p = float(np.mean(np.sum(H.real ** 2 + H.imag ** 2, (1, 2)))) / (Nr * Nt)
    Hn = H / float(np.sqrt(p))
    Rt = np.einsum("nab,nac->bc", Hn.conj(), Hn) / (n * Nr)
    Rr = np.einsum("nab,ncb->ac", Hn, Hn.conj()) / (n * Nt)
    Rt, Rr = 0.5 * (Rt + Rt.conj().T), 0.5 * (Rr + Rr.conj().T)
    sha = hashlib.sha256(np.ascontiguousarray(Hn.transpose(0, 2, 1).reshape(n, Nr * Nt)).tobytes()).hexdigest()[:16]
    return p, Rt, Rr, sha


if __name__ == "__main__":
    import sys
    import time
    sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
    import common as C                    # noqa: F401  (thread env before numpy's BLAS is used)
    if sys.argv[1:2] == ["calibrate"]:
        Nr = int(sys.argv[2]) if len(sys.argv) > 2 else 8
        t0 = time.time()
        p, Rt, Rr, sha = calibrate(Nr, C.NT)
        lit = lambda A: "np.array([" + ",\n    ".join("[" + ", ".join(repr(complex(x)) for x in row) + "]" for row in A) + "])"
        print(f"# calibrate Nr={Nr} x Nt={C.NT}, n={N_CAL}, {time.time() - t0:.0f} s")
        print(f"P_RAW[({Nr}, {C.NT})] = {p!r}\nTRAIN_SHA[({Nr}, {C.NT})] = {sha!r}")
        print(f"RT[({Nr}, {C.NT})] = {lit(Rt)}\nRR[({Nr}, {C.NT})] = {lit(Rr)}")
