from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.v1.projects.views import (
    DirectionViewSet,
    DraftViewSet,
    ProjectPreviewMainViewSet,
    ProjectViewSet,
)

router = SimpleRouter()

router.register(
    "preview_main", ProjectPreviewMainViewSet, basename="projects-preview-main"
)
router.register("directions", DirectionViewSet, basename="projects-directions")
router.register("drafts", DraftViewSet, basename="projects-drafts")
router.register("", ProjectViewSet, basename="projects")


urlpatterns = [
    path("", include(router.urls)),
]
