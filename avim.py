#!/usr/bin/env python3
import os
import json
import argparse
import subprocess as sb
from prettytable import PrettyTable

def log(msg, *args, **kwargs):
    print('[+]', msg, *args, **kwargs)

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def _num_lines(filename):
    count = 0
    if not os.path.exists(filename):
        return count
    with open(filename, 'r') as f:
        for line in f:
            count += 1
    return count

def _filesz(filename):
    if not os.path.exists(filename):
        return 'N/A'
    return sizeof_fmt(os.stat(filename).st_size)

def _find_cond(opts, vals, sep='-o'):
    """
    e.x:
    opts = ['-name', '-type']
    vals = ['hello', 'f']
    sep = '-o'
    return: ['(', '-name', 'hello', '-o', '-type', 'f', ')']
    """
    if isinstance(opts, str):
        opts = [opts] * len(vals)
    else:
        assert(len(opts) == len(vals))
    if len(opts) == 0:
        return []
    elif len(opts) == 1:
        return [opts[0], vals[0]]
    else:
        cmd = []
        cmd.append('(')
        cmd.append(opts[0])
        cmd.append(vals[0])
        for i in range(1, len(opts)):
            cmd.append(sep)
            cmd.append(opts[i])
            cmd.append(vals[i])
        cmd.append(')')
    return cmd

class Project(object):
    OUT_LIST = ".files"
    OUT_TAGS = ".tags"
    OUT_CSDB = ".cscope"

    def __init__(self, src):
        self.src = os.path.abspath(src)

    @property
    def f_list(self):
        return os.path.join(self.src, self.OUT_LIST)

    @property
    def f_tags(self):
        return os.path.join(self.src, self.OUT_TAGS)

    @property
    def f_csdb(self):
        return os.path.join(self.src, self.OUT_CSDB)

    def collect_files(self, patterns, excludes=None):
        excludes = excludes if excludes else []
        log("collecting files ...")
        cmd = ["find", self.src]
        # https://stackoverflow.com/questions/4210042/how-to-exclude-a-directory-in-find-command
        for ex in excludes:
            ex = os.path.abspath(ex)
            cmd.extend(['-not', '(', '-path', ex, '-prune', ')'])
        cmd.extend(["-type", "f", "-and"] + _find_cond('-name', patterns, '-o'))
        data = sb.check_output(cmd)
        with open(self.f_list, 'wb') as f:
            f.write(data)
        log("collected {} files: {}".format(
            _num_lines(self.f_list), self.f_list))

    def create_tags(self):
        log("adding ctags ...")
        sb.call(['rm', '-f', self.f_tags])
        cmd = ['ctags', '--fields=+l', '--links=no', '-L', self.f_list, '-f', self.f_tags]
        sb.call(cmd)

    def create_cscope(self):
        log("adding cscope ...")
        sb.call(['rm', '-f', self.f_csdb])
        cmd = ['cscope', '-b', '-i', self.f_list, '-f', self.f_csdb]
        # if self.kernel_mode:
        #     cmd.append('-k')
        sb.call(cmd)


class AVIM:
    def __init__(self):
        self.basedir = os.path.dirname(os.path.realpath(__file__))
        self.pattern_file = os.path.join(self.basedir, "patterns.txt")
        self.workspace = os.path.expanduser("~/.audit.vim")
        self.index = os.path.join(self.workspace, "index.json")
        if not os.path.exists(self.workspace):
            os.mkdir(self.workspace)

    @property
    def sessions(self):
        if not os.path.exists(self.index):
            return []
        with open(self.index, "r") as f:
            return json.load(f)

    @property
    def patterns(self):
        out = set()
        with open(self.pattern_file, 'r') as f:
            for line in f:
                out.add(line.strip())
        return list(out)

    def save_sessions(self, sessions):
        with open(self.index, "w") as f:
            json.dump(sessions, f)

    def find_project(self, startpoint, sessions):
        if startpoint == '':
            return None
        p = os.path.abspath(startpoint)
        if p in sessions:
            return Project(p)
        parent = os.path.dirname(p)
        if parent == p:
            # recursive?
            return None
        return self.find_project(parent, sessions)

    def do_make(self, args):
        proj = Project(args.src)
        sessions = self.sessions
        if proj.src in sessions:
            log("session existed:", proj.src)
            if not force:
                return
        proj.collect_files(self.patterns, args.excludes)
        proj.create_tags()
        proj.create_cscope()
        if proj.src not in sessions:
            sessions.append(proj.src)
            self.save_sessions(sessions)

    def do_clean(self, src):
        proj = Project(src)
        sessions = self.sessions
        if proj.src in sessions:
            sessions.remove(proj.src)
            log("remove session:", proj.src)
            self.save_sessions(sessions)
        else:
            log("session not exist")
        for dat in [proj.f_csdb, proj.f_tags, proj.f_list]:
            if os.path.exists(dat):
                log("remove", dat)
                os.remove(dat)

    def do_info(self):
        sessions = self.sessions
        fields = ['name', 'files', 'tags', 'cscope']
        t = PrettyTable(field_names=fields)
        t.align = "l"
        for src in sessions:
            proj = Project(src)
            row = [src, _num_lines(proj.f_list), _filesz(proj.f_tags), _filesz(proj.f_csdb)]
            t.add_row(row)
        print(t)

    def do_open(self, args):
        sessions = self.sessions
        if args.file:
            startpoint = os.path.dirname(os.path.abspath(args.file))
        else:
            startpoint = os.getcwd()
        proj = self.find_project(startpoint, sessions)
        if not proj:
            log("project not found:", startpoint)
            return
        env = os.environ.copy()
        vim = 'vim'
        if args.gui:
            vim = 'gvim'
        cmd = [vim, '-R']
        if args.tag:
            cmd.extend(['-t', args.tag])
        if args.file:
            cmd.append(args.file)
        cmd.extend([
            '-c',
            "silent cs add %s" % proj.f_csdb,
        ])
        env['AUDIT_VIM'] = proj.src
        sb.call(cmd, env=env)


def main():
    parser = argparse.ArgumentParser(description='lightweight code audit system with vim')
    subparsers = parser.add_subparsers(dest='action', help='sub actions')

    p_add = subparsers.add_parser('make', help='create new audit session from current directory')
    p_add.add_argument('src', nargs='?', default='.', help='project root direcotry to make')
    p_add.add_argument('-k', dest='kernel', action='store_true', help='kernel mode')
    p_add.add_argument('-e', dest='excludes', nargs='+', help='exclude pathes')
    p_add.add_argument('-f', dest='force', action='store_true', help='force overrite')

    p_clean = subparsers.add_parser('clean', help='remove audit session')
    p_clean.add_argument('src', nargs='?', default='.')

    p_info = subparsers.add_parser('info', help='show info of audit sessions')

    p_open = subparsers.add_parser('open', help='vim wrapper to open files')
    p_open.add_argument('file', nargs="?", help='filename to open')
    p_open.add_argument('-t', dest='tag', help='open tag')
    p_open.add_argument('-g', dest='gui', action='store_true', help='use gvim instead of vim')

    args = parser.parse_args()
    avim = AVIM()
    if args.action == 'make':
        avim.do_make(args)
    elif args.action == 'clean':
        avim.do_clean(args.src)
    elif args.action == 'info':
        avim.do_info()
    elif args.action == 'open':
        avim.do_open(args)


if __name__ == '__main__':
    main()
