#!/usr/bin/env python3
"""Generate publication-ready SVG figures from frozen result tables."""

from __future__ import annotations

import html
import json
import math
from pathlib import Path

import pandas as pd

from config import REPO_ROOT, RESULTS_DIR


FIGURES = REPO_ROOT / "figures"
FONT = "Arial, Helvetica, sans-serif"


def esc(value: object) -> str:
    return html.escape(str(value))


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f"<title>{esc(title)}</title>",
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]


def text(x: float, y: float, value: object, size: int = 18, weight: int = 400, anchor: str = "start", fill: str = "#172033") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
        f'font-weight="{weight}" text-anchor="{anchor}" fill="{fill}">{esc(value)}</text>'
    )


def write(name: str, parts: list[str]) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    parts.append("</svg>")
    (FIGURES / name).write_text("\n".join(parts), encoding="utf-8")


def evidence_architecture() -> None:
    width, height = 1400, 760
    parts = svg_header(width, height, "RetinaCellTwin evidence architecture")
    parts += [
        text(60, 62, "RetinaCellTwin evidence architecture", 30, 700),
        text(60, 95, "Observed data, derived tests and hypotheses remain explicitly separated", 17, 400, fill="#4b5563"),
    ]
    boxes = [
        (60, 160, 300, 160, "OSD-255 · RR-9", "Discovery", "362 genes at NASA FDR < 0.05", "#e8f0ff", "#3158a6"),
        (430, 160, 300, 160, "OSD-758", "External gravity audit", "uG · 0.33G · 0.66G · 1G", "#ecf8f1", "#25714f"),
        (800, 160, 300, 160, "OSD-203", "Ground analogues", "Radiation and unloading · 3 times", "#fff4e5", "#a75b13"),
        (60, 440, 300, 160, "OSD-557 / OSD-568", "Imaging context", "4-HNE · PNA · TUNEL · PECAM · ZO-1", "#f4ecfb", "#7b3ea8"),
        (430, 440, 300, 160, "Verification", "Independent audits", "VST contrasts · STAR-count effects", "#eef2f6", "#425466"),
        (800, 440, 300, 160, "Bounded hypothesis", "Prospective only", "Transient radiation-compatible component", "#fdecef", "#a8324a"),
    ]
    for x, y, w, h, title, subtitle, body, fill, stroke in boxes:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        parts.append(text(x + 24, y + 42, title, 22, 700, fill=stroke))
        parts.append(text(x + 24, y + 78, subtitle, 18, 700))
        parts.append(text(x + 24, y + 116, body, 15, 400, fill="#4b5563"))
    arrows = [
        (360, 240, 430, 240),
        (730, 240, 800, 240),
        (580, 320, 580, 440),
        (950, 320, 950, 440),
        (360, 520, 430, 520),
        (730, 520, 800, 520),
    ]
    parts.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#667085"/></marker></defs>')
    for x1, y1, x2, y2 in arrows:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#667085" stroke-width="3" marker-end="url(#arrow)"/>')
    parts += [
        text(1160, 190, "Primary decision", 18, 700),
        text(1160, 225, "Universal gravity", 16),
        text(1160, 250, "signature: not supported", 16, 700, fill="#a8324a"),
        text(1160, 315, "Secondary signal", 18, 700),
        text(1160, 350, "7-day radiation-compatible", 16),
        text(1160, 375, "panel enrichment: supported", 16, 700, fill="#25714f"),
        text(1160, 440, "Boundary", 18, 700),
        text(1160, 475, "No causal attribution", 16),
        text(1160, 500, "No human SANS prediction", 16),
        text(1160, 525, "No individual-level twin", 16),
    ]
    write("figure1_evidence_architecture.svg", parts)


def cross_mission_direction() -> None:
    gravity = json.loads((RESULTS_DIR / "gravity_hypothesis.json").read_text())
    rows = [
        ("RR-9 vs OSD-758 uG", 100 * gravity["gravity_validation"]["rr9_vs_osd758_uG_direction_fraction"]),
    ]
    for row in gravity["analog_attribution"]:
        if row["mechanism"] == "radiation":
            rows.append((f"OSD-203 radiation · {row['time']}", 100 * row["direction_fraction"]))
    width, height = 1200, 560
    parts = svg_header(width, height, "Directional concordance across missions and times")
    parts += [
        text(55, 55, "Directional concordance across missions and times", 28, 700),
        text(55, 88, "The dashed 50% line represents chance-level direction agreement", 16, fill="#4b5563"),
    ]
    x0, x1 = 380, 1120
    top, row_h = 145, 85
    parts.append(f'<line x1="{x0 + (x1-x0)*0.5}" y1="120" x2="{x0 + (x1-x0)*0.5}" y2="470" stroke="#8a94a6" stroke-width="2" stroke-dasharray="7 7"/>')
    for i, (label, value) in enumerate(rows):
        y = top + i * row_h
        color = "#2f6fba" if value >= 50 else "#b54b5f"
        parts.append(text(x0 - 18, y + 23, label, 17, 600, anchor="end"))
        parts.append(f'<rect x="{x0}" y="{y}" width="{(x1-x0)*value/100:.1f}" height="34" rx="6" fill="{color}"/>')
        parts.append(text(x0 + (x1-x0)*value/100 + 12, y + 24, f"{value:.1f}%", 17, 700, fill=color))
    for tick in (0, 25, 50, 75, 100):
        x = x0 + (x1 - x0) * tick / 100
        parts.append(f'<line x1="{x}" y1="480" x2="{x}" y2="489" stroke="#172033"/>')
        parts.append(text(x, 515, tick, 14, anchor="middle"))
    parts.append(text((x0 + x1) / 2, 550, "Genes with concordant effect direction (%)", 16, 600, anchor="middle"))
    write("figure2_cross_mission_direction.svg", parts)


def audit_concordance() -> None:
    vst = json.loads((RESULTS_DIR / "sample_level_audit.json").read_text())["contrasts"]
    count = json.loads((RESULTS_DIR / "count_level_audit.json").read_text())["contrasts"]
    labels = [
        "255 Flight/Ground", "758 uG/Ground", "758 uG/Flight 1G", "758 Flight 1G/Ground",
        "203 7d Rad", "203 7d HLU", "203 1m Rad", "203 1m HLU", "203 4m Rad", "203 4m HLU",
    ]
    width, height = 1450, 690
    parts = svg_header(width, height, "Effect concordance with NASA differential-expression results")
    parts += [
        text(55, 55, "Effect concordance with NASA differential-expression results", 28, 700),
        text(55, 88, "Spearman rank correlation across ten prespecified contrasts", 16, fill="#4b5563"),
    ]
    x0, x1, y0, y1 = 105, 1390, 130, 555
    for tick in (0.6, 0.7, 0.8, 0.9, 1.0):
        y = y1 - (tick - 0.6) / 0.4 * (y1 - y0)
        parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#e2e6ea"/>')
        parts.append(text(x0 - 18, y + 5, f"{tick:.1f}", 14, anchor="end"))
    step = (x1 - x0) / len(labels)
    for i, label in enumerate(labels):
        x = x0 + step * (i + 0.5)
        vst_value = vst[i]["vst_vs_nasa_spearman_rho"]
        count_value = count[i]["count_vs_nasa_spearman_rho"]
        for dx, value, color in ((-13, vst_value, "#3158a6"), (13, count_value, "#d06b2d")):
            y = y1 - (value - 0.6) / 0.4 * (y1 - y0)
            parts.append(f'<circle cx="{x+dx:.1f}" cy="{y:.1f}" r="8" fill="{color}"/>')
        parts.append(text(x, 590, label, 12, 600, anchor="middle"))
    parts += [
        '<circle cx="520" cy="645" r="8" fill="#3158a6"/>', text(538, 650, "VST mean-difference audit", 15),
        '<circle cx="820" cy="645" r="8" fill="#d06b2d"/>', text(838, 650, "STAR-count effect audit", 15),
        text(32, 355, "Spearman rho", 15, 600, anchor="middle"),
    ]
    write("figure3_audit_concordance.svg", parts)


def go_terms() -> None:
    frame = pd.read_csv(RESULTS_DIR / "go_enrichment.csv")
    frame = frame.loc[frame["analysis"] == "OSD-255 discovery panel vs transcriptome"].head(10).copy()
    frame["score"] = -frame["fdr"].map(math.log10)
    width, height = 1350, 720
    parts = svg_header(width, height, "Top GO Biological Process terms in the OSD-255 discovery panel")
    parts += [
        text(55, 55, "Top GO Biological Process terms in the OSD-255 discovery panel", 28, 700),
        text(55, 88, "Contextual reproduction analysis; terms ranked by −log10(FDR)", 16, fill="#4b5563"),
    ]
    x0, x1, top, row_h = 520, 1260, 130, 52
    max_score = max(6.0, float(frame["score"].max()) * 1.08)
    for i, row in frame.reset_index(drop=True).iterrows():
        y = top + i * row_h
        score = float(row["score"])
        parts.append(text(x0 - 18, y + 20, row["term"], 15, 600, anchor="end"))
        parts.append(f'<rect x="{x0}" y="{y}" width="{(x1-x0)*score/max_score:.1f}" height="30" rx="5" fill="#4067b1"/>')
        parts.append(text(x0 + (x1-x0)*score/max_score + 10, y + 21, f"{score:.2f}", 14, 700, fill="#3158a6"))
    parts.append(text((x0 + x1) / 2, 685, "−log10(FDR)", 16, 600, anchor="middle"))
    parts.append(text(55, 655, "No GO term passed FDR < 0.05 in the radiation-concordant or nine-candidate subset analyses.", 16, 600, fill="#a8324a"))
    write("figure4_go_context.svg", parts)


def cell_context() -> None:
    frame = pd.read_csv(RESULTS_DIR / "cell_class_anchor_audit.csv")
    contrasts = [
        ("osd255_flight_vs_ground", "RR-9 flight / ground"),
        ("osd758_microgravity_vs_ground", "OSD-758 uG / ground"),
        ("osd758_inflight_1g_vs_ground", "OSD-758 flight 1G / ground"),
        ("osd203_7d_radiation_vs_control", "OSD-203 7d radiation / control"),
    ]
    width, height = 1450, 850
    parts = svg_header(width, height, "Canonical retinal cell-class anchors in bulk OSDR contrasts")
    parts += [
        text(55, 55, "Canonical retinal cell-class anchors in bulk OSDR contrasts", 28, 700),
        text(55, 88, "Marker anchors from Li et al. 2024 Figure 1E; color is NASA log2 fold change", 16, fill="#4b5563"),
    ]
    x0, y0, cell_w, cell_h = 610, 160, 185, 47
    for j, (_, label) in enumerate(contrasts):
        parts.append(text(x0 + j * cell_w + cell_w / 2, 130, label, 14, 600, anchor="middle"))
    for i, row in frame.iterrows():
        y = y0 + i * cell_h
        parts.append(text(55, y + 29, row["cell_class"], 15, 600))
        parts.append(text(360, y + 29, row["marker_symbol"], 15, 700, fill="#4b5563"))
        for j, (key, _) in enumerate(contrasts):
            value = float(row[f"{key}_log2fc"])
            fdr = row[f"{key}_fdr"]
            strength = min(abs(value) / 2.0, 1.0)
            if value >= 0:
                red = int(247 - 110 * strength)
                green = int(247 - 170 * strength)
                blue = int(247 - 165 * strength)
            else:
                red = int(247 - 170 * strength)
                green = int(247 - 115 * strength)
                blue = int(247 - 55 * strength)
            fill = f"#{red:02x}{green:02x}{blue:02x}"
            x = x0 + j * cell_w
            parts.append(f'<rect x="{x}" y="{y}" width="{cell_w-6}" height="{cell_h-6}" rx="5" fill="{fill}"/>')
            star = " *" if pd.notna(fdr) and float(fdr) < 0.05 else ""
            parts.append(text(x + (cell_w-6)/2, y + 27, f"{value:+.2f}{star}", 14, 700, anchor="middle"))
    legend_y = 755
    parts += [
        text(55, legend_y, "Blue: lower expression", 15, 600, fill="#3158a6"),
        text(250, legend_y, "Red: higher expression", 15, 600, fill="#a8324a"),
        text(465, legend_y, "* NASA FDR < 0.05", 15, 600),
        text(55, 805, "These anchors provide context only: bulk RNA-seq cannot identify cell fractions or cell-intrinsic regulation.", 16, 600, fill="#a8324a"),
    ]
    write("figure5_cell_class_context.svg", parts)


def cross_modal_context() -> None:
    frame = pd.read_csv(RESULTS_DIR / "cross_modal_context.csv")
    width, height = 1450, 650
    parts = svg_header(width, height, "Unpaired cross-modal evidence matrix")
    parts += [
        text(55, 55, "Unpaired cross-modal evidence matrix", 28, 700),
        text(55, 88, "Study-level context only; RNA-seq and imaging are not sample-paired", 16, fill="#4b5563"),
        text(420, 135, "Imaging", 17, 700, anchor="middle"),
        text(790, 135, "Transcriptomic context", 17, 700, anchor="middle"),
        text(1180, 135, "Integrated classification", 17, 700, anchor="middle"),
    ]
    y0, row_h = 170, 95
    status_colors = {
        "FDR-supported": ("#e5f5eb", "#25714f"),
        "FDR-supported context": ("#e5f5eb", "#25714f"),
        "not FDR-supported": ("#f2f4f7", "#596579"),
        "not directly tested": ("#fff4e5", "#a75b13"),
        "broad context only": ("#fff4e5", "#a75b13"),
    }
    for i, row in frame.iterrows():
        y = y0 + i * row_h
        parts.append(text(55, y + 34, row["domain"], 17, 700))
        for x, value in ((275, row["imaging_status"]), (645, row["transcript_status"])):
            fill, stroke = status_colors.get(value, ("#f2f4f7", "#596579"))
            parts.append(f'<rect x="{x}" y="{y}" width="290" height="55" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
            parts.append(text(x + 145, y + 34, value, 15, 700, anchor="middle", fill=stroke))
        integration = row["integration_classification"]
        supported = integration in {
            "study-level contextual convergence",
            "imaging-only FDR-supported evidence",
        }
        fill, stroke = ("#e8f0ff", "#3158a6") if supported else ("#f2f4f7", "#596579")
        parts.append(f'<rect x="{1015}" y="{y}" width="370" height="55" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        parts.append(text(1200, y + 34, integration, 14, 700, anchor="middle", fill=stroke))
    parts += [
        text(55, 590, "Photoreceptor convergence does not imply paired association or causal mediation.", 16, 700, fill="#a8324a"),
        text(55, 620, "Apoptosis is imaging-only; oxidative and vascular/barrier domains do not cross the current FDR boundary.", 16, fill="#4b5563"),
    ]
    write("figure6_cross_modal_context.svg", parts)


def main() -> None:
    evidence_architecture()
    cross_mission_direction()
    audit_concordance()
    go_terms()
    cell_context()
    cross_modal_context()
    print(f"Generated 6 SVG figures in {FIGURES}")


if __name__ == "__main__":
    main()
