
# forked from http://pypi.python.org/pypi/collective.recipe.template/1.8

import logging
import os
import re
import stat
import zc.buildout

import collective.recipe.template

SECTION_NAME = "infi.recipe.template.version"

class Recipe(collective.recipe.template.Recipe):
    """ This recipe extends collective.recipe.template by adding adding a new section
    [infi.recipe.template.version]
    version = <git describe>.strip('v')
    author = <git head commit author>
    author_email = <git head commit author email> """

    def __init__(self, buildout, name, options):
        Recipe.update_buildout_data(buildout)
        collective.recipe.template.Recipe.__init__(self, buildout, name, options)

    @classmethod
    def get_commit_describe(cls, commit, match_pattern='v*'):
        cmd = 'git describe --tags --match %s %s' % (match_pattern, commit)
        return commit.repo._executeGitCommandAssertSuccess(cmd).stdout.read().strip()

    @classmethod
    def extract_version_tag(cls):
        from git import LocalRepository
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
    def update_buildout_data(cls, buildout):
        import git
        from os import curdir
        repository = git.LocalRepository(curdir)
        branch = repository.getCurrentBranch()
        remote = branch.getRemoteBranch() if branch is not None else None
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
        data['dirty_diff'] = repr(repository._getOutputAssertSuccess("git diff --patch --no-color"))
        buildout._data.update({SECTION_NAME: Options(buildout, SECTION_NAME, data)})

