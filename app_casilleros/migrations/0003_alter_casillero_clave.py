# Generated by Django 4.2.6 on 2023-10-29 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_casilleros", "0002_casillero_clave"),
    ]

    operations = [
        migrations.AlterField(
            model_name="casillero",
            name="clave",
            field=models.IntegerField(default=1234),
        ),
    ]
