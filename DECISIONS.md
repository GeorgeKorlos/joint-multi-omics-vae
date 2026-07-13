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

### REVISED 

**Original decision:** asymmetric per-modality trunks — deep
transcriptomics (5000→1024→256), shallow metabolomics (225→128), concat→shared
head→μ/logvar. Justified by per-modality PCA: tx variance spread across ~285 PCs
to 80%, mt concentrated in ~44, suggesting tx needed more compression capacity.

**Revision:** the deep tx trunk is dropped. Locked encoder is
now the shallow variant — single tx layer (5000→256), mt unchanged (225→128),
concat(384)→μ/logvar directly, no shared head.

**Why revised — held-out ablation, β=1, 3 seeds:**

| arch | tx R² (42/43/44) | mt R² (42/43/44) | active |
|------|------------------|------------------|--------|
| asymmetric | 0.4169 / 0.4136 / 0.4172 | 0.5767 / 0.5773 / 0.5739 | 127–128 |
| shallow    | 0.4563 / 0.4516 / 0.4543 | 0.6029 / 0.6050 / 0.6057 | 128 |

Shallow beats asymmetric on both modalities at every seed. Distributions do not
overlap; shallow's worst run (tx 0.4516) exceeds asymmetric's best (tx 0.4172);
same on mt. Within-seed spread (~0.003) is ~10× smaller than the between-arch gap
(~0.035), so the difference is architectural, not initialization noise.

**Read:** the deep tx trunk overfits. 5000→1024→256 on 723 training rows (of 904 paired) has the
capacity to memorize train and generalizes worse on held-out data than the single
5000→256 layer. The PCA measurement suggested more capacity would help;
the held-out ablation showed it hurts. Measurement supersedes prediction, the
PCA rationale is retained above as the original reasoning, not deleted.

**Robustness:** stability was established across 3 initialization seeds. K-fold
cross-validation over train+val was considered as a partition-stability check and
not run, the seed separation (~10× signal-to-noise, no distribution overlap) was
sufficient to decide, and CV would not have changed a non-overlapping result.

**Cascade:** none downstream. 128-dim output contract unchanged, linear decoder
(D022) unchanged, embedding extraction unchanged. Downstream projects see the same artifact
shape. Only the encoder that produces the latent changed.

Cross-ref: D022 (decoder), D023 (baseline, asymmetric), D024 (β on shallow),
experiments/sweep/.

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

## D018 · Top-5000 gene selection by variance

Genes are ranked by variance across the 904 clean paired lines, and the top 5000
are kept. Selection runs on the clean, un-z-scored values, it has to, because
z-scoring (D009) sets every feature's variance to 1, which would destroy the
ranking. Variance at the cut (rank 5000): 1.21716. 14205 genes are dropped.

Deterministic: ties are broken by original column position, so the selected set
is identical bit-for-bit across runs and machines. This supersedes the rejected
low-variance QC filter (D015), top-5000 is a stricter variance cut, and removes
the zero-variance genes (D014, 8 on the clean set) by construction, since they
sit at the bottom of the ranking and never reach the top 5000.

Entrez IDs are reattached to the selected symbols from the raw transcriptomics
header, position-aligned to the clean columns (two asserts guard the alignment).
The clean matrix carries bare symbols, but Week 8 (UniProt) and Week 10 (KEGG
re-fix) both key on Entrez, so the selection persists symbol + entrez together.

The selected list is written to `data/processed/selected_genes.csv`
(rank, symbol, entrez, variance) and tracked in git. It is a provenance artifact:
the gene embedding universe for P3 derives from it.

## D019 · Train/val/test split — random, not stratified

80/10/10 split on the 904 paired samples, seed 42 (the project-global seed),
stored by DepMap ID in `data/processed/split.json`. Fold sizes: train 723,
val 90, test 91 (test absorbs the rounding remainder so the three always sum to
904). The split is deterministic — same seed gives the same partition bit-for-bit,
and frozen: SHA256 `6d50beca9e8de6382d960548692ed4fc7de33a89364fca9d145821ec7faa409d`.
That hash is the contract; if the split file ever changes, the hash won't match.

The split is random, not stratified by cancer lineage. Reasoning:

- The scientific result (KEGG module membership vs embedding similarity) is
  computed from decoder weights — gene and metabolite embeddings, which do not
  depend on which cell lines sit in which fold. The split only affects the
  held-out reconstruction score used for β selection (Week 6), and at ~90 lines
  per held-out fold a random draw is representative enough for that.
- Lineage labels are not in the repo. `omics_clean.h5` carries DepMap IDs only,
  so stratifying would require downloading and SHA256-pinning a new DepMap
  metadata file and joining it by ID, a new tracked data dependency for a
  benefit that does not touch the claim.
- Simplest implementation that produces a valid artifact (project convention);
  stratification here is complexity without a justification that survives scrutiny.

## D020 · Per-feature standardizer, fit on train only

Per-feature z-score (D009), implemented as a small `Standardizer` class rather
than sklearn, so the saved object is two plain arrays (`mean`, `std`) in an
`.npz`, with no library-version baggage to break on reload across the project's
weeks.

The fit happens on the 723 training rows only, then the stored train statistics
are applied to val and test. Fitting on all 904 would leak val/test distribution
into training and inflate the held-out reconstruction numbers that drive β
selection. Confirmed empirically: after transform, train mean is ~0 (fit on
those rows) while val (0.0347) and test (0.0247) are small but non-zero — proof
the fit was train-only.

One scaler over the concatenated `[tx | mt]` matrix (5225 features), not two
per-modality scalers. Per-feature z-scoring is per-feature regardless of column
grouping, so the two approaches give bit-for-bit identical results; one scaler
is less to track. Constant features (std 0) are guarded: std is replaced with 1
before dividing, so a constant column maps to all-zeros rather than NaN.

Stored to `data/processed/scaler.npz`. The fit is sequenced strictly after the
split (D019), train rows can't be identified until the split exists.

## D021 · Modality boundary index (5000 | 225)

The model input is the concatenated `[tx | mt]` vector: 5000 genes first, then
225 metabolites, total 5225. The boundary index, 5000, marks where
transcriptomics ends and metabolomics begins.

Concatenation order (tx before mt) is fixed and load-bearing. The scaler's
stored arrays, the column order of the model input, and the boundary index all
assume it. Stored to `data/processed/boundary.json` as
`{"boundary": 5000, "tx": 5000, "mt": 225}`.

This is a forward contract: embedding extraction slices the decoder weight
matrix at exactly this index to separate gene embeddings from metabolite
embeddings. If the concat order or the selection count ever changes, this index
and every downstream slice must change with it.


## D022 · Linear decoder — locked

One linear map per modality, no hidden layers, no activation:
- transcriptomics: z (128) → 5000 genes      W_trans shape [5000 × 128]
- metabolomics:    z (128) → 225 metabolites  W_met   shape [225 × 128]

Bias kept (nn.Linear default). The bias is a per-feature offset (each feature's
mean reconstruction level); it is a separate vector from the weight matrix and is
never touched at extraction, so it does not affect the embeddings.

Reason: forced by the output contract (D006), not a modeling preference. The
contract requires a 128-dim embedding per gene and per metabolite, pulled straight
from decoder weights. A linear decoder gives exactly that: row i of W_trans IS
gene i's 128-dim embedding — its weights connecting the shared latent to that gene's
reconstruction. A multi-layer decoder cannot: the final layer of a 128→512→1024→5000
decoder is [1024 × 5000], so per-gene vectors are 1024-dim, the wrong width, with no
clean 128-dim object to extract. Extraction (.weight rows) only works if the
decoder is linear.

This is the LDVAE design (Svensson et al. 2020, linearly-decoded VAE). It also makes
the post-hoc analysis well-posed: a gene's embedding is its loading on the shared
latent, so cosine similarity between two genes is similarity of latent loading,
exactly what the KEGG co-membership test asks. A nonlinear decoder would make the
embedding a loading on some post-latent hidden layer, a murkier object.

Trade-off: a linear decoder reconstructs less accurately than a nonlinear one. This
is the correct trade, the project's purpose is interpretable, extractable embeddings for the
post-hoc test, not maximal reconstruction. The nonlinear encoder (D011) keeps the
model's expressive power on the input side; the linear decoder keeps the readout
interpretable.

## D023 · β=1 baseline result — reference point

First trained run.  β=1, lr 1e-3,
100 epochs, batch 64, seed 42, CPU. Decoder linear (D022), encoder per D011.

Result — baseline is healthy, both checks pass:

Posterior collapse: none. 128/128 latent dims active at KL threshold 0.01.
  Per-dim KL (test, avg over 91 samples): min 0.0120, median 0.0681, max 1.7922.
  Threshold note: 0.01 is justified post-measurement, the per-dim KL distribution
  has no cluster of dead dims at ~0, so the active count is stable for any small
  cutoff. The weakest dim (0.0120) sits just above the floor; the count is mildly
  threshold-sensitive at the low end, but no dimension has collapsed.

R² on held-out test (per modality, baseline = per-feature mean):
  tx: +0.4350   mt: +0.5951
  Both clear 0, the model reconstructs both modalities well above the mean baseline.
  mt > tx as expected (225 coordinated features vs 5000 genes from a 128-dim latent).

Training: val tracked train and descended throughout (val total 2.03 → 1.18, still
slightly declining at epoch 99). Val sat below train — expected, train carries the
reparameterization-noise penalty that eval (return mu) does not. Not overfitting;
no dropout warranted.

Interpretation: this is a result, not a tuning artifact. The latent is fully used and
both modalities reconstruct. β=1 is a healthy starting point; Week 6 sweeps β to test
the reconstruction-vs-KL trade and whether higher β sharpens the latent without
inducing collapse.

Cross-ref: D011 (encoder), D022 (decoder), losses.py, experiments/baseline_beta1.log.


## D024 · β = 1 selected — sweep on shallow encoder

β swept {1,2,4,8}. First run on the asymmetric encoder (pre-ablation), then
re-run on the shallow encoder after D011 was revised, so β and architecture are
selected on the same model. Both sweeps gave the same shape and the same pick.

Shallow encoder validation results:

| β | active | tx R² | mt R² | KL median |
|---|--------|-------|-------|-----------|
| 1 | 128 | 0.4563 | 0.6029 | 0.113 |
| 2 | 125 | 0.3795 | 0.5135 | 0.037 |
| 4 | 105 | 0.2971 | 0.4081 | 0.018 |
| 8 |  66 | 0.2010 | 0.2877 | 0.010 |

Selection rule, in order: (1) β=8 loses 62/128 dims and its KL median sits at the
0.01 threshold, excluded; (2) all others clear R²>0 both modalities; (3) lowest
surviving β = 1. β=1 is also the healthiest run (most active dims, best
reconstruction both modalities), so no runner-up tension; each higher β is
strictly worse on every axis.

Selected: β = 1.

The trade-off is monotonic and matches the linear-decoder prediction (D022):
higher β costs reconstruction and deactivates dims, no β sharpens the latent
without cost. Identical shape on both encoders confirms β selection is a property
of the KL term and linear decoder, not encoder depth.

Metabolite R² is highest at β=1: 0.6029
val. Config: config/training.yaml carries beta: 1.0, no change needed, the
placeholder becomes committed.

Note: the asymmetric β-sweep (D023 baseline was asymmetric) is retained in
experiments/sweep/ as the pre-ablation record; selection is on the shallow table
above.

Held-out test (shallow β=1, computed once after selection, D007-clean): tx 0.4720,
mt 0.6162, 128/128 active. Exceeds the asymmetric baseline (D023: tx 0.4350,
mt 0.5951) on both modalities — the revised architecture improves the final
reconstruction, not only validation.

Cross-ref: D007 (val/test), D011 (encoder revision), D022 (decoder), D023
(baseline), experiments/sweep/.


## D025 · DepMap Model.csv pulled for lineage coloring

D019 declined lineage metadata because stratification didn't touch the claim.
Reversed here for a different use: coloring the  latent UMAP, the standard
"did the embedding recover biology" figure. SHA256-pinned in PROVENANCE, 25Q2
(matches the transcriptomics release). Lineage never enters training, the
artifact, or the identifier space, figure only. Claim untouched.


## D026 — Dropped genes that mapped to more than one protein

Mapping the 5000 genes to UniProt gave a clean one-to-one answer for almost all of them. 
20 genes matched two (or more) different proteins with no fair way to pick one, so they 
were dropped. 8 more had no reviewed human match and were also dropped. Result: 4972 of 
5000 kept (99.4%). Dropped list: reports/dropped_genes.csv. 
Frozen file: protein_accessions.csv, SHA256: 723a06b1570a8802a8885bb4077f0a456ced7bc83939b7c6df664c61a62ea5b2


## D027 — Metabolite extra IDs deferred

Metabolites are shipped with their KEGG ID only. The extra IDs (PubChem/ChEBI) aren't 
built this round because no downstream project needs them yet. In the output file, 
the extra-IDs slot is left present but empty, marked crossrefs_status: "deferred". 
If a later project needs those IDs, they get added then. The metabolite embeddings 
themselves are unchanged, they're needed for the Project's own KEGG test regardless
. Source file: metabolite_kegg_map.csv, SHA256: 99d15773f5688937f0e62c28f275589ba35c4491b041c1bdc86fe5e3a8678253