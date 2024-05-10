import csv
import os

import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_project.settings')
if not settings.configured:
    django.setup()


def import_data(file_path, model):
    list = []
    with open(file_path, encoding='utf-8') as file:
        reader = csv.reader(file)
        for raw in reader:
            list.append(
                model(
                    name=raw[0],
                    measurement_unit=raw[1]
                )
            )
        model.objects.bulk_create(list)


def main():
    from recipes.models import Ingredient
    file_path = r'D:\Dev/foodgram/foodgram-project-react/data/ingredients.csv'
    import_data(file_path, Ingredient)


if __name__ == '__main__':
    main()
