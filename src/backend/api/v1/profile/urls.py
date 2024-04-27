from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import ProfileSpecialistsViewSet, ProfileView

router = SimpleRouter()
router.register(
    "profile/specialists",
    ProfileSpecialistsViewSet,
    basename="profile-specialists",
)

urlpatterns = [
    path("", include(router.urls)),
    path("profile/", ProfileView.as_view(), name="profile-settings"),
]
