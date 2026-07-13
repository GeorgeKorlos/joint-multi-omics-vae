import os
import csv
import time
import datetime
import requests

from src.export.mapping import (
    get_sha256,
    load_gene_table,
    parse_idmapping_tsv,
    reconcile,
    assert_all_canonical,
    write_frozen_csv,
)

UNIPROT_BASE = "https://rest.uniprot.org"
RAW_DIR = "data/raw/uniprot"
RESULTS_TSV = os.path.join(RAW_DIR, "idmapping_results.tsv")
GENES_CSV = "data/processed/selected_genes.csv"
OUT_CSV = "data/processed/protein_accessions.csv"
DROPPED_LOG = "reports/dropped_genes.csv"
POLL_DELAY = 3


def submit_job(entrez_ids: list[str]) -> str:
    joint_ids_string = ",".join(entrez_ids)
    payload = {
        "from": "GeneID",
        "to": "UniProtKB-Swiss-Prot",
        "ids": joint_ids_string,
    }

    response = requests.post(f"{UNIPROT_BASE}/idmapping/run", data=payload)
    if response.status_code != 200:
        raise RuntimeError(
            f"HTTP {response.status_code}: idmapping submit failed — {response.text[:200]}"
        )
    return response.json()["jobId"]


def poll_until_done(job_id: str) -> None:
    tries = 0
    max_tries = 100
    while tries < max_tries:
        response = requests.get(f"{UNIPROT_BASE}/idmapping/status/{job_id}")
        if response.status_code != 200:
            raise RuntimeError(
                f"HTTP {response.status_code}: status check failed — {response.text[:200]}"
            )

        status = response.json().get("jobStatus")
        if status in ("RUNNING", "NEW"):
            tries += 1
            time.sleep(POLL_DELAY)
            continue
        return

    raise TimeoutError(
        f"UniProt idmapping job {job_id} did not finish after {max_tries} attempts"
    )


def get_results_url(job_id: str) -> str:
    response = requests.get(f"{UNIPROT_BASE}/idmapping/details/{job_id}")
    if response.status_code != 200:
        raise RuntimeError(
            f"HTTP {response.status_code}: details fetch failed — {response.text[:200]}"
        )
    redirect_url = response.json().get("redirectURL")
    if not redirect_url:
        raise RuntimeError(f"job {job_id} finished but details returned no redirectURL")
    return redirect_url.replace("/results/", "/results/stream/")


def fetch_results(results_url: str) -> str:
    params = {"format": "tsv", "fields": "accession,reviewed,organism_id"}
    response = requests.get(results_url, params=params)
    if response.status_code != 200:
        raise RuntimeError(
            f"HTTP {response.status_code}: results fetch failed — {response.text[:200]}"
        )
    if not response.text.strip():
        raise RuntimeError("empty results body")
    return response.text


def append_provenance(access_date, sha256, counts) -> None:
    with open("data/PROVENANCE.md", "r") as f:
        provenance = f.read()

    if "## UniProt ID Mapping" in provenance:
        print("[skip] UniProt provenance already recorded")
        return

    lines = [
        "",
        "## UniProt ID Mapping",
        f"* **Access date**: {access_date}",
        "* **Source**: https://rest.uniprot.org",
        "* **Mapping**: GeneID (Entrez) -> UniProtKB-Swiss-Prot",
        "* **Release**: none — UniProt ID mapping is continuously updated; "
        "access date is the reproducibility anchor",
        f"* **idmapping_results.tsv SHA256**: {sha256}",
        f"* **Coverage**: {counts['mapped']} mapped / "
        f"{counts['dropped_zero']} no-match / "
        f"{counts['dropped_ambiguous']} ambiguous, of 5000 genes",
    ]

    section = "\n".join(lines) + "\n"

    with open("data/PROVENANCE.md", "a") as f:
        f.write(section)

    print("[ok] UniProt provenance appended")


def main():
    os.makedirs(RAW_DIR, exist_ok=True)

    genes_rows = load_gene_table(GENES_CSV)

    entrez = []
    for r in genes_rows:
        entrez.append(r["entrez"])

    if os.path.exists(RESULTS_TSV):
        print("[cache] using cached UniProt results")
        with open(RESULTS_TSV, "r") as f:
            raw_tsv = f.read()

    else:
        job_id = submit_job(entrez)
        poll_until_done(job_id)
        results_url = get_results_url(job_id)
        raw_tsv = fetch_results(results_url)

        with open(RESULTS_TSV, "w", newline="") as f:
            f.write(raw_tsv)

    mapping_rows = parse_idmapping_tsv(raw_tsv)

    accession_table, dropped_logs, counts = reconcile(genes_rows, mapping_rows)
    assert_all_canonical(accession_table)

    write_frozen_csv(accession_table, OUT_CSV)

    with open(DROPPED_LOG, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["symbol", "entrez", "reason"],
        )

        writer.writeheader()
        writer.writerows(dropped_logs)

    append_provenance(
        datetime.date.today().isoformat(), get_sha256(RESULTS_TSV), counts
    )
    print(
        f"[coverage] {counts['mapped']}/5000 mapped | "
        f"{counts['dropped_zero']} no-match | {counts['dropped_ambiguous']} ambiguous"
    )
    print(f"[freeze] {OUT_CSV} SHA256 {get_sha256(OUT_CSV)}")


if __name__ == "__main__":
    main()
