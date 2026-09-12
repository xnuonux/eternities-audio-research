# True Iron, deep

**You own it, so this is the one plugin in the repo you can fully characterise.** Six transformer
models, measurable at will. That makes it the best target in the collection for the
measure-then-build method, and this document is the protocol.

**[doc]** documented · **[std]** standard physics/literature · **[inf]** my inference.

---

## What a transformer is, physically, and why each part is audible

An audio transformer is two coils on a magnetic core. Primary current creates flux in the core;
changing flux induces voltage in the secondary. Every audible characteristic follows from a
non-ideality in that chain.

### The core relationship, and the one that matters most

```
Φ  ∝  ∫ v dt
```

Flux is the **time integral** of voltage. That integral is the single most important fact about
transformer sound, and here's the consequence in numbers:

For a sine of amplitude `V` at frequency `f`, peak flux is proportional to `V / f`.

So at equal voltage, **40 Hz produces 10× the peak flux of 400 Hz.** Which means:

> **Bass saturates first, and by a large margin. A model that saturates all frequencies equally
> is not modelling a transformer, whatever its harmonic profile looks like at 1 kHz.**

This is the thing most transformer plugins get wrong and it is *directly measurable* — see the
protocol below.

### The other four non-idealities

| property | cause | audible as |
|---|---|---|
| **hysteresis** | magnetic domains resist reorientation; B-H is a loop with memory | compression, level-dependent harmonics, and a *history* dependence a memoryless curve can't produce **[std]** |
| **core saturation** | finite `Mₛ`; beyond it flux stops increasing | the saturation knee itself, and where it sits vs frequency |
| **leakage inductance + winding capacitance** | imperfect coupling, inter-turn capacitance | an HF resonant peak then a rolloff — this is the "air" and the "sheen" **[std]** |
| **copper and core losses** | winding resistance, eddy currents, hysteresis loss | gentle LF rolloff, HF damping, mild overall compression |

### Why six models sound different

Not six different algorithms. **Six parameter sets over the same physics** — and knowing which
parameters differ tells you exactly what to expose:

- **core material** (nickel / steel / iron / mu-metal) → permeability and loop shape → saturation
  knee softness and harmonic balance
- **core size / mass** → total flux capacity → *where* saturation begins, and how frequency-skewed
  it is
- **turns ratio** → impedance transformation and level
- **winding geometry** → leakage inductance and capacitance → the frequency and Q of that HF
  resonance
- **input vs output role** → very different source and load impedances, which changes everything
  downstream

---

## The measurement protocol

This is the highest-value measurement in the whole repo, because it produces six complete
behavioural targets from a plugin you already own. Run it once, properly, and you have your
acceptance criteria for months.

### Step 1 — the frequency-dependent saturation map

**The test that proves whether it's really modelling a transformer.**

```bash
# for each of the 6 models, for each frequency, for each drive level
python measure.py --plugin ".../True Iron.vst3" --tests harmonics \
                  --out ../measurements/true-iron/model1
```

Sweep the tone frequency across **40, 60, 100, 200, 400, 1k, 2k, 5k Hz** and the input level
across **−30 to −1 dBFS in ~5 dB steps**, per model. For each cell record THD and the H2–H10
profile.

**What you're looking for:** THD at 40 Hz should be *substantially* higher than THD at 1 kHz at
the same input level. Plot THD as a surface over (frequency × level). **That surface is the
transformer's signature**, and matching it is the whole job.

If the surface is flat across frequency, True Iron isn't doing what it claims — which would itself
be worth knowing, and it's the kind of thing nobody checks.

### Step 2 — the even/odd map

From the same runs, extract `even_over_odd_db` per cell. Transformer distortion is usually
3rd-dominant (symmetric core behaviour) but real units are asymmetric to some degree. The
even/odd ratio *and how it moves with level* is a second signature, and it's what separates the
six models perceptually.

### Step 3 — the small-signal frequency response

```bash
python measure.py --plugin ".../True Iron.vst3" --tests response --out ...
```

At **low** drive, so the nonlinearity is barely engaged. This isolates the *linear* network:

- LF rolloff corner (primary inductance vs source impedance)
- **HF resonant peak** — its frequency and Q give you leakage inductance and winding capacitance
  directly
- the rolloff slope above it

Do this per model. These are your filter targets, and they're independent of the nonlinearity,
which makes them easy to fit.

### Step 4 — hysteresis, the hard one

Memoryless curves and hysteretic models can produce *identical* THD at steady state. They differ
on **transients and asymmetric waveforms**, because only the hysteretic one remembers.

Two discriminating tests:

- **Tone burst:** the first cycle after silence should behave differently from the tenth, if
  there's real hysteresis. Measure harmonic content cycle-by-cycle across the burst onset.
- **Asymmetric input:** feed a waveform with unequal positive and negative excursion (a sawtooth,
  or a sine plus DC offset) and compare against a memoryless model fitted to the same steady-state
  THD. Divergence there is hysteresis.

**[inf]** If True Iron shows no divergence, it's a filtered waveshaper — which would be useful
intelligence, because it means the tier-1 model in `SATURATION.md` gets you all the way there and
Jiles-Atherton is unnecessary.

---

## Building it, with the parameters mapped to what you hear

### Tier 1 — filtered waveshaper (do this first, it may be enough)

```
in → [pre-emphasis: +N dB/oct below f_c]  → nonlinearity(bias) → [de-emphasis: inverse]
   → [HF resonance + rolloff] → [DC blocker] → out
```

The pre/de-emphasis pair is what creates frequency-dependent saturation from a memoryless curve.
Set the pre-emphasis slope to match the flux relationship (flux ∝ 1/f means roughly **+6 dB/oct**
of LF emphasis into the nonlinearity) and you reproduce the core behaviour approximately.

**Fit against the Step 1 surface.** That's your loop: adjust emphasis slope and corner, re-measure,
compare surfaces.

### Tier 2 — Jiles-Atherton, and what each parameter does audibly

If Step 4 shows real hysteresis, this is the model. Five parameters, and this mapping is the part
that's hard to find written down **[std, with the audible mapping being my characterisation]**:

| parameter | physics | what you hear when you turn it up |
|---|---|---|
| **Mₛ** | saturation magnetisation | more headroom before saturation; moves the knee up in level |
| **a** | anhysteretic curve shape | softer, rounder knee; lower `a` = sharper transition |
| **α** | interdomain coupling | steepens the curve near the origin; affects low-level linearity |
| **k** | domain-wall pinning | **the width of the hysteresis loop** — more `k` = more memory, more compression, more level-dependent character |
| **c** | reversibility | how much behaviour is elastic vs hysteretic; higher `c` = closer to a memoryless curve |

`k` is the interesting one. **It is the parameter that makes it a transformer rather than a
curve**, and it's what you'd expose as "iron character."

Solve the ODE per sample with Newton-Raphson on the implicit form. Take the formulation from CHOW
Tape Model, which is open source and published — **do not re-derive it.** **[doc]**

### The ordering that matters

**Get antialiasing clean before you tune any of this.** If you fit Jiles-Atherton parameters
against a measurement while your own output has fold-back artefacts in it, you will be fitting
your model to your own aliasing, and the parameters you converge on will be wrong in a way that's
very hard to diagnose later.

`alias` test first, better than −70 dB, *then* fit.

---

## What success looks like

You have matched True Iron when, for a given model:

1. the **THD surface over (frequency × level)** matches within ~2 dB across the grid
2. the **even/odd ratio** tracks with level the same way
3. the **small-signal response** matches, including the HF resonance frequency and Q
4. the **transient/asymmetric divergence** from Step 4 is reproduced

Points 1 and 3 are straightforward fitting. Point 2 is a bias-control tune. **Point 4 is the one
that separates a real model from a good impression**, and it's the reason to run Step 4 before
deciding which tier to build.

Nothing in this process involves looking at anyone's code. It is measurement, physics, and
fitting — and it produces a model you understand, which a decompilation never would.
