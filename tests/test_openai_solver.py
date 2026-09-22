from types import SimpleNamespace
from unittest.mock import MagicMock
import json

import pytest
from django.test import override_settings

from core.errors import PipelineError
from core import mathsolver


def test_solver_uses_responses_api_without_provider_state(monkeypatch):
    response = SimpleNamespace(
        status='completed',
        model='gpt-5.6-terra',
        output_text=json.dumps({'is_math': True, 'answer': '\\(x = 2\\)', 'subject': 'OTHER',
                                'final_answer': 'x = 2', 'memory': 'We solved x + 1 = 3; x = 2.'}),
        usage=SimpleNamespace(
            input_tokens=11,
            output_tokens=23,
            output_tokens_details=SimpleNamespace(reasoning_tokens=7),
        ),
    )
    client = MagicMock()
    client.responses.create.return_value = response
    monkeypatch.setattr(mathsolver, '_client', client)

    with override_settings(OPENAI_API_KEY='test-key', OPENAI_MODEL='gpt-5.6-terra'):
        result = mathsolver.solve_math('Solve x + 1 = 3')

    assert result.text == '\\(x = 2\\)'
    assert result.usage == {'input_tokens': 11, 'output_tokens': 23, 'reasoning_tokens': 7}
    call = client.responses.create.call_args.kwargs
    assert call['model'] == 'gpt-5.6-terra'
    assert call['store'] is False
    assert call['input'][1]['content'] == 'Solve x + 1 = 3'


def test_solver_requires_server_side_key(monkeypatch):
    monkeypatch.setattr(mathsolver, '_client', None)
    with override_settings(OPENAI_API_KEY=''):
        with pytest.raises(PipelineError, match='not configured') as exc_info:
            mathsolver.solve_math('Solve x + 1 = 3')
    assert exc_info.value.code == 'provider_not_configured'
