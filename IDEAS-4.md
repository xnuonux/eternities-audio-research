# Plugin ideas, batch 4 — perceptual decisions the ear already makes

This file continues `IDEAS-3.md` and asks a narrower question:

> **What latent decisions does human hearing already make automatically that audio production software rarely exposes as a direct control?**

The research pass deliberately looked beyond pitch, loudness, spectrum, width, reverb amount, source separation and conventional modulation. It focused on psychoacoustic variables that are *inferred* by the listener from combinations of ordinary acoustic cues.

The strongest additional candidates are:

- inferred **source power** rather than at-ear loudness
- inferred **mass / impact force** rather than transient level
- **eventhood versus texture** rather than grain density
- **event / phrase boundary strength** rather than cutting or gating
- **approach / looming** rather than simple distance or volume automation
- perceived **source numerosity** rather than unison voice count
- causal **source–room binding** rather than wet/dry
- **spatial compactness / diffuseness** rather than ordinary stereo width
- global **causal plausibility** rather than realism of one individual model

Two scientifically real percepts were also investigated but are *not* clean greenfield categories:

- externalization (inside-head ↔ out-in-world) — prior-art plugins already expose related controls
- apparent source width — mature room/spatial-audio literature and many adjacent processors exist

Novelty statements below remain hypotheses until a dedicated product/patent/prior-art search is performed.

---

# 29. POWER — source power independent of playback loudness

## The new knob

**FRAIL SOURCE ← SOURCE POWER → IMMENSE SOURCE**

A listener does not only perceive the sound pressure arriving at the ears. Human listeners can infer something closer to the *power emitted by the distal source* after accounting for distance and reverberation.

This distinction is experimentally important. A distant scream and a nearby whisper can arrive at comparable levels but are not perceived as equally powerful events. Work on loudness constancy and causal sound recognition indicates that listeners use reverberation / distance cues together with received intensity to infer source strength.

Research anchors:

- Traer, Norman-Haignere & McDermott, **Causal inference in environmental sound recognition**: https://pubmed.ncbi.nlm.nih.gov/34044231/
- Kolarik et al., **Auditory distance perception in humans** review: https://link.springer.com/article/10.3758/s13414-015-1015-1
- review of distal vs proximal loudness: https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2021.583690/full

## Product hypothesis

Most dynamics plugins alter level. Saturators can imply effort, but only incidentally. POWER would target the inferred generative variable:

> **How energetic / powerful does the producer want the listener to believe the source itself was?**

while allowing the final LUFS and peak to remain locked.

### Likely mechanisms

This cannot be one universal static transfer curve. It needs source-aware modes or a general inference model.

Candidate cue families:

- performance-dependent spectral tilt / brightness
- transient-force signatures
- nonlinear harmonic growth with excitation
- source-dependent noise / breath / scrape contribution
- dynamic formant / resonance shifts where physically appropriate
- distance / DRR consistency
- frequency-dependent radiation changes
- envelope changes associated with stronger excitation

The plugin should distinguish:

- **AT-EAR LEVEL** — what reaches the listener
- **DISTANCE** — where the source appears to be
- **SOURCE POWER** — how much acoustic energy the source appears to generate

Those three variables are physically coupled in nature but need not be locked together in production.

## Killer demonstrations

- make a vocal feel shouted rather than spoken while matching output LUFS
- make a drum feel physically struck harder without simply turning up its transient
- make a distant source feel catastrophically powerful while keeping its monitor level modest
- automate SOURCE POWER while locking apparent distance

## Acceptance

Use recorded sources with known performance-intensity contrasts and create matched-loudness stimuli.

A successful prototype must:

1. produce monotonic listener ratings of source effort / power at matched short-term loudness;
2. preserve perceived distance in a DISTANCE-LOCK condition;
3. preserve nominal pitch;
4. outperform a simple EQ+saturation baseline in forced-choice judgments.

If listeners merely report “brighter” or “more distorted,” the abstraction has failed.

## Competition / risk

Distance processors exist. Saturators and transient shapers exist. Searches did not reveal an obvious mainstream processor whose primary macro is **inferred distal source power at constrained playback loudness**.

The scientific variable is strongest for identifiable natural sources, so a generic all-material mode may be less convincing than source-aware modes.

**Priority: very high.**

---

# 30. GRAVITY — inferred mass and impact force

## The new knobs

**LIGHT ← MASS → HEAVY**

**GENTLE ← FORCE → VIOLENT**

These are not the same variable.

Impact-sound research suggests listeners infer physical properties of colliding objects and can separate some impactor cues from properties of the resonating surface. This creates an opportunity to manipulate the *cause* of an existing transient after it has been recorded.

Research basis includes work showing that listeners infer material, geometry, impactor properties and causal variables from impact acoustics; modal-synthesis literature provides a tractable source model.

## Product hypothesis

A post effect for drums, Foley, percussion, doors, footsteps, impacts and plucked / struck instruments that lets the producer change the imagined physical event:

- heavier striker, same surface
- harder strike, same mass
- softer contact, same force
- larger momentum transfer, same output loudness

This differs from a transient designer because the attack envelope is only one consequence of the inferred event.

## Engine

Start with excitation–resonance decomposition:

`observed sound ≈ excitation ⊛ resonant body + residual`

Estimate:

- transient / force pulse duration
- spectral excitation envelope
- modal frequencies and decay constants
- mode excitation weights
- stochastic collision residue

Then re-excite the estimated resonator with a modified contact model.

Possible macro parameters:

- **Mass**
- **Force**
- **Hardness**
- **Contact**
- **Rebound**
- **Body Lock**
- **Level Lock**

The important engineering constraint is that MASS and FORCE must not collapse into “more low end” and “more attack.”

## Acceptance

Build a controlled impact dataset where striker mass and impact velocity vary independently on the same resonant object.

Blind listeners should correctly order processed stimuli by intended MASS and FORCE while:

- output LUFS is matched;
- resonant-object identity remains stable;
- material classification does not drift materially in BODY-LOCK mode.

Compare against transient shaping, EQ and pitch shifting.

## Competition / risk

Physical-modeling instruments expose mass, stiffness and contact parameters during synthesis. The white-space hypothesis is **causal re-parameterization of an already-recorded impact**, not physical modeling itself.

**Priority: very high, especially for sound design and drums.**

---

# 31. CONTINUUM — event stream ↔ sound mass

## The new knob

**DISCRETE EVENTS ← CONTINUUM → SOUND MASS**

At sufficient density and under the right timbral / rhythmic conditions, individually resolvable events stop being heard as events and fuse into a texture or “sound mass.” The transition is not determined by event rate alone.

Research anchors:

- Douglas, Noble & McAdams, **Auditory Scene Analysis and the Perception of Sound Mass in Ligeti’s Continuum**: https://doi.org/10.1525/mp.2016.33.3.287
- McDermott & Simoncelli, auditory texture statistics: https://pmc.ncbi.nlm.nih.gov/articles/PMC4143345/
- McWalter & McDermott, temporal averaging of auditory textures: https://doi.org/10.1016/j.cub.2018.03.049
- MacKay, **On the perception of density and stratification in granular sonic textures**: https://doi.org/10.1080/09298218408570451
- 2025 TexStat / texture synthesis work: https://dafx25.dii.univpm.it/wp-content/uploads/2025/09/DAFx25_paper_14.pdf

## Product hypothesis

Granular plugins expose grain count. CONTINUUM instead targets the listener's categorical percept:

> “I hear separate objects” ↔ “I hear one continuous material.”

It should coordinate every cue that determines event identifiability, rather than merely increasing density.

### Toward SOUND MASS

- increase / redistribute event overlap
- reduce event-specific onset contrast
- reduce stable identity differences among events
- preserve or intentionally reshape long-term auditory texture statistics
- move rapid event structure toward summary-statistic representation
- suppress emergent rhythms that cause re-segmentation

### Toward DISCRETE EVENTS

- identify latent modulation peaks / events in an existing texture
- increase local onset contrast
- sparsify redundant events
- create stable event families
- restore temporally informative detail from the source where available

## Why this is not “granular density”

Two signals can have the same event rate and radically different perceptual fusion because pitch organization, attack sharpness, timbre, emergent rhythm and statistical stationarity differ.

CONTINUUM's target variable is the *perceptual phase transition*.

## Acceptance

Use stimuli with constant physical event rate while changing other grouping / texture cues.

At matched LUFS and comparable long-term spectrum, blinded listeners must show a monotonic shift in:

- number of individually reportable events;
- “sequence / flow / swarm / texture / mass” ratings;
- event-count accuracy.

The strongest demo keeps BPM and average spectral balance fixed while the percept crosses from countable notes into material.

## Competition / risk

Granular and texture synthesizers are crowded. The differentiator must remain the **perceptual transition target**, not “another grain engine.”

**Priority: extremely high. This may be as conceptually foundational as BIND.**

---

# 32. EDGE — perceptual event / phrase boundary strength

## The new knob

**CONTINUE ← BOUNDARY → NEW EVENT**

Listeners continuously segment sound into events, phrases and sections. Research on musical boundary perception indicates that local change is only part of the story: predictive uncertainty / entropy can influence where listeners hear a boundary even independently of simple surprise.

Research anchors:

- **Predictive Uncertainty Underlies Auditory Boundary Perception**: https://doi.org/10.1177/0956797621997349
- work on expectation and auditory boundary perception: https://journals.sagepub.com/doi/10.1068/p6507

## Product hypothesis

An audio processor that changes **how strongly the listener experiences “something ended and something new began”** without requiring a hard edit.

### Increase boundary strength

Coordinate subtle resets across several dimensions:

- micro-rest / envelope reset
- spectral-envelope reset
- modulation-phase reset
- spatial compactness reset
- common-fate break
- transient novelty
- predictive-entropy peak

### Reduce boundary strength

Bridge those same dimensions:

- continuity-preserving interpolation
- overlap / masking at the join
- common modulation trajectory
- spectral-envelope continuation
- room / space continuity
- expectation-consistent transition

SEAM operates mainly on continuity of a *source through an interruption*. EDGE operates on the **segmentation of sequential musical structure**.

## Killer uses

- make a chorus feel as if it “arrived” harder without increasing its level
- soften a bad edit without smearing it with reverb
- make a loop stop feeling looped by weakening its wrap boundary
- create phrase punctuation on pads / drones without gating them

## Acceptance

Have listeners mark perceived event / phrase boundaries in processed passages.

EDGE must move boundary probability and boundary-strength ratings monotonically while conservative mode keeps:

- section LUFS within 0.25 dB;
- coarse spectral balance constrained;
- note timing unchanged unless explicitly enabled.

A simple fade / transient boost baseline is the comparison.

**Priority: high. Technical difficulty is moderate; perceptual validation is essential.**

---

# 33. LOOM — approach / threat motion without a volume ride

## The new knob

**RECEDING ← LOOM → APPROACHING**

Approaching sounds receive privileged perceptual treatment. Auditory looming biases have been demonstrated with cues beyond simple increasing level, including spectral / spatial manipulations.

This means “coming toward me” is a perceptual variable that can be targeted separately from “getting louder.”

## Product hypothesis

LOOM makes a source feel as though its physical trajectory is approaching or retreating while a loudness lock prevents the trivial solution of simply turning it up or down.

Candidate cues:

- direct / reverberant balance trajectory
- near-field spectral / binaural changes
- externalization trajectory
- frequency-dependent air / room cues
- apparent source-width changes
- optional Doppler only when desired
- dynamic spectral cues that are known to contribute to approach judgments

The key mode is **LEVEL LOCK**.

A source gets psychologically closer / more urgent while measured short-term loudness remains approximately fixed.

## Killer uses

- a riser that feels physically incoming without a crescendo
- a vocal that advances toward the listener during a phrase
- cinematic danger / impacts without consuming more headroom
- receding tails that leave perceptual depth without just fading away

## Acceptance

At matched loudness, randomized listeners classify direction of motion.

Require substantially above-chance APPROACH / RECEDE identification with:

- no net pan movement;
- no monotonic output-level cue;
- optional Doppler disabled for the hardest test.

Measure urgency / threat ratings separately from distance ratings to determine whether LOOM is merely another distance control.

## Competition / risk

Doppler, motion and distance plugins exist. The differentiated product is **looming at constrained loudness**, not general 3D movement.

**Priority: high for creative/cinematic production.**

---

# 34. MULTITUDE — perceived number of sources

## The new knob

**ONE ← SOURCE COUNT → TWO → THREE → FOUR → MANY**

Auditory numerosity is a real perceptual variable. Humans can estimate the number of simultaneous sources, but performance saturates quickly — commonly around three to five sources depending on content and conditions.

Recent work also suggests that numerosity is influenced strongly by **spectrotemporal coverage**, not simply spatial acuity.

Research anchors:

- **Towards Size of Scene in Auditory Scene Analysis: A Systematic Review**: https://doi.org/10.7874/jao.2019.00248
- Zhong & Yost, **How many images are in an auditory scene?**: https://pmc.ncbi.nlm.nih.gov/articles/PMC6909977/
- 2025 polyphonic-music study on harmonicity and voice count: https://doi.org/10.1038/s41598-025-16404-8
- 2026 **Auditory Numerosity Judgement is Driven by Non-Spatial Factors Across Azimuth, Elevation, and Distance**: https://osf.io/b39dw
- 2025 Bayesian source-count / clustering model: https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013189

## Difference from BIND

BIND manipulates **fusion strength / objecthood**.

MULTITUDE explicitly targets a desired *scene cardinality*.

It therefore needs stable latent source families, not just more or less decorrelation.

## Engine hypothesis

Decompose audio into partial / event / residual components and cluster them into `N` coherent families. Each family gets internally consistent:

- harmonic support
- onset relationships
- amplitude modulation
- frequency micro-motion
- timbral evolution
- spatial trajectory

while between-family coherence is reduced enough to encourage perceptual segregation.

For `N=1`, families converge and common-fate cues increase.

For `N=2..4`, the engine creates that many stable perceptual identities.

For MANY, it crosses toward scene-level density rather than pretending humans can precisely enumerate 17 sources.

## Killer demo

One sustained / polyphonic source becomes perceptually:

**one organism → two independent entities → a quartet → a crowd**

without conventional cloning or obvious fixed pitch detuning.

## Acceptance

Blind listeners report perceived source count. Median responses should follow the target for 1–4 and then transition into a stable “many” region.

Additional constraints:

- output LUFS matched;
- source count should not be predictable only from stereo width;
- mono tests should retain at least part of the count effect;
- compare against standard unison / chorus / Haas widening.

**Priority: very high research value; harder than BIND.**

---

# 35. BELONG — causal source–room binding

## The new knob

**PASTED ON ← BELONGING → EMBEDDED IN THE SPACE**

Human hearing does not merely hear “dry source + reverb.” Evidence suggests the brain partially separates a reverberant signal into a source and an environmental filter using priors learned from the statistics of natural reverberation.

Research anchors:

- Traer & McDermott, **Statistics of natural reverberation enable perceptual separation of sound and space**: https://doi.org/10.1073/pnas.1612524113
- neural source / room separation: https://www.eneuro.org/content/eneuro/4/1/ENEURO.0007-17.2017.full.pdf
- 2024 work on separating object resonance and room reverberation: https://escholarship.org/uc/item/00h8w7q9
- 2024 eNeuro work on perceptual decisions for natural vs synthetic reverberation: https://www.eneuro.org/content/11/8/ENEURO.0122-24.2024

## Product hypothesis

Reverb wet/dry tells us how *much* reverberant energy exists.

BELONGING asks a different question:

> **Does the auditory system attribute this reverberation to the same physical event and environment as the source?**

### Embedded direction

Make room cues causally consistent with the source:

- tail envelope tracks the source in physically plausible ways
- frequency-dependent decay follows natural-room priors
- early / late structure agrees with distance
- DRR is internally coherent
- source and reflection onset relationships obey precedence / fusion constraints
- modulation statistics avoid sounding like a separate layer

### Pasted direction

Intentionally weaken attribution while preserving nominal wet level and approximate RT60:

- subtly inconsistent decay statistics
- decorrelated envelope relation
- reflection patterns that do not agree with implied source distance
- environmental tail with an independent “behavior”

The goal is not necessarily realism. The producer might deliberately make a reverb sound like a separate supernatural object.

## Killer uses

- make algorithmic reverb sit *inside* a recorded performance instead of behind it
- make an ambient tail detach and become its own entity
- embed samples from different acoustic origins into one perceived environment

## Acceptance

At matched wet/dry, RT60 and approximate spectral balance, listeners rate:

- source–room belonging / unity
- obviousness of the effect layer
- plausibility of a shared environment

If ratings track only reverb amount, the processor has failed.

## Product role

BELONG may be more valuable as an internal Eternities reverb technology than as a standalone VST.

**Priority: high as platform IP.**

---

# 36. FOCUS — compact point ↔ diffuse field

## The new knob

**PUNCTATE / FOCUSED ← IMAGE COMPACTNESS → DIFFUSE / FIELD-LIKE**

Interaural coherence and the stability of binaural cues influence whether a sound is heard as a compact auditory object or a diffuse image. This percept can change without changing ordinary frequency response or signal power.

Research anchor:

- **Human cortical processing of interaural coherence**: https://pmc.ncbi.nlm.nih.gov/articles/PMC9051632/

## Why this is not just width

Stereo width often means L/R separation or side level.

Compactness concerns the *reliability and focus of the auditory image*.

A source can be centered yet diffuse; wide yet composed of stable compact objects; or apparently point-like while surrounded by a diffuse field.

## Engine

Manipulate short-time, frequency-dependent interaural coherence and cue variability while locking:

- image centroid
- broadband level
- optionally conventional M/S width

Expose:

- **Focus**
- **Field**
- **Centroid Lock**
- **Width Lock**
- **Mono Guard**

## Acceptance

At matched centroid and conventional width metrics, listeners must reliably order stimuli by compactness / diffuseness.

## Competition / risk

This is scientifically clean but commercially adjacent to decorrelators, stereo imagers and spatial processors. It is likely an **EPD primitive** that strengthens BIND, BEACON, LOOM and room processing rather than a flagship standalone invention.

**Priority: medium as product, high as infrastructure.**

---

# 37. OUTSIDE — externalization independent of distance

## The new knob

**IN THE HEAD ← EXTERNALIZATION → OUT IN THE WORLD**

Research shows that perceived externalization and perceived distance overlap but can be dissociated under some conditions.

That makes externality a legitimate perceptual coordinate, separate from pan, width and distance.

However, this is **not greenfield**. Binaural research tools and products already include “externalization” enhancement; Anaglyph, for example, has shipped an Externalisation Booster.

Therefore Eternities should not position OUTSIDE as a foundational invention unless a new mechanism or dramatically broader stereo-speaker-compatible formulation is discovered.

Use the science as a platform primitive for LOOM / PARALLAX / spatial rendering.

**Priority: low as standalone, medium as shared technology.**

---

# 38. REALITY — causal plausibility as a macro

## The new knob

**IMPOSSIBLE ← CAUSAL PLAUSIBILITY → PHYSICALLY COHERENT**

A growing body of auditory research supports the view that listeners infer latent physical causes rather than merely classify spectral patterns.

Examples:

- source power is judged using intensity + inferred distance;
- source and reverberant environment are separated using priors on natural room statistics;
- material / geometry / excitation can be inferred from impact acoustics;
- physically inconsistent combinations can impair source recognition or be heard as unnatural.

This suggests a meta-effect above SUBSTANCE, ORIGIN, SCALE, POWER, GRAVITY and BELONG.

## Product hypothesis

REALITY analyzes an incoming sound as a causal graph:

`gesture / force → source body / material → radiation → distance → environment → listener`

and estimates whether the cue relationships are mutually plausible.

Then a single macro can:

### Move toward REAL

Make the smallest changes necessary to satisfy the selected causal constraints.

Examples:

- a huge resonant object should not have a tiny-object modal pattern unless deliberately locked
- distance / source power / air loss / DRR should agree
- impact hardness / excitation spectrum / resonant response should agree
- room tail should obey natural decay statistics

### Move toward IMPOSSIBLE

Deliberately violate *one causal relation at a time* while holding the others stable.

That is more interesting than random mangling because the sound becomes **coherently impossible**.

Examples:

- colossal physical size with miniature modal density
- whisper-level source power that seems kilometers away yet remains identifiable
- wooden material with metal-like loss behavior but preserved body geometry
- a room whose decay behaves as if it were part of the source

## Acceptance

This cannot be validated with a null test.

Build a dataset of natural and controlled synthetic physical events. Ask listeners to rate:

- physical plausibility
- source recognizability
- material / size / force consistency
- “synthetic / impossible” character

REAL mode should increase plausibility without simply making material darker / smoother. IMPOSSIBLE mode should decrease plausibility predictably while preserving musical usefulness.

## Strategic significance

REALITY may eventually become the **constraint system behind AXIS** rather than one plugin.

AXIS asks for a perceptual destination.

REALITY supplies a model of which combinations are physically coherent.

**Priority: long-term, potentially enormous.**

---

# Research map — what the ear infers versus what plugins normally expose

| Auditory inference | Existing conventional control | Eternities primitive |
|---|---|---|
| component ownership | none / indirect separation tools | **BIND** |
| number of sources | unison voices, chorus | **MULTITUDE** |
| discrete events vs texture | grain density | **CONTINUUM** |
| continuity through occlusion | gates / noise / edits | **SEAM** |
| event / phrase boundary | fades / edits / transient shaping | **EDGE** |
| source power | fader / saturation | **POWER** |
| impact mass / force | transient / EQ | **GRAVITY** |
| physical size | pitch / formant | **SCALE** |
| material | EQ / convolution | **SUBSTANCE** |
| excitation action | transient shaping | **ORIGIN** |
| pitch certainty | pitch correction | **CERTAIN** |
| attention capture | level / EQ | **BEACON** |
| approach / looming | gain ramp / Doppler | **LOOM** |
| source-room causal unity | wet/dry | **BELONG** |
| spatial compactness | stereo width | **FOCUS** |
| externalization | binaural spatializers | **OUTSIDE** (existing category) |
| modulation-timescale content | compressor / tremolo | **VELOCITY** |
| perceptual bistability | none obvious | **RIVAL** |
| prediction / surprise | generative MIDI / random FX | **EXPECT** |
| causal plausibility | no general macro | **REALITY** |

---

# The deeper architecture: an auditory causal graph

`IDEAS-3.md` proposed Eternities Perceptual DSP (EPD). This research suggests EPD should not just be a bag of perceptual meters. It should explicitly represent a **causal scene graph**.

A first useful state could be:

```text
AUDITORY SCENE
├── environment
│   ├── room size / decay
│   ├── diffuseness
│   └── naturalness / prior probability
├── source objects [N]
│   ├── source identity confidence
│   ├── material
│   ├── physical scale
│   ├── source power
│   ├── compactness
│   ├── position / distance / motion
│   └── event stream
│       ├── excitation gesture
│       ├── mass / force
│       ├── pitch certainty
│       └── boundary / continuity state
└── relations
    ├── component ownership
    ├── common fate
    ├── source ↔ room belonging
    ├── masking
    ├── attentional salience
    └── causal plausibility
```

The processor can then change a latent node while optimizing the waveform so other locked nodes remain stable.

That is the general form behind nearly every strong invention in `IDEAS-3.md` and this file.

---

# Updated strongest bets

## Tier A — plausible new effect categories

1. **BIND** — auditory objecthood / ownership
2. **CONTINUUM** — discrete event ↔ sound mass
3. **POWER** — inferred source power independent of loudness
4. **GRAVITY** — inferred mass / force re-parameterization
5. **MULTITUDE** — perceived source numerosity
6. **EDGE** — perceptual boundary strength
7. **VELOCITY** — modulation-spectrum EQ

## Tier B — differentiated creative effects built on strong perceptual science

8. **LOOM** — approaching / receding at constrained level
9. **SEAM** — continuity / occlusion illusion
10. **CERTAIN** — pitch certainty
11. **BEACON** — attentional salience
12. **BELONG** — source–room causal binding
13. **SCALE** — apparent source size independent of nominal pitch
14. **RIVAL** — bistable auditory organization

## Tier C — strategic platform technologies

15. **REALITY** — causal plausibility optimizer
16. **AXIS** — constrained perceptual optimizer / macro interface
17. **FOCUS** — compactness / diffuseness primitive
18. **OUTSIDE** — externalization primitive; prior art means do not lead with novelty

---

# What to prototype first now

The previous build order put BIND first. Keep that.

But the quickest experiments that can *falsify or validate the new thesis* are:

### Experiment A — POWER

Use controlled vocal / instrument performances at several physical effort levels. Loudness-match them. Train / fit only enough analysis to derive source-power cues. Then attempt to move a medium-effort recording toward the low/high distributions without changing LUFS.

If listeners reliably report effort / source power rather than “EQ difference,” continue.

### Experiment B — CONTINUUM

Start with synthetic event trains at a fixed event rate. Independently manipulate onset sharpness, pitch organization, modulation statistics and event identity. Find a stable mapping from features to listener “events vs mass” reports.

Do not build the VST until the perceptual control curve exists.

### Experiment C — EDGE

Use short musical phrases and have listeners mark boundaries. Build a model from multi-feature novelty + predictive entropy. Then modify boundary cues while holding note sequence and approximate loudness fixed.

### Experiment D — GRAVITY

Record or synthesize controlled impacts with independent striker mass / velocity / material. Determine which features allow listeners to separate MASS from FORCE before attempting generic decomposition.

### Experiment E — MULTITUDE

Use one synthetic harmonic source decomposed into component families. Sweep common-fate coherence, harmonic support, onset synchrony and timbral separation, and measure reported source count from 1–4.

These five experiments answer whether Eternities can truly manipulate **latent auditory causes** rather than merely relabel familiar DSP.

---

# Current conclusion

The answer to the original question is now more precise.

The unexplored territory is not merely “psychoacoustic effects.”

It is:

> **causal audio processing — directly controlling the hidden physical and organizational causes that the human auditory system infers from a waveform.**

Classic DSP maps waveform → waveform.

A mature EPD system would map:

`waveform → inferred auditory world → edit latent cause → waveform`

If this works perceptually, that is a substantially larger idea than a new distortion topology.
