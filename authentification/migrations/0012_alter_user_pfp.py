# Generated by Django 4.2.6 on 2023-12-25 19:52

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("authentification", "0011_alter_user_pfp"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="pfp",
            field=models.FileField(default=None, null=True, upload_to="pfps/"),
        ),
    ]
