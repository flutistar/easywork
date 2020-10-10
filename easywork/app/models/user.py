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
from django.utils.translation import ugettext_lazy as _



class MyUserManager(BaseUserManager):
    # Username should exclusively used by social_django
    def create_user(self, email, password=None, auth_method='email', **kwargs):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
                                password=password
                                )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_natural_key(self, username):
        return self.get(email__iexact=username)


class BaseUser(AbstractBaseUser, PermissionsMixin):
    uid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    email = models.CharField(max_length=100, unique=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField('First name', max_length=100, null=True)
    last_name = models.CharField('Last name', max_length=100, null=True)

    user_type = models.CharField('User type', max_length=100, null=True)

    email_verified = models.BooleanField(default=False)


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []



    # @property
    # def is_staff(self):
    #     # Simplest possible answer: All admins are staff
    #     return self.is_admin

    @property
    def get_full_name(self):
        if not self.first_name:
            return self.email.split('@')[0]

        name = self.first_name
        if self.last_name:
            name += ' ' + self.last_name
        return name

    @property
    def created_at(self):
        return self.date_joined

    def get_short_name(self):
        return self.first_name


    def __str__(self):
        return self.email

    def __unicode__(self):
        return self.email

    def save(self, *args, **kwargs):
        super(BaseUser, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _(u"User")
        verbose_name_plural = _(u"Users")
        app_label= 'app'


