# Filters and EQ

**Your references:** FabFilter Pro-Q 4 · Volcano 3 · Twin 3 · Simplon · Soundtoys FilterFreak
1/2 · u-he Diva · u-he Zebra3 · Avalon AD2077 · MHB Green/Red

This is the least mysterious category in the collection, and saying so is useful: **Pro-Q's
filters are not a secret. Pro-Q's product is its interface.** The math below is published, and
the reason people pay for Pro-Q is dynamic bands, per-band mid/side, spectrum-grab editing, and
EQ-matching — not a filter you cannot write.

The *synth* filters are a different story. That's where the real engineering is.

---

## Part 1: EQ. Solved math, and the two traps

### The baseline

The **RBJ cookbook** (Robert Bristow-Johnson) gives you closed-form biquad coefficients for
lowpass, highpass, bandpass, notch, allpass, peaking and both shelves, parameterised by `f₀`, `Q`
and gain. Cascade biquads in Direct Form I or a Transposed Direct Form II for better numerical
behaviour, and you have a working EQ in an afternoon. **[std]**

### Trap 1: the Nyquist-region gain error

Bilinear-transform biquads are *warped*. The analog prototype's response is compressed onto the
digital frequency axis, so a bell centred at 16 kHz at 44.1 kHz does not have the gain or
bandwidth you asked for — the error grows as `f₀ → fs/2`. A high shelf can end up with visibly
wrong gain right where it matters most on a mix bus.

Three fixes, in increasing quality:

- **Oversample the EQ.** Works, wasteful.
- **Orfanidis peaking design** — corrects the gain at Nyquist by matching the analog response at
  DC, `f₀` and Nyquist. The classic reference. **[std]**
- **Vicanek matched-Z / "matched biquad"** — designs directly in the Z domain to match the analog
  *magnitude* response, including the Nyquist region, for peaking, shelving and lowpass forms.
  This is the current best practice and it is cheap. **[std]**

**[inf]** Pro-Q's "Natural Phase" mode is very likely doing something in this family, since it
claims analog-matched magnitude *and* a defined phase behaviour that isn't minimum-phase biquad.

### Trap 2: modulating coefficients

Recompute biquad coefficients per-sample while a user drags a frequency and you get zipper noise
or worse — Direct Form structures are not designed for time-varying coefficients and can ring or
blow up. Options: smooth the *parameters* and recompute at a control rate with interpolated
coefficients; or use a **topology-preserving transform (TPT)** state-variable filter, which is
stable under modulation by construction. For anything automatable, use TPT. **[std]**

### The three EQ modes, and what they cost

| mode | implementation | latency | phase |
|---|---|---|---|
| **Zero latency** | cascaded biquads | none | minimum phase |
| **Natural phase** | matched-magnitude biquads | none | analog-like |
| **Linear phase** | FFT partitioned convolution | high (block-dependent) | perfectly linear |

Linear phase costs pre-ringing on transients — a symmetric impulse response smears energy
*before* the hit. That's why it's right for mastering and wrong for drums.

### Dynamic EQ

A band whose gain is modulated by an envelope follower on the band's own filtered signal. That is
the entire mechanism. **Dynamic EQ and multiband compression are the same machine** differing in
presentation: dynamic EQ = bell shapes with a threshold; multiband comp = crossover-split bands
with ratios. Pro-Q 4 and Pro-MB are two UIs over one idea. **[inf]**

---

## Part 2: synth filters. Here's the actual engineering

This is where Diva earns its reputation and where the difficulty lives.

### Why a naive resonant filter sounds wrong

Take a digital lowpass, add feedback for resonance, put a `tanh` in the feedback path for
"analog" drive. You now have a **delay-free loop**: the output depends on the output, in the same
sample. Naive implementations insert a one-sample delay in the feedback path to make it
computable. That unit delay:

- detunes the resonant peak, increasingly at high cutoff
- makes self-oscillation frequency wrong and cutoff-dependent
- changes the resonance character as cutoff sweeps
- can go unstable at high resonance and high cutoff

Every one of those is audible, and collectively they are why cheap VA filters sound "phasey" or
"thin" when you sweep them with resonance up. **[std]**

### The fix: zero-delay feedback via TPT

Zavalishin's **topology-preserving transform** discretises each integrator individually
(trapezoidal / bilinear) rather than the whole transfer function, keeping the analog topology
intact. The delay-free loop is then solved *algebraically* per sample for a linear filter.

The canonical TPT one-pole:
```
g = tan(π · fc / fs)          // pre-warped cutoff
v = (x − s) · g / (1 + g)     // the instantaneous solve
y = v + s
s = y + v                     // state update
```
Cascade four of those with a global feedback path and you have a Moog ladder whose resonant peak
lands where it should at every cutoff.

**Reference: Vadim Zavalishin, "The Art of VA Filter Design."** Free PDF, and he is Native
Instruments' DSP lead. It is the definitive text on exactly this, and it is the single most
valuable document for building competitive synth filters. **[doc]**

### Nonlinear ZDF — the part that is genuinely hard

Put a saturator inside the ladder (which is what the real transistor ladder does — the transistors
*are* the nonlinearity) and the loop is no longer algebraically solvable. You must solve an
**implicit nonlinear equation per sample**:

- **Newton-Raphson**, 2–5 iterations, with the derivative of your nonlinearity in closed form.
  Converges fast for `tanh`. Needs an iteration cap and a fallback or a pathological input can
  stall it.
- **Fixed-point iteration** — simpler, slower convergence, sometimes divergent.
- **Lookup the solution** — precompute the implicit solve over a 2D grid. Fast, memory-hungry,
  awkward to modulate.

**[inf] This is almost certainly why Diva's CPU cost is what it is, and why it has explicit
quality modes.** Its "divine" setting is plausibly more solver iterations and/or higher
oversampling. A synth that solves a nonlinear implicit system several times per sample per voice
is simply expensive, and that expense is the sound.

### The filter models in your Diva, and their circuit lineage **[doc]**

Diva names them in the UI, and the lineage is the point:

| Diva model | original | topology |
|---|---|---|
| **Ladder** | Moog | 4-pole transistor ladder, nonlinear feedback |
| **Cascade** | Moog-adjacent | cascaded poles, different drive staging |
| **Multimode** | Oberheim SEM | 2-pole state-variable, LP/BP/HP continuous |
| **Bite** | Korg MS-20 | Sallen-Key, aggressive self-oscillation |
| **Uhbie** | Roland IR3109 | 4-pole OTA, the Juno/Jupiter voice |

Same for its oscillator sections — Triple VCO (Minimoog), Dual VCO (Jupiter), DCO (Juno), and a
digital model. **The architectural insight worth stealing is the architecture itself, not the
code:** mix-and-match oscillator model × filter model × envelope model, each an independent
circuit emulation. That modularity is the product.

---

## Build order for our filter

1. **TPT state-variable one-pole and two-pole**, linear. Verify the frequency response against
   the analog prototype analytically — not by ear.
2. **Four-pole ladder with linear ZDF.** Verify the resonant peak tracks cutoff correctly across
   the whole range, and that self-oscillation frequency is right. This is the test naive
   implementations fail.
3. **Add the nonlinearity with Newton-Raphson.** Cap iterations. Measure how many it actually
   takes at various drive levels — that number is your CPU budget.
4. **Then** the EQ, using Vicanek matched-Z from the start rather than plain RBJ, because
   retrofitting the Nyquist correction later means re-tuning every preset.
5. **Measure Pro-Q 4** with the harness: swept sine per band type at several Q and gain settings
   → magnitude and phase targets. Measure **Diva** per filter model at several cutoff/resonance
   points → resonance shape and self-oscillation targets.

The ordering is deliberate. Filters are the one place where getting the structure right first is
cheaper than fixing it later, because every preset you make depends on the response being correct.
