#!/usr/bin/env python3
"""Prespecified exploratory analysis of open RR-9 retina tables."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from config import DATA_DIR, RESULTS_DIR, require

DE_FILE = "GLDS-255_rna_seq_differential_expression_GLbulkRNAseq.csv"
FC = "Log2fc_(Space Flight)v(Ground Control)"
P_VALUE = "P.value_(Space Flight)v(Ground Control)"
FDR = "Adj.p.value_(Space Flight)v(Ground Control)"


@dataclass(frozen=True)
class Endpoint:
    dataset: str
    file: str
    metric: str
    label: str
    unit: str


ENDPOINTS = (
    Endpoint("OSD-557", "LSDS-1_immunostaining_Overbey_HNE_RetinaLayer_TRANSFORMED.csv", "hne_cell_density", "4-HNE-positive cell density, retina", "cells/mm²"),
    Endpoint("OSD-557", "LSDS-1_immunostaining_Overbey_HNE_PhotoreceptorLayer_TRANSFORMED.csv", "hne_mean_intensity_average", "4-HNE mean intensity, photoreceptor layer", "arbitrary intensity"),
    Endpoint("OSD-557", "LSDS-1_immunostaining_Overbey_PNA_TRANSFORMED.csv", "pna_cell_density", "PNA-positive cell density", "cells/mm²"),
    Endpoint("OSD-568", "LSDS-5_immunostaining_microscopy_TUNELtr_TRANSFORMED.csv", "Density", "TUNEL density, total", "reported density"),
    Endpoint("OSD-568", "LSDS-5_immunostaining_microscopy_TUNELtr_TRANSFORMED.csv", "Density_EC", "TUNEL density, endothelial cells", "reported density"),
    Endpoint("OSD-568", "LSDS-5_immunostaining_microscopy_PECAMtr_TRANSFORMED.csv", "Average", "PECAM mean signal", "reported intensity"),
    Endpoint("OSD-568", "LSDS-5_immunostaining_microscopy_Zo-1tr_TRANSFORMED.csv", "Average", "ZO-1 mean signal", "reported intensity"),
)


def bh(values: pd.Series) -> pd.Series:
    series = pd.to_numeric(values, errors="coerce")
    valid = series.dropna().sort_values()
    output = pd.Series(np.nan, index=series.index, dtype=float)
    if valid.empty:
        return output
    n = len(valid)
    raw = valid.to_numpy() * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(raw[::-1])[::-1]
    output.loc[valid.index] = np.clip(adjusted, 0, 1)
    return output


def clean_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(column).replace("\ufeff", "").strip() for column in frame.columns]
    return frame


def canonical_sample(value: object) -> str:
    sample = str(value).replace("\ufeff", "").strip()
    sample = re.sub(r"_Mouse_Eye$", "", sample, flags=re.IGNORECASE)
    # Sample identifiers are identifiers, not biological labels; normalizing
    # case prevents metadata joins from dropping entries such as Gc17 vs GC17.
    return sample.upper()


def metadata(accession: str) -> pd.DataFrame:
    path = require(DATA_DIR / f"{accession}_sample_metadata.csv", f"{accession} metadata")
    frame = clean_columns(pd.read_csv(path))
    factor_columns = [c for c in frame.columns if c.startswith("study.factor value.")]
    if not factor_columns:
        raise ValueError(f"No study factor found in {path.name}")
    out = frame[["id.sample name", factor_columns[0]]].rename(
        columns={"id.sample name": "sample", factor_columns[0]: "group"}
    )
    out["sample"] = out["sample"].map(canonical_sample)
    conflicts = out.groupby("sample")["group"].nunique()
    if (conflicts > 1).any():
        raise ValueError(f"Conflicting group labels in {accession} metadata")
    return out.drop_duplicates("sample")


def hedges_g(flight: np.ndarray, ground: np.ndarray) -> float:
    n1, n0 = len(flight), len(ground)
    if n1 < 2 or n0 < 2:
        return float("nan")
    pooled_df = n1 + n0 - 2
    pooled = math.sqrt(
        ((n1 - 1) * np.var(flight, ddof=1) + (n0 - 1) * np.var(ground, ddof=1))
        / pooled_df
    )
    if pooled == 0:
        return float("nan")
    correction = 1 - 3 / (4 * (n1 + n0) - 9)
    return correction * (np.mean(flight) - np.mean(ground)) / pooled


def analyze_transcriptomics() -> dict:
    frame = clean_columns(pd.read_csv(require(DATA_DIR / DE_FILE, "OSD-255 DE table"), low_memory=False))
    needed = {"ENSEMBL", "SYMBOL", "GENENAME", FC, P_VALUE, FDR}
    missing = sorted(needed - set(frame.columns))
    if missing:
        raise ValueError(f"Missing OSD-255 columns: {missing}")
    for column in (FC, P_VALUE, FDR):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    tested = frame[frame[P_VALUE].notna()].copy()
    ranked = tested.sort_values([FDR, P_VALUE, FC], ascending=[True, True, False], na_position="last")
    top = ranked[["ENSEMBL", "SYMBOL", "GENENAME", FC, P_VALUE, FDR]].head(100).rename(
        columns={FC: "log2fc_flight_vs_ground", P_VALUE: "p_value", FDR: "fdr"}
    )
    top.to_csv(RESULTS_DIR / "osd255_top_genes.csv", index=False)
    significant = tested[tested[FDR] < 0.05]
    return {
        "accession": "OSD-255",
        "contrast": "Space Flight vs Ground Control",
        "orientation": "positive log2FC means higher expression in Space Flight",
        "genes_with_p_value": int(len(tested)),
        "genes_with_fdr_below_0_05": int(len(significant)),
        "up_at_fdr_0_05": int((significant[FC] > 0).sum()),
        "down_at_fdr_0_05": int((significant[FC] < 0).sum()),
        "source_statistics": "NASA OSDR processed differential-expression table",
    }


def analyze_imaging() -> pd.DataFrame:
    metadata_by_dataset = {accession: metadata(accession) for accession in {e.dataset for e in ENDPOINTS}}
    rows = []
    for endpoint in ENDPOINTS:
        frame = clean_columns(pd.read_csv(require(DATA_DIR / endpoint.file, endpoint.label)))
        sample_column = "Sample Name" if "Sample Name" in frame.columns else "Sample_Name"
        if endpoint.metric not in frame.columns:
            raise ValueError(f"{endpoint.metric} missing from {endpoint.file}")
        values = frame[[sample_column, endpoint.metric]].rename(
            columns={sample_column: "sample", endpoint.metric: "value"}
        )
        values["sample"] = values["sample"].map(canonical_sample)
        values["value"] = pd.to_numeric(values["value"], errors="coerce")
        merged = values.merge(metadata_by_dataset[endpoint.dataset], on="sample", how="left")
        # OSDR transformed tables can contain ancillary cohort-control samples
        # that are absent from the assay-level factor response. They are not
        # guessed from their names and are not needed for the prespecified
        # Space Flight vs Ground Control contrast; record them transparently.
        unmapped = sorted(merged.loc[merged["group"].isna(), "sample"].unique())
        flight = merged.loc[merged["group"] == "Space Flight", "value"].dropna().to_numpy(float)
        ground = merged.loc[merged["group"] == "Ground Control", "value"].dropna().to_numpy(float)
        if len(flight) < 2 or len(ground) < 2:
            raise ValueError(f"Insufficient flight/ground samples for {endpoint.label}")
        welch = stats.ttest_ind(flight, ground, equal_var=False)
        mann_whitney = stats.mannwhitneyu(flight, ground, alternative="two-sided")
        rows.append(
            {
                "dataset": endpoint.dataset,
                "endpoint": endpoint.label,
                "unit": endpoint.unit,
                "unmapped_samples_excluded": ";".join(unmapped),
                "n_flight": len(flight),
                "n_ground": len(ground),
                "flight_mean": float(np.mean(flight)),
                "ground_mean": float(np.mean(ground)),
                "difference_flight_minus_ground": float(np.mean(flight) - np.mean(ground)),
                "hedges_g": hedges_g(flight, ground),
                "welch_p": float(welch.pvalue),
                "mann_whitney_p": float(mann_whitney.pvalue),
            }
        )
    result = pd.DataFrame(rows)
    result["welch_fdr"] = bh(result["welch_p"])
    result["mann_whitney_fdr"] = bh(result["mann_whitney_p"])
    result.to_csv(RESULTS_DIR / "imaging_endpoints.csv", index=False)
    return result


def json_records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.replace({np.nan: None}).to_json(orient="records"))


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    transcriptomics = analyze_transcriptomics()
    imaging = analyze_imaging()
    payload = {
        "project": "RetinaCellTwin",
        "version": "0.3.0",
        "evidence_layers": {
            "observed": ["OSD-203", "OSD-255", "OSD-557", "OSD-568", "OSD-758"],
            "derived": [
                "OSD-255 differential-expression summary",
                "prespecified imaging endpoint comparisons",
                "cross-mission gravity transfer audit",
                "time-resolved ground-analogue audit",
                "VST and STAR-count effect audits",
                "GO Biological Process context",
                "Mouse Retina Cell Atlas anchor context",
                "unpaired cross-modal evidence matrix",
            ],
            "hypothetical": [],
        },
        "transcriptomics": transcriptomics,
        "imaging": json_records(imaging),
        "claim_boundaries": [
            "Spaceflight is a combined exposure and does not isolate microgravity.",
            "Right-retina transcriptomics and left-eye imaging are not treated as paired measurements.",
            "Imaging tests are exploratory and corrected across seven prespecified endpoints.",
            "Cross-modal concordance does not establish causality.",
            "Canonical retinal cell-class anchors are contextual references, not cell-fraction estimates or cell-of-origin evidence.",
            "Cross-modal convergence is study-level and does not imply sample pairing, mediation or causality.",
            "This release does not generate synthetic data or make clinical predictions.",
        ],
    }
    (RESULTS_DIR / "summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
