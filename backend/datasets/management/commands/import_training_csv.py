import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from mathapp_ml.data import load_csv, question_hash
from datasets.models import DatasetImport, TrainingExample


class Command(BaseCommand):
    help = 'Validate and atomically import CSV examples; never overwrite reviewed data.'

    def add_arguments(self, parser):
        parser.add_argument('csv')
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        try:
            rows, audit = load_csv(options['csv'])
        except (ValueError, OSError, csv.Error) as exc:
            raise CommandError(str(exc)) from exc
        if DatasetImport.objects.filter(sha256=audit['sha256']).exists():
            self.stdout.write('Already imported this exact file; no changes.')
            return
        ids = [r['id'] for r in rows]
        hashes = [question_hash(r['question']) for r in rows]
        if TrainingExample.objects.filter(external_id__in=ids).exists() or TrainingExample.objects.filter(content_hash__in=hashes).exists():
            raise CommandError('IDs or normalized questions conflict with existing examples; no changes made.')
        if options['dry_run']:
            self.stdout.write(f"Validated {len(rows)} rows; no changes made.")
            return
        try:
            with transaction.atomic():
                dataset = DatasetImport.objects.create(filename=Path(options['csv']).name,
                    sha256=audit['sha256'], row_count=len(rows))
                # A CSV cannot assert an authenticated review. Import all rows as
                # pending, regardless of the source's claimed review status.
                TrainingExample.objects.bulk_create([
                    TrainingExample(dataset=dataset, external_id=r['id'], question=r['question'],
                        content_hash=question_hash(r['question']), label=r['label'], subtopic=r['subtopic'],
                        language=r['language'], source=r['source'], group_id=r['group_id'], review_status='pending')
                    for r in rows
                ])
        except IntegrityError as exc:
            raise CommandError('Import conflicts with existing data; transaction rolled back.') from exc
        self.stdout.write(self.style.SUCCESS(f'Imported {len(rows)} examples as pending; original CSV unchanged.'))
