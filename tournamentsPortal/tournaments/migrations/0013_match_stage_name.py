# Generated by Django 3.0.3 on 2020-05-06 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0012_match_finished'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='stage_name',
            field=models.CharField(default='1st round', max_length=64),
        ),
    ]