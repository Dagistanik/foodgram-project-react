# Generated by Django 3.0.5 on 2022-06-30 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_auto_20220626_0126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(choices=[('#0000FF', 'Синий'), ('#FFA500', 'Оранжевый'), ('#008000', 'Зеленый'), ('#800080', 'Фиолетовый'), ('#FFFF00', 'Желтый')], max_length=7, unique=True, verbose_name='Цвет в HEX'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, unique=True, verbose_name='Название тега'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(max_length=200, unique=True, verbose_name='Уникальный слаг'),
        ),
    ]
