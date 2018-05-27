# -*- coding: utf-8 -*-
from setuptools import setup
from . import __version__

install_requires = [
    'django>=2.0',
    'django-bootstrap-form',
    'django-sortedm2m',
    'allianceauth>=2.0',
    'martor>=1.2.5',
]

testing_extras = [

]

setup(
    name='allianceauth-bbs',
    version=__version__,
    author='Alliance Auth',
    author_email='basraaheve@gmail.com',
    description='A very basic Forum for Alliance Auth.',
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
        ':python_version=="3.4"': ['typing'],
    },
    python_requires='~=3.4',
    license='GPLv3',
    packages=['allianceauth.bbs'],
    url='https://github.com/basraah/allianceauth-bbs',
    zip_safe=False,
    include_package_data=True,
)
