import traceback

from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.module_loading import import_by_path
from manager_utils import sync, ManagerUtilsManager

from jsonfield import JSONField


class SmartManager(models.Model):
    """
    Specifies the template, its associated model template class, and whether or not deletions should
    be managed by this model template.
    """
    # A unique identifier to load smart managers by name
    name = models.CharField(max_length=128, unique=True)

    # The loadable model template class that inherits BaseSmartManager
    smart_manager_class = models.CharField(max_length=128)

    # True if this model template also deletes its objects when elements of the template
    # (or the template itself) is deleted
    manages_deletions = models.BooleanField(default=True)

    # The template of the model(s) being managed
    template = JSONField()

    objects = ManagerUtilsManager()

    def __unicode__(self):
        return self.name

    def clean(self):
        """
        Verify that the object can be built and the template class can be loaded. If any exception happens, raise
        a validation error.
        """
        try:
            smart_manager = import_by_path(self.smart_manager_class)(self.template)
            smart_manager.build()
        except Exception, e:
            raise ValidationError(u'{0} - {1}'.format(str(e), traceback.format_exc()))

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Builds the objects managed by the template before saving the template.
        """
        super(SmartManager, self).save(*args, **kwargs)

        # Built the template
        smart_manager = import_by_path(self.smart_manager_class)(self.template)
        smart_manager.build()

        # Sync all of the objects from the built template
        sync(self.smartmanagerobject_set.all(), [
            SmartManagerObject(
                smart_manager=self,
                model_obj_id=built_obj.id,
                model_obj_type=ContentType.objects.get_for_model(built_obj, for_concrete_model=False),
            )
            for built_obj in smart_manager.built_objs
        ], ['smart_manager_id', 'model_obj_id', 'model_obj_type_id'])


class SmartManagerObject(models.Model):
    """
    Tracks objects associated with model templates. This model is useful when model templates
    are used to manage deletions.
    """
    # The model template that manages this object
    smart_manager = models.ForeignKey(SmartManager)

    # The generic foreign key to the object
    model_obj_type = models.ForeignKey(ContentType)
    model_obj_id = models.PositiveIntegerField()
    model_obj = generic.GenericForeignKey('model_obj_type', 'model_obj_id', for_concrete_model=False)

    class Meta:
        unique_together = ('smart_manager', 'model_obj_type', 'model_obj_id')


@receiver(pre_delete, sender=SmartManagerObject, dispatch_uid='delete_model_obj_on_smart_manager_object_delete')
def delete_model_obj_on_smart_manager_object_delete(sender, instance, **kwargs):
    """
    If the model template is managing deletions, delete all of the model objects associated with it before
    the template is deleted.
    """
    if instance.smart_manager.manages_deletions and instance.model_obj:
        instance.model_obj.delete()
