from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("projects/", include("api.v1.projects.urls")),
    path("", include("api.v1.users.urls")),
    path("", include("djoser.urls.authtoken")),
    path("", include("api.v1.general.urls")),
    path("", include("api.v1.profile.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/docs/", SpectacularSwaggerView.as_view(url_name="schema")),
]
