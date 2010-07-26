# -*- coding: utf-8 -*-
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
import datetime


"""
Welcome the user
"""
def welcome(request):
    return render_to_response('basic/welcome.html', locals())
