# Adapted from django.contrib.flatpages

from django.db.models import Q
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.conf import settings
from django.core.xheaders import populate_xheaders
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_protect

from .models import Page

DEFAULT_TEMPLATE = 'pages/default.html'

# This view is called from PageFallbackMiddleware.process_response
# when a 404 is raised, which often means CsrfViewMiddleware.process_view
# has not been called even if CsrfViewMiddleware is installed. So we need
# to use @csrf_protect, in case the template needs {% csrf_token %}.
# However, we can't just wrap this view; if no matching Page exists,
# or a redirect is required for authentication, the 404 needs to be returned
# without any CSRF checks. Therefore, we only
# CSRF protect the internal implementation.
def Page(request, url):
    """
    Public interface to the flat page view.

    Models: `Pages.Pages`
    Templates: Uses the template defined by the ``template_name`` field,
        or `Pages/default.html` if template_name is not defined.
    Context:
        Page
            `Pages.Pages` object
    """
    ACTIVE = {'status__gte': Page.ACTIVE_LEVEL}

    if not url.startswith('/'):
        url = '/' + url
    try:
        f = get_object_or_404(Page, Q(slug_override__exact=url) |\
                              Q(slug__exact=url), **ACTIVE)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            url += '/'
            f = get_object_or_404(Page, Q(slug_override__exact=url) |\
                                  Q(slug__exact=url), **ACTIVE)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise
    return render_Page(request, f)

@csrf_protect
def render_Page(request, f):
    """
    Internal interface to the flat page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if f.login_required and not request.user.is_authenticated():
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
    if f.template_name:
        t = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
    else:
        t = loader.get_template(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in Page templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    f.title = mark_safe(f.title)
    f.content = mark_safe(f.copy)

    c = RequestContext(request, {
        'Page': f,
    })
    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, Page, f.id)
    return response
