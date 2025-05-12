"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path 
from django.views.static import serve
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import TemplateView
from django.conf.urls.i18n import i18n_patterns

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

import os


from apps.common.sitemap import BlogSitemap,ProductSitemap

sitemaps = {
    'blog': BlogSitemap,
    'product': ProductSitemap,
}

handler404 = 'apps.pages.views.handler404'
handler500 = 'apps.pages.views.handler500'
handler403 = 'apps.pages.views.handler403'
handler400 = 'apps.pages.views.handler400'

urlpatterns = [
    # Non-translated URLs
    path('management/', admin.site.urls),
    path("select2/", include("django_select2.urls")),
    path('f/', include('apps.emr.files.urls', namespace='files')),

]


# Translated URLs
urlpatterns += i18n_patterns(


    path('accounts/', include('accounts.urls')),
    path("", include('apps.pages.urls')),
    path("users/", include("apps.authentication.urls")),
    path("tasks/", include("apps.tasks.urls")),
    path("dashboard/", include("apps.dashboard.urls")),


    path("", include("apps.tools.urls")),
    path("", include("apps.tool_django_generator.urls")),
    path("", include("apps.tool_csv_processor.urls")),
    path("", include("apps.tool_db_migrator.urls")),
    path("", include("apps.tool_db_processor.urls")),

    path("", include("apps.products.urls")),
    path('', include('apps.blog.urls')),
    path('ticket/', include('apps.support.urls')),
    # path('docs/', include('apps.docs.urls')),
    path('docs/', include('docs.urls')),
    path("", include('apps.ai_processor.urls')),
    path('accounts/', include('allauth.urls')),
    path('api/', include('apps.api.product.v1.urls')),
    path('api/', include('apps.api.chat.v1.urls')),
    path('api/', include('apps.api.users.v1.urls')),

    re_path(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

    path(
        "sitemap.xml",
        TemplateView.as_view(template_name="sitemap.xml", content_type="text/xml"),
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),

    path("__debug__/", include("debug_toolbar.urls")),


    # Serve other documentation files
    re_path(r'^docs/(?P<path>.*)$', serve, {
        'document_root': os.path.join(os.path.dirname(__file__), '..', 'apps', 'docs', '_build', 'html'),
        'show_indexes': True
    }),


#    path('', include('mainfunctions.urls')),
#    path('about/', include('mainfunctions.urls')),


    # My Apps
    
    path('common/', include('apps.common.urls')),  # switches the language
    path("my_dashboard/", include("apps.my_dashboard.urls")),
    path("patients_dashboard/", include("apps.patients_dashboard.urls")),
    path("ros/", include("apps.emr.ros.urls")),
    path("identity/", include("apps.emr.identity.urls")),
    path('lab/', include('apps.emr.lab.urls', namespace='lab')),
    path('questionnaire/', include('apps.emr.questionnaires.urls', namespace='questionnaires')),
    path('events/', include('apps.emr.events.urls')),
    path('rtms/', include('apps.emr.rtms.urls', namespace='rtms')),
    path('oneglance/', include('apps.emr.oneglance.urls', namespace='oneglance')),
    prefix_default_language=False,
    )


# Static and media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


schema_view = get_schema_view(
   openapi.Info(
      title="Products API",
      default_version='v1',
      description="Product description",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
   path('api-docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)

