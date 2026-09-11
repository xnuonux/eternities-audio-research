# Plugin ideas

Derived from the gaps in `analysis/`. Each has a mechanism, an honest note on existing
competition, a cost estimate, and a **measured** acceptance criterion — so Astra can start
building rather than start interpreting.

Ordered by how strong I think they are.

The pattern I'm following, taken from the Waves sweep: **monetise perception, productise a
technique, or sell a measurement.** All three are more defensible than another circuit emulation.

---

## 1. SPLIT — harmonic/percussive separation as a platform

**The strongest idea here, because it's one engine that becomes five products.**

### The mechanism

**Harmonic-Percussive Source Separation** by median filtering (Fitzgerald, DAFx-2010). Take the
magnitude spectrogram `S`. Then:

- **Median-filter each row horizontally** (across time, within one frequency bin) → harmonic
  estimate `H`. A sustained tone is a horizontal ridge, so it survives; a transient is a brief
  spike in that row and gets removed.
- **Median-filter each column vertically** (across frequency, within one frame) → percussive
  estimate `P`. A transient is a vertical ridge across all frequencies, so it survives; a tone is
  a narrow peak in that column and gets removed.
- Build soft masks — `M_h = H^p / (H^p + P^p)` — and resynthesise both streams with the original
  phase.

That's it. Two median filters and a mask. **It is astonishingly cheap for how well it works**, it
needs no training data, and it is fully published.

### Why this is a platform, not a plugin

One separation engine, with a transient/tonal balance fader, gives you:

- **A transient shaper that is actually clean.** Every existing one (Smack Attack, TransX,
  Transient Designer) uses envelope differences — fast envelope minus slow envelope — which
  cannot distinguish a drum hit from the attack of a sustained note. HPSS can. **This alone is a
  better product than the incumbents.**
- **A de-esser with a real detector.** Sibilance is noise-like and lands in `P`; vowels are
  harmonic and land in `H`. Detecting sibilance as "percussive energy above 4 kHz" is far more
  specific than a bandpass, and it stops the plugin from ducking on a bright sustained vowel.
- **De-pick / de-click for guitar and piano** — attenuate `P` only in a band.
- **Tonal-only reverb send.** Send `H` to the reverb, keep `P` dry. Instantly cleans up a mix in
  a way no send-EQ achieves, because you are removing the transients from the tail rather than
  filtering them.
- **Drum-bus separation** — process the stick and the shell independently.

### Competition, honestly — CORRECTED 2026-09-11

**This section originally claimed nobody ships this. That was wrong and it is the kind of error
that wastes a build.**

**Eventide SplitEQ** (2021) ships exactly this idea: their "Structural Split" separates transient
from tonal and gives you independent gain per component across 8 bands. **oeksound Spiff** does
the transient-side case as a dynamic processor. iZotope RX has spectral layers offline.

So the *concept* is taken. What is still open:

- **SplitEQ is an EQ.** The split drives per-band gain. It is not exposed as a raw two-stream
  separation you can route, send, and process independently — which is where the reverb-send, the
  de-esser and the drum-bus uses come from.
- **Spiff is transient-only** and is a suppressor, not a rebalancer.
- **Nobody ships the split as a platform** with the five downstream products sharing one engine.

That reframes this from "new idea" to "known idea, unexploited surface." Still worth building —
the platform framing is the differentiator, not the separation — but **go and demo SplitEQ before
committing weeks**, and treat its transient/tonal quality as the bar to beat rather than a
greenfield.

*(Left as a visible correction rather than a silent edit. The competition claim was made from
memory and not checked, which is exactly the failure this repo's `[inf]` marking exists to
prevent.)*

### Cost and acceptance

**Two to three weeks.** STFT, two median filters, masks, inverse STFT.

**Accept when:**
- on a drum loop, the `P`-only output has no audible pitched content and the `H`-only output has
  no audible stick
- reconstruction is near-perfect: `H + P` sums back to the input within **−60 dB** of error with
  the balance at neutral. **This is the critical test** — if the sum isn't transparent, every
  downstream use inherits the error.
- latency is one STFT window and is reported honestly to the host
- median filter lengths are exposed; the harmonic/percussive tradeoff lives entirely there

**Measure first:** run Smack Attack's `envelope` test on a drum loop *and* on a sustained bright
vocal. Its detector will fire on the vocal. Ours shouldn't. That contrast is the demo.

---

## 2. MARGIN — a rider that understands masking

### The problem with every existing rider

Vocal Rider holds a vocal at a constant **level** relative to the music. But intelligibility isn't
about level, it's about **masking** — whether the mix's energy is sitting in the same critical
bands as the vocal's. A dense guitar at −20 dB can bury a vocal that a bass at −10 dB doesn't
touch.

So a level-based rider raises the vocal when it doesn't need to, and fails to raise it when it
does.

### The mechanism

Compute the actual **masking threshold** the mix imposes on the vocal, and ride gain to hold a
constant margin above it.

1. Both signals → **ERB/Bark critical-band** power (≈24–40 bands).
2. Apply a **spreading function** to the mix's band powers — masking leaks upward in frequency
   much more than downward, roughly +25 dB/Bark below and −10 dB/Bark above the masker.
   This is standard psychoacoustic-model machinery, the same as sits inside every perceptual
   codec. **[std]**
3. That gives a masking threshold per band. Compare the vocal's band powers against it → a
   **per-band margin in dB**.
4. Take a weighted margin across the bands that matter for speech intelligibility (roughly
   500 Hz–4 kHz, weighted by the Speech Intelligibility Index band importance functions).
5. Ride broadband gain, slowly, to hold that weighted margin at a target. Pause detection as per
   Vocal Rider.

### Why this is genuinely better

It responds to *why* the vocal is disappearing rather than to *that* it is. A dense synth stab
raises the gain; a kick drum doesn't. And the same computation gives you a **readout** — "your
vocal is 3 dB under the mask in the 2 kHz band" — which is diagnostic information no rider offers.

Extension, and this is where it gets good: the same masking map can drive a **carve** instead of
a ride — duck the *mix* in only the bands where it's masking, by only as much as needed. That's
the rigorous version of what Trackspacer and Neutron's Unmask do heuristically.

### Competition

Trackspacer, Neutron Unmask, Soothe2 all do adjacent things heuristically. **None of them
implement a real spreading-function masking model with SII weighting**, and none give you the
margin as a number. Rigour is the differentiator.

### Cost and acceptance

**Three to four weeks**, most of it in the masking model and the tuning.

**Accept when:**
- the masking model is validated against published tone-on-tone masking data: a 1 kHz masker at
  a known level should produce a threshold curve matching the textbook figures within a few dB
- with a fixed vocal, swapping the mix from "kick-heavy" to "guitar-heavy" at identical LUFS
  produces *materially different* gain rides. If it doesn't, the model isn't working and you've
  built an expensive level rider.
- control rate throughout — this must be nearly free, per `ANTIALIASING.md` §4

---

## 3. PARALLAX — distance as one physically coherent control

### The problem

Making something sound *far away* currently takes four plugins and guesswork: turn it down, roll
off the top, add reverb, maybe pre-delay. Those are four independent controls for one physical
variable, and the combinations that are physically consistent are a thin subset of the ones you
can dial.

### The mechanism

One distance control, correctly coupling everything distance actually does:

| physical effect | law |
|---|---|
| **level** | inverse square, −6 dB per doubling |
| **air absorption** | frequency- and humidity-dependent HF loss, **ISO 9613-1** gives the coefficients **[std]** |
| **propagation delay** | `d / 343 m·s⁻¹` |
| **direct-to-diffuse ratio** | direct falls as 1/r while the diffuse field is roughly uniform, so the wet/dry ratio changes with distance *on its own* |
| **early reflection timing** | first reflection arrival shifts with source position, not just room size |
| **Doppler** | if distance is *changing*, pitch shifts by the rate of change |

Couple them to one parameter and add a trajectory editor so a source can move. Now a plane
flying overhead is one automation lane instead of five, and it's physically right.

### Why nobody has this

Doppler plugins exist (Waves Doppler). Distance-as-a-single-parameter, physically coupled, with
ISO 9613 air absorption, doesn't ship anywhere I know of. It is genuinely straightforward
engineering and the reason it's missing is that it's unglamorous, not that it's hard.

### Cost and acceptance

**Two weeks** for the static version, **three** with trajectories and Doppler.

**Accept when:**
- measured HF loss at a given distance matches the ISO 9613 tables within 1 dB
- a moving source's pitch shift equals the Doppler prediction from its radial velocity
- the direct/diffuse ratio changes with distance **without the user touching a wet/dry control** —
  that's the whole point
- a fractional delay sweep introduces no measurable aliasing (allpass or Lagrange interpolation,
  per `REVERB.md`)

---

## 4. FOUNDATION — psychoacoustic bass that knows the target system

### The mechanism

MaxxBass's missing-fundamental trick (see `WAVES.md` §1) with the thing MaxxBass doesn't have: **a
measured target-system profile.**

The optimal harmonic distribution depends entirely on what the audio is coming out of. A phone
speaker rolls off around 500 Hz; earbuds around 100 Hz; a laptop around 300 Hz with a resonance
bump; a car has a 60 Hz cabin mode. **The harmonic series you should synthesise is different for
each**, and it is solvable rather than guessable: given the target's measured response, choose the
harmonic set and levels that maximise perceived fundamental strength through *that* response.

Ship with measured profiles (phone, laptop, earbud, car, club, full-range) and a "solve for this
response" mode that takes an imported measurement.

### Why it's better than the incumbent

MaxxBass gives you an intensity knob. This gives you a *destination*. And since most music is now
consumed on exactly the systems that can't reproduce bass, the destination is the useful control.

### Cost and acceptance

**Two weeks** for the generator, plus profile measurement time.

**Accept when:**
- harmonic generation tracks the source envelope — mute the bass and the harmonics stop
  (this is what separates it from a static buzz)
- **the listening test that matters:** on a phone speaker, A/B against the unprocessed source.
  Perceived bass must increase *while* measured energy below the speaker's cutoff decreases.
  Those moving in opposite directions is the proof the psychoacoustics is doing the work.
- the harmonic generator is not a broadband saturator — feed it a bass note plus a hi-hat and only
  the bass should generate harmonics

---

## 5. LEGIBLE — an intelligibility and translation meter

**Sell a measurement.** Cheapest defensible category in the catalog, per the sweep.

### What it shows

- **Intelligibility** — an **STOI**-class (Short-Time Objective Intelligibility) score for the
  vocal against the mix. A published, validated metric that correlates with human intelligibility
  scores. Nobody ships it for music.
- **The masking map** from §2 as a visual: which bands are burying the vocal, right now.
- **Translation panel** — the mix re-rendered through the target-system profiles from §4. Not a
  simulation of a speaker's *sound*, a measurement of what survives it: how much of your bass
  actually reaches a phone listener, as a number.
- **Mono-compatibility** — per-ERB-band correlation, so you see exactly which bands collapse, not
  just a single correlation meter.
- **True peak, LUFS, LRA** per BS.1770-4 — table stakes, implement to spec.

### Why this is strong

It's diagnostic rather than corrective, which means it never fights the user's taste. It's
defensible because it's rigour, not novelty. And it pairs with every other plugin on this list —
§2's masking model, §4's profiles.

### Cost and acceptance

**Three weeks.** Mostly correct implementations of published metrics plus visualisation.

**Accept when:** LUFS and true-peak agree with a reference implementation to within 0.1 dB on the
EBU test set. If the table-stakes numbers are wrong, nobody trusts the novel ones.

---

## 6. DOUBLE — the tape ADT nobody bothered to do properly

### The mechanism

Abbey Road's Automatic Double Tracking was a second tape machine running at slightly varying
speed. That's all. **A delay of 20–60 ms with independent slow pitch drift**, per side.

The reasons it beats digital doublers **[std]**:
- the drift is *continuous* and low-frequency, not an LFO on a fixed delay
- independent drift per channel gives width without a static delay offset, so it stays
  mono-compatible far better than a fixed Haas delay
- tape's own HF loss and saturation are part of the sound

### Why it's on this list

It is a two-day build that sounds better than products people pay for. Fractional delay with good
interpolation, two decorrelated low-frequency random walks, a gentle HF shelf, optional
saturation. **Highest value-per-hour on the entire list.**

### Accept when

Sum to mono and the level dip versus the dry signal is under 1 dB (a fixed-delay doubler fails
this badly). No measurable aliasing from the modulated delay.

---

## 7. SHUFFLE — Blumlein, finished

Frequency-dependent M/S width (see `WAVES.md` §4), but per **ERB band** rather than one shelf, with
a mono-compatibility readout per band so you can see what you're about to break.

Add **rotation** as distinct from panning — asymmetric balance that preserves the stereo field.

**One week.** Trivial DSP, disproportionate perceptual effect, and a 90-year-old idea that modern
plugins mostly don't implement.

**Accept when:** a width change at 100 Hz leaves the 5 kHz image measurably unchanged, and the
per-band correlation readout matches an independently computed correlation.

---

## 8. BAND-WISE REVERB MODULATION — a small, real improvement

From `REVERB.md`: modulation kills metallic ringing, but too much detunes sustained tones.

**Those two constraints live in different frequency regions.** Metallic ringing is a
high-frequency modal problem; audible detuning is a low-frequency pitch problem. So: **scale
modulation depth per critical band** — near zero below ~300 Hz, rising with frequency.

You get the ring suppression without the bass wobble. I have not seen a reverb expose this, and
it falls out of an FDN you're building anyway.

**Accept when:** a sustained low piano chord shows no measurable pitch modulation while a bright
sustained pad shows the metallic ring suppressed as much as a full-depth modulated build.

---

## What I'd actually sequence

**First:** §6 DOUBLE (two days, immediate win, proves the pipeline end to end) → §7 SHUFFLE (one
week) → §1 SPLIT (the platform).

**Then:** §5 LEGIBLE, because §2's masking model is half-built inside it and shipping the meter
first de-risks the rider.

**Then:** §2 MARGIN and §4 FOUNDATION, the two genuinely differentiated products.

**§3 PARALLAX** whenever there's appetite — it's self-contained and doesn't block anything.

Note that none of these is a compressor, an EQ, a tape emulation or a console. Those are
commodity, the market is saturated, and they're precisely where matching a measurement is hardest
and differentiation is lowest. Every idea above is either a perceptual exploit, a productised
technique, or a measurement — the three things the Waves catalog proves are durable.
