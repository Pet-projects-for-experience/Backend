from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.v1.general.views import (
    CounterApiView,
    ProfessionViewSet,
    SectionViewSet,
    SkillViewSet,
)

router = SimpleRouter()
router.register("professions", ProfessionViewSet, basename="professions")
router.register("skills", SkillViewSet, basename="skills")

urlpatterns = [
    path("section/", SectionViewSet.as_view({"get": "list"})),
    path("counter/", CounterApiView.as_view()),
    path("", include(router.urls)),
]
