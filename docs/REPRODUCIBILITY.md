# Reproducibility contract

RetinaCellTwin separates source retrieval, deterministic analysis and release verification. The intended clean-room command is:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --requirement requirements-lock.txt
bash run_all.sh
```

The workflow retrieves the public OSDR inputs declared in `data/datasets.json`, checks OSDR visibility restrictions, and records URLs, sizes, retrieval times and SHA-256 digests in `data/provenance.json`. Gene Ontology inputs are frozen by both byte count and SHA-256 in `data/functional_sources.json`; the fetcher refuses silent source drift.

`run_all.sh` then regenerates the core RR-9 summary, cross-mission transfer tests, ground-analogue audit, VST and STAR-count effect audits, GO enrichment, retinal cell-class anchor audit, unpaired cross-modal matrix and all publication figures. `run_verification.sh` checks required assets, scientific invariants, provenance hashes, Python syntax and SVG validity.

## Container execution

```bash
docker build -t retinacelltwin:0.3.0 .
docker run --rm retinacelltwin:0.3.0
```

The image runs release verification against the frozen repository outputs. To regenerate all source-derived outputs inside a container, mount a persistent data directory and invoke `bash run_all.sh`; network access to NASA OSDR and the frozen GO URLs is required.

## Reproducibility levels

| Level | Implemented check | Boundary |
| --- | --- | --- |
| Source integrity | Visibility checks, manifests, byte counts and SHA-256 | Upstream repositories can change or become unavailable |
| Statistical contrasts | Ten VST mean-difference/Welch audits | VST values were produced by NASA |
| Count effects | Independent median-of-ratios normalization from STAR counts | Not a full DESeq2 dispersion/p-value reproduction |
| External transfer | Frozen OSD-255 panel tested in OSD-758 without reselection | Missions are not exchangeable experiments |
| Mechanistic context | Time-resolved OSD-203 analogue comparisons and random-panel benchmarks | Concordance is not causal attribution |
| Biological context | Versioned GO analysis and published retinal-class anchors | Bulk RNA-seq remains unresolved at cell level |

The dependency lock was frozen and verified under Python 3.12.14, and the environment reported no broken Python requirements. A final release must repeat the container build and full workflow from a clean clone before DOI deposition.
