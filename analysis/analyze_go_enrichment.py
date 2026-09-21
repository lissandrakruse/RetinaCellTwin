#!/usr/bin/env python3
"""Prespecified GO Biological Process over-representation analyses."""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from functools import lru_cache

import numpy as np
import pandas as pd
from scipy import stats

from config import DATA_DIR, RESULTS_DIR, require


OSD255_DE = "GLDS-255_rna_seq_differential_expression_GLbulkRNAseq.csv"
OSD203_DE = "GLDS-203_rna_seq_differential_expression_GLbulkRNAseq.csv"
RADIATION_COLUMN = (
    "Log2fc_(7 day & cobalt-57 gamma radiation & Normally Loaded Control)"
    "v(7 day & non-irradiated & Normally Loaded Control)"
)


def bh(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    order = np.argsort(values)
    adjusted = np.empty_like(values)
    raw = values[order] * len(values) / np.arange(1, len(values) + 1)
    adjusted[order] = np.minimum.accumulate(raw[::-1])[::-1]
    return np.clip(adjusted, 0, 1)


def parse_obo(path) -> tuple[dict[str, str], dict[str, set[str]], str | None]:
    names: dict[str, str] = {}
    parents: dict[str, set[str]] = defaultdict(set)
    current: dict[str, object] = {}
    data_version = None

    def commit() -> None:
        term_id = current.get("id")
        if not isinstance(term_id, str) or current.get("obsolete"):
            return
        names[term_id] = str(current.get("name", term_id))
        parents[term_id].update(current.get("parents", set()))

    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if line.startswith("data-version:") and data_version is None:
                data_version = line.split(":", 1)[1].strip()
            if line == "[Term]":
                commit()
                current = {"parents": set()}
            elif not line:
                commit()
                current = {}
            elif line.startswith("id: GO:"):
                current["id"] = line.split("id:", 1)[1].strip()
            elif line.startswith("name:"):
                current["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("is_a: GO:"):
                current.setdefault("parents", set()).add(line.split()[1])
            elif line.startswith("relationship: part_of GO:"):
                current.setdefault("parents", set()).add(line.split()[2])
            elif line == "is_obsolete: true":
                current["obsolete"] = True
    commit()
    return names, parents, data_version


def parse_gaf(path) -> tuple[dict[str, set[str]], str | None]:
    direct: dict[str, set[str]] = defaultdict(set)
    gaf_version = None
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("!gaf-version:"):
                gaf_version = line.strip().split(":", 1)[1]
            if line.startswith("!"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9 or fields[8] != "P" or "NOT" in fields[3].split("|"):
                continue
            symbol, go_id = fields[2], fields[4]
            direct[symbol].add(go_id)
    return direct, gaf_version


def propagate_annotations(
    direct: dict[str, set[str]], parents: dict[str, set[str]]
) -> dict[str, set[str]]:
    @lru_cache(maxsize=None)
    def ancestors(term: str) -> frozenset[str]:
        found = {term}
        for parent in parents.get(term, set()):
            found.update(ancestors(parent))
        return frozenset(found)

    return {
        gene: set().union(*(ancestors(term) for term in terms))
        for gene, terms in direct.items()
        if terms
    }


def valid_symbols(series: pd.Series) -> set[str]:
    values = series.dropna().astype(str).str.strip()
    return {value for value in values if value and "|" not in value}


def enrichment(
    label: str,
    foreground: set[str],
    universe: set[str],
    annotations: dict[str, set[str]],
    names: dict[str, str],
    min_foreground: int,
    min_universe: int = 10,
    max_universe: int = 3000,
) -> tuple[dict, pd.DataFrame]:
    foreground_input_n = len(foreground)
    universe_input_n = len(universe)
    universe = universe & set(annotations)
    foreground = foreground & universe
    term_genes: dict[str, set[str]] = defaultdict(set)
    for gene in universe:
        for term in annotations[gene]:
            term_genes[term].add(gene)

    rows = []
    for term, genes in term_genes.items():
        background_n = len(genes)
        overlap = foreground & genes
        a = len(overlap)
        if a < min_foreground or background_n < min_universe or background_n > max_universe:
            continue
        b = len(foreground) - a
        c = background_n - a
        d = len(universe) - a - b - c
        if min(a, b, c, d) < 0:
            continue
        odds, p_value = stats.fisher_exact([[a, b], [c, d]], alternative="greater")
        rows.append(
            {
                "analysis": label,
                "go_id": term,
                "term": names.get(term, term),
                "foreground_overlap": a,
                "foreground_total": len(foreground),
                "universe_term_genes": background_n,
                "universe_total": len(universe),
                "odds_ratio": float(odds),
                "p_value": float(p_value),
                "overlap_symbols": ";".join(sorted(overlap)),
            }
        )
    result = pd.DataFrame(rows)
    if result.empty:
        result = pd.DataFrame(columns=[
            "analysis", "go_id", "term", "foreground_overlap", "foreground_total",
            "universe_term_genes", "universe_total", "odds_ratio", "p_value",
            "overlap_symbols", "fdr",
        ])
    else:
        result["fdr"] = bh(result["p_value"].to_numpy())
        result = result.sort_values(["fdr", "p_value", "go_id"])
    summary = {
        "analysis": label,
        "foreground_total_input": foreground_input_n,
        "universe_total_input": universe_input_n,
        "foreground_annotated": len(foreground),
        "annotated_universe": len(universe),
        "terms_tested": int(len(result)),
        "terms_fdr_below_0_05": int((result["fdr"] < 0.05).sum()) if len(result) else 0,
    }
    return summary, result


def main() -> None:
    names, parents, ontology_version = parse_obo(require(DATA_DIR / "go-basic.obo", "GO ontology"))
    direct, gaf_version = parse_gaf(require(DATA_DIR / "mgi.gaf.gz", "MGI GO annotations"))
    annotations = propagate_annotations(direct, parents)

    osd255 = pd.read_csv(
        require(DATA_DIR / OSD255_DE, "OSD-255 DE table"),
        usecols=["ENSEMBL", "SYMBOL", "Adj.p.value_(Space Flight)v(Ground Control)"],
        low_memory=False,
    )
    osd255_fdr = pd.to_numeric(
        osd255["Adj.p.value_(Space Flight)v(Ground Control)"], errors="coerce"
    )
    transcriptome = valid_symbols(osd255["SYMBOL"])
    panel = valid_symbols(osd255.loc[osd255_fdr < 0.05, "SYMBOL"])

    candidates_frame = pd.read_csv(RESULTS_DIR / "osd203_7d_radiation_candidates.csv")
    candidates = valid_symbols(candidates_frame["SYMBOL_osd255"])

    validation = pd.read_csv(RESULTS_DIR / "gravity_validation_genes.csv")
    osd203 = pd.read_csv(
        require(DATA_DIR / OSD203_DE, "OSD-203 DE table"),
        usecols=["ENSEMBL", RADIATION_COLUMN],
        low_memory=False,
    )
    osd203["gene_id"] = osd203["ENSEMBL"].astype(str).str.replace(r"\.\d+$", "", regex=True)
    osd203["radiation_log2fc"] = pd.to_numeric(osd203[RADIATION_COLUMN], errors="coerce")
    merged = validation.merge(osd203[["gene_id", "radiation_log2fc"]], on="gene_id", how="inner")
    concordant = valid_symbols(
        merged.loc[
            (merged["osd758_1G_vs_ground"] * merged["radiation_log2fc"]) > 0,
            "SYMBOL_osd255",
        ]
    )

    specs = [
        ("OSD-255 discovery panel vs transcriptome", panel, transcriptome, 3, 10, 3000),
        ("Seven-day radiation-concordant genes vs OSD-255 panel", concordant, panel, 3, 5, 300),
        ("Nine radiation-compatible candidates vs OSD-255 panel", candidates, panel, 2, 2, 300),
    ]
    summaries = []
    tables = []
    for args in specs:
        label, foreground, universe, min_fg, min_bg, max_bg = args
        summary, table = enrichment(
            label, foreground, universe, annotations, names, min_fg, min_bg, max_bg
        )
        summaries.append(summary)
        tables.append(table.head(100))

    combined = pd.concat(tables, ignore_index=True)
    combined.to_csv(RESULTS_DIR / "go_enrichment.csv", index=False)
    payload = {
        "project": "RetinaCellTwin",
        "analysis": "Gene Ontology Biological Process over-representation",
        "ontology_version": ontology_version,
        "gaf_version": gaf_version,
        "annotation_policy": "MGI Biological Process annotations propagated through is_a and part_of ancestors; NOT annotations excluded",
        "multiple_testing": "Benjamini-Hochberg within each prespecified analysis",
        "analyses": summaries,
        "interpretation": (
            "OSD-255 enrichment is a reproducibility/context analysis because RR-9 pathway enrichment was previously published. "
            "Candidate-set analyses are exploratory and do not establish mechanism."
        ),
    }
    (RESULTS_DIR / "go_enrichment.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
