# Generated by Django 4.2.6 on 2023-12-17 16:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("candidature", "0002_candidature_date_envoi_fichierutilisateur"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="candidature",
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name="candidature",
            constraint=models.UniqueConstraint(
                fields=("idcandidat", "idformation"),
                name="unique_migration_host_combination",
            ),
        ),
    ]
