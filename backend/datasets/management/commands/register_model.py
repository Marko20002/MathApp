import hashlib
import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from datasets.models import ModelVersion


class Command(BaseCommand):
    help = 'Record candidate model provenance, without activating it.'

    def add_arguments(self, parser):
        parser.add_argument('directory')

    def handle(self, *args, **options):
        directory = Path(options['directory']).resolve()
        try:
            report = json.loads((directory / 'report.json').read_text())
            path = directory / 'classifier.joblib'
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != report['artifact_sha256']:
                raise CommandError('Artifact checksum differs from training report')
            obj, created = ModelVersion.objects.get_or_create(version=report['version'], defaults={
                'artifact_path': str(path), 'artifact_sha256': digest,
                'dataset_sha256': report['dataset']['sha256'], 'metrics': report,
                'experimental': report['experimental']})
            if obj.artifact_sha256 != digest:
                raise CommandError('This version already identifies a different artifact')
        except (OSError, ValueError, KeyError) as exc:
            raise CommandError('Missing or invalid model report/artifact') from exc
        self.stdout.write('Candidate registered; activation requires ML_MODEL_PATH configuration.' if created else 'Already registered.')
