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
from myapp.models import Note


class NoteIndex(SearchIndex):
    text = CharField(document=True, use_template=True)
    author = CharField(model_attr='user')
    pub_date = DateTimeField(model_attr='pub_date')

    def get_queryset(self):
        """Used when the entire index for model is updated."""
        return Note.objects.filter(pub_date__lte=datetime.datetime.now())


site.register(Note, NoteIndex)