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
* **Shape**: 928 × 226 (225 metabolites + CCLE_ID column)
* **Notes**: Pre-imputed at source (no NaNs expected). Values are log-transformed.
  Column headers are metabolite names — name → KEGG compound ID translation required
  at the mapping step. CCLE_ID column dropped at preprocessing.

## Paired Dataset

* **Join key**: DepMap_ID
* **Join type**: inner
* **Paired N**: 912
* **Status**: PASS (above 850 floor)