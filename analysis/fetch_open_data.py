#!/usr/bin/env python3
"""Fetch prespecified public RR-9 retina tables and record provenance."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests

from config import DATA_DIR, MANIFEST

TIMEOUT = 180


def get_json(session: requests.Session, url: str) -> dict:
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def download(session: requests.Session, url: str, destination: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    temporary = destination.with_suffix(destination.suffix + ".part")
    with session.get(url, stream=True, timeout=TIMEOUT) as response:
        response.raise_for_status()
        with temporary.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if not chunk:
                    continue
                handle.write(chunk)
                digest.update(chunk)
                size += len(chunk)
    temporary.replace(destination)
    return size, digest.hexdigest()


def checksum_existing(destination: Path, expected_size: int | None) -> tuple[int, str] | None:
    """Reuse an intact local download while rebuilding provenance records."""
    if not destination.is_file():
        return None
    size = destination.stat().st_size
    if expected_size is not None and size != expected_size:
        return None
    digest = hashlib.sha256()
    with destination.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return size, digest.hexdigest()


def fetch_metadata(session: requests.Session, base: str, accession: str) -> tuple[str, bytes]:
    url = (
        f"{base}/query/metadata/?id.accession={accession}"
        "&study.factor%20value&format=csv"
    )
    response = session.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    # Parse once so an HTML error page can never be stored as metadata.
    rows = list(csv.reader(io.StringIO(response.text)))
    if not rows or "id.sample name" not in rows[0]:
        raise ValueError(f"Unexpected metadata response for {accession}")
    return url, response.content


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    base = manifest["api_base"].rstrip("/")
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    downloaded_data_files = 0

    with requests.Session() as session:
        session.headers.update({"User-Agent": "RetinaCellTwin/0.3 (+open-science)"})
        for accession, dataset in manifest["datasets"].items():
            files_url = f"{base}/dataset/{accession}/files/"
            listing = get_json(session, files_url)[accession]["files"]

            metadata_url, metadata_bytes = fetch_metadata(session, base, accession)
            metadata_path = DATA_DIR / f"{accession}_sample_metadata.csv"
            metadata_path.write_bytes(metadata_bytes)
            records.append(
                {
                    "accession": accession,
                    "kind": "sample metadata",
                    "local_file": metadata_path.name,
                    "source_url": metadata_url,
                    "bytes": len(metadata_bytes),
                    "sha256": hashlib.sha256(metadata_bytes).hexdigest(),
                }
            )

            for name in dataset["files"]:
                if name not in listing:
                    raise KeyError(f"{name} is not listed by {accession}")
                entry = listing[name]
                detail = get_json(session, entry["REST_URL"])[accession]["files"][name]
                metadata = detail.get("metadata", {})
                if metadata.get("restricted") is not False or metadata.get("visible") is not True:
                    raise PermissionError(f"Refusing non-public file: {accession}/{name}")
                destination = DATA_DIR / name
                expected_size = metadata.get("file_size")
                expected_size = int(expected_size) if expected_size is not None else None
                cached = checksum_existing(destination, expected_size)
                if cached:
                    size, sha256 = cached
                else:
                    size, sha256 = download(session, entry["URL"], destination)
                    downloaded_data_files += 1
                if expected_size is not None and size != int(expected_size):
                    raise IOError(
                        f"Size mismatch for {name}: downloaded {size}, expected {expected_size}"
                    )
                records.append(
                    {
                        "accession": accession,
                        "kind": metadata.get("data_type", "data file"),
                        "category": metadata.get("category"),
                        "local_file": destination.name,
                        "source_url": entry["URL"],
                        "api_record": entry["REST_URL"],
                        "restricted": metadata.get("restricted"),
                        "visible": metadata.get("visible"),
                        "bytes": size,
                        "sha256": sha256,
                    }
                )

    payload = {
        "project": "RetinaCellTwin",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "manifest": str(MANIFEST.relative_to(MANIFEST.parents[1])),
        "files": records,
    }
    (DATA_DIR / "provenance.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(
        f"Verified {len(records)} public records in {DATA_DIR}; "
        f"downloaded {downloaded_data_files} data files"
    )


if __name__ == "__main__":
    main()
