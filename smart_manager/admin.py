from django.contrib import admin
from smart_manager.models import SmartManager


class SmartManagerAdmin(admin.ModelAdmin):
    fields = ('name', 'smart_manager_class', 'primary_obj_type', 'primary_obj_id')


admin.site.register(SmartManager, SmartManagerAdmin)
