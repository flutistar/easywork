# coding=utf-8
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.views import APIView
from easywork.app.models import Payment


class coinpayments_handler(APIView):
    parser_classes = (JSONParser, FormParser)

    def post(self, request, format=None):

        if request.HMAC is None:
            return HttpResponse('No HMAC signature sent')

        if request.data.get('ipn_mode') != 'hmac':
            return HttpResponse('IPN Mode is not HMAC')

        if request.data.get('merchant') != settings.COINPAYMENTS_MERCHANT_ID:
            return HttpResponse('Invalid Merchant ID')

        if hmac.new(settings.COINPAYMENTS_IPN_SECRET, request.data, hashlib.sha512) != request.HMAC:
            return HttpResponse('HMAC signature does not match')

        txn_id = request.data.get('txn_id')
        amount1 = float(request.data.get('amount1'))
        amount2 = float(request.data.get('amount2'))
        currency1 = request.data.get('currency1')
        currency2 = request.data.get('currency2')
        status = int(request.data.get('status'))
        status_text = request.data.get('status_text')

        payment = Payment.objects.get(provider_tx=txn_id)

        if status >= 100 or status == 2:
            payment.status = Payment.PAYMENT_STATUS_PAID
        elif status < 0:
            payment.status = Payment.PAYMENT_STATUS_CANCELLED
        else:
            payment.status = Payment.PAYMENT_STATUS_PENDING

        payment.save()

        return HttpResponse('IPN OK')
