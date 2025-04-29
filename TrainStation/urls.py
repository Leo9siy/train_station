"""
URL configuration for TrainStation project.

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
from debug_toolbar.toolbar import debug_toolbar_urls
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/station/", include("station.urls", namespace="station")),
    path("api/v1/user/", include("user.urls", namespace="user")),
    path("api/doc/", SpectacularAPIView.as_view(), name="doc"),
    path("api/doc/swagger/", SpectacularSwaggerView.as_view(url_name="doc")),
    path("api/doc/redoc/", SpectacularRedocView.as_view(url_name="doc")),
] + debug_toolbar_urls()
