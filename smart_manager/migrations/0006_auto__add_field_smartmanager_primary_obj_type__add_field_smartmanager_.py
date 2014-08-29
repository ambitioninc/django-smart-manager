# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'SmartManager.primary_obj_type'
        db.add_column(u'smart_manager_smartmanager', 'primary_obj_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True),
                      keep_default=False)

        # Adding field 'SmartManager.primary_obj_id'
        db.add_column(u'smart_manager_smartmanager', 'primary_obj_id',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'SmartManager.primary_obj_type'
        db.delete_column(u'smart_manager_smartmanager', 'primary_obj_type_id')

        # Deleting field 'SmartManager.primary_obj_id'
        db.delete_column(u'smart_manager_smartmanager', 'primary_obj_id')


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
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'unique': 'True', 'null': 'True'}),
            'primary_obj_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'primary_obj_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'smart_manager_class': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'template': ('jsonfield.fields.JSONField', [], {})
        },
        u'smart_manager.smartmanagerobject': {
            'Meta': {'unique_together': "(('model_obj_type', 'model_obj_id'),)", 'object_name': 'SmartManagerObject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_obj_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'model_obj_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'smart_manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smart_manager.SmartManager']"})
        }
    }

    complete_apps = ['smart_manager']