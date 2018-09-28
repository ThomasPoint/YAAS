from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from yaasapp.views import UserViewSet
from . import views

app_name ='yaasapp'

# Routers provide an easy way of automatically determining the URL conf.
# this is for the API
router = routers.DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('profile_update', views.update_profile, name='profile_update'),
    path('profile_create', views.create_profile, name='profile_create'),
    path('change_password', views.change_password, name='change_password'),
    url(r'^api/', include(router.urls)),
]


