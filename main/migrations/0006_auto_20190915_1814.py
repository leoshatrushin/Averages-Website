# Generated by Django 2.2.5 on 2019-09-15 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_test_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='order',
            field=models.IntegerField(),
        ),
    ]
