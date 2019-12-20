import datetime
import json
import unittest
import uuid
from collections import OrderedDict, defaultdict
from decimal import Decimal
from io import BytesIO

import numpy
from rest_framework import status
from rest_framework.exceptions import ErrorDetail, ParseError
from rest_framework.settings import api_settings
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

import orjson
from drf_orjson_renderer.encoders import DjangoNumpyJSONEncoder
from drf_orjson_renderer.parsers import ORJSONParser
from drf_orjson_renderer.renderers import ORJSONRenderer


class IterObj:
    def __init__(self, value):
        self.value = value

    def __iter__(self):
        for x in range(self.value):
            yield self.value


class RendererTestCase(unittest.TestCase):
    def setUp(self):
        self.renderer = ORJSONRenderer()
        self.data = {
            "a": [1, 2, 3],
            "b": True,
            "c": 1.23,
            "d": "test",
            "e": {"foo": "bar"},
        }

    def test_basic_data_structures_rendered_correctly(self):

        rendered = self.renderer.render(self.data)
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, self.data)

    def test_renderer_works_correctly_when_media_type_and_context_provided(
        self,
    ):

        rendered = self.renderer.render(
            data=self.data, media_type="application/json", renderer_context={}
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, self.data)

    def test_renderer_works_correctly_with_browsable_api(self):
        """
        Ensure that formatted JSON is returned when called
        by the BrowsableAPIRenderer.
        """
        rendered = self.renderer.render(
            data=self.data,
            media_type="text/html",
            renderer_context={"indent": 4},
        )

        self.assertEqual(rendered, json.dumps(self.data, indent=4))

    def test_renderer_works_correctly_with_browsable_api_with_datetime(self):
        """
        When using the built-in json when called by the BrowsableAPIRenderer,
        ensure that native datetime.datetime objects are serialized correctly.
        """
        now = datetime.datetime.now()
        data = {"now": now}
        rendered = self.renderer.render(
            data=data, media_type="text/html", renderer_context={"indent": 4}
        )
        reloaded = orjson.loads(rendered)
        now_formatted = now.isoformat()
        django_formatted = now_formatted[:23] + now_formatted[26:]

        self.assertEqual(reloaded, {"now": django_formatted})

    def test_renderer_works_correctly_with_browsable_api_with_date(self):
        """
        When using the built-in json when called by the BrowsableAPIRenderer,
        ensure that native datetime.date objects are serialized correctly.
        """
        today = datetime.date.today()
        data = {"today": today}
        rendered = self.renderer.render(
            data=data, media_type="text/html", renderer_context={"indent": 4}
        )
        reloaded = orjson.loads(rendered)
        self.assertEqual(reloaded, {"today": today.isoformat()})

    def test_renderer_works_correctly_with_application_json(self):
        """
        Ensure that when application/json is requested by the client that the
        renderer returns un-indented JSON.
        """
        rendered = self.renderer.render(
            data=self.data,
            media_type="application/json",
            renderer_context={"indent": 4},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, self.data)

    def test_renderer_works_correctly_with_ordered_dict(self):
        """
        Ensure that collections.OrderedDict is serialized correctly.
        """
        rendered = self.renderer.render(
            data=OrderedDict(self.data),
            media_type="application/json",
            renderer_context={},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, self.data)

    def test_renderer_works_correctly_with_default_dict(self):
        """
        Ensure that collections.defaultdict is serialized correctly.
        """
        d = defaultdict(int)
        d["1"] = 1
        rendered = self.renderer.render(
            data=d, media_type="application/json", renderer_context={}
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, d)

    def test_renderer_works_correctly_with_decimal_as_str(self):
        """
        Ensure that decimal.Decimal is serialized correctly when
        rest_framework.settings.api_settings.COERCE_DECIMAL_TO_STRING=True
        """
        api_settings.COERCE_DECIMAL_TO_STRING = True
        rendered = self.renderer.render(
            data=Decimal("1.0"),
            media_type="application/json",
            renderer_context={},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, str(Decimal("1.0")))

    def test_renderer_works_correctly_with_decimal_as_float(self):
        """
        Ensure that decimal.Decimal is serialized correctly when
        rest_framework.settings.api_settings.COERCE_DECIMAL_TO_STRING=False
        """
        api_settings.COERCE_DECIMAL_TO_STRING = False
        rendered = self.renderer.render(
            data=Decimal("1.0"),
            media_type="application/json",
            renderer_context={},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, float(Decimal("1.0")))

    def test_renderer_works_correctly_with_error_detail(self):
        """
        Ensure that rest_framework.exceptions.ErrorDetail
        is serialized correctly.
        """
        rendered = self.renderer.render(
            data=ErrorDetail("Test", code=status.HTTP_400_BAD_REQUEST),
            media_type="application/json",
            renderer_context={},
        )
        self.assertEqual(rendered.decode(), '"Test"')

    def test_renderer_works_correctly_with_return_dict(self):
        """
        Ensure that rest_framework.utils.serializer_helpers.ReturnDict
        is serialized correctly.
        """
        rendered = self.renderer.render(
            data=ReturnDict(self.data, serializer=None),
            media_type="application/json",
            renderer_context={},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, self.data)

    def test_renderer_works_correctly_with_return_list(self):
        """
        Ensure that rest_framework.utils.serializer_helpers.ReturnList
        is serialized correctly.
        """
        test_list = [{"1": 1}]
        rendered = self.renderer.render(
            data=ReturnList(test_list, serializer=None),
            media_type="application/json",
            renderer_context={},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, test_list)

    def test_renderer_works_correctly_with_numpy_array(self):
        """
        Ensure that numpy.array is serialized correctly.
        """
        data = numpy.array([1])
        rendered = self.renderer.render(
            data=data, media_type="application/json", renderer_context={}
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, data)

    def test_renderer_works_correctly_with_numpy_int(self):
        """
        Ensure that numpy.integer is serialized correctly.
        """
        data = numpy.int32(0)
        rendered = self.renderer.render(
            data=data, media_type="application/json", renderer_context={}
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, data)

    def test_renderer_works_correctly_with_numpy_floating(self):
        """
        Ensure that numpy.floating is serialized correctly.
        """
        data = numpy.float32(0.0)
        rendered = self.renderer.render(
            data=data, media_type="application/json", renderer_context={}
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, data)

    def test_renderer_works_correctly_with_uuid(self):
        """
        Ensure that a UUID is serialized correctly.
        """
        uuid_var = uuid.uuid4()
        data = {"value": uuid_var}
        rendered = self.renderer.render(
            data=data, media_type="application/json", renderer_context={}
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, {"value": str(uuid_var)})

    def test_renderer_works_correctly_with_iter(self):
        """
        Ensure that a custom iterables are serialized correctly.
        """
        iter_obj = IterObj(5)
        data = {"value": iter_obj}
        rendered = self.renderer.render(
            data=data, media_type="application/json", renderer_context={}
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, {"value": list(IterObj(5))})

    def test_renderer_works_with_provided_default(self):
        """
        Ensure that a user can pass a default function to the renderer.
        """

        def default(obj):
            if isinstance(obj, dict):
                return dict(obj)

        data = OrderedDict({"value": "test"})
        rendered = self.renderer.render(
            data=data,
            media_type="application/json",
            renderer_context={"default_function": default},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, dict(data))

    def test_renderer_works_with_provided_default_is_none(self):
        """
        Ensure that a user can pass a default function value of None
        to the renderer.
        """

        data = {"value": "test"}
        rendered = self.renderer.render(
            data=data,
            media_type="application/json",
            renderer_context={"default_function": None},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, dict(data))

    def test_renderer_works_with_provided_default_is_none_raises_error(self):
        """
        This is a sanity check -- if the user can pass None as the
        default but the data cannot be serialized by orjson it should
        raise a JSONEncodeError.
        """

        data = OrderedDict({"value": "test"})
        with self.assertRaises(orjson.JSONEncodeError):
            self.renderer.render(
                data=data,
                media_type="application/json",
                renderer_context={"default_function": None},
            )

    def test_built_in_renderer_works_correctly_with_numpy_int(self):
        """
        Ensure that numpy.int is serialized correctly with Python's
        built-in json module.
        """
        data = numpy.int32(0)
        rendered = self.renderer.render(
            data=data,
            media_type="text/html",
            renderer_context={
                "django_encoder_class": DjangoNumpyJSONEncoder,
                "indent": 4,
            },
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, data)

    def test_built_in_renderer_works_correctly_with_numpy_floating(self):
        """
        Ensure that numpy.floating is serialized correctly with Python's
        built-in json module.
        """
        data = numpy.float32(0.0)
        rendered = self.renderer.render(
            data=data,
            media_type="text/html",
            renderer_context={
                "django_encoder_class": DjangoNumpyJSONEncoder,
                "indent": 4,
            },
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, data)


class ParserTestCase(unittest.TestCase):
    def setUp(self):
        self.parser = ORJSONParser()
        self.data = {
            "a": [1, 2, 3],
            "b": True,
            "c": 1.23,
            "d": "test",
            "e": {"foo": "bar"},
        }

    def test_basic_data_structures_parsed_correctly(self):
        dumped = orjson.dumps(self.data)
        parsed = self.parser.parse(BytesIO(dumped))

        self.assertEqual(parsed, self.data)

    def test_parser_works_correctly_when_media_type_and_context_provided(self):
        dumped = orjson.dumps(self.data)
        parsed = self.parser.parse(
            stream=BytesIO(dumped),
            media_type="application/json",
            parser_context={},
        )

        self.assertEqual(parsed, self.data)

    def test_parser_raises_decode_error(self):
        """
        Ensure that the rest_framework.errors.ParseError is raised when sending
        invalid JSON from the client.
        """
        with self.assertRaises(ParseError):
            self.parser.parse(
                stream=BytesIO(b'{"value": NaN}'),
                media_type="application/json",
                parser_context={},
            )


if __name__ == "__main__":
    from django.conf import settings

    settings.configure()
    unittest.main()
