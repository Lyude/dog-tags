#!/usr/bin/python3

from setuptools import setup
from dogtags.version import __version__
setup(
    name="dogtags",
    version=__version__,
    packages=['dogtags'],
    entry_points={
        'console_scripts': [
            'dogtags = dogtags.__main__'
        ]
    },
    author="Lyude Paul",
    author_email="thatslyude@gmail.com",
    description="Vim syntax file generator using CTags"
)
