from django.contrib import admin
from .tree_editor import TreeEditor

from .models import Page


class PageAdmin(TreeEditor, admin.ModelAdmin):

    search_fields = ('title',)
    list_display = ('title', 'comments_enabled', 'login_required',
                    'template', 'status', 'created_at')

    list_editable = ('status', 'template')
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


admin.site.register(Page, PageAdmin)
