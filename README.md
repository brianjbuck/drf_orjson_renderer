Django Rest Framework ORJSON Renderer
=====================================

`drf_orjson_renderer` is JSON renderer and parser for Django Rest Framework
using the [orjson](https://github.com/ijl/orjson) library. Backed by
[Rust](https://www.rust-lang.org/), orjson is safe, correct and _fast_. ⚡️

In addition, unlike some performance optimized DRF renderers, It also renders
pretty printed JSON when requests are made via RestFramework's BrowsableAPI.

You get:
- The safety of Rust
- The speed of orjson when requests are made with `Accept: appliation/json` HTTP
  header or when requests are made with an unspecified `Accept` header.
- The convenience of formatted output when requested with `Accept: text/html`.
- The ability to pass your own `default` function definition.


## Installation

`pip install drf_orjson_renderer`

You can then set the `ORJSONRenderer` class as your default renderer in your `settings.py`

```Python
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "drf_orjson_renderer.renderers.ORJSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
}
```

Also you can set the `ORJSONParser` class as your default parser in your `settings.py`

```Python
REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": (
        "drf_orjson_renderer.parsers.ORJSONParser",
    ),
}
```

## Passing Your Own `default` Function

By default, the `ORJSONRenderer` will pass a `default` function as a helper for
serializing objects that orjson doesn't recognize. That should cover the most
common cases found in a Django web application. If you find you have an object
it doesn't recognize you can pass your own default function by overriding the
`get_renderer_context()` method of your view:

```Python
from rest_framework.views import APIView
from rest_framework.response import Response


class MyView(APIView):
    def default(self, obj):
        if isinstance(obj, MyComplexData):
            return dict(obj)

    def get_renderer_context(self):
        renderer_context = super().get_renderer_context()
        renderer_context["default_function"] = self.default
        return renderer_context

    def get(self, request, *args, **kwargs):
        my_complex_data = MyComplexData()
        return Response(data=my_complex_data)
```

If you know your data is already in a format orjson natively
[recognizes](https://github.com/ijl/orjson/#types) you can get a small
performance boost by passing `None` to the `renderer_context`:

```Python
def get_renderer_context(self):
    renderer_context = super().get_renderer_context()
    renderer_context["default_function"] = None
    return renderer_context
```

In order to take advantage of the RestFramework Browsable API, when the
requested media type is not `application/json`, the ORJSON renderer will fall
back to using the built-in Python `json` module to pretty print your output.
If you have overriden the default function its possible that you may need to
do this as well for the `json` encoder class:

```Python
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.views import APIView
from rest_framework.response import Response


class MyJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, MyComplexData):
            return dict(obj)
        return super().default(obj)

class MyView(APIView):


    def get_renderer_context(self):
        renderer_context = super().get_renderer_context()
        renderer_context["django_encoder_class"] = MyJSONEncoder
        return renderer_context

    def get(self, request, *args, **kwargs):
        my_complex_data = MyComplexData()
        return Response(data=my_complex_data)
```

## Benchmarks
See the [orjson Benchmarks](https://github.com/ijl/orjson#performance) for more information
