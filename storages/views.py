import json
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.permissions import IsAdmin
from storages.permissions import IsOwnerOrAdmin, IsOwnerDownloadOrAdmin
from storages.serializers import StoragesGetSerializer, FileGetSerializer, FileUpdateSerializer, UserGetSerializer
from storages.models import Storages, Storage_files
from storages.functions import save_files, delete_file, download_file, public_url, download_file_public

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdmin])
def storages_get(request):
  storages = Storages.objects.select_related('user').all().order_by('id')
  serializer = StoragesGetSerializer(storages, many=True)
  return Response(serializer.data, status=200)

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsOwnerOrAdmin])
def storage_api(request, storage_id, file_id = False):
  if request.method == 'GET' and file_id is False:
    files = Storage_files.objects.filter(storage_id=storage_id).order_by('-date_load') #select_related('storage')
    user = Storages.objects.get(id=storage_id).user
    serializer_file = FileGetSerializer(files, many=True)
    serializer_user = UserGetSerializer(user)
    return Response({'files': serializer_file.data, 'user': serializer_user.data}, status=200)

  if request.method == 'GET' and file_id is not False:
    try:
      file = Storage_files.objects.get(id=file_id, storage_id=storage_id)
      serializer = FileGetSerializer(file)
      return Response({"file": serializer.data}, status=200)
    except Storage_files.DoesNotExist:
      return Response(json.dumps({"errors": {"file": ["File not found"]}}), status=404)
  
  if request.method == 'POST':
    request_files = request.FILES.getlist('files[]') if 'files[]' in request.FILES else None
    if request_files:
      save_files(request_files, request.data['comments'], storage_id)
      return Response({'status': True}, status=200)
    return Response(json.dumps({"errors": {"file": ["Files not found"]}}), status=422)

  if request.method == 'PATCH' and file_id is not False:
    try:
      file = Storage_files.objects.get(id=file_id)
      serializer = FileUpdateSerializer(instance=file, data=request.data, partial=True)
      if serializer.is_valid():
        serializer.save()
        Storages.objects.get(id=storage_id).save()
        return Response({'status update file' : True}, status=200)
      return Response(json.dumps({"errors": serializer.errors}), status=400)         
    except Storage_files.DoesNotExist:
      return Response(json.dumps({"errors": {"file": ["File not found"]}}), status=404)

  if request.method == 'DELETE':
    if delete_file(storage_id, file_id):
      return Response({f'status file delete' : True}, status=200)
    else:
      return Response(json.dumps({"errors": {"file": ["File not found"]}}), status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsOwnerDownloadOrAdmin])
def download_api(request, file_id):
  path_arr = request.path.split('/')[1:-1]
  if request.method == 'GET' and len(path_arr) == 3:
    response = download_file(file_id)
    if response:
      return response
    else:
      return Response(json.dumps({"errors": {"file": ["File not found"]}}), status=404)
    
  elif request.method == 'GET' and len(path_arr) == 4 and path_arr[2] == 'share':
    token = public_url(file_id)
    if token is not False:
      return Response({'status': True, 'token': token}, status=200)
    else:
      return Response(json.dumps({"errors": {"file": ["File not found"]}}), status=404)

@api_view(['GET'])
@permission_classes([AllowAny])
def download_public_api(request, public_url):
  path_arr = request.path.split('/')[1:-1]
  if request.method == 'GET' and len(path_arr) == 5 and path_arr[3] == 'public':
    response = download_file_public(path_arr[-1])
  if response:
    return response
  else:
    return Response(json.dumps({"errors": {"file": ["File not found"]}}), status=404)