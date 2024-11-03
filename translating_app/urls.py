# type: ignore
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("upload/", views.upload_and_translate, name="upload_and_translate"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
