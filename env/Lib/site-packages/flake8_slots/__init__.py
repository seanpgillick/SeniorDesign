#!/usr/bin/env python3
#
#  __init__.py
"""
A Flake8 plugin to require ``__slots__`` to be defined for subclasses of immutable types.
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import ast
import re
from typing import Iterator, Union

# 3rd party
import flake8_helper

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020-2021 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.1.5"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["Visitor", "Plugin", "SLOT000", "SLOT001", "SLOT002"]

SLOT000 = "SLOT000 Define __slots__ for subclasses of str"
SLOT001 = "SLOT001 Define __slots__ for subclasses of tuple"
SLOT002 = "SLOT002 Define __slots__ for subclasses of collections.namedtuple"
# SLOT003 # Don't reuse

# TODO: custom immutable types - config option and SLOT004


class ClassBodyVisitor(ast.NodeVisitor):
	"""
	AST visitor to determine whether a class body defines ``__slots__``.
	"""

	#: :py:obj:`True` if the class defines ``__slots__``.
	has_slots: bool = False

	def visit_Assign(self, node: ast.Assign):
		for target in node.targets:
			if isinstance(target, ast.Name) and target.id == "__slots__":
				self.has_slots = True

	def visit_AnnAssign(self, node: ast.AnnAssign):
		if isinstance(node.target, ast.Name) and node.target.id == "__slots__":
			self.has_slots = True


def resolve_dotted_name(name: Union[str, ast.Name, ast.Attribute, ast.Call, ast.Subscript]) -> Iterator[str]:
	if isinstance(name, str):
		yield name
	elif isinstance(name, ast.Name):
		yield name.id
	elif isinstance(name, ast.Attribute):
		yield from resolve_dotted_name(name.value)  # type: ignore
		yield from resolve_dotted_name(name.attr)
	elif isinstance(name, ast.Subscript):
		yield from resolve_dotted_name(name.value)  # type: ignore
	elif isinstance(name, ast.Call):
		yield from resolve_dotted_name(name.func)  # type: ignore


_enum_re = re.compile(r"\.?Enum")


class Visitor(flake8_helper.Visitor):
	"""
	AST visitor to identify missing ``__slots__`` for subclasses of immutable types.
	"""

	def visit_ClassDef(self, node: ast.ClassDef):  # noqa: D102

		bases = ['.'.join(resolve_dotted_name(base)) for base in node.bases]  # type: ignore

		is_str = False

		if "str" in bases or "builtins.str" in bases:  # SLOT000
			if not any(map(_enum_re.match, bases)):
				is_str = True

		if "tuple" in bases or "builtins.tuple" in bases:  # SLOT001
			is_tuple = True
		elif "Tuple" in bases or "typing.Tuple" in bases:  # SLOT001
			is_tuple = True
		else:
			is_tuple = False

		is_collections_namedtuple = "namedtuple" in bases or "collections.namedtuple" in bases  # SLOT002

		if not any([is_str, is_tuple, is_collections_namedtuple]):
			return

		body_visitor = ClassBodyVisitor()
		body_visitor.visit(node)

		if not body_visitor.has_slots:
			if is_str:
				self.report_error(node, SLOT000)
			if is_tuple:
				self.report_error(node, SLOT001)
			if is_collections_namedtuple:
				self.report_error(node, SLOT002)


class Plugin(flake8_helper.Plugin[Visitor]):
	"""
	A Flake8 plugin to identify missing ``__slots__`` for subclasses of immutable types.

	:param tree: The abstract syntax tree (AST) to check.
	"""

	name: str = __name__
	version: str = __version__  #: The plugin version
	visitor_class = Visitor
