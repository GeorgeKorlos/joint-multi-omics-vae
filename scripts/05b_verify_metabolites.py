import csv
import datetime

from src.export.mapping import get_sha256, load_metabolite_export_table

METAB_MAP = "data/metadata/metabolite_kegg_map.csv"
PROVENANCE_PATH = "data/PROVENANCE.md"


def count_total_rows(path: str) -> int:
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return sum(1 for _ in reader)


def append_provenance(access_date, sha256, n_mapped, n_total) -> None:
    with open("data/PROVENANCE.md", "r") as f:
        provenance = f.read()

    if "## Metabolite KEGG Mapping" in provenance:
        print("[skip] KEGG provenance already recorded")
        return

    lines = [
        "",
        "## Metabolite KEGG Mapping",
        f"* **Access date**: {access_date}",
        "* **Source**: manual name→KEGG compound ID map"
        "* **KEGG release**: 118.0"
        f"* **metabolite_kegg_map.csv SHA256**: {sha256}"
        f"* **Coverage**: {n_mapped}/{n_total} mapped; "
        f"{n_total - n_mapped} dropped (unmappable LC-MS names — co-eluting "
        "* **Crossrefs**: PubChem/ChEBI deferred this cycle (see DECISIONS)",
    ]

    section = "\n".join(lines) + "\n"

    with open("data/PROVENANCE.md", "a") as f:
        f.write(section)

    print("[ok] KEGG provenance appended")


def main():

    table = load_metabolite_export_table(METAB_MAP)
    n_mapped = len(table)
    n_total = count_total_rows(METAB_MAP)

    sha = get_sha256(METAB_MAP)

    append_provenance(datetime.date.today().isoformat(), sha, n_mapped, n_total)
    print(f"[metabolites] {n_mapped}/{n_total} carry a KEGG compound id")
    print(f"[verify] {METAB_MAP} SHA256 {sha}")


if __name__ == "__main__":
    main()
