import pandas as pd
import datetime
import subprocess
from src.training.trainer import load_trained_model
from src.evaluation.latent_analysis import decoder_weight_matrices
from src.data.io import read_omics_clean, OMICS_PATH
from src.export.write_h5 import (
    build_gene_table,
    build_metabolite_table,
    l2_normalize_rows,
    write_artifact,
)

MODEL_CHECKPOINT_PATH = "outputs/checkpoints/shallow_beta1_seed42.pt"
SELECTED_GENES_PATH = "data/processed/selected_genes.csv"
ACCESSIONS_PATH = "data/processed/protein_accessions.csv"
KEGG_MAP_PATH = "data/metadata/metabolite_kegg_map.csv"
DROPPED_GENES_REPORT = "reports/dropped_genes.csv"
OUT_PATH = "data/embeddings/omics_embeddings.h5"

ORIGINAL_GENE_COUNT = 5000
ORIGINAL_METABOLITE_COUNT = 225

model = load_trained_model(MODEL_CHECKPOINT_PATH)

W_tx, W_mt = decoder_weight_matrices(model)

print(f"W_tx dtype: {W_tx.dtype}")

_, mt = read_omics_clean(OMICS_PATH)
mt_names = mt.columns.astype(str).tolist()

W_tx_l2_norm = l2_normalize_rows(W_tx)
W_mt_l2_norm = l2_normalize_rows(W_mt)


gene_emb, uniprot_ids, dropped_genes_df = build_gene_table(
    W_tx_l2_norm, SELECTED_GENES_PATH, ACCESSIONS_PATH
)
mt_emb, kegg_ids, dropped_metabolites_df = build_metabolite_table(
    W_mt_l2_norm, mt_names, KEGG_MAP_PATH
)

assert len(dropped_metabolites_df) == 112

print(f"Genes kept: {len(gene_emb)}/5000")
print(f"Metabolites kept: {len(mt_emb)}/225")

assert len(gene_emb) == 4958
assert len(mt_emb) == 113

reported_drops = pd.read_csv(DROPPED_GENES_REPORT)
assert len(reported_drops) == 42
assert set(dropped_genes_df["entrez"]) == set(reported_drops["entrez"])


protein_coverage = len(gene_emb) / ORIGINAL_GENE_COUNT
metabolite_coverage = len(mt_emb) / ORIGINAL_METABOLITE_COUNT

creation_date = datetime.date.today().isoformat()
git_commit = subprocess.run(
    ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
).stdout.strip()

meta_dict = {
    "model_name": "joint-multi-omics-beta-vae",
    "model_version": "v1.0",
    "seed": 42,
    "beta": 1,
    "arch": "shallow",
    "protein_dropped": len(dropped_genes_df),
    "protein_coverage": protein_coverage,
    "metabolite_dropped": len(dropped_metabolites_df),
    "metabolite_coverage": metabolite_coverage,
    "creation_date": creation_date,
}

dropped_metabolites_df.to_csv("reports/dropped_metabolites.csv", index=False)
write_artifact(OUT_PATH, gene_emb, uniprot_ids, mt_emb, kegg_ids, meta_dict)
print(f"wrote -> {OUT_PATH}")
