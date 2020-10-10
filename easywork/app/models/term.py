# coding=utf-8

from django.utils.translation import ugettext_lazy as _
from django.db import models


class Term(models.Model):
    PAYMENT_REQUEST_DAILY = 'daily'
    PAYMENT_REQUEST_WEEKLY = 'weekly'
    PAYMENT_REQUEST_MONTHLY = 'monthly'
    PAYMENT_REQUEST_CHOICES = (
        (PAYMENT_REQUEST_DAILY, _('Daily')),
        (PAYMENT_REQUEST_WEEKLY, _('Weekly')),
        (PAYMENT_REQUEST_MONTHLY, _('Monthly'))
    )
    price_per_hour = models.IntegerField(null=True,blank=True)
    currency_id = models.CharField(max_length=64, null=True,blank=True)
    weekly_limit_in_hours = models.IntegerField(null=True,blank=True)
    payment_request = models.CharField(max_length=10, choices=PAYMENT_REQUEST_CHOICES, default=PAYMENT_REQUEST_WEEKLY)

    created_date_time = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)