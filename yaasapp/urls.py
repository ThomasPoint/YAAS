from django.urls import path

from . import views

app_name ='yaasapp'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile_update', views.update_profile, name='profile_update'),
    path('profile_create', views.create_profile, name='profile_create')
]