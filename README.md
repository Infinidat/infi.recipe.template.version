Overview
========
Buildout recipe for templating files with version information from Git repositories.
In most Git repositories, you'll see a 'version bump' commit for releases, because the version tag is hard-coded, and we hate it.
So, we have this buildout recipe, which inherits from collective.recipe.template by adding a new section:

    [infi.recipe.template.version]
    version = <git describe>.strip('v')
    author = <git head commit author>
    author_email = <git head commit author email> """

Usage
=====

Here's an example for a buildout.cfg file that uses this recipe:

    [buildout]
    include-site-packages = false
    unzip = true
    parts = version.py

    [version.py]
    recipe = infi.recipe.template.version
    output = version.py
    input = inline:
        __version__ = "${infi.recipe.template.version:version}"

Checking out the code
=====================

This project uses buildout, and git to generate setup.py and __version__.py.
In order to generate these, run:

    python -S bootstrap.py -d -t
    bin/buildout -c buildout-version.cfg
    python setup.py develop

In our development environment, we use isolated python builds, by running the following instead of the last command:

    bin/buildout install development-scripts

