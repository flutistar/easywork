# coding=utf-8

from django.db import models
from easywork.app.models import BaseUser


class Project(models.Model):
    title = models.CharField('Title', max_length=1024, null=True, blank=True)
    description = models.TextField('Description', null=True, blank=True)
    owner = models.ForeignKey(BaseUser, related_name='projects', null=True, on_delete=models.CASCADE)
    created_date_time = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "{}".format(self.title)

    def __str__(self):
        return "{}".format(self.title)
