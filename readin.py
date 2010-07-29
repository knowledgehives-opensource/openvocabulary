#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
readin.py

Created by Sebastian Kruk on .
Copyright (c)  Knowledge Hives sp. z o.o.. All rights reserved.
"""

import sys
import gc
import getopt

from django.core.management import setup_environ
import settings

settings.DEBUG = False

setup_environ(settings)

from ov.importer import *


help_message = '''
Read vocabulary into DB.
    -f/--file file to read in
'''

def read_in(file):
    triples = TriplesParser()
    triples.read(file)
    

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    file = None
    
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hf:v", ["help", "file="])
        except getopt.error, msg:
            raise Usage(help_message)
    
        # option processing
        for option, value in opts:
            if option == "-v":
                verbose = True
            if option in ("-h", "--help"):
                raise Usage(help_message)
            if option in ("-f", "--file"):
                file = value

        if file:
            gc.enable()
            read_in(file)
        else:
            raise Usage(help_message)
    
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2
        


if __name__ == "__main__":
    sys.exit(main())
