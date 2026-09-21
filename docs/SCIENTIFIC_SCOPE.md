# Scientific scope and claim boundaries

## Question for the v0.3 Oxford-candidate workflow

Which transcriptomic and image-derived retinal phenotypes differ between RR-9 spaceflight animals and matched ground controls, and which signals are sufficiently reproducible to justify prospective mechanistic work?

## Evidence architecture

### Observed layer

- OSD-255 right-retina bulk RNA-seq.
- OSD-557 left-eye transformed measurements for 4-HNE and PNA staining.
- OSD-568 left-eye transformed measurements for TUNEL, PECAM and ZO-1.
- OSD-758 retinal bulk RNA-seq across microgravity and three in-flight centrifugation levels.
- OSD-203 retinal bulk RNA-seq after low-dose gamma irradiation and/or hindlimb unloading at three times.

### Derived layer

- NASA-reported gene-level differential-expression statistics are summarized without re-estimating them from normalized values.
- Seven imaging endpoints are declared in code before comparison.
- Space Flight is compared with Ground Control. Other cohort controls remain available for sensitivity analyses but are not silently pooled.
- Any transformed-table sample missing an API factor label is excluded rather than assigned from its filename; the exclusion is reported in the output table.
- Both Welch and Mann-Whitney p-values are reported; false-discovery-rate correction is applied across the seven endpoints.
- The OSD-255 FDR < 0.05 set (362 genes) is fixed before testing OSD-758 or OSD-203.
- OSD-758 attenuation within that panel is compared with all non-panel genes rather than interpreted in isolation.
- OSD-203 concordance is benchmarked against 10,000 equal-sized random panels from the common-gene universe with a fixed seed.
- VST and independently normalized STAR-count effects are compared with NASA differential-expression effects across ten prespecified contrasts.
- GO Biological Process context uses versioned public ontology and mouse annotations.
- Twelve canonical major-class anchors from the Mouse Retina Cell Atlas are audited descriptively across four bulk contrasts; they are not used for deconvolution.
- Four declared biological domains are synthesized in an unpaired evidence matrix using existing FDR results; no new cross-modal test or sample pairing is introduced.

### Hypothesis layer

Potential links among oxidative stress, photoreceptor integrity, apoptosis and blood-retinal-barrier changes are hypotheses for future testing. A later model may generate synthetic data, but synthetic records must be visibly separated from OSDR observations.

The stable universal-gravity-signature hypothesis was not supported. A narrower seven-day radiation-compatible signal passed the random-panel enrichment test (empirical FDR 0.0246), but its absence at later times prevents a stable attribution claim.

### Probabilistic twin layer

- The interface computes an approximate sampling variance for Hedges' *g* and a reference-posterior probability of direction under an explicitly stated flat prior and Normal approximation.
- The displayed 95% interval and probability of direction quantify uncertainty about a group-difference effect size; neither is a probability of disease, retinal damage, mechanism or causation.
- Robust VOI is evaluated across the complete user-entered interval pL…pU. Sensitivity, specificity, benefit, loss and study cost are scenario assumptions, not OSDR-derived parameters.
- The research-plan optimizer is a 0–1 knapsack model. Costs and information values are user inputs, and the result is a conditional decision aid rather than an empirical scientific finding.

## Important limitations

1. Spaceflight combines altered gravity, radiation, launch/re-entry, habitat and operational exposures.
2. Bulk RNA-seq cannot assign expression changes to retinal cell types. The canonical-anchor audit does not estimate cell fractions or distinguish composition from cell-intrinsic regulation.
3. The transcriptomic and imaging accessions do not justify sample-level cross-modal pairing.
4. Small imaging cohorts limit power and effect-size precision.
5. Mouse results do not directly establish human clinical risk.
6. A digital-twin label describes the intended layered computational framework, not a validated individual-level physiological replica.
7. Artificial-gravity attenuation in OSD-758 was already reported by Kremsky et al.; the present contribution is an independent panel-transfer audit, not rediscovery of that effect.
8. OSD-203 analog exposures cannot reproduce the full orbital environment, and cross-dataset concordance cannot establish causation.

## Prospective validation path

- Freeze the v0.3 analysis and archive checksums.
- Reprocess OSD-255 with a locked DESeq2/edgeR inferential workflow or from FASTQ when resources permit.
- Extend the contextual anchor audit to a validated mouse-retina deconvolution reference only if its assumptions and platform harmonization can be justified.
- Evaluate robustness across control cohorts.
- Prospectively test the nine seven-day radiation-compatible candidates without reselecting them.
- Validate prioritized signals experimentally or in an independent mission.
