# Generated by Django 4.2.6 on 2023-12-17 21:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formations', '0007_chapitre_delete_cours_module_chapitres'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chapitre',
            old_name='documentation',
            new_name='fichier',
        ),
        migrations.RenameField(
            model_name='chapitre',
            old_name='titre',
            new_name='nom',
        ),
        migrations.RemoveField(
            model_name='module',
            name='chapitres',
        ),
        migrations.AddField(
            model_name='chapitre',
            name='module',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='chapitres', to='formations.module'),
            preserve_default=False,
        ),
    ]