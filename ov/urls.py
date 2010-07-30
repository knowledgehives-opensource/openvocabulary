# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('ov_django.ov.views',
    (r'^$',                                             'welcome'),
    (r'vocabularies[/]?$',                              'list_vocabularies'),
    (r'vocabularies/search$',                           'search_concepts'),
    (r'vocabularies/lookup$',                           'lookup_concept'),
    (r'html/(?P<path>(?:taxonomies|thesauri)[/].+)$',   'lookup_concept'),
    (r'data/(?P<path>(?:taxonomies|thesauri)[/].+)',    'rdfdata'),
    (r'(?P<path>(?:taxonomies|thesauri)[/].+)',         'redirect'),
#    (r'search/(books|creators|publishers|expressions)', 'search'),
#    (r'id/(?P<path>books/(?:isbn|sku)/[\d\w-]+)', 'redirect'),
#    (r'id/(?P<path>(?:creators|publishers|expressions)/[\d\w-]+)', 'redirect'),
#    (r'data/(?P<type>books)/(?P<key>isbn|sku)/(?P<id>[\d\w-]+)', 'rdfdata'),
#    (r'data/(?P<type>creators|publishers|expressions)/(?P<id>[\d\w-]+)', 'rdfdata'),
#    (r'(?P<path>(?P<type>books)/(?P<key>isbn|sku)/(?P<id>[\d\w-]+))', 'lookup'),
#    (r'(?P<path>(?P<type>creators|publishers|expressions)/(?P<id>[\d\w-]+))', 'lookup'),
)
