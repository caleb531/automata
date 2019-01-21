#!/usr/bin/env python
"""Setup logic for pip."""

from setuptools import setup


def get_long_description():
    """Get long description used on PyPI project page."""
    try:
        # Use pandoc to create reStructuredText README if possible
        import pypandoc
        return pypandoc.convert('README.md', 'rst')
    except Exception:
        return None


setup(
    name='automata-lib',
    version='3.0.0',
    description='A Python library for simulating automata and Turing machines',
    long_description=get_long_description(),
    url='https://github.com/caleb531/automata',
    author='Caleb Evans',
    author_email='caleb@calebevans.me',
    license='MIT',
    keywords='automata turing machine',
    packages=[
        'automata',
        'automata.fa',
        'automata.pda',
        'automata.base',
        'automata.tm'
    ],
    install_requires=[],
    entry_points={}
)
