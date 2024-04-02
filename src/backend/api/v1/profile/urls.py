from django.urls import path

from api.v1.profile.views import ProfileListAPIView, ProfileView

urlpatterns = [
    path("profiles/", ProfileListAPIView.as_view(), name="profile-list"),
    path("profiles/<pk>", ProfileView.as_view(), name="profile"),
]
