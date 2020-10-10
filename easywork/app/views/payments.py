# from decimal import Decimal
# from django import forms
# # from django_coinpayments.models import Payment
# # from django_coinpayments.exceptions import CoinPaymentsProviderError
from django.http import JsonResponse
# from django.views.generic import FormView, ListView, DetailView
# from django.shortcuts import render, get_object_or_404
from rest_framework import authentication, permissions
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token
# from easywork.app.models import Payment


class BearerTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'


class paymentView(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    #
    def get(self, request, format=None):
        # '''
        # request:
        #
        # response:
        # []
        # '''

        user = request.user
        res_arr = []

        if user.user_type == 'work':
            # TODO:
            # payments = user.payments.all()
            payments = []
        else:
            payments = user.payments.all()

        for p in payments:
            payment_dict = {
                'id': p.id,
                'currency': p.currency,
                'amount': p.amount,
                'amount_paid': p.amount_paid,
                'author_id': p.author.username,
                'status': p.status,
                'contract_id': p.contract_id
            }
            res_arr.append(payment_dict)

        return JsonResponse(res_arr, status=200, safe=False)


# class ExamplePaymentForm(forms.ModelForm):
#     class Meta:
#         model = Payment
#         fields = ['amount', 'currency_original', 'currency_paid']
#
#
# def create_tx(request, payment):
#     context = {}
#     try:
#         tx = payment.create_tx()
#         payment.status = Payment.PAYMENT_STATUS_PENDING
#         payment.save()
#         context['object'] = payment
#     except CoinPaymentsProviderError as e:
#         context['error'] = e
#     return render(request, 'django_coinpayments/payment_result.html', context)
#
#
# class PaymentDetail(DetailView):
#     model = Payment
#     template_name = 'django_coinpayments/payment_result.html'
#     context_object_name = 'object'
#
#
# class PaymentSetupView(FormView):
#     template_name = 'django_coinpayments/payment_setup.html'
#     form_class = ExamplePaymentForm
#
#     def form_valid(self, form):
#         cl = form.cleaned_data
#         payment = Payment(currency_original=cl['currency_original'],
#                           currency_paid=cl['currency_paid'],
#                           amount=cl['amount'],
#                           amount_paid=Decimal(0),
#                           status=Payment.PAYMENT_STATUS_PROVIDER_PENDING)
#         return create_tx(self.request, payment)
#
#
# class PaymentList(ListView):
#     model = Payment
#     template_name = 'django_coinpayments/payment_list.html'
#
#
# def create_new_payment(request, pk):
#     payment = get_object_or_404(Payment, pk=pk)
#     if payment.status in [Payment.PAYMENT_STATUS_PROVIDER_PENDING, Payment.PAYMENT_STATUS_TIMEOUT]:
#         pass
#     elif payment.status in [Payment.PAYMENT_STATUS_PENDING]:
#         payment.provider_tx.delete()
#     else:
#         error = "Invalid status - {}".format(payment.get_status_display())
#         return render(request, 'django_coinpayments/payment_result.html', {'error': error})
#     return create_tx(request, payment)
#
#
# class BearerTokenAuthentication(authentication.TokenAuthentication):
#     keyword = 'Bearer'
#
#
#
#     # @transaction.atomic()
#     def post(self, request, format=None):
#         p = Payment(
#             currency_original=request.data.get('currency_original'),
#             currency_paid=request.data.get('currency_paid'),
#             amount=request.data.get('amount'),
#             amount_paid=Decimal(0),
#             status=Payment.PAYMENT_STATUS_PROVIDER_PENDING
#         )
#         # '''
#         # request:
#         # {"title":"New Project","description":"Project Description"}
#         # response:
#         # {"id":3,"created_date_time":"2018-08-30T14:13:02.721687Z","owner_id":"client","title":"New Project","description":"Project Description"}
#         # '''
#         response = {}
#         status = 201
#         try:
#             p.create_tx()
#             p.status = Payment.PAYMENT_STATUS_PENDING
#             p.save()
#             response = {
#                 'currency_original': p.currency_original,
#                 'currency_paid': p.currency_paid,
#                 'amount': p.amount,
#                 'amount_paid': p.amount_paid,
#                 'status': p.status
#             }
#         except CoinPaymentsProviderError as e:
#             response['error'] = e
#             status = 422
#
#         return JsonResponse(response, status=status)