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

        # By default, this function will use its own version of `default()` in
        # order to safely serialize known Django types like QuerySets. If you
        # know you won't need this you can pass `None` to the renderer_context
        # ORJSON will only serialize native Python built-in types. If you know
        # that you need to serialize additional types such as Numpy you can
        # override the default here.
        #
        # Instead of the full if-else, the temptation here is to optimize
        # this block by calling:
        #
        # `default = renderer_context.get("default_function", self.default)`
        #
        # Don't do that here because you will lose the ability to pass `None`
        # to ORJSON.
        if "default_function" not in renderer_context:
            default = self.default
        else:
            default = renderer_context["default_function"]

        # If `indent` is provided in the context, then pretty print the result.
        # E.g. If we're being called by RestFramework's BrowsableAPIRenderer.
        indent = renderer_context.get("indent")
        if indent is None or "application/json" in media_type:
            serialized = orjson.dumps(
                data, default=default, option=orjson.OPT_SERIALIZE_DATACLASS
            )
        else:
            encoder_class = renderer_context.get(
                "django_encoder_class", DjangoJSONEncoder
            )
            serialized = json.dumps(data, indent=indent, cls=encoder_class)
        return serialized
