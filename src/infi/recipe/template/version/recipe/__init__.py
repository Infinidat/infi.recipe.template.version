
# forked from http://pypi.python.org/pypi/collective.recipe.template/1.8

import logging
import os
import re
import stat
import zc.buildout
from infi.execute import execute_async

import collective.recipe.template

SECTION_NAME = "infi.recipe.template.version"

class GitMixin(object):
    @classmethod
    def get_commit_describe(cls, commit, match_pattern='v*'):
        from gitpy.exceptions import GitCommandFailedException
        try:
            cmd = 'git describe --tags --match %s %s' % (match_pattern, commit)
            return commit.repo._executeGitCommandAssertSuccess(cmd).stdout.read().strip()
        except GitCommandFailedException:
            return commit.repo._executeGitCommandAssertSuccess(cmd.replace('*', '\*')).stdout.read().strip()

    @classmethod
    def extract_version_tag(cls):
        from gitpy import LocalRepository
        from os import curdir, path
        repository = LocalRepository(curdir)
        branch = repository.getCurrentBranch()
        head = repository.getHead()
        if branch is None:
            return cls.get_commit_describe(head)
        current_branch = branch.name
        stripped_branch = current_branch.split('/')[0]
        if current_branch.startswith('release/') or current_branch.startswith('support/') or \
                                                    current_branch.startswith('hotfix/'):
            return cls.get_commit_describe(head)
        if 'master' in stripped_branch:
            return cls.get_commit_describe(head)
        else:
            try:
                return cls.get_commit_describe(head, 'v*%s*' % stripped_branch)
            except:
                pass
            return  cls.get_commit_describe(head)
        pass

    @classmethod
    def get_origin(cls, repository):
        from gitpy.exceptions import NonexistentRefException
        try:
            return repository.getRemoteByName("origin")
        except NonexistentRefException:
            return None

    @classmethod
    def guess_origin_home_protocol(cls, fqdn):
        from urllib import urlretrieve
        try:
            if urlretrieve("https://{0}".format(fqdn)):
                return 'https'
        except:
            return 'http'

    @classmethod
    def translate_clone_url_to_homepage(cls, url):
        from re import match
        URL = r"(?P<protocol>(?:git@|git:\/\/))(?P<origin_fqdn>[a-zA-Z0-9_\-.]+)[:\/]{1,2}(?P<repository_uri>[a-zA-Z0-9_\-\.\/]+)(?:.git)+$"
        if not match(URL, url):
            return None
        groupdict = match(URL, url).groupdict()
        protocol = cls.guess_origin_home_protocol(groupdict['origin_fqdn'])
        return "{0}://{1}/{2}".format(protocol, groupdict['origin_fqdn'], groupdict['repository_uri'])

    @classmethod
    def get_homepage(cls):
        repository = cls.get_repository()

        origin = cls.get_origin(repository)
        if origin is None:
            return None
        return cls.translate_clone_url_to_homepage(origin.url)

    @classmethod
    def get_repository(cls):
        import gitpy
        from os import curdir
        repository = gitpy.LocalRepository(curdir)
        return repository

class Recipe(collective.recipe.template.Recipe, GitMixin):
    """ This recipe extends collective.recipe.template by adding adding a new section
    [infi.recipe.template.version]
    version = <git describe>.strip('v')
    author = <git head commit author>
    author_email = <git head commit author email> """

    def __init__(self, buildout, name, options):
        Recipe.update_buildout_data(buildout)
        collective.recipe.template.Recipe.__init__(self, buildout, name, options)

    @classmethod
    def update_buildout_data(cls, buildout):
        repository = cls.get_repository()
        branch = repository.getCurrentBranch()
        try:
            remote = branch.getRemoteBranch() if branch is not None else None
        except gitpy.exceptions.NonexistentRefException:
            remote = None
        head = repository.getHead()
        from zc.buildout.buildout import Options
        data = {}
        data['version'] = cls.extract_version_tag().lstrip('v')
        data['author'] = head.getAuthorName()
        data['author_email'] = head.getAuthorEmail()
        data['git_local_branch'] = repr(branch.name if branch is not None else '(Not currently on any branch)')
        data['git_remote_tracking_branch'] = repr(remote.getNormalizedName() if remote is not None else '(No remote tracking)')
        data['git_remote_url'] = repr(remote.remote.url if remote is not None else '(Not remote tracking)')
        data['head_subject'] = repr(head.getSubject())
        data['head_message'] = repr(head.getMessageBody())
        data['head_hash'] = repr(head.hash)
        diff = execute_async("git diff --patch --no-color", shell=True)
        diff.wait()
        data['dirty_diff'] = repr(diff.get_stdout().replace('${', '$\\{'))
        data['homepage'] = repr(cls.get_homepage())
        if buildout.get("project").get("homepage"):
            data['homepage'] = repr(buildout.get("project").get("homepage"))
        buildout._data.update({SECTION_NAME: Options(buildout, SECTION_NAME, data)})
