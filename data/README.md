# Data inputs

Run `python analysis/fetch_open_data.py` to retrieve the selected open tables from NASA OSDR.

The fetcher:

- resolves each filename through the official OSDR Biological Data API;
- refuses files marked restricted or invisible;
- saves sample-level spaceflight-factor metadata for each accession;
- records the source URL, API record, byte count, SHA-256 checksum and UTC retrieval time in `provenance.json`.

Downloaded inputs are excluded from Git by default because NASA OSDR is the authoritative source. The manifest `datasets.json`, workflow and derived results are versioned.

Do not infer experimental groups from filenames when metadata are available. The analysis joins measurements to the OSDR sample-level factor table.

