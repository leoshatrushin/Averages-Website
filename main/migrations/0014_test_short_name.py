# Generated by Django 2.2.5 on 2019-09-17 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_test_has_happened'),
    ]

    operations = [
        migrations.AddField(
            model_name='test',
            name='short_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
