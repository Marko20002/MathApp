from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('ms-admin-panel/', admin.site.urls),
    path('api/auth/',   include('accounts.urls')),
    path('api/solver/', include('solver.urls')),
]
