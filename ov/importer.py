#!/usr/bin/env python
# encoding: utf-8
"""
importer.py

Created by Sebastian Kruk on .
Copyright (c)  Knowledge Hives sp. z o.o.. All rights reserved.
"""

import sys
import os
import re
from ov_django.ov.models import Context, Entry, EntryReference, ClassificationReference

"""
Reads configuration from the RDF triples
"""
class Triples:
    _label = ['http://www.w3.org/2004/02/skos/core#prefLabel']
    _narrower = ['http://www.w3.org/2004/02/skos/core#narrower']
    _actions = { 'http://www.w3.org/2004/02/skos/core#inScheme' : 'set_scheme' }
    _triple = re.compile(r"""[<](?P<subject>[^>]+)[>]      # subject
                             \s+
                             [<](?P<predicate>[^>]+)[>]    # predicate 
                             \s+
                             (?:[<](?P<obj_uri>[^>]+)[>])| # object uri
                             (?:["](?P<obj_lit>[^"]+)["]  # object literal
                              (?:[@](?P<obj_lang>[^.]+))?  # object literal lang tag
                              (?:^^(?P<obj_type>[^.]+))?)  # object literal type
                             \s[.]
                             """, re.X)

    """
    Initialize processor - with alternative URIs for labels and narrowers
    """
    def __init__(self, labelProp=None, narrowerProp=None):
        if labelProp:
            _label = labelProp if isinstance(labelProp, (list, tuple, QuerySet)) else [labelProp]
        if narrowerProp:
            _narrower = narrowerProp if isinstance(narrowerProp, (list, tuple, QuerySet)) else [narrowerProp]

        for l in _labels:
            _actions[l] = 'set_label'
        for n in _narrower:
            _actions[n] = 'add_narrower'

    """
    Read in given file - line by line
    """
    def read(self, file_name):
        file = open(file_name)
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
        m = _triple.match(line)
        gdict = m.groupdict()
        dsubj = gdict['subject']
        
        if dsubj: 
            entry = Entry.objects.lookup(uri=dsubj)
            
        if not entry:
            print "Could not determine subject in line [%s]." % line
            
        
        daction = gdict['predicate']
        if daction:
            action = _action[daction]
            
        if not action:
            print "Could not determine action in line [%s]." % line
            return
            
        action(entry, obj=(gdict['obj_uri'], gdict['obj_lit'], gdict['obj_lang'], gdict['obj_tag']));
    
        
    def set_label(self, entry, obj):
        pass
        
    def add_narrower(self, entry, obj):
        pass
        
    def set_scheme(self, entry, obj):
        pass
        