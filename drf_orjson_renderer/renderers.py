import json
import uuid
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.renderers import BaseRenderer
from rest_framework.settings import api_settings

import orjson


__all__ = ["ORJSONRenderer"]


class ORJSONRenderer(BaseRenderer):
    """
    Renderer which serializes to JSON.
    Uses the Rust-backed orjson library for serialization speed.
    """

    media_type = "application/json"
    format = "json"

    @staticmethod
    def default(obj):
        """
        When orjson doesn't recognize an object type for serialization it passes
        that object to this function which then converts the object to its
        native Python equivalent.

        :param obj: Object of any type to be converted.
        :return: native python object
        """

        if isinstance(obj, dict):
            return dict(obj)
        elif isinstance(obj, list):
            return list(obj)
        elif isinstance(obj, Decimal):
            if api_settings.COERCE_DECIMAL_TO_STRING:
                return str(obj)
            else:
                return float(obj)
        elif isinstance(obj, (str, uuid.UUID)):
            return str(obj)
        elif hasattr(obj, "tolist"):
            return obj.tolist()
        elif hasattr(obj, "__iter__"):
            return list(item for item in obj)

    def render(self, data, media_type=None, renderer_context=None):
        """
        Serializes Python objects to JSON.

        :param data: The response data, as set by the Response() instantiation.
        :param media_type: If provided, this is the accepted media type, of the
                `Accept` HTTP header.
        :param renderer_context: If provided, this is a dictionary of contextual
                information provided by the view. By default this will include
                the following keys: view, request, response, args, kwargs
        :return: bytes() representation of the data encoded to UTF-8
        """
        renderer_context = renderer_context or {}

        # If `default_function` is not provided use this library's
        # implementation. If the `default_function` is provided use that
        # instead. If the key is present but the value is `None` render
        # the data using raw orjson processing.
        if "default_function" not in renderer_context:
            default = self.default
        else:
            default = renderer_context.get("default_function")

        # If `indent` is provided in the context, then pretty print the result.
        # E.g. If we're being called by RestFramework's BrowsableAPIRenderer.
        indent = renderer_context.get("indent")
        if indent is None or "application/json" in media_type:
            serialized = orjson.dumps(
                data, default=default, option=orjson.OPT_SERIALIZE_DATACLASS,
            )
        else:
            serialized = json.dumps(data, indent=indent, cls=DjangoJSONEncoder)
        return serialized
