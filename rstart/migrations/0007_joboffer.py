# Generated by Django 4.1.3 on 2022-12-05 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rstart', '0006_jobinteraction'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('candidate', models.IntegerField()),
                ('job', models.IntegerField()),
                ('accepted', models.BooleanField(default=False)),
            ],
        ),
    ]