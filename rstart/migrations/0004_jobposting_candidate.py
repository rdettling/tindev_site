# Generated by Django 4.1.3 on 2022-12-02 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rstart', '0003_jobposting'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobposting',
            name='candidate',
            field=models.CharField(max_length=200, null=True),
        ),
    ]