# Auto-Tune, deep

**You own Antares**, so this is measurable — and pitch correction is one of the few processes
whose entire product can be captured as a **trajectory curve**, which makes it unusually
tractable.

**[doc]** documented/published · **[std]** standard in the literature · **[inf]** my inference.

---

## The three stages, and which one is actually hard

```
detect pitch  →  decide target  →  resynthesise at the new pitch
```

Stage 1 is hard. Stage 2 is where the product lives. Stage 3 is well-solved.

---

## Stage 1 — pitch detection, and its specific failure modes

### The methods **[std]**

| method | how | weakness |
|---|---|---|
| **autocorrelation** | correlate signal with delayed self; peak = period | **octave errors** — correlates nearly as well at 2×period |
| **YIN** | autocorrelation with a cumulative mean normalised difference function | much better on octaves; still struggles on noisy onsets |
| **cepstrum** | FFT of log-magnitude spectrum; harmonic spacing appears as a peak | good on harmonic-rich sources, poor on breathy voice |
| **harmonic product spectrum** | multiply downsampled spectra; true f₀ reinforces | cheap, decent, coarse resolution |
| **CREPE / neural** | trained regression on raw audio | most accurate; inference cost and latency |

### What actually breaks, and why it matters

- **Octave errors are catastrophic**, not cosmetic. Detect 220 Hz as 110 Hz and the corrector
  moves the note an octave. **It is instantly, embarrassingly audible.** The mitigation is a
  continuity constraint: the pitch track must be smooth, so an isolated jump of exactly ±12
  semitones between adjacent frames is rejected as physically implausible. **A tracker without a
  continuity constraint is not shippable.**
- **Onsets** — the first few milliseconds have no established period. Real trackers delay their
  confidence, which trades latency for reliability.
- **Glottal fry and breathiness** — aperiodic by nature. There is no fundamental to find. The
  correct behaviour is to **report low confidence and stop correcting**, not to guess. Correcting
  a fry passage produces the characteristic robotic warble.
- **Vibrato** — is not an error. A tracker that's too smooth kills it; one that's too responsive
  chases it and corrects it away.

**The confidence signal is as important as the pitch estimate**, and cheap implementations don't
have one.

---

## Stage 2 — the decision layer, which is the actual product

This is where Auto-Tune's value is, and none of it is difficult DSP.

### Retune Speed — one time constant, one genre

The correction trajectory is a smoothing filter between detected pitch and target pitch.

- **0 ms** — instantaneous snap. All natural drift, scoop and portamento is destroyed, and the
  pitch becomes a staircase. **This is the "T-Pain effect"**, and an entire aesthetic came out of
  one parameter at its minimum.
- **10–40 ms** — natural correction; fixes sustained errors, preserves onset scoops
- **>100 ms** — gentle; only corrects slow drift

**[doc]** This single control is the most commercially consequential parameter in audio software.

### Flex-Tune — the feature that made it usable

Correct only when the singer is **near** a target pitch; leave larger deviations alone.

It's a **deadband** around each scale note: inside the band, pull toward the note; outside it, do
nothing. The insight is that a deliberate bend or a slide *between* notes reads as far from any
target, while an out-of-tune sustained note reads as near-but-not-on. So "distance from target"
separates expression from error remarkably well.

Simple, and it's why natural-sounding correction became possible. **[doc]**

### Humanize — different speeds for different note phases

Sustained notes get slower correction than onsets, because natural drift lives in sustains and
genuine errors are established at onsets. Requires note-event segmentation — you need to know
where a note started. **[doc]**

### Scale and key

The target set. Chromatic corrects to the nearest semitone; a key-constrained scale removes the
non-scale notes as targets, which is both more musical and more dangerous (a deliberate blue note
gets dragged to the scale).

---

## Stage 3 — resynthesis **[std]**

| method | how | when |
|---|---|---|
| **PSOLA** | overlap-add pitch-synchronous grains, respacing them to change pitch | monophonic voice; preserves formants naturally because grain *content* is unchanged |
| **phase vocoder** | STFT, scale frequencies, fix phase coherence | general purpose; smears transients, needs phase-locking to avoid "phasiness" |
| **formant-corrected** | separate spectral envelope from excitation, shift excitation only | required for large shifts, or you get chipmunk |

**PSOLA is the right default for voice.** It preserves formants for free — you're respacing
grains, not scaling the spectrum — and it handles transients well because it's time-domain.

**The formant point matters.** Pitch and formants are independent in a real voice: the vocal folds
set pitch, the vocal tract sets formants. A naive shift moves both, which is why a resampled voice
sounds like a different-sized person. Anything shifting more than a couple of semitones must
separate them.

---

## The measurement that captures the whole product

**This is the valuable part of this document.** Auto-Tune's behaviour is almost entirely
characterised by one family of curves, and you own the plugin.

### The glide test

1. Synthesise a **slow linear pitch glide** — say C3 → C4 over 4 seconds, on a source with stable
   harmonics (a sawtooth is ideal; it's periodic, harmonic-rich, easy to track).
2. Render through Auto-Tune at a given Retune Speed / Flex-Tune setting.
3. **Track the output pitch** over time (autocorrelation on the output is fine here — you control
   the input, so you know the ground truth).
4. Plot output pitch against input pitch over time.

**That plot is the product.** You will see directly:

- the **staircase** at Retune 0 — flat plateaus at each semitone with near-vertical transitions
- the **rounded staircase** as Retune increases — plateaus with exponential approach curves whose
  time constant *is* the Retune Speed
- the **Flex-Tune deadband** — regions where the output simply follows the input untouched,
  appearing as diagonal segments between the plateaus
- the **transition shape** — the exact curve between notes, which is what makes the effect sound
  like Auto-Tune specifically rather than generic quantisation

### The step test

Feed a pitch that **steps** discontinuously (C3 held, then C#3 held). Measure the output's
approach trajectory. That's the correction impulse response, and it gives you the time constant
and any overshoot directly.

### The vibrato test

Feed a sine-modulated pitch at 5–6 Hz with varying depth. Measure how much vibrato survives at
each Retune Speed. **The depth-vs-speed surface tells you exactly where the tracker stops treating
vibrato as expression and starts treating it as error** — which is the hardest judgment call in
the product, captured as a number.

---

## What I'd build, and in what order

1. **A pitch tracker with a confidence output and a continuity constraint.** Nothing else can be
   built until this is reliable. Validate it against synthesised ground truth: glides, steps,
   vibrato, noise-contaminated tones, and deliberately fry-like signals. **Measure the octave-error
   rate explicitly** — that's the number that decides whether the product is viable.
2. **PSOLA resynthesis**, verified transparent: shift by 0 semitones and the output should null
   against the input to a measurable floor. **If a zero-shift isn't transparent, nothing built on
   it will be.**
3. **Formant separation** (LPC or cepstral envelope) so shifts beyond a couple of semitones stay
   natural. This is also a product by itself — see `VOCALS.md`.
4. **The decision layer** — retune speed, deadband, note segmentation for humanize, scale
   constraint. Cheap to implement, and it's where the character is.
5. **Only then** consider the real-time/low-latency version. Latency comes almost entirely from
   the tracker's confidence delay, and optimising that before the tracker is correct is the wrong
   order.

### Acceptance criteria

- **octave-error rate under a stated threshold** on a validation set that includes breathy,
  fry-like and noise-contaminated material — and the threshold should be published internally,
  because this is the failure users hear
- zero-shift PSOLA nulls against the input below a measured floor
- the glide test reproduces a staircase whose plateau width is exactly one semitone and whose
  transition time constant matches the requested Retune Speed
- low-confidence passages **pass through uncorrected** rather than being guessed at

That last one is a design position worth holding. **A corrector that refuses to correct when it
isn't sure is better than one that always acts**, because the failure mode of guessing is loud,
weird, and immediately blamed on the plugin.
