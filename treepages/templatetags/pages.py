from django import template
from django.conf import settings

from django.utils.safestring import mark_safe
from mptt.templatetags.mptt_tags import cache_tree_children, RecurseTreeNode

from treepages.models import Page

register = template.Library()


class NavRecurseTreeNode(RecurseTreeNode):
    # Adapted from code in django-mptt

    def __init__(self, template_nodes):
        self.template_nodes = template_nodes
        self.queryset = Page.objects.filter(status__gte=Page.NAVIGATION_LEVEL)

    def _render_mptt_node(self, context, node):
        bits = []
        context.push()

        for child in node.get_children():
            context.update({'node': child, 'link': child.get_absolute_url()})
            bits.append(self._render_mptt_node(context, child))
        context['node'] = node
        context['children'] = mark_safe(u''.join(bits))
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def _render_node(self, context, node):
        """
        Render navigation provided in a list

        Example:

            [(name, link), (name, link, [(name, link)])]
        """
        bits = []
        context.push()

        context.update({'node': node[0], 'link': node[1]})
        if len(node) == 3 and isinstance(node[2], list):
            for child in node[2]:
                bits.append(self._render_node(context, child))

        context['node'] = node[0]
        context['children'] = mark_safe(u''.join(bits))
        rendered = self.template_nodes.render(context)
        context.pop()
        return rendered

    def render(self, context):
        bits = []
        add_nav = context.get('additional_navigation')
        if add_nav:
            bits += [self._render_node(context, node) for node in add_nav]
        roots = cache_tree_children(self.queryset)
        bits += [self._render_mptt_node(context, node) for node in roots]
        return ''.join(bits)


@register.tag
def navigation(parser, token):
    """
    Iterates over the nodes in the tree, and renders the contained block for each node.
    This tag will recursively render children into the template variable {{ children }}.
    Only one database query is required (children are cached for the whole tree)
    
    Usage:
        {% navigation %}
        <li>
            <a href="{{ link }}">{{ node }}</a>
            {% if not node.is_leaf_node and children %}
            <ul>
                {{ children }}
            </ul>
            {% endif %}
        </li>
        {% endnavigation %}
    """

    bits = token.contents.split()
    if len(bits) != 1:
        raise template.TemplateSyntaxError(_('%s tag requires 0 arguments') % bits[0])
    
    template_nodes = parser.parse(('endnavigation',))
    parser.delete_first_token()

    return NavRecurseTreeNode(template_nodes)
