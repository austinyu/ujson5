"""CLI supports"""

import argparse
from collections.abc import Sequence
import json

from .__version__ import version_info, VERSION
from .decoder import loads
from .core import JSON5DecodeError

ERR_NO_TARGET: str = "No target file specified."
ERR_TARGET_NOT_EXIST: str = "Target is not a file or does not exist."
VALID_JSON5: str = "Valid JSON5"
JSON_CONVERTED: str = "JSON5 converted to JSON"
DECODING_ERROR: str = "Error found when parsing JSON5 file"


def main(test_args: Sequence[str] | None = None) -> None:
    """main cli function"""
    parser = argparse.ArgumentParser(
        prog="ujson5",
        description="ujson5 is a JSON5 parser and encoder.",
        epilog="For more information, visit https://austinyu.github.io/ujson5/",
    )
    parser.add_argument(
        "target_path",
        nargs="?",
        help="Path to the target JSON5 file",
        default=None,
    )
    parser.add_argument("-o", "--out-file", help="Path to the output JSON5 file")
    parser.add_argument(
        "-s", "--space", type=int, help="Indentation level for the output JSON5 file"
    )
    parser.add_argument(
        "-v",
        "--validate",
        action="store_true",
        help="Validate the input JSON5 file without outputting",
    )
    parser.add_argument(
        "-V", "--version", action="store_true", help="Show the version of ujson5"
    )
    parser.add_argument(
        "-i", "--info", action="store_true", help="Show version and os information"
    )
    args = parser.parse_args(test_args)
    if args.info:
        print(version_info())
        return
    if args.version:
        print(VERSION)
        return
    if args.target_path is None:
        print(ERR_NO_TARGET)
        parser.print_help()
        return
    try:
        with open(args.target_path, "r", encoding="utf8") as file:
            json5_obj = loads(file.read())
    except FileNotFoundError:
        print(ERR_TARGET_NOT_EXIST)
        return
    except JSON5DecodeError as e:
        print(f"{DECODING_ERROR} {args.target_path}:")
        print(e)
        return
    if args.validate:
        print(VALID_JSON5)
        return
    if args.out_file:
        print("output to", args.out_file)
        with open(args.out_file, "w", encoding="utf8") as file:
            json.dump(json5_obj, file, indent=args.space)
    else:
        print(JSON_CONVERTED)
        print(json.dumps(json5_obj, indent=args.space))
