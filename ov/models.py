#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
models.py

Created by Sebastian Kruk on .
Copyright (c)  Knowledge Hives sp. z o.o.. All rights reserved.
"""

from django.db import connection, models
from django.contrib import admin
from django.template import RequestContext
from ov_django.rdf import *
from ov_django.settings import BASE_URL_PATH

# --------------------- context -----------------------------    
    
CONTEXT_TYPE = (
    ('tax', 'Taxonomy'),
    ('tez', 'Thesaurus'),
    ('tag', 'Tagging')
)    
DICT_CONTEXT_TYPE = dict(CONTEXT_TYPE)

    
class ContextManager(models.Manager):
    def search(self, key):
        results = [] #Publisher.objects.filter(name__icontains=key) | Publisher.objects.filter(address__icontains=key)
        print "Found %d results for %s" % (len(results), key)
        return results

    """
    Lookup manifests by isbn
    """   
    def lookup(self, value):
        try:
            result = Context.objects.get(uri=value)
        except Exception:
            result = None
        return result
    
    """
    Returns a set of distinctive languages
    """ 
    def get_langs(self):
        cursor = connection.cursor()
        cursor.execute("""
            SELECT DISTINCT lang
            FROM ov_context""")
        return [row[0] for row in cursor]        

"""
Simple class for storing tags
"""
class Tag(models.Model):
    label = models.CharField(max_length=50, db_index=True, unique=True)
    
"""
Represents the dictionary
"""    
class Context(models.Model):
    label = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    uri = models.URLField(max_length=255, verify_exists=False, db_index=True, unique=True)
    ns = models.CharField(max_length=10)
    type = models.CharField(max_length=3, choices=CONTEXT_TYPE, default='tag')
    lang = models.CharField(max_length=10, default='en')
    tags = models.ManyToManyField(Tag, related_name='tag', symmetrical=False, blank=True, null=True)
    term_uri_pattern = models.CharField(max_length=500, blank=True, null=True, verbose_name="uri pattern")
    # additional_properties
    # tree_properties
    objects = ContextManager()
    
    """
    to-string representation
    """
    def __unicode__(self):
        return "%s [%s]" % (self.label, self.uri)

    '''
    Returns roots of this context
    '''
    def get_root_entries(self):
        return Entry.objects.filter(is_root=True, context=self)

    """
    Django meta information
    """
    class Meta:
        ordering = ['label']
        
              
class ContextAdmin(admin.ModelAdmin):
#    readonly_fields = ('uid',)
    list_display = ('label', 'description', 'uri', 'ns', 'type', 'lang', 'term_uri_pattern',)
    list_filter = ('label', 'type', 'lang',)
    fieldsets = (
            ('text', {
                'fields': ('label', 'description'),
                'classes': ('basic',),
                'description': ("Provide basic information about the context"),
            }),
            ('uri', {
                'fields': ('uri', 'ns', 'term_uri_pattern'),
                'classes': ('basic',),
                'description': ("URI-based information"),
            }),
            ('meta', {
                'fields': ('type', 'lang'),
                'classes': ('basic',),
                'description': ("Additional meta information"),
            }),
    )

# --------------------- URI -----------------------------    

class URIManager(models.Manager):
    def search(self, key):
        results = [] #Publisher.objects.filter(name__icontains=key) | Publisher.objects.filter(address__icontains=key)
        print "Found %d results for %s" % (len(results), key)
        return results

    """
    Lookup manifests by isbn
    """   
    def lookup(self, value):
        try:
            result = URI.objects.get(uri=value)
        except Exception:
            result = None
        return result
    
"""
Represents an arbitrary URI
"""    
class URI(models.Model):
    uri = models.URLField(max_length=255, verify_exists=False, db_index=True, unique=True)
    objects = URIManager()
    
    """
    to-string representation
    """
    def __unicode__(self):
        return "<%s>" % self.uri

              
class URIAdmin(admin.ModelAdmin):
    pass

# --------------------- Predicate -----------------------------    

class PredicateManager(models.Manager):
    def search(self, key):
        results = [] #Publisher.objects.filter(name__icontains=key) | Publisher.objects.filter(address__icontains=key)
        print "Found %d results for %s" % (len(results), key)
        return results

    """
    Lookup manifests by isbn
    """   
    def lookup(self, value):
        try:
            result = Predicate.objects.get(uri=value)
        except Exception:
            result = None
        return result

"""
Represents an arbitrary URI
"""    
class Predicate(models.Model):
    uri = models.URLField(max_length=255, verify_exists=True, db_index=True, unique=True)
    objects = PredicateManager()

    """
    to-string representation
    """
    def __unicode__(self):
        return "<%s>" % self.uri


class URIAdmin(admin.ModelAdmin):
    pass




# --------------------- entry -----------------------------    

PART_OF_SPEECH = (
    ('adj', 'adjective'),
	('sat', 'adjectivesatellite'),
	('adv', 'adverb'),
	('noun', 'noun'),
	('verb', 'verb'),
	('none', 'unknown'),
)

ENTRY_RELATION_TYPES = (
    ('hyponym', 'hyponym'),
    ('hypernym', 'hypernym'),
    ('antonym', 'antonym'),
    ('synonym', 'synonym'),
    ('meaning', 'meaning'),
    ('meronymOf', 'meronym of'),
    ('partMeronymOf', 'part meronym of'),
    ('similarTo', 'similar to'),
    ('adverbPertainsTo', 'adverb pertains to'),
    ('adjectivePertainsTo', 'adjective pertains to'),
    ('attribute', 'attribute'),
    ('causes', 'causes'),
    ('derivationallyRelated', 'derivationally related'),
    ('entails', 'entails'),
    ('participleOf', 'participle of'),
    ('sameVerbGroupAs', 'same verb group as'),
    ('substanceMeronymOf', 'substance meronym of'),
    ('memberMeronymOf', 'member meronym of'),
    ('classifiedByRegion', 'classified by region'),
    ('classifiedByTopic', 'classified by topic'),
    ('classifiedByUsage', 'classified by usage'),
)



class EntryManager(models.Manager):
    def search(self, key, value):
        results = Entry.objects.get(label__icontains=value) #Publisher.objects.filter(name__icontains=key) | Publisher.objects.filter(address__icontains=key)
        print "Found %d results for %s=%s" % (len(results), key, value)
        return results

    """
    Lookup manifests by isbn
    """   
    def lookup(self, value):
        try:
            result = Entry.objects.get(uri=value)
        except Exception:
            result = None
        return result

"""
Represents the dictionary entry
"""    
class Entry(models.Model):
    label = models.CharField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)
    uri = models.URLField(max_length=255, verify_exists=False, db_index=True, unique=True)
    context = models.ForeignKey(Context, null=True)
    is_root = models.BooleanField(default=False)
    # -- thesaurus --
    relations = models.ManyToManyField('self', related_name='relation', symmetrical=False, through='EntryReference', blank=True, null=True)
    meanings  = models.ManyToManyField('self', related_name='meaning', symmetrical=False, blank=True, null=True)
    frame = models.CharField(max_length=255, blank=True, null=True)
    # -- word --
    lexical_form = models.CharField(max_length=255, blank=True, null=True)
    # -- word sense --
    in_synset = models.ForeignKey('self', related_name='inSynset', blank=True, null=True)
    tag_count = models.IntegerField(blank=True, null=True) #the tagcount value for word net
    words = models.ManyToManyField('self', related_name='word', symmetrical=False, blank=True, null=True)
    type_tag = models.CharField(max_length=50, blank=True, null=True)
    # -- synset --
    gloss = models.TextField(blank=True, null=True)
    synset_id = models.CharField(max_length=100, blank=True, null=True)
    pos = models.CharField(max_length=10, choices=PART_OF_SPEECH) #part of speech
    word_senses = models.ManyToManyField('self', related_name='wordSense', symmetrical=False) # --> containsWordSense, <-- inWordSense
    # -- taxonomy --
    parent = models.ForeignKey('self', related_name='childOf', blank=True, null=True)
    #
    triples = models.ManyToManyField(Predicate, related_name='triples', symmetrical=False, through='Triple', blank=True, null=True) 
    types = models.ManyToManyField(URI, related_name='types', symmetrical=False, blank=True, null=True)
    #
    objects = EntryManager()

    """
    to-string representation
    """
    def __unicode__(self):
        if self.context:
            if self.type_tag:
                return "%s (%s) [%s | %s]" % (self.get_label(), self.type_tag, self.uri, self.context.label)
            else:
                return "%s [%s | %s]" % (self.get_label(), self.uri, self.context.label)
        else:
            return "%s [%s | !!!]" % (self.get_label(), self.uri)
    
    """
    Returns array of entries that are children of this one in the tree
    """
    def get_sub_entries(self):
        return [] #TODO
        
    """
    Returns path from Root to this entry
    """
    def get_path_from_root(self):
        return [] #TODO    
        
    """
    Return all entries below this entry
    """
    def get_descendants(self):
        return [] #TODO

    """
    set of {@link WordSenseEntity} objects related to this <code>WordEntity</code> 
    through inverse property of <code>http://www.w3.org/2006/03/wn/wn20/schema/word</code>
    """
    def get_in_word_sense(self):
        return []; #TODO

    def get_label(self):
        return self.lexical_form if self.lexical_form else self.label

    """
    Django meta information
    """
    class Meta:
        ordering = ['label']
        verbose_name_plural = "entries"

"""
Allows to define multiple references between dictionary entries
"""
class EntryReference(models.Model):
    subject = models.ForeignKey(Entry, related_name='ref_subject')
    object = models.ForeignKey(Entry, related_name='ref_object')
    relation = models.CharField(max_length=30, choices=ENTRY_RELATION_TYPES)

"""
M2M relation based on triples concept
"""
class Triple(models.Model):
    subject = models.ForeignKey(Entry, related_name='triple_subject')
    predicate = models.ForeignKey(Predicate, related_name='triple_predicate')
    object = models.ForeignKey(URI, related_name='triple_object', null=True, blank=True)
    literal = models.CharField(max_length=1000, null=True, blank=True)
    literal_type = models.ForeignKey(URI, related_name='triple_literal_type', null=True, blank=True)
    literal_lang = models.CharField(max_length=10, null=True, blank=True)


class EntryAdmin(admin.ModelAdmin):
#    readonly_fields = ('uid',)
    pass