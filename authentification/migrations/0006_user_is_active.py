# Generated by Django 4.2.6 on 2023-12-12 13:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentification", "0005_remove_user_age"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(default=False),
        ),
    ]