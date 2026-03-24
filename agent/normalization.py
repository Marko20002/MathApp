import re
from dataclasses import dataclass
from agent.math_tokens import MATH_TOKENS
from agent.detect_domain import detect_domain
from typing import Dict, Any, Tuple, Optional


@dataclass
class CleanResult:
    raw: str
    core: str
    domain: str
    confidence: float
    normalized: Dict[str, str]

def clean_prompt(text: str) -> CleanResult:
    raw = text or ""
    core = extract_core_span(raw)
    domain, conf = detect_domain(core)

    if domain == "calculus":
        norm = normalize_calculus(core)
    elif domain == "probability":
        norm = normalize_probability(core)
    elif domain == "discrete":
        norm = normalize_discrete(core)
    else:
        norm = {"canonical_text": core}

    return CleanResult(raw=raw, core=core, domain=domain, confidence=conf, normalized=norm)





def normalize_calculus(core: str) -> Dict[str, str]:
    s = core.strip()

    # limit arrow normalization only if lim exists
    if re.search(r"\blim\b", s, re.I):
        # x-0 -> x->0 ONLY when it looks like a limit context
        s = re.sub(r"\b([a-zA-Z])\s*-\s*([0-9]+)\b", r"\1->\2", s)
        s = re.sub(r"\b([a-zA-Z])\s*(?:->|→)\s*([0-9]+)\b", r"\1->\2", s)

    # sinx -> sin(x) (single letter variable)
    s = re.sub(r"\b(sin|cos|tan|ln|log)\s*([a-zA-Z])\b", r"\1(\2)", s, flags=re.I)
    s = re.sub(r"\bsqrt\s*([a-zA-Z0-9]+)\b", r"sqrt(\1)", s, flags=re.I)

    s = re.sub(r"\s+", " ", s).strip()

    # minimal LaTeX
    latex = s
    latex = re.sub(r"\blim\s+([a-zA-Z])\s*->\s*([^\s]+)\s*", r"\\lim_{\1\\to \2} ", latex, flags=re.I)
    latex = latex.replace("sin(", "\\sin(").replace("cos(", "\\cos(").replace("tan(", "\\tan(")
    latex = latex.replace("ln(", "\\ln(").replace("sqrt(", "\\sqrt{").replace(")", "}")  # very rough

    return {"canonical_ascii": s, "canonical_latex": latex}

def normalize_probability(core: str) -> Dict[str, str]:
    s = core.strip()
    s = s.replace("p(", "P(")
    s = re.sub(r"\s+", " ", s).strip()
    return {"canonical_text": s}

def normalize_discrete(core: str) -> Dict[str, str]:
    s = core.strip()
    s = s.replace("=>", "->").replace("⇒", "->")
    s = re.sub(r"\s*(∀|∃|¬|∧|∨|->|↔)\s*", r" \1 ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return {"canonical_text": s}



#dava score od text primer lim izvod +=2 E+=2 diskretna....
def math_score(s: str) -> int:
    MATH_TOKEN_RE = [re.compile(pat, flags=re.IGNORECASE) for pat in MATH_TOKENS]
    score = 0
    for rx in MATH_TOKEN_RE:
        if rx.search(s):
            score += 2

    score += len(re.findall(r"[0-9]", s)) // 2
    score += len(re.findall(r"[\+\-\*/\^=]", s))
    return score


#Go vadi naj matematicko delce od tekstot
def extract_core_span(text: str, max_window_chars: int = 1200) -> str:

    s = global_clean(text)
    if not s:
        return ""

    # If already short, keep it.
    if len(s) <= max_window_chars:
        return s

    # Split into chunks by punctuation / sentence-ish boundaries
    parts = re.split(r"(?<=[\.\:\;\n])\s+", s)
    parts = [p.strip() for p in parts if p.strip()]

    # If splitting failed, fallback to sliding window
    if len(parts) <= 1:
        best = ""
        best_sc = -1
        for i in range(0, len(s), 120):
            chunk = s[i:i+max_window_chars]
            sc = math_score(chunk)
            if sc > best_sc:
                best_sc = sc
                best = chunk
        return best.strip()

    # Score each part; also consider combining adjacent parts (for probability text)
    best = parts[0]
    best_sc = math_score(best)

    for i, p in enumerate(parts):
        sc = math_score(p)
        if sc > best_sc:
            best_sc = sc
            best = p

        # combine with next sentence if likely part of same task
        if i + 1 < len(parts):
            combined = (p + " " + parts[i+1]).strip()
            if len(combined) <= max_window_chars:
                sc2 = math_score(combined)
                if sc2 > best_sc:
                    best_sc = sc2
                    best = combined

    return best.strip()


def global_clean(text :str) -> str:
    if not text:
        return ""
    s = text.strip()
    s = s.replace("→", "->").replace("⇒", "->").replace("−", "-").replace("×", "*")
    s = re.sub(r"[?!]{2,}", "?", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s




