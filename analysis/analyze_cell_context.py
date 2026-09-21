#!/usr/bin/env python3
"""Audit published retinal cell-class anchor genes in bulk OSDR contrasts.

This deliberately does not deconvolve cell fractions or assign a bulk response
to a cell type. The 12 anchors are the canonical major-class genes shown in
Figure 1E of the Mouse Retina Cell Atlas (Li et al., 2024).
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from config import DATA_DIR, RESULTS_DIR, require


OSD255_FILE = "GLDS-255_rna_seq_differential_expression_GLbulkRNAseq.csv"
OSD758_FILE = "GLDS-664_rna_seq_differential_expression_GLbulkRNAseq.csv"
OSD203_FILE = "GLDS-203_rna_seq_differential_expression_GLbulkRNAseq.csv"

CONTRASTS = {
    "osd255_flight_vs_ground": (
        OSD255_FILE,
        "Log2fc_(Space Flight)v(Ground Control)",
        "Adj.p.value_(Space Flight)v(Ground Control)",
    ),
    "osd758_microgravity_vs_ground": (
        OSD758_FILE,
        "Log2fc_(Space Flight & uG)v(Ground Control & 1G on Earth)",
        "Adj.p.value_(Space Flight & uG)v(Ground Control & 1G on Earth)",
    ),
    "osd758_inflight_1g_vs_ground": (
        OSD758_FILE,
        "Log2fc_(Space Flight & 1G by centrifugation)v(Ground Control & 1G on Earth)",
        "Adj.p.value_(Space Flight & 1G by centrifugation)v(Ground Control & 1G on Earth)",
    ),
    "osd203_7d_radiation_vs_control": (
        OSD203_FILE,
        "Log2fc_(7 day & cobalt-57 gamma radiation & Normally Loaded Control)v(7 day & non-irradiated & Normally Loaded Control)",
        "Adj.p.value_(7 day & cobalt-57 gamma radiation & Normally Loaded Control)v(7 day & non-irradiated & Normally Loaded Control)",
    ),
}


def main() -> None:
    anchors = pd.read_csv(
        require(DATA_DIR / "retinal_cell_anchors.tsv", "retinal cell anchors"), sep="\t"
    )
    result = anchors.copy()

    for label, (filename, effect_col, fdr_col) in CONTRASTS.items():
        frame = pd.read_csv(
            require(DATA_DIR / filename, label),
            usecols=["ENSEMBL", "SYMBOL", effect_col, fdr_col],
            low_memory=False,
        )
        frame = frame.drop_duplicates("SYMBOL").set_index("SYMBOL")
        result[f"{label}_gene_id"] = result["marker_symbol"].map(frame["ENSEMBL"])
        result[f"{label}_log2fc"] = pd.to_numeric(
            result["marker_symbol"].map(frame[effect_col]), errors="coerce"
        )
        result[f"{label}_fdr"] = pd.to_numeric(
            result["marker_symbol"].map(frame[fdr_col]), errors="coerce"
        )

    result.to_csv(RESULTS_DIR / "cell_class_anchor_audit.csv", index=False)

    summaries = []
    for label in CONTRASTS:
        fdr = result[f"{label}_fdr"]
        effect = result[f"{label}_log2fc"]
        significant = result.loc[fdr < 0.05, ["cell_class", "marker_symbol"]]
        summaries.append(
            {
                "contrast": label,
                "anchors_mapped": int(effect.notna().sum()),
                "anchors_with_reported_fdr": int(fdr.notna().sum()),
                "anchors_fdr_below_0_05": int((fdr < 0.05).sum()),
                "significant_anchors": [
                    {"cell_class": row.cell_class, "marker_symbol": row.marker_symbol}
                    for row in significant.itertuples(index=False)
                ],
            }
        )

    payload = {
        "project": "RetinaCellTwin",
        "analysis": "Published retinal cell-class anchor audit in bulk RNA-seq",
        "anchor_source": {
            "citation": "Li et al. Comprehensive single-cell atlas of the mouse retina. iScience (2024)",
            "doi": "10.1016/j.isci.2024.109916",
            "evidence_location": "Figure 1E",
            "atlas_scope": "more than 330,000 cells; 12 major classes; 138 cell types",
        },
        "summaries": summaries,
        "interpretation_boundary": (
            "These single canonical anchors provide cell-class context only. Bulk RNA-seq "
            "cannot distinguish regulation within a cell class from changes in cellular "
            "composition, and one marker per class is not a deconvolution signature."
        ),
    }
    (RESULTS_DIR / "cell_class_anchor_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
