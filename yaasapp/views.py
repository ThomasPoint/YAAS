from datetime import datetime, timedelta, timezone

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import generic
from django.views.generic.list import ListView
from rest_framework import viewsets
from rest_framework.decorators import api_view

from yaasapp.forms import UserForm, ProfileForm, SignUpForm, AuctionForm, \
    AuctionUpdateForm
from yaasapp.models import Profile, Auction
from yaasapp.serializers import ProfileSerializer


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
            if not user_form.data['email']:
                messages.error(request, _('The email field should not be empty.'))
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

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, _('Your password was successfully updated!'))
            return redirect('home')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'yaasapp/change_password.html', {
        'form': form
    })

@login_required
def create_auction(request):
    if request.method == 'POST':
        auction_form = AuctionForm(request.POST)
        if auction_form.is_valid():
            auction = auction_form.save(commit=False)
            auction.seller = request.user
            auction.state = 'ACTIVE'
            auction_form.save()
            messages.success(request,
                             'Your auction was successfully created!')
            send_mail(
                'Auction creation',
                'Your auction was successfully created!',
                'yaasapp@yopmail.com',
                [request.user.email],
                fail_silently=False,
            )
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below : ')
            '''
            if auction_form.data['deadline'] < (datetime.now(timezone.utc) + \
                    timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'):
                    messages.error(request, _('The deadline should be 3 days after the day you posted it'))
            '''

    else:
        auction_form = AuctionForm()
    return render(request, 'yaasapp/create_auction.html', {
        'auction_form': auction_form
    })

@login_required
def update_auction(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if request.method == 'POST':
        if auction.seller == request.user:
            if auction.state == 'ACTIVE':
                auction_form = AuctionUpdateForm(request.POST, instance=auction)
                if auction_form.is_valid():
                    auction_form.save()
                    messages.success(request,
                                     'Your auction was successfully updated!')
                    return redirect('home')
                else:
                    messages.error(request, _('Please correct the error below.'))
            else:
                return redirect('auction_not_active')
        else:
            return redirect('not_allowed')
    else:
        if auction.seller == request.user:
            if auction.state == 'ACTIVE':
                auction_form = AuctionUpdateForm(instance=auction)
            else:
                return redirect('auction_not_active')
        else:
            return redirect('not_allowed')
    return render(request, 'yaasapp/update_auction.html', {
        'auction_form': auction_form
    })


@method_decorator(login_required, name='dispatch')
@method_decorator(staff_member_required, name='dispatch')
class AuctionManagementView(generic.ListView):
    model = Auction
    template_name = 'yaasapp/manager_interface.html'
    context_object_name = 'active_auctions'

    def get_queryset(self):
        """Return the last five published questions."""
        # return Question.objects.order_by('-pub_date')[:5]
        return Auction.objects.filter(
            #Q(state='ACTIVE') | Q(state='BANNED')
            state='ACTIVE'
        )

    def get_context_data(self, **kwargs):
        context = super(AuctionManagementView, self).get_context_data(**kwargs)
        context['banned_auctions'] = Auction.objects.filter(state='BANNED')
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AuctionManagementView, self).dispatch(*args, **kwargs)

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(AuctionManagementView, self).dispatch(*args, **kwargs)


@login_required
@staff_member_required
def ban_auction(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    auction.state = 'BANNED'
    auction.save()
    messages.success(request,
                     'The auction has successfully be banned!')
    return redirect('yaasapp:manage_auction')

@login_required
@staff_member_required
def active_auction(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    auction.state = 'ACTIVE'
    auction.save()
    messages.success(request,
                     'The auction has successfully be activated!')
    return redirect('yaasapp:manage_auction')


"""
Allow registered / unregistered user to get access to the list of active auctions
"""
class ActiveAuctionsView(generic.ListView):
    model = Auction
    template_name = 'yaasapp/search_active_auctions.html'
    context_object_name = 'active_auctions'

    def get_queryset(self):
        """Return the last five published questions."""
        # return Question.objects.order_by('-pub_date')[:5]
        return Auction.objects.filter(
            state='ACTIVE'
        )


def search_auction_by_title(request):
    if ('title' in request.GET) and request.GET['title'].strip():
        title = request.GET['title']
        auctions = Auction.objects.filter(title__contains=title, state='ACTIVE')
        return render(request, 'yaasapp/search_auctions_by_title.html', {
            'auctions': auctions
        })
    else:
        return render(request, 'yaasapp/search_auctions_by_title.html', {
            'auctions': None
        })




# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
