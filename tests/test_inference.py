from types import SimpleNamespace
from unittest.mock import Mock, patch
import numpy as np
import pytest
import sklearn
from mathapp_ml.inference import _load, predict


def artifact():
    model = Mock()
    model.classes_ = np.array(['CALCULUS', 'DISCRETE', 'PROBABILITY'])
    model.predict_proba.return_value = np.array([[0.85, 0.1, 0.05]])
    model.named_steps = {'features': Mock()}
    model.named_steps['features'].transform.return_value = SimpleNamespace(nnz=3)
    return {'pipeline': model, 'version': 'test', 'experimental': True, 'sklearn_version': sklearn.__version__}


def test_model_loaded_once_for_repeated_predictions():
    _load.cache_clear()
    with patch('joblib.load', return_value=artifact()) as loader:
        assert predict('Find the limit', '/trusted/model.joblib')['label'] == 'CALCULUS'
        predict('Find another limit', '/trusted/model.joblib')
        loader.assert_called_once()
    _load.cache_clear()


def test_close_scores_return_unknown():
    _load.cache_clear()
    model = artifact()
    model['pipeline'].predict_proba.return_value = np.array([[0.51, 0.45, 0.04]])
    with patch('joblib.load', return_value=model):
        result = predict('Ambiguous task', '/trusted/ambiguous.joblib')
    assert result['label'] == 'UNKNOWN' and result['suggested_label'] == 'CALCULUS'
    _load.cache_clear()


def test_version_mismatch_rejected():
    _load.cache_clear()
    model = artifact() | {'sklearn_version': '0.0.0'}
    with patch('joblib.load', return_value=model), pytest.raises(ValueError, match='version differs'):
        predict('Find x', '/trusted/incompatible.joblib')
    _load.cache_clear()


def test_experimental_model_blocked_in_production(settings):
    settings.ML_MODEL_PATH = '/trusted/model.joblib'
    settings.DEBUG = False
    from core.classification import classify_question
    with patch('core.classification.predict', return_value={'experimental': True}), pytest.raises(ValueError, match='Experimental'):
        classify_question('Find x')
