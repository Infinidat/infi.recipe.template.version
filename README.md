Overview
========
Buildout recipe for templating files with version information from Git repositories.
In most Git repositories, you'll see a 'version bump' commit for releases, because the version tag is hard-coded, and we hate it.
So, we have this buildout recipe, which inherits from collective.recipe.template by adding a new section:

    [infi.recipe.template.version]
    version = <git describe>.strip('v')
    author = <git head commit author>
    author_email = <git head commit author email>
    homepage = <see description below>

The home deduction is being done in the following order:

* The value of option `homepage` in section `project` in the `buildout.cfg` file
* The url of git remote `origin` is being parsed, and attempted to be translated into a browser-friendly url
* As a last resort, a None value is set

For example:

* `git://github.com/Infinidat/infi.recipe.template.version.git` is translated to `https://github.com/Infinidat/infi.recipe.template.version`

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

Checking out the code
=====================

Run the following:

    easy_install -U infi.projector
    projector devenv build
