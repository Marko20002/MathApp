import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from mathapp_ml.data import COLUMNS
from datasets.models import TrainingExample


class Command(BaseCommand):
    help = 'Export reviewed examples for offline training. Never exports chats.'

    def add_arguments(self, parser):
        parser.add_argument('output')

    def handle(self, *args, **options):
        rows = TrainingExample.objects.filter(review_status='approved').order_by('external_id')
        if not rows.exists():
            raise CommandError('No approved examples. Review examples in the admin panel first.')
        path = Path(options['output'])
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with path.open('x', encoding='utf-8', newline='') as out:
                writer = csv.DictWriter(out, fieldnames=COLUMNS)
                writer.writeheader()
                for row in rows.iterator():
                    writer.writerow({k: row.external_id if k == 'id' else getattr(row, k) for k in COLUMNS})
        except FileExistsError as exc:
            raise CommandError('Output exists; choose a new snapshot filename.') from exc
        self.stdout.write(f'Exported {rows.count()} approved examples.')
