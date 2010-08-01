#!/usr/bin/env python
# -*- coding: utf-8 -*-
# encoding: utf-8
"""
search_indexes.py

Created by Sebastian Kruk on .
Copyright (c)  Knowledge Hives sp. z o.o.. All rights reserved.
"""

import datetime
from haystack.indexes import *
from haystack import site
from ov_django.ov.models import Entry, Context


class EntryIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    label = CharField(use_template=True)
#    rendered = CharField(use_template=True, indexed=False)
#    def get_queryset(self):
#        """Used when the entire index for model is updated."""
#        return Note.objects.filter(pub_date__lte=datetime.datetime.now())

site.register(Entry, EntryIndex)

class ContextIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    label = CharField(model_attr="label")
#    def get_queryset(self):
#        """Used when the entire index for model is updated."""
#        return Note.objects.filter(pub_date__lte=datetime.datetime.now())

site.register(Context, ContextIndex)