# Generated by Django 4.1 on 2023-04-04 17:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_column_options_alter_issue_options_issue_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='issue',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='main.issue'),
            preserve_default=False,
        ),
    ]
