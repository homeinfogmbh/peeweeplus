#! /usr/bin/env python3

from setuptools import setup


setup(
    name='peeweeplus',
    version_format='{tag}',
    setup_requires=['setuptools-git-version'],
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='<info at homeinfo dot de>',
    maintainer='Richard Neumann',
    maintainer_email='<r dot neumann at homeinfo priod de>',
    packages=['peeweeplus', 'peeweeplus.fields', 'peeweeplus.json'],
    license='GPLv3',
    description='Practical extensions for the peewee ORM framework.'
)
