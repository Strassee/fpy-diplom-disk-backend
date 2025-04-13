import re
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from .models import Storages, Storage_files

class UserGetSerializer(ModelSerializer):
  class Meta:
    model = User
    fields = ['id', 'username']

class StoragesGetSerializer(ModelSerializer):
  user = UserGetSerializer(read_only=True)

  class Meta:
    model = Storages
    fields = ['id', 'last_update', 'user']
  
class StorageByUserIdGetSerializer(ModelSerializer):
  class Meta:
    model = Storages
    fields = ['user_id']

class FileGetSerializer(ModelSerializer):
  class Meta:
    model = Storage_files
    # fields = '__all__'
    fields = ['id', 'name_origin', 'size', 'comment', 'date_load', 'date_download', 'public_url']

class FileUpdateSerializer(ModelSerializer):
  class Meta:
    model = Storage_files
    fields = ['name_origin', 'comment']
    # read_only_fields = ['id', 'name_storage', 'size', 'date_load', 'date_download', 'url_download', 'storage_id']

  def validate(self, attrs):
    name_origin_regexp = re.compile(r'^[0-9a-zA-Zа-яА-Я_\-. ]+$')
    if 0 > len(attrs['name_origin']) > 255 or name_origin_regexp.match(attrs['name_origin']) is None:
      raise ValidationError('name_origin validation error')
    if len(attrs['comment']) > 255 :
      raise ValidationError('comment validation error')

    return attrs