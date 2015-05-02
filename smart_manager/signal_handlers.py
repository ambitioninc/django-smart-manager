from django.db.models.signals import pre_delete
from django.dispatch import receiver

from smart_manager.models import SmartManagerObject


@receiver(pre_delete, sender=SmartManagerObject, dispatch_uid='delete_model_obj_on_smart_manager_object_delete')
def delete_model_obj_on_smart_manager_object_delete(sender, instance, **kwargs):
    """
    If the model template is managing deletions, delete all of the model objects associated with it before
    the template is deleted.
    """
    if instance.smart_manager.manages_deletions:
        try:
            instance.model_obj.delete()
        except:
            # The model object could have been deleteed. Its ctype could have been corrupted. It could
            # have also been trying to cascade delete a protected model. Ignore any deletion errors with
            # model objects.
            pass
