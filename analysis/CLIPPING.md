# Clipping

**References you own:** Kazrog KClip3 · Soundtoys Decapitator (hard mode) · Waves L-series ·
FabFilter Saturn 2
**Referenced, not owned:** Gold Clip, StandardCLIP, and the modern clipper cohort

**Vendor note, stated honestly:** I can't reliably place Gold Clip's developer, so I'm not
attributing it. The DSP below is the category, and it's what actually matters — modern clippers
differ from each other in a small number of measurable ways, all listed here.

Clipping deserves its own document because **it is the single worst case for aliasing in all of
audio DSP**, and because the modern loudness workflow depends on it in a way that isn't obvious.

---

## Why clipping is the hardest nonlinearity

Hard clipping is:

```
y = max(−T, min(T, x))
```

A discontinuity in the **derivative** at the threshold. The Fourier series of a clipped sine has
harmonics falling off only as **1/n** — which is to say, barely. A `tanh` saturator's harmonics
fall off exponentially; a hard clipper's don't.

Consequence: **there is enormous energy far above Nyquist**, all of which folds. Per
`ANTIALIASING.md`, a naive hard clipper measured **−16.1 dB** inharmonic energy in our own
validation, against **−142.9 dB** for a linear gain. That is the worst number in this repo, and it
was produced by three lines of code that look completely reasonable.

**If you build one thing carefully, build the clipper carefully.**

---

## The good news: hard clip has a closed-form antiderivative

ADAA works beautifully here, which is lucky, because this is where you need it most.

For `f(x) = clamp(x, −T, T)`, the first antiderivative is piecewise:

```
F₁(x) =  x²/2                    for |x| ≤ T
F₁(x) =  T·|x| − T²/2            for |x| >  T
```

Then the standard ADAA difference quotient:

```
y[n] = ( F₁(x[n]) − F₁(x[n−1]) ) / ( x[n] − x[n−1] )
```

with the fallback to pointwise `f(x[n])` when the denominator is near zero.

**Two implementation traps, both common:**

1. **The fallback threshold.** Too tight and you divide by near-zero and get spikes or NaNs; too
   loose and you're running pointwise most of the time and ADAA does nothing. Pick it relative to
   your numeric precision and **test the boundary explicitly** — feed `x[n] == x[n−1]` exactly,
   and feed a difference right at the threshold.
2. **Piecewise boundaries.** `F₁` is piecewise and its branches must join *exactly* at `|x| = T`,
   or you inject a small discontinuity at precisely the level where the clipper is most active.
   Assert continuity at the boundary in a unit test.

**Combine with 2× oversampling** and you get close to transparent at a fraction of the cost of
brute 16×. That's the recommended default.

---

## The clipper cohort: what actually differs between them

Modern clippers are differentiated by a short list of measurable properties. This is the whole
comparison, and every item is testable with the harness.

### 1. Knee shape

The single biggest sonic differentiator.

| shape | formula | character |
|---|---|---|
| **hard** | `clamp(x, ±T)` | brightest, most aggressive, most aliasing |
| **cubic soft** | `x − x³/3` (scaled), clamped | classic soft clip, gentle |
| **quintic / higher** | higher-order polynomial | even smoother knee, more controllable |
| **tanh** | `T·tanh(x/T)` | asymptotic — never truly clips, always soft |
| **arctan** | `(2T/π)·atan(x/T)` | softer still, more 3rd harmonic |
| **variable knee** | interpolate hard↔soft | what most products expose as one knob |

The reason "gold standard" clippers sound transparent while cheap ones sound harsh, given the same
oversampling, is almost entirely knee shape plus what happens either side of the knee.

### 2. Symmetry

Symmetric clipping → **odd harmonics only**. Asymmetric (different positive and negative
thresholds, or a DC bias before the clip) → **even harmonics**, which read as warmer.

Per `SATURATION.md`, this is the even/odd ratio control and it's the cheapest character knob that
exists. Add a DC blocker after, always.

### 3. Oversampling factor and filter quality

**The filters matter more than the factor.** 4× with steep polyphase FIR decimation beats 8× with a
sloppy IIR. Most products expose the factor and never mention the filter, which is why two
plugins at "8×" can measure very differently.

### 4. True-peak awareness

**This is the one most people get wrong.** A clipper that clamps at the *sample* level still
produces inter-sample peaks — the reconstructed analog waveform between samples can exceed the
threshold by 1 dB or more.

So a master clipped to −0.1 dBFS at sample level can hit **+0.9 dBTP**, clip the listener's DAC,
and distort after lossy encoding. Proper true-peak clipping means **clipping in the oversampled
domain**, per ITU-R BS.1770-4.

### 5. Gain compensation

Does the output level stay constant as you drive in? Auto-compensated clippers make A/B honest;
uncompensated ones make everything sound better because it's louder, which is the oldest trap in
audio.

**When measuring any clipper, level-match first or your comparison is worthless.**

---

## Why modern workflow clips *before* limiting

This is the part that isn't obvious and it's the reason the clipper cohort exists at all.

A limiter reduces gain over a **time window** — lookahead, attack, release. When a single 2 ms
transient pokes 4 dB above the ceiling, the limiter pulls down the *whole region around it* for
the duration of its release. That's audible as pumping, and as a loss of density in everything
near the transient.

A clipper removes that same peak **instantaneously**, affecting only the 2 ms where it happened,
at the cost of harmonic distortion during those 2 ms.

**Which is less audible?** Almost always the clipping — because per `IDEAS-2.md` §9, distortion
immediately at and after a loud transient sits inside the temporal masking shadow, while the
limiter's gain movement extends *outside* it, into the exposed material either side.

So the modern chain is:

```
mix → clipper (removes the peaks, ~1-3 dB) → limiter (catches the rest, gently) → ceiling
```

The clipper does the violent work in the masked moments; the limiter does the gentle work
everywhere else. **That division of labour is the whole technique**, and it's the direct ancestor
of the SHADOW idea.

---

## Building ours

### Spec

- variable knee, continuously hard → soft, with **closed-form antiderivatives for every knee
  setting** so ADAA works across the whole range. *Choose the polynomial family with this in mind
  from the start* — pick a curve because you can integrate it, not because it looks nice.
- asymmetry control with DC blocker after
- ADAA-1 plus adaptive oversampling (`IDEAS-2.md` §18 — clipping is the case that most justifies it)
- true-peak mode that clips in the oversampled domain
- auto gain compensation, defaulting **on**
- a **delta monitor** — hear only what's being removed. Per `RESONANCE-AND-AUTO-EQ.md`, this is
  how users build trust, and it's how you'll debug.

### Acceptance criteria

- `alias` test at −1 dBFS on the **hard** setting reports better than **−70 dB** inharmonic
  energy. Hard clip is the worst case; if it passes, everything softer passes.
- in true-peak mode, measured true peak never exceeds the ceiling on a torture set, verified at 4×
  oversampling per BS.1770-4
- knee continuity: sweep the knee control and the measured THD curve must be **monotonic and
  smooth**, with no discontinuity at the parameter boundaries where your piecewise polynomial
  branches change
- ADAA boundary: unit-tested at `x[n] == x[n−1]` exactly, and at the fallback threshold
- gain compensation holds output LUFS constant within 0.2 dB across the full drive range

### Measure first

```
KClip3    alias + harmonics, at every oversampling setting it offers, 4 drive levels
          — this gives you the incumbent's aliasing floor, which is your bar
KClip3    harmonics with the knee varied — the even/odd ratio across the knee range
          is the character map you're trying to match or beat
L2        curve + envelope — so you can see limiter gain movement next to clipper
          distortion and judge the tradeoff with numbers rather than opinion
```

That last comparison is the valuable one, and I don't think anyone has published it: **measure the
duration and depth of a limiter's gain excursion for a given transient, against the duration and
THD of a clipper removing the same transient.** One affects ~200 ms at low distortion; the other
affects ~2 ms at high distortion. Putting real numbers on that trade would settle an argument the
whole industry has by ear, and it's a two-hour measurement with the harness you already have.
