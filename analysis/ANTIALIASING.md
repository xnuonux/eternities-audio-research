# The actual secret: antialiasing

**If you read one file, read this one.** Nearly every "why does the expensive one sound better"
question in this collection resolves here, not in the topology. Two plugins can implement the
same transfer curve and one sounds like iron and the other sounds like a fuzz pedal, entirely
because of how they handle the harmonics that land above Nyquist.

---

## The problem, stated precisely

Any nonlinearity generates harmonics. A `tanh` waveshaper fed a 5 kHz sine at 48 kHz sample rate
produces harmonics at 10, 15, 20, 25, 30 kHz… Everything above 24 kHz has nowhere to go, so it
**folds back** into the audible band at `fs − f`. The 30 kHz harmonic reappears at 18 kHz. The
35 kHz one at 13 kHz.

Folded harmonics are not harmonically related to the input. They move *downward* as you play
*upward*. That inharmonic, descending grit is the single most recognisable signature of cheap
digital saturation, and it is why naive `tanh` sounds harsh on cymbals and fine on bass.

Analog circuits have no Nyquist. There is nothing to fold. That is the whole gap you are closing.

---

## The four ways to solve it, in order of what they cost

### 1. Oversampling (brute force)

Run the nonlinearity at 4×/8×/16× rate, then decimate with a steep lowpass. Harmonics that would
have folded now land below the *new* Nyquist and get filtered out before downsampling.

- **Cost:** linear in the oversampling factor, plus the filters. 16× oversampling is 16× the
  nonlinear math.
- **Limit:** never eliminates aliasing, only pushes it down. 4× typically leaves audible artefacts
  on bright material; 16× is usually transparent for moderate drive.
- **The filters matter more than the factor.** A 4× design with steep polyphase FIR
  decimation beats an 8× design with a sloppy IIR. Polyphase decomposition is the standard
  trick — you only compute the filter taps that contribute to retained samples.
- **This is what most plugins do**, and it's why a saturation plugin's CPU meter jumps when you
  switch quality modes. FabFilter Saturn 2 exposes this directly as an oversampling selector.

### 2. Antiderivative antialiasing (ADAA) — the good one

This is the technique that separates the modern generation. Instead of evaluating the nonlinearity
pointwise, you evaluate its **antiderivative** at the sample endpoints and take the difference.

First-order ADAA for a nonlinearity `f(x)` with antiderivative `F₁(x)`:

```
y[n] = ( F₁(x[n]) − F₁(x[n−1]) ) / ( x[n] − x[n−1] )
```

with the removable singularity at `x[n] ≈ x[n−1]` handled by falling back to `f(x[n])` (or a
Taylor expansion) when the denominator is below a threshold. **That fallback is where almost
every implementation has a bug** — get the threshold wrong and you either divide by near-zero and
spray NaNs, or you snap to the pointwise path so often that ADAA does nothing.

Why it works: the difference quotient of the antiderivative is the *average* of `f` over the
interval between samples, not its instantaneous value. Averaging is a lowpass. You have
analytically integrated away the high-frequency content that would have folded.

- **Cost:** roughly 2× the pointwise version, vs 4–16× for oversampling. Enormously cheaper.
- **Second-order ADAA** (using `F₂`, the second antiderivative) suppresses further at ~3× cost.
- **Requires a closed-form antiderivative.** `tanh` has one: `F₁ = log(cosh(x))`. Hard clip has
  one, piecewise. An arbitrary lookup-table curve does not, which is why table-driven saturators
  fall back to oversampling.
- **Reference:** Parker, Zavalishin & Le Bivic, *"Reducing the Aliasing of Nonlinear Waveshaping
  Using Continuous-Time Convolution"*, DAFx-16. This paper is the single highest-value read in
  the whole subject.

**Combine them.** 2× oversampling plus first-order ADAA outperforms 8× oversampling alone at a
fraction of the cost. This is the default you should build.

### 3. Band-limited oscillators (for synths, the same problem upstream)

A naive sawtooth is a discontinuity, whose spectrum is infinite; sampling it aliases immediately
and catastrophically. Arturia's marketing term "TAE" is fundamentally about this.

- **BLIT** (band-limited impulse train) — sum band-limited impulses, integrate to get saw/square.
  Historically important, awkward in practice.
- **PolyBLEP** — the practical winner. Detect that a discontinuity fell *between* two samples,
  compute its fractional position, and add a small polynomial correction to the samples either
  side. Two samples of correction for a linear BLEP, four for cubic. Cheap, clean, easy to get
  right, and it's what most modern VA oscillators use.
- **Wavetable** — precompute one band-limited table per octave (or per few semitones), crossfade
  between them by pitch. Zero runtime aliasing cost, memory instead. This is Vital's approach and
  Pigments' wavetable engine.
- **DPW** (differentiated parabolic waveform) — integrate a polynomial, differentiate the result.
  Very cheap, decent, degrades at high pitch.

### 4. Just don't put it in the audio path

The often-forgotten option: if a nonlinearity only shapes a *control* signal (an envelope, a
detector, a modulation curve), it runs at control rate and cannot alias audibly. A large amount of
"analog character" in good plugins lives in control-path nonlinearity — program-dependent release,
detector curvature — where it is free.

---

## How to hear whether a plugin does this properly

This is directly measurable, and the harness in this repo automates it.

**The single-tone fold test.** Feed a sine at a frequency whose harmonics will clearly fold — e.g.
**7 kHz at 48 kHz**, so harmonics 4+ are above Nyquist. Drive the plugin hard. FFT the output.

- **Real harmonics** appear at exact integer multiples: 14 k, 21 k.
- **Aliased harmonics** appear at `|k·f − n·fs|` — for 7 kHz: the 4th harmonic (28 k) folds to
  20 kHz, the 5th (35 k) folds to 13 kHz, the 7th (49 k) folds to **1 kHz**.

A 1 kHz component from a 7 kHz input cannot be anything but aliasing. There is no ambiguity.

**The sweep test.** Sweep a sine 20 Hz → 20 kHz under heavy drive and look at the spectrogram.
Real harmonics sweep upward and vanish at Nyquist. Aliases sweep **downward**, crossing the real
harmonics. Those descending diagonals are the signature. Once you have seen them on a
spectrogram you will never un-hear them.

**What you'll find on your own shelf:** the difference between Kazrog True Iron and a stock DAW
saturator on this test is not subtle, and it is almost entirely this. Run it and keep the plots —
they are your acceptance criteria.

---

## What this means for our build

1. **Pick ADAA-friendly nonlinearities from the start.** Choose curves with closed-form
   antiderivatives (`tanh`, `atan`, polynomial, piecewise hard/soft clip) rather than designing a
   pretty lookup curve and discovering later that you cannot antialias it cheaply.
2. **Default to 2× oversampling + first-order ADAA.** Offer higher OS as a quality mode.
3. **Test aliasing in CI.** The fold test is automatable: synthesise 7 kHz, render, assert energy
   below 2 kHz is under a threshold. A regression that reintroduces aliasing should fail the
   build, not wait for someone's ears.
4. **Nonlinearity in the control path is free.** Spend the character budget there first.
