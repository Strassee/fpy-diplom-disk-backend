from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
  def has_permission(self, request, view):
    if request.user.is_superuser:
      return True
    return False
  
class IsAdminOrOwner(BasePermission):
  def has_permission(self, request, view):
    if request.user.is_superuser or request.user.id == view.kwargs['id']:
      return True
    return False

class IsNotOwnerDeleteOrReadPatchOnly(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':
      return True
    if request.method == 'PATCH':
      return True
    if request.method == 'DELETE':
      return request.user.id != view.kwargs['id']
  
class IsNotFirstAdminOrReadOnly(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':
      return True
    if request.method == 'PATCH':
      return request.user.id == 1 or view.kwargs['id'] != 1
    if request.method == 'DELETE':    
      return view.kwargs['id'] != 1
    