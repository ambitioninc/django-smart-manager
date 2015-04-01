# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SmartManager',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(unique=True, null=True, max_length=128, default=None)),
                ('smart_manager_class', models.CharField(max_length=128)),
                ('manages_deletions', models.BooleanField(default=True)),
                ('primary_obj_id', models.PositiveIntegerField(default=0)),
                ('template', jsonfield.fields.JSONField()),
                ('primary_obj_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SmartManagerObject',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('model_obj_id', models.PositiveIntegerField()),
                ('model_obj_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('smart_manager', models.ForeignKey(to='smart_manager.SmartManager')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='smartmanagerobject',
            unique_together=set([('model_obj_type', 'model_obj_id')]),
        ),
    ]
