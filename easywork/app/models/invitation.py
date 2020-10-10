# coding=utf-8

import uuid
from datetime import datetime, timezone

import random
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from easywork.app.models import BaseUser, Project
from easywork.app.models.term import Term


class Invitation(models.Model):
    owner = models.ForeignKey(BaseUser, related_name='invitations_sent', null=True, on_delete=models.CASCADE)
    invitee = models.ForeignKey(BaseUser, related_name='invitations_received', null=True, on_delete=models.CASCADE)

    project = models.ForeignKey(Project, related_name='invitations', null=True, on_delete=models.CASCADE)

    invitee_email =  models.CharField('Invitee emails', max_length=1024, default="", blank=True)

    status = models.CharField('Status', max_length=1024, default="pending")

    terms = models.ForeignKey(Term, related_name='invitations', null=True, on_delete=models.CASCADE)

    created_date_time = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)