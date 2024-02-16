# Generated by Django 4.2.6 on 2024-01-13 11:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("formations", "0017_alter_fichierchapitre_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="module",
            name="responsable",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]