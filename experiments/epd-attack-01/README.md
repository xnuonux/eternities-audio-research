# EPD Attack 01 — executable research core

2026-09-12 · research 0.0.1 · no human participants

This branch adds a bounded offline implementation of BIND-CF, POWER-CT and CONTINUUM-EC. These are experimental signal transformations, not validated perceptual controls or finished VST3 plugins. Earlier plugins and idea documents are unchanged.

The accompanying conversation delivery contains the complete 48-stimulus/33-pair browser lab, source archive, analysis code, protocol and evidence. This repository directory contains the reusable DSP core and its command-line entry point plus research findings, so Claude can continue development without extracting commercial DSP.

## Run

Python 3.11+; tested with Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, SoundFile 0.13.1 and pyloudnorm 0.2.0.

```sh
python -m pip install -r requirements.txt
python -m epd.cli bind input.wav new-output.wav --amount 0.7
python -m epd.cli continuum input.wav new-output.wav --amount 0.7
python -m epd.cli power isolated-mono-impact.wav new-output.wav --amount 0.7 --modes 6
```

BIND and CONTINUUM accept at most 60 seconds through the CLI. POWER requires one isolated mono impact, onset at sample zero, at most two seconds, and rejects poor modal fits. Output must be a new file. Every function uses offline/whole-clip processing and allocates memory. There is no realtime callback, plugin state, host automation, certified true-peak meter, Windows binary or FL Studio test here.

## Findings

BIND increased cross-band envelope co-movement on four synthetic cases, but that is a cue manipulation, not a probability of fusion. A simple coherent endpoint is reproducible with ordinary shared amplitude modulation.

POWER's first contact-spectrum design is close to a fitted static-EQ control: relative RMS residual -45.77 to -38.34 dB. No claim of inaudibility is made. Absolute source power and acoustic-path gain are nonidentifiable without assumptions: (2e)*(h/2)=e*h. The implementation changes contact coloration, not watts or measured force.

CONTINUUM reduced the normalized 8–80 Hz envelope-energy diagnostic by 6.51–10.99 dB without adding events or rearranging the source timeline. A broadband version also changes event contrast. A categorical texture percept remains unassessed.

## Complete delivery identity

- EPD-Attack-01-Lab.zip: SHA-256 29a4a4d56651759ff98e390a18a5636045747bbf3cb1640e2baa64b8418fbf95
- EPD-Attack-01-Source.zip: SHA-256 3480d8cb374166bb8958ad3fbd5b3a235220b2342e87613bc6d2923f4b6d0f70

The delivered lab passed 53 pytest cases and eight named browser checks. Browser testing used Linux headless Chromium with one shared PCM fixture and injected completion events for the 33 UI flows; those simulations were discarded and are not human responses. All 48 actual stimuli are original synthesis, 48 kHz / 24-bit PCM, integrated-level matched to -23 LUFS. Largest 16x reconstruction estimate: -5.44 dBFS. No limiter was used.

## Research rules

Run the label-blind pilot before describing any of these as new effects. Keep ordinary-processing baselines and identical A/A controls. Collect brightness, loudness and musical preference separately. Aggregate trials within participants; never count repeated trials as independent listeners. Zero participants must yield UNASSESSED, not a fabricated win rate. The complete protocol fixes a practical 24-complete-session pilot target; it is not a power calculation or an external registry preregistration.

The next scientific gate is an advantage over ordinary processing on held-out real performances with a new listener group. The next engineering gate, after selecting a surviving mechanism, is causal streaming with declared latency, bounded memory/CPU, deterministic transport/state behavior, and actual Windows/FL Studio testing.
