from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

admin.site.site_header = "Portal MedSync"
admin.site.site_title = "Portal MedSync"
admin.site.index_title = "Portal MedSync"

urlpatterns = [
    path('', lambda request: redirect('admin/')),
    path('admin/', admin.site.urls),
]
