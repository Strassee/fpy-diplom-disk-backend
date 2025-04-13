from rest_framework.permissions import BasePermission
from .models import Storages, Storage_files

class IsOwnerOrAdmin(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET' or request.method == 'POST' or request.method == 'PATCH' or request.method == 'DELETE':
      try:
        return Storages.objects.get(user_id=request.user.id).id == view.kwargs['storage_id'] or request.user.is_superuser
      except:
        return False
  
class IsOwnerDownloadOrAdmin(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':
      try:
        return request.user.id == Storages.objects.get(id=Storage_files.objects.get(id=view.kwargs['file_id']).storage_id).user_id or request.user.is_superuser
      except:
        return False