from django.contrib import admin

from .constants import MAX_PROFILE_PROFESSIONS
from .models import Profile, Specialist


class SpecialistInline(admin.StackedInline):
    model = Specialist
    max_num = MAX_PROFILE_PROFESSIONS


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "country",
        "city",
        "ready_to_participate",
        "visible_status",
        "visible_status_contacts"
    )
    list_filter = (
        "ready_to_participate",
        "visible_status",
        "visible_status_contacts"
    )
    inlines = [SpecialistInline]
    fields = (
        "user",
        "name",
        "avatar",
        "birthday",
        "country",
        "city",
        "about",
        "portfolio_link",
        "phone_number",
        "telegram_nick",
        "email",
        "ready_to_participate",
        "visible_status",
        "visible_status_contacts"
    )
    readonly_fields = ("user",)

    def get_queryset(self, request):
        return Profile.objects.select_related("user").only(
            "user__email",
            "name",
            "country",
            "city",
            "ready_to_participate",
            "visible_status",
            "visible_status_contacts"
        )
