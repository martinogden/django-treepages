from django.contrib import admin

from .tree_editor import TreeEditor
from .models import Page


class PageAdmin(TreeEditor, admin.ModelAdmin):

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

    def url(self, obj):
        return obj.slug_override or obj.slug


admin.site.register(Page, PageAdmin)
