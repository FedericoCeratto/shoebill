shoebill
========
![Logo](docs/shoebill.png?raw=true)

Web-based editor for Pelican and Nikola

[![Build Status](https://travis-ci.org/FedericoCeratto/shoebill.svg?branch=master)](https://travis-ci.org/FedericoCeratto/shoebill)
[![Latest release](https://img.shields.io/pypi/v/shoebill.svg?style=plastic)](https://pypi.python.org/pypi/shoebill)
[![Number of downloads](https://img.shields.io/pypi/dm/shoebill.svg?style=plastic)](https://pypi.python.org/pypi/shoebill)
[![License](http://img.shields.io/:license-gpl3-blue.svg?style=plastic)](https://pypi.python.org/pypi/shoebill)

Features
--------

* Create and edit files
* Commit file changes on Git (optional)
* Run "make publish" and additional make targets
* Authentication (optional)

Installation
------------

Use virtualenv on package-based Linux distributions! [Learn why](http://workaround.org/easy-install-debian)

    $ pip install shoebill

Usage
-----

Create a regular Pelican or Nikola site directory (see pelican-quickstart documentation)

Make sure to create a Makefile

Run Shoebill as:

    $ ./shoebill.py /path/to/the/pelican/site

And open in your browser:
http://127.0.0.1:8080/edit/

You can create or delete users and change your password at:
http://127.0.0.1:8080/admin/

Optionally you can specify:

    -p <port number> (defaults to 8080)
    --host <hostname/ip_address>   - Hostname/IP address to bind at 
    -D                             - Bottle debugging mode
    -t <target>, --target <target> - Additional make target to be executed from the UI
    --no-auth                      - Disable authentication


Screenshots
-----------

![ScreenShot](https://raw.github.com/FedericoCeratto/shoebill/screenshots/screenshot1.jpg)
