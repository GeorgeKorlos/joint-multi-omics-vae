# Preregistration — KEGG module co-membership vs embedding similarity


**Substrate:** KEGG release 118.0 (fetched 2026-06-08). Module membership built
in `scripts/04_build_membership_matrices.py`, output
`data/processed/kegg_module_membership.tsv`. Coverage and per-modality
dimensionality characterized in `notebooks/02_kegg_coverage.ipynb`.

---

## 1. The claim

Genes and metabolites that share a KEGG module have more similar learned
embeddings than random sets of the same size and composition.

This is the single scientific claim of this project. The β-VAE is trained without any KEGG
information; module membership is used only after training, to evaluate the
embedding. KEGG is never a model input, this is the deliberate separation from
the prior constrained design.

The prediction is one-directional: co-members are predicted to be *more* similar
than random, not merely different.

---

## 2. What the test runs on

- The locked 128-dimensional embeddings, L2-normalized. Because they are
  L2-normalized, cosine similarity is just the dot product.
- Gene embeddings are keyed by UniProt accession; metabolite embeddings by KEGG
  compound ID. Module membership (Entrez genes, C-number metabolites) is
  reconciled to these keys before the test (Entrez → UniProt via the Week 8
  mapping; C-numbers already align).
- The random baseline draws from two pools: all gene embeddings, and all
  metabolite embeddings, present in the artifact.

---

## 3. The primary test

### 3.1 The number computed per module

For each module: the mean cosine similarity between its members, counting only
gene–gene and metabolite–metabolite pairs. Gene–metabolite (cross-modality)
pairs are excluded from this number.

Reason: a gene–metabolite similarity depends on whether the latent space lined up
the two modality subspaces at all, a different question from whether
co-membership predicts proximity. Including cross pairs would let weak cross-modal
alignment mask a real co-membership signal. The cross-modality similarity is
reported separately and descriptively, never as the headline number.

A module is tested only if it has at least one within-modality pair (≥2 members
of at least one modality) in addition to meeting the member threshold.

### 3.2 The random baseline

For a module with `n_g` gene members and `n_m` metabolite members, each random
draw takes `n_g` genes at random from the gene pool and `n_m` metabolites at
random from the metabolite pool, matching the module's composition, not just its
total size and computes the same number as in §3.1.

The baseline is composition-matched because genes and metabolites need not sit
the same way in the space; a fair baseline has to match the same mix. A
size-only baseline would be mis-specified for mixed-modality modules.

- Draws per module: N = 1000.
- Per-module p-value: one-sided, the fraction of random draws whose number is
  ≥ the module's real number.
- A module "beats baseline" if its real number is above the 95th percentile of
  its 1000 random draws.

### 3.3 The headline number

The fraction of tested modules that beat their own baseline.

### 3.4 How significance is decided

By chance alone, 5% of modules would beat their own 95th percentile. The observed
fraction is compared against 0.05 with a one-sided binomial test (n = number of
modules tested, p₀ = 0.05). This single aggregate test is the primary result.
Being one test, it carries no multiple-comparison burden.

Per-module p-values are also reported with Benjamini–Hochberg FDR correction
(count of modules significant at q < 0.05), as supporting detail only — not as
the headline, to avoid cherry-picking individually significant modules out of
many.

### 3.5 Threshold and sensitivity

- Headline threshold: modules with ≥3 members.
- The whole test is repeated at thresholds of 2, 3, and 5.
- The claim is supported only if the aggregate test is significant and positive
  across all of 2 / 3 / 5. Significance at one threshold but not across the sweep
  is treated as a threshold artifact, not a finding (§5).

Member counts per threshold are reported in `notebooks/02_kegg_coverage.ipynb`.
These counts are upper bounds at preregistration time and are re-fixed on the
final embedded entity set (after top-5000 gene selection and UniProt mapping);
the sensitivity sweep is designed to absorb that shrinkage.

### 3.6 Reported descriptively (not part of the headline)

The mean all-pairs similarity (including gene–metabolite cross pairs) is computed
and reported for both-modality modules, to characterize cross-modal alignment. It
is reported alongside the within-modality number, never in place of it.

---

## 4. Secondary check — four pathways (data-space)

An independent biological-plausibility check, run on the QC'd data rather than
the embeddings, on four pathways: Glycolysis (map00010), TCA (map00020),
Ser/Gly/Thr (map00260), One-carbon / folate (map00670).

For each pathway, across cell lines:

- gene activity score = mean standardized expression of the pathway's genes;
- metabolite activity score = mean standardized level of the pathway's mapped
  metabolites;
- compute the Pearson and Spearman correlation between the two scores.

**Pass:** correlation > 0 in ≥3 of the 4 pathways. Glycolysis is descriptive only
and excluded from the pass count, isobaric LC-MS leaves it too few cleanly mapped
metabolites to test (hexose phosphates co-elute; several TCA-adjacent compounds
are lost to chromatographic overlap).

This is independent of the primary test: it asks whether the paired data itself
shows coordinated gene/metabolite activity in known pathways, the precondition
for the embedding result to be meaningful. It does not override §3.

Inputs are already on disk: pathway gene lists from the cached
`link_hsa_hsa00010/00020/00260/00670.tsv`, metabolite lists from
`link_compound_map00010/00020/00260/00670.tsv` (fetched in `03`).

---

## 5. What counts as failure

The claim is **not supported** if either holds:

- The aggregate test (§3.4) is not significant in the predicted direction —
  co-members are statistically indistinguishable from the composition-matched
  baseline. This is a null result and is reported as one, not buried.
- The aggregate test is significant at one threshold but not across the full
  2 / 3 / 5 sweep (§3.5), a threshold artifact, not a robust finding.

A null result is an acceptable and reportable outcome. The purpose of this
document is to test the claim, not to confirm it.

---

## 6. Locked vs. measured

**Locked before the model (this document):** the claim and its direction; the
within-modality primary number; the composition-matched baseline with N = 1000;
the per-module rule (95th percentile); the aggregate binomial test against
p₀ = 0.05; the ≥3 headline threshold with 2 / 3 / 5 sensitivity; the FDR
reporting; the four-pathway data-space secondary check and its pass rule; the
failure criteria.

**Measured already, and not outcomes of this test:** KEGG coverage and module
member counts (Day 2); per-modality intrinsic dimensionality (Day 3 PCA). These
informed the threshold and encoder choices in DECISIONS.md and are recorded
there, not here.

---

## Amendments

(None. Any change after the date above is appended here with a date and reason;
the text above is left unmodified.)