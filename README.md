# eternities-audio-research

**How the reference plugins actually work, what they measurably do, and the order to build ours in.**

Private. For Astra and whoever else works this lane.

---

## What this is

You own a deep reference shelf. The question worth answering is *why the good ones sound good*,
and that question has real answers — most of them published, none of them requiring anyone to
open a binary.

What's here:

| | |
|---|---|
| [**`analysis/ANTIALIASING.md`**](analysis/ANTIALIASING.md) | **read this first.** the single technique that separates professional from amateur DSP |
| [`analysis/SATURATION.md`](analysis/SATURATION.md) | iron, tape, tubes — True Iron, Decapitator, Radiator, Oxide Tape, KClip3, Saturn 2 |
| [`analysis/FILTERS-AND-EQ.md`](analysis/FILTERS-AND-EQ.md) | Pro-Q 4, Volcano, FilterFreak, and the genuinely hard part: Diva's nonlinear ZDF filters |
| [`analysis/DYNAMICS.md`](analysis/DYNAMICS.md) | Pro-C 3, Pro-L 2, Pro-MB, LA-2A, True Dynamics, God Particle |
| [`analysis/REVERB.md`](analysis/REVERB.md) | Valhalla trio, EMT 140/250, Pure Plate, Pro-R 2 |
| [**`analysis/WAVES.md`**](analysis/WAVES.md) | the six headline Waves technologies — **their patents are psychoacoustic, not circuit-modeling** |
| [`analysis/WAVES-SWEEP.md`](analysis/WAVES-SWEEP.md) | the rest of the 258, by category, with the transferable idea per group |
| [**`analysis/RESONANCE-AND-AUTO-EQ.md`**](analysis/RESONANCE-AND-AUTO-EQ.md) | soothe2, Gullfoss, smart:EQ — **the most valuable modern category, and the least understood** |
| [`analysis/VOCALS.md`](analysis/VOCALS.md) | the vocal chain — Melodyne DNA, Auto-Tune, Throat, alignment, the neural generation |
| [`analysis/THE-EXPENSIVE-ONES.md`](analysis/THE-EXPENSIVE-ONES.md) | Acustica Volterra, Weiss, Kirchhoff, Massive Passive, Shadow Hills, Kotelnikov — what's technical vs reputational |
| [**`IDEAS.md`**](IDEAS.md) | **plugin concepts 1-8**, with mechanisms and measured acceptance criteria |
| [**`IDEAS-2.md`**](IDEAS-2.md) | **concepts 9-18** — harder into the psychoacoustic exploits, plus the infrastructure |
| [`harness/`](harness/) | a validated measurement rig that turns plugins you own into behavioural specs |
| [`BUILD-ORDER.md`](BUILD-ORDER.md) | what to build, in what sequence, with acceptance criteria |

Claims are marked **[doc]** (vendor-documented or published), **[std]** (standard in the
literature), or **[inf]** (my inference from behaviour). Don't treat an `[inf]` as established.

---

## The method, and why it's the strong one

**Measure the target, then build your own DSP to match the measurement.**

That's not a compromise position. It's how competitive audio DSP is actually built, and it beats
reading source for three reasons:

1. **A harmonic profile across seven drive levels is a more useful target than an algorithm.** It
   tells you what to hit. Source tells you how someone else hit it, in their architecture, with
   their constraints.
2. **It stays clean.** Nothing in this repo can come back at the product later. That matters the
   day Eternities ships something good enough to be worth attacking.
3. **The techniques are published anyway.** Zavalishin wrote the book on VA filters. Chowdhury
   published the tape hysteresis papers with the source. Costello has been explaining reverb
   algorithms for a decade. Bristow-Johnson, Orfanidis and Vicanek cover EQ completely. The gap
   between you and these plugins is craft and measurement, not secret knowledge.

The one thing measurement can't give you is *taste* — which presets, which defaults, which
curve at which knob position. That's the actual moat, and it's Dom's.

---

## Your shelf, inventoried

Read off the installed plugins on this machine:

**FabFilter (14)** — Pro-Q 4, Pro-C 3, Pro-R 2, Pro-L 2, Pro-MB, Pro-G, Pro-DS, Saturn 2,
Timeless 3, Volcano 3, Twin 3, Simplon, Micro, One
**Soundtoys (18)** — Decapitator, EchoBoy, Crystallizer, MicroShift, Radiator, PhaseMistress,
FilterFreak 1/2, PrimalTap, DevilLoc (+Deluxe), LittleAlterBoy, PanMan, Tremolator, and the
Little series
**Valhalla (3)** — VintageVerb, Room, FutureVerb
**u-he** — Diva, Zebra3
**Kazrog** — True Iron, True Dynamics, KClip3
**UAD native** — EMT 140, EMT 250, Pure Plate, Oxide Tape, Teletronix LA-2A, Century Channel Strip
**Avalon** — AD2055, AD2077, VT-747SP
**Instruments** — Arturia Pigments + Analog Lab V, Spectrasonics Omnisphere, Roland Cloud SRX
(10 titles), XLN Audio
**Waves (258 titles, V17)** — effectively the full Mercury catalog. See [`analysis/WAVES.md`](analysis/WAVES.md).
**Other** — Antares, Cradle The God Particle, Retro Sta-Level, MHB Green/Red

That is an unusually good measurement set. Between Diva and Zebra3 you have two different
u-he architectures; between the three Valhallas you have plate, room and modern; between
Decapitator, True Iron, Radiator and Oxide you have four distinct saturation physics.

---

## The open-source corpus worth reading

Production-grade DSP you can legitimately study line by line:

**Saturation / tape** — **CHOW Tape Model** (Jatin Chowdhury): Jiles-Atherton hysteresis, with
the papers. The single highest-value repo for this collection. · **Airwindows** (Chris Johnson):
~400 MIT-licensed plugins, each with a written rationale.

**Synths / filters** — **Surge XT**: production synth, large filter collection. · **Vital**:
modern wavetable architecture. · **OB-Xd**: Oberheim OB-X, the lineage Diva's Multimode draws on.
· **Dexed**: DX7 FM.

**Reverb** — **CloudSeed** (MIT): readable algorithmic reverb. · **Dragonfly** / **Aether**:
Freeverb3 lineage.

**Frameworks** — JUCE, iPlug2, DPF; CLAP for the modern plugin format.

**Papers and books** — Zavalishin, *The Art of VA Filter Design* (free PDF; he is NI's DSP lead)
· Parker/Zavalishin/Le Bivic, *Antiderivative Antialiasing*, DAFx-16 · Bristow-Johnson's EQ
cookbook · Orfanidis and Vicanek on matched-magnitude biquads · Kurt Werner's thesis on Wave
Digital Filters · ITU-R BS.1770-4 for true-peak.

---

## Start here

1. Read `analysis/ANTIALIASING.md`. It reframes everything else.
2. `pip install pedalboard numpy scipy matplotlib`, then run the harness against True Iron and
   Decapitator with `--tests alias,harmonics`. Compare their `even_over_odd_db`. You will see the
   difference between a transformer and a tube as a single number.
3. Read `BUILD-ORDER.md` and build milestone 1.
4. Read `IDEAS.md` and `IDEAS-2.md`. If you want something shippable this week rather than this
   quarter, start at idea 6 (DOUBLE) — two days, and it beats products people pay for.

**The one structural thing to notice:** a validated psychoacoustic masking model is load-bearing
across five of the eighteen ideas (§2 MARGIN, §5 LEGIBLE, §9 SHADOW, §11 FREE AIR, §17 CROWD).
Build it once against published masking data and five products fall out. It is the
highest-leverage single piece of engineering on either list.
