import inspect
import traceback

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.module_loading import import_string
from manager_utils import sync, ManagerUtilsManager
import six

from jsonfield import JSONField


@six.python_2_unicode_compatible
class SmartManager(models.Model):
    """
    Specifies the template, its associated model template class, and whether or not deletions should
    be managed by this model template.
    """
    # A unique identifier to load smart managers by name
    name = models.CharField(max_length=128, unique=True, null=True, default=None)

    # The loadable model template class that inherits BaseSmartManager
    smart_manager_class = models.CharField(max_length=128)

    # True if this model template also deletes its objects when elements of the template
    # (or the template itself) is deleted
    manages_deletions = models.BooleanField(default=True)

    # The primary object that this smart manager manages
    primary_obj_type = models.ForeignKey(ContentType, null=True)
    primary_obj_id = models.PositiveIntegerField(default=0)
    primary_obj = GenericForeignKey('primary_obj_type', 'primary_obj_id')

    # The template of the model(s) being managed
    template = JSONField()

    objects = ManagerUtilsManager()

    def __str__(self):
        return str(self.name)

    def clean(self):
        """
        Verify that the object can be built and the template class can be loaded. If any exception happens, raise
        a validation error.
        """
        try:
            smart_manager = import_string(self.smart_manager_class)(self.template)
            smart_manager.build()
        except Exception as e:
            raise ValidationError('{0} - {1}'.format(str(e), traceback.format_exc()))

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        Builds the objects managed by the template before saving the template.
        """
        super(SmartManager, self).save(*args, **kwargs)

        smart_manager = import_string(self.smart_manager_class)(self.template)
        primary_built_obj = smart_manager.build()

        # Do an update of the primary object type and id after it has been built. We use an update since
        # you can't call save in a save method. We may want to put this in post_save as well later.
        if primary_built_obj:
            self.primary_obj_type = ContentType.objects.get_for_model(primary_built_obj)
            self.primary_obj_id = primary_built_obj.id
            SmartManager.objects.filter(id=self.id).update(
                primary_obj_type=self.primary_obj_type, primary_obj_id=primary_built_obj.id)

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
    model_obj = GenericForeignKey('model_obj_type', 'model_obj_id', for_concrete_model=False)

    objects = ManagerUtilsManager()

    class Meta:
        unique_together = ('model_obj_type', 'model_obj_id')


class SmartModelMixin(object):
    """
    A mixin for django models that provides smart manager behavior. The functions provided for models are

    smart_upsert: Upsert an existing model with a provided smart manager class and template,
    smart_delete: Delete an existing model and flush its associated smart manager.
    """
    def _get_smart_manager(self):
        """
        Gets the smart manager associated with this object or None if it doesn't have one.
        """
        smo = SmartManagerObject.objects.get_or_none(
            model_obj_type=ContentType.objects.get_for_model(self, for_concrete_model=False),
            model_obj_id=self.id)
        return smo.smart_manager if smo else None

    def smart_upsert(self, sm_class, sm_template):
        """
        Upserts an existing model using a smart manager class and template.
        """
        if not self.id:
            raise ValueError('Cannot call smart_upsert on a non-persisted model')

        sm = self._get_smart_manager()
        return SmartManager.objects.upsert(
            id=sm.id if sm else None,
            updates={
                'template': sm_template,
                'smart_manager_class': '{0}.{1}'.format(inspect.getmodule(sm_class).__name__, sm_class.__name__),
            })[0]

    def smart_delete(self):
        """
        Deletes the object's smart manager. Note that the object is normally managed by the smart manager, so the object
        is often deleted as well.
        """
        sm = self._get_smart_manager()
        self.delete()
        if sm:
            sm.delete()


class SmartManagerMixin(object):
    """
    Provides additional "smart" functions for Django model managers, including:

    smart_create: Creates an object using a smart manager and returns the smart manager.
    """
    def smart_create(self, sm_class, sm_template):
        """
        Given a smart manager class and template, constructs the object using the smart manager,
        and returns the smart manager object.
        """
        sm_class_path = '{0}.{1}'.format(inspect.getmodule(sm_class).__name__, sm_class.__name__)
        return SmartManager.objects.create(smart_manager_class=sm_class_path, template=sm_template)
