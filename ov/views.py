# -*- coding: utf-8 -*-
import datetime
import re
from exceptions import NotImplementedError

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404, HttpResponseNotFound
from django.shortcuts import render_to_response
from django.db.models import Q
from django.core import serializers


from ov_django.settings import BASE_URL_PATH, BASE_OV_PATH
from ov_django.ov.models import *
from ov_django import settings
from simplejson import dumps



def welcome(request):
    """
    Welcome the user
    """
    state = "welcome"
    return render_to_response('basic/welcome.html', locals())

def list_vocabularies(request):
    """
    List/filter vocabularies
    """
    state = "vocabularies"
    tag = request.GET.get('tag', None)
    type = request.GET.get('type', None)
    lang = request.GET.get('lang', None)
    uri = request.GET.get('uri', None)
    
    langs = Context.objects.get_langs()
    tags = Tag.objects.values_list('label', flat=True)
    
    results = None
    if tag:
        results = Context.objects.filter(tags__label__exact=tag)
    elif type:
        results = Context.objects.filter(type=type)
    elif lang:
        results = Context.objects.filter(lang=lang)
    elif uri:
        results = Context.objects.filter(uri=uri)
        page = int(request.GET.get('page', 0))
        pstart = 10*page
        pend = 10*(page+1)-1
        pagep1 = page+1
        pagem1 = page-1
        pten = 10*(page+1)
        for result in results:
            result.roots = result.get_root_entries()[pstart:pend]
    else:
        results = Context.objects.all()
    
    return render_to_response('basic/vocabularies.html', locals())

"""
Concepts search
"""
def search_concepts(request):
    from haystack.views import SearchView
    state = "search"
    return SearchView(template='search/search.html')(request)    
    # query = request.GET.get('q', '')
    # label = request.GET.get('label', '')
    # size  = request.GET.get('size', 5)
    # threshold = request.GET.get('threshold', 0.5)
    # results = Entry.objects.search(query) if query != '' else []
    # site_name = request.get_host()
    # return render_to_response('basic/search.html', locals())#, mimetype="application/xhtml+xml")

"""
Concepts lookup
"""
def lookup_concept(request, path=None):
    state = "lookup"
    accept = request.META.get("HTTP_ACCEPT", "")
    entry = None
    if path:
        uri = BASE_OV_PATH + path
    else:
        uri = request.GET.get('uri', None)
    if uri:
        entry = Entry.objects.lookup(uri)
    site_name = request.get_host()
    return render_to_response('basic/lookup.html', locals())#, mimetype="application/xhtml+xml")


def redirect(request, path):
    """
    Redirects to appropriate service
    """
    accept = request.META.get("HTTP_ACCEPT", "")
    needsrdf = re.match("^.*application\/x-turtle.*$", accept) 
    prefix = "data/" if needsrdf else "html/"           
    
    response = HttpResponse(content="", status=303)
    response["Location"] = BASE_URL_PATH + prefix + path
    
    return response


def rdfdata(request, path):
    """
    Responds with RDF representation of the resource
    """
    uri = BASE_OV_PATH + path
    result = Entry.objects.lookup(uri) if id != '' else None
    if result:
        return HttpResponse(result.to_rdf(), mimetype="application/x-turtle")
    else:
        raise Http404
    

def search_label(request, label):
    "part of REST API - searches OV for entries with given label (and language); uri pattern: search/label/<label_to_search>"
    accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', None)
    if accept_encoding is None:
        accept_encoding = settings.DEFAULT_SERIALIZATION_TYPE
        
    if request.method == "GET":
        lang = request.META["HTTP_LANG"]
        results = Entry.objects.filter(Q(lexical_form__iexact=label) | Q(label__iexact=label)).filter(context__lang=lang)
        if results:
            response = HttpResponse(dumps(results[0].uri), content_type=accept_encoding)
        else:
            response = HttpResponseNotFound();
        return response 
    elif request.method == "POST": #TODO Handling user authentication etc.
        print request.POST.lists()
    else:
        raise NotImplementedError
        
        
    
