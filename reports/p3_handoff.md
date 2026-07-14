# P2 → P3 Handoff

**Artifact:** `data/embeddings/omics_embeddings.h5`
**SHA256:** `e323c37ebdfce0740fd824d3be81744720be4bfd6c82e1b01018834f52145fe0`
**Produced by:** commit `<HEAD hash>`, tag `v1.0`, on 2026-07-13
**Status:** frozen. This file does not change. Any new version gets a new hash and a new tag.

## What P3 reads

Two datasets, nothing else:

- `/protein_ids` — 4972 UniProt accessions. E-GCN's complete node set. No nodes outside this list, none created.
- `/protein_embeddings` — 4972 × 128, float32, L2-normalized. These initialize the R-GCN node states.

Row *i* of `/protein_embeddings` belongs to accession *i* in `/protein_ids`. Aligned by row, guaranteed at export. P3 can rely on row order; it does not need to key by accession.

## What P3 does not read

`/metabolite_embeddings`, `/metabolite_ids`, `/metabolite_crossrefs` are not for P3. P3 is protein-only. `/metabolite_crossrefs` is present but empty on purpose — deferred, no consumer yet.

## The numbers

- Proteins: 4972 kept of 5000. 28 dropped — 20 ambiguous (multiple accessions), 8 no reviewed human match. Coverage 99.4%.
- Metabolites: 113 kept of 225. 112 dropped — no single KEGG compound ID.

## Identifiers

- Proteins: UniProt canonical accessions. Human, Swiss-Prot reviewed, canonical isoform only. No isoform suffixes — checked, zero found. Release 2026_02 (10-June-2026), queried 2026-07-13.
- Metabolites: KEGG compound IDs, release 118.0.

## Version pins

- KEGG 118.0 
- UniProt 2026_02 

## Verified, not claimed

`scripts/07_validate_schema.py` passed on this exact file: float32 with correct shapes (4972×128, 113×128); every row L2-normalized to length 1 within 1e-5; ID counts match embedding rows (no orphans); no isoform-suffixed accessions; all metadata present.

## Reproducing this file

Check out tag `v1.0`, run `python -m scripts.06_export_artifacts`. Same SHA256, given the same run date (the creation date is written into the file).