# Generated by Django 4.1 on 2023-03-31 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_column_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='column',
            options={'ordering': ['order']},
        ),
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='issue',
            name='order',
            field=models.IntegerField(editable=False, null=True),
        ),
    ]