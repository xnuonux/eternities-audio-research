# The expensive ones

**References:** Acustica Audio (Acqua) · Weiss DS1-MK3 · Kirchhoff-EQ · Manley Massive Passive ·
Shadow Hills Mastering Compressor · DMG EQuilibrium / Limitless · TDR Kotelnikov · SSL Bus
Compressor · Maag EQ4 · Sonnox Oxford Inflator · FabFilter Pro-C 3

What people actually pay premium prices for, and whether the premium is technical or reputational.
I'll say which, because it changes what's worth building.

**[doc]** documented · **[std]** standard · **[inf]** my inference.

---

## 1. Acustica Audio — a genuinely third approach to modelling

**This is the most technically distinct thing in the whole repo and it deserves attention.**

Everyone else does one of two things: **impulse response convolution** (captures linear behaviour
perfectly, captures nonlinearity not at all) or **circuit modelling** (captures nonlinearity, but
only as well as you understood the circuit).

Acustica does a third thing: **Volterra series dynamic convolution.** **[doc — their own
description]**

### The idea

A **Volterra series** expands a nonlinear system as a sum of convolutions of increasing order:

```
y(t) = ∫h₁·x  +  ∫∫h₂·x·x  +  ∫∫∫h₃·x·x·x  +  …
```

- `h₁` is the ordinary linear impulse response
- `h₂` captures second-order (even harmonic) behaviour
- `h₃` captures third-order, and so on

So you **sample the hardware at many levels and many frequencies**, extract the kernels, and
convolution with the full kernel set reproduces *both* the linear response and the level-dependent
harmonic behaviour — without ever knowing the circuit. **[std]** — Volterra series are
standard nonlinear-systems theory; the achievement is making them practical at audio rates.

### The trade-offs, honestly

- **CPU cost is notorious**, and it's inherent — you are convolving with several kernels, with
  level-dependent interpolation between kernel sets
- **latency** from the convolution
- **memory-less within each kernel order** — Volterra captures level-dependent nonlinearity well
  and long-term hysteresis poorly, which is why it's excellent on preamps and EQs and less
  compelling on tape
- **capture rigour is everything.** The product quality is a measurement-quality problem, not a
  DSP problem.

### Why this matters to us

**It's the sophisticated endpoint of the method this entire repo advocates.** We're measuring
harmonic profiles at several drive levels and fitting parameters by hand. Volterra is that same
measurement taken to its formal conclusion: measure enough, and the kernels *are* the model.

**[inf]** A realistic intermediate: capture harmonic amplitude-and-phase versus level and
frequency on a grid, and interpolate a waveshaper-plus-filter model against it. That's 80% of the
benefit at 10% of the CPU, and it's directly buildable from our harness output.

---

## 2. Weiss DS1-MK3 — the mastering standard, and why

~$250 for what is, functionally, a compressor, limiter and de-esser. **[inf]** The premium is
three things:

- **Very clean gain computation.** Mastering dynamics must not add character. Weiss's reputation
  is for doing nothing except what you asked.
- **Linear-phase crossovers** in the multiband modes, so band-splitting doesn't smear.
- **Digital heritage.** The hardware was digital, so the plugin is not an emulation with modelling
  compromises — it's a port. That's unusual and it's most of the marketing.

**Lesson:** in mastering, *transparency is the feature*. Every character decision we've discussed
in `SATURATION.md` is the wrong instinct here. The same team should not tune both.

---

## 3. Kirchhoff-EQ and DMG EQuilibrium — depth as the product

Both ~$200–250 for EQ, competing against FabFilter and free alternatives.

Their differentiator is **multiple filter prototypes per band** — you choose the *topology*, not
just frequency/gain/Q: analog-modelled curves, proportional-Q behaviours, several biquad variants,
different shelf shapes, matched-Z and linear-phase modes. Kirchhoff ships 32 bands and a
large prototype library. **[doc]**

### Why anyone pays for this

**Proportional Q** is the one to understand. On many classic analog EQs, bandwidth changes with
boost amount — a small boost is broad, a large boost narrows. That is a *consequence of passive
component topology*, not a design choice, and it's a large part of why an API 550 "feels"
different from a clean parametric at the same nominal settings. **[std]**

A modern parametric holds Q constant regardless of gain. Offering proportional-Q as a per-band
option is therefore offering an entire class of analog behaviour without emulating any specific
box.

**Lesson:** **the filter prototype library is reusable across every EQ product we'd ever ship.**
Build it once, properly, with matched-Z designs (per `FILTERS-AND-EQ.md`) and proportional-Q
variants, and it's permanent infrastructure.

---

## 4. Manley Massive Passive — where the character actually comes from

~$300 emulated. The character has a specific and unusual cause: **it's a passive EQ.**

The filters are **passive LC networks** with no gain of their own, followed by a make-up amplifier.
Consequences **[std]**:

- **bands interact.** A passive network's impedance is shared, so adjusting one band changes the
  others' curves. You cannot model it as independent cascaded biquads — that's the single most
  important fact about it.
- **boost and cut are asymmetric**, because they're different network configurations
- **the makeup amp is always working**, so its character is always present
- **Q behaviour is emergent** from component values, not a parameter

**To model it you must solve the network**, which is exactly what Wave Digital Filters are for
(`SATURATION.md` tier 3). This is the strongest argument in the repo for building a WDF framework:
**one WDF engine covers every passive EQ and every transformer**, where curve-fitting requires a
new model per device.

---

## 5. Shadow Hills — two topologies in series

The distinguishing feature is architectural rather than algorithmic: **an optical stage followed
by a discrete VCA stage**, each with its own controls, plus a **selectable output transformer**
(nickel / iron / steel). **[doc]**

Why series beats parallel here: the optical stage's slow program-dependent behaviour handles
overall level, then the discrete stage catches what got through with fast precise reduction. Two
different time-constant regimes, doing two different jobs.

**Lesson, and it's a good one:** per `DYNAMICS.md` we're building *one* compressor engine
parameterised on four decisions. **Two instances of that engine in series, with different
parameter sets, is a different and better product than either alone** — and it costs us nothing
extra. Ship it as a two-stage topology.

---

## 6. TDR Kotelnikov — free, and better than most paid ones

Worth studying precisely because it's free and excellent. **[doc]**

Its distinguishing features:

- **Separate peak and RMS detection paths with independent release times.** Not a blend — two
  detectors, each with its own ballistics, combined. This is a more sophisticated detector than
  most paid compressors and it's the main reason it sounds clean on a mix bus.
- **Proper stereo unlink**, with a controllable degree rather than a binary.
- **Careful attention to gain-smoothing curve shape**, which per `DYNAMICS.md` is where character
  actually lives.

**Lesson for pricing reality:** a competent compressor is free. **The dual-detector architecture is
the floor, not the ceiling** — if our compressor doesn't do at least what Kotelnikov does, it has
no reason to exist.

---

## 7. Sonnox Oxford Inflator — the famous mystery

~$150 for one knob, and it has been reverse-engineered and discussed publicly for years.

**[inf, widely reported]** The mechanism appears to be: split the signal, apply a specific
**second-order polynomial** waveshaping curve, and blend against the dry — with a "curve" control
that biases the polynomial's asymmetry. The result raises perceived loudness substantially with
very little measured peak increase, because it's adding low-order harmonics that read as loudness
rather than as distortion.

**Why it's worth naming:** it's proof that **a very simple nonlinearity, carefully chosen, beats a
complicated one.** The product is the specific curve and the blend, not the sophistication.

It also lands exactly on `IDEAS-2.md` §13 PRESENCE — Inflator gets perceived loudness from
harmonics; PRESENCE gets it from spectral redistribution. **Both at once would be a strong
product**, and they don't conflict.

---

## 8. Pro-C 3's styles, and the taxonomy confirmed

Pro-C 3 ships Clean, Classic, Opto, Vocal, Mastering, Bus, Punch, Pumping. **[doc]**

Those are not eight algorithms. They are eight points in the parameter space described in
`DYNAMICS.md` — detector position, detector type, knee shape, and ballistics including
program-dependence.

**This is direct confirmation that the four-decision taxonomy is the right abstraction.** FabFilter
built one engine and sold eight characters. So should we, and the measurement to prove it is
cheap: run `curve` + `envelope` on all eight styles and you will see the same engine moving
through its parameter space.

---

## What's technical and what's reputational

| | premium is | worth building toward |
|---|---|---|
| **Acustica** | **technical** — Volterra kernels are genuinely distinct | yes, in the reduced form |
| **Massive Passive** | **technical** — passive network interaction needs WDF | yes, via a WDF framework |
| **Kirchhoff / DMG** | **technical** — prototype library is real engineering | yes, it's reusable infrastructure |
| **Kotelnikov** | **technical** — dual detector, and it's free | **this is the floor to clear** |
| **Weiss** | **mixed** — genuinely clean, plus digital heritage | as a discipline, not a product |
| **Shadow Hills** | **architectural** — two topologies in series | yes, and it's nearly free for us |
| **Inflator** | **technical but tiny** — one well-chosen curve | yes, and it pairs with PRESENCE |
| **SSL / 1176 / LA-2A** | **reputational** — the taxonomy covers them | no, commodity |
| **Artist chains** | **taste** — and taste is real | yes, once processors exist |

---

## The three pieces of permanent infrastructure

Everything above reduces to three builds that make every future product cheaper:

1. **A filter prototype library** — matched-Z, proportional-Q, multiple shelf and bell topologies,
   linear-phase and minimum-phase modes. Serves every EQ we ever ship.
2. **A Wave Digital Filter framework** — one engine for passive networks and transformers. Unlocks
   Massive Passive, Pultec, every piece of iron, and it's the only route to devices whose bands
   interact.
3. **A measured-kernel saturation model** — harmonic amplitude *and phase* versus level and
   frequency, interpolated. The practical 80% of Volterra, built directly from our harness output.

None of those is a product. All three are why the next twelve products would take weeks instead of
months, and they're the reason to resist shipping a one-off emulation first.
