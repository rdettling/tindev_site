# Generated by Django 4.1.2 on 2022-11-18 02:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cstart', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidate',
            name='last_login',
        ),
        migrations.AlterField(
            model_name='candidate',
            name='username',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]
