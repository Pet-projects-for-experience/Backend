from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProfileView, SpecialistsViewSet

router = SimpleRouter()
router.register(
    "profiles/me/specialists",
    SpecialistsViewSet,
    basename="profile-specialists",
)

urlpatterns = [
    path("", include(router.urls)),
    path("profiles/me/", ProfileView.as_view(), name="profile-settings"),
]
