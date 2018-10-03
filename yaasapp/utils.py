from django.core import mail


def util_send_mail(object_mail, body, email_to):
    with mail.get_connection() as connection:
        mail.EmailMessage(
            object_mail, body,
            'yaasapp@yopmail.com', [email_to],
            connection=connection,
        ).send()