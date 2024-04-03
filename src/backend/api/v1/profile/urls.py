from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.profile.views import (
    ProfileUpdateView,
    ProfileViewSet,
    ProfileVisibilityView,
)

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("profile_update/<pk>/", ProfileUpdateView.as_view()),
    path("profile_visibility/<pk>/", ProfileVisibilityView.as_view()),
]
