from django.conf.urls import url
from django.urls import path, include
from rest_framework import routers
from yaasapp.views import UserViewSet, AuctionViewSet, api_bid
from . import views

app_name ='yaasapp'

# Routers provide an easy way of automatically determining the URL conf.
# this is for the API
router = routers.DefaultRouter()
router.register('users', UserViewSet)
router.register('auctions', AuctionViewSet)

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
    path('save_auction', views.save_auction, name='save_auction'),
    path('bid/<int:auction_id>', views.bid, name='bid'),
    path('resolve_auction', views.resolve_auction, name='resolve_auction'),
    path('update_auction_seller/<int:auction_id>', views.update_auction_without_login, name='update_auction_seller'),
    url(r'^api/', include(router.urls)),
    path('api/auction/<int:auction_id>', views.auction_by_id, name='auction_by_id'),
    path('api/bid', api_bid),
    path('generatedata', views.generatedata, name='generate_data'),
    path('language/<slug:lang_code>', views.change_language, name='language'),
]


