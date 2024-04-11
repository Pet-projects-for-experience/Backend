from django.contrib import admin

from api.v1.projects.mixins import RecruitmentStatusMixin
from apps.projects.constants import PROJECTS_PER_PAGE
from apps.projects.models import Project, ProjectSpecialist, Skill, Specialist


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Specialist)
class SpecialistAdmin(admin.ModelAdmin):
    list_display = ("specialty", "specialization")
    list_filter = ("specialization",)
    search_fields = ("specialty", "specialization")


@admin.register(Project)
class ProjectAdmin(RecruitmentStatusMixin, admin.ModelAdmin):
    def get_queryset(self, request):
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
                "status",
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
        "status",
    )
    readonly_fields = ("recruitment_status",)
    list_filter = ("busyness", "status")
    search_fields = ("name", "description", "creator__username")
    list_per_page = PROJECTS_PER_PAGE


@admin.register(ProjectSpecialist)
class ProjectSpecialistAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "specialist",
        "level",
        "count",
        "is_required",
    )
    list_filter = ("project",)
    search_fields = ("project",)
