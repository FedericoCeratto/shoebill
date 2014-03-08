shoebill
========
![Logo](docs/shoebill.png?raw=true)

Web-based editor for Pelican and Nikola



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



