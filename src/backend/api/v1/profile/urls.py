from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProfileProfessionsViewSet, ProfileView

router = SimpleRouter()
router.register(
    "profile/professions",
    ProfileProfessionsViewSet,
    basename="profile-professions",
)

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", ProfileView.as_view(), name="profile-settings"),
]
