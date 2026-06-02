# Data Source

## Transcriptomics

- File: OmicsExpressionProteinCodingGenesTPMLogp1.csv
- Source: DepMap 25Q2, https://depmap.org/portal/data_page/?tab=allData
- Content: protein-coding gene expression, TPM log(p+1), HGNC gene symbols
- Access: public, no data access agreement required

## Metabolomics

- File: CCLE_metabolomics_20190502.csv
- Source: CCLE 2019 via DepMap portal
- Content: targeted LC-MS, 225 metabolites, metabolite names as column headers
- Access: public, no data access agreement required

## Notes

Both files are gitignored. Integrity is verified by SHA256 in data/PROVENANCE.md.
Cell line identity is expected to be DepMap IDs in both files 