# The Kazrog catalog — nine products, one core

Read from binary metadata, not assumed. Every one of these is **Kazrog Inc**:

| plugin | version | category |
|---|---|---|
| True Iron | 1.4.2 | transformer saturation, 6 models |
| True Dynamics | 1.2.6 | compressor |
| KClip3 | 3.6.7 | clipper |
| Avalon AD2055 | 1.0.3 | EQ (solid state) |
| Avalon AD2077 | 1.0.3 | mastering EQ (passive/tube) |
| Avalon VT-747SP | 1.0.8 | opto compressor **+ EQ** |
| Retro Sta-Level | 1.0.3 | vari-mu / tube compressor |
| MHB Green | 1.0.3 | channel/character |
| MHB Red | 1.0.0 | channel/character |

**This is the most valuable single asset in the collection for our purposes, and not for the
reason you'd expect.**

---

## Why nine plugins from one small developer beats nine from nine developers

Kazrog is a small shop. A small shop ships a **shared DSP core** across its catalog and varies the
parameters — nobody writes nine independent saturation engines. **[inf, high confidence]**

Which means you are holding a **controlled experiment**: one engine, nine parameter sets,
measurable with one protocol. Every difference you measure between two Kazrog products isolates a
*parameter choice*, not an implementation difference.

You cannot buy that. Measuring soothe2 against Pro-Q tells you about two different companies'
entire approaches, confounded. Measuring AD2055 against AD2077 tells you what changed when one
engineer modelled a solid-state EQ versus a passive tube one **with the same tools**.

### The three sub-experiments it gives you for free

1. **Saturation across device classes, same core.** True Iron (transformer) vs Retro Sta-Level
   (tube) vs MHB (whatever character it targets) vs KClip3 (clipper). Four points on the
   nonlinearity spectrum from one lab.
2. **Compressor topologies, same core.** True Dynamics vs VT-747SP (optical) vs Retro Sta-Level
   (vari-mu). Per `DYNAMICS.md`, those should differ measurably in **detector position** and
   **ballistics** — and if the four-decision taxonomy is right, you'll see it directly in the
   `curve` and `envelope` tests.
3. **EQ topologies, same core.** AD2055 (active solid-state, bands should be independent) vs
   AD2077 (passive/tube lineage, bands should **interact** per `THE-EXPENSIVE-ONES.md` §4).

That third one is the sharpest test in the whole repo, and it's cheap.

---

## The band-interaction test — run this first

**Question:** does AD2077 model a genuinely passive network (where bands interact through shared
impedance) or is it cascaded independent biquads with a tube curve bolted on?

**Method:**

1. `--tests response` on AD2077 with **only band 2 boosted**. Record the curve.
2. `--tests response` with **only band 4 boosted**. Record.
3. `--tests response` with **both boosted simultaneously**. Record.
4. Compare the measured "both" curve against the **sum in dB** of the two individual curves.

**Independent biquads sum exactly.** A passive network does not — the combined curve will deviate,
and the deviation *is* the interaction.

Then repeat on AD2055 as the control. If AD2055 sums and AD2077 doesn't, you have directly
measured the difference between an active and a passive EQ model, from your own desk, with no
access to anyone's source.

**Why it matters:** it tells you whether you need a Wave Digital Filter framework
(`THE-EXPENSIVE-ONES.md` §4) or whether well-chosen cascaded biquads are sufficient for the passive
character. That is a weeks-of-work decision, settled by an afternoon of measurement.

---

## The compressor topology test

`DYNAMICS.md` claims a compressor is four decisions, and that **feed-forward vs feedback detector**
is the big vintage/modern divider. Kazrog gives you three compressors that should sit at different
points:

| plugin | expected topology | what to look for |
|---|---|---|
| **True Dynamics** | modern, likely feed-forward | exact ratios, static curve matches the nominal setting closely |
| **VT-747SP** | optical | **two-slope release**; soft self-limiting ratio; forgiving knee |
| **Retro Sta-Level** | vari-mu tube | **ratio that increases with level**; feedback-ish soft knee |

**Method:** `--tests curve,envelope` on all three at matched settings.

- The **`curve`** plot reveals the knee and whether the ratio is constant. A vari-mu's curve should
  *bend* — the slope steepens as input rises. A feed-forward VCA's should be a clean straight line
  above the knee.
- The **`envelope`** plot reveals ballistics. **Look for a two-slope release** on the optical one:
  fast initial recovery then a long tail. That's the photoresistor's physics and it's the single
  most recognisable optical signature.

**If all three show the same curve shape and the same release**, the taxonomy is wrong, or Kazrog
is varying less than the marketing implies. Either would be worth knowing, and nobody has
published it.

---

## The saturation family test

Run the full `TRUE-IRON-DEEP.md` protocol — the THD surface over (frequency × level) — across
**True Iron, Retro Sta-Level, MHB Green, MHB Red, KClip3**.

What you're extracting:

- **True Iron** should show strong frequency skew (bass saturating first). If it doesn't, it isn't
  really modelling core flux.
- **Retro Sta-Level** is a tube compressor; expect **even-dominant** harmonics and much less
  frequency skew, because there's no core to saturate.
- **KClip3** should show near-zero frequency dependence and an abrupt level threshold — a clipper
  is memoryless and frequency-blind by construction. **This is your control case**: if KClip3
  shows frequency-dependent saturation, your measurement is wrong, not the plugin.
- **MHB Green vs Red** — two variants of one idea. The difference between them is a pure
  parameter delta and will show up cleanly.

**Having a known-flat control (KClip3) in the same family is what makes the whole set rigorous.**
It validates the measurement before you trust the results.

---

## The strategic read on Kazrog

**[inf]** Kazrog appears to be essentially one engineer with a shared core and good ears. Nine
credible products, official licensing deals with Avalon and Retro Instruments, and a real
reputation.

That's the existence proof for the plan in this repo: **a small team with a good core and
disciplined measurement can ship a credible analog catalog.** It doesn't require Acustica's
capture rigs or Waves' headcount.

The thing to copy is not any of the plugins. **It's the structure** — one well-built engine,
carefully parameterised, shipped repeatedly with different clothes and licensing.

---

## Run order

```bash
P="C:/Program Files/Common Files/VST3"
M="../measurements/kazrog"

# 1. the control — establishes the measurement is sound
python measure.py --plugin "$P/KClip3.vst3"          --tests alias,harmonics --out $M/kclip3

# 2. the band-interaction test — the weeks-of-work decision
python measure.py --plugin "$P/Avalon AD2077.vst3"   --tests response       --out $M/ad2077-b2
python measure.py --plugin "$P/Avalon AD2077.vst3"   --tests response       --out $M/ad2077-b4
python measure.py --plugin "$P/Avalon AD2077.vst3"   --tests response       --out $M/ad2077-both
python measure.py --plugin "$P/Avalon AD2055.vst3"   --tests response       --out $M/ad2055-control

# 3. compressor topologies
python measure.py --plugin "$P/True Dynamics.vst3"   --tests curve,envelope --out $M/true-dynamics
python measure.py --plugin "$P/Avalon VT-747SP.vst3" --tests curve,envelope --out $M/vt747
python measure.py --plugin "$P/Retro Sta-Level.vst3" --tests curve,envelope --out $M/sta-level

# 4. the saturation family
python measure.py --plugin "$P/True Iron.vst3"       --tests alias,harmonics --out $M/true-iron
python measure.py --plugin "$P/MHB Green.vst3"       --tests alias,harmonics --out $M/mhb-green
python measure.py --plugin "$P/MHB Red.vst3"         --tests alias,harmonics --out $M/mhb-red
```

Remember to set and record the plugin parameters between runs — the harness dumps them into each
report, and a measurement without its parameter state is an anecdote.
