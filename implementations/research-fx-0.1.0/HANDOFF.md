# Research FX 0.1.0 — Claude Code handoff

Three independent compiled Windows x64 VST3 **stereo effects** were built from this research: **CINDER** (harmonic color), **DOUBLE** (drifting doubles), and **SHUFFLE** (spectral stereo width). Each has 16 factory presets and a native Win32 editor. These are unsigned playable alphas, not production-certified releases.

## Where the implementation is

The complete buildable implementation and detailed evidence were delivered to Dom in the ChatGPT conversation as `Eternities-Research-FX-0.1.0-Source.zip`.

**Source archive SHA-256:** `29a2ff6c62f10647a978c210de6d0bf545c08d22e4ed60a8a0fb801248ad888e`

This branch contains a handoff document, **not the source archive or plugin binaries**. Obtain that archive from the conversation and extract it into a separate directory/worktree. Do not overwrite the existing research or instrument sources. The archive contains `src/`, reproducible build tools, native and actual-plugin host tests, original musical fixtures, parameter and identifier schemas, factory patches, licenses, and `docs/evidence/`.

Research input was the content-addressed tree `104403f369afbcdce7e19e09daaf7da69e3f1732`. The inspected snapshot contained no target-plugin measurement reports. No installed commercial reference was available to this build session. No proprietary code, commercial samples, or binary disassembly were used. Existing AUREL, BRASA, FORGE, VELORA, CORDA, and UMBRA sources were not changed.

## Implementation decisions worth retaining

### CINDER

Fixed 8x interpolation/decimation using a 1025-tap Kaiser FIR; first-order tanh antiderivative antialiasing; midpoint Taylor fallback near coincident samples; compensated ADAA small-signal filter and integer alignment; inverse low-frequency pre/de-emphasis; asymmetry, high-frequency shelf, program-dependent sag and recovery, DC blocking, optional low cut, parallel mix, and delta audition. Total reported latency is 129 samples.

Subtract the **interval-averaged bias baseline**, rather than only tanh of the current bias, so bias automation does not excite a zero-input waveshaper. This is an original analog-inspired color processor, **not** a calibrated Jiles-Atherton hysteresis model, measured transformer, or tape-transport simulation.

### DOUBLE

32-tap, 256-phase interpolated windowed-sinc readers; independent smooth random drift and flutter; bounded read-head velocity; filtered stereo layers. **Mono protect** adds only side information, preserving the original mid at neutral output gain. The added stereo effect therefore disappears in mono; this does not fix phase problems already in the source. Classic additive mode is deliberately different and is not mono invariant. The original dry path has zero reported latency; wet layers have intentional 20–60 ms base delays plus movement.

### SHUFFLE

Six overlapping logarithmic side-width regions, not a complete ERB analyzer. Hann/Hann weighted overlap-add, quarter-window hops, and 2/3 synthesis normalization. Neutral reconstruction is tested. Mono-bass treatment precedes field rotation: nonzero rotation can reintroduce low-frequency side content. Keep rotation at zero when bass anchoring is required. At 48 kHz the reported latency is 2048 samples / 42.67 ms. This is a mixing/bus tool, not latency-free monitoring.

### Shared plugin contracts

Stereo input/output, float32/64 buses, unique plugin IDs, latency-matched smoothed bypass, parameter queues, output meters, CRC-checked parameter state, 12 main controls, Save/Load, and 16 presets each. Initial host parameters delivered in the first block are primed before processing instead of ramping from an unrelated default preset. State restore clears histories: current tails, spectral history, and drift phase are not serialized. No allocation or free was observed in the instrumented audio callbacks.

## Executed verification — bounded claims

- **7,815** assertions passed under ASan/UBSan with allocation/free instrumentation: CINDER 2,595; DOUBLE 2,625; SHUFFLE 2,595. Zero measured callback allocations or frees.
- **192** independent Linux VST3 preset/sample-rate cases through Pedalboard/JUCE: 3 products x 16 presets x 44.1/48/96/192 kHz. Host-versus-separately-compiled-DSP and reset-state recall across 127/1024 sample blocks were exactly equal at float32 output. 444 host assertions passed across the completed batches.
- **48** preset cases executed through the actual compiled Windows PE audio machine code using the included restricted Microsoft-ABI bridge. This bridge runs on Linux; it is **not Windows**, did not attach or interact with the native editor, and does not validate FL Studio compatibility.
- **30** named DSP measurement results passed. CINDER's worst inharmonic result was **-87.47 dBc** in the specified coherent 7 kHz / -1 dBFS / 48 kHz test at five drive levels. This is not an all-frequency/all-setting alias bound. Conditions are recorded in the JSON.
- DOUBLE protected-mode mid null error was below 1e-13 absolute amplitude on the specified stereo fixture. SHUFFLE neutral reconstruction was below 1e-12. These are native double-DSP measurements, not universal perceptual claims.
- All three Windows binaries rebuilt **byte-for-byte identically** from the extracted source archive using the same Clang/LLD toolchain.
- First-pass failed DSP results were retained. Corrected issues included fully engaged bypass rounding, SHUFFLE low-side leakage/window normalization, first-block parameter priming, bias automation, and UI control overlap.

Native Windows editor interaction, actual FL Studio use, pluginval, and the official VST3 validator remain **unassessed**. The interface PNGs are drawing-code previews, not Windows screenshots. Musical demos use original synthesized fixtures, not real vocal or DI recordings, and were rendered through actual Linux VST3s. Each demo is 13.5 seconds dry, 0.4 seconds silence, then a processed repeat; only RMS matching and endpoint fades were applied afterward. RMS matching is not standardized LUFS matching.

## Windows binaries and packaged artifacts

Binary SHA-256:

- CINDER: `0b4acd55c0eff9b96d2bab414f266a1a9b254f068a3859a69511c70ec9f11986`
- DOUBLE: `d03c900de83bae564d392e838c461bca8225c265ccd2cf9b175662eb855bf222`
- SHUFFLE: `df14e0e4c3e3386bb6444acf3f919a3dc36930575b71f25cbf22ac8c3bab511d`

Windows ZIP SHA-256:

- `CINDER-0.1.0-Windows-VST3.zip`: `f464204134315e58ed2cf7db2d41c7d02b76b8272589a397c27a5851a2fed557`
- `DOUBLE-0.1.0-Windows-VST3.zip`: `2a92eca0828e0c4364ef59ba1b323ec06002f49581ee0856555fbb30cc6421d0`
- `SHUFFLE-0.1.0-Windows-VST3.zip`: `3773133603fff2272c259606da98133ab41a8b714cd1f12e28bb4c97da9ef864`

## Next engineering gates, in order

1. Test scan, open/close, resize, file dialogs, DPI and multiple instances on native Windows. Then test FL Studio project save/reopen, automation, bypass/PDC, routing changes, suspend/resume and offline export. Start in an empty project.
2. Run the official validator and pluginval, long-session stress, clean-machine testing and real-time CPU profiling at Dom's actual buffer/rate settings.
3. Extend alias/interpolation measurements to swept tones, two-tone intermodulation, rapid automation and transients. Do not turn one sine-test result into a universal quality claim.
4. Audition real vocal, DI and mix recordings at matched loudness. Tune presets by listening without claiming commercial equivalence.
5. After host behavior is stable, consider porting the antialiasing, state and bypass primitives into the earlier instruments. Preserve existing IDs and use explicit state migrations instead of silently changing parameter order.

No effect is a limiter: strong gain, width or layering can exceed 0 dBFS. These builds require headroom, are unsigned, and have no account/network/sample-library requirement. Accessibility and keyboard/DPI behavior require further work.
