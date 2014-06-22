from django.db import models


class UpsertModel(models.Model):
    """
    A model for testing upserts.
    """
    char_field = models.CharField(max_length=128)
    int_field = models.IntegerField()


class RelModel(models.Model):
    pass


class CantCascadeModel(models.Model):
    rel_model = models.ForeignKey(RelModel, on_delete=models.PROTECT)
