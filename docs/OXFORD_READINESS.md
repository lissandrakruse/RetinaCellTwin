# Oxford readiness: GigaScience Research Article

Assessment date: 2026-09-20

## Target

Primary target: **GigaScience** (Oxford University Press), article type **Research Article**, with the manuscript positioned for the journal's [Data-Driven Multicellular Systems Biology](https://academic.oup.com/gigascience/pages/multicellular_cfp) thematic series.

The collection explicitly invites research articles and technical notes involving modelling and simulation, high-throughput microscopy, computational analysis of multicellular data, open tools, interoperability and containers. GigaScience also requires original-research submissions to follow its minimum reporting standards and strongly integrates papers with the GigaDB repository; see the journal's [scope and publication model](https://academic.oup.com/gigascience/pages/about).

## Editorial thesis

RetinaCellTwin should not be submitted as “a website about retina.” Its publishable unit is a reproducible, multimodal, cross-mission test of whether an RR-9 retinal flight signature transfers to an independent artificial-gravity mission and to controlled ground analogues.

The central result is appropriately mixed:

1. The 362-gene RR-9 discovery signature does **not** reproduce as a universal gravity signature in OSD-758.
2. Apparent artificial-gravity attenuation inside that panel is not enriched against the transcriptome background.
3. A narrower seven-day radiation-compatible component is enriched beyond 10,000 random panels, but is transient and does not establish causality.
4. A new sample-level audit confirms strong technical agreement between public VST matrices and NASA differential-expression effects across ten prespecified contrasts (rho 0.854–0.888; direction agreement 93.5%–96.0%).
5. A Mouse Retina Cell Atlas anchor audit provides bounded cellular context: only *Arr3* passes FDR in RR-9 and no anchor passes FDR in the independent/analogue contrasts, so no replicated cell-of-origin claim is made.
6. A formal unpaired evidence matrix limits cross-modal convergence to the photoreceptor domain and keeps the apoptosis result imaging-only.

This combination of negative replication, bounded positive signal and open reproducibility is more credible than a universal-biomarker claim.

## Readiness gates

| Gate | Current state | Required action |
| --- | --- | --- |
| Clear biological question | Pass | Preserve the universal-signature falsification and transient-radiation hypothesis as separate claims. |
| Multimission design | Pass | Keep OSD-255 discovery, OSD-758 validation and OSD-203 analog attribution frozen. |
| Multimodal context | Pass with bounded scope | A four-domain unpaired evidence matrix is complete; retain the study-level, non-mediation interpretation. |
| Statistical audit | Pass for processed data | The VST audit independently re-estimates ten contrasts, but reuses NASA-processed VST values. |
| Count-level independence | Partial | Median-of-ratios normalization and effect directions are independently recomputed from STAR counts; a locked DESeq2/edgeR inferential workflow or FASTQ reprocessing remains desirable. |
| Biological interpretation | Pass with bounded scope | GO analysis and the MRCA canonical-anchor audit are complete; preserve the explicit non-deconvolution boundary. |
| Prior-work comparison | Pass in draft | Kremsky et al. (2024), Kothiyal et al. (2022), Casaletto et al. (2026) and Li et al. (2024) are distinguished from the new contribution. |
| Figures | Pass for current analyses | Six deterministic SVG figures cover architecture, transfer, audit concordance, GO context, retinal-cell anchors and cross-modal synthesis. |
| Reproducible execution | Pass in repository | Exact Python lock, Dockerfile, `run_all.sh` and CI verification workflow are present; rerun the container once more before release. |
| Data archiving | Release prepared | Archive v0.3.0 through Zenodo and insert the DOI; coordinate supporting-data deposition with GigaDB at submission. |
| Manuscript | Review DOCX complete | Final authorship, declarations and author approval remain open. |
| Editorial package | Draft complete | Cover letter, checklist, CRediT worksheet and AI disclosure are prepared; replace all placeholders only with verified human information. |
| Authorship approval | Open | Confirm author list, contributions and approval before submission. |
| AI transparency | Open | Preserve relevant interaction outputs, complete the supplement record and obtain author approval under the journal's current policy. |

## Claims that are allowed

- The RR-9 discovery panel failed to generalize as a stable universal gravity signature.
- The seven-day radiation-compatible concordance is stronger than expected for random panels of the same size under the implemented benchmark.
- The signal is time-specific and hypothesis-generating.
- Sample-level VST effects are directionally and rank-concordant with NASA log2 fold changes.
- Independently normalized STAR-count effects remain rank- and direction-concordant with NASA DESeq2 effects across ten contrasts.
- The canonical cone anchor *Arr3* is significant in RR-9, but the atlas-anchor pattern does not replicate in the tested independent/analogue contrasts.
- Photoreceptor imaging and transcriptomic results converge at the study/domain level, without sample pairing or mediation inference.
- The software separates observed data, derived statistics and hypothetical decision scenarios.

## Claims that are not allowed

- Radiation caused the RR-9 retinal response.
- The nine candidates are validated biomarkers.
- The model predicts SANS or human clinical outcomes.
- The opposite-eye imaging and RNA-seq measurements are paired.
- The VST audit is an independent FASTQ reprocessing.
- The count-level effect audit reproduces the complete DESeq2 inferential model.
- RetinaCellTwin is a validated individual-level physiological digital twin.
- A canonical anchor change identifies a responding cell population or a change in cell abundance.
- The photoreceptor evidence matrix establishes a sample-level association or causal path between *Arr3* and PNA density.

## Release strategy

Version v0.3.0 freezes the expanded scientific workflow, derived outputs, figures and review-formatted manuscript. Archive this exact tag with Zenodo and insert its DOI into the manuscript before submission. Journal submission should occur only after the corresponding author and every coauthor approve the exact manuscript, author order and declarations.
