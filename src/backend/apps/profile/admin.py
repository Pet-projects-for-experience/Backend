from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Profile, Specialist


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = (
        "profile",
        "profession",
        "level",
        "skills_display"
    )
    list_filter = ("level", "profession__specialty")

    @admin.display(description="Навыки")
    @mark_safe
    def skills_display(self, specialist):
        return '<br>'.join(skill.name for skill in specialist.skills.all())

    def get_queryset(self, request):
        return (
            Specialist.objects.select_related("profile", "profession")
            .prefetch_related("skills")
        )


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
        "visible_status_contacts",
        "allow_notifications",
        "subscribe_to_projects"
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

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions

    def has_delete_permission(self, request, obj=None):
        return False
