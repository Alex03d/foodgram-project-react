import csv
import os

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredients


class Command(BaseCommand):
    help = 'Загрузка из csv файла'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv', nargs='?',
                            type=str)

    def handle(self, *args, **options):

        with open(os.path.join(
                settings.BASE_DIR,
                'data',
                options['filename']),
                'r',
                encoding='utf-8') as f:
            data = csv.reader(f)
            for row in data:
                name, measurement_unit = row
                Ingredients.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )

        self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
