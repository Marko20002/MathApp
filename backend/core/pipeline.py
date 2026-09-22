"""Extract a task, classify it, then solve it. Heavy OCR imports are lazy."""
from .classification import classify_question
from .errors import PipelineError


def _solve(text, history=None):
    text = text.strip()
    if not text:
        raise PipelineError('empty_extraction', 'No problem text could be extracted.')
    if len(text) > 20000:
        raise PipelineError('problem_too_long', 'Use a problem of at most 20000 characters.', 400)
    classification = classify_question(text)
    from .mathsolver import solve_math
    provider_solution = solve_math(text, history=history)
    if provider_solution.text == '[NOT_MATH]':
        raise PipelineError('not_math', 'Please enter a math problem.', 400)
    return {'problem_text': text, 'solution': provider_solution.text,
            'domain': classification['label'].lower(), 'classification': classification,
            'provider': provider_solution.provider, 'provider_model': provider_solution.model,
            'usage': provider_solution.usage, 'openai_subject': provider_solution.subject,
            'final_answer': provider_solution.final_answer, 'memory': provider_solution.memory}


def solve_text(text, history=None):
    return _solve(text, history)


def solve_image_bytes(image_bytes, ocr_engine='2', history=None, caption=''):
    import cv2
    import numpy as np
    from .ocr.easyocr_engine import run_easyocr
    frame = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise PipelineError('invalid_image', 'Could not decode the image.', 400)
    if frame.shape[0] * frame.shape[1] > 20000000:
        raise PipelineError('image_too_large', 'Use an image below 20 megapixels.', 400)
    return _solve('\n\n'.join(filter(None, [caption, run_easyocr(frame)])), history)


def solve_pdf_bytes(pdf_bytes, history=None, caption=''):
    from .ocr.pdf import extract_pdf_text
    return _solve('\n\n'.join(filter(None, [caption, extract_pdf_text(pdf_bytes)])), history)
