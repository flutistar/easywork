# coding=utf-8
from rest_framework import serializers

from  easywork.app.models import BaseUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BaseUser
        fields = ('id', 'email', 'get_full_name', 'first_name', 'last_name')