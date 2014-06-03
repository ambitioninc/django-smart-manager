from django.db import models


class UpsertModel(models.Model):
    """
    A model for testing upserts.
    """
    char_field = models.CharField(max_length=128)
    int_field = models.IntegerField()
