# Waves: 258 titles, and the six ideas worth taking

You have essentially the full catalog. Most of it is circuit emulation already covered by
`SATURATION.md`, `DYNAMICS.md` and `FILTERS-AND-EQ.md`, or artist-signature chains whose product
is curation rather than DSP.

But Waves is genuinely different from the boutique developers in one respect, and it is the
reason they became the biggest plugin company in the world: **their core patents are
psychoacoustic, not circuit-modeling.** They built a business on exploiting how hearing works
rather than on modeling how hardware works.

That is the gold. It is also the most legitimately studiable material in your entire collection,
because psychoacoustics is an academic field with a century of published literature.

Marked **[doc]** documented/published · **[std]** standard in the literature · **[inf]** my
inference.

---

## 1. MaxxBass — the missing fundamental. Take this one first.

**Titles:** MaxxBass · RBass · LoAir · Submarine · Vitamin (partly)

This is Waves' founding technology and it is the highest-value idea in the catalog.

### The phenomenon

If you play harmonics at 2f, 3f, 4f, 5f **without the fundamental f at all**, a listener hears
pitch **f**. The auditory system reconstructs the missing fundamental from the harmonic spacing.
This is **residue pitch** (Schouten) or **virtual pitch** (Terhardt), and it is one of the most
robust results in psychoacoustics. **[std]**

It is why a telephone — which transmits nothing below ~300 Hz — can carry a male voice with an
85 Hz fundamental and still sound pitched correctly. Your brain fills it in.

### The exploit

A small speaker physically cannot reproduce 50 Hz. So: **don't try.** Detect the bass content,
synthesise its *harmonic series* in a range the speaker can actually reproduce, and let the
listener's auditory system reconstruct the bass that was never emitted.

```
in ──► LPF (cutoff = speaker's real limit)
          │
          ├──► harmonic generator (2f, 3f, 4f… of the detected bass)
          │         │
          │    envelope-follow the original bass so the harmonics track its dynamics
          │         │
          └──► [optionally remove or attenuate the true fundamental] ──┬──► out
                                                                        │
                        harmonics mixed back in ────────────────────────┘
```

The counterintuitive part: **removing the real bass and adding harmonics can make a small speaker
sound like it has more bass**, because the un-reproducible energy was only causing cone excursion
and distortion, while the harmonics actually deliver the percept.

### Building it

- **Harmonic generation** must track the original's envelope, or the implied bass won't move with
  the music and it'll sound like a static buzz. This is the difference between MaxxBass and a
  cheap "bass enhancer." **[inf]**
- **Which harmonics, and their relative levels, determine whether it reads as "bass" or as
  "buzz."** The 2nd and 3rd carry most of the pitch percept; higher ones add presence and, past a
  point, just grit.
- Use a **multiplier/rectifier or a tracked oscillator**, not a broadband saturator — a saturator
  generates harmonics of *everything*, not of the bass you detected.
- **LoAir and Submarine are the inverse:** generate a *sub*harmonic (octave down) for systems that
  genuinely can reproduce it. Different mechanism, opposite direction.

**This is buildable in a week and there is very little good open-source competition.** It is my
pick for the first shipped Eternities plugin that isn't a me-too.

---

## 2. IDR — dithering and noise shaping. The L1 legacy.

**Titles:** L1 · L2 · L3 (all variants) · L4 · UM · everything with a bit-depth control

L1's lasting contribution wasn't the limiter, it was **IDR (Increased Digital Resolution)** —
getting 16-bit output to sound like more than 16 bits. **[doc]**

### Why dither at all

Truncating 24-bit to 16-bit produces quantisation error **correlated with the signal**, which is
distortion, and it is worst at low levels — exactly where reverb tails and fades live. Adding a
tiny amount of noise before truncation **decorrelates** the error, converting distortion into
steady noise. The ear forgives noise far more readily than it forgives correlated distortion, and
dithered 16-bit audio can carry information below the LSB.

- **TPDF dither** (triangular probability density, 2 LSB peak-to-peak) is the correct default —
  it fully decorrelates and has no noise modulation. Rectangular PDF leaves noise modulation.
  **[std]**

### Noise shaping — the actual clever bit

Dither noise doesn't have to be flat. Use an **error-feedback filter** to push the quantisation
noise into frequency regions where the ear is least sensitive — above ~15 kHz, and out of the
2–5 kHz region where hearing is most acute.

```
        ┌──────── H(z) error feedback ────────┐
        │                                      │
x ──►(+)──► quantise ──┬──► y                  │
        ▲              │                       │
        └── shaped error ◄── (y − pre-quantise) ┘
```

Total noise *power* increases. Perceived noise drops, by a lot — 10–20 dB of effective
resolution gain is achievable. The filter is designed by weighting the noise spectrum against an
inverse equal-loudness curve and minimising perceived loudness. **[std]**

**Caution worth knowing:** aggressive noise shaping puts a lot of energy just below Nyquist. If
that gets resampled or lossy-encoded downstream, it can fold back or waste bit allocation. This
is why mastering practice is "shape only at the final stage, once."

---

## 3. NLS — console summing as a system, not a channel

**Titles:** NLS (Spike/EMI, Nevo/Neve, Mike/SSL)

Most "console" plugins are per-channel saturation. NLS's interesting claim is that a console is a
**system-level** effect **[inf]**:

- **Per-channel nonlinearity** — mild, and it accumulates across channels
- **Crosstalk between adjacent channels** — small amounts of neighbouring signal bleeding in,
  which is a real physical property of a shared-ground console with adjacent wiring
- **Noise floor per channel** — summing 48 channels sums 48 noise floors
- **Behaviour that changes with channel count** — the effect on a 48-channel mix is not the
  per-channel effect times 48

The architectural lesson generalises well beyond consoles: **an effect can be a property of the
graph, not of a node.** If we build a mixing environment rather than isolated plugins, this is the
kind of thing that is only available to us because we control the whole signal path.

---

## 4. S1 and PS22 — stereo geometry

### S1 Stereo Imager — the Blumlein shuffler **[std]**

M/S is well known: `M = (L+R)/2`, `S = (L−R)/2`, adjust width by scaling S, convert back.

The part people miss is the **shuffler**, Alan Blumlein's idea from the 1930s: apply
**frequency-dependent** width. Spaced-microphone stereo under-represents low-frequency width
relative to how we localise, so boosting S at low frequencies restores perceived spaciousness
without smearing the centre. That's a shelf on the S channel, and it is a remarkably large
perceptual effect for a trivial amount of DSP.

S1 also does rotation (asymmetric balance that preserves the stereo field) as distinct from
simple panning. Worth implementing both.

### PS22 — mono to stereo without comb filtering **[inf]**

The naive mono-widener delays one side. That comb-filters on fold-down to mono, which is fatal.

PS22's approach is **frequency-dependent panning**: split the spectrum into many bands and pan
alternating bands opposite. Mono sums back almost perfectly (you're only re-summing what you
split), but each ear gets a different spectral slice, which the auditory system reads as width.

Elegant, mono-safe, and directly buildable from a filter bank you already need.

---

## 5. The riders — level, not density

**Titles:** Vocal Rider · Bass Rider · MaxxVolume · PlaylistRider

**A rider is not a compressor**, and the distinction is the whole point. **[doc]**

A compressor reduces gain *within* a phrase — it changes density, texture and transient shape. A
rider moves a **fader**: slow, target-seeking gain that keeps the vocal sitting at a consistent
level against a sidechain reference, without touching the internal dynamics of any word.

Mechanism **[inf]**:
- long-window level estimate of the target vs a sidechain (the music)
- slow gain movement toward a target offset, with rate limits
- **pause detection** — hold the last gain through silences instead of riding noise up. This is
  the part that makes it usable, and it's where naive implementations fail audibly.

Nothing about this is expensive. It is a control-rate process, and per `ANTIALIASING.md` §4,
control-rate nonlinearity is free. High perceptual value, near-zero DSP cost — the best ratio in
the whole catalog.

---

## 6. Noise reduction, and where Waves went ML

**Titles:** X-Noise · Z-Noise · WNS · NS1 · Clarity Vx (+ Pro, DeReverb) · X-Hum · X-Click · X-Crackle

The generational progression is legible and worth understanding as a roadmap:

1. **Spectral subtraction** (X-Noise) — learn a noise profile, subtract its magnitude spectrum
   per frame, resynthesise. Artefact: "musical noise," isolated warbling bins. **[std]**
2. **Better estimators** (Z-Noise) — smarter noise tracking and gain smoothing across
   time/frequency to suppress musical noise; typically a Wiener-style or MMSE gain rule rather
   than naive subtraction. **[std]**
3. **Blind/adaptive** (NS1) — no learn step; estimate noise continuously from signal statistics.
4. **Neural** (Clarity Vx, DeReverb) — a trained model separating voice from everything else.
   This is a different engineering problem: dataset, training, inference cost, latency. **[inf]**

**For us:** stages 1–2 are classical and buildable now. Stage 4 is a data problem, not a DSP
problem, and it should be scoped as such if we ever take it on. Do not confuse them.

---

## Also genuinely worth a look

- **PuigTec (Pultec EQP-1A)** — the famous **low-end trick**: boost and cut at the *same*
  frequency simultaneously and they do not cancel, because the boost and cut curves have
  different shapes and Q. You get a boost below plus a dip just above, which is why engineers
  love it. Worth modeling precisely because its behaviour is counterintuitive and beloved. **[std]**
- **PuigChild (Fairchild 670)** — vari-mu: ratio *increases* with level because tube bias shifts.
  See `DYNAMICS.md` — feedback detector plus level-dependent ratio.
- **Q-Clone** — captures a hardware EQ's response through a loop and clones it as a filter. This
  is our harness, shipped as a product. Proof the method is legitimate and commercially normal.
- **Smack Attack / TransX** — transient shapers. Envelope-difference detection (fast envelope vs
  slow envelope) drives independent attack and sustain gain. Not compression; much more surgical,
  and cheap.
- **Doppler** — real Doppler: distance drives delay, pitch shift, air absorption and level
  together. Under-explored as a creative effect.
- **InPhase** — phase alignment via cross-correlation between mics. Unglamorous, enormously
  useful, easy to get right.
- **Abbey Road Chambers** — convolution of actual physical echo chambers, plus the speaker and
  mic in the chain. The lesson: a convolution product's value is the *quality of the captures*,
  not the convolution engine.
- **Torque** — drum pitch shifting via tracked resynthesis. Solves a real problem nobody else had
  named.

---

## What I'd actually build from this

Ranked by (perceptual value) ÷ (engineering cost):

1. **MaxxBass-class harmonic bass enhancer.** Highest ratio in the catalog. Real psychoacoustics,
   little good open-source competition, buildable in a week.
2. **A rider.** Control-rate, cheap, immediately useful, and almost nobody outside Waves ships one.
3. **Blumlein shuffler + rotation** in a stereo tool. Trivial DSP, large perceptual effect.
4. **TPDF dither with a good noise shaper.** Needed anyway on any output stage; do it properly
   once and it's done forever.
5. **Transient shaper.** Cheap, surgical, popular.
6. **PS22-style mono-to-stereo.** Falls out of a filter bank you'll already have.

Note what is *not* on that list: another console emulation, another 1176, another tape plugin.
The market is saturated with those and they are exactly where measurement-matching is hardest and
differentiation is lowest.

## Measure these

```
MaxxBass / RBass        harmonics  — see which harmonics it generates and at what ratio
L2 / L4                 curve + envelope — limiter reduction shape and true-peak behaviour
PuigTec                 response — with boost and cut BOTH up at the same frequency
S1                      response per channel — measure M and S paths separately for the shuffler shelf
NLS                     harmonics at 1, 8, 24 "channels" — does it really change with count
Smack Attack            envelope — attack/sustain gain vs input transient
Z-Noise / Clarity Vx    response on speech + known noise — artefact character, not just reduction
```

The NLS one is a genuine open question I'd want answered before copying the idea: **[inf]** I
believe the per-channel effect compounds with channel count, but that is inference from how it's
marketed and how a real console behaves, not something I've measured. Measure it before building
on it.
