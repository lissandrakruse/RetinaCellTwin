# Theoretical foundation and novelty boundary

Assessment date: 2026-09-20

## Biological foundation

### Spaceflight-associated neuro-ocular risk

SANS is a clinically observed neuro-ocular condition associated with long-duration spaceflight. Reported features include optic-disc edema, globe flattening, choroidal and retinal folds, refractive change and nerve-fiber-layer abnormalities. The syndrome is multifactorial, and its existence does not mean that a mouse retinal molecular signature can be interpreted directly as human SANS.

- Yang et al. (2022), *Spaceflight-associated neuro-ocular syndrome: a review of potential pathogenesis and intervention*. <https://doi.org/10.18240/ijo.2022.02.21>
- Martin Paez et al. (2020), *Spaceflight associated neuro-ocular syndrome (SANS): a systematic review and future directions*. <https://doi.org/10.2147/EB.S234076>

**Implication:** SANS provides the human-health motivation, but RetinaCellTwin must retain a mouse-retina and hypothesis-generating scope.

### Retinal oxidative stress, photoreceptors and structural injury

Overbey et al. reported that RR-9 retinal RNA-seq changes were enriched for visual perception, phototransduction, retinal phenotypes and RNA processing. The same study reported increased 4-HNE staining, cone-photoreceptor degradation and reduced retinal-layer thickness after spaceflight.

- Overbey et al. (2019), *Spaceflight influences gene expression, photoreceptor integrity, and oxidative stress-related damage in the murine retina*. <https://doi.org/10.1038/s41598-019-49453-x>
- Mao et al. (2023), *Evidence of Spaceflight-Induced Adverse Effects on Photoreceptors and Retinal Function in the Mouse Eye*. <https://doi.org/10.3390/ijms24087362>

**Implication:** OSD-255, OSD-557 and OSD-568 have a biologically coherent oxidative-stress/photoreceptor/apoptosis/barrier foundation. Repeating the original RR-9 enrichment is not novel. Testing transferability and failure across missions is the new question.

### Artificial gravity as a countermeasure experiment

Mouse studies have reported biochemical/proteomic retinal responses under artificial gravity, and Kremsky et al. later demonstrated dose-dependent attenuation of retinal and optic-nerve transcriptomic responses in OSD-758.

- Mao et al. (2018), *Impact of Spaceflight and Artificial Gravity on the Mouse Retina: Biochemical and Proteomic Analysis*. <https://doi.org/10.3390/ijms19092546>
- Kremsky et al. (2024), *Artificial Gravity Attenuates the Transcriptomic Response to Spaceflight in the Optic Nerve and Retina*. <https://doi.org/10.3390/ijms252212041>

**Implication:** RetinaCellTwin cannot claim discovery of artificial-gravity attenuation. Its contribution is the frozen-panel transfer test and comparison with the transcriptome background.

### Radiation and hindlimb-unloading analogues

Kothiyal et al. used longitudinal multi-omics to characterize murine retinal responses to chronic low-dose irradiation and simulated microgravity, providing the biological basis for using OSD-203 as a bounded attribution audit.

- Kothiyal et al. (2022), *A multi-omics longitudinal study of the murine retinal response to chronic low-dose irradiation and/or simulated microgravity*. <https://doi.org/10.1038/s41598-022-19360-9>

**Implication:** Cross-dataset concordance can show compatibility with an analogue response. It cannot identify radiation or unloading as the cause of a spaceflight effect.

### Existing machine-learning analysis

Casaletto et al. analyzed RR-9 retinal molecular and imaging data using a machine-learning ensemble and reported molecular pathways associated with retinal damage.

- Casaletto et al. (2026), *Machine learning ensemble reveals distinct molecular pathways of retinal damage in spaceflown mice*. <https://doi.org/10.1038/s41526-026-00625-w>

**Implication:** RetinaCellTwin must not present machine-learning pathway discovery in RR-9 as new. Its distinct contribution is cross-mission falsification, time-resolved analogue benchmarking, provenance and explicit uncertainty boundaries.

### Single-cell retinal reference

Li et al. integrated newly generated and public mouse retinal single-cell RNA-seq into the Mouse Retina Cell Atlas, comprising more than 330,000 cells, 12 major classes and 138 cell types. Figure 1E displays one canonical anchor for each major class.

- Li et al. (2024), *Comprehensive single-cell atlas of the mouse retina*. <https://doi.org/10.1016/j.isci.2024.109916>

**Implication:** These published anchors can test whether obvious class-associated genes appear in the bulk contrasts, but they cannot recover cell proportions, assign an effect to a specific cell population or separate compositional change from within-cell regulation. A true cell-resolved extension requires single-cell or spatial measurements under the relevant exposure.

## Digital-twin foundation

A credible biomedical digital twin requires more than an interface. Verification, validation and uncertainty quantification (VVUQ) are central to determining whether a computational representation is fit for its intended use.

- Corral-Acero et al. (2020), *The 'Digital Twin' to enable the vision of precision cardiology*. <https://doi.org/10.1016/j.molmed.2020.04.009>
- National Academies (2024), *Foundational Research Gaps and Future Directions for Digital Twins*. <https://doi.org/10.17226/26894>
- Sel et al. (2025), *Survey and perspective on verification, validation, and uncertainty quantification of digital twins for precision medicine*. <https://doi.org/10.1038/s41746-025-01447-y>

RetinaCellTwin implements an early-stage VVUQ interpretation:

| VVUQ element | Current implementation | Remaining limitation |
| --- | --- | --- |
| Code verification | Automated tests, deterministic seeds, checksums, frozen results, exact Python lock, container and CI workflow | Container still requires a final clean-room release rerun |
| Data verification | API visibility checks, filenames, sizes and SHA-256 provenance | Relies on public repository metadata |
| Internal statistical validation | NASA DE tables compared with VST-level and raw-count effect audits | Full independent DESeq2 model still pending |
| External validation | OSD-255 panel tested without reselection in OSD-758 | Missions differ in hardware, design and exposure |
| Mechanistic triangulation | OSD-203 radiation and unloading contrasts across three times | Analogues do not reproduce the orbital environment |
| Cellular context | Published MRCA canonical anchors audited across four bulk contrasts | One marker per class is not deconvolution or cell-of-origin evidence |
| Cross-modal context | Four-domain evidence matrix using frozen modality-specific results | Accessions and eyes are not paired; no mediation or joint statistic |
| Uncertainty | FDR, effect sizes, random-panel tests and explicit scenario assumptions | No validated individual-level predictive uncertainty |

## Defensible novelty statement

> RetinaCellTwin is a reproducible cross-mission credibility audit of a murine retinal spaceflight signature. It shows that a statistically significant RR-9 signature does not generalize as a universal gravity signature, distinguishes study-wide artificial-gravity attenuation from panel-specific enrichment, and identifies a transient seven-day radiation-compatible component that exceeds random-panel expectations while remaining non-causal and prospective.

## Stronger research hypotheses

### Primary hypothesis

An RR-9 flight-versus-ground retinal signature will not necessarily transfer as a stable gravity-specific signature across a mission containing in-flight artificial-gravity controls.

### Secondary hypothesis

Residual flight-associated expression under in-flight 1G contains a time-restricted component concordant with controlled low-dose radiation, but not a stable radiation signature across all time points.

### Multimodal contextual hypothesis

Transcriptomic signals related to stress and retinal function coexist with image-derived oxidative-stress, photoreceptor, apoptosis and barrier phenotypes at the study level, but the available accessions do not support sample-paired mediation or causal modelling.

## Claims deliberately excluded

- Prediction or diagnosis of human SANS.
- Individualized physiological forecasting.
- Causal separation of microgravity and radiation from flight-versus-ground comparisons.
- Rediscovery of previously published RR-9 pathways or artificial-gravity attenuation.
- A validated therapeutic or antioxidant countermeasure.
