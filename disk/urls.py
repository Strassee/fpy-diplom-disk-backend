"""
URL configuration for disk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from users.views import UsersLogin, user_reg, users_get, user_api
from storages.views import storages_get, storage_api, download_api, download_public_api
from rest_framework.routers import DefaultRouter


# router = DefaultRouter()
# router.register('users', UsersModelViewSet)
# print(router.urls)

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/users/', users_get),
    # path('users/<pk>/', UserView.as_view()),
    path('api/user/reg/', user_reg),
    path('api/user/login/', UsersLogin.as_view()),
    path('api/user/logout/', UsersLogin.as_view()),
    path('api/user/<int:id>/', user_api),
    path('api/storages/', storages_get),
    path('api/storage/<int:storage_id>/', storage_api),
    path('api/storage/<int:storage_id>/<int:file_id>/', storage_api),
    path('api/download/<int:file_id>/', download_api),
    path('api/download/share/<int:file_id>/', download_api),
    path('api/download/share/public/<str:public_url>/', download_public_api),
]
#]+ router.urls
