#! /usr/bin/env python3

from distutils.core import setup
from homeinfo.lib.misc import GitInfo

version, author, author_email, *_ = GitInfo()

setup(
    name='homeinfo-peewee',
    version=version,
    author=author,
    author_email=author_email,
    requires=['peewee',
              'homeinfo'],
    package_dir={'homeinfo': ''},
    py_modules=['homeinfo.peewee'],
    description='peewee extensions for HOMEINFO')
