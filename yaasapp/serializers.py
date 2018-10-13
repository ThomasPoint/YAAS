from django.contrib.auth.models import User
from rest_framework import serializers

from yaasapp.models import Profile, Auction, Bid


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


# Serializers define the API representation.
class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Profile
        fields = ('user',
                  'birth_date', 'location')


class AuctionSerializer(serializers.HyperlinkedModelSerializer):
    seller = UserSerializer(required=True)

    class Meta:
        model = Auction
        fields = ('pk', 'seller', 'title', 'description', 'min_price', 'post_date',
                  'deadline', 'state')


class BidSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bid
        fields = '__all__'