from django.contrib import admin
from vocab.ov.models import *

admin.site.register(Context, ContextAdmin)
admin.site.register(Entry, EntryAdmin)
