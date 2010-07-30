#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
fixme.py

Created by Sebastian Kruk on .
Copyright (c)  Knowledge Hives sp. z o.o.. All rights reserved.
"""

import sys
import gc
import re
import getopt
import time
import datetime

from django.core.management import setup_environ
import settings
settings.DEBUG = False
setup_environ(settings)

from django.db import connection
assert not connection.queries, 'settings.DEBUG=True?'

from ov.models import *
from ov.importer import *

name_pat = re.compile(r"^(?:.+)[/](?P<label>[^/]+)[/]?$")

gc.enable()


print "will fix labels now (%s)"%sys.getfilesystemencoding()
date = time.mktime(datetime.datetime.utcnow().timetuple())
i=0
for entry in Entry.objects.iterator():
    print "%d | %s" % (i, str(entry))
    i+=1
    # fix correct type tags
    if entry.type_tag and entry.type_tag in TriplesParser._word_types:
        entry.type_tag = TriplesParser._word_types[entry.type_tag]
        entry.save()
        print u"update type_tag %s" % str(entry)

    # fix labels that should not have a separate type tag
    elif entry.type_tag and entry.label and \
        not entry.type_tag in TriplesParser._word_types and \
        not entry.type_tag in TriplesParser._word_types.values():
        entry.label = "%s (%s)" % (entry.label, entry.type_tag)
        entry.type_tag = None
        entry.save()
        print "fixed label with type_tag to %s" % str(entry)

    # fix lexical forms that should have a separate type tag
    elif not entry.label and entry.lexical_form:
        m = TriplesParser._type_tag.match(entry.lexical_form)
        if m:
            gd = m.groupdict()
            if 'type' in gd and gd['type'] in TriplesParser._word_types:
                entry.type_tag = TriplesParser._word_types[gd['type']]
                entry.lexical_form = gd['label']
                entry.save()
                print "fixed lexical form with type_tag to %s" % str(entry)
            else:
                print u"did not match for fixing: ", str(gd)

    # retrieve label from URI
    elif not entry.label and not entry.lexical_form:
        m = name_pat.match(entry.uri)
        if m:
            gdict = m.groupdict()
            label = gdict['label']
            if label:
                entry.label = label.lower().replace('_', ' ')
                entry.save()
                print "extracted label for %s" % str(entry)
            else:
                print u"Did not find label for %s " % str(entry)
        else:
            print u"Could not get label for %s " % str(entry)
            
    if not i%100:
        gc.collect()
    
print u"Completed in ", time.mktime(datetime.datetime.utcnow().timetuple()) - date

