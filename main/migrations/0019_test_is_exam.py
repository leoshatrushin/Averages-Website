# Generated by Django 2.2.5 on 2019-11-12 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20191112_2109'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='is_exam',
            field=models.BooleanField(null=True),
        ),
    ]