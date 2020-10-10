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

from easywork.app.models.contract import Contract


class ContractEvent(models.Model):
    title = models.CharField('Title', max_length=1024, null=True, blank=True)

    contract = models.ForeignKey(Contract, related_name='contract_events', null=True, on_delete=models.CASCADE)

    screenshot_filename = models.CharField('Screenshot filename', max_length=1024, null=True, blank=True)
    screenshot_url = models.CharField('Screenshot URL', max_length=1024, null=True, blank=True)

    mouse_events_count = models.IntegerField(default=0)
    keyboard_events_count = models.IntegerField(default=0)

    event_type = models.CharField('Event type', max_length=1024, null=True, blank=True)

    created_date_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_date = models.DateField(null=True, blank=True)
