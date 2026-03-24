MATH_TOKENS = [

    # ---------------------
    # CALCULUS - LIMITS
    # ---------------------
    r"\blim\b", r"\\lim",
    r"->", r"→", r"∞", r"infty", r"\\infty",

    # ---------------------
    # CALCULUS - INTEGRALS
    # ---------------------
    r"∫", r"\\int",
    r"\bdx\b", r"\bdy\b", r"\bdz\b", r"\bdt\b", r"\bdθ\b",
    r"dA\b", r"dV\b",
    r"double\s+integral", r"triple\s+integral",
    r"∬", r"∭",

    # ---------------------
    # CALCULUS - DERIVATIVES
    # ---------------------
    r"f'\(", r"\bderivative\b", r"\bizvod\b",
    r"d/dx", r"d/dy",
    r"\\frac\s*\{d\}",

    # ---------------------
    # TRIGONOMETRIC
    # ---------------------
    r"\bsin\b", r"\bcos\b", r"\btan\b",
    r"\bcot\b", r"\bsec\b", r"\bcsc\b",
    r"\barcsin\b", r"\barccos\b", r"\barctan\b",
    r"\bsinh\b", r"\bcosh\b", r"\btanh\b",

    # ---------------------
    # LOGARITHMIC / EXP
    # ---------------------
    r"\bln\b", r"\blog\b", r"\bexp\b",
    r"e\^", r"e\*\*",

    # ---------------------
    # ROOTS
    # ---------------------
    r"sqrt", r"√",

    # ---------------------
    # SERIES / SEQUENCES
    # ---------------------
    r"\\sum", r"∑",
    r"\\prod", r"∏",
    r"a_n", r"b_n",
    r"\bn\s*->\s*∞\b",

    # ---------------------
    # PROBABILITY BASICS
    # ---------------------
    r"\bP\s*\(", r"\bp\s*\(",
    r"\bprobability\b", r"\bverojatnost\b",
    r"\bnastan\b", r"\bslucajna\b",
    r"\buslovna\b", r"\bconditional\b",

    # ---------------------
    # PROBABILITY DISTRIBUTIONS
    # ---------------------
    r"\bpoisson\b", r"\bпуасон\b",
    r"\bbinom", r"\bбином",
    r"\bnormal\b", r"\bнормал",
    r"\bexponential\b", r"\bekspon",
    r"\bgeometric\b", r"\bгеометр",
    r"\buniform\b", r"\bрамномер",

    # ---------------------
    # STATISTICS
    # ---------------------
    r"\bmean\b", r"\bocekuvanje\b", r"\bexpected\b",
    r"\bvariance\b", r"\bvarijansa\b",
    r"\bstd\b", r"\bσ\b",
    r"\bchi\b", r"χ", r"x\^2",
    r"\bt-test\b", r"\bz-test\b",
    r"\bp-value\b",

    # ---------------------
    # DISCRETE / LOGIC
    # ---------------------
    r"∀", r"∃",
    r"¬", r"∧", r"∨", r"↔",
    r"\bfor\s+all\b", r"\bexists\b",
    r"\bpredikat\b", r"\bpredicate\b",
    r"\bindukcija\b", r"\binduction\b",

    # ---------------------
    # SET THEORY
    # ---------------------
    r"\bsubset\b", r"⊂", r"⊆",
    r"\bunion\b", r"∪",
    r"\bintersection\b", r"∩",
    r"∅",

    # ---------------------
    # LINEAR ALGEBRA (optional but useful)
    # ---------------------
    r"\bmatrix\b", r"\bdet\b",
    r"\bvector\b", r"\bvektor\b",
    r"\btranspose\b",
    r"\bspan\b",

    # ---------------------
    # GENERAL MATH STRUCTURE
    # ---------------------
    r"\^", r"/", r"=", r"\(", r"\)", r"\[", r"\]",
    r"[0-9]+",
    r"π", r"\\pi",
    r"λ", r"\\lambda",
    r"μ", r"\\mu",
    r"σ", r"\\sigma"
]
