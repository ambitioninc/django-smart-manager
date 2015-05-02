# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import smart_manager.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CantCascadeModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='RelModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='UpsertModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('char_field', models.CharField(max_length=128)),
                ('int_field', models.IntegerField()),
            ],
            bases=(models.Model, smart_manager.models.SmartModelMixin),
        ),
        migrations.AddField(
            model_name='cantcascademodel',
            name='rel_model',
            field=models.ForeignKey(to='tests.RelModel', on_delete=django.db.models.deletion.PROTECT),
        ),
    ]
