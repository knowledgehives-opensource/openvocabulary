#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
importer.py

Created by Sebastian Kruk on .
Copyright (c)  Knowledge Hives sp. z o.o.. All rights reserved.
"""

import sys
import os
import re
import gc
import codecs
import time
import datetime
import fileinput
from django import db
from ov_django.ov.models import *
from django.utils.encoding import smart_unicode

"""
Reads configuration from the RDF triples
"""
class TriplesParser:
	#    <http://dmoz.org/rdf/narrow1>
	#    <http://dmoz.org/rdf/narrow2>
	#    <http://dmoz.org/rdf/narrow>
	#    <http://www.w3.org/2004/02/skos/core#broader>
	#    <http://www.w3.org/2004/02/skos/core#inScheme>
	#    <http://www.w3.org/2004/02/skos/core#narrower>
	#    <http://www.w3.org/2006/03/wn/wn20/schema/containsWordSense>
	_actions = {
		'http://www.w3.org/2004/02/skos/core#inScheme'    : 'set_scheme',
		'http://www.w3.org/2004/02/skos/core#broader'     : 'add_broader',
		'http://www.w3.org/2004/02/skos/core#narrower'    : 'add_narrower',
		'http://dmoz.org/rdf/narrow'                      : 'add_narrower',
		'http://dmoz.org/rdf/narrow1'                     : 'add_narrower',
		'http://dmoz.org/rdf/narrow2'                     : 'add_narrower',
		'http://www.openvocabulary.info/ontology/x-broader' : 'add_broader',
		'http://www.openvocabulary.info/ontology/x-narrower' : 'add_narrower',
		'http://www.w3.org/2004/02/skos/core#hasTopConcept': 'mark_as_root',
		'http://www.openvocabulary.info/ontology/wordType' : 'set_type_tag',
	}
	#    <http://www.w3.org/2006/03/wn/wn20/schema/containsWordSense>
	#    <http://www.w3.org/2006/03/wn/wn20/schema/word>
	#    <http://www.openvocabulary.info/ontology/hasMeaning>
	_entry_actions = {
		'http://www.w3.org/2006/03/wn/wn20/schema/containsWordSense' : 'word_senses', #-in_synset ...
		'http://www.w3.org/2006/03/wn/wn20/schema/word'              : 'words',
		'http://www.openvocabulary.info/ontology/hasMeaning'         : 'meanings', #deprecagted - use inSynset instead
	    'http://www.w3.org/2006/03/wn/wn20/schema/inSynset'          : 'in_synset',
	}
	#    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>
	_uri_actions = {
		'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' : 'types',
				   }
	#    <http://www.w3.org/2004/02/skos/core#prefLabel>
	#    <http://www.w3.org/2000/01/rdf-schema#label>
	#    <http://www.w3.org/2004/02/skos/core#definition>
	#    <http://purl.org/dc/elements/1.0/Title>
	#    <http://purl.org/dc/elements/1.0/Description>
	#    <http://www.w3.org/2006/03/wn/wn20/schema/gloss>
	#    <http://www.w3.org/2006/03/wn/wn20/schema/synsetId>
	#    <http://www.w3.org/2006/03/wn/wn20/schema/lexicalForm>
	#    <http://www.w3.org/2006/03/wn/wn20/schema/tagCount>
	_literal_actions = {
		'http://www.w3.org/2000/01/rdf-schema#label'      : 'label',
		'http://www.w3.org/2004/02/skos/core#prefLabel'   : 'label',
		'http://purl.org/dc/elements/1.0/Title'           : 'label',
		'http://www.w3.org/2004/02/skos/core#definition'  : 'description',
		'http://purl.org/dc/elements/1.0/Description'     : 'description',
		'http://www.w3.org/2000/01/rdf-schema#comment'    : 'description',
		'http://www.w3.org/2006/03/wn/wn20/schema/gloss'  : 'gloss',
		'http://www.w3.org/2006/03/wn/wn20/schema/synsetId' : 'synset_id',
		'http://www.w3.org/2006/03/wn/wn20/schema/lexicalForm' : 'lexical_form',
		'http://www.w3.org/2006/03/wn/wn20/schema/tagCount' : 'tag_count',
		'http://www.w3.org/2006/03/wn/wn20/schema/frame' : 'frame',
					   }
	#    <http://www.w3.org/2004/02/skos/core#related>
	#    <http://dmoz.org/rdf/symbolic1>
	#    <http://dmoz.org/rdf/symbolic2>
	#    <http://dmoz.org/rdf/symbolic>
	#    <http://www.w3.org/2006/03/wn/wn20/schema/hyponymOf>
	#    <http://www.w3.org/2006/03/wn/wn20/schema/similarTo>
	_relations_actions = {
		'http://dmoz.org/rdf/related'                   : 'similarTo',
		'http://dmoz.org/rdf/symbolic'                  : 'synonym',
		'http://dmoz.org/rdf/symbolic1'                 : 'synonym',
		'http://dmoz.org/rdf/symbolic2'                 : 'synonym',
		'http://www.w3.org/2004/02/skos/core#related'   : 'similarTo',
		'http://www.w3.org/2006/03/wn/wn20/schema/similarTo' : 'similarTo',
		'http://www.w3.org/2006/03/wn/wn20/schema/hyponymOf' : 'hypernym',
		'http://www.w3.org/2006/03/wn/wn20/schema/partMeronymOf' : 'partMeronymOf',
		'http://www.w3.org/2006/03/wn/wn20/schema/adjectivePertainsTo' : 'adjectivePertainsTo',
		'http://www.w3.org/2006/03/wn/wn20/schema/adverbPertainsTo' : 'adverbPertainsTo',
		'http://www.w3.org/2006/03/wn/wn20/schema/antonymOf' : 'antonym',
		'http://www.w3.org/2006/03/wn/wn20/schema/attribute' : 'attribute',
		'http://www.w3.org/2006/03/wn/wn20/schema/causes' : 'causes',
		'http://www.w3.org/2006/03/wn/wn20/schema/derivationallyRelated' : 'derivationallyRelated',
		'http://www.w3.org/2006/03/wn/wn20/schema/entails' : 'entails',
		'http://www.w3.org/2006/03/wn/wn20/schema/participleOf' : 'participleOf',
		'http://www.w3.org/2006/03/wn/wn20/schema/sameVerbGroupAs' : 'sameVerbGroupAs',
		'http://www.w3.org/2006/03/wn/wn20/schema/substanceMeronymOf' : 'substanceMeronymOf',
		'http://www.w3.org/2006/03/wn/wn20/schema/memberMeronymOf' : 'memberMeronymOf',
		'http://www.w3.org/2006/03/wn/wn20/schema/classifiedByRegion' : 'classifiedByRegion',
		'http://www.w3.org/2006/03/wn/wn20/schema/classifiedByTopic' : 'classifiedByTopic',
		'http://www.w3.org/2006/03/wn/wn20/schema/classifiedByUsage' : 'classifiedByUsage',
		'http://www.openvocabulary.info/ontology/x-antonym' : 'antonym',
	}
	#    <http://www.w3.org/2004/02/skos/core#related>
	#    <http://www.w3.org/2000/01/rdf-schema#seeAlso>,
	#    <http://purl.org/dc/elements/1.0/charset>,
	#    <http://dmoz.org/rdf/newsGroup>,
	#    <http://dmoz.org/rdf/letterbar>
	#    <http://dmoz.org/rdf/lastUpdate>
	#    <http://dmoz.org/rdf/editor>
	#    <http://dmoz.org/rdf/catid>
	#    <http://dmoz.org/rdf/altlang>
	#    <http://www.openvocabulary.info/ontology/x-antonym>
	#    <http://www.openvocabulary.info/ontology/x-broader>
	#    <http://www.openvocabulary.info/ontology/x-narrower>
	_triples_actions = [
		'http://www.w3.org/2004/02/skos/core#related',
		'http://www.w3.org/2000/01/rdf-schema#seeAlso',
		'http://purl.org/dc/elements/1.0/charset',
		'http://dmoz.org/rdf/newsGroup',
		'http://dmoz.org/rdf/letterbar',
		'http://dmoz.org/rdf/lastUpdate',
		'http://dmoz.org/rdf/editor',
		'http://dmoz.org/rdf/catid',
		'http://dmoz.org/rdf/altlang'
	]
	#    <http://www.w3.org/2002/07/owl#allValuesFrom>
	#    <http://www.w3.org/2002/07/owl#cardinality>
	#    <http://www.w3.org/2002/07/owl#disjointWith>
	#    <http://www.w3.org/2002/07/owl#inverseOf>
	#    <http://www.w3.org/2002/07/owl#onProperty>
	#    <http://www.w3.org/2002/07/owl#someValuesFrom>
	#    <http://www.w3.org/2002/07/owl#unionOf>
	_skip_actions = [
		'http://www.w3.org/2002/07/owl#allValuesFrom',
		'http://www.w3.org/2002/07/owl#cardinality',
		'http://www.w3.org/2002/07/owl#disjointWith',
		'http://www.w3.org/2002/07/owl#inverseOf',
		'http://www.w3.org/2002/07/owl#onProperty',
		'http://www.w3.org/2002/07/owl#someValuesFrom',
		'http://www.w3.org/2002/07/owl#unionOf',
		'http://www.w3.org/2000/01/rdf-schema#domain',
		'http://www.w3.org/2000/01/rdf-schema#range',
		'http://www.w3.org/2000/01/rdf-schema#subClassOf',
		'http://www.w3.org/2000/01/rdf-schema#subPropertyOf',
		'http://www.w3.org/1999/02/22-rdf-syntax-ns#first',
		'http://www.w3.org/1999/02/22-rdf-syntax-ns#rest',
		#<http://www.w3.org/2000/01/rdf-schema#label>
	]

	#    216	nadużyw.
	#    396	poet.
	#    549	oficj.
	#    887	specjalist.
	#    957	wulg.
	#    1155	żart.
	#    2422	książk.
	#    3128	przestarz.
	#    10225	pot.
	_word_types = {
		u'nadużyw' : 'Overused',
		u'poet' : 'Poetic',
		u'oficj' : 'Official',
		u'specjalist' : 'Specialized',
		u'wulg' : 'Vulgarism',
		u'żart' : 'Facetious',
		u'książk' : 'Literary',
		u'przestarz' : 'Obsolete',
		u'pot' : 'Colloquialism',
	}
	pat_type_tag = re.compile(r"^http[:][/][/]www\.openvocabulary\.info[/]ontology[/]I(.+)$")


	#    Pattern for processing triples
	_triple = re.compile(r"""\s*[<](?P<subject>[^>]+)[>]      # subject
							 \s+
							 [<](?P<predicate>[^>]+)[>]    # predicate
							 \s+
							 (?:(?:[<](?P<obj_uri>[^>]+)[>])|    # object uri
								(?:["'](?P<obj_lit>.+)['"]      # object literal
								   (?:[@](?P<obj_lang>.+))?   # object literal lang tag
								   (?:\^\^(?P<obj_type>.+))?))  # object literal type
							 \s*[.]\s*$
							 """, re.X)

	#    Pattern for extracting label and type (used in OpenVocabulary wordmeanings)
	_type_tag = re.compile(r"""(?P<label>.+) #core label
							\s+\(
							(?P<type>\S+)[.] #type of word
							\)
							""", re.X)

	def __init__(self):
		"""
		Initialize processor - with alternative URIs for labels and narrowers
		"""
		pass


	def read(self, file_name):
		"""
		Read in given file - line by line
		"""
		file = codecs.open(file_name, encoding='utf-8', mode="r")
		i = 0
		size = 100
		date = time.mktime(datetime.datetime.utcnow().timetuple())
		for line in file:
			line = line.rstrip()
			if line:
				self.process_line(line)
				i += 1
				if not i % size:
					now_date = time.mktime(datetime.datetime.utcnow().timetuple())
					db.reset_queries()
					gc.collect()
					print "[INFO] importing next %d lines [%d, %d]" % (size, i, now_date - date)
					date = now_date
		# update is_root column to 1 for all root entries:
		for (orphan,) in Entry.objects.all().filter(types__uri="http://www.w3.org/2006/03/wn/wn20/schema/Synset").filter(parent__isnull=True).values_list("id"):
			if Entry.objects.filter(parent__id=orphan):
				Entry.objects.filter(id=orphan).update(is_root=1)

	def process_line(self, line):
		"""
		Process single line entry
		"""
		m = self._triple.match(line)

		if not m:
			print "[ERROR] could not parse line: |%s|" % line.encode("utf-8")
			return

		gdict = m.groupdict()

		# get predicate
		if 'predicate' in gdict:
			daction = gdict['predicate']

			if daction in self._skip_actions:
				print "[INFO] skipping line ", line
				return

			# get subject Entry
			entry = None
			if 'subject' in gdict and gdict['subject']:
				dsubj = self._encode(gdict['subject'])
				entry, created = Entry.objects.get_or_create(uri=dsubj)

				if created:
					try:
						entry.save()
					except Exception, e:
						print "[ERROR] cannot create subject entry: %s | %s" % (gdict['subject'], len(dsubj))
						raise e

			if entry:
				processed = False

				# package matching
				obj = {'pred'  : daction,
					'uri'   : gdict['obj_uri'],
					'label' : gdict['obj_lit'],
					'lang'  : gdict['obj_lang'],
					'type'  : gdict['obj_type'], }

				# is it a literal predicate ?
				if daction in self._literal_actions:
					literal = self._get_literal(obj)
					if literal:
						processed = self.set_literal(entry, self._literal_actions[daction], literal)
				# is it a uri predicate ?
				elif daction in self._uri_actions:
					uri = self._get_uri(obj)
					if uri:
						processed = self.add_uri(entry, self._uri_actions[daction], uri)
				# is it an entry predicate ?
				elif daction in self._entry_actions:
					oentry = self._get_entry(obj)
					if oentry:
						processed = self.add_entry(entry, self._entry_actions[daction], oentry)
				# is it a relation predicate ?
				elif daction in self._relations_actions:
					relation = self._relations_actions[daction]
					oentry = self._get_entry(obj)
					if oentry and relation:
						processed = self.add_relation(entry, relation, oentry)
				# is it a predefined (complex) action or add_triple
				elif daction in self._actions:
					action = self._actions[daction]
					if action and hasattr(self, action):
						faction = getattr(self, action)
						processed = faction(entry, obj=obj)

				# (fallback) is it a triple predicate ?
				if not processed or daction in self._triples_actions:
					processed = self.add_triple(entry, obj=obj)

				if processed:
					try:
						entry.save()
					except Exception, e:
						print "[ERROR] Could not save entry from line [%s]." % line
						raise e
					# inform about the problem
					return

		print "[ERROR] Could not determine action in line [%s]." % line


	def set_type_tag(self, entry, obj):
		"""
		Updates type_tag value of the given entry
		"""
		value = None

		if obj['label'] in self._word_types:
			value = self._word_types[obj['label']]
		elif obj['uri']:
			m = self.pat_type_tag.match(obj['uri'])
			if m:
				value = m.group(1)

		if value:
			entry.type_tag = value
			entry.save()

	def mark_as_root(self, entry, obj):
		"""
		Marks given object as root (top level concept)
		"""
		oentry = self._get_entry(obj)
		oentry.is_root = True
		oentry.save()

	def add_narrower(self, entry, obj):
		"""
		sets narrower relation for given entry
		"""
		oentry = self._get_entry(obj)

		if oentry:
			oentry.parent = entry
			oentry.save()

			reference, created = EntryReference.objects.get_or_create(subject=entry, object=oentry, relation='hyponym')
			if created:
				reference.save()

			return True

		print "[WARNING] cannot add narrower"
		return False


	def add_broader(self, entry, obj):
		"""
		sets broader relation for given entry
		"""
		oentry = self._get_entry(obj)

		if oentry:
			entry.parent = oentry

			reference, created = EntryReference.objects.get_or_create(subject=entry, object=oentry, relation='hypernym')
			if created:
				reference.save()

			return True

		print "[WARNING] cannot add broader"
		return False


	def add_relation(self, entry, relation, oentry):
		"""
		sets any relation for given entry
		"""
		reference, created = EntryReference.objects.get_or_create(subject=entry, object=oentry, relation=relation)
		if created:
			reference.save()
		return True


	def add_uri(self, entry, pred, uri):
		"""
		Allows to add URI type object to given property in Entry
		"""
		if hasattr(entry, pred) and uri:
			uriPred = getattr(entry, pred)
			if hasattr(uriPred, 'add'):
				uriPred.add(uri)
				return True

		print "[WARNING] cannot add uri"
		return False


	def add_entry(self, entry, pred, oentry):
		"""
		Allows to add Entry object to given property in Entry
		"""
		if hasattr(entry, pred) and oentry:
			uriPred = getattr(entry, pred)
			if hasattr(uriPred, 'add'):
				uriPred.add(oentry)
			else:
				setattr(entry, pred, oentry)
			return True

		print "[WARNING] cannot add entry  <%s> %s <%s> | %s " % (entry.uri, pred, oentry.uri, str(uriPred))
		return False


	def set_literal(self, entry, pred, literal):
		"""
		Allows to set literal of given property in Entry
		"""
		if hasattr(entry, pred) and literal:
			# fallback to normal literal predicate set
			setattr(entry, pred, literal)
			return True

		print "[WARNING] cannot set literal (%s, %s)" % (entry.uri, pred)
		return False


	def add_triple(self, entry, obj):
		"""
		adds triple relation for given entry
		"""
		upred = None
		uobj = None
		utype = None

		if 'pred' in obj and obj['pred']:
			upred, created = Predicate.objects.get_or_create(uri=obj['pred'])
			if created:
				upred.save()
		else:
			print "[WARNING] cannot set triple without proper predicate"
			return False

		if 'uri' in obj and obj['uri']:
			uobj = self._get_uri(obj)

		if 'type' in obj and obj['type']:
			utype, created = URI.objects.get_or_create(uri=obj['type'])
			if created:
				utype.save()

		triple = Triple(subject=entry,
						predicate=upred,
						object=uobj,
						literal=self._get_literal(obj),
						literal_type=utype,
						literal_lang=obj['lang'])
		triple.save()

		return True


	def set_scheme(self, entry, obj):
		"""
		sets scheme for given entry
		"""
		if 'uri' in obj and obj['uri']:
			ouri = obj['uri']
			context, created = Context.objects.get_or_create(uri=ouri) #lookup(ouri)
			if created:
				context.save()

			entry.context = context

			return True

		print "[WARNING] cannot set scheme to non existing object: " + str(obj)
		return False



	# ---------------------------------------------------

	def _get_uri(self, obj):
		"""
		retrieves URI object based on obj map
		"""
		if 'uri' in obj and obj['uri']:
			ouri = self._encode(obj['uri'])
			uri, created = URI.objects.get_or_create(uri=ouri) #lookup(ouri)
			if created:
				uri.save()

			return uri

		print "[WARNING] cannot determine uri to a non existing object: " + str(obj)
		return None


	def _get_literal(self, obj):
		"""
		sets label for given entry
		"""
		if 'label' in obj and obj['label']:
			label = self._encode(obj['label'])
			return label
		else:
#            print "[WARNING] cannot determine literal label: "+str(obj)
			return None


	def _get_entry(self, obj):
		"""
		retrieves Entry object based on given URI
		"""
		if 'uri' in obj and obj['uri']:
			ouri = self._encode(obj['uri'])
			oentry, created = Entry.objects.get_or_create(uri=ouri) #lookup(ouri)
			if created:
				try:
					oentry.save()
				except Exception, e:
					print "[ERROR] problem creating new entry with URI: %s (len: %s) " % (obj['uri'], len(ouri))
					raise e

			return oentry

		print "[WARNING] cannot retrieve a non existing object: " + str(obj)
		return None

	def _encode(self, text):
		"""
		Encodes \u???? into utf-8 text
		"""
		if text and "\u" in text:
			t = eval('u"%s"' % text.replace('"', '\"'))
			text = t.encode('utf-8')
		return text





