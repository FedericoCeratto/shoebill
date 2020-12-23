#
# Shoebill functional testing
#

from mock import patch, Mock
from tempfile import mkdtemp
from webtest import TestApp
import os
import subprocess
import shutil

import shoebill

# Prevent Bottle from capturing exceptions
shoebill.app.catchall = False


class PelicanDirSetup(object):
    def __init__(self):
        self._patchers = []

    def dir_setup(self):
        assert shoebill.content_path is None, shoebill.content_path
        self._site_path = mkdtemp()
        print("Created %s" % self._site_path)
        assert self._site_path.startswith("/tmp/tmp")
        assert os.path.isdir(self._site_path)
        for dirname in ("content", "content/pages"):
            os.mkdir(os.path.join(self._site_path, dirname))

        assert os.path.isdir(os.path.join(self._site_path, "content"))
        assert os.path.isdir(os.path.join(self._site_path, "content/pages"))
        shoebill.content_path = os.path.join(self._site_path, "content")

    def dir_teardown(self):
        shoebill.content_path = None
        assert self._site_path.startswith("/tmp/tmp")
        shutil.rmtree(self._site_path)
        print("Removed %s" % self._site_path)
        assert not os.path.isdir(self._site_path)
        del self._site_path

    def git_setup(self):
        assert shoebill.git_repo is None
        shoebill.git_repo = Mock()
        shoebill.git_repo.is_dirty.return_value = True

    def git_teardown(self):
        shoebill.git_repo = None

    def webapp_setup(self):
        shoebill.make_targets = []
        env = {"REMOTE_ADDR": "127.0.0.1"}
        self._app = TestApp(shoebill.app, extra_environ=env)

    def webapp_teardown(self):
        pass

    def create_patch(self, name):
        patcher = patch(name)
        thing = patcher.start()
        self._patchers.append(patcher)
        return thing

    def create_disabling_patch(self, name):
        """Patch a method to raise an exception on call.
        Used to detect unexpected calls.
        """
        m = self.create_patch(name)
        m.side_effect = Exception("Unexpected call to %s" % name)

    def patches_teardown(self):
        while self._patchers:
            self._patchers.pop().stop()


class TestWebapp(PelicanDirSetup):
    """Functional tests"""

    def setUp(self):
        self.dir_setup()
        self.webapp_setup()

    def tearDown(self):
        self.dir_teardown()
        self.webapp_teardown()
        self.patches_teardown()

    # Fetching edit page

    def test_edit(self):
        assert self._app.get("/edit").status == "200 OK"
        assert self._app.get("/edit/").status == "200 OK"

    def test_edit_new_file(self):
        r = self._app.get("/edit/hi.rst")
        assert r.status == "200 OK"
        assert "Rebuild" in r

    def test_edit_missing_dir(self):
        r = self._app.get("/edit/notthere/")
        assert r.status == "200 OK"
        assert "Error: the directory you specified does not exists." in r
        assert "Rebuild" not in r

    def test_edit_hidden_file(self):
        r = self._app.get("/edit/.hidden.rst")
        assert r.status == "200 OK", r.status
        assert "Error: the directory you specified does not exists." in r

    def test_edit_dir_without_slash(self):
        r = self._app.get("/edit/pages")
        assert r.status == "302 Found", r
        assert r.location == "http://localhost:80/edit/pages/"

    # Writing to a file

    def test_write_existing_file(self):
        r = self._app.post("/edit/hi.rst", {"file_contents": "test_contents"})
        assert r.status == "200 OK"
        assert "Saved." in r, [l.strip() for l in r.body.split("\n") if '"errmsg' in l]

    def test_write_missing_dir(self):
        r = self._app.post("/edit/nothere/hi.rst", {"file_contents": "test_contents"})
        assert r.status == "200 OK", r.status
        assert "Error: the directory you specified does not exists." in r

    def test_write_hidden_file(self):
        r = self._app.post("/edit/.hidden.rst", {"file_contents": "test_contents"})
        assert r.status == "200 OK", r.status
        assert "Error: the directory you specified does not exists." in r

    def test_write_new_file(self):
        r = self._app.post("/edit/hi.rst", {"file_contents": "test_contents"})
        assert r.status == "200 OK"
        assert "Saved." in r, r.content.split("\n")

    def test_get_make(self):
        r = self._app.get("/make/foo")
        assert r.status == "302 Found"

    @patch("subprocess.Popen")
    def test_make_publish(self, popen):
        cmd = popen.return_value
        cmd.communicate.return_value = ["test_output\n"]

        r = self._app.post("/make/publish")
        assert r.status == "200 OK"
        assert "test_output" in r
        popen.assert_called_once_with(
            ["make", "publish"],
            cwd=self._site_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )


class TestWebappWithGitRepo(PelicanDirSetup):
    """Functional tests with Git repo"""

    def setUp(self):
        self.dir_setup()
        self.git_setup()
        self.webapp_setup()

    def tearDown(self):
        self.dir_teardown()
        self.git_teardown()
        self.webapp_teardown()

    def test_write_file_with_git(self):
        r = self._app.post(
            "/edit/hi.rst", {"file_contents": "test_contents", "desc": "blah"}
        )
        assert r.status == "200 OK"
        assert "Saved." in r
        assert shoebill.git_repo.is_dirty.called
        assert shoebill.git_repo.git.add.called
        shoebill.git_repo.git.add.assert_called_once_with(
            "%s/content/hi.rst" % self._site_path
        )
