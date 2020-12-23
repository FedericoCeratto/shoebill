#!/usr/bin/env python

from setuptools import setup

__version__ = "1.0.1"

CLASSIFIERS = map(
    str.strip,
    """Environment :: Console
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Natural Language :: English
Operating System :: POSIX :: Linux
Programming Language :: Python
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Topic :: Internet :: WWW/HTTP :: WSGI
""".splitlines(),
)

entry_points = {"console_scripts": ["shoebill = shoebill:main"]}

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
    keywords="pelican nikola static generator editor",
    install_requires=[
        "Beaker>=1.6.3",
        "Bottle>=0.10.11",
        "GitPython>=0.1.7",
        "bottle-cork",
        "setproctitle>=1.0.1",
    ],
    packages=["shoebill"],
    package_dir={"shoebill": "shoebill"},
    platforms=["Linux"],
    zip_safe=False,
    test_suite="nose.collector",
    tests_require=["nose"],
    entry_points=entry_points,
    # Used by setup.py bdist to include files in the binary package
    package_data={"shoebill": ["views/*.tpl", "static/*"]},
)
