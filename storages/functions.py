import os
import shutil
import uuid
import json
import binascii
from datetime import datetime
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.db.models import Sum
from django.conf import settings
from storages.models import Storages, Storage_files

path = os.getcwd() 
parent = os.path.join(path, os.pardir)
recycle_bin_storages_dir = os.path.join(parent, settings.MEDIA_ROOT, 'recycle_bin_storages')
storages_dir = os.path.join(parent, settings.MEDIA_ROOT)

def mk_system_dirs():
  if os.path.isdir(storages_dir) is False:
    os.mkdir(storages_dir)
  if os.path.isdir(recycle_bin_storages_dir) is False:
    os.mkdir(recycle_bin_storages_dir)
  
mk_system_dirs()

def mk_storage(id):
  storage_user_dir = os.path.join(storages_dir, str(id))
  if os.path.isdir(storage_user_dir) is False:
    os.mkdir(storage_user_dir)
  return storages_dir

def replace_delete_user_storage(storage_id):
  storage_user_dir = os.path.join(storages_dir, str(storage_id))
  if os.path.isdir(storage_user_dir) is not False:
    shutil.copytree(storage_user_dir, os.path.join(recycle_bin_storages_dir, str(storage_id)), dirs_exist_ok = True)
    shutil.rmtree(storage_user_dir)
    return True
  return False

def storage_statistic(storage_id):
  storage_user_files = Storage_files.objects.filter(storage_id = storage_id)
  storage = Storages.objects.get(id=storage_id)
  storage.count_files = storage_user_files.count()
  total_files_size = storage_user_files.aggregate(Sum("size"))['size__sum']
  storage.total_files_size = total_files_size if total_files_size != None else 0
  storage.save()

def save_files(request_files, request_comments, id):
  mk_storage(id)
  comments = json.loads(request_comments)
  fs = FileSystemStorage(os.path.join(settings.MEDIA_ROOT, str(id)))
  for file in request_files:
    uuid_name = str(uuid.uuid4().hex)
    Storage_files.objects.create(storage_id = id, name_origin = file.name, name_storage = uuid_name, comment=comments.get(f'comment_{file.name}_{file.size}'), size = file.size)
    storage_statistic(id)
    fs.save(uuid_name, file)

def delete_file(storage_id, file_id):
  try: 
    file = Storage_files.objects.get(id=file_id)
    file.delete()
    storage_statistic(storage_id)
    fs = FileSystemStorage(os.path.join(settings.MEDIA_ROOT, str(storage_id)))
    if fs.exists(file.name_storage.hex):
      fs.delete(file.name_storage.hex)
      return True
    else:
      return False
  except Storage_files.DoesNotExist:
    return False

def download_file(file_id):
  try:
    file_object = Storage_files.objects.get(id=file_id)
    path_to_file = os.path.join(storages_dir, str(file_object.storage_id), str(file_object.name_storage.hex))
    file = open(path_to_file, 'rb')
    response = FileResponse(file, as_attachment=True, filename=file_object.name_origin)
    file_object.date_download = datetime.now()
    file_object.save(update_fields=["date_download"]) 
    return response
  except Storage_files.DoesNotExist:
    return False

def public_url(file_id):
  try:
    token = None
    file_object = Storage_files.objects.get(id=file_id)
    if file_object.public_url == None:
      token = binascii.hexlify(os.urandom(20)).decode()
      file_object.public_url = token
    else:
      file_object.public_url = None
    file_object.save(update_fields=["public_url"])
    return token
  except Storage_files.DoesNotExist:
    return False
  
def download_file_public(public_url):
  try:
    file_object = Storage_files.objects.get(public_url=public_url)
    path_to_file = os.path.join(storages_dir, str(file_object.storage_id), str(file_object.name_storage.hex))
    file = open(path_to_file, 'rb')
    # create the file response object
    response = FileResponse(file, as_attachment=True, filename=file_object.name_origin)
    # set the filename for the response
    # response['Content-Disposition'] = f"attachment; filename={base64.b64encode(bytes(file_object.name_origin, 'utf-8')).decode()}"
    file_object.date_download = datetime.now()
    file_object.save(update_fields=["date_download"]) 
    return response
  except Storage_files.DoesNotExist:
    return False