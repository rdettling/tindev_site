# Generated by Django 4.1.2 on 2022-11-18 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rstart', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recruiter',
            name='last_login',
        ),
        migrations.AlterField(
            model_name='recruiter',
            name='username',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
