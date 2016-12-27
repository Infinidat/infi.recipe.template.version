__import__("pkg_resources").declare_namespace(__name__)

from infi import unittest
from infi.execute import execute_assert_success
from mock import patch
from contextlib import contextmanager
from ..recipe import Recipe, GitMixin

TRANSLATE_URLS = {
    'git@infinigit.infinidat.com:/host/recipe-template-version.git': 'http://infinigit.infinidat.com/host/recipe-template-version',
    'git://infinigit.infinidat.com/qa/tests.git': 'http://infinigit.infinidat.com/qa/tests',
    'git@github.com:Infinidat/infi.execute.git': 'https://github.com/Infinidat/infi.execute',
    'git://github.com/Infinidat/infi.execute.git': 'https://github.com/Infinidat/infi.execute',
}

from logging import getLogger
logger = getLogger(__name__)

@contextmanager
def chdir(path):
    from os.path import abspath
    from os import curdir, chdir
    path = abspath(path)
    current_dir = abspath(curdir)
    logger.debug("chdir {!r}".format(path))
    chdir(path)
    try:
        yield
    finally:
        chdir(current_dir)
        logger.debug("chdir {!r}".format(current_dir))

@contextmanager
def temporary_directory_context():
    from tempfile import mkdtemp
    from shutil import rmtree
    tempdir = mkdtemp()
    with chdir(tempdir):
        yield tempdir
    rmtree(tempdir, ignore_errors=True)

class VersionInfoTestCase(unittest.TestCase):
    def setUp(self):
        self._chdir = temporary_directory_context()
        self._chdir.__enter__()

    def tearDown(self):
        self._chdir.__exit__(None, None, None)

    def test_vesion_tag_simple(self):
        execute_assert_success('git init .'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git tag -a v0.0.1 -m tag'.split())
        version = Recipe.extract_version_tag()
        self.assertEqual(version, 'v0.0.1')

    def test_vesion_tag_longer(self):
        from gitpy import LocalRepository
        execute_assert_success('git init .'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git tag -a v0.0.1 -m tag'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        version = Recipe.extract_version_tag()
        self.assertTrue('v0.0.1.post3' in version)

    def test_vesion_tag_in_feature_branch(self):
        execute_assert_success('git init .'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git tag -a v0.0.0.alpha -m tag'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git tag -a v0.0-feature1 -m tag'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        version = Recipe.extract_version_tag()
        self.assertIn('v0.0-feature1.post4', version)

    def test_vesion_tag_in_release_branch(self):
        execute_assert_success('git init .'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git tag -a v0.0.alpha -m tag'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        version = Recipe.extract_version_tag()
        self.assertTrue('v0.0.alpha.post2' in version)

    def test_vesion_tag_in_no_branch(self):
        execute_assert_success('git init .'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git tag -a v0.0.alpha -m tag'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git checkout v0.0.alpha'.split())
        version = Recipe.extract_version_tag()
        self.assertEqual(version, 'v0.0.alpha')

    def test_verison_tag_with_non_version_tag_outside_of_branch(self):
        execute_assert_success('git init .'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git tag -a v0.0.alpha -m tag'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git commit --allow-empty -m empty'.split())
        execute_assert_success('git checkout HEAD^'.split())
        execute_assert_success('git tag -a foo -m foo'.split())
        version = Recipe.extract_version_tag()
        self.assertTrue('v0.0.alpha' in version)

    def test_homepage__no_origin(self):
        execute_assert_success('git init .'.split())
        homepage = Recipe.get_homepage()
        self.assertEqual(homepage, None)

    def test_homepage__github(self):
        execute_assert_success('git init .'.split())
        execute_assert_success("git remote add origin git://github.com/Infinidat/infi.recipe.template.version.git".split())
        homepage = Recipe.get_homepage()
        self.assertEqual(homepage, "https://github.com/Infinidat/infi.recipe.template.version")

    @unittest.parameters.iterate("in_out_tuple", TRANSLATE_URLS.items())
    def test_url_translation(self, in_out_tuple):
        subject, expected = in_out_tuple
        actual = GitMixin.translate_clone_url_to_homepage(subject)
        self.assertEqual(actual, expected)

class HomepageRealTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        execute_assert_success("python setup.py develop".split())

    @contextmanager
    def new_repository_context(self, origin_url, expected_homepage):
        with temporary_directory_context():
            execute_assert_success("projector repository init infi.test {0} short long".format(origin_url).split())
            with open("setup.in") as fd:
                setup_in = fd.read()
            with open("setup.in", "w") as fd:
                fd.write(setup_in.replace("url = 'http://www.infinidat.com'",
                                          "url = ${infi.recipe.template.version:homepage}"))
            yield
            execute_assert_success("projector devenv build --no-scripts".split())
            with open("setup.py") as fd:
                actual_homepath = "url = {0},".format(None if expected_homepage is None else repr(expected_homepage))
                self.assertIn(actual_homepath, fd.read())

    def test_homepage__github(self):
        with self.new_repository_context("git://github.com/Infinidat/infi.test.git",
                                         'https://github.com/Infinidat/infi.test'):
            pass

    def test_homepage__invalid(self):
        with self.new_repository_context("https://github.com/Infinidat/infi.test", None):
            pass

    def test_homepage__overriden_in_buildout(self):
        with self.new_repository_context("https://github.com/Infinidat/infi.test", "http://google.com"):
            with open("buildout.cfg") as fd:
                buildout_cfg = fd.read()
            with open("buildout.cfg", 'w') as fd:
                fd.write(buildout_cfg.replace("[project]", "[project]\nhomepage = http://google.com"))

    def test_homepage__old_setup_in(self):
        from os.path import abspath, dirname, exists
        from shutil import copy
        with temporary_directory_context():
            execute_assert_success("projector repository init infi.test https://github.com/Infinidat/infi.test short long".split())
            execute_assert_success("projector devenv build --no-scripts".split())
            exists(abspath("./setup.py"))
