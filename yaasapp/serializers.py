from django.contrib.auth.models import User
from rest_framework import serializers

from yaasapp.models import Profile


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