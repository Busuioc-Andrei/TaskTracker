# Generated by Django 4.1 on 2023-06-03 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_alter_sprint_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprint',
            name='project',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='main.project'),
        ),
    ]
