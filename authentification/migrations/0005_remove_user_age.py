# Generated by Django 4.2.6 on 2023-11-15 10:41

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("authentification", "0004_user_age"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="age",
        ),
    ]