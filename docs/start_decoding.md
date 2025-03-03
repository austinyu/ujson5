# Deserializing / Decoding

`ujson5` API is similar to the standard `json` module. If you are familiar with the `json` module, you will find `ujson5` easy to use. Like the `json` module, `ujson5` provides two main functions for decoding JSON5 strings to python objects: [load][ujson5.load] and [loads][ujson5.loads].

When using [load][ujson5.load] or [loads][ujson5.loads] functions, you can either pass in parameters or pass in a subclass of [JSON5Decoder][ujson5.decoder.Json5Decoder] to customize the deserialization process. When passing in the `object_hook` or `pairs_hook` parameter, you can exploit types exposed by the `ujson5` module to enforce type checking. Here is an example:

```python

`ujson5` provides some useful type variables that will help you to enforce type checking when writing object hook functions. Here is an example:

```python
import ujson5

def my_obj_hook(dct: ujson5.ObjectHookArg) -> dict:
    dct["count"] = len(dct)
    return dct

data = '{"key": "value", "key2": "value2"}'
deserialized = ujson5.loads(data, object_hook=my_obj_hook)
assert deserialized == {"key": "value", "key2": "value2", "count": 2}
```

Similarly, you also have the type variable for object pairs hook. Here is an example:

```python
import ujson5

def my_pairs_hook(pairs: ujson5.PairsHookArg) -> dict:
    dct_pairs = dict(pairs)
    dct_pairs["count"] = len(dct_pairs)
    return dct_pairs

data = '{"key": "value", "key2": "value2"}'
deserialized = ujson5.loads(data, pairs_hook=my_pairs_hook)
assert deserialized == {"key": "value", "key2": "value2", "count": 2}
```

!!! View full API
    Checkout the [API Reference](api_reference/decoder.md) for more details on decoding.
