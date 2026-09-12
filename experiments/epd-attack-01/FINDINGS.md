# Attack 01 findings — no human outcomes yet

## BIND-CF

Mean cross-band envelope correlation (not a source-count estimate):

| Synthetic family | Reference | Intermediate | Candidate |
|---|---:|---:|---:|
| 0 | 0.518 | 0.699 | 0.863 |
| 1 | 0.401 | 0.701 | 0.937 |
| 2 | 0.498 | 0.739 | 0.926 |
| 3 | 0.604 | 0.717 | 0.817 |

Energy-inactive bands were excluded with a fixed rule. This is a manipulation check, not evidence that listeners heard fewer sources. An ordinary-AM-equivalent calibration nulls to 5.56e-17 maximum error; do not use that easy example to claim a new primitive.

## POWER-CT

Candidate versus oracle spectrum-matched static EQ, relative RMS residual in dB: -45.77, -43.19, -40.48, -38.34. These are not audibility thresholds. The source-power claim is not supported by the current contact-coloration implementation. Body-model frequencies/decays remain fixed by construction. On a separate exactly specified three-mode calibration, modal fit relative error was 3.43e-14; that is not a validation on arbitrary real recordings.

## CONTINUUM-EC

Normalized 8–80 Hz envelope energy decreased 6.51, 10.99, 8.06 and 6.99 dB on four synthetic streams. Source rates were 12/16/20/24 events per second, unchanged by processing. The sample timeline was not rearranged, but transient audibility and perceived rhythm can change. Broadband processing is an active alternative; categorical texture perception is UNASSESSED.

## Evidence boundaries

All stimuli were normalized within comparison families to -23 integrated LUFS, maximum post-quantization deviation <0.001 LU. Maximum 16x reconstruction estimate -5.44 dBFS; no clipping or limiting. Equal LUFS does not guarantee equal perceived loudness. The browser asks about loudness and brightness differences separately.

Zero human participants. 53 software tests and simulated browser interactions are not listening results. No VST3 or FL Studio verification in this research release.

## Primary research anchors

- Elhilali et al. (2009), temporal coherence. DOI 10.1016/j.neuron.2008.12.005. https://pubmed.ncbi.nlm.nih.gov/19186172/
- Bogaard et al. (2025), harmonicity and tracking polyphonic voices. https://www.nature.com/articles/s41598-025-16404-8
- Traer et al. (2021), causal inference and source intensity. DOI 10.1016/j.cognition.2021.104627. https://pubmed.ncbi.nlm.nih.gov/34044231/
- Douglas et al. (2016), sound mass in Continuum. DOI 10.1525/mp.2016.33.3.287. Coauthor discussion: https://mtosmt.org/issues/mto.18.24.3/mto.18.24.3.noble.php

These papers motivate hypotheses; none validate this implementation. Full protocol, source/build scripts, PCM stimuli, hash manifest and listener analyzer are in the separately delivered Lab/Source archives identified in README.md.
