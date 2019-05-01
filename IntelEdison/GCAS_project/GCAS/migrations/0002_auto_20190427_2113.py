# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-27 21:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('GCAS', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GCAS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('temperature', models.FloatField(blank=True, default=None, null=True)),
                ('prediction', models.IntegerField(blank=True, default=None, null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Temperature',
        ),
    ]