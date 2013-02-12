__import__("pkg_resources").declare_namespace(__name__)

from infi import unittest
from mock import patch
from contextlib import contextmanager
from ..recipe import Recipe, GitMixin
from os import system

TRANSLATE_URLS = {
    'git@gitserver:/host/recipe-template-version.git': 'https://gitserver/host/recipe-template-version',
    'git://gitserver/qa/tests.git': 'https://gitserver/qa/tests',
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
        system('git init .')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.1 -m tag')
        version = Recipe.extract_version_tag()
        self.assertEquals(version, 'v0.0.1')

    def test_vesion_tag_longer(self):
        from gitpy import LocalRepository
        system('git init .')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.1 -m tag')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        version = Recipe.extract_version_tag()
        self.assertTrue('v0.0.1-3' in version)

    def test_vesion_tag_in_feature_branch(self):
        system('git init .')
        system('git flow init -fd')
        system('git flow release start v0.0')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.0.alpha -m tag')
        system('git flow release finish v0.0.0')
        system('git flow feature start feature1')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0-feature1 -m tag')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        version = Recipe.extract_version_tag()
        self.assertTrue('v0.0-feature1-4' in version)

    def test_vesion_tag_in_release_branch(self):
        system('git init .')
        system('git flow init -fd')
        system('git flow release start v0.0')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.alpha -m tag')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        version = Recipe.extract_version_tag()
        self.assertTrue('v0.0.alpha-2' in version)

    def test_vesion_tag_in_no_branch(self):
        system('git init .')
        system('git flow init -fd')
        system('git flow release start v0.0')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.alpha -m tag')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        system('git checkout v0.0.alpha')
        version = Recipe.extract_version_tag()
        self.assertEquals(version, 'v0.0.alpha')

    def test_verison_tag_with_non_version_tag_outside_of_branch(self):
        system('git init .')
        system('git flow init -fd')
        system('git flow release start v0.0')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.alpha -m tag')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        system('git checkout HEAD^')
        system('git tag -a foo -m foo')
        version = Recipe.extract_version_tag()
        self.assertTrue('v0.0.alpha' in version)

    def test_homepage__no_origin(self):
        system('git init .')
        system('git flow init -fd')
        homepage = Recipe.get_homepage()
        self.assertEquals(homepage, None)

    def test_homepage__github(self):
        system('git init .')
        system('git flow init -fd')
        system("git remote add origin git://github.com/Infinidat/infi.recipe.template.version.git")
        homepage = Recipe.get_homepage()
        self.assertEquals(homepage, "https://github.com/Infinidat/infi.recipe.template.version")

    @unittest.parameters.iterate("in_out_tuple", TRANSLATE_URLS.items())
    def test_url_translation(self, in_out_tuple):
        subject, expected = in_out_tuple
        actual = GitMixin.translate_clone_url_to_homepage(subject)
        self.assertEquals(actual, expected)

class HomepageRealTestCase(unittest.TestCase):
    @contextmanager
    def install_myself(self):
        system("python setup.py develop")
        try:
            yield
        finally:
            system("easy_install -U infi.recipe.template.version")

    @contextmanager
    def new_repository_context(self, origin_url, expected_homepage):
        with temporary_directory_context():
            system("projector repository init infi.test {0} short long".format(origin_url))
            with open("setup.in") as fd:
                setup_in = fd.read()
            with open("setup.in", "w") as fd:
                fd.write(setup_in.replace("url = 'http://www.infinidat.com'",
                                          "url = ${infi.recipe.template.version:homepage}"))
            yield
            system("projector devenv build --no-scripts")
            with open("setup.py") as fd:
                actual_homepath = "url = {0},".format(None if expected_homepage is None else repr(expected_homepage))
                self.assertIn(actual_homepath, fd.read())

    def test_homepage__github(self):
        with self.install_myself():
            with self.new_repository_context("git://github.com/Infinidat/infi.test.git",
                                             'https://github.com/Infinidat/infi.test'):
                pass

    def test_homepage__invalid(self):
        with self.install_myself():
            with self.new_repository_context("https://github.com/Infinidat/infi.test", None):
                pass

    def test_homepage__overriden_in_buildout(self):
        with self.install_myself():
            with self.new_repository_context("https://github.com/Infinidat/infi.test", "http://google.com"):
                with open("buildout.cfg") as fd:
                    buildout_cfg = fd.read()
                with open("buildout.cfg", 'w') as fd:
                    fd.write(buildout_cfg.replace("[project]", "[project]\nhomepage = http://google.com"))

    def test_homepage__old_setup_in(self):
        from os.path import abspath, dirname, exists
        from shutil import copy
        with self.install_myself():
            with temporary_directory_context():
                system("projector repository init infi.test https://github.com/Infinidat/infi.test short long")
                system("projector devenv build --no-scripts")
                exists(abspath("./setup.py"))
