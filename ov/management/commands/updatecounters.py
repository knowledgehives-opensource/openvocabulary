from django.core.management.base import BaseCommand

from ov_django.ov.models import Context, Tag

class Command(BaseCommand):
    help = "Updates tag usage counters"

    def handle(self, *args, **kwargs):
        tags = Tag.objects.all()
        for tag in tags:
            tag.usages = Context.objects.filter(visible=True, tags__label__exact=tag.label).count()
            self.stdout.write("Tag '%s' had %d usages\n" % (tag.label, tag.usages))
            tag.save()
        self.stdout.write('All tags processed\n')
