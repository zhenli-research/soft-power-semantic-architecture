# Note S1 sensitivity analysis

This folder contains the materials for the sensitivity analysis reported in Note S1 of Online Resource 1.

- `note_s1_added_pairs.csv` – the 51 work–phrase pairs added after first-pass extraction for five final core works. The `text_match_category` column compares each phrase with the title, abstract and keywords of its work: `a`, the phrase appears verbatim (31 pairs); `b`, all of its content words appear (8 pairs); `c`, only some of them appear (12 pairs). The `author_judgement` column records the authors' judgment of textual support: `supported_text` (categories `a` and `b`; 39 pairs), `supported_context` (supported by the context of the abstract; 8 pairs) and `weak` (weakly supported; 4 pairs).
- `note_s1_sensitivity.py` – removes the 51 pairs, recalculates document frequency, retains phrases with df ≥ 3 and repeats the primary graph construction and Leiden community detection with the primary parameters, using the stored embeddings (phrases are not re-encoded).
- `note_s1_sensitivity_results.json` – output of the script.

## Running

From the repository root:

    python supplement_note_s1/note_s1_sensitivity.py

Outputs are written to `outputs/note_s1/`. The script does not overwrite existing output files, so delete that folder before running it again. The `author_judgement` column is not produced by the script and is blank in its output.

## Results

- Recurrent phrases (df ≥ 3): 249
- Communities: 7 (sizes 61, 48, 37, 34, 26, 25, 18)
- Structural coverage: 1,063 of 2,055 works (51.73%)
- Agreement with the primary partition on the 249 shared phrases: ARI 0.892, AMI 0.924; family-level Cohen's κ 0.946

These values were obtained with Python 3.10.11, numpy 2.2.6, pandas 2.3.3, scikit-learn 1.7.2, python-igraph 1.0.0 and leidenalg 0.11.0.
