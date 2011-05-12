__import__("pkg_resources").declare_namespace(__name__)

import collective.recipe.template


class Recipe(collective.recipe.template.Recipe):
    """
    see collective.recipe.template.Recipe
    the only addition on top of it is that we can to the buildout options
    a section named __name__ with some additional attributes
    """
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

    @classmethod
    def update_options_with_new_data(cls, buildout, options, data):
        from zc.buildout.buildout import Options
        data.update(options._raw)
        new_options = Options(buildout, options.name, data)
        new_options._created = []
        return new_options
        
class SetupPyRecipe(Recipe):
    """
    see Recipe class.
    the only addition on top of it is that we set the input to be setup.in
    and the output to be setup.py
    """
    def __init__(self, buildout, name, options):
        new_options = SetupPyRecipe.get_options_with_input_and_output(buildout, options)
        Recipe.__init__(self, buildout, name, new_options)

    @classmethod
    def get_options_with_input_and_output(cls, buildout, options):
        data = {}
        data['input'] = '${buildout:directory}/setup.in'
        data['output'] = '${buildout:directory}/setup.py'
        return Recipe.update_options_with_new_data(buildout, options, data)

class VersionPyRecipe(Recipe):
    """
    see Recipe class.
    the only addition on top of it is that we set the input to in-line
    and the output to be ${project:VERSION_FILE}
    """
    def __init__(self, buildout, name, options):
        new_options = VersionPyRecipe.get_options_with_input_and_output(buildout, options)
        Recipe.__init__(self, buildout, name, new_options)

    @classmethod
    def get_options_with_input_and_output(cls, buildout, options):
        data = {}
        data['inline'] = '\n'.join(["""__import__("pkg_resources").declare_namespace(__name__)""",
                                    """version = '${infinidat.host.recipe.version:version}'"""])
        data['output'] = '${project:VERSION_FILE}'
        return Recipe.update_options_with_new_data(buildout, options, data)

