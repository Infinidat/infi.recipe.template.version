
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
    def update_buildout_data(cls, buildout):
        from ..git import GitFlow
        from zc.buildout.buildout import Options
        data = {}
        head = GitFlow().head
        data['version'] = head.version_tag.lstrip('v')
        data['author'] = head.name
        data['author_email'] = head.email
        buildout._data.update({SECTION_NAME: Options(buildout, SECTION_NAME, data)})
