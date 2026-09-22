import re


def clean_mathsolver_output(raw: str) -> str:
    """
    Го средува текстот вратен од solve_math_with_deepseek:
    - трга вишок празни линии
    - едноставен markdown bold (**text**) -> <strong>text</strong>
    - подготвува текст за HTML (ќе го прикажеме со |safe)
    """
    if not raw:
        return ""

    text = raw.strip()

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Скратување на повеќе празни линии (3+ во 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Markdown bold: **текст** -> <strong>текст</strong>
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    # (опционално) ако сакаш да ги тргнеш празните LaTeX редови \[ и \]
    # но јас би ги оставил, сакајќи подоцна MathJax да ги рендерира
    # text = text.replace("\\[", "").replace("\\]", "")

    return text
