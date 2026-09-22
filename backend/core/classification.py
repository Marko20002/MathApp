import logging
from pathlib import Path
from django.conf import settings
from mathapp_ml.inference import predict

logger = logging.getLogger(__name__)


def classify_question(text):
    if not settings.ML_MODEL_PATH:
        return {'label': 'UNKNOWN', 'suggested_label': None, 'scores': {}, 'confidence': None,
                'uncertain': True, 'model_version': 'unconfigured', 'experimental': True}
    path = Path(settings.ML_MODEL_PATH)
    if not path.is_absolute():
        path = settings.PROJECT_ROOT / path
    result = predict(text, path, settings.ML_CONFIDENCE_THRESHOLD, settings.ML_CONFIDENCE_MARGIN)
    if result['experimental'] and not settings.DEBUG:
        raise ValueError('Experimental classifier cannot be used with DEBUG=False')
    return result
