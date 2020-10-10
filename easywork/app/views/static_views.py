# coding=utf-8
from django.shortcuts import redirect


def home(request):
    return redirect('/admin')