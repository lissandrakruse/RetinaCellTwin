#!/usr/bin/env python3
"""Fetch versioned public Gene Ontology inputs and record provenance."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import requests

from config import DATA_DIR, REPO_ROOT


MANIFEST = REPO_ROOT / "data" / "functional_sources.json"
PROVENANCE = REPO_ROOT / "data" / "functional_provenance.json"
TIMEOUT = 180


def file_identity(path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return size, digest.hexdigest()


def download(url: str, destination, expected_size: int, expected_sha256: str) -> tuple[int, str]:
    temporary = destination.with_suffix(destination.suffix + ".part")
    digest = hashlib.sha256()
    size = 0
    with requests.get(url, stream=True, timeout=TIMEOUT, headers={"User-Agent": "RetinaCellTwin/0.3"}) as response:
        response.raise_for_status()
        with temporary.open("wb") as handle:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    handle.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
    if size != expected_size or digest.hexdigest() != expected_sha256:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"Functional source changed for {destination.name}: expected "
            f"{expected_size} bytes/{expected_sha256}, received {size} bytes/{digest.hexdigest()}. "
            "Update the frozen source manifest only as a new reviewed release."
        )
    temporary.replace(destination)
    return size, digest.hexdigest()


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    records = []
    downloaded = 0
    for source in manifest["sources"]:
        destination = DATA_DIR / source["local_file"]
        expected_size = int(source["expected_bytes"])
        expected_sha256 = source["expected_sha256"]
        if destination.is_file():
            size, sha256 = file_identity(destination)
            if size == expected_size and sha256 == expected_sha256:
                records.append({**source, "bytes": size, "sha256": sha256})
                continue
        size, sha256 = download(
            source["url"], destination, expected_size, expected_sha256
        )
        downloaded += 1
        records.append({**source, "bytes": size, "sha256": sha256})
    payload = {
        "project": "RetinaCellTwin",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "sources": records,
    }
    PROVENANCE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"Verified {len(records)} functional annotation resources; "
        f"downloaded {downloaded}"
    )


if __name__ == "__main__":
    main()
