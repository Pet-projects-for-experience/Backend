from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.profile.views import (
    ProfileUpdateView,
    ProfileViewSet,
    ProfileVisibulityView,
)

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
urlpatterns = [
    path("", include(router.urls)),
    path("profile_update/<pk>/", ProfileUpdateView.as_view()),
    path("profile_visibility/<pk>/", ProfileVisibulityView.as_view()),
]
