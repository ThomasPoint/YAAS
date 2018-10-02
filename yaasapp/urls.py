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
    path('create_auction', views.create_auction, name='create_auction'),
    path('update_auction/<int:auction_id>', views.update_auction,
         name='update_auction'),
    path('manage_auctions', views.AuctionManagementView.as_view(),
         name='manage_auction'),
    path('ban_auction/<int:auction_id>', views.ban_auction, name='ban_auction'),
    path('active_auction/<int:auction_id>', views.active_auction, name='active_auction'),
    path('active_auction_list', views.ActiveAuctionsView.as_view(),
         name='active_auction_list'),
    path('search_auction_by_title', views.search_auction_by_title, name='search_auction_by_title'),
    url(r'^api/', include(router.urls)),
]


