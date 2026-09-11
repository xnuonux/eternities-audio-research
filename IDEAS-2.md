# Plugin ideas, batch 2

Continues from [`IDEAS.md`](IDEAS.md) §1–8. Same contract: mechanism, honest competition note,
cost, and a **measured** acceptance criterion.

This batch pushes harder into the psychoacoustic exploits, because that's where the sweep says
the durable value is, and into two pieces of infrastructure that make everything else cheaper.

---

## 9. SHADOW — a limiter that hides in temporal masking

**My favourite idea in either document. Nobody does this.**

### The exploit

Hearing has **temporal masking** in both directions **[std]**:

- **forward (post-) masking** — for roughly **100–200 ms** after a loud event, quieter sounds are
  raised toward inaudibility. Strong and long.
- **backward (pre-) masking** — for roughly **5–20 ms** *before* a loud event, sounds are also
  masked. Shorter, weaker, but real.

So immediately after a transient there is a **window in which distortion is substantially less
audible than it would be in silence.** Every limiter on the market ignores this. They apply the
same gain-reduction envelope shape regardless of whether the ear can currently hear what they're
doing.

### The mechanism

Track a **temporal masking threshold** — a decaying envelope following each detected transient,
with the decay fitted to published post-masking curves. Then make the limiter's aggression
*follow* it:

- **inside the masking shadow:** release fast and hard, let the reduction envelope be as sharp as
  it likes, allow more distortion. It is masked.
- **outside it** (sustained passages, exposed tails, silence): release slowly and smoothly,
  minimise distortion, protect transparency.

You get the loudness of an aggressive limiter with the transparency of a gentle one, because the
aggression is scheduled into the moments the ear is least able to detect it.

### Competition

None that I know of. Limiters have "styles" and program-dependent release, but those are
*signal*-dependent, not **perception**-dependent. Nobody schedules distortion against a masking
model.

### Cost and acceptance

**Three weeks**, most of it in the masking envelope and listening validation.

**Accept when:**
- the temporal masking envelope matches published post-masking data — threshold elevation vs
  time-after-masker within a few dB of the textbook curves
- at matched LUFS against a reference limiter, measured THD **inside** the shadow is allowed to be
  higher while THD **outside** it is measurably lower
- **the real test is a null test:** at matched loudness, A/B against Pro-L 2 on sparse material
  (solo piano, a vocal with gaps). Ours should be more transparent precisely where the reference
  has nothing to hide behind.

---

## 10. GLUE — the mystery word, made measurable

### The hypothesis

"Glue" is the least falsifiable term in audio. Here is a testable definition:

**Glue is inter-channel envelope correlation.** Elements sound like one performance in one space
when their amplitude envelopes move *together* — which is exactly what a bus compressor does
incidentally, by applying one common gain signal derived from the sum to everything at once.

If that's right, then glue is directly measurable (correlation between per-track envelopes) and
directly producible (impose common gain movement) — and you don't need a compressor to do it.

### The mechanism

A multi-instance plugin with a shared bus:

1. Each instance reports its envelope to a shared context.
2. Compute a **common envelope** from the sum.
3. Apply a scaled fraction of the common envelope's *movement* to each track — with **no
   threshold and no ratio.** Not compression. Common modulation.
4. A "coherence" control sets how much of each track's own envelope is replaced by the common one.

Crucially, this can move gain **up** as well as down, which a compressor cannot, so it glues
without reducing dynamic range.

### Why it's interesting even if the hypothesis is wrong

The meter is worth shipping regardless: a readout of envelope correlation across a session tells
you something real about a mix that nothing currently displays. And if the hypothesis *is* right,
it's the first non-mystical glue processor.

### Cost and acceptance

**Two weeks** for a single-instance version driven by a sidechain; **four** for the multi-instance
shared-context version.

**Accept when:** measured inter-track envelope correlation rises with the coherence control while
**measured dynamic range (LRA, crest factor) stays constant.** That combination is the proof it's
doing something a compressor can't.

---

## 11. FREE AIR — noise you cannot hear, character you can

### The exploit

People add tape noise, console noise and vinyl crackle for "analog character," then fight the
noise floor it costs them.

But you already have the masking model from `IDEAS.md` §2. So: **compute the mix's own masking
threshold, and inject shaped noise that sits just underneath it, per critical band, continuously.**

The noise is *provably* below the threshold of audibility given the current program material. It
is inaudible as noise. But it fills the spectral gaps between partials, it dithers the low-level
detail, and it decorrelates quantisation — which is a meaningful part of what "analog" is.

And when the music stops, the noise stops, because the masking threshold collapses. **No noise
floor.** That is the thing tape emulation cannot offer.

### Mechanism

1. Per-ERB-band masking threshold of the program (the §2 model).
2. Generate noise per band, level set to `threshold − margin` (a few dB of safety).
3. Optional character: the noise's *spectral tilt* and its correlation between L/R are the knobs.
   Correlated noise reads as a console; decorrelated reads as air and width.

### Competition

Dither does this at the LSB. Nobody does it at program level using a real masking model. This is
a genuinely new product shape.

### Cost and acceptance

**Two weeks** once §2's masking model exists. **Sequence it after §2 or §5.**

**Accept when:**
- in silence, output is bit-identical to input (noise gates itself completely)
- an ABX listening test at the stated margin is at chance — if people can hear it, the margin is
  wrong and you've built a noise generator
- measured per-band noise level tracks the computed threshold as program material changes

---

## 12. DEPTH — the precedence effect, unexploited

### The exploit

The **precedence effect**: when two versions of a sound arrive within roughly **1–35 ms**, the
auditory system localises to the *first* arrival and fuses the second into it. You do not hear an
echo — you hear **one** source, and it sounds bigger, closer, and more present. **[std]**

The fusion window is content-dependent: a few milliseconds for clicks, up to ~40 ms for speech
and sustained material. Cross that boundary and it splits into an audible echo.

### Why this is a gap

Haas-delay widening is well known and crude — one fixed delay, one side, and it comb-filters on
mono fold-down.

Nobody ships a tool that **tracks the fusion boundary against the material** and places delays
adaptively to sit just inside it. The delay that maximises presence on a vocal is not the one that
works on a hi-hat, and it changes within a performance.

### Mechanism

- onset/transient detection to classify material as impulsive vs sustained
- set the delay adaptively within the fusion window for that classification
- **multiple short taps** rather than one, at incommensurate intervals, to avoid a single comb
  notch — spreading the comb rather than deepening it
- per-band handling, since the fusion window and the comb consequences both vary with frequency
- mono-compatibility metering, because this is exactly the effect that collapses

### Cost and acceptance

**Two to three weeks.**

**Accept when:**
- mono fold-down level dip is under 1 dB (the test every Haas widener fails)
- on impulsive material the delay stays short enough that no discrete echo is audible — verified
  by listening, and by checking the autocorrelation of the output for a discrete peak
- perceived size increases in an A/B while measured stereo correlation stays above a floor

---

## 13. PRESENCE — more loudness at the same LUFS

### The exploit

Perceived loudness is **spectrally weighted**. The ear is most sensitive around 2–5 kHz, and the
equal-loudness contours (ISO 226) quantify by how much, at every level. **[std]**

So at a **fixed** LUFS or true-peak, redistributing energy toward the sensitive region makes the
material perceptibly louder. Every engineer knows this as "presence EQ." Nobody has built it as a
**solved optimisation**.

### Mechanism

Treat it as constrained optimisation:

> maximise predicted perceived loudness (ISO 226-weighted, level-aware)
> subject to: LUFS unchanged, true-peak unchanged, and per-band deviation ≤ a user-set tonal budget

Solve per-band gains against that. The tonal-budget constraint is what keeps it from just
becoming a fixed presence boost — it must not wreck the tonal balance, and the user sets how much
licence it has.

Display **predicted loudness gain in phons at constant LUFS.** That number is the product.

### Why it's honest rather than a loudness-war trick

It gains loudness *without* gaining level, so it doesn't cost dynamic range or headroom. The
competitor trick is to crush; this is to redistribute. And because it's constrained and displayed,
the user can see exactly what they traded.

### Cost and acceptance

**Three weeks.** The optimiser is straightforward; the loudness model must be right.

**Accept when:** measured LUFS is unchanged within 0.1 dB, true-peak unchanged, and a listening
panel reliably picks the processed version as louder. If they can't, the loudness model is wrong.

---

## 14. PERIOD — saturation that lands on the harmonic series

### The problem

A waveshaper distorts per *sample*, with no knowledge of the waveform's period. Its harmonics land
on the harmonic series only to the extent the input is a perfect periodic tone. On real material —
slightly inharmonic, vibratoed, polyphonic — the generated components are *not* exactly harmonic,
and that mismatch is part of what makes digital distortion sound gritty rather than rich.

### The mechanism

**Pitch-synchronous waveshaping.** Track the fundamental period, then apply the nonlinearity in a
period-locked frame — each detected period gets shaped as a unit, so the generated harmonics fall
exactly on integer multiples of the *tracked* pitch rather than wherever sample-wise shaping puts
them.

Related to PSOLA, borrowed from the vocal world and pointed at distortion instead.

Consequences worth noting: it's monophonic-only (a pitch tracker needs one pitch), and it needs
graceful failure — on unpitched or polyphonic material it must fall back to ordinary shaping
rather than produce garbage. **That fallback is the engineering risk.**

### Competition

None I know of. This is the most speculative idea in either document, and also the most likely to
sound genuinely unlike anything else — which is worth a two-week spike to find out.

### Cost and acceptance

**Two weeks for a spike.** Prove or kill it before scoping further.

**Accept when:** on a slightly-detuned or vibratoed source, measured harmonic components sit
closer to exact integer multiples than the same nonlinearity applied sample-wise. If that doesn't
hold, the idea is wrong and you stop there.

---

## 15. GEOMETRY — early reflections from an actual room

### The mechanism

Instead of a hand-tuned tap bank, compute early reflections from a **real geometric model** using
the **image-source method** (Allen & Berkley, 1979) **[std]**: mirror the source across each wall,
compute arrival times from path length, attenuate by distance and per-surface absorption
coefficients, and iterate to the desired reflection order.

Give the user a box with dimensions, movable source and listener, and per-surface materials with
real published absorption coefficients (concrete, glass, carpet, drape, wood).

Feed the FDN tail from `REVERB.md` for the late field.

### Why this beats a tap bank

- the ER pattern is **physically consistent** — move the source and everything updates coherently
- room modes fall out for free, because they're a consequence of the geometry
- it composes directly with `IDEAS.md` §3 PARALLAX: source position *is* distance
- you can model a space you can describe but have no IR for

### Competition

Exists in acoustics simulation software and game audio middleware. **Rare as a music production
reverb with a usable interface** — and that gap is UI, not DSP.

### Cost and acceptance

**Three weeks** for shoebox geometry; more for arbitrary shapes (and arbitrary shapes are not
worth it — a shoebox with adjustable dimensions covers nearly every useful room).

**Accept when:** for a given box, the computed RT60 matches the **Sabine/Eyring** prediction from
its volume and total absorption within 10%. That is a hard, published check, and it catches a
wrong absorption model immediately.

---

## 16. LIVE IR — convolution that isn't frozen

### The problem

Convolution reverb is maximally realistic and completely static. It's the same room, the same
positions, forever. An FDN is alive but never quite as convincing. **[std]**

### The mechanism

Modulate the impulse response itself:

- decompose the IR into short segments
- apply slow, decorrelated time-varying delay and gain per segment
- crossfade between two or more IR variants (captured or synthesised) on slow LFOs
- add slight per-segment pitch drift in the late portion only

The **late** field is where modulation is safe and helpful — the early reflections carry the
localisation cues and must stay stable, exactly as in `IDEAS.md` §8. So: static early, living
late.

### Cost and acceptance

**Three weeks**, on top of a working partitioned-convolution engine.

**Accept when:** a sustained tone through the modulated version shows no measurable pitch
modulation in the first 20 ms (localisation intact) while the tail's modal peaks are measurably
broadened compared to the static version.

---

## 17. CROWD — an arrangement meter, not a mix meter

**Sell a measurement. Diagnose a problem nobody currently displays.**

### What it shows

Not spectrum. **Occupancy.** Across the session, per critical band, over time: **how many
simultaneous elements are competing in each band.**

- a timeline heatmap: bands on Y, time on X, "number of tracks with significant energy here" as
  colour
- hotspots ranked, each naming the tracks involved
- an "arrangement density" curve over the whole song

### Why it's useful and new

Mix problems are usually arrangement problems. Two instruments fighting at 400 Hz is not fixed by
EQ, it's fixed by moving one of them — an octave, an inversion, a different voicing, or out of the
section entirely. **Nothing currently shows you that as a diagnosis**, so people reach for EQ and
subtractive fixes.

This pairs directly with §2 MARGIN's masking model — occupancy is the arrangement-level view of
the same computation.

### Cost and acceptance

**Three weeks**, mostly the multi-instance session plumbing and the visualisation.

**Accept when:** on a deliberately-built test mix with two tracks placed in the same band, the
hotspot list names exactly those two tracks and that band, with no false positives.

---

## 18. ADAPTIVE OVERSAMPLING — infrastructure that pays for everything else

Not a product. A library component that makes every other product cheaper.

### The mechanism

Oversampling is a fixed cost paid constantly, for a problem that is **intermittent**. Aliasing
only happens when there is significant HF content *and* enough drive to generate harmonics past
Nyquist. On a bass line at moderate drive, 16× oversampling is computing nothing of value.

So: measure it. Per block, estimate the HF energy and the current drive, predict the harmonic
order that will exceed Nyquist, and **set the oversampling factor to what's actually needed** —
1× to 16×, changing between blocks with a crossfade to avoid a discontinuity.

### Why it matters

Per `ANTIALIASING.md`, oversampling is the dominant CPU cost in every nonlinear plugin we ship.
Cutting the average factor by 4× across a session is the difference between 8 instances and 32.
**That's a competitive feature by itself**, and CPU efficiency is something users notice and
reviewers measure.

### Cost and acceptance

**Two weeks.**

**Accept when:** measured aliasing is **within 3 dB of fixed 16× oversampling** across a torture
set (sweeps, drums, full mixes, at every drive level), at a measured average CPU cost under half.
Both halves of that are required — cheaper but noisier is a failure.

---

## Revised sequencing across both documents

**This week:** §6 DOUBLE (two days).

**This month:** §7 SHUFFLE → §18 ADAPTIVE OVERSAMPLING (infrastructure, pays back immediately) →
§1 SPLIT (the platform).

**Then, the differentiated products:** §5 LEGIBLE (builds the masking model) → §2 MARGIN and
§11 FREE AIR (both reuse it) → §9 SHADOW → §4 FOUNDATION.

**Spikes worth two weeks each to prove or kill:** §14 PERIOD, §10 GLUE.

**Bigger builds, when there's appetite:** §3 PARALLAX + §15 GEOMETRY (they compose — one is
distance, the other is the room), §12 DEPTH, §13 PRESENCE, §16 LIVE IR, §17 CROWD.

### The dependency worth noticing

**The masking model is load-bearing across five ideas** — §2 MARGIN, §5 LEGIBLE, §11 FREE AIR,
§9 SHADOW (temporal rather than spectral, but the same framework), and §17 CROWD. Build it once,
properly, validated against published masking data, and five products fall out of it.

That is the highest-leverage single piece of engineering on either list. If you only do one
serious thing, do that.
