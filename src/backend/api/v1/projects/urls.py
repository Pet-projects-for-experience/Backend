from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.v1.projects.views import (  # ParticipantsViewSet,
    DirectionViewSet,
    DraftViewSet,
    InvitationToProjectViewSet,
    MyRequestsViewSet,
    ProjectParticipationRequestsViewSet,
    ProjectPreviewMainViewSet,
    ProjectSpecialistsViewSet,
    ProjectViewSet,
)

router = SimpleRouter()

router.register(
    "projects/preview_main",
    ProjectPreviewMainViewSet,
    basename="projects-preview-main",
)
router.register(
    r"projects/requests",
    ProjectParticipationRequestsViewSet,
    basename="specialist-requests",
)
router.register(
    r"projects/my-requests",
    MyRequestsViewSet,
    basename="my-requests",
)
router.register(
    r"projects/directions",
    DirectionViewSet,
    basename="projects-directions",
)
router.register(
    r"projects/project_specialists",
    ProjectSpecialistsViewSet,
    basename="projects-specialists",
)
# router.register(
#     r"projects/(?P<project_pk>\d+)/participants",
#     ParticipantsViewSet,
#     basename="projects-participants",
# )
router.register(
    r"projects/invitations",
    InvitationToProjectViewSet,
    basename="projects-invitations",
)
router.register(r"projects/drafts", DraftViewSet, basename="projects-drafts")
router.register(r"projects", ProjectViewSet, basename="projects")

urlpatterns = [
    path("", include(router.urls)),
]
