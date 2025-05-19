#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT
# Copyright (c) 2025 OMGnotThatGuy
# Licensed under the MIT License; see the LICENSE file for details.

"""
A small command‑line script to discover all Exception subclasses in a given
Python module or package, then display their inheritance tree.
"""

from __future__ import annotations
import argparse
import inspect
import importlib
import pkgutil
import sys
from typing import Optional, TypeAlias

ExcSet: TypeAlias = set[type[Exception]]
ExcChildMap: TypeAlias = dict[type[Exception], list[type[Exception]]]


def find_exceptions_recursive(root_name: str) -> ExcSet:
    """
    Import root_name, walk its submodules, and return
    a set of all Exception subclasses defined in them.
    """
    try:
        root = importlib.import_module(root_name)
    except ImportError as e:
        print(f"Error: could not import '{root_name}': {e}", file=sys.stderr)
        sys.exit(10)

    modules = [(root_name, root)]
    # if it's a package, walk its submodules
    if hasattr(root, "__path__"):
        for _finder, name, _ispkg in pkgutil.walk_packages(root.__path__, root_name + "."):
            try:
                submod = importlib.import_module(name)
                modules.append((name, submod))
            except ImportError:
                # skip modules that fail to import
                continue

    exceptions = set()
    for modname, mod in modules:
        for _, cls in inspect.getmembers(mod, inspect.isclass):
            # only include classes actually defined in this module
            if cls.__module__ != modname:
                continue
            if issubclass(cls, Exception):
                exceptions.add(cls)

    return exceptions


def get_display_name(cls: type[Exception]) -> str:
    """Pretty-print: builtins drop module, others show full dotted path."""
    if cls.__module__ == "builtins":
        return cls.__name__
    return f"{cls.__module__}.{cls.__name__}"


def build_inheritance_tree(exc_classes: ExcSet, all_paths: bool = False) -> tuple[type[Exception], ExcChildMap, ExcSet]:
    """
    Given a set of exception classes, build a map of parent → [children]
    that spans from Exception down through all their ancestors.
    """
    # always include Exception itself as the root
    root = Exception
    nodes = {root}

    # gather every exception class plus exception ancestors up to Exception
    for cls in exc_classes:
        for ancestor in cls.__mro__:
            if ancestor is object:
                break
            # only include Exception subclasses (skip non-Exception bases)
            if not issubclass(ancestor, Exception):
                continue
            nodes.add(ancestor)

    # find each node's parent (closest ancestor in nodes)
    parent_map = {}
    for cls in nodes:
        if cls is root:
            continue
        for anc in cls.__mro__[1:]:
            if anc in nodes:
                parent_map[cls] = anc
                break

    # invert into children map
    children: ExcChildMap = {}
    for child, parent in parent_map.items():
        children.setdefault(parent, []).append(child)

    # sort children lists for stable output
    for lst in children.values():
        lst.sort(key=lambda c: get_display_name(c).lower())
    # detect classes with multiple direct Exception-parents
    multi_parents = {
        cls for cls in nodes
        if cls is not root and len([base for base in cls.__bases__ if base in nodes]) > 1
    }

    if all_paths:
        # duplicate multi-parent classes under each parent
        for cls in multi_parents:
            direct_parents = [base for base in cls.__bases__ if base in nodes]
            for base in direct_parents:
                if cls not in children.get(base, []):
                    children.setdefault(base, []).append(cls)
        # re-sort children lists after adding duplicates
        for lst in children.values():
            lst.sort(key=lambda c: get_display_name(c).lower())

    return root, children, multi_parents


def _print_subtree(
    node: type[Exception],
    children_map: ExcChildMap,
    indent: str = "",
    compact: bool = False,
    multi_parents: Optional[ExcSet] = None,
) -> None:
    """Helper: print all descendants of node under the current indent."""
    if multi_parents is None:
        multi_parents = set()
    kids = children_map.get(node, [])
    for idx, child in enumerate(kids):
        # if previous sibling had children, insert a blank line at this indent
        if not compact and idx > 0:
            prev = kids[idx - 1]
            if children_map.get(prev):
                print(indent + "|")
        last = idx == len(kids) - 1
        branch = "└── " if last else "├── "
        suffix = " *" if child in multi_parents else ""
        print(indent + branch + get_display_name(child) + suffix)
        # recurse into children
        if children_map.get(child):
            new_indent = indent + ("    " if last else "│   ")
            _print_subtree(child, children_map, new_indent, compact, multi_parents)


def print_tree(
    root: type[Exception],
    children_map: ExcChildMap,
    multi_parents: ExcSet,
    compact: bool = False,
) -> None:
    """Print the full tree, starting with Exception."""
    # Print the root exception
    print(get_display_name(root))
    # Iterate over first-level children
    children = children_map.get(root, [])
    for idx, child in enumerate(children):
        # blank line before each root child if not in compact mode
        if not compact:
            print("|")
        # branch character
        last = idx == len(children) - 1
        branch = "└── " if last else "├── "
        suffix = " *" if child in multi_parents else ""
        print(branch + get_display_name(child) + suffix)
        # prepare indent for subtree
        new_indent = "" + ("    " if last else "│   ")
        _print_subtree(child, children_map, new_indent, compact, multi_parents)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Find all Exception subclasses in a module/package and show their inheritance tree.",
        epilog="Classes marked with '*' indicate classes inheriting from multiple Exception bases. Use -a or --all-paths to see them.",
    )
    p.add_argument(
        "module",
        help="Name of the module or package to inspect, e.g. 'requests' or 'my_pkg.subpkg'",
        metavar="module|package.submodule",
    )
    p.add_argument(
        "-a", "--all-paths",
        action="store_true",
        dest="all_paths",
        help="Duplicate classes inheriting from multiple Exception bases under each parent class"
    )
    p.add_argument(
        "-c", "--compact",
        action="store_true",
        dest="compact",
        help="Use compact output (no extra blank lines)"
    )

    args = p.parse_args()

    excs = find_exceptions_recursive(args.module)
    if not excs:
        print(f"No Exception subclasses found in '{args.module}'.", file=sys.stderr)
        sys.exit(1)

    root, child_map, multi_parents = build_inheritance_tree(excs, all_paths=args.all_paths)
    print_tree(root, child_map, multi_parents, compact=args.compact)

if __name__ == "__main__":
    main()