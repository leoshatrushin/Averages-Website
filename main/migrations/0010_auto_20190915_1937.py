# Generated by Django 2.2.5 on 2019-09-15 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_remove_mark_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mark',
            name='value',
            field=models.DecimalField(decimal_places=1, max_digits=4),
        ),
    ]
