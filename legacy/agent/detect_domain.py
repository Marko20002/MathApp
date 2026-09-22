import re
from typing import Tuple, Dict, List

# 1) Доменски токени (regex) — широки, но внимателни
DOMAIN_PATTERNS: Dict[str, List[tuple[str, int]]] = {
    "calculus": [
        (r"\blim\b|\\lim", 6),
        (r"∫|\\int|∬|∭", 7),
        (r"\bdx\b|\bdy\b|\bdz\b|\bdt\b|dθ\b|dA\b|dV\b", 5),
        (r"\bderivative\b|\bizvod\b|d/dx|d/dy|\\frac\{d\}", 5),
        (r"\bgradient\b|\bdiv\b|\bcurl\b|\\nabla", 3),
        (r"\bsin\b|\bcos\b|\btan\b|\bcot\b|\bsec\b|\bcsc\b", 2),
        (r"\barcsin\b|\barccos\b|\barctan\b|\bsinh\b|\bcosh\b|\btanh\b", 2),
        (r"\bln\b|\blog\b|\bexp\b|e\^|e\*\*", 2),
        (r"sqrt|√", 2),
        (r"\\sum|∑|\\prod|∏", 2),  # series show up in calc2 too
        (r"∞|\\infty", 2),
    ],
    "probability": [
        (r"\bP\s*\(|\bp\s*\(", 7),
        (r"\bprobability\b|\bverojatnost\b|веројатност", 4),
        (r"\bconditional\b|условна|uslovna|\bBayes\b|Баес|bayes|тотална|totalna", 5),
        (r"\bpoisson\b|пуасон|\\text\{Poisson\}", 6),
        (r"\bbinom(ial)?\b|бином", 5),
        (r"\bnormal\b|нормал|\bgaussian\b", 4),
        (r"\bexponential\b|експон", 4),
        (r"\bgeometric\b|геометр", 4),
        (r"\buniform\b|рамномер", 3),
        (r"\bmean\b|очекуван|ocekuvan|\bexpected\b|E\s*\(", 3),
        (r"\bvariance\b|varijansa|σ\^2|\bstd\b|\\sigma", 3),
        (r"\bchi\b|χ|x\^2|chi-square|хи-квадрат", 4),
        (r"\bt-test\b|\bz-test\b|p-value|p\s*-\s*value|hipotez|hypothesis", 4),
        (r"\bpmf\b|\bpdf\b|\bcdf\b|F\s*\(", 3),
        (r"\blambda\b|λ|\bmu\b|μ", 2),
    ],
    "discrete": [
        (r"∀|\\forall", 7),
        (r"∃|\\exists", 7),
        (r"¬|\\neg", 6),
        (r"∧|\\wedge", 6),
        (r"∨|\\vee", 6),
        (r"↔|\\leftrightarrow", 5),
        (r"->|→|\\to", 2),  # arrow is weaker because appears elsewhere too
        (r"\bpredicate\b|предикат|predikat", 5),
        (r"\binduction\b|индукц", 5),
        (r"\bgraph\b|граф|vertex|edge|јазол|ребро", 4),
        (r"\brelation\b|релац", 4),
        (r"\bset\b|множество|subset|⊆|⊂|∪|∩|∅", 4),
        (r"\bcombinatorics\b|комбинатор", 4),
        (r"\bmod\b|\bmodulo\b|остаток", 3),
        (r"\bboolean\b|булова|k-map|карно", 3),
    ]
}

def detect_domain(core: str) -> Tuple[str, float]:
    """
    Returns (domain, confidence).
    domain in {'calculus','probability','discrete','unknown'}.
    Confidence is a soft ratio based on weighted scores.
    """
    t = core or ""
    if not t.strip():
        return "unknown", 0.0

    scores = {k: 0 for k in DOMAIN_PATTERNS.keys()}

    # 2) Weighted scoring by regex matches
    for domain, pats in DOMAIN_PATTERNS.items():
        for pat, w in pats:
            if re.search(pat, t, flags=re.IGNORECASE):
                scores[domain] += w

    # 3) Additional structure hints (operator density)
    # Helps distinguish plain text vs math-like text, but doesn't force domain.
    op_count = len(re.findall(r"[\+\-\*/\^=]", t))
    digit_count = len(re.findall(r"\d", t))
    if op_count >= 3:
        scores["calculus"] += 1
        scores["probability"] += 1
        scores["discrete"] += 1
    if digit_count >= 6:
        scores["probability"] += 1  # probabilities often have parameters/percentages

    best = max(scores, key=scores.get)
    total = sum(scores.values())

    if scores[best] == 0:
        return "unknown", 0.0

    # confidence: how dominant is best score vs others
    conf = scores[best] / total

    # optional: if best barely beats second best, lower confidence
    second = sorted(scores.values(), reverse=True)[1]
    if scores[best] - second <= 2:
        conf *= 0.75

    return best, float(conf)
