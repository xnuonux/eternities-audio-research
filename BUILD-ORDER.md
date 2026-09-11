# Build order

Dependency-ordered, with an acceptance criterion per milestone that is **measured, not judged by
ear**. Ear comes after the number passes.

The sequencing rule throughout: **antialiasing before character, structure before presets.** Both
are cheap to get right first and expensive to retrofit, because every preset you tune depends on
them.

---

## M0 — the foundation nobody skips

**Build:** a plugin skeleton (JUCE or iPlug2, CLAP + VST3), a parameter system with smoothing, an
oversampling wrapper (2×/4×/8×/16× with polyphase decimation), and a test rig that renders offline
and asserts on the output.

**Accept when:** the oversampling wrapper is transparent — pass a full-band sweep through it with
no processing and the measured magnitude deviation is under 0.1 dB from 20 Hz to 20 kHz, and the
`alias` test on a linear gain reports better than −120 dB.

**Why first:** every later milestone is measured through this. If the wrapper colours the signal,
every measurement after it is wrong and you will chase ghosts.

---

## M1 — saturation

**Build:** `tanh` with first-order ADAA, inside 2× oversampling. Then, in order: bias + DC
blocker (asymmetry → even/odd control), pre/de-emphasis pair (frequency-dependent saturation), HF
loss shelf with a leakage resonance.

**Accept when:**
- `alias` at −1 dBFS input reports **better than −70 dB** inharmonic energy
- the ADAA singularity fallback is unit-tested: assert no NaN and no discontinuity when
  `x[n] == x[n−1]` exactly, and when the difference is at the threshold boundary
- `even_over_odd_db` moves monotonically across the asymmetry control's range
- LF saturates before HF: at fixed drive, THD at 60 Hz exceeds THD at 6 kHz by a measured margin

**Then fit:** measure True Iron across its six models at 5–6 drive levels. You now have six
harmonic-series targets. Adjust *your* parameters until your profile matches. Measure Decapitator
across its five styles for the tube/transistor axis.

**Reference to read:** the DAFx-16 ADAA paper, then CHOW Tape's source for where this goes next.

---

## M2 — filters

**Build:** TPT state-variable one-pole and two-pole. Then a 4-pole ladder with linear
zero-delay feedback. Then the nonlinearity inside the loop, solved with Newton-Raphson (capped
iterations, with a documented fallback).

**Accept when:**
- the linear filter's measured magnitude response matches the analog prototype **analytically**,
  not approximately, at 10 cutoffs spanning the range
- **the resonant peak lands at the requested cutoff at every cutoff** — this is the test naive
  unit-delay implementations fail, and it is the whole reason to do TPT
- self-oscillation frequency is correct at max resonance across the range
- Newton-Raphson iteration count is logged; you know your worst case and it is bounded

**Then fit:** measure Diva per filter model (Ladder, Cascade, Multimode, Bite, Uhbie) at several
cutoff/resonance points. Measure Pro-Q 4 per band type for the EQ side.

**Build the EQ with Vicanek matched-Z from the start**, not plain RBJ. Retrofitting the Nyquist
correction later means re-tuning every preset you have made.

**Reference to read:** Zavalishin, *The Art of VA Filter Design*. Cover to cover. It is the book
for this milestone.

---

## M3 — dynamics

**Build:** one engine parameterised on the four decisions — detector position (feed-forward /
feedback), detector type (peak / RMS / blend), knee (hard → soft width), ballistics (attack,
release, program-dependence). **Smooth gain in dB.** Do not write "an 1176" and "an LA-2A" as
separate code paths; they are two parameter sets.

**Accept when:**
- the measured static curve matches the intended knee exactly (this is a unit test)
- measured attack and release envelopes match the requested time constants within tolerance
- switching detector position from FF to FB visibly softens the measured ratio, as theory says it
  must
- no zipper noise under fast automation of threshold or ratio

**Then fit:** `curve` + `envelope` on LA-2A (expect a two-slope release — that's the optical
cell), Pro-C 3 across its styles, True Dynamics.

**Limiter after the compressor is proven:** lookahead with a *shaped* reduction envelope, and
ITU-R BS.1770-4 true-peak detection from day one. Accept when true-peak never exceeds the ceiling
on a program-material torture test, measured at 4× oversampling.

---

## M4 — reverb

**Build:** Schroeder baseline first (4 combs + 2 allpasses) purely as a reference point — it will
sound metallic, which is the lesson. Then an 8-line FDN, Householder matrix, mutually prime delay
lengths, one-pole damping per line. Then slow decorrelated modulation with **allpass**
interpolation. Then shelving damping for independent low/mid/high decay. Then pre-delay + early
reflection tap bank + allpass diffusion.

**Accept when:**
- **energy conservation:** set damping to unity and the tail neither decays nor grows over 30
  seconds. This catches a wrong feedback matrix immediately and is the highest-value early test
  in the whole project.
- measured RT60 falls with frequency (flat RT60 across octaves = under-damped)
- **the sustained-chord test:** a held piano chord through the pre-modulation version rings
  metallically; through the post-modulation version it does not. Same input, A/B the two builds.
- no audible pitch wobble on a sustained sine — if there is, the modulation is too deep or the
  modulators are correlated

**Then fit:** IR + octave-band RT60 + early/late energy ratio from the Valhalla trio, EMT 140,
EMT 250, Pure Plate. An IR plus its decay curves is very nearly a complete spec for a reverb, and
it is the easiest measurement in this repo to take.

---

## M5 — delay and modulation

Timeless 3, EchoBoy, PrimalTap, MicroShift, Crystallizer, PhaseMistress territory.

**Build:** fractional delay with high-quality interpolation, feedback path with filtering and
saturation, tempo sync, and a modulation system. Then pitch-shift (granular or phase-vocoder) for
MicroShift/Crystallizer behaviour.

**Accept when:** a modulated delay line adds no measurable aliasing of its own (this is where
linear interpolation fails), and a 100% feedback loop is stable indefinitely without runaway.

**Note:** short-delay detune (MicroShift) is perceptually enormous for very little DSP. High
value per unit effort — consider pulling it earlier.

---

## M6 — instrument

Only after M1/M2 are solid, because a synth is oscillators plus those filters.

**Build:** PolyBLEP oscillators (saw, square, pulse, triangle), then wavetable with per-octave
band-limited tables. Envelopes with analog-style curves. The M2 filter per voice. Voice
allocation and proper voice stealing.

**Accept when:** a single oscillator at the top of the keyboard range measures better than −70 dB
inharmonic energy. Naive oscillators fail this catastrophically and audibly.

**The architecture to take from Diva** is the architecture, not the code: independent,
swappable oscillator model × filter model × envelope model. That modularity *is* the product —
it's what lets one engine cover Minimoog, Jupiter and Juno character without three codebases.

---

## Cross-cutting, from day one

1. **Aliasing in CI.** The fold test is automatable: synthesise 7 kHz, render, assert energy
   below 2 kHz is under threshold. A commit that reintroduces aliasing should fail the build, not
   wait for someone's ears.
2. **Every measurement records its parameter state.** A measurement you cannot reproduce is an
   anecdote.
3. **Re-validate the harness when you change it.** The validation cases are in
   `harness/README.md` — linear gain, naive clip, oversampled clip, with expected numbers. A rig
   you have not tried to fool is not a rig.
4. **Nonlinearity in the control path is free.** No aliasing risk, real character. Spend there
   first, always.
5. **Keep the negative results.** A model you tried that did not match the measurement is
   information, and it is the thing most likely to be re-derived by the next person.
