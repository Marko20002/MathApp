from django.contrib import admin
from django.urls import path, include   # внимавај include да е увезен

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",include("webui.urls")),
]
