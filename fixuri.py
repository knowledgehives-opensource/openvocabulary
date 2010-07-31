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
words_pat = re.compile(r"^(?:[A-Z][a-z]+){2,}$")
word_pat = re.compile(r"(?P<word>[A-Z][a-z]+)")

gc.enable()


print "will fix labels now (%s)"%sys.getfilesystemencoding()
date = time.mktime(datetime.datetime.utcnow().timetuple())
i=0
for uri in URI.objects.iterator():
    print "%d | %s" % (i, str(uri))
    i+=1
    # retrieve label from URI
    if not uri.label:
        m = name_pat.match(uri.uri)
        if m:
            gdict = m.groupdict()
            label = gdict['label']
            if label:
                if words_pat.match(label):
                    l = ""
                    for m in word_pat.finditer(label):
                        if m.start() > 0:
                            l += m.group().lower()+" "
                        else:
                            l += m.group()+" "
                    label = l.strip()
                # continue                
                uri.label = label.replace('_', ' ')
                uri.save()
                print "extracted label for %s" % str(uri)
            else:
                print u"Did not find label for %s " % str(uri)
        else:
            print u"Could not get label for %s " % str(uri)
            
    if not i%100:
        gc.collect()
    
print u"Completed in ", time.mktime(datetime.datetime.utcnow().timetuple()) - date

