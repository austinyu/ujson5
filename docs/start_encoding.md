# Serializing / encoding

`ujson5` API is similar to the standard `json` module with some additional features to support JSON5 syntax. If you are familiar with the `json` module, you will find `ujson5` easy to use. Like the `json` module, `ujson5` provides two main functions for encoding python objects to JSON5 strings: [dump][ujson5.dump] and [dumps][ujson5.dumps].

When using [dump][ujson5.dump] or [dumps][ujson5.dumps] functions, you can either pass in parameters or pass in a subclass of [JSON5Encoder][ujson5.encoder.JSON5Encoder] to customize the serialization process. When passing in the `default` parameter, you can exploit types exposed by the `ujson5` module to enforce type checking. Here is an example:

```python
import ujson5
from typing import Any

def default(obj: Any) -> ujson5.Serializable:
    if isinstance(obj, complex):
        return {"__complex__": True, "real": obj.real, "imag": obj.imag}
    elif isinstance(obj, set):
        return list(obj)
    raise TypeError(f"Object of type '{obj.__class__.__name__}' is not JSON serializable")

data = {"complex": 1 + 2j}
serialized = ujson5.dumps(data, default=default)
print(serialized)
```

## Comments Extraction

!!! warning
    Comment extraction is currently only fully supported on Python 3.12+. On older
    versions, the function will still work but will not extract all comments from the
    parent TypedDicts.

!!! Note
    Comments will only be extracted and added when `indent` argument to [dumps][ujson5.dumps], [dump][ujson5.dump] or [JSON5Encoder][ujson5.encoder.JSON5Encoder] is set to a non-`None` value. Because if `indent` is `None`, the output will be a single line string and comments will not be added.

JSON5 supports adding comments to the data using the `//` and `/* */` syntax. These comments are ignored during the parsing process. Here is an example:

```json
{
    // Single line comment
    "key": "value",
    /* Multi-line
    comment */
    "key2": "value2"
}
```

`ujson5` makes it easy to encode python objects with comments to json5 strings with comments.

Here is an example to show how it works.

```python
from typing import TypedDict

class Courses(TypedDict, total=False):
    # you can also add comments in the TypedDict
    CS101: int
    # Multi-line comments are also supported
    # In this case, the comments in JSON5 will also be multi-line
    ART101: int
    # You can also add comments to the TypedDict attributes
    HIS101: int  # a comment can also be in-line
    # if a dictionary does not contain all the keys, only the keys that are
    # present will be commented
    LIT101: int

my_courses = Courses(CS101=1, ART101=2, HIS101=3)
serialized = ujson5.dumps(my_courses, typed_dict_cls=Courses, indent=4)
assert serialized == '''{
    // you can also add comments in the TypedDict
    "CS101": 1,
    // Multi-line comments are also supported
    // In this case, the comments in JSON5 will also be multi-line
    "ART101": 2,
    // You can also add comments to the TypedDict attributes
    "HIS101": 3,  // a comment can also be in-line
}'''
```

As mentioned in the [official JSON5 website](https://json5.org/):

> JSON5 is an extension to the popular JSON file format that aims to be easier to write and maintain by hand (e.g. for config files).

Comments extraction is a very handy feature if you are going to use `TypeDict` to validate your config files. Just make sure to comment your `TypeDict` attributes and `ujson5` will take care of propagating your comments to the JSON5 output so that you can easily maintain your config files.

Here is a more complex example involving composite and inherited TypedDicts:

```python
from typing import TypedDict
import ujson5

class Courses(TypedDict, total=False):
    # you can also add comments in the TypedDict
    CS101: int
    # Multi-line comments are also supported
    # In this case, the comments in JSON5 will also be multi-line
    # The entries of dictionaries that implement this TypedDict will be commented
    ART101: int
    HIS101: int  # a comment can also be in-line
    # if a dictionary does not contain all the keys, only the keys that are
    # present will be commented
    LIT101: int

class Creature(TypedDict):
    height: int  # height of the creature
    # weight of the creature
    # weight cannot be too high!
    weight: int

class Human(Creature):  # (1)
    # age of the human
    age: int  # human can be very old!
    # name of the human
    name: str
    # human can be very intelligent
    courses: Courses  # hard-working human  (2)
    hobbies: list[str]  # hobbies takes a lot of time...

```

1. The `Human` TypedDict inherits from the `Creature` TypedDict. This means that the `Human` TypedDict will have all the attributes of the `Creature` TypedDict in addition to its own attributes. Dictionary entries that implement the `Human` TypedDict will have comments for the `Creature` TypedDict attributes as well as the `Human` TypedDict attributes.
2. The `courses` attribute of the `Human` TypedDict is a dictionary that implements the `Courses` TypedDict. This means that the dictionary entries that implement the `Human` TypedDict will have comments for the `Courses` TypedDict attributes as well as the `Human` TypedDict attributes.

Let's define some dictionaries that implement the `Human` TypedDict:

```python

Austin: Human = {
    "height": 180,
    "weight": 70,
    "age": 30,
    "name": "Austin",
    "courses": {
        "CS101": 90,
        "ART101": 80,
        "HIS101": 70,
    },
    "hobbies": ["reading", "swimming", "coding"],
}

assert ujson5.dumps(Austin, typed_dict_cls=Human, indent=4) == '''{
    // height of the creature
    "height": 180,
    // weight of the creature
    // weight cannot be too high!
    "weight": 70,
    // age of the human
    // human can be very old!
    "age": 30,
    // name of the human
    "name": "Austin",
    // human can be very intelligent
    // hard-working human
    "courses": {
        // you can also add comments in the TypedDict
        "CS101": 90,
        // Multi-line comments are also supported
        // In this case, the comments in JSON5 will also be multi-line
        // The entries of dictionaries that implement this TypedDict will be commented
        "ART101": 80,
        // You can also add comments to the TypedDict attributes
        "HIS101": 70,  // a comment can also be in-line
        // if a dictionary does not contain all the keys, only the keys that are
        // present will be commented
        "LIT101": null,
    },
    // hobbies takes a lot of time...
    "hobbies": [
        "reading",
        "swimming",
        "coding",
    ],
}'''

Jack: Human = {
    "height": 170,
    "weight": 80,
    "age": 25,
    "name": "Jack",
    "courses": {
        "CS101": 23,
        "ART101": 67,
        "LIT101": 12,
    },
    "hobbies": ["tennis", "writing", "coding"],
}

assert ujson5.dumps(Jack, typed_dict_cls=Human, indent=4) == '''{
    // height of the creature
    "height": 170,
    // weight of the creature
    // weight cannot be too high!
    "weight": 80,
    // age of the human
    // human can be very old!
    "age": 25,
    // name of the human
    "name": "Jack",
    // human can be very intelligent
    // hard-working human
    "courses": {
        // you can also add comments in the TypedDict
        "CS101": 23,
        // Multi-line comments are also supported
        // In this case, the comments in JSON5 will also be multi-line
        // The entries of dictionaries that implement this TypedDict will be commented
        "ART101": 67,
        // if a dictionary does not contain all the keys, only the keys that are
        // present will be commented
        "HIS101": null,
        // You can also add comments to the TypedDict attributes
        "LIT101": 12,
    },
    // hobbies takes a lot of time...
    "hobbies": [
        "tennis",
        "writing",
        "coding",
    ],
}'''
```

!!! View full API
    Checkout the [API Reference](api_reference/encoder.md) for more details on decoding.
