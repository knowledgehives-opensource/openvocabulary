# -*- coding: utf-8 -*-
import datetime

from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response

from ov_django.settings import BASE_URL_PATH, BASE_OV_PATH
from ov_django.ov.models import *


"""
Welcome the user
"""
def welcome(request):
    state = "welcome"
    return render_to_response('basic/welcome.html', locals())

"""
List/filter vocabularies
"""
def list_vocabularies(request):
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


"""
Redirects to appropriate service
"""    
def redirect(request, path):
    accept = request.META.get("HTTP_ACCEPT", "")
    needsrdf = re.match("^.*application\/x-turtle.*$", accept) 
    prefix = "data/" if needsrdf else "html/"           
    
    response = HttpResponse(content="", status=303)
    response["Location"] = BASE_URL_PATH + prefix + path
    
    return response


"""
Responds with RDF representation of the resource
"""
def rdfdata(request, path):
    uri = BASE_OV_PATH + path
    result = Entry.objects.lookup(uri) if id != '' else None
    if result:
        return HttpResponse(result.to_rdf(), mimetype="application/x-turtle")
    else:
        raise Http404
