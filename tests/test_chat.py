import gzip
import json
from datetime import timedelta
from unittest.mock import patch, MagicMock
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from core.context import build_context
from core.mathsolver import solve_math
from core.errors import PipelineError
from solver.models import Conversation, Message, Problem, SolveEvent
from test_api import result

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_throttles():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def client():
    user = get_user_model().objects.create_user('chat-owner')
    client = APIClient()
    client.force_authenticate(user)
    return client


def reply():
    return {**result('Evaluate lim x->infinity 1/x'), 'memory': 'The limit of 1/x at infinity is 0.',
            'openai_subject': 'CALCULUS', 'final_answer': '0'}


def test_followup_receives_history_and_resumes_after_reload(client):
    with patch('solver.views.solve_text', return_value=reply()) as provider:
        first = client.post('/api/solver/solve/', {'content': 'Evaluate lim x->infinity 1/x'})
        second = client.post('/api/solver/solve/', {
            'content': 'Why is that the solution?', 'conversation_id': first.data['conversation_id']})
    assert second.status_code == 200
    assert provider.call_args.kwargs['history'] == [
        {'role': 'user', 'content': 'Evaluate lim x->infinity 1/x'},
        {'role': 'assistant', 'content': 'The answer is 4.'},
    ]
    response = client.get(f"/api/solver/conversations/{first.data['conversation_id']}/messages/")
    assert [m['sequence'] for m in response.data['results']] == [3, 2, 1, 0]
    assert response.data['results'][0]['analysis']['openai_subject'] == 'CALCULUS'
    assert 'memory' not in response.data['results'][0]
    assert Message.objects.filter(role='assistant').last().memory


def test_compact_context_is_bounded_and_keeps_originals(client):
    owner = get_user_model().objects.get(username='chat-owner')
    conversation = Conversation.objects.create(owner=owner, title='Limits')
    for i in range(20):
        Message.objects.create(conversation=conversation, sequence=i, role='user' if i % 2 == 0 else 'assistant',
                               content=('x² + X = 3. ' * 70), memory='Exact equation: x² + X = 3.' if i % 2 else '')
    with override_settings(CHAT_HISTORY_CHAR_LIMIT=2000):
        history, info = build_context(conversation)
    assert info['mode'] == 'compact'
    assert info['history_characters'] <= 2000
    assert 'x² + X' in history[0]['content']
    assert Message.objects.count() == 20
    assert Message.objects.get(sequence=0).content == 'x² + X = 3. ' * 70


def test_old_long_chat_without_memory_fails_before_api(client):
    owner = get_user_model().objects.get(username='chat-owner')
    convo = Conversation.objects.create(owner=owner, title='Old')
    for i in range(10):
        Message.objects.create(conversation=convo, sequence=i, role='user' if i % 2 == 0 else 'assistant', content='x = 2')
    with patch('solver.views.solve_text') as provider:
        response = client.post('/api/solver/solve/', {'content': 'Why?', 'conversation_id': convo.pk})
    assert response.status_code == 409
    provider.assert_not_called()


def test_parallel_submission_is_blocked_before_spending(client):
    convo = Conversation.objects.create(owner=get_user_model().objects.get(username='chat-owner'), title='Busy',
                                       busy_until=timezone.now() + timedelta(minutes=2))
    with patch('solver.views.solve_text') as provider:
        response = client.post('/api/solver/solve/', {'content': 'Why?', 'conversation_id': convo.pk})
    assert response.status_code == 409
    provider.assert_not_called()


def test_lease_released_when_provider_fails(client):
    convo = Conversation.objects.create(owner=get_user_model().objects.get(username='chat-owner'), title='Retry')
    with patch('solver.views.solve_text', side_effect=PipelineError('incomplete_solution', 'Incomplete', 502,
                                                                   {'input_tokens': 42, 'output_tokens': 80})):
        response = client.post('/api/solver/solve/', {'content': 'x?', 'conversation_id': convo.pk})
    assert response.status_code == 502
    convo.refresh_from_db()
    assert convo.busy_until is None
    assert SolveEvent.objects.get().output_tokens == 80
    assert not Message.objects.exists()


def test_reference_requires_staff_and_ownership(client):
    with patch('solver.views.solve_text', return_value=reply()):
        first = client.post('/api/solver/solve/', {'content': 'Find the limit'})
    problem = Problem.objects.get()
    url = f'/api/solver/problems/{problem.pk}/reference/'
    assert client.patch(url, {'answer': '0', 'label': 'CALCULUS'}).status_code == 403
    user = get_user_model().objects.get(username='chat-owner')
    user.is_staff = True
    user.save()
    client.force_authenticate(user)
    assert client.patch(url, {'answer': '0', 'label': 'CALCULUS'}).status_code == 200
    response = client.get(f"/api/solver/conversations/{first.data['conversation_id']}/messages/")
    assert response.data['results'][0]['analysis']['reference']['answer'] == '0'
    other = get_user_model().objects.create_user('foreign-admin', is_staff=True)
    client.force_authenticate(other)
    assert client.patch(url, {'answer': '1', 'label': 'DISCRETE'}).status_code == 404


def test_lossless_gzip_export_and_ownership(client):
    with patch('solver.views.solve_text', return_value=reply()):
        response = client.post('/api/solver/solve/', {'content': 'x² + X = 3'})
    pk = response.data['conversation_id']
    exported = client.get(f'/api/solver/conversations/{pk}/export/')
    data = json.loads(gzip.decompress(b''.join(exported.streaming_content)))
    assert data['messages'][0]['content'] == 'x² + X = 3'
    other = get_user_model().objects.create_user('foreign-reader')
    client.force_authenticate(other)
    assert client.get(f'/api/solver/conversations/{pk}/export/').status_code == 404


def test_attachment_is_extracted_once_then_followup_uses_text(client):
    upload = SimpleUploadedFile('question.pdf', b'%PDF-fake-for-mocked-extractor', content_type='application/pdf')
    with patch('solver.views.solve_pdf_bytes', return_value=reply()) as extract:
        first = client.post('/api/solver/solve/', {'file': upload, 'input_type': 'pdf', 'content': 'Explain this'})
    assert first.status_code == 200
    assert extract.call_args.kwargs['caption'] == 'Explain this'
    with patch('solver.views.solve_pdf_bytes') as extract, patch('solver.views.solve_text', return_value=reply()) as provider:
        second = client.post('/api/solver/solve/', {'content': 'Why?', 'conversation_id': first.data['conversation_id']})
    assert second.status_code == 200
    extract.assert_not_called()
    assert provider.call_args.kwargs['history'][0]['content'] == 'Evaluate lim x->infinity 1/x'


def test_incomplete_and_malformed_provider_results_are_not_saved(monkeypatch):
    client = MagicMock()
    client.responses.create.return_value = SimpleNamespace(status='incomplete', usage=None)
    monkeypatch.setattr('core.mathsolver._client', client)
    with pytest.raises(PipelineError) as failure:
        solve_math('x = 2')
    assert failure.value.code == 'incomplete_solution'
    client.responses.create.return_value = SimpleNamespace(status='completed', usage=None, output_text='not json')
    with pytest.raises(PipelineError) as failure:
        solve_math('x = 2')
    assert failure.value.code == 'invalid_solution'
