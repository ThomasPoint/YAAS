import requests
from django.core import mail


def util_send_mail(object_mail, body, email_to):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            object_mail, body,
            'yaasapp@yopmail.com', [email_to],
            connection=connection,
        ).send()


def util_currency_convert(currency_dst):
    # url = 'http://api.example.com/books'
    # params = {'year': year, 'author': author}
    # r = requests.get(url, params=params)
    # books = r.json()
    # books_list = {'books': books['results']}
    # return books_list

    # http: // apilayer.net / api / live
    #
    # ? access_key = dfd9afd300638847c6b6435349e35c24
    # & currencies = EUR, GBP, CAD, PLN
    # & source = USD
    # & format = 1

    url = "http://data.fixer.io/api/latest"
    params = {'access_key':'22f4f0beedb2412f347388c5b275fd60',
              'base': 'EUR',
              'symbols': currency_dst}
    r = requests.get(url, params)
    result = r.json()
    rates = result['rates']
    key = f'{currency_dst}'
    return rates[key]
