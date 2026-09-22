from unittest.mock import patch
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from solver.models import Conversation, Message, SolveHistory, SolveEvent, Classification
from core.errors import PipelineError

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    user = get_user_model().objects.create_user('tester')
    client = APIClient()
    client.force_authenticate(user)
    return client


def result(text):
    return {'problem_text': text, 'solution': 'The answer is 4.', 'domain': 'calculus',
        'classification': {'label': 'CALCULUS', 'scores': {'CALCULUS': 0.9},
                           'uncertain': False, 'model_version': 'test-v1'},
        'provider': 'openai', 'provider_model': 'gpt-5.6-terra',
        'usage': {'input_tokens': 12, 'output_tokens': 34, 'reasoning_tokens': 5}}


def test_solve_preserves_long_text_and_prediction(client):
    text = 'Evaluate the limit. ' * 60
    with patch('solver.views.solve_text', return_value=result(text)):
        response = client.post('/api/solver/solve/', {'content': text}, format='json')
    assert response.status_code == 200
    assert SolveHistory.objects.get().problem_text == text
    assert Message.objects.get(role='user').content == text
    assert Message.objects.count() == 2
    assert Classification.objects.get().model_version == 'test-v1'
    event = SolveEvent.objects.get(status='succeeded')
    assert (event.provider, event.model, event.input_tokens, event.output_tokens, event.reasoning_tokens) == (
        'openai', 'gpt-5.6-terra', 12, 34, 5)
    from datasets.models import TrainingExample
    assert not TrainingExample.objects.exists()


def test_failure_not_saved_as_solution(client):
    with patch('solver.views.solve_text', side_effect=PipelineError('provider_unavailable', 'Unavailable', 503)):
        response = client.post('/api/solver/solve/', {'content': 'Find x'}, format='json')
    assert response.status_code == 503
    assert not SolveHistory.objects.exists() and not Message.objects.exists()
    assert SolveEvent.objects.get().status == 'failed'


def test_foreign_conversation_blocked_before_provider_call(client):
    other = get_user_model().objects.create_user('other')
    convo = Conversation.objects.create(owner=other, title='Private')
    with patch('solver.views.solve_text') as solve:
        response = client.post('/api/solver/solve/', {'content': 'Find x', 'conversation_id': convo.pk}, format='json')
    assert response.status_code == 404
    solve.assert_not_called()
    assert client.get(f'/api/solver/conversations/{convo.pk}/messages/').status_code == 404


def test_invalid_file_is_rejected(client):
    response = client.post('/api/solver/solve/', {'content': 'not-base64!', 'input_type': 'image'}, format='json')
    assert response.status_code == 400
    assert not SolveHistory.objects.exists()


def test_non_string_content_is_rejected(client):
    response = client.post('/api/solver/solve/', {'content': {'nested': 'data'}}, format='json')
    assert response.status_code == 400


def test_classify_is_authenticated_and_local_only(client):
    assert APIClient().post('/api/solver/classify/', {'question': 'Find x'}).status_code == 401
    with patch('solver.views.classify_question', return_value=result('task')['classification']):
        response = client.post('/api/solver/classify/', {'question': 'Find x'})
    assert response.status_code == 200
    assert not SolveHistory.objects.exists()


def test_existing_conversation_appends_ordered_messages(client):
    with patch('solver.views.solve_text', return_value=result('Find the limit')):
        first = client.post('/api/solver/solve/', {'content': 'Find the limit'}, format='json')
        second = client.post('/api/solver/solve/', {'content': 'Find another limit',
            'conversation_id': first.data['conversation_id']}, format='json')
    assert second.status_code == 200
    assert Conversation.objects.count() == 1
    assert list(Message.objects.values_list('sequence', flat=True)) == [0, 1, 2, 3]


def test_original_message_and_extracted_task_are_separate(client):
    original = '  Evaluate lim x->2 x².  '
    with patch('solver.views.solve_text', return_value=result(original.strip())):
        response = client.post('/api/solver/solve/', {'content': original}, format='json')
    assert response.status_code == 200
    message = Message.objects.get(role='user')
    assert message.content == original
    assert message.problem.text == original.strip()
