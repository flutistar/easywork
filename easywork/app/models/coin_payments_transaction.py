# coding=utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _


class CoinPaymentsTransaction(models.Model):
    id = models.CharField(max_length=100, verbose_name=_('id'), primary_key=True, editable=True)
    address = models.CharField(max_length=150, verbose_name=_('Address'))
    amount = models.DecimalField(max_digits=100, decimal_places=18, verbose_name=_('Amount'))
    confirms_needed = models.PositiveSmallIntegerField(verbose_name=_('Confirms needed'))
    qrcode_url = models.URLField(verbose_name=_('QR Code Url'))
    status_url = models.URLField(verbose_name=_('Status Url'))
    timeout = models.DateTimeField(verbose_name=_('Valid until'))

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = _('CoinPayments Transaction')
        verbose_name_plural = _('CoinPayments Transactions')
