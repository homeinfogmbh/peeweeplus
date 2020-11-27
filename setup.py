#! /usr/bin/env python3

from setuptools import setup


setup(
    name='peeweeplus',
    version_format='{tag}',
    setup_requires=['setuptools-git-version'],
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='<info@homeinfo.de>',
    maintainer='Richard Neumann',
    maintainer_email='<r.neumann@homeinfo.de>',
    packages=['peeweeplus', 'peeweeplus.fields', 'peeweeplus.json'],
    license='GPLv3',
    description='Practical extensions for the peewee ORM framework.'
)
