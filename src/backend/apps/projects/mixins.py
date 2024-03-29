class RecruitmentStatusMixin:
    """Миксин с методом определения статуса набора специалистов в проект."""

    def calculate_recruitment_status(self, obj) -> str:
        """Метод определения статуса набора в проект."""

        if any(
            specialist.is_required
            for specialist in obj.project_specialists.all()
        ):
            return "Набор открыт"
        return "Набор закрыт"
