__import__("pkg_resources").declare_namespace(__name__)

import os
from os import path
import shlex

def run_cmd(cmd, return_stderr = False):
    from subprocess import Popen, PIPE
    p = Popen(shlex.split(cmd, posix = True), stdout = PIPE, stderr = PIPE if return_stderr else None)
    p.wait()
    stdout = p.stdout.read()
    if return_stderr:
        stderr = p.stderr.read()
        return (p.returncode, stdout, stderr)
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
        if current_branch.startswith('release/') or current_branch.startswith('support/') or current_branch.startswith('hotfix/'):
            return self.describe  
        if 'master' in stripped_branch:
            return self.describe
        else:
            try:
                return self._describe_match(stripped_branch)
            except OSError:
                pass
            return self.describe

    def _describe_match(self, match):
        commandline = 'git describe %s --tags --match "*%s*"' % (self._ref, match)
        rc, out,err = run_cmd(commandline, True)
        if 'fatal' in err.lower():
            raise OSError("git tag not found")
        return strip(out)
    @property
    def describe(self):
        commandline = 'git describe %s --tags' % self._ref
        rc, out,err = run_cmd(commandline, True)
        if 'fatal' in err.lower():
            raise OSError("git tag not found")
        return strip(out)

    @property
    def date(self):
        commandline = 'git show %s %s' % (self._ref, '--no-color --pretty=format:"%ai"')
        rc, out = run_cmd(commandline)
        return out.splitlines()[0].strip().strip('"')

    @property
    def hash(self):
        commandline = 'git show %s %s' % (self._ref, '--no-color --pretty=format:"%H"')
        rc, out = run_cmd(commandline)
        return out.splitlines()[0].strip().strip('"')

    @property
    def name(self):
        commandline = 'git show %s %s' % (self._ref, '--no-color --pretty=format:"%an"')
        rc, out = run_cmd(commandline)
        return out.splitlines()[0].strip().strip('"')

    @property
    def email(self):
        commandline = 'git show %s %s' % (self._ref, '--no-color --pretty=format:"%ae"')
        rc, out = run_cmd(commandline)
        return out.splitlines()[0].strip().strip('"')

    @property
    def branches(self):
        """ returns a list of branches that contains this commit
        this method assumes the commit exists in the current branch
        which is placed first in the list
        """
        commandline = 'git branch --no-color --contains %s' % self._ref
        rc, out = run_cmd(commandline)
        branches = out.splitlines()
        branches = Commit._move_starred_branch_to_top(branches)
        return branches

    @classmethod
    def _move_starred_branch_to_top(cls, branches):
        from copy import copy
        branches = copy(branches)
        starred_branch_names = filter(lambda x: x.startswith("* "), branches)

        if not starred_branch_names:
            return branches

        current_branch_name = starred_branch_names[0].partition("* ")[2]
        branches.remove(starred_branch_names[0])
        branches.insert(0, current_branch_name)
        return branches

class GitFlow(object):
    def __init__(self):
        command = 'git show'
        rc, out, err = run_cmd(command, True)
        if 'fatal' in err.lower():
            raise OSError("not a git repository or a bare repository")

    @property
    def head(self):
        return Commit("HEAD")

