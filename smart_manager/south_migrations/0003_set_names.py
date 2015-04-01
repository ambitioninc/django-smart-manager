# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for i, smart_manager in enumerate(orm.SmartManager.objects.all()):
            smart_manager.name = '{0} {1}'.format(smart_manager.smart_manager_class, i)
            smart_manager.save()

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
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
    symmetrical = True
