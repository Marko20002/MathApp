import os
import re
from openai import OpenAI

MATH_KEYWORDS = re.compile(
    r'\b(integr|deriv|limit|lim|differenti|equation|solve|calculat|factor|expand|simplif|'
    r'matrix|determin|eigenvalue|vector|proof|theorem|modulo|combinat|permut|probabilit|'
    r'statistic|variance|expect|distribut|logarithm|exponent|trigonometr|sin|cos|tan|'
    r'polynomial|quadratic|linear|algebr|geometr|area|volume|perimeter|prime|divisib|'
    r'sequence|series|converge|diverge|binomial|set|function|graph|slope|intercept|'
    r'fraction|decimal|percent|ratio|proportion|inequality|absolute|radical|sqrt|'
    r'\d|\+|\-|\*|\/|\^|=|\\frac|\\int|\\sum|\\prod|\\lim|\\infty|dx|dy)\b',
    re.IGNORECASE,
)

SYSTEM_PROMPT = (
    'You are a strict math tutor. You ONLY answer mathematics questions: '
    'algebra, calculus, geometry, statistics, probability, discrete math, linear algebra, etc. '
    'If the input is not a math problem, respond with exactly: '
    '"[NOT_MATH]" and nothing else. '
    'For math problems, solve step by step using LaTeX for all expressions '
    '(inline: \\(...\\), block: \\[...\\]). Clearly mark the final answer.'
)

# Cached once per worker process — avoids rebuilding the HTTP connection pool on every request
_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        if not api_key:
            return None
        _client = OpenAI(api_key=api_key, base_url='https://api.deepseek.com')
    return _client


def solve_math(problem_text: str) -> str:
    if not MATH_KEYWORDS.search(problem_text):
        return '[NOT_MATH]'

    client = _get_client()
    if client is None:
        return '[DeepSeek API key not configured. Add DEEPSEEK_API_KEY to your .env file.]'

    try:
        response = client.chat.completions.create(
            model='deepseek-reasoner',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user',   'content': problem_text},
            ],
            temperature=0.2,
        )
        result = response.choices[0].message.content
        if result.strip().startswith('[NOT_MATH]'):
            return '[NOT_MATH]'
        return result
    except Exception as e:
        return f'[Error contacting DeepSeek: {e}]'
