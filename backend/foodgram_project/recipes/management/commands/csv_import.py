import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиентов из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help="file path")

    def handle(self, *args, **options):
        file_path = options['path']
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                name = row[0]
                measurement_unit = row[1]
                Ingredient.objects.create(name=name,
                                          measurement_unit=measurement_unit)
        self.stdout.write('Ингредиенты загружены!')
