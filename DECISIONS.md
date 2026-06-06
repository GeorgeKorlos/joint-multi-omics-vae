## D001 · Project scope

P2 produces a clean embedding artifact and one post-hoc KEGG result.

## D002 · Python 3.10

Cross-project portfolio consistency is the deciding
factor. Consequence: numpy capped at 2.2.6, pandas at 2.3.3, scipy at 1.15.3,
scikit-learn at 1.7.2 — newer releases of all four dropped Python 3.10 support.
No pipeline functionality is affected by these caps.

## D003 · Environment locked at requirements.txt

Direct dependencies pinned to exact versions. Any change requires a new DECISIONS
entry. Transitive deps resolve from these pins. CUDA build of torch requires a
separate index URL — see requirements.txt comment.


## D004 · seaborn and python-dotenv added 

seaborn for QC and latent-space figures. python-dotenv for loading .env API keys
(KEGG, UniProt, STRING). jupyter goes in requirements-dev.txt only — exploration
tooling, not pipeline.

## D005 · KEGG release 118.0 

Pinned. Confirmed live as of 2026-06-02 via REST API. 

## D006 · Output contract 

128-dim · HDF5 float32 · L2-normalized per row · gene-level embeddings from decoder
weights · protein IDs = canonical Swiss-Prot UniProt accessions (human only) ·
metabolite IDs = KEGG compound IDs + PubChem/ChEBI crossrefs.

## D007 · Split ratios 80/10/10

Held-out test set keeps reconstruction quality claims uncontaminated by the beta and
architecture tuning done on validation. At N≈904 this is ~90 samples per split.

## D08 · Reconstruction loss = MSE 

Both modalities are continuous after normalization. MSE is the correct likelihood
for real-valued data. BCE assumes inputs in [0,1] and would misstate the noise model.

## D09 · Per-feature z-score normalization 

Puts expression and metabolite scales on comparable footing so the higher-variance
modality does not dominate the latent space. Applied per feature, not globally.

## D010 · L2 normalization at export, not in training 

Unit-sphere rows make cosine similarity well-defined for the post-hoc KEGG analysis.
Applied at export so learned decoder weights are preserved intact.
Already fixed by output contract (D006); this entry locks the implementation.

## D011 · Asymmetric encoder

Modalities differ in intrinsic dimensionality. Deeper encoder for transcriptomics,
shallower for metabolomics. Exact layer counts wait on per-modality PCA in week 3.
Do not lock numbers before measuring.

## KEGG mapping scope note

Manually inspected the first 20 metabolite column headers from
CCLE_metabolomics_20190502.csv. Several entries are co-eluting compounds recorded
under a single slash-separated name (DHAP/glyceraldehyde 3P, F1P/F6P/G1P/G6P,
fumarate/maleate/alpha-ketoisovalerate), these cannot be mapped to a single KEGG
compound ID and will be dropped at the mapping step. One entry is a class-level name
(hexoses HILIC neg), also unmappable. Remaining entries appear to be single named
compounds with standard names and are expected to map. Estimated drop rate from
inspection: ~15-20% of the 225 metabolites. Coverage risk: medium. This is a data
limitation of targeted LC-MS, not a pipeline bug. Decision on mapping strategy
deferred to week 3 preregistration.

Gene column format in transcriptomics: SYMBOL (ENTREZ_ID) — e.g. TSPAN6 (7105).
The mapping pipeline must strip the Entrez suffix before passing symbols to the
UniProt ID mapping API.


## D012 · Missing-value handling — no imputation

No imputation, no missingness-based removal, either modality. Both frames contain
zero NaNs (Day 1, full-frame isna().sum().sum()). Metabolomics pre-imputed claim
(PROVENANCE) holds empirically. No missing-value step in 02_qc.py.

## D013 · Detection filter — rejected

Metabolomics source is floor-filled at ~2.976 (min non-zero value); value
distribution is unimodal centered ~5.9 with no near-floor mass. Every metabolite is
detected above floor in essentially every cell line, so a detection-rate filter
removes nothing. Distinct from the ~46% KEGG compound-mapping loss, which is a
mapping-axis loss applied downstream (week 3), not a detection-axis QC filter.

## D014 · Zero-variance genes — no QC drop

5 genes are constant across all 1684 lines. Not removed at QC. They sit at the
bottom of the variance ranking and are removed by the week 4 top-5000 selection
before per-feature z-scoring (D009), so the divide-by-zero risk is eliminated by
construction rather than by a QC step.

## D015 · Low-variance QC filter — rejected as redundant

A low-variance cut would remove 5.1% / 9.5% / 12.1% of genes at var < 0.01 / 0.05 /
0.10. Week 4 top-5000-by-variance selection removes ~74% of genes by the same
criterion, strictly superseding any QC-stage low-var threshold. Metabolomics (225
features, no zero-variance) retains all features for the join and embedding. No
low-var filter in 02_qc.py.

## D016 · Outlier policy — 3 SD, one-sided low, transcriptomics-driven

Per-sample total-signal z-score, removed where z < -3. Computed on the paired set
(912) post-join, not the full transcriptomics frame.
- One-sided (low only): no biological basis for removing high-total samples; none
  exist (max < mean + 3 SD). Left-skewed tx distribution inflates SD, making the
  cut conservative.
- Transcriptomics-only: metabolomics per-sample totals have CV < 1% (SD 7.4 / mean
  1322); a 3 SD cut there flags tight-Gaussian tails, not quality failures. The 9
  metabolomics flags are recorded but not acted on.
- Disjoint sets: tx and meta outliers share zero IDs (overlap ∅) — meta flags are
  independent noise, not corroboration.
- Result: 8 samples removed. N: 912 → 904 (≥ 850 floor, passes).
- Removed DepMap IDs: ACH-000544, ACH-000732, ACH-000002, ACH-000979, ACH-000646,
  ACH-000415, ACH-000771, ACH-000794.
- These eight IDs are the expected 02_qc.py output. The script computes the cut on
  the paired 912; if it produces a different set, the script is wrong (likely
  computed on the full 1684 frame), not this decision.