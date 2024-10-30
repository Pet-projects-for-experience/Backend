from django.contrib import admin

from api.v1.projects.mixins import RecruitmentStatusMixin
from apps.projects.constants import PROJECTS_PER_PAGE
from apps.projects.models import (
    ParticipationRequest,
    Profession,
    Project,
    ProjectSpecialist,
    Skill,
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ("speciality", "specialization")
    list_filter = ("specialization",)
    search_fields = ("speciality", "specialization")


@admin.register(Project)
class ProjectAdmin(RecruitmentStatusMixin, admin.ModelAdmin):
    def get_queryset(self, request):
        """Метод получения queryset-а для проектов и черновиков."""

        return (
            Project.objects.select_related("creator", "owner")
            .only(
                "creator__email",
                "owner__email",
                "name",
                "description",
                "started",
                "ended",
                "busyness",
                "phone_number",
                "telegram_nick",
                "email",
                "link",
                "project_status",
            )
            .prefetch_related(
                "project_specialists",
            )
        )

    def recruitment_status(self, obj):
        """Метод получения статуса набора у проекта."""

        return self.get_recruitment_status(obj)

    recruitment_status.short_description = "Статус набора"  # type: ignore

    list_display = (
        "name",
        "description",
        "creator",
        "owner",
        "started",
        "ended",
        "busyness",
        "link",
        "phone_number",
        "telegram_nick",
        "email",
        "recruitment_status",
        "project_status",
    )
    readonly_fields = ("recruitment_status",)
    list_filter = (
        "busyness",
        "project_status",
    )
    search_fields = (
        "name",
        "description",
        "creator__email",
        "owner__email",
    )
    list_per_page = PROJECTS_PER_PAGE


@admin.register(ProjectSpecialist)
class ProjectSpecialistAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "profession",
        "level",
        "count",
        "is_required",
    )
    list_filter = ("project",)
    search_fields = ("project",)


@admin.register(ParticipationRequest)
class ParticipationRequestAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        """Метод получения queryset-а для запросов на участие в проекте."""

        return ParticipationRequest.objects.select_related(
            "project", "user"
        ).only(
            "project__name",
            "user__email",
            "is_viewed",
            "request_status",
            "cover_letter",
            "answer",
        )

    list_display = (
        "project",
        "user",
        "request_status",
        "is_viewed",
        "cover_letter",
        "answer",
    )
    list_filter = ("request_status",)
    search_fields = (
        "project__name",
        "user__email",
    )
