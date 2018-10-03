from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from yaasapp.models import Profile, Auction


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


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ('title', 'description', 'min_price', 'deadline')


class AuctionUpdateForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ('description', )


class ConfAuctionCreationForm(forms.Form):
    CHOICES = [(x, x) for x in ("Yes", "No")]
    option = forms.ChoiceField(choices=CHOICES)

    title = forms.CharField(widget=forms.HiddenInput())
    description = forms.CharField(widget=forms.HiddenInput())
    min_price = forms.FloatField(widget=forms.HiddenInput())
    deadline = forms.DateField(widget=forms.HiddenInput())

