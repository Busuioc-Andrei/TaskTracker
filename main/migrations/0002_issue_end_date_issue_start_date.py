# Generated by Django 4.1 on 2023-03-12 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='end_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='start_date',
            field=models.DateTimeField(null=True),
        ),
    ]