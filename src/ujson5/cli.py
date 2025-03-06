"""CLI supports"""

import argparse
from collections.abc import Sequence
import json
import sys

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
        "infile",
        nargs="?",
        help="a JSON5 file to be validated or converted to JSON",
        default=None,
    )
    parser.add_argument(
        "outfile",
        nargs="?",
        help="write the output of infile to outfile",
        default=None,
    )
    parser.add_argument(
        "-v", "--version", action="store_true", help="show the version of ujson5"
    )
    parser.add_argument(
        "-i", "--info", action="store_true", help="show version and os information"
    )
    parser.add_argument(
        "--sort-keys",
        action="store_true",
        help="sort the output of dictionaries alphabetically by key",
    )
    parser.add_argument(
        "--no-ensure-ascii",
        action="store_true",
        help="disable escaping of non-ASCII characters",
    )

    parser.add_argument(
        "--no-indent",
        action="store_true",
        help="separate items with spaces rather than newlines",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="suppress all whitespace separation (most compact)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="separate items with newlines and use this number of spaces for indentation",
    )

    args = parser.parse_args(test_args)
    if args.info:
        print(version_info())
        return
    if args.version:
        print(VERSION)
        return
    if args.infile is None and sys.stdin.isatty():
        print(ERR_NO_TARGET)
        parser.print_help()
        return
    try:
        if args.infile is not None:
            with open(args.infile, "r", encoding="utf8") as file:
                json5_obj = loads(file.read())
        else:
            json5_obj = loads(sys.stdin.read())
    except FileNotFoundError:
        print(ERR_TARGET_NOT_EXIST)
        return
    except JSON5DecodeError as e:
        print(f"{DECODING_ERROR} {args.infile}:")
        print(e)
        return
    if args.no_indent:
        indent: int | None = None
        separators: tuple[str, str] | None = (", ", ": ")
    elif args.compact:
        indent = None
        separators = (",", ":")
    else:
        indent = args.indent
        separators = None
    if args.outfile:
        print("output to", args.outfile)
        with open(args.outfile, "w", encoding="utf8") as file:

            json.dump(
                json5_obj,
                file,
                indent=indent,
                separators=separators,
                ensure_ascii=not args.no_ensure_ascii,
                sort_keys=args.sort_keys,
            )
    else:
        print(JSON_CONVERTED)
        print(
            json.dumps(
                json5_obj,
                indent=indent,
                separators=separators,
                ensure_ascii=not args.no_ensure_ascii,
                sort_keys=args.sort_keys,
            )
        )
