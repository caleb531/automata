#!/usr/bin/env python
"""Setup logic for pip."""

from setuptools import setup


def get_long_description():
    with open('README.md', 'r') as readme_file:
        return readme_file.read()


setup(
    name='automata-lib',
    version='5.0.0',
    description='A Python library for simulating automata and Turing machines',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
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
    install_requires=['pydot'],
    entry_points={}
)
