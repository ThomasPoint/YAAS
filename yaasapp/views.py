from _decimal import Decimal
from datetime import datetime, timedelta, timezone, date

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.core import mail
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
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from yaasapp.forms import UserForm, ProfileForm, SignUpForm, AuctionForm, \
    AuctionUpdateForm, ConfAuctionCreationForm, BidForm
from yaasapp.models import Profile, Auction, Bid
from yaasapp.serializers import ProfileSerializer, AuctionSerializer
from yaasapp.utils import util_send_mail


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
            form = ConfAuctionCreationForm({'title': auction_form.cleaned_data.get('title'),
                                           'description': auction_form.cleaned_data.get('description'),
                                           'min_price': auction_form.cleaned_data.get('min_price'),
                                           'deadline': auction_form.cleaned_data.get('deadline')})

            """
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
            """
            #return redirect('home')
            return render(request, 'yaasapp/conf_auction.html', {'form': form})
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
def save_auction(request):
    option = request.POST.get('option', 'No')
    if option == 'Yes':
        title = request.POST.get('title')
        description = request.POST.get('description')
        min_price = request.POST.get('min_price')
        deadline = request.POST.get('deadline')
        auction = Auction(title=title,
                          description=description,
                          seller=request.user,
                          min_price=min_price,
                          deadline=deadline,
                          state='ACTIVE')
        auction.save()
        messages.success(request,
                         'Your auction was successfully created!')
        util_send_mail('Auction creation', 'Your auction has successfully been created!', request.user.email)
        return redirect('home')
    else:
        messages.success(request,
                         'Your auction was not created!')
        return redirect('home')

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
    util_send_mail('Banned auction', 'Your auction has been banned', auction.seller.email)

    # send mail to the bidders
    bidders_id = Bid.objects.filter(auction=auction).values_list('bidder',
                                     flat=True).distinct()
    for bidder_id_value in bidders_id:
        if bidder_id_value != auction.seller.id:
            user_mail = User.objects.get(pk=bidder_id_value).email
            util_send_mail('Banned auction',
                           f'The auction {auction.title} has been banned, you can\'t bid anymore',
                           user_mail)
    ####
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


@login_required
def bid(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)
    if auction.state == 'ACTIVE':
        if request.method == 'POST':
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                # owner of auction can't bid on it
                if auction.seller != request.user:
                    bids = Bid.objects.filter(auction=auction).order_by('-value')
                    if not bids:
                        curr_win_bidder = ""
                    else:
                        curr_win_bidder = bids[0].bidder
                    # user who currently win the auction cannot bid
                    if curr_win_bidder == "" or request.user != curr_win_bidder:
                        value = bid_form.cleaned_data.get('value')

                        if not bids:
                            max_val = auction.min_price
                        else:
                            max_val = bids[0].value
                        # check that the new value is strictly greater than the previous one
                        if value > max_val:
                            bid = Bid(bidder=request.user, auction=auction,
                                      value=value)
                            util_send_mail('New bid', 'A new bid has been created for your auction', auction.seller)
                            if curr_win_bidder != "":
                                util_send_mail('New bid', 'Your are not anymore the leader of the auction ! Bid again to be the winner !', curr_win_bidder.email)
                            bid.save()
                            messages.success(request,
                                           'You bid has been taken into account !')
                            return redirect('home')
                        else:
                            messages.error(request,
                                             f"The value of the bid should be greater than {max_val}")
                    else:
                        messages.error(request,
                                         'You cannot bid since you are winning this auction !')
                        return redirect('home')
                else:
                    messages.error(request,
                                     'You cannot bid because you are the owner of the auction !')
            else:
                messages.success(request,
                                 'Check the value you have entered !')
        else:
            bids = Bid.objects.filter(auction=auction).order_by('-value')
            if not bids :
                init_val = auction.min_price + 0.01
            else :
               init_val = bids[0].value + Decimal('0.01')
            bid_form = BidForm(initial={'value': init_val})
        return render(request, 'yaasapp/bid.html', {
            'form': bid_form,
            'description': auction.description})
    else:
        return redirect('auction_not_active')


def resolve_auction(request):
    auctions = Auction.objects.filter(state='ACTIVE')
    # we change the state of the auctions
    for auction in auctions:
        date_today = date.today()
        if auction.deadline < date_today + timedelta(days=4): # à changer par <
            auction.state = 'DUE'
            auction.save()

            # we want to resolve the auction
            # we order it by decreasing value

            if not Bid.objects.filter(auction=auction).order_by('-value'):
                winner = auction.seller
            else:
                winner = Bid.objects.filter(auction=auction).order_by('-value')[0].bidder

            auction.state = 'ADJUCATED'
            auction.save()

            # send notification mail
            util_send_mail('Auction resolved',
                           'Your auction has been resolved'
                               'and a winner has been chosen',
                           auction.seller.email)
            if winner != auction.seller:
                util_send_mail('Auction win',
                               f'You have won the auction : {auction.title}',
                               winner.email)
            else:
                util_send_mail('Auction Finished',
                               f'No one has bidden for your auction : {auction.title}',
                               winner.email)
            if not Bid.objects.filter(auction=auction)[1:]:
                pass
            else:
                bidders_id = Bid.objects.filter(auction=auction).values_list('bidder', flat=True).distinct()
                for bidder_id_value in bidders_id:
                    if bidder_id_value != winner.id:
                        user_mail = User.objects.get(pk=bidder_id_value).email
                        util_send_mail('Auction lost',
                                       f'You have not won this auction : {auction.title}',
                                       user_mail)
    return redirect('home')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class AuctionViewSet(viewsets.ModelViewSet):
    queryset = Auction.objects.all()
    serializer_class = AuctionSerializer
    permission_classes = (AllowAny,)

    # override get_queryset to handle a search by title
    def get_queryset(self):
        title = self.request.query_params.get('title')
        id_val = self.request.query_params.get('id')

        if not id_val:
            if not title:
                queryset = Auction.objects.all()
            else:
                queryset = Auction.objects.filter(title__contains=title)
        else:
            auctions = set()
            auction = get_object_or_404(Auction, pk=id_val)
            auctions.add(auction)
            queryset = auctions
        return queryset
