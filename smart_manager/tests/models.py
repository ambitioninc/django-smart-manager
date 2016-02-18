from django.db import models

from smart_manager.models import SmartManagerMixin, SmartModelMixin


class UpsertModelManager(models.Manager, SmartManagerMixin):
    pass


class UpsertModel(models.Model, SmartModelMixin):
    """
    A model for testing upserts.
    """
    char_field = models.CharField(max_length=128)
    int_field = models.IntegerField()

    objects = UpsertModelManager()


class RelModel(models.Model):
    pass


class CantCascadeModel(models.Model):
    rel_model = models.ForeignKey(RelModel, on_delete=models.PROTECT)
