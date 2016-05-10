#!/usr/bin/env python3
"""Functions for testing the compliance of project files."""

import glob
import itertools

import isort
import nose.tools as nose
import pep8
import radon.complexity as radon


def test_pep8():
    """All source files should comply with PEP 8."""
    file_paths = itertools.chain(
        glob.iglob('automata/*/*.py'),
        glob.iglob('tests/*.py'))
    for file_path in file_paths:
        style_guide = pep8.StyleGuide(quiet=True)
        total_errors = style_guide.input_file(file_path)
        fail_msg = '{} does not comply with PEP 8'.format(file_path)
        yield nose.assert_equal, total_errors, 0, fail_msg


def test_complexity():
    """All source file functions should have a low cyclomatic complexity."""
    file_paths = itertools.chain(
        glob.iglob('automata/*/*.py'),
        glob.iglob('tests/*.py'))
    for file_path in file_paths:
        with open(file_path, 'r') as file_obj:
            blocks = radon.cc_visit(file_obj.read())
        for block in blocks:
            fail_msg = '{} ({}) has a cyclomatic complexity of {}'.format(
                block.name, file_path, block.complexity)
            yield nose.assert_less_equal, block.complexity, 10, fail_msg


def test_import_order():
    """All source file imports should be ordered and formatted properly."""
    file_paths = itertools.chain(
        glob.iglob('automata/*/*.py'),
        glob.iglob('tests/*.py'))
    for file_path in file_paths:
        with open(file_path, 'r') as file_obj:
            file_contents = file_obj.read()
        len_change = isort.SortImports(
            file_contents=file_contents).length_change
        fail_msg = '{} imports do not comply with PEP 8'.format(file_path)
        yield nose.assert_equal, len_change, 0, fail_msg
