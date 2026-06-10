import os
import pandas as pd

RAW_DIR = "data/raw/kegg/"
LINK_HSA_MODULE = RAW_DIR + "link_hsa_module.tsv"
LINK_COMPOUND_MODULE = RAW_DIR + "link_compound_module.tsv"
METAB_MAP = "data/metadata/metabolite_kegg_map.csv"
TX_RAW = "data/raw/OmicsExpressionProteinCodingGenesTPMLogp1.csv"
OUT_PATH = "data/processed/kegg_module_membership.tsv"


def parse_gene_module_links(path) -> list[tuple[str, str]]:
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) != 2:
                continue
            module_id = None
            entrez = None

            for token in parts:
                if token.startswith("md:"):

                    module_token = token[3:]
                    module_id = module_token

                    if module_id.startswith("hsa_"):
                        module_id = module_id[4:]

                elif token.startswith("hsa:"):
                    entrez = token[4:]

            if module_id and entrez:
                pairs.append((module_id, entrez))

    return pairs


def parse_compound_module_links(path) -> list[tuple[str, str]]:
    pairs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) != 2:
                continue

            module_id = None
            cid = None

            for token in parts:
                if token.startswith("md:"):
                    module_id = token[3:]

                elif token.startswith("cpd:"):
                    cid = token[4:]

            if module_id and cid:
                pairs.append((module_id, cid))

    return pairs


def load_present_entrez(tx_raw_path) -> set[str]:
    cols = pd.read_csv(tx_raw_path, nrows=0).columns.tolist()
    gene_cols = cols[1:]
    entrez_set = set()
    for col in gene_cols:
        if "(" not in col or ")" not in col:
            continue

        entrez = col.split("(")[-1].rstrip(")").strip()
        if entrez:
            entrez_set.add(entrez)

    return entrez_set


def load_mapped_cids(map_path) -> set[str]:
    df = pd.read_csv(map_path, dtype=str, keep_default_na=False)

    cids = df["kegg_compound_id"].astype(str).str.strip()

    return set(cids[cids != ""])


def build_membership(
    gene_links, present_entrez, compound_links, mapped_cids
) -> pd.DataFrame:
    rows = []
    for module_id, entrez in gene_links:
        if entrez in present_entrez:
            rows.append((module_id, entrez, "gene"))

    for module_id, cid in compound_links:
        if cid in mapped_cids:
            rows.append((module_id, cid, "metabolite"))

    df = pd.DataFrame(
        rows,
        columns=["module_id", "member_id", "member_type"],
    )

    df = (
        df.drop_duplicates()
        .sort_values(by=["module_id", "member_type", "member_id"], kind="stable")
        .reset_index(drop=True)
    )

    return df


def main():
    gene_links = parse_gene_module_links(LINK_HSA_MODULE)
    compound_links = parse_compound_module_links(LINK_COMPOUND_MODULE)
    present_entrez = load_present_entrez(TX_RAW)
    mapped_cids = load_mapped_cids(METAB_MAP)
    membership = build_membership(
        gene_links, present_entrez, compound_links, mapped_cids
    )
    os.makedirs("data/processed", exist_ok=True)

    membership.to_csv(
        OUT_PATH,
        sep="\t",
        index=False,
    )

    n_modules = membership["module_id"].nunique()

    n_genes = membership.loc[membership["member_type"] == "gene", "member_id"].nunique()

    n_metabolites = membership.loc[
        membership["member_type"] == "metabolite", "member_id"
    ].nunique()

    print(
        f"Wrote {len(membership):,} rows | "
        f"{n_modules:,} modules | "
        f"{n_genes:,} genes | "
        f"{n_metabolites:,} metabolites"
    )


if __name__ == "__main__":
    main()
