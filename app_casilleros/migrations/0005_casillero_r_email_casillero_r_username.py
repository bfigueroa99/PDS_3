# Generated by Django 4.2.6 on 2023-11-09 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_casilleros", "0004_casillero_abierto_alter_casillero_disponible"),
    ]

    operations = [
        migrations.AddField(
            model_name="casillero",
            name="r_email",
            field=models.CharField(default="@gmail.com", max_length=50),
        ),
        migrations.AddField(
            model_name="casillero",
            name="r_username",
            field=models.CharField(default="", max_length=50),
        ),
    ]
