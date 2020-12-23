#
# Shoebill unit testing
#

from mock import patch, Mock
import os

import shoebill
from shoebill import Path, gen_random_token

# Prevent Bottle from capturing exceptions
shoebill.app.catchall = False


def test_gen_token():
    t = gen_random_token(6)
    assert len(t) == 8, repr(t)
    assert gen_random_token(6) != gen_random_token(6)


class TestPathOnDir(object):
    def setUp(self):
        shoebill.content_path = "/tmp/foo"
        self._p = Path(relurl="a/b/")

    def tearDown(self):
        shoebill.content_path = None

    def test_is_dir_on_dir(self):
        assert self._p.is_dir

    def test_basename_on_dir(self):
        assert self._p.basename() == "b"

    def test_as_url(self):
        p = Path(relurl="a/b/")
        assert p.as_url == "a/b/", p.as_url

    def test_url_chunks(self):
        assert self._p.url_chunks() == ["a", "b", ""]


class TestPathOnFile(object):
    def setUp(self):
        shoebill.content_path = "/tmp/foo"
        self._p = Path(relurl="a/b/test.rst")

    def tearDown(self):
        shoebill.content_path = None
        del self._p

    def test_is_dir_on_file(self):
        assert not self._p.is_dir

    def test_basename_on_file(self):
        assert self._p.basename() == "test.rst"

    def test_as_abs_path(self):
        assert self._p.as_abs_path == "/tmp/foo/a/b/test.rst"

    def test_url_chunks(self):
        assert self._p.url_chunks() == ["a", "b", "test.rst"]

    def test_not_hidden(self):
        assert not self._p.is_hidden, "The files should not show as hidden"

    def test_hidden(self):
        self._p = Path(relurl="a/.b.rst")
        assert self._p.is_hidden, "The files should show as hidden"

    def test_repr(self):
        assert "<Path" in repr(self._p)
