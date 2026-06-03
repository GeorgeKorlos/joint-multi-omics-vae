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

## D007 · Output contract 

128-dim · HDF5 float32 · L2-normalized per row · gene-level embeddings from decoder
weights · protein IDs = canonical Swiss-Prot UniProt accessions (human only) ·
metabolite IDs = KEGG compound IDs + PubChem/ChEBI crossrefs.

## D008 · Split ratios 80/10/10

Held-out test set keeps reconstruction quality claims uncontaminated by the beta and
architecture tuning done on validation. At N≈898 this is ~90 samples per split.

## D09 · Reconstruction loss = MSE 

Both modalities are continuous after normalization. MSE is the correct likelihood
for real-valued data. BCE assumes inputs in [0,1] and would misstate the noise model.

## D010 · Per-feature z-score normalization 

Puts expression and metabolite scales on comparable footing so the higher-variance
modality does not dominate the latent space. Applied per feature, not globally.

## D011 · L2 normalization at export, not in training 

Unit-sphere rows make cosine similarity well-defined for the post-hoc KEGG analysis.
Applied at export so learned decoder weights are preserved intact.
Already fixed by output contract (D007); this entry locks the implementation.

## D012 · Asymmetric encoder

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