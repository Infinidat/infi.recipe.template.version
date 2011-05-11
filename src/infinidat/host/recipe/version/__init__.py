__import__("pkg_resources").declare_namespace(__name__)

import collective.recipe.template

class Recipe(collective.recipe.template.Recipe):
    def __init__(self, buildout, name, options):
        Recipe.update_buildout_data(buildout)
        collective.recipe.template.Recipe.__init__(self, buildout, name, options)
        
    @classmethod
    def update_buildout_data(cls, buildout):
        from git import GitFlow
        from zc.buildout.buildout import Options
        data = {}
        head = GitFlow().head
        data['version'] = head.version_tag.lstrip('v')
        data['author'] = head.name
        data['author_email'] = head.email
        buildout._data.update({__name__: Options(buildout, __name__, data)})
        