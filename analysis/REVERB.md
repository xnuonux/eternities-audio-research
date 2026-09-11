# Reverb

**Your references:** ValhallaVintageVerb · ValhallaRoom · ValhallaFutureVerb · UAD EMT 140 ·
UAD EMT 250 · UAD Pure Plate · FabFilter Pro-R 2

**Start here:** Sean Costello (Valhalla) has written publicly and in detail about reverb
algorithms for years, on the Valhalla blog and in forum posts. He is unusually generous about
method. **Reading what he has already published will get you further than any disassembly**, and
it is the reason this category is more approachable than it looks.

---

## The two families

### Convolution
Record an impulse response, convolve. Perfectly faithful to *one* space in *one* configuration,
and fundamentally static — you cannot change the room size, you cannot modulate it, and it costs
a partitioned FFT. Not what any of your references are.

### Algorithmic
Build a recirculating network that *behaves* like a room. Cheap, parametric, modulatable, and
what all seven of your references are. Everything below is this.

---

## Feedback Delay Networks — the modern backbone

An FDN is: `N` delay lines, each fed by a mix of all the outputs through an `N×N` **feedback
matrix**, with damping per line.

```
       ┌──────── A (N×N mixing matrix) ────────┐
       │                                        │
in ──► [delay₁, delay₂, … delayₙ] ──► damping ──┴──► out
```

The matrix is the whole trick. It must be **lossless** (unitary/orthogonal) so that energy is
redistributed between delay lines without being created or destroyed — then decay is controlled
*only* by the damping filters, independently of the diffusion. If the matrix isn't lossless,
changing diffusion changes decay time and the reverb becomes untunable.

Standard choices **[std]**:

- **Householder reflection** — `A = I − (2/N)·1·1ᵀ`. Implementable as a sum plus a subtract per
  line: **O(N)** instead of O(N²). This is why it's everywhere.
- **Hadamard** — maximal mixing, also O(N log N) via a fast transform. Very diffuse.
- **Block-circulant / permutation-plus-rotation** — cheaper, more controllable character.

**Delay lengths must be mutually prime** (or at least share no small common factors), or modes
pile up on top of each other and you get ringing at specific pitches instead of a smooth tail.
Pick primes, and space them to spread the modal density evenly.

### Damping = frequency-dependent decay

Real rooms absorb treble faster than bass. Put a one-pole lowpass in each delay line's feedback
path and you get an RT60 that falls with frequency, which is most of "this sounds like a real
space" versus "this sounds like a machine." A shelving filter per line gives independent
low/mid/high decay — which is exactly the `Bass Mult` / `Decay` / `High Freq Damping` control set
you see on the Valhalla plugins. **[inf]**

---

## The thing that separates good from bad: modulation

A static FDN has fixed resonant modes. Sustained material excites them and you hear **metallic
ringing** — a specific pitched character that screams "algorithm."

**The fix is to modulate the delay lengths slowly and slightly**, so no mode can sustain. This is
the most important single technique in algorithmic reverb and it is the one most often
under-implemented.

Getting it right:

- **Fractional delay interpolation.** Modulating a delay length means reading between samples.
  Linear interpolation is a lowpass that varies with fractional position — it adds its own
  wobbling HF loss and distortion. Use **allpass interpolation** (Thiran) or higher-order
  Lagrange/spline. **[std]**
- **Decorrelate the modulators.** All lines on one LFO gives you audible pitch wobble on the
  whole tail. Use independent LFOs at different rates, or low-passed noise.
- **Amounts are tiny.** Fractions of a millisecond of deviation. Too much and sustained tones
  (piano, strings, pads) audibly detune in the tail — the classic "chorusy reverb" failure.

**[doc/inf]** VintageVerb's "mode" selector explicitly evokes different eras of digital reverb
hardware (1970s/1980s). The audible differences between those eras are largely: bandwidth limits,
converter bit depth and resulting noise floor, modulation depth and style, and the specific
diffusion topology. Those are all parameters, not different products.

---

## Plates — EMT 140, Pure Plate

A plate is a steel sheet under tension, driven at one point and picked up at others. Its physics
is a **2D wave equation**, and its modes are *much* denser and more uniformly spread than a
room's — which is why plates sound smooth and immediate with no discernible early reflections.

Two ways to model **[std]**:

1. **Modal synthesis** — solve for the plate's eigenmodes, run a bank of resonators. Physically
   exact, expensive, scales with mode count.
2. **Waveguide mesh / FDN tuned to plate statistics** — use an FDN but choose delay lengths and
   damping to match a plate's modal density and frequency-dependent decay. Cheaper, and
   overwhelmingly what's done in practice.

Plate character to capture: **no meaningful pre-delay or early reflections** (the wave reaches the
pickups almost immediately), very dense onset, bright and long decay, and a distinctive HF
"shimmer" from dense high modes. The EMT 140's damper plate changes decay by physically absorbing
— modelled as a global damping control.

---

## Rooms — ValhallaRoom, EMT 250

A room needs the part a plate doesn't have: **early reflections**. Structure:

```
in ──► pre-delay ──► early reflection tap bank ──┬──► out
                                                 │
                     └──► diffusion ──► FDN tail ─┘
```

- **Pre-delay** — time to the first reflection. Directly encodes apparent room size and is the
  single most perceptually powerful control.
- **Early reflections** — a sparse tap bank, tuned by geometry. Their *pattern* is what tells the
  ear "small tiled bathroom" vs "concert hall." This is where a room reverb's identity lives.
- **Diffusion** — usually a cascade of **allpass** filters, which smear in time without changing
  magnitude response. Schroeder's original insight and still correct.
- **Tail** — the FDN.

Get the early reflection pattern right and a mediocre tail still sounds like a room. Get the
tail perfect with no early reflections and it sounds like a plate.

---

## Pro-R 2 **[inf]**

FabFilter's angle is control-surface rather than algorithm: a "Space" control that morphs a
curated set, decay-rate EQ rather than a simple damping knob, and a "Distance" control mixing
early/late balance. **[inf]** Plausibly an FDN with a well-designed early-reflection bank and a
multiband decay curve. Again: the product is the parameterisation, which is a legitimate place to
compete.

---

## Build order for our reverb

1. **Schroeder baseline** — 4 comb filters + 2 allpasses. An hour's work, and it gives you a
   reference to hear how far the rest takes you. It will sound metallic, which is the point.
2. **8-line FDN with a Householder matrix, mutually prime delays, one-pole damping per line.**
   Verify energy conservation: set damping to unity and confirm the tail neither decays nor grows.
   **That test catches a wrong matrix immediately** and is the most valuable early check.
3. **Add slow decorrelated modulation with allpass interpolation.** Compare against step 2 on a
   sustained piano chord. The metallic ring should vanish. This is the moment it starts sounding
   professional.
4. **Shelving damping** for independent low/mid/high decay.
5. **Early reflection tap bank + pre-delay + allpass diffusion.** Now it's a room.
6. **Measure the references.** Impulse response per plugin per preset → RT60 per octave band,
   modal density, early/late energy ratio, the modulation's spectral signature. An IR plus its
   octave-band decay curves is a nearly complete behavioural spec for a reverb, and it's the
   easiest measurement in this whole repo to take.

Step 2's energy-conservation test and step 3's sustained-chord test are the two that matter. Most
bad algorithmic reverb fails one of them.
