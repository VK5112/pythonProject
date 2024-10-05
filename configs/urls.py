from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('admin_panel/', include('admin_panel.urls')),
    path('authorization/', include('authorization.urls')),
    path('groups/', include('groups.urls')),
    path('orders/', include('orders.urls')),
    path('api/v1/doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
