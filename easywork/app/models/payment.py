# coding=utf-8
import uuid
from decimal import Decimal
from datetime import datetime, timezone, timedelta
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django_coinpayments.coinpayments import CoinPayments
from django_coinpayments.exceptions import CoinPaymentsProviderError
from easywork.app.models import BaseUser, Contract, CoinPaymentsTransaction


def get_coins_list():
    return getattr(settings, 'COINPAYMENTS_ACCEPTED_COINS', None)


class Payment(models.Model):
    PAYMENT_STATUS_PAID = 'paid'
    PAYMENT_STATUS_TIMEOUT = 'timeout'
    PAYMENT_STATUS_PENDING = 'pending'
    PAYMENT_STATUS_PROVIDER_PENDING = 'provider_pending'
    PAYMENT_STATUS_CANCELLED = 'cancelled'
    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_STATUS_PROVIDER_PENDING, _('Provider-related payment pending')),
        (PAYMENT_STATUS_PENDING, _('Pending')),
        (PAYMENT_STATUS_CANCELLED, _('Cancelled')),
        (PAYMENT_STATUS_TIMEOUT, _('Timed out')),
        (PAYMENT_STATUS_PAID, _('Paid'))
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency = models.CharField(max_length=8, choices=get_coins_list(), verbose_name=_('Payment currency'))
    amount = models.DecimalField(max_digits=100, decimal_places=18, verbose_name=_('Amount'))
    amount_paid = models.DecimalField(max_digits=100, decimal_places=18, verbose_name=_('Amount paid'))
    provider_tx = models.OneToOneField(CoinPaymentsTransaction, on_delete=models.CASCADE,
                                       verbose_name=_('Payment transaction'), null=True, blank=True)
    status = models.CharField(max_length=16, choices=PAYMENT_STATUS_CHOICES)
    author = models.ForeignKey(BaseUser, related_name='payments', null=False, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, related_name='payments', null=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # objects = PaymentManager()

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def __str__(self):
        return "{} of {} - {}".format(str(self.amount_paid.normalize()), str(self.amount.normalize()), self.get_status_display())

    def is_paid(self):
        return self.status == self.PAYMENT_STATUS_PAID

    def amount_left(self):
        return self.amount - self.amount_paid

    def is_cancelled(self):
        if self.provider_tx:
            return self.provider_tx.timeout < datetime.now()

    def create_tx(self, invoice=None, **kwargs):
        """
        :param invoice: Field for custom use. Default - payment id
        :param kwargs:
            address      The address to send the funds to in currency_paid network
            buyer_email  Optionally (but highly recommended) set the buyer's email address.
                         This will let us send them a notice if they underpay or need a refund.
            buyer_name   Optionally set the buyer's name for your reference.
            item_name    Item name for your reference,
                         will be on the payment information page and in the IPNs for the transaction.
            item_number  Item number for your reference,
                         will be on the payment information page and in the IPNs for the transaction.
            custom       Field for custom use.
            ipn_url      URL for your IPN callbacks.
                         If not set it will use the IPN URL in your Edit Settings page if you have one set.
        :return: `CoinPaymentsTransaction` instance
        """
        obj = CoinPayments.get_instance()
        if not invoice:
            invoice = self.id
        params = dict(amount=self.amount_left(), currency1=self.currency,
                      currency2=self.currency, invoice=invoice)
        params.update(**kwargs)
        result = obj.create_transaction(params)
        if result['error'] == 'ok':
            result = result['result']
            timeout = datetime.now() + timedelta(seconds=result['timeout'])
            c = CoinPaymentsTransaction.objects.create(id=result['txn_id'],
                                                       amount=Decimal(result['amount']),
                                                       address=result['address'],
                                                       confirms_needed=int(result['confirms_needed']),
                                                       qrcode_url=result['qrcode_url'],
                                                       status_url=result['status_url'],
                                                       timeout=timeout)
            self.provider_tx = c
            self.save()
        else:
            raise CoinPaymentsProviderError(result['error'])

        return c
