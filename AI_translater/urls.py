# type: ignore
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("upload/", views.upload_and_translate, name="upload_and_translate"),
]
