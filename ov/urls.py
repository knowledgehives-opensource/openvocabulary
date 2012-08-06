#urls.py
#
#Created by Sebastian Kruk.
#Copyright (c) 2011, KnowledgeHives sp. z o.o
#
#This file is part of OpenVocabulary.
#
#OpenVocabulary is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#OpenVocabulary is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.
#
#You should have received a copy of the GNU Affero General Public License
#along with OpenVocabulary.  If not, see <http://www.gnu.org/licenses/>.
#
#IMPORTANT:
#1) In addition to the terms and conditions defined in the GNU Affero 
#General Public License you agree to use this software to provide access 
#to vocabularies, i.e., thesauri, taxonomies, and such, ONLY through 
#a generally available end-point.
#2) You will also notify the copyright owners, i.e., Knowledge Hives 
#sp. z o.o., via email at info@knowledgehives.com, about the address 
#of end-point you have setup using this software.
#3) Finally, you need to ensure that the vocabularies managed using this 
#software are correctly indexed by the Sindice semantic index service; 
#we suggest using semantic sitemap protocol in oder to do so.
#
#See http://opensource.knowledgehives.com/wiki/OpenVocabulary 
#for more information

from django.conf.urls.defaults import *
from piston.resource import Resource
from ov_django.ov.handlers import *

urlpatterns = patterns('ov_django.ov.views',
	(r'^$', 'welcome'),
	(r'vocabularies[/]?$', 'list_vocabularies'),
	(r'vocabularies/search$', 'search_concepts'),
	(r'vocabularies/lookup$', 'lookup_concept'),
	(r'html/(?P<path>(?:taxonomies|thesauri)[/].+)$', 'lookup_concept'),
	(r'data/(?P<path>(?:taxonomies|thesauri)[/].+)', 'rdfdata'),
	(r'(?P<path>(?:taxonomies|thesauri)[/].+)', 'redirect'),
)

class CsrfExemptResource(Resource):
	"""
	A work-around for allowing REST POST, PUT and DELETE methods (normally they would be
	disabled by Django's cross-site request forgery discovery module (at least that's what they
	are writing on the Internet - http://www.robertshady.com/content/creating-very-basic-api-using-python-django-and-piston)
	"""
	def __init__(self, handler, authentication=None):
		super(CsrfExemptResource, self).__init__(handler, authentication)
		self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

searchSynsetByWord = CsrfExemptResource(SearchSynsetByWordHandler)
searchAllSynsetsByWord = CsrfExemptResource(SearchAllSynsetsByWordHandler)
searchRelated = CsrfExemptResource(SearchRelatedHandler)
getSynsetForId = CsrfExemptResource(GetSynsetForIdHandler)
getPathForId = CsrfExemptResource(GetPathForIdHandler)
getSynsetForUri = CsrfExemptResource(GetSynsetForUriHandler)

"""
URL patterns for REST API. It uses Piston API (http://bitbucket.org/jespern/django-piston).
The default response serialization is JSON. To use different serialization add third argument like:
{ 'emitter_format': 'xml' }
"""
urlpatterns += patterns('',
	(r'search/synset/(?P<word>.+)[/]?$', searchSynsetByWord),
	(r'search/allsynsets/(?P<word>.+)[/]?$', searchAllSynsetsByWord),
	(r'search/related/(?P<id>\d+)[/]?$', searchRelated),
	(r'get/id/(?P<id>\d+)[/]?$', getSynsetForId),
	(r'get/path/(?P<id>\d+)[/]?$', getPathForId),
	(r'get/uri[/]?$', getSynsetForUri),
)
