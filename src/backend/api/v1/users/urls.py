from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.v1.users.views import CustomUserViewSet

router = SimpleRouter()
router.register(r"users", CustomUserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
