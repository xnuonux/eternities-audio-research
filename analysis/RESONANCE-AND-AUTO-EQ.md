# Resonance suppression and auto-EQ

**The most valuable category in modern mixing, and the least understood.**

**References:** oeksound soothe2 · oeksound Spiff · Soundtheory Gullfoss · sonible smart:EQ ·
iZotope Neutron Unmask · TDR Nova · FabFilter Pro-Q 4 dynamic bands

These are the plugins engineers describe as "I can't mix without it" and they cost $150–250 each.
Understanding why they work is worth more than another console emulation, because the mechanism
is genuinely different from an EQ and most people — including people who use them daily — don't
know what they're doing.

**[doc]** documented · **[std]** standard in the literature · **[inf]** my inference.

---

## 1. soothe2 — the key insight most people miss

### What everyone thinks it is

"A dynamic EQ with lots of bands." It isn't, and the difference is the entire product.

### What it actually does **[inf, high confidence]**

A dynamic EQ reduces a band **when that band is loud**. soothe reduces a band **when that band is
anomalous** — and those are completely different criteria.

The mechanism:

1. High-resolution spectral analysis, fine bands or per-bin.
2. Compute a **smoothed local spectral envelope** — the running average shape of the spectrum
   across neighbouring frequencies.
3. For each bin, compute its **deviation above that local envelope**. A resonance is a narrow peak
   standing proud of its neighbours. Broadband energy is not.
4. Apply narrow, fast reduction proportional to the deviation.

**That is why it doesn't dull the sound.** A dynamic EQ set to tame 3 kHz pulls down 3 kHz whether
the energy there is a nasty resonance or the singer's core tone. soothe pulls down 3 kHz *only
when 3 kHz is sticking out relative to 2.5 and 3.5 kHz* — so a broad, even, bright tone passes
untouched while a narrow ring gets flattened.

It's a **local-contrast** detector, not a level detector. The closest analogy is unsharp masking in
image processing, run in reverse: find what deviates from the local average, and pull it back
toward the average.

### Why that's hard to build well

- **Resolution vs latency.** Narrow resonances need fine frequency resolution, which needs long
  windows, which costs latency and smears transients. soothe's "quality" settings are almost
  certainly this tradeoff. **[inf]**
- **Envelope smoothing width is the critical parameter.** Too narrow and the envelope tracks the
  resonance itself, so nothing deviates and nothing is detected. Too wide and you start detecting
  legitimate spectral shape as anomaly. This single number determines whether the plugin works.
- **Reduction must be fast but not produce modulation sidebands.** Fast narrow gain changes are
  amplitude modulation with audible artefacts if not smoothed properly.
- **The "delta" monitor is not a nicety, it's essential.** Being able to hear only what's being
  removed is how a user verifies it's catching resonance rather than tone — and it's how you'll
  debug it.

### Spiff is the same idea in the time axis

Where soothe finds bins anomalous **across frequency**, Spiff finds them anomalous **across time**
— a bin whose level jumps relative to its own recent history is transient energy. Same
local-contrast logic, rotated 90°. **[inf]**

That framing is worth internalising: **local contrast in frequency = resonance; local contrast in
time = transient.** One detector, two axes, two products.

---

## 2. Gullfoss — an auditory model as a product

**The commercially proven version of the thesis in `IDEAS-2.md`.**

Soundtheory built their own computational model of human hearing and use it to decide what the
listener is *failing to perceive*, then fixes that. **[doc — their own published description]**

The controls give it away — they are not EQ parameters:

| control | what it means |
|---|---|
| **Recover** | how much to restore detail the model says is being masked |
| **Tame** | how much to reduce what the model says is dominating |
| **Bias** | the balance between recovering and taming |
| **Brighten** / **Boost** | tilts the model's target |

There are no frequencies and no gains. You are adjusting a perceptual objective and it solves for
the filter.

### Why this matters to us

Gullfoss is the existence proof that **a rigorous auditory model, wrapped in perceptual controls,
is a sellable product** — at $200, with a devoted user base, competing against free EQs.

That validates `IDEAS-2.md`'s structural finding directly: build the masking model once, properly,
and products fall out. Gullfoss is one company's answer to exactly that observation.

### Where the opening is

**[inf]** Gullfoss is a single-instance processor — it analyses one signal against a model of
hearing. It has no knowledge of *the rest of the mix*.

The masking that actually ruins a vocal is caused by **other tracks**, not by the vocal's own
spectrum. A model that sees the whole session — `IDEAS.md` §2 MARGIN and `IDEAS-2.md` §17 CROWD —
is doing something Gullfoss structurally cannot. **That's the gap, and it's a real one.**

---

## 3. sonible smart:EQ — learned target curves

**[inf]** Trained per instrument class: identify what the source is, compare its spectrum to a
learned "good" target for that class, and generate corrective filtering. The multi-instance
version does cross-track spectral allocation.

This is a **data product wearing an EQ's clothes**. The DSP is ordinary; the value is the
reference corpus and the classifier. Which means competing with it is a dataset problem, not a
DSP problem — worth knowing before anyone scopes it as a plugin.

---

## 4. Neutron / Nectar Unmask — inter-track masking, heuristically

**[inf]** Sidechain from the masking track, find bands where both have energy, duck the masker in
those bands.

The honest assessment: this is the right *idea* with an approximate implementation. From what the
controls expose, it appears to be band-energy overlap rather than a psychoacoustic masking
threshold — no spreading function, no critical-band scale, no SII weighting.

Which is precisely why `IDEAS.md` §2 is worth building. **The difference between "both tracks have
energy at 2 kHz" and "track B raises track A's masked threshold at 2 kHz by 7 dB" is the
difference between a heuristic and a measurement**, and the second one can show you a number.

---

## 5. The dynamic-EQ baseline: TDR Nova, Pro-Q 4

Worth naming as the floor. Both are excellent, both are conventional: parametric bands, each with
an envelope follower on its own filtered signal driving the band gain.

**TDR Nova is free** and very good, which sets the commercial reality: **a conventional dynamic EQ
is not a viable product.** The entry price for this category is a genuinely better *detector*,
which is exactly what soothe and Gullfoss sell.

---

## What to take from this category

1. **Local contrast beats absolute level as a detection criterion.** This is the single most
   transferable insight in the document. Anywhere you currently threshold on "is this loud," ask
   whether "is this anomalous relative to its neighbours" is the better question. It usually is,
   and it's usually why the expensive plugin sounds transparent and yours doesn't.
2. **The axis is a free parameter.** Contrast across frequency → resonance. Contrast across time →
   transient. Contrast across channels → masking. **Contrast across *instances* → arrangement
   collision**, which nobody has built.
3. **Perceptual controls sell better than technical ones.** Gullfoss ships four knobs with no
   frequencies on them and wins. Pro-Q ships everything and wins differently. Both beat "here are
   32 biquads."
4. **The delta/difference monitor is a feature, not a debug tool.** Every plugin in this category
   has one, and it's how users build trust in a process they can't see.

## Measure these

```
soothe2     response, at several thresholds, on (a) a resonant source and (b) a broadband source
            — the resonant one should show narrow notches, the broadband one should show almost
            nothing. That contrast IS the mechanism, measured.
Gullfoss    response on the same two sources, then again with Recover/Tame swept — you are
            mapping a perceptual objective onto an actual filter curve
Pro-Q 4     dynamic band: envelope + response, to get the baseline detector behaviour
```

The soothe2 test is the important one and it's cheap. Feed it a sine sweep with one narrow
resonance added, then feed it pink noise. If the notch appears in the first and not the second,
you have measured local-contrast detection directly, and you have your acceptance criterion for
building one.
