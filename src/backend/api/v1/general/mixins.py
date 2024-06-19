from typing import Dict

from django.db import models
from rest_framework import fields

from .fields import CustomEmailField, CustomURLField


class ToRepresentationOnlyIdMixin:
    """Миксин с методом to_representation, возвращающим только id объекта."""

    def to_representation(self, instance) -> Dict[str, int]:
        """Метод представления объекта в виде словаря с полем 'id'."""

        return {"id": instance.id}


class OverridedFieldMappingMixin:
    """Миксин с переопределенным атрибутом сопоставления полей модели."""

    serializer_field_mapping = {
        models.AutoField: fields.IntegerField,
        models.BigIntegerField: fields.IntegerField,
        models.BooleanField: fields.BooleanField,
        models.CharField: fields.CharField,
        models.CommaSeparatedIntegerField: fields.CharField,
        models.DateField: fields.DateField,
        models.DateTimeField: fields.DateTimeField,
        models.DecimalField: fields.DecimalField,
        models.DurationField: fields.DurationField,
        models.EmailField: CustomEmailField,
        models.Field: fields.ModelField,
        models.FileField: fields.FileField,
        models.FloatField: fields.FloatField,
        models.ImageField: fields.ImageField,
        models.IntegerField: fields.IntegerField,
        models.NullBooleanField: fields.BooleanField,
        models.PositiveIntegerField: fields.IntegerField,
        models.PositiveSmallIntegerField: fields.IntegerField,
        models.SlugField: fields.SlugField,
        models.SmallIntegerField: fields.IntegerField,
        models.TextField: fields.CharField,
        models.TimeField: fields.TimeField,
        models.URLField: CustomURLField,
        models.UUIDField: fields.UUIDField,
        models.GenericIPAddressField: fields.IPAddressField,
        models.FilePathField: fields.FilePathField,
    }
