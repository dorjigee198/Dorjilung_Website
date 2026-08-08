from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from careers import views as careers_views
from cldp import views as cldp_views
from grievance import views as grievance_views
from . import views_dhpl
from django.urls import re_path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
]


# Media (user-uploaded images/documents) isn't handled by WhiteNoise —
# that only serves STATIC_ROOT. Django's own `static()` helper looks
# like it would do this, but it silently no-ops whenever DEBUG=False
# (a built-in guard, regardless of whether it's called inside an
# `if settings.DEBUG:` block) — so it's registered directly here instead,
# via the same underlying view `static()` would have used. Fine for a
# small site without a fronting reverse proxy; move to nginx or
# S3-backed storage before real production traffic.
from django.views.static import serve as serve_static

urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve_static, {"document_root": settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static files from the dev server directly out of
    # STATICFILES_DIRS (source files, not the collected STATIC_ROOT) —
    # WhiteNoise handles this in production instead.
    urlpatterns += staticfiles_urlpatterns()

urlpatterns = urlpatterns + [
    path('', views_dhpl.home, name='dhpl_home'),
    path('about/', lambda req: views_dhpl.section_placeholder(req, 'About')),
    path('project/', lambda req: views_dhpl.section_placeholder(req, 'Project')),
    path('environment/', lambda req: views_dhpl.section_placeholder(req, 'Environment & Social')),
    path('media-centre/', views_dhpl.media_centre, name='media_centre'),
    # 'tenders/' is intentionally not listed here — it's a real Wagtail
    # page (TenderIndexPage) served by the wagtail_urls catch-all below.
    path('careers/', careers_views.careers_list, name='careers_list'),
    path('cldp/', cldp_views.cldp_dashboard, name='cldp_dashboard'),
    path('grievance/', grievance_views.grievance_form, name='grievance_form'),
    path('grievance/submitted/<str:reference_no>/', grievance_views.grievance_submitted, name='grievance_submitted'),
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
