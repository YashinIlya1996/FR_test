from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from mailing_service.views import about

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v0',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0)),
    path('about/', about),
    path('api/auth/', include('rest_framework.urls')),
    path('api/v0/', include('mailing_service.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('admin/', admin.site.urls)
    ]
