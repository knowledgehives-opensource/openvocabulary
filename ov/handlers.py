#handlers.py
#
#Created by Mateusz Kaczmarek.
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

from piston.handler import BaseHandler
from ov_django.ov.models import Entry, EntryReference
from django.db.models.query_utils import Q
from django.http import HttpResponse
import simplejson as json

# searches all available thesauri in a given language (passed as http request parameter)
# for all synsets with at least one wordsense with a given label
# NOTE - taxonomies (DDC etc.) are not searched by this method, only thesauri with clear synset definition
class SearchAllSynsetsByWordHandler(BaseHandler):
    
    allowed_methods = ('GET')
    model = Entry
    fields = ('id', 'label', 'gloss', 'uri', 'is_root', ('context', ('id', 'uri')));
    
    
    def read(self, request, word):
        """
        part of REST API - searches OV for synsets with a given word (and language); 
        returns all such synsets (as well as their direct parents and children (if they exist) - NOTE:
        currently removed for better performance)
        uri pattern: search/allsynsets/<word_to_search>
        """
            
        # Notice - Django automatically CAPITALIZES and adds "HTTP_" prefix to all GET properties added in Java using setRequestProperty()
        try:   
            lang = request.META["HTTP_LANG"]
        # this is for GET arguments added to the URL
        except KeyError:
            lang = request.GET["lang"]
            
        synsets = list(Entry.objects.filter(context__lang=lang, word_senses__label=word, synset_id__isnull=False))
        
        result = []
        for synset in synsets:
            result.append(synset.prepare_synset_dict())
        
        return HttpResponse(json.dumps(result), mimetype="application/json")


# looks for a synset with at least one wordsense whose label is equal to a given one or an entry (from taxonomy) whose label contains given word
# searches only one given Taxonomy/Thesaurus (passed as request attribute)
# uri pattern: search/synset/<word_to_search>
class SearchSynsetByWordHandler(BaseHandler):
    
    allowed_methods = ('GET')
    model = Entry
    fields = ('id', 'label', 'gloss', 'uri', 'is_root', ('context', ('id', 'uri')));
    
    
    def read(self, request, word):
        try:   
            context_uri = request.META["HTTP_CONTEXT_NAMESPACE"]
        except KeyError:
            context_uri = request.GET["context_namespace"]
            
        synsets = list(Entry.objects.filter(context__uri=context_uri, word_senses__label=word, synset_id__isnull=False))
        if len(synsets) == 0:
            synsets = list(Entry.objects.filter(context__uri=context_uri, label__istartswith=word))
        
        result = []
        for synset in synsets:
            result.append(synset.prepare_synset_dict())
        
        return HttpResponse(json.dumps(result), mimetype="application/json")
    
class GetSynsetForIdHandler(BaseHandler):
    
    allowed_methods = ('GET')
    
    def read(self, request, id):
        synset = Entry.objects.get(pk=id)
        
        result = {'count': 1}
        result['synset1'] = synset
#        result['parent1'] = synset.parent
#        result['children1'] = synset.get_sub_entries()
        
        return result
    
    
class GetPathForIdHandler(BaseHandler):
    
    def read(self, request, id):
        e = Entry.objects.get(pk=id)
        result = {}
        result['id'] = e.id
        parent = e.parent
        i = 0
        while(parent != None):
            i += 1
            result['parent'+i.__str__()] = parent.id
            parent = parent.parent
            
        result['length'] = i
        
        return result

class GetSynsetForUriHandler(BaseHandler):
    
    def read(self, request):
        try:   
            uri = request.META["HTTP_URI"]
        except KeyError:
            uri = request.GET["uri"]
        synset = Entry.objects.get(uri=uri)
        
        result = synset.prepare_synset_dict()
        
        return HttpResponse(json.dumps(result), mimetype="application/json")

    
class SearchRelatedHandler(BaseHandler): 
    
    allowed_methods = ('GET')
    model = EntryReference
    fields = (('subject', ()), 'relation', ('object', ()));
    
    
    def read(self, request, id):
        return EntryReference.objects.filter(Q(subject=id) | Q(object=id))
    
