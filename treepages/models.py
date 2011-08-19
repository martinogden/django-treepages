from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel

from .settings import TREEPAGES_TEMPLATES

NULL = {'null': True, 'blank': True}


class BasePage(MPTTModel, models.Model):
    """
    Abstract model for easy extensibility
    """
    class Meta(MPTTModel.Meta):
        abstract = True
        ordering = ('tree_id', 'lft')

    STATUS_CHOICES = (
        (0, 'Draft'),
        (1, 'Archive'),
        (2, 'Published'),
        (3, 'In Navigation'),
    )
    ACTIVE_LEVEL = 2
    NAVIGATION_LEVEL = 3

    parent = models.ForeignKey('self', related_name='children', **NULL)

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    slug_override = models.SlugField(max_length=255,
                        help_text=_('In the format /path/to/page/'), **NULL)
    copy = models.TextField()

    status = models.IntegerField(max_length=255, default=0, 
                                 choices=STATUS_CHOICES)
    template = models.CharField(max_length=255, choices=TREEPAGES_TEMPLATES,
                                default=TREEPAGES_TEMPLATES[0][0])

    comments_enabled = models.BooleanField()
    login_required = models.BooleanField()

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        segments = [self.title]
        parent = self.parent
        while parent:
            segments.append(parent.title)
            parent = parent.parent
        self.slug = '/%s/' % '/'.join([slugify(s) for s in reversed(segments)])
        return super(BasePage, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return self.slug_override or self.slug


class Page(BasePage):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
