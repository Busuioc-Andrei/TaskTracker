# Generated by Django 4.1 on 2023-06-04 00:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_remove_sprint_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='done',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
