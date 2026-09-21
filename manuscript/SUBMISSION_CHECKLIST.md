# GigaScience submission checklist

Verified against the journal webpages on 2026-09-20. This is a working checklist, not evidence that the authors have approved submission.

## Journal fit and submission route

- [x] Target journal: **GigaScience**.
- [x] Proposed article type: **Research Article**.
- [x] Proposed collection: **Data-Driven Multicellular Systems Biology**.
- [x] Cover letter explicitly names the thematic series, as requested by the [call for papers](https://academic.oup.com/gigascience/pages/multicellular_cfp).
- [ ] Confirm in the live Editorial Manager form that the Research Article and thematic-series choices remain available on the submission date.

## Manuscript and reporting

- [x] Exact sample sizes, group identities and exclusions are recorded in the generated results and supplementary methods.
- [x] Statistical tests state sidedness, multiple-testing correction and effect-size definitions.
- [x] For imaging groups with n < 6, machine-readable source values are preserved and the deterministic figures expose the underlying endpoint summaries. Confirm whether the final figure format should additionally plot every individual observation.
- [x] Biological and technical replication boundaries are stated.
- [x] Software, database and package versions are captured in `requirements-lock.txt`, `environment.yml` and the container definition.
- [x] Data Availability section lists every OSDR accession.
- [x] Code uses an OSI-approved MIT licence.
- [x] Current and archived software links have designated locations in the manuscript.
- [x] Freeze the v0.3.0 software package and prepare its GitHub release for Zenodo archiving.
- [ ] Insert the immutable Zenodo DOI after it is minted.
- [ ] Coordinate the supporting-data package with GigaDB during editorial curation.
- [ ] Consider registering the complete workflow in WorkflowHub; GigaScience recommends workflow registration and DOI citation.

The applicable official requirements are the [Minimum Standards of Reporting Checklist](https://academic.oup.com/gigascience/pages/Minimum_Standards_of_Reporting_Checklist) and [Editorial Policies and Reporting Standards](https://academic.oup.com/gigascience/pages/editorial_policies_and_reporting_standards).

## Reproducibility package

- [x] One-command workflow: `bash run_all.sh`.
- [x] Exact Python lock and Conda environment.
- [x] Dockerfile and continuous-integration verification.
- [x] Public input provenance, byte counts and SHA-256 checksums.
- [x] Frozen derived CSV/JSON results.
- [x] Six deterministic SVG figures.
- [x] Automated scientific-invariant, syntax and SVG tests.
- [ ] Execute and record one clean container build before release.
- [ ] Rerun the final tagged commit in a clean environment and preserve the verification log.
- [ ] Confirm that every URL and DOI resolves from outside the development environment.

## Claim control

- [x] The failed universal-gravity-signature transfer is reported as a negative result.
- [x] The seven-day radiation-compatible signal is described as transient, cross-study and non-causal.
- [x] Cell-atlas anchors are contextual and are not used for deconvolution or cell-of-origin claims.
- [x] Imaging and RNA-seq are explicitly unpaired.
- [x] Photoreceptor evidence is limited to study-level contextual convergence.
- [x] Apoptosis is labelled imaging-only because no direct transcriptomic apoptosis test was prespecified.
- [x] Oxidative-stress and vascular/barrier imaging domains are labelled not FDR-supported.
- [x] No human SANS prediction or clinical claim is made.

## Authorship and declarations — blocking before submission

- [ ] Every listed author meets all four ICMJE authorship criteria described in the journal's [Authorship Guidelines](https://academic.oup.com/gigascience/pages/authorship_guidelines).
- [ ] Final author list and order are approved by every author.
- [ ] Corresponding author is confirmed and agrees to remain responsive throughout review.
- [ ] CRediT roles are fact-checked and approved using `CREDIT_CONTRIBUTIONS_DRAFT.md`.
- [ ] Every author has read and approved the exact submitted manuscript.
- [ ] Competing-interest declaration is completed for every author.
- [ ] Funding and grant identifiers are completed without inferring support from affiliation.
- [ ] The manuscript is not under consideration elsewhere; disclose related manuscripts, abstracts, preprints or overlapping text.
- [ ] Original animal-study approvals are cited accurately from the source studies; the secondary-analysis status is retained.

## AI-use transparency — blocking before submission

- [x] AI is not listed as an author or CRediT contributor.
- [x] A conservative disclosure draft exists in `AI_DISCLOSURE_DRAFT.md`.
- [ ] The human authors verify every citation, numerical statement, analysis choice and generated-code path.
- [ ] Export or otherwise preserve the relevant AI interaction outputs required by the journal and deposit them as a supplement or in an open repository.
- [ ] Replace all disclosure placeholders with exact tool names, versions/models where available, dates, purposes and a persistent supplement link.
- [ ] All authors approve the final disclosure and accept responsibility for the work.

GigaScience currently permits generative AI writing assistance only with transparent disclosure, human accountability and an end-of-paper summary; its policy also requests that relevant outputs be made available as supplementary material. See [Editorial Policies: Use of AI Tools and Technologies in Writing](https://academic.oup.com/gigascience/pages/editorial_policies_and_reporting_standards).

## Files for the portal

- [x] Review-formatted editable Word draft generated from the versioned manuscript source.
- [ ] Finalize declarations and obtain author approval for the exact submitted Word file.
- [ ] Cover letter, after replacing every bracketed item.
- [ ] Main figures 1–6 in the required production format and resolution.
- [ ] Figure legends embedded in or supplied with the manuscript as instructed.
- [ ] Supplementary Methods.
- [ ] Machine-readable supplementary tables/results.
- [ ] AI-use supplement and disclosure, if applicable.
- [ ] Suggested reviewers only after checking expertise, independence and conflicts; do not invent names.
- [ ] ORCID, affiliation and contact details verified for each author.

## Release order

1. Resolve authorship, corresponding-author, declaration and AI-log blockers.
2. Freeze code and results; execute clean-room and container verification.
3. Tag v0.3.0 and archive the exact release with a persistent DOI.
4. Update the manuscript's software citation and Data Availability statement with that DOI.
5. Obtain final written approval from every author.
6. Submit through the current GigaScience Editorial Manager route.
