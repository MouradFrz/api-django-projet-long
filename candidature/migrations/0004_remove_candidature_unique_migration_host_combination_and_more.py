# Generated by Django 4.2.6 on 2023-12-17 16:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("candidature", "0003_alter_candidature_unique_together_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="candidature",
            name="unique_migration_host_combination",
        ),
        migrations.AddConstraint(
            model_name="candidature",
            constraint=models.UniqueConstraint(
                fields=("idcandidat", "idformation"), name="unique_candidat_formation"
            ),
        ),
    ]
