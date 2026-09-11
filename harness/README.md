# The measurement harness

Renders test signals through plugins **you have licensed, on your own machine**, and
characterises the output. It does not inspect, decompile, or copy anything. The output is a
behavioural spec — the thing you actually need in order to implement from first principles.

```
pip install pedalboard numpy scipy matplotlib

python measure.py --list
python measure.py --plugin "C:/Program Files/Common Files/VST3/True Iron.vst3" \
                  --tests alias,harmonics,response --out ../measurements/true-iron
```

## Tests, and which references to point them at

| test | signal | what you get | point it at |
|---|---|---|---|
| `alias` | 7 kHz tone, 3 drive levels | inharmonic energy + measured fold bins | True Iron, Decapitator, KClip3, Saturn 2, Radiator |
| `harmonics` | 1 kHz at 7 input levels | H2–H10 vs level, THD, **even/odd ratio** | every saturator; this is the character fingerprint |
| `response` | exponential sweep, Farina deconvolution | magnitude + phase + saved IR | Pro-Q 4, Volcano, MHB, Avalon, the Diva filters |
| `curve` | 12 s level ramp −60→0 dB | static input/output transfer | Pro-C 3, LA-2A, True Dynamics, God Particle |
| `envelope` | quiet→loud→quiet burst | gain envelope at 1 ms resolution | any compressor; attack and release shape |
| `rt60` | impulse | octave-band RT60 + early/late split | Valhalla trio, EMT 140/250, Pure Plate, Pro-R 2 |

## The detector is validated, not assumed

The aliasing analysis was tested against three synthetic cases with known behaviour before being
trusted on anything real:

| case | inharmonic energy | verdict |
|---|---:|---|
| linear gain (cannot alias) | **−142.9 dB** | clean |
| naive pointwise hard clip @ 48 kHz | **−16.1 dB** | heavy aliasing |
| same clip at 16× oversampling | **−68.0 dB** | some aliasing |

16× oversampling buys **52 dB**. That single number is the best argument in this repo for taking
`ANTIALIASING.md` seriously.

And the fold predictions came out physically exact, which is the part that proves the instrument
rather than just exercising it. For 7 kHz at 48 kHz through a symmetric clipper:

```
H4 (28 kHz) -> folds to 20000 Hz   measured -228.6 dB   <- absent, correctly
H5 (35 kHz) -> folds to 13000 Hz   measured  -18.5 dB   <- present
H6 (42 kHz) -> folds to  6000 Hz   measured -217.9 dB   <- absent, correctly
H7 (49 kHz) -> folds to  1000 Hz   measured  -27.5 dB   <- present
```

A symmetric clipper generates **only odd harmonics**, so the even fold bins are empty and the odd
ones are loud. The detector found exactly that, unprompted. A **1 kHz component from a 7 kHz
input** is the cleanest possible proof of fold-back: there is no mechanism other than aliasing
that can put energy there.

Re-run that validation any time you change the analysis code. A measurement rig you have not
tried to fool is not a measurement rig.

## Reading the outputs

- **`inharmonic_energy_db_rel_fund`** — below −70 dB is clean, −70 to −45 is audible on bright
  material, above −45 is the "cheap digital distortion" sound.
- **`even_over_odd_db`** — positive means even-dominant, which correlates with "warm" and "tube."
  Negative means odd-dominant, which correlates with "edge" and "transistor." **This is the single
  most useful number for matching a saturator's character.**
- **`curve`** — plot `out_db` against `in_db`. A compressor's knee, threshold and ratio are all
  directly readable off that plot.
- **`envelope`** — the step up gives attack, the step down gives release. A **two-slope** release
  is the signature of program-dependent ballistics (see `DYNAMICS.md`), and you will see it
  clearly on the LA-2A.
- **`rt60`** — per-octave decay. Falling RT60 with frequency is correct and expected; flat RT60
  across octaves is the mark of an under-damped algorithm.

## Practical notes

- **Set the plugin's parameters before measuring.** `pedalboard` exposes them; the report dumps
  the first 60 so each measurement records the state it was taken in. A measurement without its
  parameter state is not reproducible.
- **Measure at several drive levels, always.** A single-level harmonic profile tells you almost
  nothing, because the whole point is that real analog character *changes shape* with level.
- **Watch for latency.** Lookahead limiters and linear-phase EQs delay the signal; the sweep
  deconvolution handles it, but `curve` and `envelope` do not compensate.
- **Some plugins won't load headless** (iLok, or a UI-dependent init). If `load_plugin` throws,
  that plugin has to be measured by rendering through a DAW offline instead.
