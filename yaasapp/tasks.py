from datetime import date
from django.contrib.auth.models import User

from YAAS.celery import app
from yaasapp.models import Auction, Bid
from yaasapp.utils import util_send_mail


@app.task
def resolve_auction():
    auctions = Auction.objects.filter(state='ACTIVE')
    # we change the state of the auctions
    for auction in auctions:
        date_today = date.today()
        if auction.deadline < date_today: # à changer par <
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
                # check if there are other bidder and send them notifications
                if not Bid.objects.filter(auction=auction)[1:]:
                    pass
                else:
                    bidders_id = Bid.objects.filter(
                        auction=auction).values_list('bidder',
                                                     flat=True).distinct()
                    for bidder_id_value in bidders_id:
                        if bidder_id_value != winner.id:
                            user_mail = User.objects.get(
                                pk=bidder_id_value).email
                            util_send_mail('Auction lost',
                                           f'You have not won this auction : {auction.title}',
                                           user_mail)
            else:
                util_send_mail('Auction Finished',
                               f'No one has bidden for your auction : {auction.title}',
                               winner.email)






