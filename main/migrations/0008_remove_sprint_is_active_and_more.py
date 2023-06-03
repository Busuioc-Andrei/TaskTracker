# Generated by Django 4.1 on 2023-06-03 13:56

from django.db import migrations, models
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_project_current_sprint_sprint_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sprint',
            name='is_active',
        ),
        migrations.AlterField(
            model_name='sprint',
            name='estimated_end_date',
            field=models.DateTimeField(default=main.models.get_default_estimated_end_date),
        ),
    ]