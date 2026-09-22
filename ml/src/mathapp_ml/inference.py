"""Cached inference from trusted operator-selected local artifacts."""
from functools import lru_cache
from threading import RLock

_lock = RLock()


@lru_cache(maxsize=2)
def _load(path):
    import joblib
    import sklearn
    # joblib is pickle-based. Never load model uploads supplied by API clients.
    artifact = joblib.load(path)
    if artifact["sklearn_version"] != sklearn.__version__:
        raise ValueError("Classifier scikit-learn version differs; use the lockfile or retrain")
    return artifact


def predict(text, path, threshold=0.60, margin=0.15):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Question must be nonempty text")
    if len(text) > 20000:
        raise ValueError("Question exceeds 20000 characters")
    if not 0 <= threshold <= 1 or not 0 <= margin <= 1:
        raise ValueError("Threshold and margin must be between zero and one")
    with _lock:
        artifact = _load(str(path))
    pipeline = artifact["pipeline"]
    scores = dict(zip(pipeline.classes_, map(float, pipeline.predict_proba([text.strip()])[0])))
    ordered = sorted(scores, key=scores.get, reverse=True)
    top, second = ordered[:2]
    unseen = pipeline.named_steps["features"].transform([text.strip()]).nnz == 0
    uncertain = unseen or scores[top] < threshold or scores[top] - scores[second] < margin
    return {"label": "UNKNOWN" if uncertain else top, "suggested_label": top,
            "scores": scores, "confidence": scores[top], "uncertain": uncertain,
            "model_version": artifact["version"], "experimental": artifact["experimental"]}
