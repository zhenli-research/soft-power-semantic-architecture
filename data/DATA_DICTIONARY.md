# Data dictionary

All CSV files are UTF-8, comma-delimited derived outputs. `work_id` is a public study-level identifier; `phrase_id` is a stable derived identifier assigned in canonical-phrase sort order; `community_id` identifies one of the seven communities of the df >= 3 partition (`C1`–`C7`); `family_id` is a non-exclusive analytical family (`F1`–`F5`). Counts of family membership are therefore not mutually exclusive unless a field explicitly says otherwise. Missing values mean “not applicable at this result level” unless specified below.

In file and column names, “corrected” refers to the final version of the analysis reported in the article; earlier working versions are not included.

## `corpus_manifest.csv` — one row per final-core work (2,055 rows)

- `work_id` (string): public derived work identifier used for joins.
- `year` (integer): publication year.
- `doi` (string, nullable): DOI as a public identifier where available; blank means no DOI is supplied in this manifest.

## `canonical_phrase_dictionary.csv` — canonical vocabulary (8,308 rows)

- `phrase_id` (string): stable public phrase identifier.
- `canonical_phrase` (string): normalized phrase text.
- `df` (integer): document frequency, the number of final-core works supporting the canonical phrase.

Phrases were not shortened after normalization. 228 canonical phrases contain more than five words, either because hyphens and slashes were replaced with spaces during normalization or because the model returned a phrase longer than the five-word limit given in the prompt. All 228 have df ≤ 2, so none is part of the df ≥ 3 backbone.

## `recurrent_phrase_dictionary_df3.csv` — final recurrent phrase backbone (256 rows)

- `phrase_id` (string): join key to the canonical dictionary.
- `canonical_phrase` (string): normalized recurrent phrase text.
- `df` (integer): document frequency in final-core works; each row meets df >= 3.
- `community_id` (category `C1`–`C7`): Leiden community assignment.
- `family_id` (category `F1`–`F5`): mapped analytical family.

## `work_phrase_incidence_df3.csv` — derived recurrent phrase/work incidence

- `work_id` (string): work identifier.
- `phrase_id` (string): recurrent phrase identifier.
- `community_id` (category): final community of that phrase.
- `family_id` (category): family of that community.

Each row is one derived work–recurrent-phrase incidence; works and families are non-exclusive across rows.

## `community_family_mapping.csv` — final community summary (7 rows)

- `community_id` (category `C1`–`C7`): community identifier.
- `community_label` (string): descriptive English label assigned to the final community.
- `family_id` (category `F1`–`F5`): analytical family containing the community.
- `phrase_n` (integer): number of recurrent df >= 3 phrases in the community.
- `work_n` (integer): number of unique final-core works supporting at least one phrase in the community; counts may overlap across communities.

## `family_work_membership.csv` — non-exclusive work/family membership (1,505 rows)

- `work_id` (string): work identifier.
- `family_id` (category `F1`–`F5`): assigned analytical family.
- `family_label_en` (string): English family label.
- `communities` (semicolon-delimited category string): final communities supporting the work’s family membership.
- `supporting_phrases` (integer): number of recurrent phrases supporting that work/family membership.
- `year` (integer): work publication year.

One work can occur in multiple family rows. This file is the source for Figure 2b: diagonal co-membership counts works in a family; off-diagonal counts works assigned to both families.

## `temporal_results.csv` — annual and pooled-period family results (200 rows)

- `result_level` (category `annual` or `period`): result grain. Annual rows populate annual fields; period rows populate pooled-period fields.
- `year` (integer, annual rows only): publication year, 1990–2025; blank for period rows.
- `period` (category): descriptive interval `1990–2007`, `2008–2015`, `2016–2020`, or `2021–2025`.
- `family_id` (category): non-exclusive family identifier.
- `family_label_en` (string): English family label.
- `n_works` (integer, annual rows): unique works in the family/year.
- `core_works` (integer, annual rows): final-core works in the publication year, used as annual structural context.
- `baseline_covered_works` (integer, annual rows): unique baseline-covered works in the publication year; denominator for `family_prevalence`.
- `family_prevalence` (proportion, annual rows): `n_works / baseline_covered_works`; blank when the denominator is zero.
- `baseline_coverage` (proportion, annual rows): `baseline_covered_works / core_works`; blank when the denominator is zero.
- `figure3b_visible` (Boolean, annual rows): `True` when the Figure 3b annual denominator is at least 10; `False` otherwise; blank for period rows.
- `family_unique_works` (integer, period rows): unique works in the family across the complete descriptive period.
- `period_core_works` (integer, period rows): final-core works in the complete period.
- `period_baseline_covered_works` (integer, period rows): baseline-covered works in the complete period.
- `pooled_family_prevalence` (proportion, period rows): `family_unique_works / period_baseline_covered_works`; non-exclusive across families.
- `pooled_baseline_coverage` (proportion, period rows): `period_baseline_covered_works / period_core_works`.

## `robustness_results.csv` — fixed-vocabulary robustness runs (14 rows)

Three rows (seed = 42, k = 15 and resolution = 1.0 in their respective sweeps) use the primary configuration and are excluded from the robustness summaries reported in the article.

- `run_id` (string): unique public identifier for the robustness run.
- `sweep_type` (category `seed`, `k`, or `resolution`): graph/partition parameter varied in the run.
- `value` (number): value of the parameter named by `sweep_type`.
- `k` (integer): k-nearest-neighbor setting used for the run.
- `resolution` (number): Leiden resolution parameter used for the run.
- `seed` (integer): partition random seed used for the run.
- `community_count` (integer): number of communities in the run.
- `cluster_size_vector` (semicolon-delimited integers): community phrase sizes for the run, ordered as recorded by the final run output.
- `ARI_vs_corrected_primary` (proportion): adjusted Rand index against the primary df >= 3 partition.
- `AMI_vs_corrected_primary` (proportion): adjusted mutual information against the primary df >= 3 partition.
- `graph_edge_count` (integer): edge count in the run’s graph representation.

## `threshold_sensitivity_results.csv` — df >= 4 and df >= 5 sensitivity

- `threshold` (category `df>=4` or `df>=5`): recurrence threshold compared with the primary df >= 3 analysis.
- `retained_phrase_count` (integer): phrases retained at the threshold.
- `cluster_count` (integer): communities recovered at the threshold.
- `cluster_sizes` (semicolon-delimited integers): phrase counts of recovered clusters.
- `covered_works` (integer): unique final-core works covered by retained phrases.
- `core_works_total` (integer): final-core denominator (2,055).
- `document_coverage` (proportion): `covered_works / core_works_total`.
- `shared_phrases_with_df3` (integer): retained phrases shared with the df >= 3 backbone.
- `shared_phrase_rate_vs_df3` (proportion): `shared_phrases_with_df3 / 256`.
- `ARI_vs_df3` (proportion): adjusted Rand index versus the df >= 3 partition on shared phrases.
- `AMI_vs_df3` (proportion): adjusted mutual information versus the df >= 3 partition on shared phrases.
- `graph_edge_count` (integer): edge count in the threshold graph.

## `family_stability_results.csv` — family-level threshold correspondence

- `threshold` (category `df>=4` or `df>=5`): alternative recurrence threshold.
- `shared_phrase_count` (integer): phrases shared with the df >= 3 backbone.
- `alternative_cluster_count` (integer): clusters in the alternative threshold partition.
- `family_agreement_count` (integer): shared phrases whose alternative-cluster family correspondence agrees with the df >= 3 family.
- `family_agreement_rate` (proportion): `family_agreement_count / shared_phrase_count`.
- `family_cohens_kappa` (proportion): Cohen’s kappa for family correspondence on shared phrases.
- `family_ARI` (proportion): adjusted Rand index for family labels on shared phrases.
- `family_AMI` (proportion): adjusted mutual information for family labels on shared phrases.
- `macro_F1` (proportion): unweighted mean of the five family F1 scores.
- `F1_recall` (proportion): recall for family F1 against the df >= 3 family reference.
- `F2_recall` (proportion): recall for family F2 against the df >= 3 family reference.
- `F3_recall` (proportion): recall for family F3 against the df >= 3 family reference.
- `F4_recall` (proportion): recall for family F4 against the df >= 3 family reference.
- `F5_recall` (proportion): recall for family F5 against the df >= 3 family reference.
- `mean_alternative_cluster_purity` (proportion): mean dominant-family purity across alternative clusters.
- `minimum_alternative_cluster_purity` (proportion): minimum dominant-family purity among alternative clusters.
- `family_structure_verdict` (category): final recorded structural interpretation (`FAMILY_STRUCTURE_SUPPORTED` or `FAMILY_STRUCTURE_PARTIALLY_SUPPORTED`).
- `structural_note` (string): recorded explanation of the verdict.

## `df2_validation_summary.csv` — final df = 2 validation decision (one row)

- `population_total` (integer): full df = 2 candidate population.
- `attached_n` (integer): candidates attached to the df >= 3 structure.
- `unattached_n` (integer): candidates not attached to the structure.
- `attached_sample_n` (integer): attached cases in the independent accuracy sample.
- `diagnostic_unattached_n` (integer): unattached diagnostic cases.
- `human_reliability_n` (integer): cases in the human reliability sample.
- `agreement_n` (integer): agreeing cases in the human reliability sample.
- `agreement_rate` (proportion): `agreement_n / human_reliability_n`.
- `kappa` (proportion): Cohen’s kappa for the human reliability comparison.
- `weighted_strict_accuracy` (proportion): weighted strict attached-classification accuracy from the independent validation design.
- `ci_lower` (proportion): lower confidence bound for weighted strict accuracy.
- `ci_upper` (proportion): upper confidence bound for weighted strict accuracy.
- `criterion` (proportion): weighted strict accuracy required to retain the df = 2 extension, applied as an evaluation rule rather than a pre-specified analytical threshold (Section 2.6 of the article).
- `decision` (category `NOT_RETAINED`): final df = 2 retention decision.

## `semantic_screening_validation.csv` — sampled semantic-screening validation (400 rows)

- `sample_id` (integer): sample identifier, unique within `sample_group`.
- `sample_group` (category `core` or `noncore`): sampled screening population.
- `sampling_stratum` (string, nullable): recorded noncore stratification label; blank for core cases not stratified in this file.
- `human_label` (binary integer): human screening label (`1` retained/eligible, `0` not retained/eligible).
- `first_pass_model_label` (binary integer): first-pass model screening label using the same binary coding.
- `sampling_weight` (number): design weight for the sampled stratum/group.
- `sampling_frame_size` (integer): population size represented by the sample stratum/group.

## `phrase_extraction_validation.csv` — phrase-support audit (504 rows)

- `audit_id` (string): audit-case identifier; several phrase rows may belong to one audited work.
- `work_id` (string): audited work identifier.
- `sample_group` (category): audit frame (`baseline_df_ge_3_covered`, `core_unassigned`, or `df2_extended_only`).
- `work_audit_result` (category): work-level review result (`PASS`, `PARTIAL`, or `MINOR_ISSUE`).
- `phrase` (string): extracted phrase assessed in the audit.
- `phrase_support` (category): support assessment (`DIRECTLY_SUPPORTED`, `SEMANTICALLY_SUPPORTED`, or `UNSUPPORTED`). This measures support of listed phrases, not phrase-extraction recall or completeness.
- `major_omission` (Boolean string `TRUE`/`FALSE`): whether the audit recorded a major omission for the work.

## `lexical_concentration_results.csv` — within-community lexical summaries (7 rows)

- `community_id` (category): final community.
- `family_id` (category): mapped family.
- `phrase_count` (integer): phrases in the community.
- `exact_soft_power_count` (integer): phrases exactly equal to “soft power”.
- `power_token_phrase_count` (integer): phrases containing the token “power”.
- `within_pair_count` (integer): all unordered within-community phrase pairs used for the mean.
- `within_raw_jaccard_mean` (proportion): mean Jaccard overlap of unmasked phrase-token sets across within-community pairs.
- `within_anchor_masked_jaccard_mean` (proportion): mean within-community Jaccard overlap after masking the anchor terms “soft” and “power”; no stopword filtering is implied.
- `sampled_cross_pair_count` (integer): number of cross-community comparison pairs sampled under the recorded sequence.
- `sample_seed` (integer): pseudorandom seed used for the cross-community sampling sequence.

## `figure2a_visualization_coordinates.csv` — Figure 2a visualization input (256 rows)

- `phrase` (string): final recurrent phrase text.
- `df` (integer): document frequency of the phrase in final-core works.
- `final_cluster_id` (category `C1`–`C7`): community assignment displayed by color.
- `family_id` (category `F1`–`F5`): mapped family for the phrase’s community.
- `tsne_1` (float): first stored t-SNE visualization coordinate.
- `tsne_2` (float): second stored t-SNE visualization coordinate.

The two t-SNE fields reproduce the visualization only. They were not used to determine Leiden communities and must not be treated as analytical distances or community-assignment inputs.

## `figure3_v3_plot_data.csv` — Figure 3 plotting input (180 rows)

- `year`, `period`, `family_id`, `family_label_en`: recorded annual family-series identifiers and labels.
- `n_works`, `core_works`, `baseline_covered_works`, `family_prevalence`, `baseline_coverage`: annual values used by the Figure 3 script.
- `figure3b_visible`, `family_label_short`, `prevalence_pct_recomputed`, `plotted_in_panel_a`, `plotted_in_panel_b`: display fields for the two Figure 3 panels.

This is the table from which the published Figure 3 was drawn. It contains no bibliographic titles, abstracts, author keywords, or source-record text.

## Supplementary Note S1 derived inputs

- `s1_corrected_work_phrase_pairs.csv`: complete `work_id`–canonical-phrase incidence for the 2,055 final core works (10,269 rows). The Note S1 script removes the 51 added work–phrase pairs from it before recalculating document frequency.
- `s1_corrected_phrase_vocabulary.csv`: canonical phrases with their document frequencies in the primary analysis.
- `s1_primary_clusters_df3.csv`: the 256 df >= 3 phrases with their graph `node_index` and Leiden cluster identifier in the primary partition, used for agreement scoring.
- `corrected_embeddings_df3.npy`: NumPy array of the 256 recurrent-phrase embeddings (all-MiniLM-L6-v2, 384 dimensions). The Note S1 script subsets this stored array; it does not re-encode text.

These files are derived analytical inputs, not WoS/Scopus exports and not DeepSeek request or response caches. The Note S1 script uses `corpus_manifest.csv` only to verify the final 2,055-work denominator and to join a DOI to its released `note_s1_added_pairs.csv` output.
