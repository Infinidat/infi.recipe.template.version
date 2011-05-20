__import__("pkg_resources").declare_namespace(__name__)

import unittest
from mock import patch
from ..recipe import Recipe

def run_cmd(cmd, return_stderr=False):
    from subprocess import Popen, PIPE
    import shlex
    p = Popen(shlex.split(cmd, posix=True), stdout=PIPE, stderr=PIPE if return_stderr else None)
    p.wait()
    stdout = p.stdout.read()
    if return_stderr:
        stderr = p.stderr.read()
        return (p.returncode, stdout, stderr)
    return (p.returncode, stdout)

def strip(string):
    output = string.strip('\n').strip('"')
    return output

class VersionInfoTestCase(unittest.TestCase):
    def setUp(self):
        from os.path import abspath
        from os import chdir, curdir
        from tempfile import mkdtemp
        self._curdir = abspath(curdir)
        self._tempdir = mkdtemp()
        chdir(self._tempdir)

    def tearDown(self):
        from os import chdir, curdir
        chdir(self._curdir)

    def test_vesion_tag_simple(self):
        from os import system
        system('git init .')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.1 -m tag')
        version = Recipe.extract_version_tag()
        self.assertEquals(version, 'v0.0.1')

    def test_vesion_tag_longer(self):
        from os import system
        from git import LocalRepository
        system('git init .')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.1 -m tag')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        version = Recipe.extract_version_tag()
        self.assertTrue('v0.0.1-3' in version)

    def test_vesion_tag_in_feature_branch(self):
        from os import system
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
        from os import system
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
        from os import system
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

