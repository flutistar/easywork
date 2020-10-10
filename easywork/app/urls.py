from django.contrib import admin
from django.urls import path, re_path
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from easywork.app.views import users as user_views, static_views
from easywork.app.views import projects as project_views
from easywork.app.views import contracts as contract_views
from easywork.app.views import invitations as invitation_views
from easywork.app.views import payments as payment_views
from easywork.app.views import ipns as ipn_views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^docs/', include_docs_urls(title='EasyWork API',
                                         authentication_classes=[],
                                         permission_classes=[])),
    re_path(r'^$', static_views.home, name='home'),
]

# The following is just the backwards compatible version
urlpatterns += [

    # User
    re_path(r'^users/?$', user_views.userView.as_view(), name='api_user_create'),  # 1 DONE TESTED
    re_path(r'^users/(?P<user_id>[-\w]+)/?$', user_views.get_user_by_id_handler.as_view(), name='api_user_get'),  # 20 DONE TESTED
    re_path(r'^user/login/?$', user_views.login_user_handler.as_view(), name='login_user_handler'),  # 2


    re_path(r'^projects/?$', project_views.projectView.as_view(), name='api_project'),  # 7 #8 DONE TESTED
    re_path(r'^projects/(?P<project_id>[-\w]+)/?$', project_views.get_project_by_id_handler.as_view(), name='api_project_get'),  # 15 DONE TESTED


    re_path(r'^invitations/?$', invitation_views.invitationView.as_view(), name='api_invitation'),  # 10 #12 DONE TESTED


    re_path(r'^invitations/(?P<invitation_id>[-\w]+)/accept/?$', invitation_views.accept_invitation_handler.as_view(), name='api_invitation_accept'),  # 19 DONE TESTED
    re_path(r'^invitations/(?P<invitation_id>[-\w]+)/decline/?$', invitation_views.decline_invitation_handler.as_view(), name='api_invitation_decline'),  # 18 DONE
    re_path(r'^invitations/(?P<invitation_id>[-\w]+)?$', invitation_views.delete_invitation_handler.as_view(), name='api_invitation_delete'),

    re_path(r'^contracts/?$', contract_views.contractView.as_view(), name='api_contract'),  # 21 DONE
    re_path(r'^contracts/(?P<contract_id>[-\w]+)/?$', contract_views.get_contract_by_id_handler.as_view(), name='api_contract_get'),  # 16 DONE


    re_path(r'^contracts/(?P<contract_id>[-\w]+)/terms/?$', contract_views.get_contract_terms_by_id_handler.as_view(), name='api_contract_get_terms'),  # 17 #DONE
    re_path(r'^contracts/(?P<contract_id>[-\w]+)/totals/?$', contract_views.get_contract_totals_by_id_handler.as_view(), name='api_contract_get_totals'),  # 29 #DONE
    re_path(r'^contracts/(?P<contract_id>[-\w]+)/events/?$', contract_views.get_contract_events_by_id_handler.as_view(), name='api_contract_get_events'),  # 27 DONE
    re_path(r'^contracts/(?P<contract_id>[-\w]+)/events/(?P<event_type>[\w-]+)/?$', contract_views.events_contract_handler.as_view(), name='api_contract_events'),
    re_path(r'^contracts/(?P<contract_id>[-\w]+)/end/?$', contract_views.end_contract_handler.as_view(), name='api_contract_end'),  # 14 DONE
    re_path(r'^contracts/(?P<contract_id>[-\w]+)/pause/?$', contract_views.pause_contract_handler.as_view(), name='api_contract_pause'),  # 26 DONE
    re_path(r'^contracts/(?P<contract_id>[-\w]+)/resume/?$', contract_views.resume_contract_handler.as_view(), name='api_contract_resume'),  # 25 DONE
    re_path(r'^contracts/(?P<contract_id>[-\w]+)/pay/?$', contract_views.pay_contract_handler.as_view(), name='api_contract_pay'),

    re_path(r'^screenshots/(?P<filepath>[\w\/,\s-]+\.[A-Za-z]{3})$', contract_views.screenshots_contract_handler.as_view(), name='api_get_screenshot_file'),

    re_path(r'^payments/?$', payment_views.paymentView.as_view(), name='api_payment'),

    re_path(r'^ipn/coinpayments/', ipn_views.coinpayments_handler.as_view(), name='ipn_coinpayments')
    # re_path(r'^payments/$', PaymentList.as_view(), name='payment_list'),
    # re_path(r'^payment/(?P<pk>[0-9a-f-]+)$', PaymentDetail.as_view(), name='payment_detail'),
    # re_path(r'^payment/?$', payment_views.PaymentSetupView.as_view(), name='payment_setup'),
    # re_path(r'^payment/new/(?P<pk>[0-9a-f-]+)$', payment_views.create_new_payment, name='payment_new'),
]
