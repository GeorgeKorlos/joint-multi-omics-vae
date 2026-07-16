# P2 → P3 Handoff

**Artifact:** `data/embeddings/omics_embeddings.h5`
**SHA256:** `35eb28d8d5a1e3af095db596bbdcf2d5b8bdfccc0053f600cd836e764dce7caa`
**Produced:** 2026-07-16, tag `v1.1`
**Status:** frozen. 

**Supersedes v1.0.**

## What P3 reads


- `/protein_ids` — 4958 UniProt accessions. P3's complete node set. No nodes outside this list, none created. All 4958 are unique.
- `/protein_embeddings` — 4958 × 128, float32, L2-normalized. These initialize the R-GCN node states.

Row *i* of `/protein_embeddings` belongs to accession *i* in `/protein_ids`. Aligned by row, guaranteed at export. P3 can rely on row order; it does not need to key by accession.


## The numbers

- Proteins: 4958 kept of 5000. 42 dropped, 20 ambiguous (multiple accessions), 8 no reviewed human match, 14 collapsed (shared an accession with another gene). Coverage 99.2%.


## Identifiers

- Proteins: UniProt canonical accessions. Human, Swiss-Prot reviewed, canonical isoform only. No isoform suffixes — checked, zero found. Release 2026_02 (10-June-2026), queried 2026-07-13.
- Metabolites: KEGG compound IDs, release 118.0.


## Verified

`scripts/07_validate_schema.py` passed on this exact file: float32 with correct shapes (4958×128, 113×128); every row L2-normalized to length 1 within 1e-5; ID counts match embedding rows (no orphans); no isoform-suffixed accessions; all metadata present.

## Reproducing this file

Check out tag `v1.1`, run `python -m scripts.06_export_artifacts`. Same SHA256, given the same run date (the creation date is written into the file).