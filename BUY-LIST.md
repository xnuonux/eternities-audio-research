# What to buy

Unlimited funds is a constraint too — it makes it easy to buy forty plugins and measure none of
them. So this is **ranked by the research question each one answers**, and every entry says what
it's for and whether you'll use it after the measurement.

Prices are approximate and from memory; check them. Marked **[!]** where I'm confident and
**[~]** where I'd verify before ordering.

---

## Tier 1 — buy these this week. Each settles an open question in this repo.

### 1. oeksound **soothe2** — ~$200 **[!]**

**Question it answers:** is my local-contrast reading of it correct
(`RESONANCE-AND-AUTO-EQ.md` §1)?

**The test is already written:** feed it a sine sweep with one narrow resonance added, then feed it
pink noise. If it notches the first and does nearly nothing to the second, local-contrast detection
is confirmed and you have your acceptance criterion for building one.

**This is the single highest-value purchase on the list.** It's the most-used modern mixing
plugin, the mechanism is the most transferable insight in the repo, and you'll use it forever
regardless of what we build.

### 2. Soundtheory **Gullfoss** — ~$200 **[!]**

**Question:** what does a perceptual objective actually look like when it's resolved into a filter
curve?

Measure `response` while sweeping Recover and Tame. You are mapping an auditory model's output
onto an EQ curve — which is precisely what `IDEAS.md` §2 MARGIN and §5 LEGIBLE need to produce.
It is the commercial existence proof for the whole masking-model thesis, and seeing its curves is
the cheapest way to sanity-check ours.

### 3. Eventide **SplitEQ** — ~$100, often on sale **[!]**

**Question:** how good is the incumbent's transient/tonal separation, and is `IDEAS.md` §1 still
worth building?

**I told you to demo this before committing weeks, and I meant it.** This is the plugin that made
me correct my own "nobody ships this" claim. Buy it, measure its separation quality on drums and
on sustained material, and decide whether our platform framing beats it. If SplitEQ's split is
excellent, the honest answer might be that we build something else.

Eventide **Physion Mk II** (~$100) is the same technology as a standalone splitter and is arguably
the more direct comparison. **[~]** If you only get one, get Physion — it's closer to the raw
two-stream tool we'd be building.

### 4. Newfangled Audio **Elevate** bundle — ~$200 **[!]**

**Question:** does perception-scheduled limiting actually work? This is `IDEAS-2.md` §9 SHADOW's
closest living relative.

Elevate is a 26-band limiter driven by an auditory model that decides per-band how much reduction
is perceptually acceptable. That is adjacent to SHADOW's core claim. Measure it against Pro-L 2 at
matched LUFS on sparse material and you'll learn whether the perceptual-scheduling idea delivers
in practice before we spend three weeks on it.

The bundle includes **Saturate** and **Punctuate**, which are the same engine split out —
another shared-core family like Kazrog.

### 5. MeldaProduction **MTurboComp** — ~$200 **[~]**

**Question:** is the four-decision compressor taxonomy in `DYNAMICS.md` right?

MTurboComp ships dozens of compressor models **with the topology parameters exposed** — detector
position, detector type, knee, ballistics, saturation stages. It is essentially our taxonomy sold
as a product. Measure ten of its models with `curve,envelope` and you either confirm the taxonomy
or find what it's missing.

Also worth it: **MSpectralDynamics**, per-bin dynamics, which is the generalised version of
soothe-class processing.

---

## Tier 2 — reference targets. Buy, measure, keep.

### 6. Acustica Audio — one Acqua title, ~$100–200 **[~]**

**Question:** what does Volterra-kernel modelling actually sound like, and is the CPU cost as bad
as reported?

Pick any well-regarded single title. You're measuring the *approach*, not the box. Run the
harmonics protocol at many levels — a Volterra model should show harmonic behaviour that varies
with level in a way a fitted waveshaper struggles to reproduce, and that difference is what you're
looking for.

### 7. Tokyo Dawn **Kotelnikov GE** — ~$60 **[!]**

**Question:** what's the floor?

Per `THE-EXPENSIVE-ONES.md` §6, its dual peak/RMS detector with independent releases is the bar
our compressor has to clear. Cheap, excellent, and measuring it tells you what "good and free"
looks like. TDR **Nova GE** (~$60) likewise for dynamic EQ.

### 8. Three-Body Tech **Kirchhoff-EQ** — ~$250 **[~]**

**Question:** what's in a filter prototype library, concretely?

Per `THE-EXPENSIVE-ONES.md` §3, the prototype library is permanent infrastructure for us. Kirchhoff
ships a large one with the prototypes selectable per band — so you can measure the *same* band at
the *same* settings through a dozen different topologies and extract each one's curve family.
That's a shortcut to specifying our own library properly.

**DMG EQuilibrium** (~$300) **[~]** is the alternative with even deeper parameterisation. One or
the other, not both.

### 9. Goodhertz **Lossy** — ~$100 **[~]**

**Question:** how do codec artefacts actually behave, and is the codec-preview idea real?

Lossy emulates lossy-codec degradation as a creative effect. It's the closest thing to
`IDEAS.md` §5's translation panel, and measuring it tells you what codec damage looks like
spectrally without building an encoder chain first.

### 10. Zynaptiq **UNVEIL** — ~$200 **[~]**

**Question:** how far can blind de-reverberation get?

Zynaptiq is the most algorithmically adventurous company in audio, and UNVEIL does
mixing-informed reverb reduction on material with no dry reference. If you want to know what's
possible at the frontier of separation, this is the one to own. **UNCHIRP** and **UNFILTER** are
similarly novel. **[~]**

---

## Tier 3 — free or cheap, punches far above its price

- **Valhalla Supermassive** — **free**. Enormous FDN with heavy modulation. Measure its `rt60` and
  you're studying a very well-made feedback delay network at no cost. **[!]**
- **TDR Nova**, **TDR SlickEQ** — **free** versions. The dynamic-EQ and EQ baselines. **[!]**
- **Klanghelm MJUC** — ~$25. Excellent vari-mu emulation for the price. A cheap way to get a
  **ratio-increases-with-level** measurement target. **[~]**
- **Klanghelm DC8C** — ~$30. Deeply parameterised compressor, another taxonomy check. **[~]**
- **Voxengo SPAN** — free analyser. **GlissEQ** (~$100) has genuinely unusual
  spectrum-dependent filter behaviour worth measuring. **[~]**
- **Airwindows** — **free and open source**, ~400 plugins with written rationales. Not a purchase,
  but it belongs on this list because it's the best free DSP reading in existence. **[!]**

---

## Tier 4 — the expensive specialists. Only if we commit to that lane.

### Celemony **Melodyne Studio** — ~$700 **[!]**

Only buy if polyphonic separation is genuinely on the roadmap. Per `VOCALS.md` §1, DNA is a
months-long problem needing a sinusoidal-modelling framework. **Owning it won't teach you how it
works** — it will show you what the bar is, and the bar is very high.

If you want the vocal lane without the hardest problem, **Melodyne Essential/Assistant** (~$100–
$250) gives you monophonic editing to measure against for far less. **[~]**

### Synchro Arts **Revoice Pro** — ~$600 **[!]**

Per `VOCALS.md` §3, this is the **most attackable expensive incumbent in the collection** — DTW is
textbook and the premium is workflow. Buy it to measure how good the alignment and the pitch/level
contour transfer actually are, because that's the spec we'd be building to.

**VocAlign Ultra** (~$250) is the cheaper way to get the core alignment behaviour. **[~]**

### iZotope **RX Advanced** — ~$1200 **[~]**

The restoration reference: spectral repair, dialogue isolate, de-reverb, de-plosive. Expensive,
and genuinely the state of the art for repair. **Only worth it if restoration is a product lane**
rather than a curiosity. If it's a curiosity, Zynaptiq UNVEIL at $200 teaches more per dollar.

---

## What NOT to buy, and why

- **More console, 1176, LA-2A, Pultec or tape emulations.** You own several of each. They're
  commodity, the taxonomy in `DYNAMICS.md` and `SATURATION.md` covers them, and buying a tenth one
  teaches nothing the ninth didn't.
- **Another conventional EQ or compressor.** Pro-Q 4 and Pro-C 3 are best-in-class and you have
  them. Kotelnikov covers the free floor.
- **Bundles.** You'll get forty plugins and measure two. Buy individually, against a named
  question, and measure it before buying the next one.
- **Anything I marked [inf] in the analysis without a question attached.** Curiosity is not a
  research budget.

---

## The order I'd actually do it in

**Week 1:** soothe2, Gullfoss, Physion (or SplitEQ). ~$500. These three settle the three biggest
open questions in the repo, and all three are things you'd want anyway.

**Week 2:** measure them. Don't buy anything else until the Tier 1 measurements are in the repo —
because the results will change what's worth buying next.

**Then:** Elevate and MTurboComp if the SHADOW and taxonomy questions still look live after the
first round. Kotelnikov and Supermassive whenever, they're cheap or free.

**Tier 4 only after a lane is chosen.** Melodyne and Revoice are answers to "are we building a
vocal product," and that question isn't settled yet.

Total for a genuinely complete research position: **under $2,000**, most of it in things you'd use
in real sessions anyway. The unlimited budget isn't the constraint — measurement time is. Every
plugin bought and not measured is worse than not buying it, because it's a false sense of
coverage.
