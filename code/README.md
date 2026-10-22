# Code

Run all scripts from the repository root. They read their inputs from `data/` and write their outputs to `outputs/`; set the environment variable `SOFTPOWER_OUTPUT_DIR` to write them elsewhere. Package versions are listed in `requirements.txt` (Python 3.10.11).

## Figure scripts (`figures/`)

- `Figure2.py` – Fig. 2. Panel a uses the stored t-SNE coordinates in `data/figure2a_visualization_coordinates.csv` (the projection is not recomputed); panel b is computed from `data/family_work_membership.csv`. The script produces the same content as the published figure in an earlier layout; the script used for the final single-column layout was not preserved.
- `Figure3.py` – Fig. 3, from `data/figure3_v3_plot_data.csv`.
- `Figure4.py` – Fig. 4. Threshold-sensitivity values are read from `data/threshold_sensitivity_results.csv` and `data/family_stability_results.csv`, and the robustness runs from `data/robustness_results.csv`; the df ≥ 3 reference values are computed from `data/recurrent_phrase_dictionary_df3.csv`, `data/community_family_mapping.csv`, `data/work_phrase_incidence_df3.csv` and `data/corpus_manifest.csv`. Panel b summarizes the 11 robustness runs whose parameters differ from the primary configuration. Values are plotted at the precision shown in the figure.

`Figure3.py` and `Figure4.py` produce the published Figs. 3 and 4 (119 mm wide). The figures use Arial; if Arial is not installed, the scripts fall back to Liberation Sans.

## Prompt templates (`prompts/`)

- `semantic_screening_prompt.txt` – the prompt used for first-pass semantic screening. For records judged core, the same prompt asked the model to return three to six candidate phrases (`dimension_phrases`); these are the candidate phrases analyzed in the article.
- `semantic_screening_retry_prompt.txt` – used when a response could not be parsed or did not follow the required JSON schema.

The templates are given as the Python functions in which they were defined.

## Not included

The script that called the DeepSeek API and the scripts of the full analysis pipeline are not included, because they operate on raw Web of Science and Scopus records and on intermediate files derived from them. They are available from the corresponding authors on reasonable request.

The phrase embeddings were computed with sentence-transformers 5.2.0 (all-MiniLM-L6-v2). The scripts here use the stored embeddings in `data/corrected_embeddings_df3.npy`, so sentence-transformers is not required.
