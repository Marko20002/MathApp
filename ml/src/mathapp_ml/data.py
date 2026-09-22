"""Validate CSVs without exposing question text in diagnostics."""
import csv
import hashlib
import io
import re
import unicodedata
from collections import Counter
from pathlib import Path

COLUMNS = ["id", "question", "label", "subtopic", "language", "source", "group_id", "review_status"]
LABELS = ("CALCULUS", "PROBABILITY", "DISCRETE")
STATUSES = ("pending", "approved", "rejected")


def normalized_question(text):
    # NFC preserves meaningful superscripts: x² must not become x2.
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def question_hash(text):
    return hashlib.sha256(normalized_question(text).encode()).hexdigest()


def template_fingerprint(text):
    # Catches number-only variants. This is not semantic deduplication.
    text = re.sub(r"\d+(?:\.\d+)?", "#", normalized_question(text).casefold())
    return hashlib.sha256(text.encode()).hexdigest()


def load_csv(path):
    raw = Path(path).read_bytes()
    errors, records, seen_ids, seen_questions = [], [], set(), set()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""), strict=True)
    if reader.fieldnames != COLUMNS:
        raise ValueError("CSV header must be: " + ",".join(COLUMNS))
    for number, row in enumerate(reader, 2):
        if None in row or any(v is None or not v.strip() for v in row.values()):
            errors.append(f"Row {number}: missing field or wrong column count")
            continue
        row = {k: v.strip() for k, v in row.items()}
        before = len(errors)
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", row["id"]):
            errors.append(f"Row {number}: invalid ID")
        if row["id"] in seen_ids:
            errors.append(f"Row {number}: duplicate ID")
        digest = question_hash(row["question"])
        if digest in seen_questions:
            errors.append(f"Row {number}: duplicate normalized question")
        if row["label"] not in LABELS:
            errors.append(f"Row {number}: invalid subject label")
        if row["review_status"] not in STATUSES:
            errors.append(f"Row {number}: invalid review status")
        if row["language"] not in ("en", "mk"):
            errors.append(f"Row {number}: language must be en or mk")
        for key, limit in {"question": 20000, "subtopic": 100, "source": 500, "group_id": 200}.items():
            if len(row[key]) > limit:
                errors.append(f"Row {number}: {key} exceeds {limit} characters")
        if "\x00" in "".join(row.values()):
            errors.append(f"Row {number}: NUL character is not allowed")
        seen_ids.add(row["id"])
        seen_questions.add(digest)
        if before == len(errors):
            records.append(row)
    if errors:
        raise ValueError(f"{len(errors)} CSV validation errors:\n" + "\n".join(errors[:25]))
    if not records:
        raise ValueError("CSV contains no examples")
    report = {"sha256": hashlib.sha256(raw).hexdigest(), "rows": len(records),
              "labels": dict(Counter(r["label"] for r in records)),
              "review_status": dict(Counter(r["review_status"] for r in records)),
              "languages": dict(Counter(r["language"] for r in records)),
              "sources": dict(Counter(r["source"] for r in records)),
              "declared_groups": len({r["group_id"] for r in records}),
              "effective_groups": len(set(effective_groups(records)))}
    return records, report


def effective_groups(records):
    """Union declared groups and numeric variants, including transitive links."""
    parents = list(range(len(records)))

    def root(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    seen = {}
    for i, row in enumerate(records):
        for key in (("declared", row["group_id"]), ("template", template_fingerprint(row["question"]))):
            if key in seen:
                parents[root(i)] = root(seen[key])
            else:
                seen[key] = i
    return [root(i) for i in range(len(records))]
