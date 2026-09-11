# The vocal chain

**References:** Celemony Melodyne · Antares Auto-Tune Pro (+ Throat) · Synchro Arts Revoice Pro /
VocAlign · oeksound soothe2 · Waves Clarity Vx · Soundtoys Little AlterBoy · iZotope Nectar ·
Waves Tune Real-Time · Waves Harmony · DeBreath · Sibilance

Vocals are where the money is, where the hardest DSP lives, and where the most expensive plugins
sit. Melodyne Studio is ~$700. Revoice Pro is ~$600. There are reasons.

**[doc]** documented · **[std]** standard in the literature · **[inf]** my inference.

---

## The chain, in processing order, and what's hard about each stage

```
capture → align → pitch → resonance → dynamics → tone → space → level
```

Every stage has a market leader, and the two genuinely hard problems are **align** and **pitch**.

---

## 1. Melodyne DNA — the hardest problem on this list, solved

### What DNA does

**Direct Note Access**: edit individual notes inside a *polyphonic* recording. A guitar chord
becomes six editable notes. That is Celemony's crown jewel and the reason Studio costs what it
does. **[doc]**

### Why it is genuinely hard

Two simultaneous notes share the frequency axis. A perfect fifth means note B's fundamental sits
on note A's 3rd harmonic — **the same FFT bin contains energy from both notes and there is no way
to separate them from magnitude alone.**

So you cannot solve this with a filter. You need to:

1. **Detect all fundamentals** present, including ones whose fundamental is weak or absent
2. **Assign each partial to a parent note** — the grouping problem
3. **Resolve shared partials** — when two notes both own a bin, split the energy between them
4. **Resynthesise** each note independently while preserving the others

### How it's approachable **[std]**

- **Harmonic grouping**: partials belonging to one note share a common *fundamental spacing* and
  tend to share a common *amplitude envelope* and *vibrato trajectory*. Two notes played by
  different fingers have subtly different onset times and modulation — that's the separating
  evidence.
- **Common-fate grouping** is the psychoacoustic principle underneath (Bregman, *Auditory Scene
  Analysis*): partials that start together, modulate together and decay together are perceived as
  one source. The algorithm is implementing the same heuristic the ear uses.
- **Shared-bin resolution**: estimate each note's expected amplitude for a shared partial from
  its *other*, unshared partials, then divide the shared energy in that ratio.
- **Phase matters.** Two partials at the same frequency sum as complex vectors; magnitude alone
  loses the information. Phase-aware analysis (or a sinusoidal model tracking frequency, amplitude
  *and* phase per partial) is what makes separation possible at all.

**This is a genuinely hard, genuinely valuable problem**, and unlike most items in this repo I
would not scope it as a few weeks. Months, and it needs a sinusoidal-modelling framework first.

---

## 2. Auto-Tune — pitch correction, and the parts people don't know about

### The detector

Pitch detection is the whole game and the failure modes are specific **[std]**:

- **autocorrelation / YIN** — robust, cheap, but prone to **octave errors** (locking to 2f or f/2)
- **cepstral** — good on harmonic-rich sources
- **CREPE and neural trackers** — currently the most accurate, at inference cost
- The hard cases are consistent: onsets, breathy or glottal-fry passages, and the transition
  between two notes.

**An octave error is instantly audible** in correction, which is why production trackers combine
methods and apply continuity constraints — the pitch track must be smooth, so an isolated
octave jump is rejected as implausible.

### The three features that are the actual product **[doc]**

- **Retune Speed** — the famous one. At 0 ms you get the hard-snap "T-Pain" sound because the
  pitch is quantised instantaneously, killing all natural drift. Slower values preserve vibrato
  and portamento. The *entire aesthetic* of a genre came out of one time constant.
- **Flex-Tune** — correct only when the singer is *near* a scale note; leave expressive bends
  alone. This is the feature that made Auto-Tune usable for natural correction, and it's a
  deadband around each target pitch, not a different algorithm.
- **Humanize** — apply slower correction to sustained notes than to onsets, because sustained
  notes are where natural drift lives and onsets are where pitch errors live.

### Throat — physical modelling of the vocal tract

**[doc]** Antares Throat models the vocal tract as a **series of connected tube sections** with
adjustable lengths and diameters, plus glottal-source parameters. Change the resonator geometry
and you change the singer's apparent physiology — a different throat, not a different EQ.

This is real physical modelling (Kelly-Lochbaum digital waveguide vocal tract), and it is the
right way to alter a voice's identity, because formants are *resonances of a geometry* rather
than bands on a curve. **[std]**

**The practical version worth building:** formant shifting via spectral-envelope manipulation.
Separate envelope (cepstral liftering or LPC) from excitation, scale the envelope's frequency
axis, resynthesise. That gets most of the perceptual effect for a fraction of the work, and it's
what Little AlterBoy's formant control does. **[inf]**

---

## 3. Alignment — VocAlign / Revoice Pro

### The mechanism

**Dynamic time warping.** Compute a similarity matrix between two signals' feature sequences
(spectral features, not raw samples), find the lowest-cost monotonic path through it, and you have
a time-mapping from the double onto the lead. Then variable-rate time-stretch the double to follow
that map. **[std]**

DTW is a solved textbook algorithm. The value is in three places that are *not* the algorithm:

1. **Feature choice** — MFCCs or spectral flux align better than waveforms, because you want
   phonetic similarity not waveform similarity
2. **Path constraints** — limit how much the warp can accelerate or decelerate, or consonants get
   smeared into mush
3. **Stretch quality** — the actual time-stretching must be transparent, which means PSOLA or a
   good phase vocoder, and this is where cheap implementations fail audibly

**Revoice Pro also transfers pitch and level contours**, not just timing — which is why it sounds
like one singer doing two takes rather than two takes locked together. **[doc]**

**[inf] This is the most under-served expensive tool.** DTW is free, the features are standard,
and the incumbents charge $600 largely on workflow and reputation. A good implementation with a
clean interface is a genuinely attackable market.

---

## 4. Sibilance, breath, and plosives — the classification generation

The progression here is instructive:

| generation | method | problem |
|---|---|---|
| **bandpass de-esser** | compress 5–8 kHz | ducks on bright vowels and cymbal bleed too |
| **spectral de-esser** (Pro-DS, SuprEsser) | high-band **ratio** to total energy | better, still level-based |
| **classification** (Sibilance, DeBreath) | recognise the *signature* — sibilance is noise-like, breath has a characteristic envelope | needs a real detector |
| **separation** (Clarity Vx) | neural voice/non-voice split | dataset problem |

**The insight that connects this to the rest of the repo:** sibilance is **stochastic** and vowels
are **harmonic**. So the harmonic/percussive split (`IDEAS.md` §1) is a *better sibilance detector
than any bandpass* — sibilance lands almost entirely in the percussive/noise stream.

Same for plosives: a plosive is a low-frequency transient, so it's percussive-stream energy below
200 Hz. Trivial to detect once you have the split, and very hard to detect reliably without it.

**This is the argument for building SPLIT first.** It makes three vocal products nearly free.

---

## 5. Clarity Vx and the neural generation

**[inf]** A trained model separating voice from everything else — noise, room, bleed, other
instruments. Different engineering discipline entirely:

- it's a **dataset and training** problem, not a DSP problem
- inference cost and latency are the constraints, not algorithmic elegance
- it fails *differently* — not with predictable artefacts but with occasional uncanny errors, which
  is harder to tell a user about

**Scope this honestly if it ever comes up.** It is not "a plugin with a neural net in it," it is a
machine-learning product with a plugin wrapper, and the work is 80% data.

---

## The vocal chain we should build, in order

Notice how much of this falls out of things already on the lists:

1. **SPLIT** (`IDEAS.md` §1) → de-esser, de-plosive, de-breath, and transient control, from one
   engine. **Start here.** Three products for one build.
2. **A resonance suppressor** (`RESONANCE-AND-AUTO-EQ.md` §1) — local-contrast detection. The
   single most-used modern vocal tool, and the mechanism is now clear.
3. **MARGIN** (`IDEAS.md` §2) — the vocal's whole job is to sit in a mix. A masking-aware rider is
   a vocal plugin more than it is a mix plugin.
4. **Formant shifting** via spectral-envelope manipulation — cheap, high perceptual impact, and
   the foundation for anything voice-identity related later.
5. **Alignment** via DTW — the most attackable expensive incumbent on this list.
6. **Pitch correction** — only after a pitch tracker is genuinely reliable. A tracker with octave
   errors is worse than no product, because the failures are loud.
7. **Polyphonic separation** — months, not weeks. Needs a sinusoidal-modelling framework. Do not
   scope this casually.

## Measure these

```
soothe2 on a vocal    response — where does it actually cut on a real voice
Pro-DS                envelope + response — detector behaviour on sibilance vs a bright vowel
Little AlterBoy       response with formant swept, pitch fixed — the envelope-scaling curve
Clarity Vx            response on voice+noise — artefact character, and where it fails
Waves Tune Real-Time  pitch-step test: feed a slow glide and measure the correction trajectory
                      at several Retune Speeds. That curve IS the product.
```

The Waves Tune measurement is the interesting one. Feed a controlled glide, measure how the output
pitch tracks it at each Retune Speed setting, and you have the correction trajectory as data —
which is exactly the target to implement against, and it also tells you where the hard-snap
aesthetic lives as a number.
