# Derived results

Run:

```bash
python analysis/fetch_open_data.py
python analysis/analyze_open_data.py
python analysis/analyze_gravity_hypothesis.py
python analysis/analyze_sample_level_audit.py
python analysis/analyze_count_level_audit.py
python analysis/fetch_functional_data.py
python analysis/analyze_go_enrichment.py
python analysis/analyze_cell_context.py
python analysis/analyze_cross_modal_context.py
python analysis/make_figures.py
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
- `sample_level_audit.json`: concordance between sample-level VST contrasts and NASA differential-expression effects.
- `sample_level_audit_top_genes.csv`: top 50 genes by Welch FDR for each audited contrast.
- `count_level_audit.json`: agreement between independently normalized STAR-count effects and NASA DESeq2 effects.
- `count_level_audit_top_genes.csv`: top 100 absolute count-derived effects for each audited contrast.
- `go_enrichment.json`: prespecified GO analysis metadata and significant-term counts.
- `go_enrichment.csv`: up to 100 ranked GO terms for each prespecified analysis.
- `cell_class_anchor_audit.json`: mapped-anchor counts and FDR decisions for four bulk RNA-seq contrasts.
- `cell_class_anchor_audit.csv`: effect sizes and NASA-reported FDR values for the 12 published major-class anchors.
- `cross_modal_context.json`: machine-readable, explicitly unpaired synthesis across four prespecified biological domains.
- `cross_modal_context.csv`: compact evidence matrix linking existing imaging FDR results to bounded transcriptomic context without a new cross-modal hypothesis test.

These are derived results, not source observations. Their provenance traces back to `data/provenance.json`.
