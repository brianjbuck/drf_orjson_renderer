import unittest
from io import BytesIO

import orjson
from rest_framework.exceptions import ParseError

from drf_orjson_renderer.parsers import ORJSONParser


class ParserTestCase(unittest.TestCase):
    """Tests for ORJSONParser focusing on DRF integration."""

    def setUp(self):
        self.parser = ORJSONParser()
        self.data = {
            "a": [1, 2, 3],
            "b": True,
            "c": 1.23,
            "d": "test",
            "e": {"foo": "bar"},
        }

    def test_media_type_is_set_correctly(self):
        """Verify the parser declares the correct media type."""
        self.assertEqual(self.parser.media_type, "application/json")

    def test_basic_parsing(self):
        """Test basic JSON parsing without context."""
        dumped = orjson.dumps(self.data)
        parsed = self.parser.parse(BytesIO(dumped))

        self.assertEqual(parsed, self.data)

    def test_parsing_with_media_type_and_context(self):
        """Test parsing with media_type and parser_context provided."""
        dumped = orjson.dumps(self.data)
        parsed = self.parser.parse(
            stream=BytesIO(dumped),
            media_type="application/json",
            parser_context={},
        )

        self.assertEqual(parsed, self.data)

    def test_parsing_with_custom_encoding(self):
        """Test that custom encoding in parser_context is respected."""
        data = {"text": "hello"}
        dumped = orjson.dumps(data)

        parsed = self.parser.parse(
            stream=BytesIO(dumped),
            parser_context={"encoding": "utf-8"},
        )

        self.assertEqual(parsed, data)

    def test_parser_wraps_orjson_errors_in_parse_error(self):
        """
        Ensure that orjson ValueError is wrapped in DRF's ParseError.
        """
        with self.assertRaises(ParseError) as context:
            self.parser.parse(
                stream=BytesIO(b'{"value": NaN}'),
                media_type="application/json",
                parser_context={},
            )

        # Verify it's a ParseError with helpful message
        self.assertIn("JSON parse error", str(context.exception))

    def test_parser_handles_unicode_decode_errors(self):
        """
        Ensure that invalid UTF-8 bytes raise ParseError (issue #29).
        """
        # Invalid UTF-8 byte sequence
        invalid_utf8 = b"\x80\x81\x82"
        with self.assertRaises(ParseError):
            self.parser.parse(
                stream=BytesIO(invalid_utf8),
                media_type="application/json",
                parser_context={},
            )


if __name__ == "__main__":
    from django.conf import settings

    settings.configure()
    unittest.main()
