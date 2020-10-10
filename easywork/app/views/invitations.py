# coding=utf-8
# coding=utf-8
from django.db import transaction
from django.http import JsonResponse
from rest_framework import authentication, permissions
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from easywork.app.models import Project, Invitation, Term, Contract
from  easywork.app.models import BaseUser

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

def ThisIsEmail(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


class BearerTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'


class invitationView(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    def get(self, request, format=None):

        user = request.user
        res_arr = []
        if user.user_type == 'work':
            invitations_qs = user.invitations_received.all()
        else:
            invitations_qs = user.invitations_sent.all()

        for i in invitations_qs:
            invitation_dict = {"id": i.id,
                               "owner_id": i.owner.username,
                               "invitee_id": i.invitee.username,
                               "created_date_time": i.created_date_time,
                               "status": i.status,
                               "project_id": i.project.id,
                               "invitee_email": i.invitee_email,
                               "terms_id": i.terms.id
                               }
            res_arr.append(invitation_dict)

        return JsonResponse(res_arr, status=200, safe=False)

    def post(self, request, format=None):

        project_id = request.data.get('project_id')
        invitee_id = request.data.get('invitee_id')
        currency_id = request.data.get('currency_id')
        price_per_hour = request.data.get('price_per_hour')
        weekly_limit_in_hours = request.data.get('weekly_limit_in_hours')
        payment_request = request.data.get('payment_request')

        try:
            if ThisIsEmail(invitee_id):
                invitee = BaseUser.objects.get(email=invitee_id)
            else:
                invitee = BaseUser.objects.get(username=invitee_id)
        except BaseUser.DoesNotExist:
            return JsonResponse({"error":"{} do not exist in our database".format(invitee)}, status=404)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return JsonResponse({"error":"project_id does not exist !"}, status=404)
        
        if weekly_limit_in_hours > 100:
            return JsonResponse({"error":"Is allowed maximum 100 working hours for weeks"}, status=409)

        terms = Term.objects.create(
            price_per_hour=price_per_hour,
            currency_id=currency_id,
            weekly_limit_in_hours=weekly_limit_in_hours,
            payment_request=payment_request
        )

        invitation = Invitation.objects.create(
            owner=request.user,
            invitee=invitee,
            project=project,
            terms=terms,
        )

        response = {"id": invitation.id,
                    "owner_id": invitation.owner.username,
                    "invitee_id": invitation.invitee.username,
                    "created_date_time": invitation.created_date_time,
                    "status": invitation.status,
                    "project_id": invitation.project.id,
                    "invitee_email": invitation.invitee_email,
                    "terms_id": invitation.terms.id
                    }
        
        #TODO: SEND Notification email for new inviation request..

        return JsonResponse(response, status=201)




class delete_invitation_handler(APIView):
    """ This function allow to delete invitation by owner of project """
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    def delete(self, request, invitation_id=None, format=None):

        invitation = Invitation.objects.get(id=invitation_id)
        invitation.status = "declined"
        invitation.save()

        response = {
            "code": "declined"

        }

        #TODO: send email notification

        return JsonResponse(response, status=200)

class accept_invitation_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    # @transaction.atomic()
    def post(self, request, invitation_id=None, format=None):

        invitation = Invitation.objects.get(id=invitation_id)
        invitation.status = "accepted"

        contract = Contract.objects.create(
            project=invitation.project,
            contractor=invitation.invitee,
            owner=invitation.owner,
            terms=invitation.terms,
            status='started'
        )
        invitation.contract = contract
        invitation.save()

        response = {
            "contract_id": invitation.contract.id

        }

        #TODO: SEND EMAIL NOTIFICATION TO CLIENT
        return JsonResponse(response, status=200)


class decline_invitation_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    def post(self, request, invitation_id=None, format=None):

        invitation = Invitation.objects.get(id=invitation_id)
        invitation.status = "declined"
        invitation.save()

        response = {
            "code": "declined"

        }

        #TODO: SEND EMAIL NOTIFICATION TO CLIENT.

        return JsonResponse(response, status=200)


