# Generated by Django 4.2.6 on 2023-11-10 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_casilleros", "0005_casillero_r_email_casillero_r_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="casillero",
            name="r_email",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="casillero",
            name="r_username",
            field=models.CharField(max_length=50, null=True),
        ),
    ]