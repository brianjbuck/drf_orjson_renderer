import datetime
import json
import unittest
import uuid
from collections import OrderedDict, defaultdict
from decimal import Decimal
from io import BytesIO

import numpy
import orjson
import pytest
from django.db.models import TextChoices
from django.utils.functional import lazy
from rest_framework import status
from rest_framework.exceptions import ErrorDetail, ParseError
from rest_framework.settings import api_settings
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList

from drf_orjson_renderer.encoders import DjangoNumpyJSONEncoder
from drf_orjson_renderer.parsers import ORJSONParser
from drf_orjson_renderer.renderers import ORJSONRenderer


class IterObj:
    def __init__(self, value):
        self.value = value

    def __iter__(self):
        for x in range(self.value):
            yield self.value


class ListLikeObj(list):
    pass


class ToListObj:
    def tolist(self):
        return [1]


class ChoiceObj(TextChoices):
    FIELD = "option-one", "Option One"


UUID_PARAM = uuid.uuid4()
string_doubler = lazy(lambda i: i + i, str)

DATA_PARAMS = [
    (OrderedDict({"a": "b"}), {"a": "b"}, False),
    (ListLikeObj([1]), [1], False),
    (Decimal("1.0"), "1.0", True),
    (Decimal("1.0"), 1.0, False),
    ("Test", "Test", False),
    (UUID_PARAM, str(UUID_PARAM), False),
    (string_doubler("hello"), "hellohello", False),  # Promise
    (ToListObj(), [1], False),
    (IterObj(1), [1], False),
    (ReturnList([{"1": 1}], serializer=None), [{"1": 1}], False),
    (ReturnDict({"a": "b"}, serializer=None), {"a": "b"}, False),
    (ChoiceObj.FIELD, "option-one", False,)
]


@pytest.mark.parametrize(
    "test_input,expected,coerce_decimal",
    DATA_PARAMS,
    ids=[type(item[0]) for item in DATA_PARAMS],
)
def test_built_in_default_method(test_input, expected, coerce_decimal):
    """Ensure that the built-in default method works for all data types."""
    api_settings.COERCE_DECIMAL_TO_STRING = True if coerce_decimal else False
    result = ORJSONRenderer.default(test_input)
    assert result == expected


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

    def test_default_media_type(self):
        assert self.renderer.media_type == "application/json"

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
            data=self.data, media_type="text/html", renderer_context=None,
        )

        self.assertEqual(rendered.decode(), json.dumps(self.data, indent=2))

        rendered = self.renderer.render(
            data=self.data, media_type="text/html; q=1.0", renderer_context=None,
        )

        self.assertEqual(rendered.decode(), json.dumps(self.data, indent=2))

    def test_renderer_works_correctly_with_browsable_api_with_datetime(self):
        """
        When using the built-in json when called by the BrowsableAPIRenderer,
        ensure that native datetime.datetime objects are serialized correctly.
        """
        now = datetime.datetime.now()
        data = {"now": now}
        rendered = self.renderer.render(
            data=data, media_type="text/html", renderer_context=None
        )
        reloaded = orjson.loads(rendered)
        now_formatted = now.isoformat()

        self.assertEqual(reloaded, {"now": now_formatted})

    def test_renderer_works_correctly_with_browsable_api_with_date(self):
        """
        When using the built-in json when called by the BrowsableAPIRenderer,
        ensure that native datetime.date objects are serialized correctly.
        """
        today = datetime.date.today()
        data = {"today": today}
        rendered = self.renderer.render(
            data=data, media_type="text/html", renderer_context=None
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
            renderer_context=None,
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
        data = {"this is a set", "that orjson cannot serialize"}
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
            renderer_context={"django_encoder_class": DjangoNumpyJSONEncoder,},
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
            renderer_context={"django_encoder_class": DjangoNumpyJSONEncoder,},
        )
        reloaded = orjson.loads(rendered)

        self.assertEqual(reloaded, data)

    def test_built_in_renderer_works_correctly_with_none(self):
        """
        Ensure that empty response won't generate 'null' as result.
        """
        data = None
        rendered = self.renderer.render(
            data=data, media_type="application/json",
        )

        self.assertEqual(b"", rendered)


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
