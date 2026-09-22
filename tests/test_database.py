import io
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.utils import timezone
from datasets.models import DatasetImport, TrainingExample
from solver.models import Conversation, Message
from test_data import example, write_csv

pytestmark = pytest.mark.django_db


def test_import_is_idempotent_and_never_self_approves(tmp_path):
    path = write_csv(tmp_path / 'data.csv', [example(review_status='approved')])
    call_command('import_training_csv', str(path), stdout=io.StringIO())
    row = TrainingExample.objects.get()
    assert row.review_status == 'pending'
    assert row.reviewed_by is None
    call_command('import_training_csv', str(path), stdout=io.StringIO())
    assert TrainingExample.objects.count() == 1
    assert DatasetImport.objects.count() == 1


def test_conflicting_import_leaves_no_partial_records(tmp_path):
    first = write_csv(tmp_path / 'first.csv', [example()])
    call_command('import_training_csv', str(first), stdout=io.StringIO())
    second = write_csv(tmp_path / 'second.csv', [example(question='Changed question'),
        example('new', question='A different question')])
    with pytest.raises(CommandError, match='conflict'):
        call_command('import_training_csv', str(second))
    assert DatasetImport.objects.count() == TrainingExample.objects.count() == 1


def test_dry_run_does_not_write(tmp_path):
    path = write_csv(tmp_path / 'data.csv', [example()])
    call_command('import_training_csv', str(path), dry_run=True, stdout=io.StringIO())
    assert not TrainingExample.objects.exists()


def test_database_enforces_labels_and_review_attribution(tmp_path):
    path = write_csv(tmp_path / 'data.csv', [example()])
    call_command('import_training_csv', str(path), stdout=io.StringIO())
    for fields in [{'label': 'INVALID'}, {'review_status': 'approved'}, {'question': '   '}]:
        with pytest.raises(IntegrityError), transaction.atomic():
            TrainingExample.objects.update(**fields)


def test_export_contains_only_approved_examples(tmp_path):
    path = write_csv(tmp_path / 'data.csv', [example(), example('second', question='Evaluate an integral')])
    call_command('import_training_csv', str(path), stdout=io.StringIO())
    reviewer = get_user_model().objects.create_user('reviewer')
    TrainingExample.objects.filter(external_id='calc_1').update(
        review_status='approved', reviewed_by=reviewer, reviewed_at=timezone.now())
    output = tmp_path / 'approved.csv'
    call_command('export_training_csv', str(output), stdout=io.StringIO())
    from mathapp_ml.data import load_csv
    records, _ = load_csv(output)
    assert len(records) == 1 and records[0]['id'] == 'calc_1'


def test_message_sequence_unique():
    user = get_user_model().objects.create_user('user')
    convo = Conversation.objects.create(owner=user, title='Test')
    Message.objects.create(conversation=convo, sequence=0, role='user', content='Hello')
    with pytest.raises(IntegrityError), transaction.atomic():
        Message.objects.create(conversation=convo, sequence=0, role='assistant', content='Reply')


def test_admin_review_attributes_reviewer(tmp_path):
    from django.contrib.admin.sites import AdminSite
    from django.test import RequestFactory
    from datasets.admin import TrainingExampleAdmin
    path = write_csv(tmp_path / 'data.csv', [example()])
    call_command('import_training_csv', str(path), stdout=io.StringIO())
    row = TrainingExample.objects.get()
    request = RequestFactory().get('/')
    request.user = get_user_model().objects.create_user('admin', is_staff=True, is_superuser=True)
    admin = TrainingExampleAdmin(TrainingExample, AdminSite())
    form_class = admin.get_form(request, row)
    form = form_class(data={'question': row.question, 'label': row.label, 'subtopic': row.subtopic,
        'language': row.language, 'source': row.source, 'group_id': row.group_id,
        'review_status': 'approved'}, instance=row)
    assert form.is_valid(), form.errors
    admin.save_model(request, form.save(commit=False), form, True)
    row.refresh_from_db()
    assert row.reviewed_by == request.user and row.reviewed_at is not None
