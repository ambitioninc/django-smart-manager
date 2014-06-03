# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SmartManager'
        db.create_table(u'smart_manager_smartmanager', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('smart_manager_class', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('manages_deletions', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('template', self.gf('jsonfield.fields.JSONField')()),
        ))
        db.send_create_signal(u'smart_manager', ['SmartManager'])

        # Adding model 'SmartManagerObject'
        db.create_table(u'smart_manager_smartmanagerobject', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('smart_manager', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['smart_manager.SmartManager'])),
            ('model_obj_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('model_obj_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'smart_manager', ['SmartManagerObject'])

        # Adding unique constraint on 'SmartManagerObject', fields ['smart_manager', 'model_obj_type', 'model_obj_id']
        db.create_unique(u'smart_manager_smartmanagerobject', ['smart_manager_id', 'model_obj_type_id', 'model_obj_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SmartManagerObject', fields ['smart_manager', 'model_obj_type', 'model_obj_id']
        db.delete_unique(u'smart_manager_smartmanagerobject', ['smart_manager_id', 'model_obj_type_id', 'model_obj_id'])

        # Deleting model 'SmartManager'
        db.delete_table(u'smart_manager_smartmanager')

        # Deleting model 'SmartManagerObject'
        db.delete_table(u'smart_manager_smartmanagerobject')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'smart_manager.smartmanager': {
            'Meta': {'object_name': 'SmartManager'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manages_deletions': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'smart_manager_class': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'template': ('jsonfield.fields.JSONField', [], {})
        },
        u'smart_manager.smartmanagerobject': {
            'Meta': {'unique_together': "(('smart_manager', 'model_obj_type', 'model_obj_id'),)", 'object_name': 'SmartManagerObject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_obj_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'model_obj_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'smart_manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smart_manager.SmartManager']"})
        }
    }

    complete_apps = ['smart_manager']