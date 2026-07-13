# Data Provenance

## DepMap Release

* **Release**: DepMap Public 25Q2
* **Download date**: 2026-06-02
* **Source**: https://depmap.org/portal/data_page/?tab=allData
* **Citation**: DepMap, Broad (2025). DepMap Public 25Q2. Dataset. depmap.org

## File 1 — OmicsExpressionProteinCodingGenesTPMLogp1.csv

* **SHA256**: e0326e16eb23bea1be980fce315acb36b224dedd7af6b47e0ba37e7747dbcc47
* **Shape**: 1684 × 19205
* **Notes**: Row index = DepMap IDs (ACH-XXXXXX). Column headers = HGNC symbols
  with Entrez IDs appended (e.g. TSPAN6 (7105)) — strip Entrez suffix before
  HGNC → UniProt mapping in export step.

## File 2 — CCLE_metabolomics_20190502.csv

* **Release**: CCLE 2019
* **Citation**: Li et al. The landscape of cancer cell line metabolism.
  Nature Medicine 25, 850–860 (2019).
* **SHA256**: 7c1d24aa575f4c58a29019026b5df8e6d1142a56925aba32ff3f1d1d5a7fd0ac
* **Shape**: 928 × 227 
* **Notes**: Pre-imputed at source (no NaNs expected). Values are log-transformed.
  Column headers are metabolite names — name → KEGG compound ID translation required
  at the mapping step. CCLE_ID column dropped at preprocessing.

## Paired Dataset

* **Join key**: DepMap_ID
* **Join type**: inner
* **Paired N**: 912
* **Status**: PASS (above 850 floor)

## KEGG Module Database
* **Release**: kegg             Release 118.0+/06-08, Jun 26
* **Fetch date**: 2026-06-08
* **Source**: https://rest.kegg.jp
* **Endpoints**: /link/hsa/module, /link/compound/module, /list/module, /link/hsa/hsa00010, /link/compound/map00010, /link/hsa/hsa00020, /link/compound/map00020, /link/hsa/hsa00260, /link/compound/map00260, /link/hsa/hsa00670, /link/compound/map00670
* **link_compound_map00010.tsv**: adb555da7ad112350865cf87fc989b1aafbdd0346f06a2aa7ad7cceb52851950
* **link_compound_map00020.tsv**: 255b5673d9328739afd449d746c1b930e61fcc4e21ea12f4d31b00b1b18ed93f
* **link_compound_map00260.tsv**: b2bdbf1afd971c5167f479cd8f4a40c0d7a59c94b7c4f7db7bae46dacbdc6a8f
* **link_compound_map00670.tsv**: 5c9374a84fd1e6dd83bf9142a151bcb00b1442514b2c29c0010c5b088df5436a
* **link_compound_module.tsv**: 74eb99eb951b89b8653c6cc16fa7609f1e329d0ad600d93e403ba2039e8675a3
* **link_hsa_hsa00010.tsv**: c5df3de5037a72fa201fe8aa3afcb1b820dbc54f0e92824f39a20ca1f7a67bd1
* **link_hsa_hsa00020.tsv**: 595acabe7f2fab1a86ced813e2987ad0fea4fea90e899d4e10d776269a101edb
* **link_hsa_hsa00260.tsv**: e96bcfb877b0ff6920f8331fb090580a24aa930b04a1c183403d728c60cc5ac4
* **link_hsa_hsa00670.tsv**: f93eeac12ebf62494b0ce88bb20ce9b37ee4e194d8e812fcf06beb276d414b67
* **link_hsa_module.tsv**: a926e06d52b39698869ef0532709c28e4848d383074f1852ede6b106ab40d8c5
* **list_module.tsv**: 61e96a77d64f6fa77d120e30ee7f0d633f523f100b8c81a041bda0ff6f6462d9


## File 3 - Model.csv

* **Release**: DepMap Public 25Q2
* **Download date**: 2026-07-04
* **Source**: https://depmap.org/portal/data_page/?tab=allData
* **SHA256**: b096e03bfefdc2679211545ddbf1bb7878d69ffde07ae335af5b968a7883733c
* **Join key**: ModelID (= DepMap ID, matches omics sample index)
* **Columns used**: ModelID, OncotreeLineage
* **Scope**: lineage coloring for latent UMAP only. Not in the HDF5
  artifact, embeddings, or downstream project identifier space, visualization dependency,
  output-contract-inert.
## UniProt ID Mapping
* **Access date**: 2026-07-12
* **Source**: https://rest.uniprot.org
* **Mapping**: GeneID (Entrez) -> UniProtKB-Swiss-Prot
* **Release**: none — UniProt ID mapping is continuously updated; access date is the reproducibility anchor
* **idmapping_results.tsv SHA256**: 2012f4e3ad3a1d2659d8c42810e77602d532380bf041085e31aff117ad38c5d9
* **Coverage**: 4972 mapped / 8 no-match / 20 ambiguous, of 5000 genes

## Metabolite KEGG Mapping
* **Access date**: 2026-07-12
* **Source**: manual name→KEGG compound ID map* **KEGG release**: 118.0* **metabolite_kegg_map.csv SHA256**: 99d15773f5688937f0e62c28f275589ba35c4491b041c1bdc86fe5e3a8678253* **Coverage**: 113/225 mapped; 112 dropped (unmappable LC-MS names — co-eluting * **Crossrefs**: PubChem/ChEBI deferred this cycle (see DECISIONS))
