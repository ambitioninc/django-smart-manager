# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ModelTemplate'
        db.create_table(u'model_template_modeltemplate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_template_class', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('manages_deletions', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('template', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal(u'model_template', ['ModelTemplate'])

        # Adding model 'ModelTemplateObject'
        db.create_table(u'model_template_modeltemplateobject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('model_template', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['model_template.ModelTemplate'])),
            ('model_obj_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('model_obj_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'model_template', ['ModelTemplateObject'])

        # Adding unique constraint on 'ModelTemplateObject', fields ['model_template', 'model_obj_type', 'model_obj_id']
        db.create_unique(u'model_template_modeltemplateobject', ['model_template_id', 'model_obj_type_id', 'model_obj_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ModelTemplateObject', fields ['model_template', 'model_obj_type', 'model_obj_id']
        db.delete_unique(u'model_template_modeltemplateobject', ['model_template_id', 'model_obj_type_id', 'model_obj_id'])

        # Deleting model 'ModelTemplate'
        db.delete_table(u'model_template_modeltemplate')

        # Deleting model 'ModelTemplateObject'
        db.delete_table(u'model_template_modeltemplateobject')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'model_template.modeltemplate': {
            'Meta': {'object_name': 'ModelTemplate'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manages_deletions': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'model_template_class': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'template': ('jsonfield.fields.JSONField', [], {})
        },
        u'model_template.modeltemplateobject': {
            'Meta': {'unique_together': "(('model_template', 'model_obj_type', 'model_obj_id'),)", 'object_name': 'ModelTemplateObject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_obj_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'model_obj_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'model_template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['model_template.ModelTemplate']"})
        }
    }

    complete_apps = ['model_template']