#!/usr/bin/env python3
"""Build a descriptive, explicitly unpaired cross-modal evidence matrix."""

from __future__ import annotations

import json

import pandas as pd

from config import RESULTS_DIR, require


DOMAINS = [
    {
        "domain": "Photoreceptor integrity",
        "imaging_endpoints": ["PNA-positive cell density"],
        "transcript_kind": "atlas anchor plus GO context",
    },
    {
        "domain": "Apoptosis",
        "imaging_endpoints": ["TUNEL density, total"],
        "transcript_kind": "no prespecified direct transcriptomic test",
    },
    {
        "domain": "Oxidative stress",
        "imaging_endpoints": [
            "4-HNE-positive cell density, retina",
            "4-HNE mean intensity, photoreceptor layer",
        ],
        "transcript_kind": "broad stress context only",
    },
    {
        "domain": "Vascular/barrier integrity",
        "imaging_endpoints": [
            "TUNEL density, endothelial cells",
            "PECAM mean signal",
            "ZO-1 mean signal",
        ],
        "transcript_kind": "endothelial canonical anchor",
    },
]


def main() -> None:
    imaging = pd.read_csv(require(RESULTS_DIR / "imaging_endpoints.csv", "imaging results"))
    anchors = pd.read_csv(
        require(RESULTS_DIR / "cell_class_anchor_audit.csv", "cell anchor results")
    )
    go = pd.read_csv(require(RESULTS_DIR / "go_enrichment.csv", "GO results"))

    rows = []
    for spec in DOMAINS:
        subset = imaging.loc[imaging["endpoint"].isin(spec["imaging_endpoints"])].copy()
        if len(subset) != len(spec["imaging_endpoints"]):
            missing = set(spec["imaging_endpoints"]) - set(subset["endpoint"])
            raise KeyError(f"Missing imaging endpoints for {spec['domain']}: {sorted(missing)}")

        significant = subset.loc[subset["welch_fdr"] < 0.05]
        imaging_status = "FDR-supported" if len(significant) else "not FDR-supported"
        imaging_detail = "; ".join(
            f"{row.endpoint}: difference={row.difference_flight_minus_ground:.3g}, "
            f"Hedges g={row.hedges_g:.3g}, Welch FDR={row.welch_fdr:.3g}"
            for row in subset.itertuples(index=False)
        )

        transcript_status = "not directly tested"
        transcript_detail = spec["transcript_kind"]
        integration = "no cross-modal convergence claim"

        if spec["domain"] == "Photoreceptor integrity":
            arr3 = anchors.loc[anchors["marker_symbol"] == "Arr3"].iloc[0]
            light = go.loc[
                (go["analysis"] == "OSD-255 discovery panel vs transcriptome")
                & (go["term"] == "response to light stimulus")
            ].iloc[0]
            transcript_status = "FDR-supported context"
            transcript_detail = (
                f"Arr3 log2FC={arr3.osd255_flight_vs_ground_log2fc:.3g}, "
                f"FDR={arr3.osd255_flight_vs_ground_fdr:.3g}; "
                f"GO response to light stimulus FDR={light.fdr:.3g}"
            )
            if len(significant):
                integration = "study-level contextual convergence"
        elif spec["domain"] == "Vascular/barrier integrity":
            pecam = anchors.loc[anchors["marker_symbol"] == "Pecam1"].iloc[0]
            transcript_status = "not FDR-supported"
            transcript_detail = (
                f"Pecam1 log2FC={pecam.osd255_flight_vs_ground_log2fc:.3g}, "
                f"FDR={pecam.osd255_flight_vs_ground_fdr:.3g}"
            )
        elif spec["domain"] == "Oxidative stress":
            transcript_status = "broad context only"
            transcript_detail = (
                "The RR-9 panel is enriched for response to abiotic stimulus, "
                "which is not a specific oxidative-stress test."
            )
        elif spec["domain"] == "Apoptosis" and len(significant):
            integration = "imaging-only FDR-supported evidence"

        rows.append(
            {
                "domain": spec["domain"],
                "imaging_status": imaging_status,
                "imaging_endpoints_n": int(len(subset)),
                "imaging_endpoints_fdr_below_0_05": int(len(significant)),
                "minimum_welch_fdr": float(subset["welch_fdr"].min()),
                "imaging_detail": imaging_detail,
                "transcript_status": transcript_status,
                "transcript_detail": transcript_detail,
                "integration_classification": integration,
            }
        )

    table = pd.DataFrame(rows)
    table.to_csv(RESULTS_DIR / "cross_modal_context.csv", index=False)
    payload = {
        "project": "RetinaCellTwin",
        "analysis": "Descriptive unpaired cross-modal evidence matrix",
        "domains_declared": [row["domain"] for row in DOMAINS],
        "multiple_testing": (
            "No new cross-modal hypothesis test was performed. Imaging FDR values are "
            "the existing Benjamini-Hochberg results across seven prespecified endpoints."
        ),
        "rows": rows,
        "interpretation_boundary": (
            "The RNA-seq and imaging data come from different accessions and opposite eyes. "
            "Convergence is study-level context, not sample pairing, mediation, mechanism or causality."
        ),
    }
    (RESULTS_DIR / "cross_modal_context.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
