from typing import Dict


class ToRepresentationOnlyIdMixin:
    """Миксин с методом to_representation, возвращающим только id объекта."""

    def to_representation(self, instance) -> Dict[str, int]:
        """Метод представления объекта в виде словаря с полем 'id'."""

        return {"id": instance.id}
