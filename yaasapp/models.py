from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from datetime import datetime, timedelta, timezone, date
from django.utils.translation import gettext as _

# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=40, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def clean(self):
        if not self.user.email:
            raise ValidationError(_('The email should not be empty'))

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwarg):
    instance.profile.save()


class Auction(models.Model):
    STATE = (
        ('ACTIVE', 'active'),
        ('BANNED', 'banned'),
        ('DUE', 'due'),
        ('ADJUCATED', 'adjudicated'),
        ('DEFAULT', 'default')
        ,
    )
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=60, blank=False)
    description = models.TextField(max_length=500, blank=False)
    min_price = models.FloatField(blank=False, default=1)
    state = models.CharField(max_length=1, choices=STATE, default='DEFAULT')
    post_date = models.DateField(default=date.today())
    deadline = models.DateField(default=date.today()+timedelta(days=3))

    def clean(self):
        if self.min_price < 1:
            raise ValidationError(_('The minimum price should be at least 1'))
        elif self.deadline < self.post_date + timedelta(days=3):
            raise ValidationError(_('The deadline should be 3 days after the '
                                    'day you posted it'))


class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=False, default=datetime.now())
    value = models.DecimalField(blank=False, decimal_places=2, max_digits=1000)
