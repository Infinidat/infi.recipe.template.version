
SETUP_INFO = dict(
    name = 'infinidat.host.version-info',
    version = '0.1',
    author = 'Your Name Here',
    author_email = 'username@infinidat.com',
    maintainer = 'Your Name Here',
    maintainer_email = 'username@infinidat.com',

    url = 'http://www.infinidat.com',
    keywords = 'string of space-separated keywords',
    license = 'PSF',
    description = 'short description',
    long_description = ('long description'),

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
    install_requires = [],

    # A dictionary mapping names of "extras" (optional features of your project) to strings or lists of strings specifying what
    # other distributions must be installed to support those features.
    extras_require = {},

    # A string or list of strings specifying what other distributions need to be present in order for the setup script to run.
    setup_requires = '',

    test_suite = '',
    tests_require = {},

    dependency_links = [],

    namespace_packages = ['infinidat.host'],

    # packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,

    # A dictionary mapping entry point group names to strings or lists of strings defining the entry points
    entry_points = dict(
        console_scripts = [],
        gui_scripts = [])

    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

