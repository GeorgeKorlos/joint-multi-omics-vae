# Mapping Coverage — P2 Embedding Export

KEGG release 118.0 (portfolio invariant). Coverage is reported, not gated.

## Genes (Entrez → UniProt)

- Source: `data/processed/selected_genes.csv` (5000 genes, variance-ranked)
- Method: Entrez GeneID → UniProtKB-Swiss-Prot (reviewed, human 9606, canonical)
- **Mapped: 4972 / 5000 (99.4%)**
- Dropped: 28 total
  - 20 ambiguous — one gene → ≥2 distinct reviewed proteins (e.g. CALCA →
    P01258/P06881 calcitonin/CGRP; HSPA1A/B duplicate pair). No non-arbitrary
    tiebreak; all dropped. Full list: `reports/dropped_genes.csv`.
  - 8 no reviewed human canonical match (RIPK4, SRRM3, PLCXD2, OBSCN, SLC22A31,
    CXCC4, ANKRD18B, FOXO6) — expected long tail.
- Frozen: `data/processed/protein_accessions.csv`
- **SHA256: 723a06b1570a8802a8885bb4077f0a456ced7bc83939b7c6df664c61a62ea5b2**

## Metabolites (name → KEGG compound ID)

- Source: `data/metadata/metabolite_kegg_map.csv` (225 metabolites, frozen Week 3)
- **Mapped: 113 / 225 (50.2%)**
- Dropped: 112 unmappable LC-MS names (locked Week 3, not revisited).
- Crossrefs (PubChem/ChEBI): deferred this cycle — no current consumer. See DECISIONS.
- **SHA256: 99d15773f5688937f0e62c28f275589ba35c4491b041c1bdc86fe5e3a8678253**

## Downstream

- P3 consumes genes keyed by UniProt accession (4972 nodes).
- Metabolites ship keyed by KEGG compound ID only.
- Mapping method for the HDF5 artifact: UniProt ID mapping API (STRING dropped — see DECISIONS).