from django.contrib import admin
from smart_manager.models import SmartManager

admin.site.register(SmartManager)


class SmartManagerAdmin(admin.ModelAdmin):
    fields = ('name', 'smart_manager_class')
