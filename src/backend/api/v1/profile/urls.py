from django.urls import path

from .views import SettingProfileView


urlpatterns = [
    path("settings/profile/",
         SettingProfileView.as_view(),
         name="profile-settings"),
]
