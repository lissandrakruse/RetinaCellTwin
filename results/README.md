# Derived results

Run:

```bash
python analysis/fetch_open_data.py
python analysis/analyze_open_data.py
python analysis/analyze_gravity_hypothesis.py
```

Expected outputs:

- `summary.json`: machine-readable project summary and claim boundaries.
- `osd255_top_genes.csv`: top 100 genes ranked from the NASA-processed OSD-255 table.
- `imaging_endpoints.csv`: seven prespecified imaging comparisons.
- `gravity_hypothesis.json`: cross-mission tests, background benchmarks and explicit hypothesis decisions.
- `gravity_validation_genes.csv`: all 362 frozen RR-9 panel genes mapped to OSD-758.
- `osd758_direct_gravity_genes.csv`: OSD-758 uG-versus-in-flight-1G genes at NASA FDR < 0.05.
- `osd203_attribution.csv`: time-resolved concordance and random-panel enrichment tests.
- `osd203_7d_radiation_candidates.csv`: post-audit candidate list requiring prospective validation.

These are derived results, not source observations. Their provenance traces back to `data/provenance.json`.
