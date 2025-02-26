"""Scratch"""

# from typing import Any, Iterator, is_typeddict, TypedDict
# import inspect
# import re

# COMMENTS_PATTERN = re.compile(
#     r"(?P<block_comment>(?: *# *.+? *\n)*)"
#     r" *(?P<name>\w+): *(?P<type>\w+) *(?:# *(?P<inline_comment>.+))?\n"
# )


# class EntryComments(TypedDict):
#     block_comments: list[str]
#     inline_comment: str

# CommentsCache = dict[str, EntryComments]

# def build_comments_cache_name(cls_name: str, key: str) -> str:
#     return f"{cls_name}/{key}"

# def get_comments(typed_dict_cls: Any) -> CommentsCache:

#     comments: CommentsCache = {}

#     def _get_comments(typed_dict_cls: Any) -> None:
#         nonlocal comments
#         typed_dict_name: str = typed_dict_cls.__name__

#         # get comments from all inherit fields from parent TypedDict
#         for base in typed_dict_cls.__orig_bases__:
#             if is_typeddict(base):
#                 _get_comments(base)

#         # get comments from current TypedDict
#         source: str = inspect.getsource(typed_dict_cls)
#         matches: Iterator[re.Match[str]] = COMMENTS_PATTERN.finditer(source)
#         for match in matches:
#             block_comment: str = match.group('block_comment').strip()
#             name = match.group('name')
#             inline_comment: str = match.group('inline_comment') or ""
#             block_comments: list[str] = [
#                 comment.strip()[1:].strip()
#                 for comment in block_comment.split('\n') if comment.strip()
#             ]
#             comments[build_comments_cache_name(typed_dict_name, name)] = {
#                 "block_comments": block_comments,
#                 "inline_comment": inline_comment
#             }
#         # get comments from nested TypedDict
#         for _, type_def in typed_dict_cls.__annotations__.items():
#             if is_typeddict(type_def):
#                 _get_comments(type_def)

#     _get_comments(typed_dict_cls)
#     return comments

# class Courses(TypedDict, total=False):
#     # you can also add comments in the TypedDict
#     CS101: int
#     # Multi-line comments are also supported
#     # In this case, the comments in JSON5 will also be multi-line
#     # The entries of dictionaries that implement this TypedDict will be commented
#     ART101: int
#     HIS101: int  # a comment can also be in-line
#     # if a dictionary does not contain all the keys, only the keys that are
#     # present will be commented
#     LIT101: int

# class Creature(TypedDict):
#     height: int  # height of the creature
#     # weight of the creature
#     # weight cannot be too high!
#     weight: int

# class Human(Creature):
#     # age of the human
#     age: int  # human can be very old!
#     # name of the human
#     name: str
#     # human can be very intelligent
#     courses: Courses

# com = get_comments(Human)
# for key, value in com.items():
#     print(key, value)
