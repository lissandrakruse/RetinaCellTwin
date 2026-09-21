# RetinaCellTwin

**An open, NASA OSDR-grounded framework for multimodal analysis of spaceflight-associated retinal responses in mice.**

RetinaCellTwin is a research prototype inspired by the reproducible architecture of PlantCellTwin. It integrates openly accessible transcriptomic and imaging-derived measurements from the Rodent Research-9 (RR-9) mission while keeping three evidence layers separate:

1. **Observed data** downloaded from NASA OSDR.
2. **Derived statistics** calculated by the versioned workflow in this repository.
3. **Hypotheses and future simulations**, which are not treated as empirical observations.

The current version is a cross-mission analysis framework, not a physiological, clinical, or causal digital twin.

The interactive interface now includes a transparent probabilistic layer. For each imaging endpoint it derives an approximate reference posterior for Hedges' *g* (flat prior and Normal sampling approximation), reports the probability of the observed effect direction and preserves the Welch/Mann-Whitney FDR results alongside it. This is a probability about the direction of a group difference—not the probability of disease, damage, mechanism or causality.

The decision layer implements two scenario tools inspired by the earlier Rocha workflow:

- robust expected value of sample information (EVSI) evaluated throughout a user-specified prior interval pL…pU;
- a transparent 0–1 integer research-portfolio solver that maximizes user-declared information value under a budget.

All probabilities, utilities and costs entered in these scenario tools are visibly identified as user inputs rather than NASA observations.

## Resumo em português

O projeto combina dados públicos de retina de camundongos da missão RR-9. A primeira versão usa RNA-seq para estudar alterações de expressão gênica e tabelas derivadas de microscopia para avaliar dano oxidativo, integridade de fotorreceptores, apoptose e marcadores da barreira retiniana. Todas as entradas vêm do repositório aberto NASA OSDR e cada arquivo baixado recebe checksum SHA-256.

## Open evidence base

| Dataset | Material and modality | Role in the Oxford-candidate workflow |
| --- | --- | --- |
| [OSD-255](https://osdr.nasa.gov/bio/repo/data/studies/OSD-255) | Right retina; bulk RNA-seq | Transcriptomic discovery |
| [OSD-557](https://osdr.nasa.gov/bio/repo/data/studies/OSD-557) | Left eye; microscopy, 4-HNE and PNA immunostaining | Oxidative-stress and photoreceptor context |
| [OSD-568](https://osdr.nasa.gov/bio/repo/data/studies/OSD-568) | Left eye; microscopy, TUNEL, PECAM and ZO-1 | Apoptosis and blood-retinal-barrier context |
| [OSD-758](https://osdr.nasa.gov/bio/repo/data/studies/OSD-758) | Retina RNA-seq; uG, 0.33G, 0.66G and 1G in flight | Independent artificial-gravity audit |
| [OSD-203](https://osdr.nasa.gov/bio/repo/data/studies/OSD-203) | Retina RNA-seq; low-dose gamma radiation and hindlimb unloading | Time-resolved ground-analog attribution |

The selected inputs are public files marked `restricted: false` by the OSDR Biological Data API. Raw images remain at NASA; this repository downloads compact transformed tables and the processed RNA-seq differential-expression table.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python analysis/fetch_open_data.py
python analysis/fetch_functional_data.py
python analysis/analyze_open_data.py
python analysis/analyze_gravity_hypothesis.py
python analysis/analyze_sample_level_audit.py
python analysis/analyze_count_level_audit.py
python analysis/analyze_go_enrichment.py
python analysis/analyze_cell_context.py
python analysis/analyze_cross_modal_context.py
python analysis/make_figures.py
bash run_verification.sh
python -m http.server 8000
```

Open `http://localhost:8000` after the analysis finishes.

For an exact rerun, install `requirements-lock.txt` and execute `bash run_all.sh`. A
container definition and a continuous-integration release check are also included.

To keep data elsewhere, set `RCT_DATA_DIR` and optionally `RCT_RESULTS_DIR`.

## What the workflow calculates

- NASA-processed OSD-255 flight-versus-ground differential-expression summary.
- A ranked table of genes using the NASA-reported adjusted p-values and log2 fold changes.
- Seven prespecified imaging endpoints from OSD-557 and OSD-568.
- Flight-versus-ground effect estimates, Welch tests, Mann-Whitney tests and Benjamini-Hochberg corrections across imaging endpoints.
- A machine-readable provenance record containing download URLs, sizes, SHA-256 checksums and retrieval timestamps.
- Explicit reporting of transformed-table samples that lack a matching factor label in the API; no experimental group is guessed from a filename.
- A frozen 362-gene OSD-255 discovery panel tested in OSD-758 without reselection.
- Panel-versus-transcriptome benchmarks for apparent artificial-gravity attenuation.
- OSD-203 radiation and hindlimb-unloading concordance at 7 days, 1 month and 4 months.
- A deterministic 10,000-random-panel test asking whether analog concordance exceeds the common-gene background.
- A sample-level sensitivity audit that recomputes ten prespecified contrasts from public VST matrices and compares their ranks and directions with NASA log2 fold changes.
- An upstream count-level audit that independently estimates median-of-ratios size factors and unshrunken effects from public STAR gene counts.
- Three prespecified Gene Ontology Biological Process analyses using versioned MGI/GO inputs and within-analysis FDR control.
- A bounded cell-class context audit using the 12 canonical major-class anchors shown in Figure 1E of the Mouse Retina Cell Atlas; this is explicitly not deconvolution.
- An explicitly unpaired cross-modal evidence matrix across photoreceptor, apoptosis, oxidative-stress and vascular/barrier domains, with no new cross-modal hypothesis test.

The imaging analysis is exploratory. Small sample sizes, multiple control cohorts and modality-specific sample availability require cautious interpretation.

## Cross-mission hypothesis decision

The original broad hypothesis was **not supported as a stable universal signature**. The 362 OSD-255 genes did not reproduce in OSD-758 uG versus ground (Spearman rho = -0.071; 170/362 genes in the same direction), and no gene met the strict prespecified gravity-sensitive candidate rule. Artificial-gravity attenuation at 0.66G and 1G was visible within the panel but was not stronger than the transcriptome background.

A narrower prospective hypothesis survived: the OSD-758 residual flight-associated effect (in-flight 1G versus ground) was concordant with the OSD-203 seven-day radiation effect in 229/362 genes (Spearman rho = 0.272). This concordance exceeded 10,000 equally sized random-gene panels after correction (empirical FDR = 0.0246). Nine panel genes also had OSD-203 radiation FDR < 0.05 and concordant direction. The pattern did not persist at one or four months, so it is interpreted as a **time-specific radiation-compatible signal**, not causal attribution.

The new sample-level audit supports technical consistency without overstating independence. Across ten prespecified contrasts, VST mean differences agreed strongly with NASA log2 fold changes (Spearman rho 0.854–0.888; direction agreement 93.5%–96.0%). For OSD-255 flight versus ground, rho was 0.863 with 94.9% directional agreement. Because these VST matrices were produced by the NASA pipeline, this is an independent statistical-contrast audit, not an independent FASTQ-to-count reprocessing.

The count-level audit starts from unnormalized STAR gene counts and independently recomputes normalization and effect direction. Across ten contrasts, count-derived effects correlated with NASA effects at rho 0.799–0.873, with 82.3%–88.0% directional agreement. It does not reproduce DESeq2 dispersion modelling or inferential p-values and is labelled as an effect-level audit rather than a DESeq2 replacement.

The functional audit recapitulated known RR-9 biology: 95 Biological Process terms passed FDR < 0.05, led by response to abiotic stimulus, protein localization, light response and protein folding. Neither the 209 symbol-resolved seven-day radiation-concordant genes nor the eight symbol-resolved candidate genes produced a GO term passing FDR < 0.05 against the frozen RR-9 panel. This null result prevents the transient signal from being promoted as a validated pathway.

The cell-class context audit mapped all 12 canonical major-class anchors from the Mouse Retina Cell Atlas. Only the cone-photoreceptor anchor *Arr3* passed FDR < 0.05 in OSD-255; none of the anchors passed FDR in OSD-758 microgravity versus ground, OSD-758 in-flight 1G versus ground, or OSD-203 seven-day radiation versus control. This supports retinal context while withholding a cell-type attribution: one anchor per class and bulk RNA-seq cannot distinguish cell-intrinsic regulation from composition.

The formal cross-modal matrix found study-level contextual convergence only for photoreceptor integrity: PNA-positive density was lower in flight (Hedges' g = -1.91; Welch FDR = 0.0242), while *Arr3* was downregulated (FDR = 0.000480) and the discovery panel was enriched for response to light stimulus (FDR = 0.00248). Total TUNEL density supported an imaging-only apoptosis signal (g = 3.50; FDR = 0.000810). Oxidative-stress and vascular/barrier imaging endpoints did not pass the seven-endpoint Welch FDR boundary. These are study-level categories, not paired associations or mediation results.

Six deterministic SVG publication figures are generated from the frozen outputs; see [`figures/README.md`](figures/README.md).

## Manuscript package

The GigaScience-formatted review draft is available as
[`manuscript/RetinaCellTwin_GigaScience_Submission_Draft.docx`](manuscript/RetinaCellTwin_GigaScience_Submission_Draft.docx).
Its scientific source is
[`manuscript/GIGASCIENCE_RESEARCH_ARTICLE.md`](manuscript/GIGASCIENCE_RESEARCH_ARTICLE.md),
and the complete editorial checklist is in
[`manuscript/SUBMISSION_CHECKLIST.md`](manuscript/SUBMISSION_CHECKLIST.md).
The DOCX is a review-ready draft; authorship, funding, competing-interest and
AI-record declarations must be confirmed before journal submission.

Kremsky et al. previously established dose-dependent artificial-gravity attenuation in OSD-758. RetinaCellTwin does not claim that result as novel; its contribution is the independent RR-9 transferability test and explicit transcriptome-background/random-panel benchmarks.

## Scientific boundaries

- Spaceflight is a combined exposure; it does not isolate microgravity.
- The transcriptomic and imaging datasets use opposite eyes and are not assumed to be sample-paired across accessions.
- Cross-modal agreement does not establish mechanism or causality.
- Hindlimb unloading and low-dose gamma irradiation are imperfect analogs of the spaceflight environment.
- The seven-day radiation concordance is a dataset-level, time-specific hypothesis and not proof that radiation caused the flight response.
- No synthetic data are generated in the v0.3.0 release workflow.
- No clinical inference about human retinal disease is supported.
- Canonical single-cell-atlas anchors are contextual references, not inferred cell fractions or proof of a cell-of-origin.
- Cross-modal convergence is descriptive and study-level because the RNA-seq and imaging observations are neither accession-matched nor sample-paired.

## Methodological references

- Hedges LV. Distribution theory for Glass's estimator of effect size and related estimators. 1981. [doi:10.3102/10769986006002107](https://doi.org/10.3102/10769986006002107)
- Benjamini Y, Hochberg Y. Controlling the false discovery rate. 1995. [doi:10.1111/j.2517-6161.1995.tb02031.x](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x)
- Makowski D, et al. Indices of Effect Existence and Significance in the Bayesian Framework. 2019. [doi:10.3389/fpsyg.2019.02767](https://doi.org/10.3389/fpsyg.2019.02767)
- Strong M, et al. Estimating the Expected Value of Sample Information. 2015. [doi:10.1177/0272989X15575225](https://doi.org/10.1177/0272989X15575225)
- Corral-Acero J, et al. The 'Digital Twin' to enable the vision of precision cardiology. 2020. [doi:10.1016/j.molmed.2020.04.009](https://doi.org/10.1016/j.molmed.2020.04.009)
- Casaletto JA, et al. Machine learning ensemble reveals distinct molecular pathways of retinal damage in spaceflown mice. 2026. [PubMed 42399270](https://pubmed.ncbi.nlm.nih.gov/42399270/)
- Kremsky I, et al. Artificial Gravity Attenuates the Transcriptomic Response to Spaceflight in the Optic Nerve and Retina. 2024. [doi:10.3390/ijms252212041](https://doi.org/10.3390/ijms252212041)
- Kothiyal P, et al. A multi-omics longitudinal study of the murine retinal response to chronic low-dose irradiation and/or simulated microgravity. 2022. [doi:10.1038/s41598-022-19360-9](https://doi.org/10.1038/s41598-022-19360-9)
- Li J, et al. Comprehensive single-cell atlas of the mouse retina. 2024. [doi:10.1016/j.isci.2024.109916](https://doi.org/10.1016/j.isci.2024.109916)

See [`docs/SCIENTIFIC_SCOPE.md`](docs/SCIENTIFIC_SCOPE.md), [`docs/THEORETICAL_FOUNDATION.md`](docs/THEORETICAL_FOUNDATION.md) and [`docs/AWG_POSITIONING.md`](docs/AWG_POSITIONING.md).

Clean-room execution details are in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md), and the exact computational design is expanded in [`manuscript/SUPPLEMENTARY_METHODS.md`](manuscript/SUPPLEMENTARY_METHODS.md).

## Authors and status

- Lissandra Kruse Fuganti — ORCID [0009-0008-8189-112X](https://orcid.org/0009-0008-8189-112X), Universidade Estadual de Ponta Grossa

Status: **v0.3.0 open research release and GigaScience/Oxford research-article candidate**. Scientific outputs are frozen for this release, while the human-approval and declaration gates in [`docs/OXFORD_READINESS.md`](docs/OXFORD_READINESS.md) remain open. Additional contributors should be added only after confirming their role and authorship contribution.

## License

Source code is released under the MIT License. NASA OSDR source data remain governed by their repository terms and are not relicensed here.
