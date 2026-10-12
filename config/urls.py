"""Root URL configuration for Fusion-Integrated."""

from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from fusion_auth.views import LoginView, LogoutView, MeView
import core.api.schema  # noqa: F401
from core.api.health import healthz, readyz

urlpatterns = [
    path("healthz", healthz, name="healthz"),
    path("readyz", readyz, name="readyz"),
    path("api/v1/", include("fusion_auth.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    path("api/v1/elm/", include("modules.elm.api.urls")),
]

if "modules.directory" in settings.INSTALLED_APPS:
    urlpatterns.append(
        path("api/v1/directory/", include("modules.directory.api.urls"))
    )

if "modules.placement" in settings.INSTALLED_APPS:
    urlpatterns.append(
        path("api/v1/placement/", include("modules.placement.api.urls"))
    )
