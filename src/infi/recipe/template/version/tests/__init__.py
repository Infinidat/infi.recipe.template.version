__import__("pkg_resources").declare_namespace(__name__)

import unittest
from mock import patch
from ..git import GitFlow, Commit, run_cmd

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

    def test_starred_branches_1(self):
        branches = ['* one', 'two', 'three']
        expected = ['one', 'two', 'three']
        self.assertEquals(Commit._move_starred_branch_to_top(branches), expected)

    def test_starred_branches_2(self):
        branches = ['one', '* two', 'three']
        expected = ['two', 'one', 'three']
        self.assertEquals(Commit._move_starred_branch_to_top(branches), expected)

    def test_starred_branches_3(self):
        branches = ['one', 'two', 'three']
        expected = ['one', 'two', 'three']
        self.assertEquals(Commit._move_starred_branch_to_top(branches), expected)

    def test_starred_branches_4(self):
        branches = ['one', 'two', '* three']
        expected = ['three', 'one', 'two']
        self.assertEquals(Commit._move_starred_branch_to_top(branches), expected)

    def test_version_tag_no_repository(self):
        self.assertRaises(OSError, GitFlow)

    def test_vesion_tag_empty_repository(self):
        from os import system
        system('git init .')
        self.assertRaises(OSError, GitFlow)

    def test_vesion_tag_no_tag(self):
        from os import system
        system('git init .')
        system('git commit --allow-empty -m empty')
        self.assertRaises(OSError, getattr, *[GitFlow().head, 'version_tag'])

    def test_vesion_tag_simple(self):
        from os import system
        system('git init .')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.1 -m tag')
        version = GitFlow().head.version_tag
        self.assertEquals(version, 'v0.0.1')

    def test_vesion_tag_longer(self):
        from os import system
        system('git init .')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.1 -m tag')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        version = GitFlow().head.version_tag
        self.assertTrue('v0.0.1-3' in version)
        self.assertEquals(version, 'v0.0.1-3-g%s' % GitFlow().head.hash[:7])

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
        version = GitFlow().head.version_tag
        self.assertTrue('v0.0-feature1-3' in version)
        self.assertEquals(version, 'v0.0-feature1-3-g%s' % GitFlow().head.hash[:7])

    def test_vesion_tag_in_release_branch(self):
        from os import system
        system('git init .')
        system('git flow init -fd')
        system('git flow release start v0.0')
        system('git commit --allow-empty -m empty')
        system('git tag -a v0.0.alpha -m tag')
        system('git commit --allow-empty -m empty')
        system('git commit --allow-empty -m empty')
        version = GitFlow().head.version_tag
        self.assertTrue('v0.0.alpha-2' in version)
        self.assertEquals(version, 'v0.0.alpha-2-g%s' % GitFlow().head.hash[:7])

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
        version = GitFlow().head.version_tag
        self.assertEquals(version, 'v0.0.alpha')

    def test_git_commit_attributes(self):
        from os import system
        system('git init .')
        system('git commit --allow-empty -m empty')
        date = GitFlow().head.date
        name = GitFlow().head.name
        email = GitFlow().head.email
        self.assertEquals(run_cmd('git config --get user.name')[1].splitlines()[0].strip(), name)
        self.assertEquals(run_cmd('git config --get user.email')[1].splitlines()[0].strip(), email)
