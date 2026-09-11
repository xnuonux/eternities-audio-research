# Saturation: iron, tape, and tubes

**Your references:** Kazrog True Iron · Soundtoys Decapitator · Soundtoys Radiator · Soundtoys
Little Radiator · UAD Oxide Tape · Kazrog KClip3 · FabFilter Saturn 2 · Avalon AD2055/AD2077 ·
Retro Sta-Level · MHB Green/Red

Confidence is marked per claim: **[doc]** vendor-documented or published · **[std]** standard
practice in the literature · **[inf]** my inference from behaviour and general design.

---

## The thing people get wrong

Saturation is not a waveshaper. A waveshaper is *memoryless*: output depends only on the current
input sample, so its distortion is a fixed function of level and completely independent of
frequency. Real analog saturation is **none of those things**:

- **Frequency-dependent.** A transformer saturates at low frequencies first, because core flux is
  proportional to the integral of voltage. Bass hits the core limit while treble sails through.
- **Hysteretic.** The core's magnetic state depends on where it has *been*, not just where it is.
  The transfer curve is a loop, not a line.
- **Asymmetric.** Real circuits clip the positive and negative halves differently, generating
  **even** harmonics. A symmetric `tanh` generates only odd harmonics, which is the "digital"
  sound people complain about.
- **Level-dependent in character, not just amount.** The *harmonic ratio* shifts with drive, it
  doesn't just scale.

Nail those four and you are most of the way to "analog."

---

## Transformer modeling — True Iron territory

True Iron models six transformers **[doc]** (its UI names them; the marketing references classic
iron — Neve-style, API-style, Edcor, etc.).

### What a transformer actually does to audio

1. **Core saturation (low frequency).** Flux `Φ ∝ ∫v dt`. Integration means a 40 Hz signal
   accumulates ~10× the flux of a 400 Hz signal at the same voltage. So bass saturates first and
   hardest. **This is the single most important characteristic and the one most often missed** —
   if your model saturates all frequencies equally, it will never sound like iron. **[std]**
2. **Hysteresis.** The B-H curve is a loop with memory. Energy is lost per cycle (the loop area),
   which reads as compression plus harmonic generation whose phase depends on history. **[std]**
3. **High-frequency loss.** Winding capacitance, leakage inductance and eddy currents roll off and
   phase-shift the top. Often a gentle shelf plus a resonant bump before the rolloff, from the
   leakage-inductance/capacitance tank. That bump is a lot of the "air" people hear. **[inf]**
4. **Frequency-dependent phase.** Because it's a real filter network, not a curve.

### How to model it, cheapest to most faithful

**Tier 1 — filtered waveshaper (get this working first).**
```
in → [pre-emphasis: boost LF]  → nonlinearity → [de-emphasis: inverse] → [HF loss shelf] → out
```
Boosting LF before a memoryless nonlinearity makes LF saturate first; the inverse filter after
restores the balance. You get frequency-dependent saturation out of a memoryless curve. Add
asymmetry by offsetting the input (`f(x + bias)` then remove the DC) for even harmonics. This is
cheap, it works, and it's the right first milestone. **[std]**

**Tier 2 — Jiles-Atherton hysteresis (the real thing).**
A physical model of magnetic domain behaviour, parameterised by saturation magnetisation `Mₛ`,
domain wall pinning `k`, interdomain coupling `α`, anhysteretic shape `a`, and reversibility `c`.
Solve the ODE per sample — RK4 or Newton-Raphson on the implicit form.

This is exactly what **CHOW Tape Model** implements, it is open source, and Jatin Chowdhury
published the papers. **That repo is the closest thing to "the secrets inside" that you are going
to legitimately get, and it's better than a disassembly because it comes with the derivation.**
**[doc]**

**Tier 3 — Wave Digital Filters.** Model the actual circuit topology — transformer, windings,
loading, the driving stage — as WDF elements and solve the network. Faithful, expensive, and the
right answer if you want one engine that covers many devices by changing component values rather
than re-tuning curves. Fettweis originally; Kurt Werner's thesis is the modern reference. **[std]**

---

## Tape — Oxide Tape territory

Tape is transformer physics plus a transport:

- **Hysteresis** in the magnetic coating — same Jiles-Atherton machinery. **[std]**
- **Bias.** High-frequency bias linearises the recording; too little means crossover distortion,
  too much means HF loss. **[std]**
- **Gap loss / head bump.** Playback head geometry gives a comb-like HF rolloff and a
  characteristic low-frequency resonance ("head bump") that is a big part of why tape flatters
  kick drums. **[std]**
- **Wow and flutter.** Slow (wow, <10 Hz) and fast (flutter) speed variation — a modulated
  fractional delay line. Needs proper interpolation or it adds its own aliasing.
- **Speed and EQ curve.** 15 vs 30 ips changes bump frequency and HF headroom; NAB vs CCIR
  changes the pre/de-emphasis.
- **Self-erasure / print-through** at high levels. Usually ignored, occasionally modelled.

---

## Tubes vs transistors vs diodes — Decapitator territory

Decapitator's five styles are explicitly labelled after their references **[doc]**: **A**
Ampex 350 tape preamp · **E** Chandler/EMI TG12345 · **N** Neve 1057 · **T** Thermionic Culture
Vulture (triode) · **P** the same Vulture in pentode mode.

What actually differs between them:

| device class | curve | harmonics | why |
|---|---|---|---|
| **Triode tube** | soft, strongly asymmetric | **even-dominant** (2nd, 4th) | single-ended topology clips halves unequally |
| **Pentode tube** | harder knee, more aggressive | odd + even, denser | different plate characteristic |
| **Transformer/iron** | soft, frequency-dependent | 3rd with LF emphasis | core flux integration |
| **Transistor (class A)** | moderate, fairly symmetric | odd-dominant | push-pull cancels even |
| **Diode clipper** | hard, sharp | dense odd | abrupt conduction threshold |
| **Digital clip** | absolute | very dense odd | discontinuous derivative |

**The practical lever: asymmetry controls the even/odd ratio, and the even/odd ratio is most of
what listeners call "warm" vs "harsh."** Even harmonics (octave, double-octave) are consonant;
odd harmonics above the 3rd read as edge. A `tanh` with a DC offset before it and a DC blocker
after gives you a continuous knob between "transistor" and "tube" for almost no cost. **[std]**

**Also:** real tube stages sag. Plate voltage drops under load, so gain reduces momentarily after
a transient. That is a level-dependent *time-varying* gain, not a curve — it's why tube gear
"breathes." Model it as a slow envelope pulling down the operating point. **[std]**

---

## Limiting and clipping — KClip3 territory

Clipping is distinct from limiting and the distinction matters:

- **Clipper** — instantaneous, no time constants. Hard clip is a discontinuity in the derivative
  and aliases violently, so this is where ADAA pays for itself most. Soft clip rounds the knee.
- **Limiter** — a gain-reduction *process* with lookahead and release. See `DYNAMICS.md`.

Modern loudness practice clips before limiting: the clipper takes the sharp transient peaks the
limiter would otherwise have to pump for. KClip3's oversampling selector exists because clipping
is the worst-case aliasing scenario. **[inf]**

---

## Build order for our saturator

1. **`tanh` with ADAA-1 and 2× oversampling.** Prove the fold test passes. This is the foundation
   and it must be clean before anything else goes on top.
2. **Bias + DC blocker** for an asymmetry control → even/odd ratio knob.
3. **Pre/de-emphasis pair** → frequency-dependent saturation. Now it can sound like iron.
4. **HF loss shelf + leakage resonance** → the top-end character.
5. **Measure True Iron** with the harness across its six models, at 5–6 drive levels. You now have
   six behavioural targets as harmonic-series tables.
6. **Fit steps 2–4 to those targets.** Not by copying anything — by adjusting your own parameters
   until your harmonic profile matches the measurement. This is clean-room and it is exactly how
   this is done properly.
7. **Only then** consider Jiles-Atherton, and start from CHOW Tape's published formulation.

The order matters: if you build hysteresis before you have clean antialiasing, you will spend
weeks tuning a model whose output is dominated by fold-back artefacts rather than by the physics
you wrote.
