import ast
import hashlib
import json
import unittest
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
            "data/datasets.json",
            "analysis/fetch_open_data.py",
            "analysis/analyze_open_data.py",
            "analysis/analyze_gravity_hypothesis.py",
            "index.html",
            "app.js",
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
        self.assertEqual(sum(len(x["files"]) for x in manifest["datasets"].values()), 14)

    def test_generated_results_if_present(self):
        summary_path = ROOT / "results" / "summary.json"
        if not summary_path.exists():
            self.skipTest("analysis has not been run")
        summary = json.loads(summary_path.read_text())
        self.assertEqual(summary["project"], "RetinaCellTwin")
        self.assertEqual(summary["evidence_layers"]["observed"], ["OSD-255", "OSD-557", "OSD-568"])
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
        self.assertEqual(len(provenance["files"]), 19)
        for record in provenance["files"]:
            local = ROOT / "data" / record["local_file"]
            self.assertTrue(local.is_file(), record["local_file"])
            digest = hashlib.sha256(local.read_bytes()).hexdigest()
            self.assertEqual(digest, record["sha256"], record["local_file"])
            if record["kind"] != "sample metadata":
                self.assertIs(record["restricted"], False)
                self.assertIs(record["visible"], True)

    def test_no_machine_paths_in_interface(self):
        for name in ("index.html", "app.js", "styles.css"):
            self.assertNotIn("/workspace/", (ROOT / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
