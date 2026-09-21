# Data inputs

Run `python analysis/fetch_open_data.py` to retrieve the selected open tables from NASA OSDR.

The fetcher:

- resolves each filename through the official OSDR Biological Data API;
- refuses files marked restricted or invisible;
- saves sample-level spaceflight-factor metadata for each accession;
- retrieves prespecified VST matrices and STAR unnormalized gene counts used for the two sensitivity audits;
- records the source URL, API record, byte count, SHA-256 checksum and UTC retrieval time in `provenance.json`.

Downloaded inputs are excluded from Git by default because NASA OSDR is the authoritative source. The manifest `datasets.json`, workflow and derived results are versioned.

Do not infer experimental groups from filenames when metadata are available. The analysis joins measurements to the OSDR sample-level factor table.

Run `python analysis/fetch_functional_data.py` to retrieve the Gene Ontology basic ontology and MGI mouse annotations declared in `functional_sources.json`. Expected sizes and SHA-256 checksums are frozen in that manifest; the fetcher refuses silent drift. Verification is recorded separately in `functional_provenance.json`. These downloaded annotation files are excluded from Git and remain governed by their source terms.

`retinal_cell_anchors.tsv` is a small, versioned literature-derived reference, not an OSDR observation. It freezes the 12 canonical major-class genes displayed in Figure 1E of Li et al., *Comprehensive single-cell atlas of the mouse retina* ([doi:10.1016/j.isci.2024.109916](https://doi.org/10.1016/j.isci.2024.109916)). The file is used only for a descriptive bulk-RNA-seq anchor audit and must not be interpreted as a deconvolution signature.
