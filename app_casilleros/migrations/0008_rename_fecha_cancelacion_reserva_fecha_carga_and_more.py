# Generated by Django 4.2.6 on 2023-11-24 19:01

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app_casilleros", "0007_casillero_o_email_casillero_o_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="reserva",
            old_name="fecha_cancelacion",
            new_name="fecha_carga",
        ),
        migrations.RenameField(
            model_name="reserva",
            old_name="fecha_confirmacion",
            new_name="fecha_retiro",
        ),
        migrations.RemoveField(
            model_name="reserva",
            name="cancelada",
        ),
        migrations.RemoveField(
            model_name="reserva",
            name="confirmada",
        ),
        migrations.AddField(
            model_name="casillero",
            name="fecha_creacion",
            field=models.DateTimeField(default=datetime.datetime.today),
        ),
        migrations.AlterField(
            model_name="reserva",
            name="fecha_reserva",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="Historial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("porcentaje_uso", models.FloatField(default=0)),
                (
                    "reserva",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="app_casilleros.reserva",
                    ),
                ),
            ],
        ),
    ]
