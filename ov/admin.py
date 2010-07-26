from django.contrib import admin
from ov_django.ov.models import *

admin.site.register(Context, ContextAdmin)
admin.site.register(Entry, EntryAdmin)
