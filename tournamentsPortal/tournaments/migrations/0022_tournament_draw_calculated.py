# Generated by Django 3.0.3 on 2020-05-09 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0021_auto_20200508_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='draw_calculated',
            field=models.BooleanField(default=False),
        ),
    ]
