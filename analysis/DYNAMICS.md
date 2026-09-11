# Dynamics: compressors, limiters, gates

**Your references:** FabFilter Pro-C 3 · Pro-L 2 · Pro-MB · Pro-G · Pro-DS · UAD Teletronix LA-2A ·
UAD Century Channel Strip · Retro Sta-Level · Kazrog True Dynamics · Soundtoys DevilLoc ·
Cradle The God Particle

**The headline:** a compressor is four independent design decisions, and "which compressor sounds
like what" is almost entirely determined by them. Get the taxonomy right and you can build any of
them.

---

## The four decisions

### 1. Detector position: feed-forward vs feedback

- **Feed-forward** — measure the *input*, compute gain, apply it. Predictable, exact ratios,
  what almost all digital compressors do.
- **Feedback** — measure the *output* (post-gain-reduction) and feed that back to the detector.
  The ratio becomes soft and level-dependent, the knee rounds itself, and very high ratios become
  gentle rather than brutal.

**This is the single biggest "vintage vs modern" divider.** The LA-2A is feedback-driven; its
famously forgiving, self-softening behaviour is largely this, not the optical cell alone. A
feed-forward compressor set to the LA-2A's nominal ratio will not behave like one. **[std]**

### 2. Detector type: peak vs RMS vs true-peak

- **Peak** — instantaneous absolute value. Fast, catches transients, reads nothing like loudness.
- **RMS** — windowed energy. Tracks perceived level, misses transients entirely.
- **Hybrid** — most good compressors blend, or run both and take the max.
- **True peak (ITU-R BS.1770-4)** — 4× oversampled peak detection to catch inter-sample peaks
  that a sample-rate peak detector misses. **Mandatory for a limiter**, because inter-sample peaks
  clip D/A converters and lossy encoders even when every sample is below 0 dBFS. **[doc]**

### 3. Gain computer: the knee

Hard knee: `GR = (level − threshold) · (1 − 1/ratio)` above threshold, zero below. Audible as a
"grab."

Soft knee interpolates over a width `W` centred on threshold, usually with a quadratic:
```
if      2(x − T) < −W    →  no reduction
else if 2|x − T| ≤ W     →  quadratic blend region
else                     →  full ratio
```
The quadratic is C¹ continuous, which is what matters — a discontinuity in the *derivative* of the
gain curve is audible even when the curve itself is continuous. **[std]**

### 4. Ballistics: attack and release

This is where character actually lives, and where cheap compressors are cheap.

- **Linear** (fixed dB/s) — sounds mechanical.
- **Exponential** (one-pole smoother, fixed time constant) — the default, `α = exp(−1/(τ·fs))`.
- **Dual-stage / program-dependent** — fast stage catches transients, slow stage handles
  sustained material, and the blend depends on how long the signal has been over threshold.
  **This is the "auto release" in most vintage emulations and it is most of what makes them feel
  musical.** The LA-2A's optical cell has an inherently two-time-constant recovery (fast initial,
  long tail) because of the photoresistor's physics. **[std]**
- **Asymmetric on program material** — release that adapts to crest factor.

**The real trick:** smooth the **gain in dB**, not the linear gain, and not the detector output.
Smoothing linear gain gives you a different (and worse) curve shape for the same time constant.
This is a one-line difference that changes the whole feel. **[std]**

---

## Optical vs VCA vs FET vs vari-mu

| type | mechanism | signature | how to model |
|---|---|---|---|
| **Optical** (LA-2A, Sta-Level-adjacent) | lamp + photoresistor | slow, program-dependent two-stage release, very forgiving | dual time constant, feedback detector, level-dependent release |
| **VCA** (SSL, dbx) | voltage-controlled amp | precise, fast, clean | feed-forward, straightforward ballistics |
| **FET** (1176) | FET as variable resistor | very fast attack, aggressive, distorts when driven | fast attack, add a nonlinearity in the gain element |
| **Vari-mu** (Fairchild, Manley) | tube bias shifts gain | ratio increases with level, self-softening | feedback + level-dependent ratio |

**The crucial point:** these differ by *topology and ballistics*, not by a mystery ingredient.
Implement the four decisions as parameters and you can position anywhere in this table.

---

## Limiting — Pro-L 2 territory

A limiter is a compressor with ratio ∞, near-zero attack, and **lookahead**.

- **Lookahead** = delay the audio by N samples while the detector runs un-delayed, so gain
  reduction is already applied when the peak arrives. Costs exactly N samples of latency; there
  is no way around that trade.
- **The gain envelope must be smooth.** A rectangular or linear ramp to the required reduction
  creates its own distortion — you're multiplying by a signal with sharp corners, which is
  modulation with wideband sidebands. Good limiters shape the reduction envelope (raised cosine,
  or higher-order smoothing) over the lookahead window. **[inf] Pro-L 2's several "styles" are
  most plausibly different envelope shapes and multiband splits rather than different detectors.**
- **True peak is not optional.** Sample-peak limiting to −0.1 dBFS routinely produces +0.5 dB
  true-peak overshoots.
- **Oversample the whole limiter** or the gain modulation itself aliases.

---

## Multiband — Pro-MB territory

Split into bands, compress each, sum. The only hard part is the **crossover**:

- **Linkwitz-Riley** (cascaded Butterworth, even order) sums flat in magnitude — the standard
  choice. LR4 is the workhorse.
- **Allpass-complementary** designs sum perfectly at the cost of phase.
- **Naive Butterworth crossovers do not sum flat** and you get a dip or bump at every crossover
  point. This is a classic beginner bug and it's immediately visible in a measurement.

Then: as noted in `FILTERS-AND-EQ.md`, multiband compression and dynamic EQ are the same machine.
Build one engine, present it twice.

---

## De-essing — Pro-DS territory

Not simply a bandpassed compressor. The good ones detect sibilance by comparing **high-band energy
to total energy** (a ratio, so it tracks regardless of overall level) and then reduce either
just the high band or the whole signal. Broadband reduction preserves timbre better on vocals;
band-limited reduction is more surgical. **[inf]**

---

## "The God Particle" **[inf]**

Cradle's plugin is a one-knob mastering chain — almost certainly a fixed, curated cascade
(saturation → multiband dynamics → EQ contour → limiting) with one macro. The product is the
*curation*, which is a genuinely legitimate thing to compete on and needs no reverse engineering
at all: it needs taste, and a measurement of what the curve does at each knob position. Measure
it at 10 settings and you have its entire behaviour as a spec.

---

## Build order for our compressor

1. **One engine, parameterised on the four decisions.** Detector position (FF/FB), detector type
   (peak/RMS/blend), knee (hard→soft width), ballistics (attack, release, program-dependence).
   Do not build "an 1176" and "an LA-2A" as separate code.
2. **Smooth gain in dB.** Get this right at the start.
3. **Verify the static curve** by measuring your own plugin: input a slow level ramp, plot
   output-vs-input. It should match your intended knee exactly. This is a unit test, not an ear
   test.
4. **Then ballistics:** feed a burst and measure the actual attack and release envelopes. Assert
   them against the requested time constants.
5. **Measure the references.** LA-2A, Pro-C 3, True Dynamics: level ramp → static curve; tone
   bursts → envelope shapes; sine at several levels → harmonic content of the gain element. That
   is a complete behavioural description of a compressor, and it's what you fit to.
6. **Limiter last**, on top of the proven compressor, with true-peak detection and a shaped
   reduction envelope from day one.
