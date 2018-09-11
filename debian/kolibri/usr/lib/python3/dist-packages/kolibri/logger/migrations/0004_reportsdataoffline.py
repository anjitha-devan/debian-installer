# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-03 10:09
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields
import kolibri.content.models
import kolibri.core.fields
import kolibri.utils.time


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('logger', '0003_auto_20170531_1140'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportsDataOffline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_id', kolibri.content.models.UUIDField(db_index=True)),
                ('student_id', kolibri.content.models.UUIDField(db_index=True)),
                ('number_of_attempt', models.IntegerField()),
                ('course_id', kolibri.content.models.UUIDField(db_index=True)),
                ('unit_id', kolibri.content.models.UUIDField(db_index=True)),
                ('lesson_id', kolibri.content.models.UUIDField(db_index=True)),
                ('collection_id', kolibri.content.models.UUIDField(db_index=True)),
                ('collection_type', models.CharField(blank=True, max_length=50, null=True)),
                ('content_id', kolibri.content.models.UUIDField(db_index=True)),
                ('content_type', models.CharField(blank=True, max_length=50, null=True)),
                ('time_spent', models.FloatField(default=0.0, help_text='(in seconds)', validators=[django.core.validators.MinValueValidator(0)])),
                ('reaction', models.IntegerField()),
                ('student_response', jsonfield.fields.JSONField(blank=True, default=[])),
                ('score', models.BooleanField(default=False)),
                ('created_date', kolibri.core.fields.DateTimeTzField(default=kolibri.utils.time.local_now, editable=False)),
                ('modified_date', kolibri.core.fields.DateTimeTzField(default=kolibri.utils.time.local_now, editable=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_user', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]