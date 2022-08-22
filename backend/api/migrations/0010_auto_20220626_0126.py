import json
import os

from django.db import migrations, transaction
from django.db.utils import IntegrityError

from api.models import Ingredient


def load_ingridients(self, *args, **options):
    DATA_FILE = os.path.join("data", "data.json")

    f = open(DATA_FILE, "r", encoding="utf-8")
    data = json.load(f)
    for ingredient in data:
        try:
            with transaction.atomic():
                Ingredient.objects.create(
                    name=ingredient["name"],
                    measurement_unit=ingredient["measurement_unit"],
                )
        except IntegrityError:
            print('double')


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20220625_2214'),
    ]
    operations = [migrations.RunPython(load_ingridients)]
