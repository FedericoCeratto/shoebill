#!/usr/bin/env python
#
# Web-based editor for Pelican and Nikola websites
#
# Copyright (C) 2014 Federico Ceratto
#
# This package is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from base64 import b64encode
from datetime import datetime
from git import Repo, InvalidGitRepositoryError
from pkg_resources import resource_filename
from setproctitle import setproctitle
import argparse
import bottle
import logging
import os
import subprocess
import sys

log = logging.getLogger("shoebill")

app = bottle.app()
aaa = None

tpl_path = resource_filename("shoebill", "views")
bottle.TEMPLATE_PATH.insert(0, tpl_path)
static_path = resource_filename("shoebill", "static")

try:
    from beaker.middleware import SessionMiddleware
    from cork import Cork

    aaa_available = True
except ImportError:  # pragma: nocover
    aaa_available = False


git_repo = None
content_path = None
make_targets = None


def gen_random_token(length):
    """Generate a printable random string"""
    return b64encode(os.urandom(length))


class Path(object):
    """Represent a path to a file or directory in the site dir"""

    def __init__(self, relurl=None, absfile=None):
        global content_path
        self._content_path = content_path
        self._ossep = os.sep
        self._urlsep = "/"
        # print "relurl %r" % relurl
        # print "absfile %r" % absfile

        if absfile:
            self._abspath = absfile
        else:
            relurl = relurl.lstrip("/")  # Prevent directory traversal attacks
            relpath = self._ossep.join(relurl.split(self._urlsep))
            self._abspath = os.path.join(self._content_path, relpath)

        if self.is_dir:
            assert self.as_url.endswith(self._urlsep), "%r" % self.as_url
        else:
            assert not self.as_url.endswith(self._urlsep), "%r" % self.as_url

    @property
    def is_dir(self):
        """Check if the current path is meant to be a directory
        (ends with a slash)

        :returns: bool
        """
        return self._abspath.endswith(self._ossep)

    @property
    def as_abs_path(self):
        """Returns the absolute path

        :returns: str
        """
        return self._abspath

    @property
    def as_relative_path(self):
        """Returns a relative path from the current path

        :returns: str
        """
        trunc = len(self._content_path) + 1
        relpath = self._abspath[trunc:]
        return relpath

    @property
    def as_url(self):
        """Returns a relative URL from the current path

        :returns: str
        """
        relpath = self.as_relative_path
        url = self._urlsep.join(relpath.split(self._ossep))
        assert self._content_path not in url

        if self.is_dir:
            if not url.endswith(self._urlsep):
                url += self._urlsep

            return url

        return url.rstrip(self._urlsep)

    def url_chunks(self):
        relpath = self.as_relative_path
        return relpath.split(self._ossep)

    @property
    def is_hidden(self):
        """Detect if the relative path contains hidden directories or files

        :returns: bool
        """
        for c in self.url_chunks():
            if c.startswith("."):
                return True

        return False

    def basedir(self):
        """Extract base directory of the current path

        :returns: :class:`Path`
        """
        dn = os.path.dirname(self._abspath)
        return Path(absfile=dn)

    @property
    def is_real_dir(self):
        """Check if a real directory exists on disk

        :returns: bool
        """
        return os.path.isdir(self._abspath)

    @property
    def is_real_file(self):
        """Check if a real file exists on disk

        :returns: bool
        """
        return os.path.isfile(self._abspath)

    def list_current_dir(self):
        """List current directory contents.
        Hidden directories and files are not listed.

        :returns: (dirname, filenames) lists
        """
        bdn = os.path.dirname(self._abspath)
        w = os.walk(bdn)
        _, dirnames, filenames = next(w)
        dirnames = [Path(absfile=os.path.join(bdn, d) + "/") for d in sorted(dirnames)]
        dirnames = [d for d in dirnames if not d.is_hidden]

        filenames = [Path(absfile=os.path.join(bdn, f)) for f in sorted(filenames)]
        filenames = [f for f in filenames if not f.is_hidden]

        return dirnames, filenames

    def basename(self):
        """"""
        if self.is_dir:
            return self.basedir().basename()

        return os.path.basename(self._abspath)

    def __repr__(self):
        return "<Path '%s' url='%s'>" % (self._abspath, self.as_url)


## Webapp methods ##


def post_get(name):
    return bottle.request.forms[name].strip()


def error(msg):
    """Generate an error page"""
    return bottle.template("msgbox", output=[], errmsg=msg)


def msg(text):
    """Generate a message page"""
    return bottle.template("msgbox", output=text.split("\n"), errmsg="")


path_not_found = error("Error: the directory you specified does not exists.")


@bottle.route("/")
def route_index():
    return bottle.redirect("/edit")


@bottle.route("/login")
@bottle.view("login_form")
def route_login_form():
    """Serve login form"""
    pass


@bottle.post("/login")
def login():
    """Authenticate users"""
    if not aaa:
        return bottle.redirect("/edit")

    username = post_get("username")
    password = post_get("password")
    aaa.login(username, password, success_redirect="/edit", fail_redirect="/login")


@bottle.route("/logout")
def logout():
    """Log out"""
    if aaa:
        aaa.logout(success_redirect="/login")

    return bottle.redirect("/edit")


@bottle.route("/change_password")
@bottle.view("password_change_form")
def route_password_change_form():
    """Serve password change form"""
    if not aaa:
        return bottle.redirect("/edit")


@bottle.post("/change_password")
def route_change_password():
    """Change password"""
    if not aaa:
        return bottle.redirect("/edit")

    aaa.require(fail_redirect="/login")
    password = post_get("password")
    aaa.current_user.update(pwd=password)

    return msg("Password updated.")


@bottle.route("/edit")
@bottle.route("/edit/")
@bottle.route("/edit/<path:path>")
@bottle.view("edit")
def route_edit(path="", savemsg=None):
    """Serve the main UI page, displaying files and directories and,
    optionally, a form to edit the current file. Also, display buttons
    to execute makefile targets
    """
    if aaa:
        aaa.require(fail_redirect="/login")

    path = path.strip()
    path = Path(relurl=path)

    if path.is_dir and not path.is_real_dir:
        # path ends with '/' but there is no such dir
        return path_not_found

    if not path.basedir().is_real_dir:
        # path's parent dir is missing
        return path_not_found

    if path.is_hidden:
        # hidden files are not accessible
        return path_not_found

    if not path.is_dir and path.is_real_dir:
        # path ends without '/' but there is a directory with that name
        return bottle.redirect(path.as_url + "/")

    contents = ""
    if path.is_real_file and not path.is_dir:
        with open(path.as_abs_path) as f:
            contents = f.read()

    d = dict(
        path=path,
        contents=contents,
        savemsg=savemsg,
        git_enabled=bool(git_repo),
        make_targets=make_targets,
        aaa_enabled=bool(aaa),
    )
    return d


@bottle.post("/edit/<path:path>")
def route_post_save(path):
    """Save changes to a file (or create new file)
    Commits on Git if a repository exists.
    """
    if aaa:
        aaa.require(fail_redirect="/login")

    path = path.strip()
    path = Path(relurl=path)
    if path.is_dir or path.is_real_dir:
        # Path should point to a file, not a directory
        return path_not_found

    if not path.basedir().is_real_dir:
        # The file should be in an existing directory
        return path_not_found

    if path.is_hidden:
        # hidden files are not accessible
        return path_not_found

    already_existing = path.is_real_file

    print("writing %s", path.as_abs_path)
    file_contents = bottle.request.forms.file_contents
    with open(path.as_abs_path, "w") as f:
        f.write(file_contents)

    if not git_repo:
        return route_edit(path=path.as_url, savemsg="Saved.")

    repo_is_dirty = git_repo.is_dirty()
    git_repo.git.add(path.as_abs_path)
    repo_is_dirty = repo_is_dirty or git_repo.is_dirty()

    if already_existing and not repo_is_dirty:
        return route_edit(path=path.as_url, savemsg="No changes to be saved!")

    description = post_get("desc") or "Update %s" % path.as_abs_path

    if aaa:
        cu = aaa.current_user
        email_addr = cu.email_addr or ""
        author = "%s <%s>" % (cu.username, email_addr)
        git_repo.git.commit(m=description, author=author)

    else:
        git_repo.git.commit(m=description)

    return route_edit(path=path.as_url, savemsg="Saved.")


@bottle.route("/make")
@bottle.route("/make/")
@bottle.route("/make/<target>")
def route_get_make_target(target=None):
    """Redirect GETs on /make to /edit"""
    if aaa:
        aaa.require(fail_redirect="/login")

    raise bottle.redirect("/edit/")


@bottle.post("/make/<target>")
@bottle.view("msgbox")
def route_run_make_target(target):
    """Execute make target, serve output page"""
    global content_path
    global make_targets

    if aaa:
        aaa.require(fail_redirect="/login")

    target = target.strip()
    print("Running target: %r" % target)

    if target != "publish" and target not in make_targets:
        return error("Unknown make target")

    site_path = os.path.dirname(content_path)

    cmd = subprocess.Popen(
        ["make", target],
        cwd=site_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = cmd.communicate()[0]
    output = output.split("\n")
    return dict(output=output, errmsg=None)


@bottle.route("/favicon.ico")
def serve_favicon():
    return bottle.static_file("favicon.ico", root=static_path)


# Admin-only pages


@bottle.route("/admin")
@bottle.route("/admin/")
@bottle.view("admin_page")
def admin():
    """Only admin users can see this"""
    # aaa.require(role='admin', fail_redirect='/')
    return dict(
        current_user=aaa.current_user, users=aaa.list_users(), roles=aaa.list_roles()
    )


@bottle.post("/create_user")
def create_user():
    try:
        aaa.create_user(post_get("username"), post_get("role"), post_get("password"))
        return msg("User created")
    except Exception as e:
        return error(msg=e.message)


@bottle.post("/delete_user")
def delete_user():
    try:
        aaa.delete_user(post_get("username"))
        return msg("User deleted")
    except Exception as e:
        return error(msg=e.message)


@bottle.post("/create_role")
def create_role():
    try:
        aaa.create_role(post_get("role"), post_get("level"))
        return msg("Role created")
    except Exception as e:
        return error(msg=e.message)


@bottle.post("/delete_role")
def delete_role():
    try:
        aaa.delete_role(post_get("role"))
        return msg("Role deleted")
    except Exception as e:
        return error(msg=e.message)


# end of admin-only pages


def check_site_dir(site_path, content_path):

    if not os.path.isdir(site_path):
        print("%s does not exists or is not a directory" % site_path)
        sys.exit(1)

    if not os.path.isdir(content_path):
        print("The content directory %s is missing" % content_path)
        sys.exit(1)

    makefile = os.path.join(site_path, "Makefile")
    if not os.path.isfile(makefile):
        print("WARNING: missing Makefile at %s" % makefile)


def setup_git_repo(site_path):
    global git_repo
    try:
        git_repo = Repo(site_path)
    except InvalidGitRepositoryError:
        print("%s is not a valid Git repository" % site_path)


def main():
    global aaa
    global app
    global content_path

    setproctitle("shoebill")

    args = parse_args()

    site_path = os.path.abspath(args.directory)
    content_path = os.path.join(site_path, "content")
    check_site_dir(site_path, content_path)

    print("Starting Shoebill...")
    setup_git_repo(site_path)

    if not args.no_auth:
        # Setup authentication
        if not aaa_available:
            print(
                """Error: the Beaker and/or Cork libraries are missing. \
            \nPlease install them or disable authentication using --no-auth"""
            )
            sys.exit(1)

        auth_dir = os.path.join(site_path, ".shoebill_auth")
        if not os.path.isdir(auth_dir):
            print("Creating authentication data")
            os.mkdir(auth_dir)

            token = gen_random_token(21)
            with open(os.path.join(auth_dir, "token"), "w") as f:
                f.write(token)

            aaa = Cork(auth_dir, initialize=True)
            aaa._store.roles["admin"] = 100
            aaa._store.roles["editor"] = 50
            aaa._store.save_roles()
            tstamp = str(datetime.utcnow())
            admin_password = gen_random_token(6)
            aaa._store.users["admin"] = {
                "role": "admin",
                "hash": aaa._hash("admin", admin_password),
                "email_addr": "",
                "desc": "admin",
                "creation_date": tstamp,
                "_accessed_time": tstamp,
                "last_login": tstamp,
            }
            aaa._store.save_users()
            print("\n", "*" * 32, "\n")
            print("Initialized user 'admin' with password '%s'" % admin_password)
            print("\n", "*" * 32, "\n")

        else:
            aaa = Cork(auth_dir)

    if aaa:
        # Sessions are enabled only if authentication is enabled
        with open(os.path.join(auth_dir, "token")) as f:
            session_encrypt_key = f.read()

        session_opts = {
            "session.cookie_expires": True,
            "session.encrypt_key": session_encrypt_key,
            "session.httponly": True,
            "session.timeout": 3600 * 24,  # 1 day
            "session.type": "cookie",
            "session.validate_key": True,
        }
        wrapped_app = SessionMiddleware(app, session_opts)
        bottle.run(
            wrapped_app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            reloader=args.debug,
            server="auto",
        )

    else:
        bottle.run(
            app,
            host=args.host,
            port=args.port,
            debug=args.debug,
            reloader=args.debug,
            server="auto",
        )


def parse_args():
    """Parse CLI options and arguments

    :returns: args object
    """
    global make_targets
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", default=8080, help="Port (default: 8080)")
    ap.add_argument(
        "-t",
        "--target",
        help="Enable an additional make target",
        action="append",
        default=[],
    )
    ap.add_argument("--host", default="localhost")
    ap.add_argument("-D", "--debug", action="store_true")
    ap.add_argument("directory", help="site directory")
    ap.add_argument("--no-auth", help="Disable authentication", action="store_true")

    args = ap.parse_args()
    make_targets = args.target
    return args


if __name__ == "__main__":
    main()
