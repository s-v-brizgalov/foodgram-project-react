import csv
from product.models import Ingredients


def run():
    with open('scripts/ingredients.csv', encoding='Utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            Ingredients(name=row[0], measurement_unit=row[1]).save()
