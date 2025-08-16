from django.http import Http404
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from core.api.exceptions import handle_api_exception


def get_list(model_or_queryset, **kwargs):
    try:
        return get_list_or_404(model_or_queryset)
    except Http404:
        raise NotFound("Users Not Found")


def get_object(model_or_queryset, **kwargs):
    try:
        return get_object_or_404(model_or_queryset, **kwargs)
    except Http404:
        return None


def update_object(obj, **kwargs):
    try:
        for key, value in kwargs.items():
            setattr(obj, key, value)

        obj.save()

        return obj
    except Exception as e:
        raise handle_api_exception(e, f"update {obj.__class__.__name__}")


def create_serializer_class(name, fields):
    return type(name, (serializers.Serializer,), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    serializer_class = create_serializer_class(name="inline_serializer", fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)
