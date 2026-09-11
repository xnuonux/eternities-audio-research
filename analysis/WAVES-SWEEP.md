# Waves: the full sweep

The rest of the 258, by category, with the transferable idea per group. `WAVES.md` covers the six
headline technologies; this is everything else, and several of these point at genuine gaps.

**[doc]** documented · **[std]** standard in the literature · **[inf]** my inference.

---

## Spatial and immersive — the most under-exploited group

**Nx · CLA Nx · Nx Germano Studios · Nx Ocean Way Nashville · WavesHeadTracker · B360 · C360 ·
L360 · S360 · R360 · MV360 · LFE360 · IR-360 · Immersive Wrapper · Spherix · Sub Align · TRACT**

**Nx is the interesting one.** It renders a real control room over headphones: measured HRTF
(head-related transfer function) + the room's measured impulse responses + **live head tracking**
via webcam or a hardware sensor. When you turn your head, the phantom speakers stay put. That
head-tracking is the difference between "reverb on headphones" and actually externalising the
image outside your skull. **[doc]**

Mechanism **[std]**:
- convolve each virtual speaker position with a left/right HRTF pair → binaural cues (ITD, ILD,
  spectral notches from the pinna)
- add the room's early reflections and tail per position
- **crosstalk cancellation is not needed** on headphones, which is why this is easier than
  speaker-based 3D and why it actually works
- head tracking rotates the whole virtual scene against head orientation, at low latency

**The transferable insight:** externalisation comes overwhelmingly from *head tracking plus
individualised-enough HRTF*, not from reverb quality. A mediocre room with tracking beats a
beautiful room without it.

**Brauer Motion** — autopanner with three independent panners on orbital paths, tempo-syncable.
Michael Brauer's actual mixing technique productised. **[doc]** The idea worth taking is that
motion is *compositional*, not an LFO: paths, phase relationships between elements, and
tempo-locked orbits.

**TRACT / Sub Align** — room correction and subwoofer time alignment. Measurement-driven: sweep
the room, compute correction. Same machinery as our harness, pointed at a room instead of a
plugin.

**Primary Source Expander (PSE)** — live sound. Instead of gating, it *expands* the difference
between the primary source and background bleed. Gentler artefacts than a gate because there's no
hard threshold. **[inf]** Clever and rarely copied.

---

## Pitch and voice — where the modern money is

**Waves Tune / Real-Time / LT · Waves Harmony · UltraPitch · Vocal Bender · OVox · Morphoder ·
Sync Vx · Reel ADT · Doubler · DeBreath · Sibilance · Silk Vocal · Clarity Vx (+Pro, DeReverb) ·
Torque · Key Detector**

The chain underneath almost all of these **[std]**:

1. **Pitch detection** — autocorrelation, YIN, or CREPE-class neural. Latency and octave errors
   are the two hard problems; a half-octave error is instantly audible in correction.
2. **Resynthesis** — phase vocoder (STFT, phase manipulation) or PSOLA (pitch-synchronous overlap
   add). PSOLA preserves transients and formants better on monophonic voice; phase vocoders
   smear but handle polyphony.
3. **Formant handling** — shift pitch without shifting formants or you get chipmunk. Separate the
   spectral envelope (cepstral liftering or LPC) from the excitation, shift one, keep the other.

**Waves Harmony** generates 8 voices with scale/key awareness — so it needs the pitch detector,
the shifter, *and* a music-theory layer that maps detected pitch to a harmony interval within a
key. **[doc]**

**Reel ADT** deserves attention for how simple it is: Abbey Road's automatic double tracking was
literally a second tape machine with varispeed wobble. **A delay of ~20–60 ms with independent
slow pitch drift is the whole effect**, and it beats most digital doublers. **[std]** Very high
value per unit effort.

**Sync Vx** aligns a double to a lead — dynamic time warping on the two signals, then variable
time-stretch to match. **[inf]** DTW is a solved algorithm; this is mostly UX.

**DeBreath** detects breaths by pattern-matching their spectral signature (broadband, noise-like,
characteristic envelope) and attenuates or replaces them. **[inf]** Notable as an early example of
*classification* rather than thresholding — the ancestor of the Clarity Vx line.

**Torque** retunes drums by tracking the membrane's fundamental and resynthesising — solves a real
problem nobody else had named. **[doc]**

---

## Metering and analysis — the category everyone under-invests in

**PAZ · WLM / WLM Plus · Dorrough · VU Meter · AR TG Meter Bridge · Waves Stream · Key Detector**

**PAZ (Psychoacoustic Analyzer)** — spectrum on a **critical-band** axis rather than linear or
log, plus stereo position and level. The critical-band part matters: a linear FFT display tells
you about signal, a Bark/ERB display tells you about *hearing*. **[doc]**

**WLM Plus** — ITU-R BS.1770 / EBU R128 loudness: K-weighted (a shelving pre-filter approximating
head and ear response) mean square, gated at −10 LU relative, plus true-peak. **[doc]** This is a
spec you implement exactly, not creatively.

**Waves Stream** — previews how a master survives streaming loudness normalisation. **[inf]**

**The gap here is large and I'd take it.** See `IDEAS.md` §6.

---

## Restoration, and its inverse

**X-Noise · Z-Noise · WNS · NS1 · X-Click · X-Crackle · X-Hum · X-FDBK · Feedback Hunter ·
Clarity Vx DeReverb**

Covered in `WAVES.md` §6 for the noise-reduction generations. The specific ones:

- **X-Click** — impulsive-noise detection: a click is a short, broadband, statistically anomalous
  event. Detect via prediction error (LPC: a click is where linear prediction fails badly), then
  interpolate across the gap. **[std]** Classic, well-documented, and still the right approach.
- **X-Hum** — comb-notch at 50/60 Hz and harmonics. Trivial and reliable.
- **X-FDBK / Feedback Hunter** — detect the feedback frequency (a rapidly-growing narrow peak) and
  place a notch automatically. Live-sound staple. **[std]**
- **DeReverb** — genuinely hard. Blind deconvolution, or a neural model trained on
  reverberant/dry pairs. **[inf]** The neural route is the only one that works well, which makes
  it a dataset problem.

**Abbey Road Vinyl and Retro Fi are the inverse** — they *add* the artefacts: surface noise,
crackle, wow, RIAA curve, tracking distortion, cartridge resonance. Worth noting that the
restoration and degradation models are the same physics pointed in opposite directions, so one
codebase can serve both.

---

## Multiband and adaptive dynamics

**C1 · C4 · C6 · LinMB · F6 · MultiMod Rack · MaxxVolume · MV2 · IDX Intelligent Dynamics ·
Scheps Parallel Particles · IMPusher · Vitamin · Saphira**

The evolution is legible: **C1** (single band, parametric) → **C4** (4-band) → **C6**
(6-band + floating bands) → **F6** (dynamic EQ, i.e. the same engine presented as EQ) →
**LinMB** (linear-phase crossovers for mastering). Confirms the point from `FILTERS-AND-EQ.md`:
**multiband dynamics and dynamic EQ are one machine with two UIs.**

**Scheps Parallel Particles is the one to actually study.** Four knobs — Sub, Thick, Air, Bite —
each a *parallel* processed path blended in, not a serial insert. **[doc]** Parallel is why it
sounds additive rather than destructive: the dry signal is always intact underneath, so you cannot
make it worse, only more. That is a genuinely excellent UX principle and it applies to nearly
everything: **offer character as a parallel blend, not a serial transform.**

**Saphira** — harmonic exciter where you choose *which* harmonics to generate and their balance.
More controllable than a saturator because it's additive synthesis of harmonics rather than
waveshaping. **[inf]**

**Vitamin** — multiband harmonic enhancement + per-band width. Combines exciter and stereo tool.

---

## Delay, reverb, modulation

**H-Delay · H-Reverb · H-EQ · H-Comp · SuperTap · TrueVerb · RVerb · IR-1 / IR-L / IRLive ·
MagmaSprings · Abbey Road Chambers · ARPlates · CLA EchoSphere · Space Rider · Doppler ·
MetaFilter · MetaFlanger · MondoMod · Enigma · Kaleidoscopes · SoundShifter · Lofi Space`

- **H-Reverb** is a hybrid: FDN tail plus convolution-style early reflections, with a settable
  reverb *envelope* (you can make the tail swell rather than decay). **[doc]** The envelope idea is
  unusual and worth stealing — a decay that isn't monotonic is a genuinely different sound.
- **TrueVerb** separates early reflections from the tail with a **distance** control that trades
  their ratio *and* their timing together. **[doc]** That coupling is the right idea and it's the
  seed of `IDEAS.md` §4.
- **SuperTap** — 6 independent taps with per-tap pan, filter, level. Multitap is under-used
  because the UI is hard, not because the DSP is.
- **Enigma** — modulated notch/comb network. Genuinely strange, hard to describe, beloved.
  Evidence that **weird sells** when it's controllable.
- **MondoMod** — AM + FM + rotation in one, all tempo-syncable. The combination is the product.
- **SoundShifter** — independent time and pitch, including tempo-mapped. Phase vocoder + DTW.
- **Doppler** — real distance physics: delay, pitch, filtering and level all driven by one
  trajectory. Under-explored; see `IDEAS.md` §4.

---

## Console, tape, and artist chains

**SSL (E/G/EV2/Comp/EQ) · API (550/560/2500) · Neve-lineage (V-Comp, VEQ3, VEQ4, W43, Scheps 73) ·
REDD17 / REDD37-51 · TG12345 · RS124 · RS56 · PuigTec · PuigChild · dbx-160 · DPR-402 · CLA-2A /
3A / 76 · KramerHLS / PIE / Tape · J37 · NLS · BB Tubes · Lil Tube · Abbey Road Saturator ·
Magma · MDMX · Berzerk · GTR · Voltage Amps · PRS Supermodels**

All covered by the mechanisms in `SATURATION.md` and `DYNAMICS.md`. Two specifics:

- **PuigTec (Pultec EQP-1A)** — the low-end trick: boost and cut at the *same* frequency don't
  cancel, because the curves have different shapes and Q. You get a boost below plus a dip just
  above. **[std]** Model this precisely; its value is that it's counterintuitive.
- **RS124** — Abbey Road's modified Altec compressor, with a genuinely unusual two-stage release
  and a "hold" behaviour. **[doc]** Good test case for the program-dependent ballistics in
  `DYNAMICS.md`.

**The artist chains** — CLA, JJP, Maserati, Eddie Kramer, Greg Wells, Butch Vig, Manny M,
Scheps, OneKnob — are curated fixed chains behind 1–5 macros. **The product is taste, and it needs
no reverse engineering at all.** It needs a good engineer's ear and a measurement of what each
macro position does. Measure one at 10 knob positions and you have its entire behaviour.

**This is the most commercially proven format in the entire catalog**, and the cheapest for us to
enter once the underlying processors exist.

---

## Instruments, ML, and infrastructure

**Element2 · CODEX · Clavinet · Electric88 / 200 / Grand 80 · GrandRhapsody · Bass Fingers /
Slapper · CR8 Sampler · Waves Gemstones · COSMOS · Curves AQ / Equator / Resolve · StudioVerse ·
InTrigger · Q-Clone · InPhase · KingsMic · Smack Attack · TransX · Center · UM · GEQ ·
SignalGenerator · RenAxx · AudioTrack · Element / RChannel / Scheps Omni Channel`

- **CODEX** — wavetable + granular with a spectral engine. **[inf]**
- **COSMOS** — ML sample browser: analyses your entire library, tags by timbre, searches by
  similarity. **The product is the embedding + the index**, not audio DSP. Worth noting as a
  category: *audio ML that isn't a processor.*
- **Curves Equator** — ML-assisted EQ matching and auto-EQ. **[inf]**
- **StudioVerse** — shareable AI-assembled chains. A marketplace, not a plugin.
- **Q-Clone** — capture a hardware EQ's response and clone it. **This is our harness sold as a
  product.** Direct proof the measurement method is commercially normal.
- **InPhase** — cross-correlation phase alignment between mics. Unglamorous, hugely useful, easy.
- **Center** — extracts and rebalances the centre against the sides. M/S with independent
  processing per component.
- **KingsMic** — microphone modeling: measure the difference between two mics' responses, apply it
  as a filter. Same measurement logic again.

---

## What the sweep tells us about Waves as a company

Three patterns, and all three are strategically useful:

1. **They monetise perception, not circuits.** MaxxBass, IDR, PAZ, Nx, the riders, PS22 — the
   durable products exploit hearing. The circuit emulations are commodity and they ship dozens of
   them because the market wants them, not because they're differentiated.
2. **They productise workflows, repeatedly.** Brauer Motion is one engineer's panning technique.
   Scheps Parallel Particles is one engineer's parallel chain. The artist series is taste, sold.
   **A technique with a name and a face sells better than a better algorithm.**
3. **They ship measurement as product.** Q-Clone, KingsMic, TRACT, InPhase, PAZ. Measure something
   real, then sell the measurement. This is the cheapest defensible category available to us,
   because it needs rigour rather than novelty.

See [`../IDEAS.md`](../IDEAS.md) for what I'd build out of all this.
