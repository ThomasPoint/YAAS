from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _

# Create your views here.
from yaasapp.forms import UserForm, ProfileForm, SignUpForm


def index(request):
    if request.user.is_authenticated:
        return HttpResponse("Hello, world. You're at YAAS app index")
    else:
        return HttpResponse("You are not authenticated")

@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            #return redirect('yaasapp:index')
            return redirect('home')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'yaasapp/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


def create_profile(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.birth_date = form.cleaned_data.get('birth_date')
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request,
                _('Your profile was successfully created!'))
            return redirect('home')
        else:
            messages.error(request,
                _('Please correct the error below.'))
    else:
        form = SignUpForm()
    return render(request, 'yaasapp/signup.html', {
        'form': form
    })

