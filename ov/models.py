#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
models.py

Created by Sebastian Kruk on .
Copyright (c)  Knowledge Hives sp. z o.o.. All rights reserved.
"""

from django.db import models
from django.contrib import admin
from ov_django.rdf import RdfClass
from ov_django.rdf import URI as RdfURI

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
#		cursor = connection.cursor()
#		cursor.execute("""
#			SELECT DISTINCT lang
#			FROM ov_context""")
		langs = Context.objects.values('lang').distinct(True).order_by()
		return [lang['lang'] for lang in langs]

"""
Simple class for storing tags
"""
class Tag(models.Model):
	label = models.CharField(max_length=50, db_index=True, unique=True)

"""
Represents the dictionary
"""    
class Context(models.Model, RdfClass):
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


	# -------- RdfClass --------

	"""
	Metainformation for RDF output
	"""
	def rdfMeta(self):
		return {
			'label' 		: {'uri' : [ RdfURI('skos:prefLabel'), RdfURI('dcel:title') ] },
			'description' : {'uri' : [ RdfURI('v:description'), RdfURI('dcel:description'), RdfURI('rev:text'), RdfURI('bibtex:abstract') ] },
			'info' 		: {'uri' : [ RdfURI('v:summary'), RdfURI('dcel:description'), RdfURI('rev:text'), RdfURI('bibtex:note') ] },
			'lang' 		: {'uri' : 'dcel:language' },
			'tags' 		: {'uri' : ['skos:topic', 'dcel:subject'] },
			  }

	"""
	Override RdfClass default uri implementation
	"""
	def get_uri(self):
		return self.uri

	"""
	Override RdfClass default rdf:type listing
	"""
	def get_rdf_types(self):
		return [ RdfURI('skos:ConceptScheme') ]


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
	label = models.CharField(max_length=100, null=True, blank=True)
	objects = URIManager()

	"""
	to-string representation
	"""
	def __unicode__(self):
		if self.label:
			return "%s <%s>" % (self.label, self.uri)
		else:
			return "<%s>" % (self.uri)


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
	label = models.CharField(max_length=100, null=True, blank=True)
	objects = PredicateManager()

	"""
	to-string representation
	"""
	def __unicode__(self):
		if self.label:
			return "%s <%s>" % (self.label, self.uri)
		else:
			return "<%s>" % (self.uri)




# --------------------- entry -----------------------------    

PART_OF_SPEECH = (
	('adj', 'Adjective'),
	('sat', 'Adjective Satellite'),
	('adv', 'Adverb'),
	('noun', 'Noun'),
	('verb', 'Verb'),
	('none', 'Unknown'),
)
DICT_PART_OF_SPEECH = dict(PART_OF_SPEECH)

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
DICT_ENTRY_RELATION_TYPES = dict(ENTRY_RELATION_TYPES)



class EntryManager(models.Manager):
	def search(self, key, value):
		results = Entry.objects.get(label__icontains=value) #Publisher.objects.filter(name__icontains=key) | Publisher.objects.filter(address__icontains=key)
		print "Found %d results for %s=%s" % (len(results), key, value)
		return results

	def lookup(self, value):
		"""
		Lookup manifests by isbn
		"""
		try:
			result = Entry.objects.get(uri=value)
		except Exception:
			result = None
		return result

class Entry(models.Model, RdfClass):
	"""
	Represents the dictionary entry
	"""
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

	def __unicode__(self):
		"""
		to-string representation
		"""
		if self.context:
			if self.type_tag:
				return "%s (%s) [%s | %s]" % (self.get_label(), self.type_tag, self.uri, self.context.label)
			else:
				return "%s [%s | %s]" % (self.get_label(), self.uri, self.context.label)
		else:
			return "%s [%s | !!!]" % (self.get_label(), self.uri)

	def get_sub_entries(self):
		"""
		Returns array of entries that are children of this one in the tree
		"""
		return Entry.objects.filter(parent=self)

	def get_path_from_root(self):
		"""
		Returns path from Root to this entry
		"""
		return [] #TODO

	def get_descendants(self):
		"""
		Return all entries below this entry
		"""
		return [] #TODO

	def get_in_word_sense(self):
		"""
		set of {@link WordSenseEntity} objects related to this <code>WordEntity</code>
		through inverse property of <code>http://www.w3.org/2006/03/wn/wn20/schema/word</code>
		"""
		return Entry.objects.filter(words__contains=self)

	def get_label(self):
		if self.lexical_form:
			return self.lexical_form
		if self.label:
			return self.label
		return self.uri

	def get_description(self):
		if self.description:
			return self.description
		if self.gloss:
			return self.gloss
		if self.in_synset:
			return self.in_synset.gloss
		return ""

	class Meta:
		"""
		Django meta information
		"""
		ordering = ['label']
		verbose_name_plural = "entries"

	# -------- RdfClass --------

	def rdfMeta(self):
		"""
		Metainformation for RDF output
		"""
		return {
			'label' 		: {'uri' : [ RdfURI('skos:prefLabel'), RdfURI('dcel:title') ] },
			'description' : {'uri' : [ RdfURI('v:description'), RdfURI('dcel:description'), RdfURI('rev:text'), RdfURI('bibtex:abstract') ], 'property' : 'get_description' },
			'context' 		: {'uri' : 'skos:inScheme', 'condition' : ('is_root', False) },
			'top_concept' 	: {'uri' : 'skos:topConceptOf', 'condition' : ('is_root', True), 'property' : 'context' },
			'type_tag' 	    : {'uri' : 'ov:wordType', 'uri_pattern': 'ov:I%s' },
		    'word_senses'   : {'uri' : 'wn20schema:containsWordSense', 'condition': ('in_synset', None)},
		    'in_synset'     : {'uri' : 'wn20schema:inSynset'},
		    'parent'        : {'uri' : [ RdfURI('skos:broader') ]},
		    'childOf'       : {'uri' : [ RdfURI('skos:narrower')]},
			#'is_root' 	: {'uri' : 'dcel:language' },
			#'relations' 	: {'uri' : 'skos:inScheme' },
			#'meanings' 	: {'uri' : 'skos:inScheme' },
			#'frame' 	: {'uri' : 'skos:inScheme' },
			#'lexical_form': {'uri' : [ RdfURI('skos:prefLabel'), RdfURI('dcel:title') ] },
			#'in_synset' 	: {'uri' : 'skos:inScheme' },
			#'tag_count' 	: {'uri' : 'skos:inScheme' },
			#'words' 	: {'uri' : 'skos:inScheme' },
			  }
	"""
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
	"""


	"""
	Override RdfClass default uri implementation
	"""
	def get_uri(self):
		return self.uri

	"""
	Override RdfClass default rdf:type listing
	"""
	def get_rdf_types(self):
		return [ RdfURI('skos:Concept') ]


"""
Allows to define multiple references between dictionary entries
"""
class EntryReference(models.Model):
	subject = models.ForeignKey(Entry, related_name='ref_subject')
	object = models.ForeignKey(Entry, related_name='ref_object')
	relation = models.CharField(max_length=30, choices=ENTRY_RELATION_TYPES)

	"""
	to-string representation
	"""
	def __unicode__(self):
		return "%s (%s) %s" % (self.subject.get_label(), self.relation, self.object.get_label())

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