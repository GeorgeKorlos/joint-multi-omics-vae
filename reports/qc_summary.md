# QC Summary

## Inputs
* **Raw datasets**:
    * **Transcriptomics**: 1684 × 19205
    * **Metabolomics**: 928 × 225
* **Reference integrity**: SHA256 matched to PROVENANCE

## Missing Values
* **Transcriptomics**: 0
* **Metabolomics**: 0
* **Status**: pre-imputation claim verified (D012)

## Detection Characteristics
* **Source floor**: ~2.976
* **Filtering**: No additional filtering applied (D013)

## Outlier Handling
* **Policy**: 3 SD threshold, one-sided (low tail), tx-only, paired-set constraint
* **Samples removed**: 8
* **Metabolomics**: flagged but not acted upon (documented only) (D016)

## Variance Filtering
* **Zero-variance genes**: 5 identified, rejected (D014)
* **Low-variance thresholds tested**: 5.1%, 9.5%, 12.1%
* **Status**: All rejected as QC filters (D015)

## Cross-Modality Signal
* **Pearson correlation**: r = 0.045
* **Interpretation**: no global alignment detected

## Output
* **Transcriptomics dimensions**: 904 × 19205
* **Metabolomics dimensions**: 904 × 225
* **Storage**: HDF5
* **Indexing**: shared sample index maintained