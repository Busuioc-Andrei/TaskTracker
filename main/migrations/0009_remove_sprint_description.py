# Generated by Django 4.1 on 2023-06-03 16:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_remove_sprint_is_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sprint',
            name='description',
        ),
    ]