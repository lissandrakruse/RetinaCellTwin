#!/usr/bin/env python3
"""Count-level effect audit using public STAR gene-count matrices.

The audit independently recomputes size factors and unshrunken log2 effect
estimates from unnormalized counts.  It intentionally does not reproduce
DESeq2 dispersion modelling or gene-level P values.  Agreement with the NASA
DESeq2 output is therefore assessed by effect ranks and directions.
"""

from __future__ import annotations

import json
from functools import lru_cache

import numpy as np
import pandas as pd
from scipy import stats

from analyze_sample_level_audit import CONTRASTS, Contrast, clean_id
from config import DATA_DIR, RESULTS_DIR, require


MIN_BASE_MEAN = 10.0
PSEUDOCOUNT = 0.5


def count_filename(contrast: Contrast) -> str:
    return contrast.vst_file.replace(
        "VST_Counts", "STAR_Unnormalized_Counts"
    )


@lru_cache(maxsize=None)
def normalized_dataset(count_file: str, sample_file: str) -> tuple[pd.DataFrame, pd.DataFrame, int]:
    counts = pd.read_csv(require(DATA_DIR / count_file, count_file), low_memory=False)
    counts = counts.rename(columns={counts.columns[0]: "gene_id"})
    counts["gene_id"] = clean_id(counts["gene_id"])
    sample_columns = [column for column in counts.columns if column != "gene_id"]
    matrix = counts[sample_columns].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    if not np.isfinite(matrix).all() or (matrix < 0).any():
        raise ValueError(f"Invalid count values in {count_file}")

    positive = (matrix > 0).all(axis=1)
    if int(positive.sum()) < 1000:
        raise ValueError(f"Too few all-positive genes for size-factor estimation in {count_file}")
    log_geomean = np.log(matrix[positive]).mean(axis=1)
    ratios = matrix[positive] / np.exp(log_geomean)[:, None]
    size_factors = np.median(ratios, axis=0)
    size_factors = size_factors / np.exp(np.log(size_factors).mean())
    if not np.isfinite(size_factors).all() or (size_factors <= 0).any():
        raise ValueError(f"Invalid size factors in {count_file}")

    normalized = matrix / size_factors[None, :]
    frame = pd.DataFrame(normalized, columns=sample_columns)
    frame.insert(0, "gene_id", counts["gene_id"].to_numpy())
    samples = pd.read_csv(require(DATA_DIR / sample_file, sample_file))
    samples = samples.rename(columns={samples.columns[0]: "sample"})
    return frame, samples, int(positive.sum())


def analyze(contrast: Contrast) -> tuple[dict, pd.DataFrame]:
    count_file = count_filename(contrast)
    normalized, samples, normalization_genes = normalized_dataset(count_file, contrast.sample_file)
    left_samples = samples.loc[samples["condition"] == contrast.left_condition, "sample"].tolist()
    right_samples = samples.loc[samples["condition"] == contrast.right_condition, "sample"].tolist()
    missing = sorted((set(left_samples) | set(right_samples)) - set(normalized.columns))
    if missing:
        raise ValueError(f"Samples missing from {count_file}: {missing}")

    left_mean = normalized[left_samples].mean(axis=1)
    right_mean = normalized[right_samples].mean(axis=1)
    base_mean = normalized[left_samples + right_samples].mean(axis=1)
    result = pd.DataFrame(
        {
            "gene_id": normalized["gene_id"],
            "base_mean_normalized_count": base_mean,
            "count_log2fc": np.log2((left_mean + PSEUDOCOUNT) / (right_mean + PSEUDOCOUNT)),
        }
    )
    result = result.loc[result["base_mean_normalized_count"] >= MIN_BASE_MEAN].copy()

    nasa_column = f"Log2fc_({contrast.nasa_left})v({contrast.nasa_right})"
    de = pd.read_csv(
        require(DATA_DIR / contrast.de_file, contrast.de_file),
        usecols=["ENSEMBL", "SYMBOL", "GENENAME", nasa_column],
        low_memory=False,
    ).rename(columns={nasa_column: "nasa_log2fc"})
    de["gene_id"] = clean_id(de["ENSEMBL"])
    de["nasa_log2fc"] = pd.to_numeric(de["nasa_log2fc"], errors="coerce")
    result = result.merge(de[["gene_id", "SYMBOL", "GENENAME", "nasa_log2fc"]], on="gene_id", how="left")

    pair = result[["count_log2fc", "nasa_log2fc"]].dropna()
    rho = stats.spearmanr(pair["count_log2fc"], pair["nasa_log2fc"])
    nonzero = pair.loc[(pair != 0).all(axis=1)]
    direction = np.sign(nonzero["count_log2fc"]) == np.sign(nonzero["nasa_log2fc"])
    same = int(direction.sum())
    total = int(len(direction))

    result["absolute_count_log2fc"] = result["count_log2fc"].abs()
    result["contrast"] = contrast.name
    top = result.sort_values("absolute_count_log2fc", ascending=False).head(100)
    summary = {
        "contrast": contrast.name,
        "accession": contrast.accession,
        "count_file": count_file,
        "n_left": len(left_samples),
        "n_right": len(right_samples),
        "size_factor_reference_genes": normalization_genes,
        "genes_after_base_mean_filter": int(len(result)),
        "minimum_base_mean": MIN_BASE_MEAN,
        "pseudocount": PSEUDOCOUNT,
        "count_vs_nasa_spearman_rho": float(rho.statistic),
        "count_vs_nasa_spearman_p": float(rho.pvalue),
        "direction_concordant": same,
        "direction_total": total,
        "direction_fraction": same / total if total else None,
        "direction_binomial_p": float(stats.binomtest(same, total, 0.5, alternative="greater").pvalue),
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
        "analysis": "count-level effect audit",
        "normalization": "DESeq-style median-of-ratios size factors using all-positive genes",
        "effect": "unshrunken log2 ratio of group mean normalized counts",
        "interpretation": (
            "This analysis starts from public unnormalized STAR gene counts and independently recomputes "
            "normalization and effect direction. It does not reproduce DESeq2 dispersion estimation, "
            "hypothesis tests or fold-change shrinkage and must not be presented as a DESeq2 replacement."
        ),
        "contrasts": summaries,
    }
    (RESULTS_DIR / "count_level_audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    pd.concat(top_tables, ignore_index=True).to_csv(
        RESULTS_DIR / "count_level_audit_top_genes.csv", index=False
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
