# coding=utf-8
from django.db import transaction
from django.http import JsonResponse
from rest_framework import authentication, permissions
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from easywork.app.models import Project


class BearerTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'


class projectView(APIView):
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

        for p in user.projects.all():
            project_dict = {
                'title': p.title,
                'id': p.id,
                'description': p.description,
                'owner_id': p.owner.id,
                'created_date_time': p.created_date_time
            }
            res_arr.append(project_dict)

        return JsonResponse(res_arr, status=200, safe=False)

    # @transaction.atomic()
    def post(self, request, format=None):
        title = request.data.get('title')
        description = request.data.get('description')

        project = Project.objects.create(
            title=title,
            description=description,
            owner=request.user,
        )
        # '''
        # request:
        # {"title":"New Project","description":"Project Description"}
        # response:
        # {"id":3,"created_date_time":"2018-08-30T14:13:02.721687Z","owner_id":"client","title":"New Project","description":"Project Description"}
        # '''

        response = {
            "id": project.id,
            "created_date_time": project.created_date_time,
            "owner_id": project.owner.username,
            "title": project.title,
            "description": project.description
        }
        return JsonResponse(response, status=201)


class get_project_by_id_handler(APIView):
    authentication_classes = (BearerTokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    parser_classes = (JSONParser, FormParser)

    #
    def get(self, request, project_id=None,format=None):
        # '''
        # request:
        #
        # response:
        # '''

        project = Project.objects.get(id=project_id)

        response = {
            "id": project.id,
            "created_date_time": project.created_date_time,
            "owner_id": project.owner.username,
            "title": project.title,
            "description": project.description
        }
        return JsonResponse(response, status=200)
