import csv
import hashlib
import re

UNIPROT_CANONICAL = re.compile(
    r"^([OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2})$"
)
HUMAN_ORGANISM_ID = "9606"
KEGG_COMPOUND = re.compile(r"^C\d{5}$")


def get_sha256(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def load_gene_table(path: str) -> list[dict]:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return [{"symbol": r["symbol"], "entrez": r["entrez"]} for r in reader]


def parse_idmapping_tsv(raw_tsv: str) -> list[dict]:
    records = []
    lines = raw_tsv.splitlines()
    header = lines[0].split("\t")
    col_to_idx = {name: i for i, name in enumerate(header)}

    for line in lines[1:]:
        if not line.strip():  # skip any blank lines
            continue
        fields = line.split("\t")

        records.append(
            {
                "entrez": fields[col_to_idx["From"]],
                "accession": fields[col_to_idx["Entry"]],
                "reviewed": fields[col_to_idx["Reviewed"]],
                "organism": fields[col_to_idx["Organism (ID)"]],
            }
        )
    return records


def is_canonical_accession(accession: str) -> bool:
    return bool(UNIPROT_CANONICAL.match(accession))


def reconcile(
    gene_rows: list[dict], mapping_rows: list[dict]
) -> tuple[list, list, dict]:
    mapping_by_entrez = {}

    for row in mapping_rows:
        entrez = row["entrez"]
        mapping_by_entrez.setdefault(entrez, []).append(row)

    accession_table = []
    dropped_log = []

    counts = {
        "mapped": 0,
        "dropped_zero": 0,
        "dropped_ambiguous": 0,
    }

    for gene in gene_rows:
        symbol = gene["symbol"]
        entrez = gene["entrez"]

        candidates = mapping_by_entrez.get(entrez, [])

        survivors = [
            row
            for row in candidates
            if row["reviewed"] == "reviewed"
            and row["organism"] == HUMAN_ORGANISM_ID
            and is_canonical_accession(row["accession"])
        ]

        if len(survivors) == 1:
            accession_table.append(
                {
                    "symbol": symbol,
                    "entrez": entrez,
                    "uniprot_accession": survivors[0]["accession"],
                }
            )
            counts["mapped"] += 1

        elif len(survivors) == 0:
            dropped_log.append(
                {
                    "symbol": symbol,
                    "entrez": entrez,
                    "reason": "no reviewed human canonical match",
                }
            )
            counts["dropped_zero"] += 1

        else:
            accs = [row["accession"] for row in survivors]

            dropped_log.append(
                {
                    "symbol": symbol,
                    "entrez": entrez,
                    "reason": f"ambiguous: {accs}",
                }
            )
            counts["dropped_ambiguous"] += 1

    return accession_table, dropped_log, counts


def assert_all_canonical(accession_table: list[dict]) -> None:
    bad = []
    for row in accession_table:
        accession = row["uniprot_accession"]
        if not is_canonical_accession(accession):
            bad.append(row)
    assert not bad, f"non-canonical accessions: {bad}"


def write_frozen_csv(accession_table: list[dict], out_path: str) -> None:
    rows = sorted(accession_table, key=lambda row: int(row["entrez"]))

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["symbol", "entrez", "uniprot_accession"],
        )

        writer.writeheader()
        writer.writerows(rows)


def load_metabolite_export_table(path: str) -> list[dict]:
    with open(path, newline="") as f:
        rows = csv.DictReader(f)
        mapped = []

        for row in rows:

            kegg_id = row["kegg_compound_id"].strip()

            if kegg_id:
                mapped.append(
                    {
                        "metabolite_name": row["metabolite_name"].strip(),
                        "kegg_compound_id": kegg_id,
                    }
                )

    invalid_ids = []
    for row in mapped:
        kegg_id = row["kegg_compound_id"]

        if not KEGG_COMPOUND.match(kegg_id):
            invalid_ids.append(kegg_id)

    if invalid_ids:
        raise ValueError(f"Invalid KEGG IDs: {invalid_ids}")

    counts = {}

    for row in mapped:
        kegg_id = row["kegg_compound_id"]

        if kegg_id in counts:
            counts[kegg_id] += 1
        else:
            counts[kegg_id] = 1

    duplicates = []

    for kegg_id, count in counts.items():
        if count > 1:
            duplicates.append(kegg_id)

    if duplicates:
        raise ValueError(f"Duplicate KEGG IDs: {duplicates}")

    return mapped
