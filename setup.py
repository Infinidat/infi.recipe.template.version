
SETUP_INFO = dict(
    name = 'infinidat.git-version-tag',

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
    install_requires = ['setuptools'],

    namespace_packages = ['infinidat'],

    # packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,

    # A dictionary mapping entry point group names to strings or lists of strings defining the entry points
    entry_points = dict(
        console_scripts = [],
        gui_scripts = [])
    )

def setup():
    import sys
    sys.path.append('src')

    from setuptools import setup as _setup
    from setuptools import find_packages
    from infinidat.git_version_tag import GitFlow
    head = GitFlow().head
    SETUP_INFO['packages'] = find_packages('src')
    SETUP_INFO['version'] = head.version_tag.lstrip('v')
    SETUP_INFO['author'] = head.name
    SETUP_INFO['author_email'] = head.email
    SETUP_INFO['maintainer'] = head.name
    SETUP_INFO['maintainer_email'] = head.email
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

