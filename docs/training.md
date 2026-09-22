# Local classifier workflow

The package under `ml/src/mathapp_ml` replaces the old MLMath training approach
(TF-IDF plus logistic regression) with question-only features and reproducible
group-separated evaluation. It requires no model-provider API key or tokens.

1. Audit: `.venv/bin/mathapp-ml audit data/raw/math_subject_classifier_en_1000.csv`
2. Train an experimental candidate:
   `.venv/bin/mathapp-ml train data/raw/math_subject_classifier_en_1000.csv --output models/baseline-v1 --include-pending`
3. Inspect `report.json` and `splits.json` in that directory.
4. Try inference:
   `.venv/bin/mathapp-ml predict 'Evaluate lim x->2 x^2' --model models/baseline-v1/classifier.joblib`
5. Register provenance: `.venv/bin/python backend/manage.py register_model models/baseline-v1`

Existing candidate directories cannot be overwritten. Use `baseline-v2`, etc.,
for new experiments. The model is not retrained when the app starts or a user
asks a question. It is loaded once per backend process on its first inference.
Only trusted operator-selected model files may be loaded: joblib uses pickle.
Use the same scikit-learn version as training (the checked local lockfile pins it).

## What the experiment does

- Validates all rows without printing questions in diagnostics.
- Uses only `question` as input and `label` as the supervised target.
- Combines word and character TF-IDF features so symbols and short variables can
  contribute without discarding the word-problem wording.
- Separates about 60% training, 20% validation and 20% held-out test data.
- Unions declared template groups and detected number-only variants before splitting.
- Fits preprocessing only on training rows. Selects between two regularization
  settings using validation macro F1. Evaluates the selected, unchanged model on
  test rows; it never fits on those test rows.
- Saves artifact hash, dataset hash, dependency versions, split membership and
  confusion matrix. Reports do not copy full question text.

The first CSV has 1,000 English synthetic examples, all pending. The explicit
`--include-pending` option is for a baseline only; normal training uses approved
examples. Rejecting a row excludes it even from an experimental run.

## Interpretation

Test accuracy in the report is the raw highest-score classification, before the
inference rejection threshold. It is measured against generated labels, not
independently verified truth. Synthetic wording, missed template families and
label mistakes can overstate real-world performance. A separate reviewed real
test set is required before claiming production accuracy. English training does
not establish Macedonian accuracy.

Inference returns UNKNOWN when the top class score is below 0.60, the gap to the
runner-up is below 0.15, or no features are recognized. These are conservative
initial heuristics, not calibrated confidence or a reliable out-of-domain
detector. UNKNOWN means review/clarification, not a training label. Difficulty,
correctness, and solving are outside this classifier's scope.

Set `ML_MODEL_PATH` to opt into a specific model. An empty value yields unknown
classification in the solver and HTTP 503 in the standalone classify endpoint.
Experimental artifacts are blocked when `DEBUG=False`. Restart backend workers
when promoting a new immutable version. Never silently overwrite a loaded file.
