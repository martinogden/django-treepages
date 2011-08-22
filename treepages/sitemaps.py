from django.contrib.sitemaps import Sitemap
from .models import Page


class TreePagesSitemap(Sitemap):

    def items(self):
        kwargs = {'status__gte':Page.ACTIVE_LEVEL, 'login_required': False}
        return Page.objects.filter(**kwargs)
