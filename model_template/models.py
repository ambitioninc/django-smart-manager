from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import pre_delete
from django.db.transaction import atomic
from django.dispatch import receiver
from django.utils.module_loading import import_by_path
from manager_utils import sync

from jsonfield import JSONField


class ModelTemplate(models.Model):
    """
    Specifies the template, its associated model template class, and whether or not deletions should
    be managed by this model template.
    """
    # The loadable model template class that inherits BaseModelTemplate
    model_template_class = models.CharField(max_length=128)

    # True if this model template also deletes its objects when elements of the template
    # (or the template itself) is deleted
    manages_deletions = models.BooleanField(default=True)

    # The template of the model(s) being managed
    template = JSONField()

    @atomic
    def save(self, *args, **kwargs):
        """
        Builds the objects managed by the template before saving the template.
        """
        super(ModelTemplate, self).save(*args, **kwargs)

        # Built the template
        model_template = import_by_path(self.model_template_class)(self.template)
        model_template.build()

        # Sync all of the objects from the built template
        sync(self.modeltemplateobject_set.all(), [
            ModelTemplateObject(
                model_template=self,
                model_obj_id=built_obj.id,
                model_obj_type=ContentType.objects.get_for_model(built_obj, for_concrete_model=False),
            )
            for built_obj in model_template.built_objs
        ], ['model_template_id', 'model_obj_id', 'model_obj_type_id'])


class ModelTemplateObject(models.Model):
    """
    Tracks objects associated with model templates. This model is useful when model templates
    are used to manage deletions.
    """
    # The model template that manages this object
    model_template = models.ForeignKey(ModelTemplate)

    # The generic foreign key to the object
    model_obj_type = models.ForeignKey(ContentType)
    model_obj_id = models.PositiveIntegerField()
    model_obj = generic.GenericForeignKey('model_obj_type', 'model_obj_id', for_concrete_model=False)

    class Meta:
        unique_together = ('model_template', 'model_obj_type', 'model_obj_id')


@receiver(pre_delete, sender=ModelTemplateObject, dispatch_uid='delete_model_obj_on_model_template_object_delete')
def delete_model_obj_on_model_template_object_delete(sender, instance, **kwargs):
    """
    If the model template is managing deletions, delete all of the model objects associated with it before
    the template is deleted.
    """
    if instance.model_template.manages_deletions and instance.model_obj:
        instance.model_obj.delete()
