# Generated by Django 3.0.3 on 2020-05-05 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0004_auto_20200505_0954'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='localization',
            field=models.CharField(default='', max_length=128),
        ),
    ]
