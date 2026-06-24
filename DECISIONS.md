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

## D008 · Reconstruction loss = MSE 

Both modalities are continuous after normalization. MSE is the correct likelihood
for real-valued data. BCE assumes inputs in [0,1] and would misstate the noise model.

## D009 · Per-feature z-score normalization 

Puts expression and metabolite scales on comparable footing so the higher-variance
modality does not dominate the latent space. Applied per feature, not globally.

## D010 · L2 normalization at export, not in training 

Unit-sphere rows make cosine similarity well-defined for the post-hoc KEGG analysis.
Applied at export so learned decoder weights are preserved intact.
Already fixed by output contract (D006); this entry locks the implementation.

## D011 · Asymmetric encoder — locked

Asymmetric per-modality encoder trunks: deep transcriptomics, shallow
metabolomics. Trunk outputs concatenated → shared head → μ, logvar (128-dim each).

Locked widths:
- transcriptomics trunk: 5000 → 1024 → 256
- metabolomics trunk: 225 → 128
- concat (256 + 128 = 384) → shared head → μ, logvar

Per-modality PCA on the full QC'd matrix (Day 3, 02_kegg_coverage.ipynb):
transcriptomics needs 285 PCs to 80% variance / 490 to 90%; metabolomics needs
44 / 80. Transcriptomics variance spreads across hundreds of components → more
capacity to compress; metabolomics concentrates in ~50 → a deep stack would
overfit 225 features on 904 samples. Hence deep tx, shallow mt.

Caveat: PCA ran on all 19205 genes; the model sees top-5000 (week 4), so absolute
PC counts are indicative, not model-input dimensionality. The relative tx≫mt gap
(~6×) is the load-bearing finding and is robust to the gene subset — that is what
justifies locking the asymmetry. PCA supports deep-vs-shallow; the exact widths
are a modeling choice, not dictated by the numbers.

Confirmation (top-5000 subset). D011's PCA ran on all 19205 genes; the model sees the top-5000. 
Re-running per-modality PCA on the 5000-gene subset: transcriptomics 197 PCs to 80% / 397 to 90%, 
metabolomics unchanged at 44 / 80. The gap is 4.5× at 80% and 5.0× at 90%, down from ~6.5× / ~6.1× 
on the full frame. The drop is expected: top-5000 removes low-variance genes that carried long-tail 
dimensions, concentrating transcriptomics variance into fewer PCs while metabolomics is untouched. 
The asymmetry holds in the direction that matters, transcriptomics remains several times 
higher-dimensional, so the asymmetric encoder depth is unchanged. Only the headline multiple 
shrinks from ~6× to ~4.5–5×.

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

Update. The 5-gene count is measured on the full 1684-line transcriptomics frame. 
Selection actually runs on the clean 904-line set, where 8 genes are zero-variance. 
The difference is the dropped lines: 1684 → 912 at the metabolomics join → 904 after outlier removal (D016). 
Removing lines can only flatten a gene, never un-flatten it, so the original 5 are a subset of these 8, 
three more genes vary only across lines that were dropped, and read constant across the 904 that remain. 
All 8 sit at the bottom of the variance ranking and are removed by the top-5000 cut by construction; 
the divide-by-zero protection is unchanged.

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

## D017 · KEGG module member threshold — ≥3 headline, sweep 2/3/5

≥3 members headline, sensitivity sweep at 2 / 3 / 5. Claim supported only if it
holds across all three (preregistered, §3.5).

Coverage at each threshold (Day 2, 02_kegg_coverage.ipynb), over 258 modules
detected in data:

| threshold | total | gene side | metabolite side |
|-----------|-------|-----------|-----------------|
| ≥2 | 195 | 129 | 97 |
| ≥3 | 140 | 117 | 32 |
| ≥5 | 101 | 84 | 7 |
| ≥10 | 50 | 44 | 0 |

≥3 is the floor where mean pairwise similarity is more than a single pairwise
distance, and leaves a healthy count (140 total, 117 gene-side). ≥2 is thin (one
pair); ≥10 leaves too few modules and zero metabolite-side. The 2/3/5 sweep shows
the result is not a threshold artifact.

Metabolite side collapses past ≥3 (32 → 7 → 0) — structural, only 71 compounds
appear in any module. This is why the primary statistic is within-modality
(prereg §3.1) and the both-modality pool is small. Counts are upper bounds here,
re-fixed at week 10 on the embedded entity set; the sweep absorbs the shrinkage.