import ast
import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


class ReleaseTests(unittest.TestCase):
    def test_required_project_files(self):
        required = [
            "README.md",
            "LICENSE",
            "CITATION.cff",
            "environment.yml",
            "requirements.txt",
            "requirements-lock.txt",
            "Dockerfile",
            "run_all.sh",
            "docs/REPRODUCIBILITY.md",
            "manuscript/GIGASCIENCE_RESEARCH_ARTICLE.md",
            "manuscript/RetinaCellTwin_GigaScience_Submission_Draft.docx",
            "manuscript/build_gigascience_docx.py",
            "manuscript/SUPPLEMENTARY_METHODS.md",
            "manuscript/SUBMISSION_CHECKLIST.md",
            "manuscript/COVER_LETTER_DRAFT.md",
            "manuscript/CREDIT_CONTRIBUTIONS_DRAFT.md",
            "manuscript/AI_DISCLOSURE_DRAFT.md",
            "manuscript/EDITORIAL_PACKAGE.md",
            "data/datasets.json",
            "data/retinal_cell_anchors.tsv",
            "analysis/fetch_open_data.py",
            "analysis/analyze_open_data.py",
            "analysis/analyze_gravity_hypothesis.py",
            "analysis/analyze_sample_level_audit.py",
            "analysis/analyze_count_level_audit.py",
            "analysis/fetch_functional_data.py",
            "analysis/analyze_go_enrichment.py",
            "analysis/analyze_cell_context.py",
            "analysis/analyze_cross_modal_context.py",
            "analysis/make_figures.py",
            "data/functional_sources.json",
            "index.html",
            "app.js",
            "dist/results/cross_modal_context.json",
        ]
        for name in required:
            self.assertTrue((ROOT / name).is_file(), name)

    def test_python_syntax(self):
        for path in (ROOT / "analysis").glob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_manifest_has_five_public_sources(self):
        manifest = json.loads((ROOT / "data" / "datasets.json").read_text())
        self.assertEqual(
            set(manifest["datasets"]),
            {"OSD-203", "OSD-255", "OSD-557", "OSD-568", "OSD-758"},
        )
        self.assertEqual(sum(len(x["files"]) for x in manifest["datasets"].values()), 20)

    def test_generated_results_if_present(self):
        summary_path = ROOT / "results" / "summary.json"
        if not summary_path.exists():
            self.skipTest("analysis has not been run")
        summary = json.loads(summary_path.read_text())
        self.assertEqual(summary["project"], "RetinaCellTwin")
        self.assertEqual(
            summary["evidence_layers"]["observed"],
            ["OSD-203", "OSD-255", "OSD-557", "OSD-568", "OSD-758"],
        )
        imaging = pd.read_csv(ROOT / "results" / "imaging_endpoints.csv")
        self.assertEqual(len(imaging), 7)
        self.assertTrue((imaging[["n_flight", "n_ground"]] >= 2).all().all())
        self.assertTrue(imaging["welch_fdr"].dropna().between(0, 1).all())
        self.assertEqual(len(pd.read_csv(ROOT / "results" / "osd255_top_genes.csv")), 100)

    def test_cross_mission_results_if_present(self):
        path = ROOT / "results" / "gravity_hypothesis.json"
        if not path.exists():
            self.skipTest("cross-mission analysis has not been run")
        result = json.loads(path.read_text())
        gravity = result["gravity_validation"]
        decision = result["decision_summary"]
        self.assertEqual(gravity["discovery_panel_genes"], 362)
        self.assertEqual(gravity["mapped_to_osd758"], 362)
        self.assertFalse(decision["rr9_signature_replicated_in_osd758"])
        self.assertFalse(decision["rr9_panel_specific_artificial_gravity_attenuation"])
        self.assertEqual(decision["strict_gravity_sensitive_candidates"], 0)
        self.assertTrue(decision["seven_day_radiation_concordance_panel_enriched"])
        candidates = pd.read_csv(ROOT / "results" / "osd203_7d_radiation_candidates.csv")
        self.assertEqual(len(candidates), 9)

    def test_download_provenance_if_present(self):
        path = ROOT / "data" / "provenance.json"
        if not path.exists():
            self.skipTest("open data have not been fetched")
        provenance = json.loads(path.read_text())
        self.assertEqual(len(provenance["files"]), 25)
        local_files = [ROOT / "data" / record["local_file"] for record in provenance["files"]]
        if not any(local.is_file() for local in local_files):
            return
        for record in provenance["files"]:
            local = ROOT / "data" / record["local_file"]
            self.assertTrue(local.is_file(), record["local_file"])
            digest = hashlib.sha256(local.read_bytes()).hexdigest()
            self.assertEqual(digest, record["sha256"], record["local_file"])
            if record["kind"] != "sample metadata":
                self.assertIs(record["restricted"], False)
                self.assertIs(record["visible"], True)

    def test_sample_level_audit_if_present(self):
        path = ROOT / "results" / "sample_level_audit.json"
        if not path.exists():
            self.skipTest("sample-level audit has not been run")
        result = json.loads(path.read_text())
        contrasts = result["contrasts"]
        self.assertEqual(len(contrasts), 10)
        self.assertTrue(all(row["vst_vs_nasa_spearman_rho"] > 0.8 for row in contrasts))
        self.assertTrue(all(row["direction_fraction"] > 0.9 for row in contrasts))
        self.assertTrue(
            all(
                isinstance(row["genes_with_zero_variance_in_both_groups"], int)
                and row["genes_with_zero_variance_in_both_groups"] >= 0
                for row in contrasts
            )
        )
        top = pd.read_csv(ROOT / "results" / "sample_level_audit_top_genes.csv")
        self.assertEqual(set(top["contrast"]), {row["contrast"] for row in contrasts})

    def test_count_level_audit_if_present(self):
        path = ROOT / "results" / "count_level_audit.json"
        if not path.exists():
            self.skipTest("count-level audit has not been run")
        result = json.loads(path.read_text())
        contrasts = result["contrasts"]
        self.assertEqual(len(contrasts), 10)
        self.assertTrue(all(row["count_vs_nasa_spearman_rho"] > 0.75 for row in contrasts))
        self.assertTrue(all(row["direction_fraction"] > 0.8 for row in contrasts))
        top = pd.read_csv(ROOT / "results" / "count_level_audit_top_genes.csv")
        self.assertEqual(set(top["contrast"]), {row["contrast"] for row in contrasts})

    def test_go_enrichment_if_present(self):
        path = ROOT / "results" / "go_enrichment.json"
        if not path.exists():
            self.skipTest("GO enrichment has not been run")
        result = json.loads(path.read_text())
        analyses = result["analyses"]
        self.assertEqual(len(analyses), 3)
        self.assertGreater(analyses[0]["terms_fdr_below_0_05"], 0)
        self.assertEqual(analyses[1]["terms_fdr_below_0_05"], 0)
        self.assertEqual(analyses[2]["terms_fdr_below_0_05"], 0)
        table = pd.read_csv(ROOT / "results" / "go_enrichment.csv")
        self.assertTrue(table["fdr"].between(0, 1).all())

    def test_cell_class_anchor_audit_if_present(self):
        path = ROOT / "results" / "cell_class_anchor_audit.json"
        if not path.exists():
            self.skipTest("cell-class anchor audit has not been run")
        result = json.loads(path.read_text())
        summaries = {row["contrast"]: row for row in result["summaries"]}
        self.assertEqual(len(summaries), 4)
        self.assertTrue(all(row["anchors_mapped"] == 12 for row in summaries.values()))
        self.assertEqual(summaries["osd255_flight_vs_ground"]["anchors_fdr_below_0_05"], 1)
        self.assertEqual(
            summaries["osd255_flight_vs_ground"]["significant_anchors"][0]["marker_symbol"],
            "Arr3",
        )
        self.assertTrue(
            all(
                summaries[label]["anchors_fdr_below_0_05"] == 0
                for label in summaries
                if label != "osd255_flight_vs_ground"
            )
        )
        table = pd.read_csv(ROOT / "results" / "cell_class_anchor_audit.csv")
        self.assertEqual(len(table), 12)
        self.assertEqual(table["marker_symbol"].nunique(), 12)

    def test_cross_modal_context_if_present(self):
        path = ROOT / "results" / "cross_modal_context.json"
        if not path.exists():
            self.skipTest("cross-modal synthesis has not been run")
        result = json.loads(path.read_text())
        rows = {row["domain"]: row for row in result["rows"]}
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            rows["Photoreceptor integrity"]["integration_classification"],
            "study-level contextual convergence",
        )
        self.assertEqual(
            rows["Apoptosis"]["integration_classification"],
            "imaging-only FDR-supported evidence",
        )
        self.assertEqual(
            rows["Oxidative stress"]["imaging_endpoints_fdr_below_0_05"], 0
        )
        self.assertEqual(
            rows["Vascular/barrier integrity"]["imaging_endpoints_fdr_below_0_05"],
            0,
        )

    def test_publication_figures_if_present(self):
        figures = ROOT / "figures"
        if not figures.exists():
            self.skipTest("publication figures have not been generated")
        expected = {
            "figure1_evidence_architecture.svg",
            "figure2_cross_mission_direction.svg",
            "figure3_audit_concordance.svg",
            "figure4_go_context.svg",
            "figure5_cell_class_context.svg",
            "figure6_cross_modal_context.svg",
        }
        self.assertEqual({path.name for path in figures.glob("*.svg")}, expected)
        for name in expected:
            root = ET.parse(figures / name).getroot()
            self.assertTrue(root.tag.endswith("svg"), name)

    def test_no_machine_paths_in_interface(self):
        for name in ("index.html", "app.js", "styles.css"):
            self.assertNotIn("/workspace/", (ROOT / name).read_text(encoding="utf-8"))

    def test_interface_exposes_cross_modal_boundaries(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        script = (ROOT / "app.js").read_text(encoding="utf-8")
        self.assertIn("Unpaired multimodal synthesis", html)
        self.assertIn("different OSDR accessions and opposite eyes", html)
        self.assertIn("Observed contextual convergence", script)
        self.assertIn("Imaging-only evidence", script)
        self.assertIn("Not supported across modalities", script)

    def test_deployed_interface_matches_release_sources(self):
        mirrored = [
            "app.js",
            "index.html",
            "styles.css",
            "results/summary.json",
            "results/gravity_hypothesis.json",
            "results/cross_modal_context.json",
        ]
        for name in mirrored:
            self.assertEqual(
                (ROOT / name).read_bytes(),
                (ROOT / "dist" / name).read_bytes(),
                name,
            )


if __name__ == "__main__":
    unittest.main()
