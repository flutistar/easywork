# coding=utf-8

import uuid
from datetime import datetime, timezone, timedelta

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


class Contract(models.Model):
    project = models.ForeignKey(Project, related_name='contracts', null=True, on_delete=models.CASCADE)

    contractor = models.ForeignKey(BaseUser, related_name='contracts_as_contractor', null=True, on_delete=models.CASCADE)
    owner = models.ForeignKey(BaseUser, related_name='contracts_owned', null=True, on_delete=models.CASCADE)

    terms = models.ForeignKey(Term, related_name='contracts', null=True, on_delete=models.CASCADE)

    status = models.CharField('Status', max_length=1024, null=True, blank=True)
    '''
    contract_started -> started
    invitation_pending
    contract_paused -> paused
    contract_ended -> ended
    none
    '''

    agent_first_name = models.CharField('Agent First Name', max_length=1024, null=True, blank=True)
    agent_last_name = models.CharField('Agent Last Name', max_length=1024, null=True, blank=True)
    last_date_worked = models.DateTimeField(null=True, blank=True)
    # weekly_limit = models.IntegerField(null=True,blank=True) NOT Necessary term.weekly_limit_in_hours

    # last_week_value = models.IntegerField(null=True,blank=True) Not necessary, calculated
    # last_day_value = models.IntegerField(null=True,blank=True) Not necessary, calculated


    created_date_time = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def last_date_worked(self):
        if self.totals.count() > 0:
            return self.totals.last().date
        else:

            return ""

    @property
    def last_date_value(self):
        if self.totals.count() > 0:
            return self.totals.last().get_value
        else:
            return 0

    @property
    def week_limit(self):
        return self.terms.weekly_limit_in_hours

    @property
    def current_week_value(self):
        today = datetime.now().date()
        last_monday = today - timedelta(days=today.weekday())
        cdate = last_monday
        total_value = 0
        while (cdate <= today):
            # print(cdate)
            totals = self.totals.filter(date=cdate)
            if totals.count() > 0:
                total_value += totals.first().get_value
            else:
                # TODO: This shouldn't be necessary because the total should be created when an event isn't in any day
                total = DayTotal.objects.create(date=cdate, contract=self)
                total_value += total.get_value
                # TODO: END

            cdate = cdate + timedelta(days=1)

        return total_value

    @property
    def last_week_value(self):
        today = datetime.now().date()
        last_monday = today - timedelta(days=today.weekday() + 7)
        end_sunday = today - timedelta(days=today.weekday() + 1)
        cdate = last_monday
        total_value = 0
        while (cdate <= end_sunday):
            # print(cdate)

            totals = self.totals.filter(date=cdate)
            if totals.count() > 0:
                total_value += totals.first().get_value
            else:
                # TODO: This shouldn't be necessary because the total should be created when an event isn't in any day
                total = DayTotal.objects.create(date=cdate, contract=self)
                total_value += total.get_value
                # TODO: END

            cdate = cdate + timedelta(days=1)
        return total_value

    @property
    def last_day_value(self):
        return 0

    @property
    def today_value(self):
        today = datetime.now().date()
        totals = self.totals.filter(date=today)

        if totals.count() == 0:
            # TODO: This shouldn't be necessary because the total should be created when an event isn't in any day
            total = DayTotal.objects.create(date=today, contract=self)
            return total.get_value
            # TODO: END
            # return 0
        else:
            return totals[0].get_value

    @property
    def all_time_value(self):
        today = datetime.now().date()
        cdate = self.created_date_time.date()
        total_value = 0
        while (cdate <= today):
            cdate = cdate + timedelta(days=1)

            totals = self.totals.filter(date=cdate)
            if totals.count() > 0:
                total_value += totals.first().get_value
        return total_value

    def __unicode__(self):
        return "{} - {} - {} ({})".format(self.project, self.owner, self.contractor, self.status)

    def __str__(self):
        return "{} - {} - {} ({})".format(self.project, self.owner, self.contractor, self.status)

class DayTotal(models.Model):
    date = models.DateField(null=True, blank=True)
    value = models.IntegerField(default=0)
    contract = models.ForeignKey(Contract, related_name='totals', null=True, on_delete=models.CASCADE)

    @property
    def get_value(self):
        from easywork.app.models.contract_event import ContractEvent
        today = datetime.now().date()
        if self.value != 0 and today != self.date:
            return self.value

        sum = 0
        for ce in ContractEvent.objects.filter(created_date=self.date, contract=self.contract):
            sum += 10

        self.value = sum
        self.save()
        # print("totals saved")
        return sum

    def __unicode__(self):
        return "{} - {}".format(self.date, self.value)

    def __str__(self):
        return "{} - {}".format(self.date, self.value)
