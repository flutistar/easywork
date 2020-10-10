# coding=utf-8
from django.shortcuts import redirect, render


def home(request):
    return render(request,'index.html')