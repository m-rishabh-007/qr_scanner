from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from apps.core.views import health, model_health, readiness

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health),
    path("health/ready/", readiness),
    path("health/model/", model_health),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/merchant/", include("apps.locations.urls")),
    path("api/merchant/analytics/", include("apps.analytics.urls")),
    path("api/public/", include("apps.feedback.urls")),
    path("", include("apps.public_site.urls")),
]
