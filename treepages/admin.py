from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, get_object_or_404


from .tree_editor import TreeEditor

from .models import Page


class PageAdmin(TreeEditor, admin.ModelAdmin):

    DIRECTIONS = ['up', 'down', 'left',  'right']

    fieldsets = (
        (None, {
            'fields': ('parent', 'title', 'copy', 'status')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('slug_override', 'template', 'comments_enabled',
                       'login_required')
        }),
    )
    list_display = ('title', 'move', 'comments_enabled', 'login_required',
                    'template', 'status', 'created_at')

    list_editable = ('status',)
    list_filter = ('status',)
    search_fields = ('title', 'parent__title', 'copy')

    def get_urls(self):
        return patterns('',
            url(r'^(?P<pk>\d{1,6})/move/$', self.view_move_node,
                name='treepages_page_move_node'),
        ) + super(PageAdmin, self).get_urls()

    def view_move_node(self, request, pk):
        """
        Move page nodes using MPTT
        """
        obj = get_object_or_404(self.model, pk=pk)
        direction = request.GET.get('direction')

        if direction in self.DIRECTIONS:
            if direction == 'up':
                target, position = obj.get_previous_sibling(), 'left'
            elif direction == 'down':
                target, position = obj.get_next_sibling(), 'right'
            elif direction == 'left':
                target, position = obj.parent, 'right'
            elif direction == 'right':
                target, position = obj.get_previous_sibling(), 'first-child'

            if target and position:
                obj.move_to(target, position=position)
                obj.save()
        return redirect(request.META['HTTP_REFERER'])

    def url(self, obj):
        return obj.slug_override or obj.slug

    def move(self, obj):
        """
        Add movement links to change list view
        """
        arrows = {
            'up': '&uarr;', 'down': '&darr;',
            'left': '&larr;', 'right': '&rarr;'}
        links = []
        url = reverse('admin:treepages_page_move_node', kwargs={'pk': obj.pk})

        for direction in self.DIRECTIONS:
            arrow = arrows[direction]
            links.append('<a href="%(url)s?direction=%(direction)s" '\
                    'class="%(direction)s">%(arrow)s</a>' % locals())
        return ' '.join(links)
    move.allow_tags = True

admin.site.register(Page, PageAdmin)
