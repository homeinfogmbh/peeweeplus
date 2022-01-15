#! /usr/bin/env python3
"""Installation script."""


from setuptools import setup


setup(
    name='peeweeplus',
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'configlib',
        'lxml',
        'mimeutil',
        'peewee',
    ],
    extras_require={
        'Argon2Field': ['argon2_cffi'],
        'authlib integration': ['authlib']
    },
    author='HOMEINFO - Digitale Informationssysteme GmbH',
    author_email='<info@homeinfo.de>',
    maintainer='Richard Neumann',
    maintainer_email='<r.neumann@homeinfo.de>',
    packages=['peeweeplus', 'peeweeplus.fields', 'peeweeplus.json'],
    license='GPLv3',
    description='Practical extensions for the peewee ORM framework.'
)
