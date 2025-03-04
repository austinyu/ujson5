"""CLI supports"""

import argparse


def main():
    """main"""
    parser = argparse.ArgumentParser(
        prog="ujson5",
        description="ujson5 is a JSON5 parser and encoder.",
        epilog="For more information, visit https://austinyu.github.io/ujson5/",
    )
    parser.add_argument("target_path", help="Path to the target JSON5 file")
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
    args = parser.parse_args()
    assert args


if __name__ == "__main__":
    main()
