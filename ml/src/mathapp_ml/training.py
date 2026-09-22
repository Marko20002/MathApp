"""Offline training. No API calls and no automatic model promotion."""
import hashlib
import json
import platform
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import FeatureUnion, Pipeline

from .data import LABELS, effective_groups, load_csv


def split_examples(records):
    y = np.array([r["label"] for r in records])
    groups = np.array(effective_groups(records))
    for label in LABELS:
        if len(set(groups[y == label])) < 10:
            raise ValueError(f"Need at least 10 independent groups for {label}")
    remaining, test = next(StratifiedGroupKFold(5, shuffle=True, random_state=42).split(y, y, groups))
    tr, val = next(StratifiedGroupKFold(4, shuffle=True, random_state=43).split(
        y[remaining], y[remaining], groups[remaining]))
    splits = {"train": remaining[tr], "validation": remaining[val], "test": test}
    for name, indices in splits.items():
        if set(y[indices]) != set(LABELS):
            raise ValueError(f"{name} split lacks a label; add independent groups")
    return splits, groups


def pipeline(c):
    return Pipeline([
        ("features", FeatureUnion([
            ("words", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=30000, sublinear_tf=True)),
            ("characters", TfidfVectorizer(analyzer="char", ngram_range=(2, 5), min_df=2,
                                          max_features=50000, sublinear_tf=True)),
        ])),
        ("classifier", LogisticRegression(C=c, class_weight="balanced", max_iter=1500, random_state=42)),
    ])


def train(csv_path, output, include_pending=False):
    output = Path(output)
    if output.exists():
        raise ValueError("Output directory exists; use a new candidate version")
    rows, audit = load_csv(csv_path)
    allowed = {"approved", "pending"} if include_pending else {"approved"}
    rows = [r for r in rows if r["review_status"] in allowed]
    if not rows:
        raise ValueError("No approved examples. Use --include-pending only for an experimental baseline.")
    splits, groups = split_examples(rows)
    x = np.array([r["question"] for r in rows])  # Never metadata or solutions.
    y = np.array([r["label"] for r in rows])
    trials, best_score, best_model = [], -1, None
    for c in (0.5, 2.0):
        model = pipeline(c)
        model.fit(x[splits["train"]], y[splits["train"]])
        score = f1_score(y[splits["validation"]], model.predict(x[splits["validation"]]), average="macro")
        trials.append({"C": c, "validation_macro_f1": score})
        if score > best_score:
            best_model, best_score = model, score
    indices = splits["test"]
    predicted = best_model.predict(x[indices])
    version = output.name
    report = {
        "version": version, "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "candidate", "experimental": any(r["review_status"] != "approved" for r in rows),
        "limitation": "Held-out dataset evaluation only. Synthetic results do not establish real-world accuracy. Scores are uncalibrated.",
        "dataset": audit, "used_rows": len(rows), "input_fields": ["question"],
        "python_version": platform.python_version(), "sklearn_version": sklearn.__version__,
        "split_seed": [42, 43], "trials": trials,
        "splits": {name: {"rows": len(ids), "groups": len(set(groups[ids])),
                         "labels": dict(Counter(y[ids]))} for name, ids in splits.items()},
        "test": {"accuracy": accuracy_score(y[indices], predicted),
                 "macro_f1": f1_score(y[indices], predicted, average="macro"),
                 "per_class": classification_report(y[indices], predicted, labels=list(LABELS), output_dict=True, zero_division=0),
                 "confusion_matrix_labels": list(LABELS),
                 "confusion_matrix": confusion_matrix(y[indices], predicted, labels=list(LABELS)).tolist()},
    }
    output.mkdir(parents=True)
    artifact = output / "classifier.joblib"
    joblib.dump({"pipeline": best_model, "version": version, "sklearn_version": sklearn.__version__,
                 "labels": list(LABELS), "experimental": report["experimental"]}, artifact)
    report["artifact_sha256"] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    membership = {name: [{"id": rows[int(i)]["id"], "group": int(groups[i])} for i in ids]
                  for name, ids in splits.items()}
    (output / "splits.json").write_text(json.dumps(membership, indent=2), encoding="utf-8")
    return report
