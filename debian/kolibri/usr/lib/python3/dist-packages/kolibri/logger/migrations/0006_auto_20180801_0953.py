# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-01 04:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logger', '0005_reportsdataoffline_attended'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportsdataoffline',
            name='reaction',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]