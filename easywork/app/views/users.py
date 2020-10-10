# coding=utf-8
import datetime, pytz
from django.db import transaction
from django.http import JsonResponse
from django.contrib import auth
from rest_framework import authentication, permissions
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from  easywork.app.models import BaseUser


class BearerTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'


class userView(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    parser_classes = (JSONParser, FormParser)

    #
    # def get(self, request, format=None):
    #     error_response = {}
    #     return Response("Get test")

    @transaction.atomic()
    def post(self, request, format=None):
        email = request.data.get('email')
        id = request.data.get('id')
        user_type = request.data.get('user_type')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        user = BaseUser.objects.create(
            email=email,
            username=id,
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
            date_joined=datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        )
        user.set_password(password)
        user.save()

        token, _ = Token.objects.get_or_create(user=user)
        response = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "id": user.username,
            "email": user.email,
            "token": token.key

        }
        return JsonResponse(response, status=201)


class get_user_by_id_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    #
    def get(self, request, user_id=None, format=None):

        user = BaseUser.objects.get(username=user_id)

        response = {
            "is_admin": user.is_staff,
            "user_type": user.user_type,
            "id": user.username,
            "email": user.email,
            "created_date_time": user.created_at

        }
        return JsonResponse(response, status=200)


class login_user_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.AllowAny,)

    parser_classes = (JSONParser, FormParser)

    # @transaction.atomic()
    def post(self, request, format=None):
        email = request.data.get('email')
        password = request.data.get('password')
        user = auth.authenticate(username=email, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)

            token, _ = Token.objects.get_or_create(user=user)
            response = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "id": user.username,
                "email": user.email,
                "token": token.key

            }
            return JsonResponse(response, status=200)
        else:
            response = {"code": 1010, "message": "Wrong email or password"}
            return JsonResponse(response, status=401)


class types(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    def get(self, request, format=None):
        error_response = {}
        return Response("Get test")


class verify_token_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    @transaction.atomic()
    def post(self, request, format=None):
        return Response("Post test")


class show_status_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    def get(self, request, format=None):
        error_response = {}
        return Response("Get test")


class get_users_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    def get(self, request, format=None):
        error_response = {}
        return Response("Get test")


class update_user_password_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)


    @transaction.atomic()
    def post(self, request, format=None):
        return Response("Post test")


class update_user_profile_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)


    @transaction.atomic()
    def post(self, request, format=None):
        return Response("Post test")
