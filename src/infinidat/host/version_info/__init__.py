__import__("pkg_resources").declare_namespace(__name__)

import os
from os import path
import shlex

def run_cmd(cmd):
    from subprocess import Popen, PIPE
    p = Popen(shlex.split(cmd, posix=True), stdout=PIPE, stderr=None)
    p.wait()
    stdout = p.stdout.read()
    return (p.returncode, stdout)

def strip(string):
    output = string.strip('\n').strip('"')
    return output

class Commit(object):
    def __init__(self, ref):
        self._ref = ref

    @property
    def version_tag(self):
        current_branch = self.branches[0]
        stripped_branch = current_branch.split('/')[0]
        commandline = 'git describe %s --tags --match "*%s*"' % stripped_branch
        rc, out = run_cmd(commandline)
        return strip(out)

    @property
    def describe(self):
        commandline = 'git describe %s --tags' % self._ref
        rc, out = run_cmd(commandline)
        return strip(out)

    @property
    def date(self):
        commandline = 'git show %s --no-color --pretty=format:"%ai"' % self._ref
        rc, out = run_cmd(commandline)
        return strip(out)

    @property
    def head_commit_hash(self):
        commandline = 'git show %s --no-color --pretty=format:"%H"' % self._ref
        rc, out = run_cmd(commandline)
        return strip(out)

    @property
    def branches(self):
        """ returns a list of branches that contains this commit
        this method assumes the commit exists in the current branch
        which is placed first in the list
        """
        commandline = 'git branch --no-color --contains %s' % self._def
        rc, out = run_cmd(commandline)
        branches = out.splitlines()
        branches = Commit._move_starred_branch_to_top(branches)

    @classmethod
    def _move_starred_branch_to_top(cls, branches):
        starred_branch_names = filter(lambda x: x.startswith("* "), branches)

        if not starred_branch_names:
            return branches

        current_branch_name = starred_branch_names[0].partition("* ")[2]
        branches.remove(starred_branch_names[0])
        branches.insert(0, current_branch_name)
        return branches

class GitFlow(object):
    def __init__(self):

    @property
    def head(self):
        return Commit("HEAD")

