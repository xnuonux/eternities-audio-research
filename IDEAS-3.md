# Plugin ideas, batch 3 — the perceptual-inference layer

## Thesis

Classic audio effects mostly manipulate coordinates of the waveform:

- amplitude / dynamics
- frequency / spectrum
- phase
- pitch
- time
- space
- nonlinearity
- modulation

The larger unexplored design space is one level above the waveform: **the latent variables the auditory system infers from sound**.

The ear does not merely measure a waveform. It constructs auditory objects and asks, implicitly:

- how many sources are present?
- which components belong to the same source?
- is the source continuous through an interruption?
- how strong / certain is its pitch?
- how attention-grabbing is it relative to context?
- how large is the source?
- what material is it made from?
- what action excited it?
- how predictable is its evolution?
- how quickly does its character change?

That gives Eternities Audio a new product strategy:

> **Give producers knobs for perceptual inferences, not only signal parameters.**

This document extends `IDEAS.md` and `IDEAS-2.md`. It also incorporates the separate concepts RECALL, SUBSTANCE, ORIGIN, TENSION, LUCID, THERMAL and AXIS.

Research anchors:

- 2026 review of musical auditory scene analysis: https://link.springer.com/article/10.3758/s13414-026-03310-y
- auditory stream formation review: https://pmc.ncbi.nlm.nih.gov/articles/PMC3282308/
- pitch/harmonicity and concurrent segregation: https://pmc.ncbi.nlm.nih.gov/articles/PMC2885481/
- auditory continuity work: https://doi.org/10.26481/dis.20090401lr
- acoustic scale / size perception: https://pmc.ncbi.nlm.nih.gov/articles/PMC2821800/
- auditory salience in natural soundscapes: https://pmc.ncbi.nlm.nih.gov/articles/PMC6909985/
- pitch salience / periodicity: https://pmc.ncbi.nlm.nih.gov/articles/PMC3171186/

Novelty language in this file is deliberately conservative. A missing product in a search is not proof of first invention.

---

# 19. BIND — auditory objecthood as an effect

## The new knob

**FISSION ← OBJECTHOOD → FUSION**

Instead of changing EQ, width, level or delay as endpoints, BIND changes the probability that the listener hears components as **one source versus multiple sources**.

Auditory-scene research identifies several grouping cues that can be manipulated:

- onset / offset synchrony
- harmonicity and F0 agreement
- spectral / timbral similarity
- common amplitude modulation
- common frequency modulation
- spatial similarity
- parallel pitch and dynamic motion
- continuity through time

The important point is that these cues jointly influence auditory grouping. BIND would coordinate them behind one perceptual control.

### Single-track mode

Decompose an input into tracked partial / transient / residual groups. At FUSION:

- tighten partials toward common harmonic support without hard pitch quantization
- increase onset synchrony across groups
- correlate slow amplitude and frequency micro-modulation
- reduce contradictory spatial cues
- make spectral-envelope evolution more common-fate

At FISSION:

- selectively decorrelate those cues
- divide partials into stable families
- stagger micro-onsets
- introduce bounded differences in modulation trajectory
- distribute families spatially while protecting mono compatibility

The goal is not a chorus. The goal is changing **perceived source count and grouping**.

### Multi-instance mode

One BIND on several tracks shares descriptors. FUSION makes a guitar, synth and backing vocal behave perceptually more like one orchestral color. FISSION increases their perceptual independence without merely panning or EQ-notching them.

### Acceptance

This needs psychophysics, not just null tests.

Build controlled ABA / interleaved-melody and concurrent-tone tests based on published auditory-streaming paradigms. With level and gross spectrum held approximately constant, blinded listeners must show a monotonic change in one-stream vs multi-stream reports as OBJECTHOOD moves.

Secondary constraints:

- no unintended >0.25 dB short-term loudness drift in conservative mode
- no >1 dB mono-fold loss in conservative mode
- no note-level retuning greater than a user-set bound

### Status

**Highest-priority invention candidate.** The scientific phenomenon is established; the proposed producer-facing control is the novel product hypothesis.

---

# 20. VELOCITY — modulation-spectrum EQ

## The new knob

**EQ the speed of change rather than the frequency of sound.**

A conventional EQ asks how much energy exists at 100 Hz, 1 kHz, 10 kHz.

VELOCITY asks how much a perceptual band changes at:

- 0.05–0.5 Hz — drift
- 0.5–2 Hz — sway
- 2–8 Hz — pulse / syllabic-scale movement
- 8–30 Hz — flutter / texture
- 30–150+ Hz — roughness / microstructure

Use a gammatone or ERB analysis bank, extract band envelopes (and optionally instantaneous-frequency trajectories), then analyze those envelopes with a second modulation-frequency filterbank.

That creates a 2-D representation:

`carrier frequency × modulation frequency`

The effect can boost or suppress energy in *modulation-rate space* and resynthesize a signal whose long-term spectrum can remain almost unchanged while its temporal life changes radically.

Examples:

- remove 4–8 Hz modulation from a vocal without simply compressing it
- exaggerate 0.5–2 Hz movement in pads
- suppress 20–80 Hz roughness while preserving brightness
- turn a static source into one with natural-scale microactivity by borrowing its own modulation statistics

This is related to modulation-spectrum analysis used in psychoacoustics and audio evaluation, but the product is an **interactive modulation-rate equalizer**.

### Acceptance

Create AM/FM test signals at known modulation frequencies. Each modulation band must selectively raise / lower the intended modulation component while keeping carrier-frequency magnitude response within a defined tolerance at neutral.

Listening test: two outputs matched for long-term spectrum and LUFS but with strongly different modulation-EQ settings must produce reliably different judgments of stillness / movement / roughness.

### Status

**Very strong.** Market searches found modulation-spectrum analysis and research uses, but not an obvious mainstream general-purpose modulation-spectrum processor. Continue prior-art search before novelty claims.

---

# 21. SEAM — perceptual continuity processor

## The new knob

**BROKEN ← CONTINUITY → UNBROKEN**

The continuity illusion shows that a physically interrupted tone or stream can be perceived as continuing through a masker when the auditory evidence supports that interpretation.

SEAM would deliberately engineer this inference.

### Modes

**HEAL** — when audio drops out or is intentionally gated, construct a spectrally appropriate masker / residual that encourages the brain to hear the original stream as persisting through the missing interval.

**FRACTURE** — create perceptual discontinuity in a physically continuous signal by violating continuity / grouping cues at selected boundaries.

**GHOST** — remove physical signal during selected intervals while making the listener perceive a stronger sense that it remains behind the interruption.

### Creative uses

- impossible vocal edits whose line feels continuous through noise
- guitars that disappear physically but feel as if they pass behind another object
- drums that fracture into separate perceptual events without hard gating
- transitions that hide edits inside perceptual restoration

### Acceptance

Psychophysical AB tests using interrupted tones and musical lines. At equal physical gap duration, HEAL must materially increase continuity reports over silence and over spectrally mismatched masker controls.

### Status

Scientific foundation is strong. Search found continuity research but no obvious mainstream music-production VST centered on the illusion.

---

# 22. CERTAIN — pitch-strength processor

## The new knob

**AMBIGUOUS ← PITCH CERTAINTY → DEFINITE**

Pitch has more than a value. It has **salience / strength**. Periodicity research shows perceived pitch salience varies with periodic structure.

Most plugins move pitch. CERTAIN changes how strongly the listener believes a pitch exists while attempting to preserve its nominal value.

### Increase certainty

- reinforce periodicity around tracked F0
- gently organize near-harmonic partials
- reduce competing aperiodic energy only where it masks periodic structure
- phase / envelope handling that strengthens periodic evidence

### Decrease certainty

- bounded partial detuning
- selective temporal jitter
- partial bandwidth broadening
- periodic-to-residual redistribution

At low settings a vocal, synth or guitar becomes spectrally ghostlike / uncertain without simply becoming noise. At high settings its pitch becomes unusually solid without Auto-Tune-style note correction.

### Acceptance

Use established pitch-salience models / periodicity metrics plus listener pitch-strength ratings. Fundamental estimate must stay within a tight cent tolerance while perceived strength changes monotonically.

---

# 23. BEACON — attention as an audio effect

## The new knob

**IGNORE ← SALIENCE → NOTICE**

Audio salience is context-dependent: change, spectral contrast, temporal contrast, pitch, micro-modulation, timbral contrast and expectation violations can all pull attention.

BEACON would manipulate *bottom-up attentional capture* while constraining loudness and peak.

The engine analyzes the target against either:

1. its own recent history, or
2. an external sidechain / mix context.

It then makes small distributed changes that increase or decrease predicted salience while respecting locks:

- LUFS lock
- peak lock
- tone-budget lock
- stereo lock

Attract mode might slightly increase context-relative spectral / temporal contrast and micro-modulation novelty. Recede mode minimizes those contrasts without simply turning the source down.

### Acceptance

At matched LUFS and true peak, blinded listeners in multi-source scenes should select the processed target earlier / more often in a rapid attention task as SALIENCE rises.

This is a research-heavy product because salience is listener- and context-dependent. Do not oversell a scalar model until validated.

---

# 24. RIVAL — perceptual bistability

## The new knob

**ONE STREAM ← AMBIGUITY → TWO STREAMS**

Auditory streaming has a bistable region in which perception can flip between one coherent stream and multiple streams even though the physical signal remains unchanged.

RIVAL deliberately drives material toward that boundary.

This is not merely BIND at 50%. BIND aims for controllable direction. RIVAL aims for **unstable perceptual interpretation**.

The engine maintains competing grouping cues:

- pitch proximity says “one” while timbre says “two”
- spatial location says “one” while modulation pattern says “two”
- common onset says “one” while partial families say “two”

The result could create musical material that appears to reorganize in the listener's head without a conventional modulation cycle.

### Acceptance

Repeated-trial listener reports should show elevated spontaneous percept switching near the target setting compared with stable FUSE and SPLIT controls.

This is speculative but potentially a completely new creative-effect experience.

---

# 25. SCALE — apparent acoustic size independent of pitch

## The new knob

**MINIATURE ← SCALE → COLOSSAL**

Listeners can infer physical source scale from sound. A generic effect could manipulate cues to apparent size while approximately preserving musical pitch and duration.

Candidate cues / mechanisms:

- modal spacing and density
- frequency-dependent decay
- inharmonicity / dispersion
- spectral-envelope scaling
- attack bandwidth
- formant / body resonance placement
- optional coherent room coupling

Unlike a pitch/formant shifter, SCALE's objective is a perceptual estimate: "this sounds like a larger object".

SUBSTANCE changes material. ORIGIN changes excitation gesture. SCALE changes inferred geometry.

### Acceptance

Listener forced-choice size judgments must move monotonically with SCALE while pitch-identification error stays within a defined bound.

---

# 26. EXPECT — acoustic predictability / surprise processor

## The new knob

**INEVITABLE ← SURPRISE → UNEXPECTED**

Rather than generate new notes, EXPECT models short-term regularities in the source — spectral envelope, rhythm, pitch trajectory, modulation trajectory, event timing — then controls the amount of deviation from those predictions.

Low surprise reinforces expected continuation.

High surprise introduces bounded changes specifically where the current event is most predictable, creating maximum perceptual novelty for minimum physical change.

Possible implementation:

- self-supervised short-context predictor at control rate
- prediction-error map over time-frequency / partial features
- constrained optimizer decides where tiny perturbations create the largest novelty increase

### Acceptance

A held-out predictor should measure monotonically increasing surprise while LUFS, peak and coarse spectrum stay within constraints. Human novelty / attention ratings are the decisive test.

This is more generative and less deterministic than the earlier concepts. Prototype after the lower-risk perceptual primitives.

---

# 27. COMMON FATE — coherence of motion

## The new knob

**INDEPENDENT ← COMMON FATE → TOGETHER**

Gestalt auditory grouping is influenced when components evolve together. Instead of adding an LFO, COMMON FATE measures the source's own slow amplitude, pitch, spectral and spatial micro-trajectories and controls their cross-band / cross-source coherence.

At TOGETHER, partial families and/or linked tracks breathe, drift and articulate in correlated ways.

At INDEPENDENT, the same amount of aggregate modulation is retained but distributed decorrelatively.

This means the amount of *movement* can remain nearly constant while the perceived unity of that movement changes.

This can be a BIND subsystem, but may deserve its own effect if the sound is compelling.

---

# 28. ABSTRACT — source recognizability

## The new knob

**IDENTIFIABLE ← SOURCE IDENTITY → ABSTRACT**

Timbre carries cues to source family, material and excitation. ABSTRACT would estimate a source-identity embedding and move the input toward or away from its own stable identity while preserving pitch, loudness and event envelope as much as possible.

Unlike ordinary timbre transfer, it does not ask “make this guitar sound like a cello.” It asks “how strongly should this sound continue to read as the thing that produced it?”

At the abstract extreme, source-cause cues are decorrelated while musical structure survives.

This may require learned embeddings and careful dataset provenance. Keep it behind the deterministic perceptual projects until its evaluation can be rigorous.

---

# Existing concepts mapped into the same layer

The earlier inventions fit this taxonomy:

- **RECALL** — auditory memory / associative recurrence
- **SUBSTANCE** — inferred material
- **ORIGIN** — inferred excitation gesture
- **TENSION** — sensory roughness / consonance
- **LUCID** — timbral velocity
- **THERMAL** — long-memory virtual physical state
- **AXIS** — perceptual constrained optimization

And `IDEAS.md` / `IDEAS-2.md` already cover:

- masking margin
- distance
- temporal masking
- precedence / fusion-window size
- acoustic geometry
- target-system psychoacoustic bass
- envelope coherence / glue
- arrangement occupancy
- perceptual loudness optimization

Together these are no longer a bag of plugins. They are the beginnings of a **perceptual audio engine**.

---

# What may actually be the next foundational effect

If distortion gave producers a **nonlinearity knob**, delay a **time-displacement knob**, reverb a **space/decay knob**, and chorus a **correlated pitch/time-variation knob**, the strongest candidate for a new foundational primitive here is:

> **OBJECTHOOD — how strongly the auditory system believes acoustic components belong to one source.**

That variable sits above several ordinary DSP parameters and changes the organization of the perceived scene itself.

The first prototype should therefore be **BIND**.

# Proposed research/build order

1. **BIND prototype** — controlled-tone / interleaved-melody engine first, plugin later.
2. **VELOCITY prototype** — modulation-spectrum analysis + resynthesis; technically measurable.
3. **CERTAIN prototype** — pitch salience without pitch correction.
4. **SEAM prototype** — continuity illusion on tones, then musical sources.
5. **RIVAL experiment** — determine whether bistability survives musical material strongly enough to productize.
6. **BEACON** — build only after a salience model is validated against listener data.
7. **SCALE** — leverage the modal / physical modeling code already developed for Eternities instruments.
8. **EXPECT** — highest research risk; potentially enormous if the perceptual effect survives constraints.

# Platform implication

Do not implement each project as an island.

Shared libraries should expose:

- ERB / gammatone auditory filterbank
- STFT + perfect reconstruction layer
- partial tracking / periodicity estimation
- modulation-spectrum analysis
- transient / event segmentation
- masking threshold model
- auditory-scene feature vectors
- perceptual constraint optimizer
- deterministic test-stimulus generator
- psychophysical ABX / forced-choice harness

Call this internal layer **Eternities Perceptual DSP (EPD)** until a better name emerges.

That shared substrate is likely more valuable than any single plugin.