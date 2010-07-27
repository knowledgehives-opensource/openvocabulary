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
import codecs
from ov_django.ov.models import *
from django.utils.encoding import smart_unicode

"""
Reads configuration from the RDF triples
"""
class TriplesParser:
    _actions = { 'http://www.w3.org/2004/02/skos/core#inScheme'    : 'set_scheme',
                 'http://www.w3.org/2004/02/skos/core#broader'     : 'add_broader', 
                 'http://www.w3.org/2004/02/skos/core#narrower'    : 'add_narrower', 
                 'http://www.w3.org/2004/02/skos/core#prefLabel'   : 'set_label',
                 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' : 'add_type', }
    _triple = re.compile(r"""[<](?P<subject>[^>]+)[>]      # subject
                             \s+
                             [<](?P<predicate>[^>]+)[>]    # predicate 
                             \s+
                             (?:(?:[<](?P<obj_uri>[^>]+)[>])|    # object uri
                                (?:["](?P<obj_lit>[^"]+)["]      # object literal
                                   (?:[@](?P<obj_lang>[^.]+))?   # object literal lang tag
                                   (?:^^(?P<obj_type>[^.]+))?))  # object literal type
                             \s*[.]
                             """, re.X)

    """
    Initialize processor - with alternative URIs for labels and narrowers
    """
    def __init__(self, labelProp=None, narrowerProp=None):
        if labelProp:
            for l in labelProp:
                self._actions[l] = 'set_label'
        if narrowerProp:
            for n in narrowerProp:
                self._actions[n] = 'add_narrower'


    """
    Read in given file - line by line
    """
    def read(self, file_name):
        file = codecs.open(file_name, encoding='ascii')
        while 1:
            lines = file.readlines(100000)
            if not lines:
                break
            for line in lines:
                self.process_line(line)
        
    """
    Process single line entry
    """
    def process_line(self, line):
        m = self._triple.match(line)
        gdict = m.groupdict()
        dsubj = gdict['subject']
        
        if dsubj: 
            entry = Entry.objects.lookup(dsubj)
            
        if not entry:
            entry = Entry(uri=dsubj)
        
        action = None
        daction = gdict['predicate']
        if daction and daction in self._actions:
            action = self._actions[daction]
            
        if not action or not hasattr(self, action):
            if daction:
                faction = self.add_triple
            else:
                print "Could not determine action in line [%s]." % line
                return
        else:    
            faction = getattr(self, action)
            
        faction(entry, obj={'pred'  : gdict['predicate'],
                            'uri'   : gdict['obj_uri'], 
                            'label' : gdict['obj_lit'], 
                            'lang'  : gdict['obj_lang'], 
                            'type'  : gdict['obj_type'], });
                           
        entry.save()
    
    """
    sets label for given entry
    """    
    def set_label(self, entry, obj):
        label = obj['label']
        print u"set label '%s' for <%s>." % (label, entry.uri)
        if "\u" in label:
            l = eval('u"%s"' % label.replace('"', '\\"'))
            label = l.encode('utf-8')
        entry.label = label
        
    """
    sets narrower relation for given entry
    """
    def add_narrower(self, entry, obj):
        ouri = obj['uri']
        if not ouri:
            print "cannot narrow to non existing object"
            return
            
        oentry = Entry.objects.lookup(ouri)
        if not oentry:
            oentry = Entry(uri=ouri)
        
        oentry.parent = entry
        oentry.save()
        
        reference = EntryReference(subject=entry, object=oentry, relation='hyponym')
        reference.save()
        
        print "added <%s> skos:narrower <%s>." % (entry.uri, oentry.uri)
    
    """
    sets broader relation for given entry
    """
    def add_broader(self, entry, obj):
        ouri = obj['uri']
        if not ouri:
            print "cannot broader to non existing object"
            return

        oentry = Entry.objects.lookup(ouri)
        if not oentry:
            oentry = Entry(uri=ouri)
            oentry.save()

        entry.parent = oentry

        reference = EntryReference(subject=entry, object=oentry, relation='hypernym')
        reference.save()

        print "added <%s> skos:broader <%s>." % (entry.uri, oentry.uri)

    """
    adds rdf:type relation for given entry
    """
    def add_type(self, entry, obj):
        ouri = obj['uri']
        if not ouri:
            print "cannot add rdf:type to a non existing object"
            return

        uri = URI.objects.lookup(ouri)
        if not uri:
            uri = URI(uri=ouri)
            uri.save()

        entry.types.add(uri)

        print "added <%s> rdf:type <%s>." % (entry.uri, uri.uri)


    """
    adds triple relation for given entry
    """
    def add_triple(self, entry, obj):
        upred = None
        uobj  = None
        utype = None
        
        if obj['pred']:
            upred = Predicate.objects.lookup(obj['pred'])
            if not upred:
                upred = Predicate(uri=obj['pred'])
                upred.save()
        else:
            print "cannot set triple without proper predicate"
            return
        
        
        if obj['uri']:
            uobj = URI.objects.lookup(obj['uri'])
            if not uobj:
                uobj = URI(uri=obj['uri'])
                uobj.save()
        
        if obj['type']:
            utype = URI.objects.lookup(obj['type'])
            if not utype:
                utype = URI(uri=obj['type'])
                utype.save()
        
        triple = Triple(subject=entry,
                        predicate=upred,
                        object=uobj,
                        literal=obj['label'],
                        literal_type=utype,
                        literal_lang=obj['lang'])
        triple.save()
        
        if uobj:
            print "added <%s> <%s> <%s>." % (entry.uri, upred.uri, uobj.uri)
        elif utype:
            print "added <%s> <%s> '%s'^^<%s>." % (entry.uri, upred.uri, obj['label'], utype.uri)
        elif obj['lang']:
            print "added <%s> <%s> '%s'@%s." % (entry.uri, upred.uri, obj['label'], obj['lang'])
        else:
            print "added <%s> <%s> '%s'." % (entry.uri, upred.uri, obj['label'])


    """
    sets scheme for given entry
    """    
    def set_scheme(self, entry, obj):
        ouri = obj['uri']
        if not ouri:
            print "cannot set scheme to non existing object"
            return
        
        context = Context.objects.lookup(ouri)
        if not context:
            context = Context(uri=ouri)
            context.save()
            
        entry.context = context    
            