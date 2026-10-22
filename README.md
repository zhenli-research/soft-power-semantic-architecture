# Data and code for "Mapping the Semantic Structure of Soft Power Research: An LLM-Assisted Bibliometric Analysis, 1990–2025"

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23571334.svg)](https://doi.org/10.5281/zenodo.23571334)

Zhen Li¹, Huaiqun Zhao¹, Zengru Di²\*, Ya Zhou²\*

¹ School of National Safety and Emergency Management, Beijing Normal University, Beijing 100875, China  
² School of Systems Science, Beijing Normal University, Beijing 100875, China  
\* Corresponding authors: Ya Zhou (zhouya@bnu.edu.cn); Zengru Di (zdi@bnu.edu.cn)

This repository contains the derived data, figure-generation code and prompt templates supporting the article above, together with the materials for Note S1 in Online Resource 1.

## Contents

```text
soft-power-semantic-architecture/
├── CITATION.cff
├── FILE_CHECKSUMS.csv
├── LICENSE
├── README.md
├── code/
│   ├── README.md
│   ├── requirements.txt
│   ├── figures/
│   │   ├── Figure2.py
│   │   ├── Figure3.py
│   │   └── Figure4.py
│   └── prompts/
│       ├── semantic_screening_prompt.txt
│       └── semantic_screening_retry_prompt.txt
├── data/
│   ├── canonical_phrase_dictionary.csv
│   ├── community_family_mapping.csv
│   ├── corpus_manifest.csv
│   ├── corrected_embeddings_df3.npy
│   ├── DATA_DICTIONARY.md
│   ├── df2_validation_summary.csv
│   ├── family_stability_results.csv
│   ├── family_work_membership.csv
│   ├── figure2a_visualization_coordinates.csv
│   ├── figure3_v3_plot_data.csv
│   ├── LICENSE.md
│   ├── lexical_concentration_results.csv
│   ├── phrase_extraction_validation.csv
│   ├── recurrent_phrase_dictionary_df3.csv
│   ├── robustness_results.csv
│   ├── s1_corrected_phrase_vocabulary.csv
│   ├── s1_corrected_work_phrase_pairs.csv
│   ├── s1_primary_clusters_df3.csv
│   ├── semantic_screening_validation.csv
│   ├── temporal_results.csv
│   ├── threshold_sensitivity_results.csv
│   └── work_phrase_incidence_df3.csv
└── supplement_note_s1/
    ├── note_s1_added_pairs.csv
    ├── note_s1_sensitivity.py
    ├── note_s1_sensitivity_results.json
    └── README.md
```

- `data/` – derived data supporting the article: corpus manifest with study identifiers and DOIs, work–phrase incidence, phrase dictionaries, community and family assignments, temporal results, robustness and threshold-sensitivity results, validation data and figure source data. Each file is described in `data/DATA_DICTIONARY.md`.
- `code/` – figure-generation scripts and the prompt templates used for first-pass semantic screening and candidate phrase extraction; see `code/README.md`.
- `supplement_note_s1/` – the work–phrase pairs added after first-pass extraction, the authors' judgments of their textual support, and the script and output of the sensitivity analysis reported in Note S1; see `supplement_note_s1/README.md`.
- `FILE_CHECKSUMS.csv` – SHA-256 checksums of all other files.

## What is not included

Raw bibliographic records exported from Web of Science and Scopus, including abstracts and other database-supplied text, are not redistributed because of database licensing and copyright restrictions. For the same reason, the cached requests and responses of the LLM screening run are not included, because the requests contain database abstracts. Works are identified by study-specific identifiers and, where available, DOIs.

The script that called the LLM API and the scripts of the full analysis pipeline are not included, because they operate on the raw records and on intermediate files derived from them. They are available from the corresponding authors on reasonable request.

## Reproducing the figures and Note S1

The analyses were run in Python 3.10.11. Install the dependencies with

    pip install -r code/requirements.txt

Fig. 1 is a workflow diagram drawn in PowerPoint and has no script. `code/figures/Figure2.py` produces the content of Fig. 2 in an earlier layout; the script used for the final single-column layout was not preserved. Run the following commands from the repository root:

    python code/figures/Figure2.py                      # Fig. 2 (earlier layout)
    python code/figures/Figure3.py                      # Fig. 3
    python code/figures/Figure4.py                      # Fig. 4
    python supplement_note_s1/note_s1_sensitivity.py    # Note S1

The scripts read their inputs from `data/` and write their outputs to `outputs/`.

## LLM screening

First-pass semantic screening and candidate phrase extraction used the DeepSeek API with the model identifier `deepseek-chat`, which the provider's documentation listed as DeepSeek-V3.2 in non-thinking mode at the time of the run (21 January 2026). The identifier has since been remapped to newer models, so exact reproduction of the original screening outputs cannot be guaranteed. Screening and phrase extraction were performed with a single prompt, provided in `code/prompts/` together with the retry prompt used when a response could not be parsed.

## Licenses

- Code, including the script in `supplement_note_s1/`: MIT License (`LICENSE`).
- Data files in `data/` and `supplement_note_s1/`: Creative Commons Attribution 4.0 International (CC BY 4.0); see `data/LICENSE.md`.

## Citation

Please cite the article and this archive:

Li, Z., Zhao, H., Di, Z., & Zhou, Y. (2026). *Data and code for "Mapping the Semantic Structure of Soft Power Research: An LLM-Assisted Bibliometric Analysis, 1990–2025"* (Version 1.0.0) [Data set and software]. Zenodo. https://doi.org/10.5281/zenodo.23571334

Citation metadata are provided in `CITATION.cff`.
