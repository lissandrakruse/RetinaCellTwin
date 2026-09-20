#!/usr/bin/env python3
"""Independent cross-dataset test of the RetinaCellTwin gravity hypothesis.

Discovery genes are selected only in OSD-255. OSD-758 is then used as an
independent artificial-gravity validation dataset, and OSD-203 is used for
descriptive attribution against hindlimb unloading and gamma radiation.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from config import DATA_DIR, RESULTS_DIR, require


OSD255 = "GLDS-255_rna_seq_differential_expression_GLbulkRNAseq.csv"
OSD758 = "GLDS-664_rna_seq_differential_expression_GLbulkRNAseq.csv"
OSD203 = "GLDS-203_rna_seq_differential_expression_GLbulkRNAseq.csv"

RR9_FC = "Log2fc_(Space Flight)v(Ground Control)"
RR9_FDR = "Adj.p.value_(Space Flight)v(Ground Control)"

G_LEVELS = {
    "uG": "Space Flight & uG",
    "0.33G": "Space Flight & 0.33G by centrifugation",
    "0.66G": "Space Flight & 0.66G by centrifugation",
    "1G": "Space Flight & 1G by centrifugation",
}
GROUND = "Ground Control & 1G on Earth"
TIMES = ("7 day", "1 month", "4 month")


def fc(left: str, right: str) -> str:
    return f"Log2fc_({left})v({right})"


def fdr(left: str, right: str) -> str:
    return f"Adj.p.value_({left})v({right})"


def clean_id(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.\d+$", "", regex=True)


def bh(values: list[float]) -> list[float]:
    series = pd.Series(values, dtype=float)
    valid = series.dropna().sort_values()
    output = pd.Series(np.nan, index=series.index, dtype=float)
    if valid.empty:
        return output.tolist()
    n = len(valid)
    raw = valid.to_numpy() * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(raw[::-1])[::-1]
    output.loc[valid.index] = np.clip(adjusted, 0, 1)
    return output.tolist()


def safe_spearman(x: pd.Series, y: pd.Series) -> tuple[float, float, int]:
    pair = pd.concat([x, y], axis=1).dropna()
    if len(pair) < 3 or pair.iloc[:, 0].nunique() < 2 or pair.iloc[:, 1].nunique() < 2:
        return float("nan"), float("nan"), len(pair)
    result = stats.spearmanr(pair.iloc[:, 0], pair.iloc[:, 1])
    return float(result.statistic), float(result.pvalue), len(pair)


def sign_test(matches: pd.Series) -> tuple[int, int, float]:
    usable = matches.dropna().astype(bool)
    successes = int(usable.sum())
    total = int(len(usable))
    p_value = float(stats.binomtest(successes, total, 0.5, alternative="greater").pvalue) if total else float("nan")
    return successes, total, p_value


def load_discovery_panel() -> pd.DataFrame:
    columns = ["ENSEMBL", "SYMBOL", "GENENAME", RR9_FC, RR9_FDR]
    frame = pd.read_csv(require(DATA_DIR / OSD255, "OSD-255 DE table"), usecols=columns, low_memory=False)
    frame["gene_id"] = clean_id(frame["ENSEMBL"])
    frame[RR9_FC] = pd.to_numeric(frame[RR9_FC], errors="coerce")
    frame[RR9_FDR] = pd.to_numeric(frame[RR9_FDR], errors="coerce")
    frame = frame.loc[(frame[RR9_FDR] < 0.05) & frame[RR9_FC].notna()].copy()
    if frame["gene_id"].duplicated().any():
        frame = frame.sort_values(RR9_FDR).drop_duplicates("gene_id")
    return frame.rename(columns={RR9_FC: "rr9_log2fc", RR9_FDR: "rr9_fdr"})


def load_osd758() -> pd.DataFrame:
    effect_columns = [fc(condition, GROUND) for condition in G_LEVELS.values()]
    direct_columns = [fc(G_LEVELS["uG"], G_LEVELS["1G"]), fdr(G_LEVELS["uG"], G_LEVELS["1G"])]
    usecols = ["ENSEMBL", "SYMBOL", *effect_columns, *direct_columns]
    frame = pd.read_csv(require(DATA_DIR / OSD758, "OSD-758 DE table"), usecols=usecols, low_memory=False)
    frame["gene_id"] = clean_id(frame["ENSEMBL"])
    rename = {fc(condition, GROUND): f"osd758_{label}_vs_ground" for label, condition in G_LEVELS.items()}
    rename[fc(G_LEVELS["uG"], G_LEVELS["1G"])] = "osd758_uG_vs_inflight_1G"
    rename[fdr(G_LEVELS["uG"], G_LEVELS["1G"])] = "osd758_uG_vs_inflight_1G_fdr"
    frame = frame.rename(columns=rename)
    numeric = list(rename.values())
    frame[numeric] = frame[numeric].apply(pd.to_numeric, errors="coerce")
    if frame["gene_id"].duplicated().any():
        raise ValueError("Duplicate OSD-758 ENSEMBL gene identifiers")
    return frame


def gravity_validation(panel: pd.DataFrame) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    osd758 = load_osd758()
    merged = panel.merge(osd758, on="gene_id", how="inner", suffixes=("_osd255", "_osd758"))
    if len(merged) < 100:
        raise ValueError("Too few OSD-255 discovery genes mapped to OSD-758")

    rho, rho_p, n = safe_spearman(merged["rr9_log2fc"], merged["osd758_uG_vs_ground"])
    matches = np.sign(merged["rr9_log2fc"]) == np.sign(merged["osd758_uG_vs_ground"])
    same, total, sign_p = sign_test(pd.Series(matches))

    rescue_rows = []
    base = merged["osd758_uG_vs_ground"].abs()
    panel_ids = set(merged["gene_id"])
    background = osd758.loc[~osd758["gene_id"].isin(panel_ids)].copy()
    background_base = background["osd758_uG_vs_ground"].abs()
    discovery_direction = np.sign(merged["rr9_log2fc"])
    trend_matrix = []
    for label in ("uG", "0.33G", "0.66G", "1G"):
        trend_matrix.append(merged[f"osd758_{label}_vs_ground"] * discovery_direction)
    trend_frame = pd.concat(trend_matrix, axis=1)
    trend_frame.columns = ["uG", "0.33G", "0.66G", "1G"]
    gravities = np.array([0.0, 0.33, 0.66, 1.0])
    merged["gravity_trend_rho"] = trend_frame.apply(
        lambda row: stats.spearmanr(gravities, row.to_numpy(float), nan_policy="omit").statistic,
        axis=1,
    )

    for label in ("0.33G", "0.66G", "1G"):
        current = merged[f"osd758_{label}_vs_ground"].abs()
        usable = pd.concat([base, current], axis=1).dropna()
        wilcoxon = stats.wilcoxon(usable.iloc[:, 1], usable.iloc[:, 0], alternative="less", zero_method="wilcox")
        rescued = current < base
        panel_delta = base - current
        background_current = background[f"osd758_{label}_vs_ground"].abs()
        background_delta = background_base - background_current
        comparison = stats.mannwhitneyu(
            panel_delta.dropna(), background_delta.dropna(), alternative="two-sided"
        )
        rescue_rows.append(
            {
                "gravity": label,
                "n": int(len(usable)),
                "median_abs_log2fc": float(current.median()),
                "median_abs_log2fc_uG": float(base.median()),
                "fraction_closer_to_ground": float(rescued.mean()),
                "wilcoxon_p": float(wilcoxon.pvalue),
                "panel_median_attenuation": float(panel_delta.median()),
                "background_median_attenuation": float(background_delta.median()),
                "background_fraction_closer_to_ground": float((background_current < background_base).mean()),
                "panel_vs_background_mannwhitney_p": float(comparison.pvalue),
            }
        )
    adjusted = bh([row["wilcoxon_p"] for row in rescue_rows])
    for row, value in zip(rescue_rows, adjusted):
        row["wilcoxon_fdr"] = value
    benchmark_adjusted = bh([row["panel_vs_background_mannwhitney_p"] for row in rescue_rows])
    for row, value in zip(rescue_rows, benchmark_adjusted):
        row["panel_vs_background_mannwhitney_fdr"] = value

    concordant = matches & merged["osd758_uG_vs_ground"].notna()
    merged["gravity_sensitive_candidate"] = (
        concordant
        & (merged["osd758_uG_vs_inflight_1G_fdr"] < 0.05)
        & (merged["osd758_1G_vs_ground"].abs() < merged["osd758_uG_vs_ground"].abs())
    )
    merged["gravity_independent_residual_candidate"] = (
        concordant
        & (np.sign(merged["osd758_1G_vs_ground"]) == np.sign(merged["osd758_uG_vs_ground"]))
        & (merged["osd758_1G_vs_ground"].abs() >= 0.5 * merged["osd758_uG_vs_ground"].abs())
    )

    output_columns = [
        "gene_id", "SYMBOL_osd255", "GENENAME", "rr9_log2fc", "rr9_fdr",
        "osd758_uG_vs_ground", "osd758_0.33G_vs_ground", "osd758_0.66G_vs_ground",
        "osd758_1G_vs_ground", "osd758_uG_vs_inflight_1G",
        "osd758_uG_vs_inflight_1G_fdr", "gravity_trend_rho",
        "gravity_sensitive_candidate", "gravity_independent_residual_candidate",
    ]
    genes = merged[output_columns].sort_values(
        ["gravity_sensitive_candidate", "osd758_uG_vs_inflight_1G_fdr"],
        ascending=[False, True],
    )
    genes.to_csv(RESULTS_DIR / "gravity_validation_genes.csv", index=False)

    direct = osd758.loc[osd758["osd758_uG_vs_inflight_1G_fdr"] < 0.05].copy()
    direct = direct.sort_values("osd758_uG_vs_inflight_1G_fdr")
    direct[[
        "gene_id", "SYMBOL", "osd758_uG_vs_inflight_1G",
        "osd758_uG_vs_inflight_1G_fdr", "osd758_uG_vs_ground",
        "osd758_1G_vs_ground",
    ]].to_csv(RESULTS_DIR / "osd758_direct_gravity_genes.csv", index=False)

    negative_trends = int((merged["gravity_trend_rho"] < 0).sum())
    trend_total = int(merged["gravity_trend_rho"].notna().sum())
    return {
        "discovery_panel_genes": int(len(panel)),
        "mapped_to_osd758": int(len(merged)),
        "rr9_vs_osd758_uG_spearman_rho": rho,
        "rr9_vs_osd758_uG_spearman_p": rho_p,
        "rr9_vs_osd758_uG_n": n,
        "rr9_vs_osd758_uG_direction_concordant": same,
        "rr9_vs_osd758_uG_direction_total": total,
        "rr9_vs_osd758_uG_direction_fraction": same / total,
        "rr9_vs_osd758_uG_direction_binomial_p": sign_p,
        "gravity_rescue": rescue_rows,
        "osd758_genes_tested": int(osd758["osd758_uG_vs_inflight_1G"].notna().sum()),
        "osd758_direct_gravity_fdr_lt_0_05": int(len(direct)),
        "osd758_direct_gravity_up_in_uG": int((direct["osd758_uG_vs_inflight_1G"] > 0).sum()),
        "osd758_direct_gravity_down_in_uG": int((direct["osd758_uG_vs_inflight_1G"] < 0).sum()),
        "osd758_direct_gravity_overlap_rr9_panel": int(direct["gene_id"].isin(panel_ids).sum()),
        "median_gene_gravity_trend_rho": float(merged["gravity_trend_rho"].median()),
        "negative_gravity_trends": negative_trends,
        "gravity_trend_total": trend_total,
        "gravity_trend_binomial_p": float(stats.binomtest(negative_trends, trend_total, 0.5, alternative="greater").pvalue),
        "gravity_sensitive_candidates": int(merged["gravity_sensitive_candidate"].sum()),
        "gravity_independent_residual_candidates": int(merged["gravity_independent_residual_candidate"].sum()),
    }, merged, osd758


def load_osd203() -> pd.DataFrame:
    columns = ["ENSEMBL", "SYMBOL"]
    contrasts: dict[str, str] = {}
    for time in TIMES:
        control = f"{time} & non-irradiated & Normally Loaded Control"
        hlu = f"{time} & non-irradiated & Hindlimb Unloaded"
        radiation = f"{time} & cobalt-57 gamma radiation & Normally Loaded Control"
        combined = f"{time} & cobalt-57 gamma radiation & Hindlimb Unloaded"
        for label, left in (("hlu", hlu), ("radiation", radiation), ("combined", combined)):
            effect = fc(left, control)
            adjusted = fdr(left, control)
            columns.extend([effect, adjusted])
            contrasts[effect] = f"osd203_{time}_{label}_log2fc"
            contrasts[adjusted] = f"osd203_{time}_{label}_fdr"
    frame = pd.read_csv(require(DATA_DIR / OSD203, "OSD-203 DE table"), usecols=columns, low_memory=False)
    frame["gene_id"] = clean_id(frame["ENSEMBL"])
    frame = frame.rename(columns=contrasts)
    frame[list(contrasts.values())] = frame[list(contrasts.values())].apply(pd.to_numeric, errors="coerce")
    if frame["gene_id"].duplicated().any():
        raise ValueError("Duplicate OSD-203 ENSEMBL gene identifiers")
    return frame


def panel_rank_enrichment(
    all_pairs: pd.DataFrame,
    panel_ids: set[str],
    left: str,
    right: str,
    seed: int,
    permutations: int = 10000,
) -> tuple[float, float, int, int]:
    """Compare panel correlation with equal-sized random gene panels.

    Correlations use ranks defined across the common-gene universe so the
    observed panel and every random panel are evaluated identically.
    """
    usable = all_pairs[["gene_id", left, right]].dropna().copy()
    usable["left_rank"] = stats.rankdata(usable[left].to_numpy(float))
    usable["right_rank"] = stats.rankdata(usable[right].to_numpy(float))
    mask = usable["gene_id"].isin(panel_ids).to_numpy()
    panel_n = int(mask.sum())
    if panel_n < 3:
        return float("nan"), float("nan"), panel_n, len(usable)

    x = usable["left_rank"].to_numpy(float)
    y = usable["right_rank"].to_numpy(float)

    def corr(index: np.ndarray) -> float:
        a = x[index]
        b = y[index]
        a = a - a.mean()
        b = b - b.mean()
        denominator = math.sqrt(float(np.dot(a, a) * np.dot(b, b)))
        return float(np.dot(a, b) / denominator) if denominator else float("nan")

    observed = corr(np.flatnonzero(mask))
    rng = np.random.default_rng(seed)
    at_least = 0
    universe = np.arange(len(usable))
    for _ in range(permutations):
        sampled = rng.choice(universe, size=panel_n, replace=False)
        if corr(sampled) >= observed:
            at_least += 1
    empirical_p = (at_least + 1) / (permutations + 1)
    return observed, float(empirical_p), panel_n, int(len(usable))


def analog_attribution(
    gravity_genes: pd.DataFrame, osd758: pd.DataFrame
) -> tuple[list[dict], pd.DataFrame]:
    osd203 = load_osd203()
    merged = gravity_genes.merge(osd203, on="gene_id", how="inner", suffixes=("", "_osd203"))
    universe = osd758.merge(osd203, on="gene_id", how="inner", suffixes=("", "_osd203"))
    panel_ids = set(gravity_genes["gene_id"])
    rows = []
    contrast_index = 0
    for time in TIMES:
        for mechanism, reference in (
            ("hlu", "osd758_uG_vs_inflight_1G"),
            ("radiation", "osd758_1G_vs_ground"),
        ):
            analog = f"osd203_{time}_{mechanism}_log2fc"
            rho, p_value, n = safe_spearman(merged[reference], merged[analog])
            usable = merged[[reference, analog]].dropna()
            direction = np.sign(usable[reference]) == np.sign(usable[analog])
            same, total, sign_p = sign_test(pd.Series(direction))
            genome_rho, genome_p, genome_n = safe_spearman(universe[reference], universe[analog])
            ranked_panel_rho, enrichment_p, ranked_panel_n, universe_n = panel_rank_enrichment(
                universe, panel_ids, reference, analog, seed=20260920 + contrast_index
            )
            contrast_index += 1
            rows.append(
                {
                    "time": time,
                    "mechanism": mechanism,
                    "reference_effect": reference,
                    "n": n,
                    "spearman_rho": rho,
                    "spearman_p": p_value,
                    "direction_concordant": same,
                    "direction_total": total,
                    "direction_fraction": same / total if total else None,
                    "direction_binomial_p": sign_p,
                    "common_gene_universe_n": genome_n,
                    "common_gene_universe_spearman_rho": genome_rho,
                    "common_gene_universe_spearman_p": genome_p,
                    "panel_global_rank_rho": ranked_panel_rho,
                    "panel_enrichment_empirical_p": enrichment_p,
                    "panel_enrichment_permutations": 10000,
                    "panel_rank_n": ranked_panel_n,
                    "panel_rank_universe_n": universe_n,
                }
            )
    rho_fdr = bh([row["spearman_p"] for row in rows])
    sign_fdr = bh([row["direction_binomial_p"] for row in rows])
    for row, corr, direction in zip(rows, rho_fdr, sign_fdr):
        row["spearman_fdr"] = corr
        row["direction_binomial_fdr"] = direction
    enrichment_fdr = bh([row["panel_enrichment_empirical_p"] for row in rows])
    for row, value in zip(rows, enrichment_fdr):
        row["panel_enrichment_fdr"] = value
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "osd203_attribution.csv", index=False)

    radiation_lfc = "osd203_7 day_radiation_log2fc"
    radiation_fdr = "osd203_7 day_radiation_fdr"
    radiation_candidates = merged.loc[
        (merged[radiation_fdr] < 0.05)
        & ((merged["osd758_1G_vs_ground"] * merged[radiation_lfc]) > 0)
    ].copy()
    radiation_candidates[[
        "gene_id", "SYMBOL_osd255", "GENENAME", "rr9_log2fc", "rr9_fdr",
        "osd758_1G_vs_ground", radiation_lfc, radiation_fdr,
    ]].sort_values(radiation_fdr).to_csv(
        RESULTS_DIR / "osd203_7d_radiation_candidates.csv", index=False
    )
    return rows, merged


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    panel = load_discovery_panel()
    gravity, gravity_genes, osd758 = gravity_validation(panel)
    attribution, merged = analog_attribution(gravity_genes, osd758)
    rr9_replicated = bool(
        gravity["rr9_vs_osd758_uG_spearman_rho"] > 0
        and gravity["rr9_vs_osd758_uG_spearman_p"] < 0.05
        and gravity["rr9_vs_osd758_uG_direction_fraction"] > 0.5
    )
    rescue_specific = any(
        row["gravity"] in {"0.66G", "1G"}
        and row["panel_median_attenuation"] > row["background_median_attenuation"]
        and row["panel_vs_background_mannwhitney_fdr"] < 0.05
        for row in gravity["gravity_rescue"]
    )
    radiation_7d = next(
        row for row in attribution if row["time"] == "7 day" and row["mechanism"] == "radiation"
    )
    radiation_enriched = bool(radiation_7d["panel_enrichment_fdr"] < 0.05)
    conclusion = (
        "The independently selected and frozen RR-9 retinal flight signature did not replicate as a stable "
        "cross-mission gravity signature. Artificial gravity attenuation in OSD-758 is "
        "not enriched in the RR-9 panel relative to the transcriptome background. "
    )
    if radiation_enriched:
        conclusion += (
            "A time-specific seven-day radiation concordance was enriched beyond random "
            "gene panels, but it did not persist at one or four months and remains a "
            "prospective hypothesis rather than causal attribution."
        )
    else:
        conclusion += (
            "Ground-analog concordance is time-dependent and was not enriched beyond "
            "the common-gene background."
        )
    payload = {
        "project": "RetinaCellTwin",
        "analysis": "independent gravity hypothesis test",
        "discovery_dataset": "OSD-255",
        "artificial_gravity_validation_dataset": "OSD-758",
        "ground_analog_attribution_dataset": "OSD-203",
        "gravity_validation": gravity,
        "analog_attribution": attribution,
        "decision_summary": {
            "rr9_signature_replicated_in_osd758": rr9_replicated,
            "rr9_panel_specific_artificial_gravity_attenuation": rescue_specific,
            "strict_gravity_sensitive_candidates": gravity["gravity_sensitive_candidates"],
            "seven_day_radiation_concordance_observed": bool(
                radiation_7d["spearman_fdr"] < 0.05
                and radiation_7d["direction_binomial_fdr"] < 0.05
            ),
            "seven_day_radiation_concordance_panel_enriched": bool(
                radiation_enriched
            ),
            "stable_hlu_attribution_supported": False,
            "conclusion": conclusion,
        },
        "interpretation_rules": [
            "OSD-255 FDR < 0.05 genes define the discovery panel before OSD-758 is examined.",
            "OSD-758 uG versus in-flight 1G is the primary gravity contrast.",
            "OSD-758 in-flight 1G versus ground is treated only as residual flight-associated signal.",
            "OSD-203 hindlimb unloading and gamma radiation are imperfect ground analogs, not causal equivalents.",
            "All gene-level statistics are NASA OSDR processed differential-expression results.",
            "Random-panel enrichment uses 10,000 deterministic permutations and the common-gene universe.",
            "The OSD-758 artificial-gravity attenuation result was published previously; this analysis tests transferability of the independently selected RR-9 panel.",
        ],
    }
    path = RESULTS_DIR / "gravity_hypothesis.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
