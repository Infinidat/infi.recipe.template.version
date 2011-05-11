
SETUP_INFO = dict(
    name = 'infinidat.host.recipe.version',
    version = '0.1.5',
    author = 'Guy Rozendorn',
    author_email = 'guy@rzn.co.il',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = 'simple interface in Python to get version tags out of git describe',
    long_description = ('simple interface in Python to get version tags out of git describe'),

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
    install_requires = ['setuptools', 'zc.buildout', 'collective.recipe.template'],

    namespace_packages = ['infinidat', 'infinidat.host', 'infinidat.host.recipe'],

    # packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe = False,

    entry_points = """
    [zc.buildout]
    default = infinidat.host.recipe.version:Recipe
    """
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

