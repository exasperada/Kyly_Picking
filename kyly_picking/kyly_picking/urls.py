"""
URL Configuration for Kyly Picking project.
"""
from django.contrib import admin
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.urls import include, path, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^static/(?P<path>.*)$", staticfiles_serve, {"insecure": True}),
    path('', include('picking.urls')),
]
