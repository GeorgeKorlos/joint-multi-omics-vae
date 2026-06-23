# KEGG module coverage

Coverage of KEGG release 118.0 modules over the QC'd feature set, and
per-modality intrinsic dimensionality. All numbers are produced in
`notebooks/02_kegg_coverage.ipynb` over `data/processed/kegg_module_membership.tsv`
(built by `scripts/04_build_membership_matrices.py`). KEGG was fetched 2026-06-08;
release and per-file hashes are recorded in `data/PROVENANCE.md`.

## 1. How membership is built

Module membership has two sides with different reliability. The **gene side is
exact**: KEGG keys human genes by NCBI Entrez ID, and the transcriptomics column
headers carry the Entrez ID directly (`SYMBOL (ENTREZ_ID)`), so the gene→module
join is unambiguous — the only gene-side loss is genes KEGG does not annotate. The
**metabolite side is lossy**: the metabolomics headers are names, which must be
translated to KEGG compound IDs by hand (`data/metadata/metabolite_kegg_map.csv`,
curated against release 118.0) before joining to modules. Every number below
should be read with this asymmetry in mind.

Module IDs were reconciled to a single reference namespace: the gene link returns
organism-specific IDs (`hsa_M#####`) and the compound link returns reference IDs
(`M#####`); the `hsa_` prefix is stripped so both sides share the reference
`M#####` space.

## 2. Metabolite mapping coverage

Of 225 metabolites, **113 (50.2%) map to a KEGG compound ID**. The 112 unmapped
break down by reason:

- 89 lipid species classes (e.g. `C52:3 TAG`) — named by carbon:double-bond
  count, denoting a family of isomers with no single KEGG compound;
- 12 co-eluting mixtures (e.g. `F1P/F6P/G1P/G6P`) — isobaric species recorded
  under one slash-separated name, not resolvable to a single compound;
- 9 with no KEGG 118.0 entry (acetylglycine and long-chain acylcarnitines);
- 2 class-level names (`hexoses HILIC neg/pos`).

This is a limitation of targeted LC-MS naming and of KEGG's compound coverage, not
a pipeline defect. Each drop is recorded with its reason in the mapping table.

## 3. Module composition

258 modules are detected in the data. By modality composition:

- gene-only: 77
- metabolite-only: 127
- both modalities: 54

This composition is reported as information, not as a selector. Unlike the prior
constrained design, modules are **not** down-selected to both-modality, every
module meeting the member threshold enters the post-hoc analysis regardless of
composition.

## 4. Coverage by threshold

Modules meeting each minimum member count, total and per side:

| threshold | total | gene side | metabolite side |
|-----------|-------|-----------|-----------------|
| ≥2 | 195 | 129 | 97 |
| ≥3 | 140 | 117 | 32 |
| ≥5 | 101 | 84 | 7 |
| ≥10 | 50 | 44 | 0 |

The headline threshold is ≥3 (140 modules total, 117 gene-side), with a
sensitivity sweep at 2 / 3 / 5 (DECISIONS D017). The metabolite side collapses
past ≥3 (32 → 7 → 0): only 71 compounds appear in any module, so
metabolite-bearing modules are sparse by construction. This is why the primary
post-hoc statistic is within-modality (preregistration §3.1) and the
both-modality pool available for cross-modal description is small.

## 5. Module size distribution

Members per module (258 modules):

| | total | gene | metabolite |
|---|---|---|---|
| mean | 5.4 | 4.1 | 1.3 |
| median | 3 | 1.5 | 1 |
| max | 28 | 27 | 6 |

The total distribution is right-skewed (most modules small, a tail to ~28). The
metabolite-per-module distribution is sparse and concentrated at 0–2, consistent
with the 71-compound in-module set. Histograms are in the notebook.

## 6. Per-modality intrinsic dimensionality

PCA on the full QC'd matrix, z-scored, per modality principal components to
reach cumulative variance:

| modality | 80% | 90% |
|----------|-----|-----|
| transcriptomics | 285 | 490 |
| metabolomics | 44 | 80 |

Transcriptomics needs roughly 6× the components of metabolomics to reach the same
variance: its variance is spread across hundreds of components, metabolomics'
concentrates in ~50. This gap drove the asymmetric encoder, deep transcriptomics,
shallow metabolomics (DECISIONS D011).

Caveat: PCA ran on all 19205 genes; the model sees the top-5000 (week 4). The
absolute PC counts are indicative, not the model-input dimensionality. The
relative gap is the load-bearing finding and is robust to the gene subset, which
is what justifies locking the encoder asymmetry now.

## 7. Limitations

- **Metabolite coverage (~50%)** is a targeted-LC-MS and KEGG-coverage limitation,
  not a QC failure. The gene side is exact by contrast.
- **Member counts are upper bounds.** They are computed over the full QC'd gene
  panel and the current mapped-metabolite set. Final counts are re-fixed at week
  10, after top-5000 gene selection (week 4) and Entrez → UniProt reconciliation
  (week 8); they can only shrink. The 2 / 3 / 5 sensitivity sweep is designed to
  absorb this.
- **The metabolite side is sparse**, so most threshold-passing modules are
  gene-dominated. This is a data property of the assay, and it is the reason the
  primary statistic is within-modality rather than all-pairs.