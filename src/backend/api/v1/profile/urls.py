from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProfilesViewSet, SpecialistsViewSet

router = SimpleRouter()
router.register(
    "profiles/me/specialists",
    SpecialistsViewSet,
    basename="profile-specialists",
)
router.register("profiles", ProfilesViewSet, basename="profile")

urlpatterns = [
    path("", include(router.urls)),
]
