# RetinaCellTwin: a reproducible multimodal and cross-mission audit of retinal responses to spaceflight, artificial gravity and ground analogues

**Article type:** Research Article

**Target:** GigaScience / Data-Driven Multicellular Systems Biology

**Status:** v0.3.0 review draft; not approved for journal submission

## Authors

Lissandra Kruse Fuganti<sup>1</sup>

<sup>1</sup>Universidade Estadual de Ponta Grossa, Ponta Grossa, Paraná, Brazil

**Corresponding author:** to be confirmed before submission.

**Author order and contributions:** to be confirmed with every contributor before submission.

## Abstract

### Background

Spaceflight-associated retinal responses reflect a mixture of altered gravity, radiation, habitat and operational exposures. Public NASA Open Science Data Repository (OSDR) studies provide transcriptomic and image-derived measurements across spaceflight, artificial-gravity and ground-analogue experiments, but differences among missions and modalities complicate direct biological interpretation. We developed RetinaCellTwin as an evidence-layered, reproducible framework to test cross-mission transferability while keeping observed measurements, derived statistics and hypothetical decision scenarios separate. The intended use is research audit and hypothesis generation rather than individual diagnosis or clinical prediction.

### Results

We froze a 362-gene retinal flight-versus-ground discovery panel from OSD-255 at NASA-adjusted P < 0.05 and tested it without reselection in the independent OSD-758 artificial-gravity study. The OSD-255 effects did not reproduce in OSD-758 microgravity versus ground (Spearman rho = -0.071; 170/362, 47.0%, directionally concordant), and no gene met the prespecified strict gravity-sensitive candidate rule. Although absolute effects decreased within the panel at 0.66G and 1G relative to microgravity, this attenuation was not enriched relative to the transcriptome background. We then compared OSD-758 residual flight-associated effects with the OSD-203 radiation and hindlimb-unloading analogues. Seven-day radiation effects were concordant for 229/362 genes (63.3%; rho = 0.272), and the panel exceeded 10,000 random panels after correction (empirical FDR = 0.0246). Nine genes additionally had OSD-203 radiation FDR < 0.05 and concordant direction. The pattern was not maintained at one or four months. VST- and count-level sensitivity audits supported effect-level consistency with NASA results. Gene Ontology analysis recapitulated known RR-9 stress, localization, light-response and protein-folding biology, whereas neither the seven-day concordant subset nor the nine-candidate subset had a term passing FDR < 0.05 against the frozen panel. Of 12 canonical major-class anchors from the Mouse Retina Cell Atlas, only the cone anchor *Arr3* passed FDR in OSD-255 and none passed FDR in the independent or analogue contrasts. An explicitly unpaired evidence matrix identified study-level photoreceptor convergence—lower PNA-positive density (Welch FDR = 0.0242), lower *Arr3* expression (FDR = 0.000480) and light-response GO enrichment (FDR = 0.00248)—and imaging-only apoptosis evidence from total TUNEL density (FDR = 0.000810). Oxidative-stress and vascular/barrier imaging domains did not cross the seven-endpoint Welch FDR boundary.

### Conclusions

The data do not support a stable universal retinal gravity signature. They support a narrower, time-specific radiation-compatible hypothesis that requires prospective validation and cannot be interpreted causally from cross-dataset concordance. RetinaCellTwin provides a transparent computational framework and negative-replication result while exposing the statistical and biological boundaries of a digital-twin label.

**Keywords:** retina; spaceflight; artificial gravity; radiation; NASA OSDR; transcriptomics; microscopy; digital twin; reproducibility

## Background

Spaceflight-associated neuro-ocular syndrome (SANS) includes optic-disc, globe, choroidal, retinal and refractive changes after spaceflight [1,2]. Its pathophysiology is multifactorial, and a mouse retinal molecular signature cannot be interpreted directly as human SANS. Orbital experiments expose organisms to multiple correlated environmental factors; consequently, a flight-versus-ground contrast cannot by itself isolate microgravity or radiation. Rodent retinal studies in NASA OSDR nevertheless make it possible to test whether signatures discovered in one mission generalize to other designs with artificial-gravity controls or ground analogues.

Overbey et al. reported RR-9 changes in visual perception, phototransduction, retinal phenotypes, RNA processing, oxidative damage and cone-photoreceptor integrity [3]. Later work provided functional evidence of adverse photoreceptor responses after spaceflight [4]. Mao et al. and Kremsky et al. established retinal effects and transcriptomic attenuation under artificial gravity [5,6]. Kothiyal et al. described longitudinal retinal responses to low-dose irradiation and hindlimb unloading, providing the experimental basis for OSD-203 [7]. Casaletto et al. subsequently reported machine-learning-derived molecular pathways of retinal damage using RR-9 datasets [8]. RetinaCellTwin does not claim these findings as new. Instead, it asks a different reproducibility question: does a gene set selected only in RR-9 transfer to the independent artificial-gravity experiment, and can any remaining flight-associated component be bounded using time-resolved ground analogues?

Li et al. constructed a unified Mouse Retina Cell Atlas from more than 330,000 cells, resolving 12 major classes and 138 cell types [9]. We use only the 12 canonical major-class anchors displayed in that study as a bounded contextual audit. They are not treated as a cell-fraction reference or a substitute for single-cell measurements in the spaceflight experiments.

The framework follows three evidence layers. The observed layer contains public OSDR measurements and metadata. The derived layer contains prespecified statistical contrasts, multiple-testing corrections and cross-dataset benchmarks. The hypothetical layer contains sensitivity and research-decision scenarios that are explicitly excluded from empirical claims.

## Data description

Five public mouse retinal accessions were prespecified:

- OSD-255: right-retina bulk RNA-seq, used for discovery;
- OSD-557: left-eye 4-HNE and PNA microscopy-derived measurements;
- OSD-568: left-eye TUNEL, PECAM and ZO-1 microscopy-derived measurements;
- OSD-758: retinal RNA-seq under microgravity, 0.33G, 0.66G and 1G in flight, plus ground controls;
- OSD-203: retinal RNA-seq after gamma irradiation and/or hindlimb unloading at seven days, one month and four months.

The workflow accepts only API records marked public and visible, records retrieval URLs, byte counts and SHA-256 checksums, and does not infer biological groups from filenames when OSDR metadata are available.

A small literature-derived reference table freezes the 12 canonical major-class anchors shown in Figure 1E of the Mouse Retina Cell Atlas [9], with DOI and evidence location recorded for every row.

## Analyses

### Prespecified discovery panel

The discovery panel comprised all OSD-255 genes with NASA-reported Benjamini-Hochberg adjusted P < 0.05 for Space Flight versus Ground Control. Selection occurred before examination of OSD-758 or OSD-203 effects.

### Independent artificial-gravity audit

The OSD-255 panel was mapped to OSD-758 by version-stripped Ensembl identifiers. Transferability was evaluated by Spearman correlation and directional concordance between OSD-255 flight-versus-ground effects and OSD-758 microgravity-versus-ground effects. Artificial-gravity attenuation was measured as the change in absolute effect relative to the microgravity condition and compared with non-panel genes. A strict candidate required concordant cross-mission behavior and a direct OSD-758 microgravity-versus-in-flight-1G association passing the prespecified FDR threshold.

### Ground-analogue attribution audit

OSD-758 microgravity-versus-in-flight-1G effects were compared with OSD-203 hindlimb-unloading effects. OSD-758 in-flight-1G-versus-ground effects were treated as a residual flight-associated contrast and compared with OSD-203 radiation effects. Correlations, direction tests and 10,000 deterministic equal-sized random-panel benchmarks were calculated in the common-gene universe. Benjamini-Hochberg correction was applied across the prespecified time-by-mechanism comparisons.

### Sample-level sensitivity audit

Ten prespecified contrasts were re-estimated from OSDR variance-stabilized expression matrices using group mean differences, Welch tests and Benjamini-Hochberg correction. Agreement with NASA log2 fold changes was evaluated by Spearman correlation and direction. Because the VST matrices were generated by the NASA workflow, this analysis is independent at the statistical-contrast stage but is not an independent FASTQ-to-count reprocessing.

### Count-level effect audit

Public STAR unnormalized gene-count matrices were normalized independently with DESeq-style median-of-ratios size factors calculated from genes having positive counts in every sample. Genes with a mean normalized count below 10 in the samples of a contrast were excluded. Unshrunken log2 ratios of group mean normalized counts were calculated with a 0.5 pseudocount and compared with NASA DESeq2 log2 fold changes by Spearman correlation and direction. This audit starts upstream of the VST matrices but does not reproduce DESeq2 dispersion estimation, hypothesis testing or fold-change shrinkage.

### Functional enrichment

Three Gene Ontology Biological Process analyses were prespecified: the OSD-255 discovery panel against the OSD-255 transcriptome universe; the seven-day radiation-concordant subset against the frozen panel; and the nine radiation-compatible candidates against the frozen panel. Public MGI annotations were propagated through `is_a` and `part_of` ancestors in the GO basic ontology, `NOT` annotations were excluded, one-sided Fisher tests were used, and Benjamini-Hochberg correction was applied separately within each analysis. RR-9 panel enrichment was treated as contextual reproduction because related pathway results had already been published.

### Retinal cell-class anchor context

The canonical anchors *Pde6a*, *Arr3*, *Vsx2*, *Pax6*, *Rbpms*, *Onecut1*, *Slc1a3*, *Gfap*, *Cd74*, *Pecam1*, *Pdgfrb* and *Rpe65* were taken directly from Figure 1E of Li et al. [9]. NASA-reported log2 fold changes and FDR values were extracted for OSD-255 flight versus ground, OSD-758 microgravity versus ground, OSD-758 in-flight 1G versus ground, and OSD-203 seven-day radiation versus control. The audit was descriptive and prespecified as non-deconvolution: no cell fractions, cell-of-origin assignments or cell-intrinsic effects were inferred.

### Imaging context

Seven endpoints were declared in code before testing. Space Flight and Ground Control groups were compared with Welch and Mann–Whitney tests, with FDR correction across endpoints. Hedges' g and uncertainty summaries were calculated. RNA-seq and microscopy accessions use opposite eyes and are therefore not treated as paired observations.

### Unpaired cross-modal synthesis

Four biological domains declared in the project scope—photoreceptor integrity, apoptosis, oxidative stress and vascular/barrier integrity—were assembled into a descriptive evidence matrix. Existing imaging Welch FDR values were retained without recalculation. Transcriptomic context was limited to the prespecified GO results and published atlas anchors. No cross-modal p-value, sample matching, mediation analysis or causal model was fitted.

## Results

### RR-9 does not define a stable universal gravity signature

All 362 OSD-255 discovery genes mapped to OSD-758. The OSD-255 and OSD-758 microgravity-versus-ground effects were not positively correlated (rho = -0.071, P = 0.180), and only 170/362 genes shared direction (47.0%; one-sided binomial P = 0.887). No gene met the strict gravity-sensitive candidate rule.

### Apparent panel attenuation is not panel-specific

Within-panel absolute effects decreased at 0.66G and 1G relative to microgravity. However, panel attenuation did not exceed the background distribution of non-panel genes at those gravity levels. This distinguishes a study-wide artificial-gravity response, already reported by Kremsky et al., from enrichment of the independently frozen RR-9 panel.

### A transient radiation-compatible component survives the benchmark

For the OSD-758 residual flight-associated contrast and OSD-203 seven-day radiation contrast, 229/362 genes shared direction and effect ranks were positively correlated (rho = 0.272). The panel-level rank correlation exceeded equal-sized random panels (10,000 permutations; empirical FDR = 0.0246). Nine genes—*Pias2*, *Rad54b*, *Gars1*, *Mtmr10*, *Snrnp70*, ENSMUSG00000113831, *Trpc1*, *Eef2* and *Stxbp1*—also passed the OSD-203 radiation gene-level FDR threshold and had concordant direction. The corresponding radiation pattern was absent at one and four months, precluding a stable attribution claim.

### Sample-level effects reproduce the direction and ranking of NASA effects

Across ten contrasts, VST mean differences and NASA log2 fold changes had Spearman correlations from 0.854 to 0.888 and directional agreement from 93.5% to 96.0%. For OSD-255 flight versus ground, rho was 0.863 and 22,261/23,459 nonzero effects (94.9%) shared direction. These results support technical consistency of the contrast definitions while retaining the limitation that both analyses depend on NASA-processed expression values.

### Independent count normalization supports effect-level consistency

Across the same ten contrasts, independently normalized STAR-count effects correlated with NASA effects at rho 0.799–0.873, with 82.3%–88.0% directional agreement after the mean-count filter. For OSD-255 flight versus ground, rho was 0.799 and 13,057/15,573 nonzero effects (83.8%) shared direction. This lower concordance relative to the VST audit is expected because the count audit uses unshrunken mean ratios rather than the complete DESeq2 model. The audit nevertheless shows that the principal effect ranking and direction are not created by reading the final differential-expression table alone.

### Functional analysis reproduces known RR-9 biology but does not validate a radiation pathway

Of 336 unique unambiguous panel symbols, 312 had mouse Biological Process annotations. Ninety-five terms passed FDR < 0.05 against the annotated transcriptome universe. Leading terms included response to abiotic stimulus, intracellular protein localization, response to light stimulus, protein folding and detection of light stimulus, broadly reproducing the biological context reported for RR-9. Among 209 symbol-resolved seven-day radiation-concordant genes, 194 were annotated, but no term passed FDR < 0.05 against the panel background. Eight of the nine candidates had unambiguous symbols and seven were annotated; no candidate-set term passed FDR < 0.05. These null subset results prevent a gene-level concordance signal from being promoted as a validated radiation-response pathway.

### Canonical cell-class anchors do not define a replicated cellular signature

All 12 Mouse Retina Cell Atlas anchors mapped in every tested contrast. In OSD-255, only *Arr3*, the canonical cone-photoreceptor anchor, passed FDR < 0.05 (log2 fold change = -0.301; FDR = 0.000480). No anchor passed FDR < 0.05 in OSD-758 microgravity versus ground, OSD-758 in-flight 1G versus ground or OSD-203 seven-day radiation versus control. Thus, the RR-9 cone-associated observation is consistent with the published photoreceptor context but does not constitute a replicated cell-class signature.

### Cross-modal convergence is confined to study-level photoreceptor context

PNA-positive cell density was lower in flight animals (difference = -326.5 cells/mm²; Hedges' g = -1.91; Welch FDR = 0.0242). Together with lower *Arr3* expression and enrichment of response to light stimulus, this formed the only study-level cross-modal contextual convergence. Total TUNEL density was higher in flight (difference = 73.1 reported density units; g = 3.50; FDR = 0.000810), but no direct transcriptomic apoptosis test had been prespecified, so this was classified as imaging-only evidence. Neither 4-HNE endpoint passed Welch FDR < 0.05; none of the three vascular/barrier endpoints passed, with PECAM closest to the boundary (FDR = 0.0501). The matrix does not imply that the transcriptomic and imaging changes occurred in the same animal, eye or causal pathway.

## Discussion

The principal scientific result is a failed transfer: an RR-9 retinal flight signature does not behave as a mission-independent gravity signature in OSD-758. This negative result matters because it constrains the biological interpretation of single-mission signatures and argues against promoting the 362 genes as universal biomarkers.

The seven-day radiation-compatible component is narrower and more defensible. It passed a transcriptome-background random-panel benchmark and produced a small candidate set, but it is time-specific, cross-study and observational. Radiation is therefore a compatible explanatory component, not an identified cause. The candidates should be frozen and evaluated in a prospective experiment or a genuinely independent mission before mechanistic interpretation.

The single-cell reference adds context without resolving the bulk-data limitation. The isolated *Arr3* result is compatible with the RR-9 photoreceptor findings, but its absence from the independent and analogue FDR results prevents promotion to a cross-mission cone signature. Distinguishing altered cone abundance from transcriptional regulation within cones would require exposure-matched single-cell or spatial data.

The cross-modal matrix further narrows the claims. Photoreceptor evidence is coherent across modalities at the domain level, whereas apoptosis is supported only by imaging and the oxidative and vascular/barrier domains remain below the corrected threshold. This separation prevents visually similar directions from being promoted to formal cross-modal associations.

The term digital twin is used here for an evidence-layered computational framework, not for an individualized or clinically validated physiological replica. Contemporary digital-twin methodology emphasizes verification, validation and uncertainty quantification as requirements tied to an explicit intended use [12–14]. RetinaCellTwin therefore exposes code/data verification, internal statistical audits, external cross-mission validation and uncertainty boundaries separately. The current framework does not predict SANS, human disease or astronaut outcomes. Its value is provenance, falsifiable transfer tests, uncertainty and explicit separation of empirical from hypothetical quantities.

## Limitations

1. Spaceflight is a combined exposure and cannot isolate a single causal factor.
2. The principal discovery and validation tests use NASA DESeq2 differential-expression results.
3. The VST and count audits re-estimate effects but do not independently align FASTQ files or reproduce the complete DESeq2 inferential model.
4. Bulk RNA-seq cannot assign responses to retinal cell types; a one-anchor-per-class audit does not estimate cell fractions or distinguish compositional from cell-intrinsic effects.
5. Imaging cohorts are small, accessions differ and cross-modal samples are not paired; the evidence matrix is descriptive and cannot estimate mediation or within-animal association.
6. Ground analogues incompletely reproduce orbital exposures.
7. Mouse findings do not directly establish human clinical risk.

## Reproducibility and software availability

Source code, manifests, tests and frozen derived outputs are available in the immutable v0.3.0 release at <https://github.com/lissandrakruse/RetinaCellTwin>. The archival DOI will be inserted after the Zenodo deposit is minted. Public inputs are retrieved from NASA OSDR by accession and verified with SHA-256 checksums. The release package includes an exact Python dependency lock, a Dockerfile, a single-command full workflow and continuous-integration release tests.

## Data availability

Source observations and processed matrices are available from NASA OSDR under OSD-203, OSD-255, OSD-557, OSD-568 and OSD-758. Compact derived results, workflow code and provenance records accompany the software release. Supporting data intended for peer review will be deposited according to GigaScience/GigaDB curation requirements before final submission.

## Declarations

### Ethics approval

This study is a secondary computational analysis of publicly available animal-study data. The original study ethics and animal-care approvals must be cited from the corresponding OSDR records and primary publications in the final manuscript.

### Competing interests

To be completed and approved by all authors.

### Funding

To be completed. Do not infer funding from institutional affiliation.

### Author contributions

To be completed using the CRediT taxonomy after the author list is confirmed. A non-approved verification worksheet is provided in `CREDIT_CONTRIBUTIONS_DRAFT.md`; no proposed role should be treated as final without the contributor's confirmation.

### Use of artificial intelligence tools

During development of this manuscript and its software package, OpenAI ChatGPT with Codex was used to assist with literature discovery, code and documentation drafting, organization of the manuscript, and English-language editing. It was not treated as an author or contributor and did not supply empirical observations. Numerical results were generated from the cited public datasets by the versioned scripts and verification tests. Before submission, the named human authors must verify the complete manuscript, code, citations and numerical claims, approve this disclosure and accept full responsibility for the work. The persistent location of the AI-use output record remains to be inserted after preparation of the required supplement.

## References

1. Yang JW, et al. Spaceflight-associated neuro-ocular syndrome: a review of potential pathogenesis and intervention. 2022. <https://doi.org/10.18240/ijo.2022.02.21>.
2. Martin Paez Y, et al. Spaceflight associated neuro-ocular syndrome (SANS): a systematic review and future directions. 2020. <https://doi.org/10.2147/EB.S234076>.
3. Overbey EG, et al. Spaceflight influences gene expression, photoreceptor integrity, and oxidative stress-related damage in the murine retina. *Scientific Reports*. 2019. <https://doi.org/10.1038/s41598-019-49453-x>.
4. Mao X, et al. Evidence of Spaceflight-Induced Adverse Effects on Photoreceptors and Retinal Function in the Mouse Eye. 2023. <https://doi.org/10.3390/ijms24087362>.
5. Mao XW, et al. Impact of Spaceflight and Artificial Gravity on the Mouse Retina: Biochemical and Proteomic Analysis. 2018. <https://doi.org/10.3390/ijms19092546>.
6. Kremsky I, et al. Artificial Gravity Attenuates the Transcriptomic Response to Spaceflight in the Optic Nerve and Retina. 2024. <https://doi.org/10.3390/ijms252212041>.
7. Kothiyal P, et al. A multi-omics longitudinal study of the murine retinal response to chronic low-dose irradiation and/or simulated microgravity. 2022. <https://doi.org/10.1038/s41598-022-19360-9>.
8. Casaletto JA, et al. Machine learning ensemble reveals distinct molecular pathways of retinal damage in spaceflown mice. 2026. <https://doi.org/10.1038/s41526-026-00625-w>.
9. Li J, et al. Comprehensive single-cell atlas of the mouse retina. *iScience*. 2024. <https://doi.org/10.1016/j.isci.2024.109916>.
10. Benjamini Y, Hochberg Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. 1995. <https://doi.org/10.1111/j.2517-6161.1995.tb02031.x>.
11. Hedges LV. Distribution theory for Glass's estimator of effect size and related estimators. 1981. <https://doi.org/10.3102/10769986006002107>.
12. Corral-Acero J, et al. The 'Digital Twin' to enable the vision of precision cardiology. 2020. <https://doi.org/10.1016/j.molmed.2020.04.009>.
13. National Academies of Sciences, Engineering, and Medicine. *Foundational Research Gaps and Future Directions for Digital Twins*. 2024. <https://doi.org/10.17226/26894>.
14. Sel K, et al. Survey and perspective on verification, validation, and uncertainty quantification of digital twins for precision medicine. 2025. <https://doi.org/10.1038/s41746-025-01447-y>.
