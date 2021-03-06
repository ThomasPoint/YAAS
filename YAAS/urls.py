"""YAAS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('not_allowed', TemplateView.as_view(template_name='not_allowed.html'),
         name='not_allowed'),
    path('auction_not_active', TemplateView.as_view(template_name='auction_not_active.html'),
         name='auction_not_active'),
    path('yaasapp/', include('django.contrib.auth.urls')),
    path('yaasapp/', include('yaasapp.urls')),
    url(r'^admin/', admin.site.urls),
]
