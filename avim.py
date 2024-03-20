#!/usr/bin/env python3
import os
import time
import json
import shutil
import argparse
import subprocess as sb
from pathlib import Path

WORKSPACE = os.path.expanduser("~/.audit.vim")

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


class Project(object):
    OUT_LIST = "files"
    OUT_TAGS = "tags"
    OUT_CSDB = "cscope"

    def __init__(self, src, data=None):
        # full path
        self.src = os.path.abspath(src)
        self.data = data

    def create(self, suffixes, excludes=None):
        if self.data is None:
            # create new data dir
            self.data = os.path.join(WORKSPACE, str(int(time.time())))
        if not os.path.exists(self.data):
            os.mkdir(self.data)
        self.collect_files(suffixes, excludes)
        self.create_tags()
        self.create_cscope()

    def remove(self):
        if os.path.exists(self.data):
            shutil.rmtree(self.data)

    @property
    def f_list(self):
        return os.path.join(self.data, self.OUT_LIST)

    @property
    def f_tags(self):
        return os.path.join(self.data, self.OUT_TAGS)

    @property
    def f_csdb(self):
        return os.path.join(self.data, self.OUT_CSDB)

    def collect_files(self, suffixes, excludes=None):
        excludes = [Path(e).absolute() for e in excludes] if excludes else []
        log("collecting files ...")
        out = []
        num_ignored = 0
        num_excluded = 0
        for p in Path(self.src).glob("**/*"):
            if not p.is_file():
                continue
            if excludes:
                exc = False
                for ex in excludes:
                    if ex in p.absolute().parents:
                        exc = True
                        break
                if exc:
                    num_excluded += 1
                    continue
            if p.suffix in suffixes:
                # relative path
                out.append(str(p))
            else:
                num_ignored += 1
        log("collected {} files, {} ignored, {} excluded".format(
            len(out), num_ignored, num_excluded))
        with open(self.f_list, 'w') as f:
            for line in out:
                f.write(line + "\n")

    def create_tags(self):
        log("adding ctags ...")
        if os.path.exists(self.f_tags):
            os.remove(self.f_tags)
        cmd = ['ctags', '--fields=+l', '--links=no', '-L', self.f_list, '-f', self.f_tags]
        sb.call(cmd)

    def create_cscope(self):
        log("adding cscope ...")
        if os.path.exists(self.f_csdb):
            os.remove(self.f_csdb)
        buf = ''
        with open(self.f_list, 'r') as f:
            for line in f:
                if ' ' in line:
                    line = '"%s"\n' % line[:-1]
                buf += line
        cmd = ['cscope', '-b', '-i', "-", '-f', self.f_csdb]
        # if self.kernel_mode:
        #     cmd.append('-k')
        try:
            p = sb.Popen(cmd, stdin=sb.PIPE)
            p.communicate(input=buf.encode())
        except KeyboardInterrupt:
            log("user interrupt, cleanning...")
            # TODO: remove n.cscope file


class AVIM:
    def __init__(self):
        self.basedir = os.path.dirname(os.path.realpath(__file__))
        self.suffix_file = os.path.join(self.basedir, "suffixes.txt")
        self.index = os.path.join(WORKSPACE, "index.json")
        if not os.path.exists(WORKSPACE):
            os.mkdir(WORKSPACE)

    @property
    def sessions(self):
        """
        {
            "src": "data_dir",
            "src2": "data_dir2",
        }
        """
        if not os.path.exists(self.index):
            return {}
        with open(self.index, "r") as f:
            return json.load(f)

    @property
    def suffixes(self):
        out = set()
        with open(self.suffix_file, 'r') as f:
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
            return Project(p, sessions[p])
        parent = os.path.dirname(p)
        if parent == p:
            # recursive?
            return None
        return self.find_project(parent, sessions)

    def do_make(self, args):
        proj = Project(args.src)
        if not os.path.exists(proj.src):
            log("path not exists:", proj.src)
            return
        sessions = self.sessions
        if proj.src in sessions:
            log("project existed:", proj.src)
            if not args.force:
                return
            # clear old session first
            self.do_rm(proj.src, sessions[proj.src])
        # create session
        proj.create(self.suffixes, args.excludes)
        sessions = self.sessions
        sessions[proj.src] = proj.data
        self.save_sessions(sessions)

    def do_rm(self, src, sessions=None):
        """
        src: abspath of source tree
        """
        if sessions is None:
            sessions = self.sessions
        if src not in sessions:
            log("session not exist")
            return
        proj = Project(src, sessions[src])
        proj.remove()
        log("remove session:", proj.src)
        del sessions[proj.src]
        self.save_sessions(sessions)

    def do_info(self):
        from prettytable import PrettyTable
        sessions = self.sessions
        fields = ['source', 'files', 'tags', 'cscope']
        t = PrettyTable(field_names=fields)
        t.align = "l"
        for src, data in sessions.items():
            proj = Project(src, data)
            row = [src, _num_lines(proj.f_list), _filesz(proj.f_tags), _filesz(proj.f_csdb)]
            t.add_row(row)
        print(t)

    def do_open(self, args):
        sessions = self.sessions
        env = os.environ.copy()
        vim = 'vim'
        if args.gui:
            vim = 'gvim'
        cmd = [vim, '-M', '-n']
        if args.tag:
            cmd.extend(['-t', args.tag])
        if args.file:
            cmd.append(args.file)
            startpoint = os.path.dirname(os.path.abspath(args.file))
        else:
            startpoint = os.getcwd()
        proj = self.find_project(startpoint, sessions)
        if not proj:
            log("project not found:", startpoint)
            env['AVIM_SRC'] = os.getcwd()
        else:
            env['AVIM_SRC'] = proj.src
            if os.path.exists(proj.f_csdb):
                env['AVIM_CSDB'] = proj.f_csdb
            if os.path.exists(proj.f_tags):
                # use envrioment to make "vim -t" work
                env['AVIM_TAGS'] = proj.f_tags
        if args.extra_args:
            cmd.extend(args.extra_args)
        sb.call(cmd, env=env)


def main():
    parser = argparse.ArgumentParser(description='lightweight code audit system with vim')
    subparsers = parser.add_subparsers(dest='action', help='sub actions')

    p_add = subparsers.add_parser('make', help='create new audit session from current directory')
    p_add.add_argument('src', nargs='?', default='.', help='project root direcotry to make')
    p_add.add_argument('-k', dest='kernel', action='store_true', help='kernel mode')
    p_add.add_argument('-e', dest='excludes', nargs='+', help='exclude pathes')
    p_add.add_argument('-f', dest='force', action='store_true', help='force overrite')

    p_rm = subparsers.add_parser('rm', help='remove audit session')
    p_rm.add_argument('src', nargs='*', default=['.'])

    p_info = subparsers.add_parser('info', help='show info of audit sessions')

    p_open = subparsers.add_parser('open', help='vim wrapper to open files')
    p_open.add_argument('file', nargs="?", help='filename to open')
    p_open.add_argument('-t', dest='tag', help='open tag')
    p_open.add_argument('-g', dest='gui', action='store_true', help='use gvim instead of vim')
    p_open.add_argument("extra_args", nargs="*", help="extra arguments that pass to vim")

    args = parser.parse_args()
    avim = AVIM()
    if args.action == 'make':
        avim.do_make(args)
    elif args.action == 'rm':
        for src in args.src:
            src = os.path.abspath(src)
            avim.do_rm(src)
    elif args.action == 'info':
        avim.do_info()
    elif args.action == 'open':
        avim.do_open(args)


if __name__ == '__main__':
    main()
