import numpy as np
import pandas as pd


def l2_normalize_rows(W):
    l2_normalized = W / np.linalg.norm(W, axis=1, keepdims=True)
    assert np.isfinite(l2_normalized).all()
    return l2_normalized


def build_gene_table(W_tx, selected_genes_path, accessions_path):
    selected_genes = pd.read_csv(selected_genes_path)
    assert len(selected_genes) == W_tx.shape[0] == 5000

    protein_accessions = pd.read_csv(accessions_path)

    selected_genes = selected_genes.reset_index().rename(
        columns={"index": "decoder_row"}
    )

    merged = selected_genes.merge(
        protein_accessions[["entrez", "uniprot_accession"]], on="entrez", how="inner"
    )

    assert len(merged) == 4972

    dropped_df = selected_genes[
        ~selected_genes["entrez"].isin(protein_accessions["entrez"])
    ][["symbol", "entrez"]]

    assert len(dropped_df) == 28

    kept_rows = merged["decoder_row"].to_numpy()

    W_tx_kept = W_tx[kept_rows]

    assert len(W_tx_kept) == len(merged)
    assert np.array_equal(
        selected_genes.iloc[kept_rows]["entrez"].to_numpy(),
        merged["entrez"].to_numpy(),
    )

    uniprot_ids = merged["uniprot_accession"].to_numpy()

    return W_tx_kept, uniprot_ids, dropped_df


def build_metabolite_table(W_mt, mt_names_ordered, kegg_map_path):
    assert len(mt_names_ordered) == W_mt.shape[0] == 225

    kegg_map = pd.read_csv(kegg_map_path)

    ordered = pd.DataFrame(
        {
            "decoder_row": np.arange(len(mt_names_ordered)),
            "metabolite_name": mt_names_ordered,
        }
    )

    merged = ordered.merge(
        kegg_map[["metabolite_name", "kegg_compound_id"]],
        on="metabolite_name",
        how="left",
    )
    assert len(merged) == 225

    has_kegg = merged["kegg_compound_id"].notna() & (merged["kegg_compound_id"] != "")

    kept = merged[has_kegg]
    dropped_df = merged[~has_kegg][["metabolite_name", "decoder_row"]]

    assert len(kept) == 113
    assert len(dropped_df) == 112

    kept_rows = kept["decoder_row"].to_numpy()

    W_mt_kept = W_mt[kept_rows]

    assert np.array_equal(
        kept["metabolite_name"].to_numpy(), np.array(mt_names_ordered)[kept_rows]
    )

    kegg_ids = kept["kegg_compound_id"].to_numpy()

    return W_mt_kept, kegg_ids, dropped_df
