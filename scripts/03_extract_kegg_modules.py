import os
import time
import hashlib
import requests

KEGG_BASE = "https://rest.kegg.jp"
RAW_DIR = "data/raw/kegg/"
EXPECTED_RELEASE = "118.0"
PROVENANCE_PATH = "data/PROVENANCE.md"
REQUEST_DELAY = 0.4


def get_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def verify_release(expected: str = EXPECTED_RELEASE) -> str:
    """GET /info/kegg, parse the release line, assert `expected` in it.
    Returns the full release line for logging. Raises on mismatch."""
    response = requests.get(f"{KEGG_BASE}/info/kegg")

    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: failed to fetch KEGG info")

    lines = response.text.splitlines()
    release_line = next((line for line in lines if "Release" in line), None)

    if release_line is None:
        raise ValueError("No 'Release' line found in KEGG response")

    release_line = release_line.strip()

    if expected not in release_line:
        raise AssertionError(
            f"Expected '{expected}' not found in release line: {release_line}"
        )

    time.sleep(REQUEST_DELAY)
    return release_line


def fetch_raw(endpoint, filename) -> str:
    path = os.path.join(RAW_DIR, filename)
    if os.path.exists(path):
        print(f"[cache] {filename}")
        return path

    response = requests.get(f"{KEGG_BASE}/{endpoint}")

    if response.status_code != 200:
        raise RuntimeError(f"HTTP {response.status_code}: failed {endpoint}")

    if not response.text.strip():
        raise RuntimeError(f"Empty body from {endpoint}")

    with open(path, "w") as f:
        f.write(response.text)

    time.sleep(REQUEST_DELAY)
    return path


def write_provenance(release, sha256_map, endpoints) -> None:
    with open(PROVENANCE_PATH, "r") as f:
        provenance = f.read()

    if "## KEGG Module Database" in provenance:
        print("[skip] KEGG provenance already recorded")
        return

    lines = [
        "",
        "## KEGG Module Database",
        f"* **Release**: {release}",
        "* **Fetch date**: 2026-06-08",
        f"* **Source**: {KEGG_BASE}",
        f"* **Endpoints**: {', '.join(endpoints)}",
    ]

    for path, sha256 in sorted(sha256_map.items()):
        filename = os.path.basename(path)
        lines.append(f"* **{filename}**: {sha256}")

    section = "\n".join(lines) + "\n"

    with open(PROVENANCE_PATH, "a") as f:
        f.write(section)

    print("[ok] KEGG provenance appended")


def main():

    os.makedirs(RAW_DIR, exist_ok=True)

    release = verify_release()

    downloads = [
        ("link/hsa/module", "link_hsa_module.tsv"),
        ("link/compound/module", "link_compound_module.tsv"),
        ("list/module", "list_module.tsv"),
        ("link/hsa/hsa00010", "link_hsa_hsa00010.tsv"),
        ("link/compound/map00010", "link_compound_map00010.tsv"),
        ("link/hsa/hsa00020", "link_hsa_hsa00020.tsv"),
        ("link/compound/map00020", "link_compound_map00020.tsv"),
        ("link/hsa/hsa00260", "link_hsa_hsa00260.tsv"),
        ("link/compound/map00260", "link_compound_map00260.tsv"),
        ("link/hsa/hsa00670", "link_hsa_hsa00670.tsv"),
        ("link/compound/map00670", "link_compound_map00670.tsv"),
    ]

    paths = []

    for endpoint, filename in downloads:
        path = fetch_raw(endpoint, filename)
        paths.append(path)

    sha256_map = {}
    for path in paths:
        sha256_map[path] = get_sha256(path)

    endpoints = []

    for endpoint, _ in downloads:
        endpoints.append("/" + endpoint)

    write_provenance(release, sha256_map, endpoints)


if __name__ == "__main__":
    main()
