
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
    def extract_version_tag(cls):
        from git import LocalRepository
        from os import curdir, path
        repository = LocalRepository(curdir)
        branch = repository.getCurrentBranch()
        head = repository.getHead()
        if branch is None:
            return head.getDescribe()
        current_branch = branch.name
        stripped_branch = current_branch.split('/')[0]
        if current_branch.startswith('release/') or current_branch.startswith('support/') or \
                                                    current_branch.startswith('hotfix/'):
            return head.getDescribe()
        if 'master' in stripped_branch:
            return head.getDescribe()
        else:
            try:
                return head.getDescribe('\*%s\*' % stripped_branch)
            except:
                pass
            return head.getDescribe()
        pass

    @classmethod
    def update_buildout_data(cls, buildout):
        import git
        from os import curdir
        repository = git.LocalRepository(curdir)
        branch = repository.getCurrentBranch()
        head = repository.getHead()
        from zc.buildout.buildout import Options
        data = {}
        data['version'] = cls.extract_version_tag().lstrip('v')
        data['author'] = head.getAuthorName()
        data['author_email'] = head.getAuthorEmail()
        buildout._data.update({SECTION_NAME: Options(buildout, SECTION_NAME, data)})
