from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from yaasapp.models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date')


class SignUpForm(UserCreationForm):
    birth_date = forms.DateField()
    # bio = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',
                  'birth_date', 'password1', 'password2')