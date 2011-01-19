# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from piston.resource import Resource
from ov_django.ov.handlers import *

urlpatterns = patterns('ov_django.ov.views',
    (r'^$', 'welcome'),
    (r'vocabularies[/]?$', 'list_vocabularies'),
    (r'vocabularies/search$', 'search_concepts'), #include('haystack.urls')), #'search_concepts'),
    (r'vocabularies/lookup$', 'lookup_concept'),
    (r'html/(?P<path>(?:taxonomies|thesauri)[/].+)$', 'lookup_concept'),
    (r'data/(?P<path>(?:taxonomies|thesauri)[/].+)', 'rdfdata'),
#    (r'json/(?P<path>(?:taxonomies|thesauri)[/].+)',    'rdfdata'),
    (r'(?P<path>(?:taxonomies|thesauri)[/].+)', 'redirect'),
#    (r'search/(books|creators|publishers|expressions)', 'search'),
#    (r'id/(?P<path>books/(?:isbn|sku)/[\d\w-]+)', 'redirect'),
#    (r'id/(?P<path>(?:creators|publishers|expressions)/[\d\w-]+)', 'redirect'),
#    (r'data/(?P<type>books)/(?P<key>isbn|sku)/(?P<id>[\d\w-]+)', 'rdfdata'),
#    (r'data/(?P<type>creators|publishers|expressions)/(?P<id>[\d\w-]+)', 'rdfdata'),
#    (r'(?P<path>(?P<type>books)/(?P<key>isbn|sku)/(?P<id>[\d\w-]+))', 'lookup'),
#    (r'(?P<path>(?P<type>creators|publishers|expressions)/(?P<id>[\d\w-]+))', 'lookup'),
)

"""
A work-around for allowing REST POST, PUT and DELETE methods (normally they would be
disabled by Django's cross-site request forgery discovery module (at least that's what they
are writing on the Internet - http://www.robertshady.com/content/creating-very-basic-api-using-python-django-and-piston) 
"""
class CsrfExemptResource(Resource):
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

searchSynsetByWord = CsrfExemptResource(SearchSynsetByWordHandler)
searchRelated = CsrfExemptResource(SearchRelated)
getSynsetForId = CsrfExemptResource(GetSynsetForId)
getPathForId = CsrfExemptResource(GetPathForId)

"""
URL patterns for REST API. It uses Piston API (http://bitbucket.org/jespern/django-piston).
The default response serialization is JSON. To use different serialization add third argument like:
{ 'emitter_format': 'xml' }
"""
urlpatterns += patterns('',
    (r'search/synset/(?P<word>.+)[/]?$', searchSynsetByWord),
    (r'search/related/(?P<id>\d+)[/]?$', searchRelated),
    (r'get/id/(?P<id>\d+)[/]?$', getSynsetForId),
     (r'get/path/(?P<id>\d+)[/]?$', getPathForId)
)
