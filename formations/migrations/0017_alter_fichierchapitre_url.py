# Generated by Django 4.2.6 on 2023-12-25 19:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("formations", "0016_remove_chapitre_fichier_fichierchapitre"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fichierchapitre",
            name="url",
            field=models.FileField(upload_to="chapitres/"),
        ),
    ]