# coding=utf-8
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from easywork.app.models import Contract, Project, Invitation, ContractEvent, DayTotal
from  easywork.app.models.user import BaseUser
from django.contrib.auth.forms import UserChangeForm
admin.site.site_header = 'Easy Work'

class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = BaseUser


class BaseUserAdmin(UserAdmin):
    form = MyUserChangeForm
    list_display = (
        'pk', 'email', 'username', 'first_name', 'last_name', 'date_joined', 'is_staff',
        'last_login', 'user_type')
    # , 'invitations_sent_num', 'invitations_opened_num', 'projects_num')
    list_filter = ['is_staff']
    search_fields = ['email', 'first_name', 'last_name']


class DayTotalInline(admin.TabularInline):
    model = DayTotal
    extra = 0


class ContractEventInline(admin.TabularInline):
    model = ContractEvent
    extra = 0


class ContractAdmin(admin.ModelAdmin):
    inlines = [ContractEventInline, DayTotalInline]
    list_display = (
        'pk', 'project', 'contractor', 'owner', 'agent_first_name', 'agent_last_name', 'last_date_worked',
        'created_date_time', 'status')


class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'title', 'description', 'owner', 'created_date_time')


class InvitationAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'owner', 'invitee', 'project', 'invitee_email', 'status', 'terms',
        'created_date_time')


class DayTotalAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'date', 'value', 'contract')


admin.site.register(DayTotal, DayTotalAdmin)

admin.site.register(BaseUser, BaseUserAdmin)

admin.site.register(Contract, ContractAdmin)

admin.site.register(Project, ProjectAdmin)

admin.site.register(Invitation, InvitationAdmin)
