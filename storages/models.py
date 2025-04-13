from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Storages(models.Model):
    user = models.OneToOneField(User, related_name="storage", on_delete=models.CASCADE)
    count_files = models.IntegerField()
    total_files_size = models.BigIntegerField()
    last_update = models.DateTimeField(editable=False, auto_now=True)

class Storage_files(models.Model):
    storage = models.ForeignKey(Storages, on_delete=models.CASCADE)
    name_origin = models.CharField(max_length=255)
    name_storage = models.UUIDField(editable=False)
    size = models.PositiveBigIntegerField(editable=False)
    comment = models.CharField(max_length=255, null=True, blank=True)
    date_load = models.DateTimeField(editable=False, auto_now_add=True)
    date_download = models.DateTimeField(null=True, blank=True)
    public_url = models.CharField(max_length=255, null=True, blank=True)
