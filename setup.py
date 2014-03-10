#!/usr/bin/env python

from setuptools import setup

__version__ = '0.1'

CLASSIFIERS = map(str.strip,
"""Environment :: Console
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Natural Language :: English
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 2.7
Topic :: Internet :: WWW/HTTP :: WSGI
""".splitlines())

entry_points = {
    'console_scripts': [
        'shoebill = shoebill:main',
    ]
}


setup(
    name="shoebill",
    version=__version__,
    author="Federico Ceratto",
    author_email="federico.ceratto@gmail.com",
    description="Simple web-based Markdown editor for Pelican and Nikola",
    license="GPLv3+",
    url="https://github.com/FedericoCeratto/shoebill",
    long_description="Simple web-based Markdown editor for Pelican and Nikola,"
        "with authentication and Git support",
    classifiers=CLASSIFIERS,
    install_requires=[
        'Beaker>=1.6.3',
        'Bottle>=0.10.11',
        'GitPython>=0.3.1',
        'bottle-cork',
        'setproctitle>=1.0.1',
    ],
    packages=['shoebill'],
    data_files=[
        ('views', [
            'views/admin_page.tpl',
            'views/edit.tpl',
            'views/login_form.tpl',
            'views/msgbox.tpl']),
    ],
    platforms=['Linux'],
    test_suite='nose.collector',
    tests_require=['nose'],
    entry_points=entry_points,
)
