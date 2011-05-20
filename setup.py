
SETUP_INFO = dict(
    name = 'infi.recipe.template.version',
    version = '0.3.1',
    author = 'Guy Rozendorn',
    author_email = 'guyr@infinidat.com',

    license = 'BSD',
    description = 'an extension to collective.recipe.template',
    long_description = ("""this extends collective.recipe.template by adding adding a new section:
[infi.recipe.template.version],
version = <git describe>.strip("v"),
author = <git head commit author>,
author_email = <git head commit author email>,
with this, you can inject the version into setup.py and modules"""),

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # A string or list of strings specifying what other distributions need to be installed when this one is
    # We use namespaced packages so we must require setuptools
    install_requires = ['setuptools', 'zc.buildout', 'collective.recipe.template', 'gitpy'],

    namespace_packages = ['infi', 'infi.recipe', 'infi.recipe.template'],

    # packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe = False,

    entry_points = """
    [zc.buildout]
    default = infi.recipe.template.version.recipe:Recipe
    """
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

