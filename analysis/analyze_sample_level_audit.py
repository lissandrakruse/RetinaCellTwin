#!/usr/bin/env python3
"""Audit NASA differential-expression effects from sample-level VST values.

This is deliberately a sensitivity analysis, not a replacement for the NASA
DESeq2 pipeline.  It estimates each prespecified contrast directly from the
public variance-stabilized expression matrix, applies Welch tests and BH FDR,
and quantifies agreement with the independently supplied NASA log2 fold
changes.  The different effect scales (VST mean difference versus log2 fold
change) are compared by ranks and directions, not by numerical equality.
"""

from __future__ import annotations

import json
import math
import warnings
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

from config import DATA_DIR, RESULTS_DIR, require


@dataclass(frozen=True)
class Contrast:
    name: str
    accession: str
    vst_file: str
    sample_file: str
    de_file: str
    left_condition: str
    right_condition: str
    nasa_left: str
    nasa_right: str


def spec(
    name: str,
    accession: str,
    prefix: str,
    left_condition: str,
    right_condition: str,
    nasa_left: str,
    nasa_right: str,
) -> Contrast:
    return Contrast(
        name=name,
        accession=accession,
        vst_file=f"{prefix}_rna_seq_VST_Counts_GLbulkRNAseq.csv",
        sample_file=f"{prefix}_rna_seq_SampleTable_GLbulkRNAseq.csv",
        de_file=f"{prefix}_rna_seq_differential_expression_GLbulkRNAseq.csv",
        left_condition=left_condition,
        right_condition=right_condition,
        nasa_left=nasa_left,
        nasa_right=nasa_right,
    )


CONTRASTS: list[Contrast] = [
    spec(
        "OSD-255 flight versus ground",
        "OSD-255",
        "GLDS-255",
        "Space.Flight",
        "Ground.Control",
        "Space Flight",
        "Ground Control",
    ),
    spec(
        "OSD-758 uG versus ground",
        "OSD-758",
        "GLDS-664",
        "Space.Flight...uG",
        "Ground.Control...1G.on.Earth",
        "Space Flight & uG",
        "Ground Control & 1G on Earth",
    ),
    spec(
        "OSD-758 uG versus in-flight 1G",
        "OSD-758",
        "GLDS-664",
        "Space.Flight...uG",
        "Space.Flight...1G.by.centrifugation",
        "Space Flight & uG",
        "Space Flight & 1G by centrifugation",
    ),
    spec(
        "OSD-758 in-flight 1G versus ground",
        "OSD-758",
        "GLDS-664",
        "Space.Flight...1G.by.centrifugation",
        "Ground.Control...1G.on.Earth",
        "Space Flight & 1G by centrifugation",
        "Ground Control & 1G on Earth",
    ),
]

for time_condition, nasa_time, short_time in (
    ("7.day", "7 day", "7d"),
    ("1.month", "1 month", "1m"),
    ("4.month", "4 month", "4m"),
):
    control_condition = f"{time_condition}...non.irradiated...Normally.Loaded.Control"
    control_nasa = f"{nasa_time} & non-irradiated & Normally Loaded Control"
    for mechanism, left_condition, nasa_left in (
        (
            "radiation",
            f"{time_condition}...cobalt.57.gamma.radiation...Normally.Loaded.Control",
            f"{nasa_time} & cobalt-57 gamma radiation & Normally Loaded Control",
        ),
        (
            "hlu",
            f"{time_condition}...non.irradiated...Hindlimb.Unloaded",
            f"{nasa_time} & non-irradiated & Hindlimb Unloaded",
        ),
    ):
        CONTRASTS.append(
            spec(
                f"OSD-203 {short_time} {mechanism} versus control",
                "OSD-203",
                "GLDS-203",
                left_condition,
                control_condition,
                nasa_left,
                control_nasa,
            )
        )


def clean_id(values: pd.Series) -> pd.Series:
    return values.astype(str).str.replace(r"\.\d+$", "", regex=True)


def bh(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    output = np.full(values.shape, np.nan)
    valid_index = np.flatnonzero(np.isfinite(values))
    if not len(valid_index):
        return output
    order = valid_index[np.argsort(values[valid_index])]
    n = len(order)
    raw = values[order] * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(raw[::-1])[::-1]
    output[order] = np.clip(adjusted, 0, 1)
    return output


def hedges_g(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    n1, n0 = left.shape[1], right.shape[1]
    pooled_df = n1 + n0 - 2
    pooled = np.sqrt(
        ((n1 - 1) * np.var(left, axis=1, ddof=1) + (n0 - 1) * np.var(right, axis=1, ddof=1))
        / pooled_df
    )
    correction = 1 - 3 / (4 * (n1 + n0) - 9)
    effect = np.full(pooled.shape, np.nan, dtype=float)
    np.divide(
        correction * (np.mean(left, axis=1) - np.mean(right, axis=1)),
        pooled,
        out=effect,
        where=pooled > 0,
    )
    return effect


def analyze(contrast: Contrast) -> tuple[dict, pd.DataFrame]:
    vst = pd.read_csv(require(DATA_DIR / contrast.vst_file, contrast.vst_file), low_memory=False)
    gene_column = vst.columns[0]
    vst = vst.rename(columns={gene_column: "gene_id"})
    vst["gene_id"] = clean_id(vst["gene_id"])

    samples = pd.read_csv(require(DATA_DIR / contrast.sample_file, contrast.sample_file))
    samples = samples.rename(columns={samples.columns[0]: "sample"})
    left_samples = samples.loc[samples["condition"] == contrast.left_condition, "sample"].tolist()
    right_samples = samples.loc[samples["condition"] == contrast.right_condition, "sample"].tolist()
    missing = sorted((set(left_samples) | set(right_samples)) - set(vst.columns))
    if missing:
        raise ValueError(f"Samples missing from {contrast.vst_file}: {missing}")
    if len(left_samples) < 2 or len(right_samples) < 2:
        raise ValueError(f"Insufficient samples for {contrast.name}")

    left = vst[left_samples].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    right = vst[right_samples].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    complete = np.isfinite(left).all(axis=1) & np.isfinite(right).all(axis=1)
    result = pd.DataFrame({"gene_id": vst.loc[complete, "gene_id"].to_numpy()})
    left = left[complete]
    right = right[complete]
    result["vst_mean_difference"] = left.mean(axis=1) - right.mean(axis=1)
    result["hedges_g"] = hedges_g(left, right)
    zero_variance_both_groups = (np.var(left, axis=1, ddof=1) == 0) & (
        np.var(right, axis=1, ddof=1) == 0
    )
    with warnings.catch_warnings():
        # SciPy warns when nearly identical values cause catastrophic
        # cancellation. We retain its numerical result and expose exactly
        # degenerate rows in the machine-readable contrast summary.
        warnings.filterwarnings(
            "ignore",
            message="Precision loss occurred in moment calculation",
            category=RuntimeWarning,
        )
        test = stats.ttest_ind(left, right, axis=1, equal_var=False, nan_policy="omit")
    result["welch_p"] = np.asarray(test.pvalue, dtype=float)
    result["welch_fdr"] = bh(result["welch_p"].to_numpy())

    nasa_column = f"Log2fc_({contrast.nasa_left})v({contrast.nasa_right})"
    de = pd.read_csv(
        require(DATA_DIR / contrast.de_file, contrast.de_file),
        usecols=["ENSEMBL", "SYMBOL", "GENENAME", nasa_column],
        low_memory=False,
    ).rename(columns={nasa_column: "nasa_log2fc"})
    de["gene_id"] = clean_id(de["ENSEMBL"])
    de["nasa_log2fc"] = pd.to_numeric(de["nasa_log2fc"], errors="coerce")
    result = result.merge(de[["gene_id", "SYMBOL", "GENENAME", "nasa_log2fc"]], on="gene_id", how="left")

    pair = result[["vst_mean_difference", "nasa_log2fc"]].dropna()
    rho = stats.spearmanr(pair["vst_mean_difference"], pair["nasa_log2fc"])
    nonzero = pair.loc[(pair != 0).all(axis=1)]
    direction = np.sign(nonzero["vst_mean_difference"]) == np.sign(nonzero["nasa_log2fc"])
    same = int(direction.sum())
    total = int(len(direction))

    result["contrast"] = contrast.name
    top = result.sort_values(["welch_fdr", "welch_p"], na_position="last").head(50)
    summary = {
        "contrast": contrast.name,
        "accession": contrast.accession,
        "left_condition": contrast.left_condition,
        "right_condition": contrast.right_condition,
        "n_left": len(left_samples),
        "n_right": len(right_samples),
        "genes_audited": int(len(result)),
        "nasa_effects_compared": int(len(pair)),
        "vst_vs_nasa_spearman_rho": float(rho.statistic),
        "vst_vs_nasa_spearman_p": float(rho.pvalue),
        "direction_concordant": same,
        "direction_total": total,
        "direction_fraction": same / total if total else None,
        "direction_binomial_p": float(stats.binomtest(same, total, 0.5, alternative="greater").pvalue),
        "welch_fdr_below_0_05": int((result["welch_fdr"] < 0.05).sum()),
        "genes_with_zero_variance_in_both_groups": int(zero_variance_both_groups.sum()),
        "effect_scale_note": "VST mean differences and NASA log2 fold changes are compared only by ranks and directions.",
    }
    return summary, top


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summaries: list[dict] = []
    top_tables: list[pd.DataFrame] = []
    for contrast in CONTRASTS:
        summary, top = analyze(contrast)
        summaries.append(summary)
        top_tables.append(top)
    payload = {
        "project": "RetinaCellTwin",
        "analysis": "sample-level VST sensitivity audit",
        "method": "Welch tests and BH FDR on public NASA OSDR VST matrices",
        "interpretation": (
            "This audit is independent at the statistical contrast stage but reuses NASA-processed VST values; "
            "it is not an independent FASTQ-to-count reprocessing and does not replace DESeq2 inference."
        ),
        "contrasts": summaries,
    }
    (RESULTS_DIR / "sample_level_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    pd.concat(top_tables, ignore_index=True).to_csv(
        RESULTS_DIR / "sample_level_audit_top_genes.csv", index=False
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
