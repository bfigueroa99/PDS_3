# Generated by Django 4.2.6 on 2023-11-26 19:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_casilleros', '0009_alter_casillero_fecha_creacion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casillero',
            name='fecha_creacion',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 26, 19, 58, 33, 749731)),
        ),
    ]