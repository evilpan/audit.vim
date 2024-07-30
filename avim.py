#!/usr/bin/env python3
import os
import time
import json
import shutil
import argparse
import subprocess as sb
import fnmatch
import ast
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table

WORKSPACE = os.path.expanduser("~/.audit.vim")
CONN = Console()

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
        return '-'
    return sizeof_fmt(os.stat(filename).st_size)


class Project(object):
    OUT_LIST = "files"
    OUT_TAGS = "tags"
    OUT_CSDB = "cscope"
    OUT_BOOKMARK = "bookmark"

    def __init__(self, src, data=None):
        # full path
        self.src = os.path.abspath(src)
        self.data = data

    def create(self, suffixes, excludes=None, tag=True, cscope=True):
        if self.data is None:
            # create new data dir
            self.data = os.path.join(WORKSPACE, str(int(time.time())))
        if not os.path.exists(self.data):
            os.mkdir(self.data)
        self.collect_files(suffixes, excludes)
        if tag:
            self.create_tags()
        if cscope:
            self.create_cscope()

    def remove(self):
        if os.path.exists(self.data):
            shutil.rmtree(self.data)

    @property
    def timestamp(self):
        return int(os.path.basename(self.data))

    @property
    def f_bookmark(self):
        return os.path.join(self.data, self.OUT_BOOKMARK)

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
            if p.is_symlink():
                continue
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
            if p.suffix.lower() in suffixes:
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
                ft = line.strip()
                out.add(ft.lower())
        return list(out)

    def save_sessions(self, sessions):
        with open(self.index, "w") as f:
            json.dump(sessions, f, indent=2)

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

    def _read_bookmark(self, filename):
        count = 0
        if not os.path.exists(filename):
            return '-'
        with open(filename, 'r') as f:
            _ = f.readline()
            line = f.readline()
        bm_sessions = line.split("=", 1)[1]
        bm_sessions = ast.literal_eval(bm_sessions)
        for bms in bm_sessions['default'].values():
            count += len(bms)
        return count

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
        proj.create(self.suffixes, args.excludes, args.tag, args.cscope)
        sessions = self.sessions
        sessions[proj.src] = proj.data
        self.save_sessions(sessions)

    def do_rm(self, src: str, sessions=None, is_glob=False):
        """
        src: abspath of source tree
        """
        matches = []
        if sessions is None:
            sessions = self.sessions
        if is_glob:
            matches.extend(fnmatch.filter(sessions.keys(), src))
        else:
            key = os.path.abspath(src)
            if key in sessions:
                matches.append(key)
        if not matches:
            log(f"not match any sessions: {src}")
            return
        for key in matches:
            proj = Project(key, sessions[key])
            proj.remove()
            log("remove session:", proj.src)
            del sessions[proj.src]
        self.save_sessions(sessions)

    def do_info(self, args):
        sessions = self.sessions
        if not sessions:
            log("No data")
            return
        fields = ['location', 'timestamp', 'files', 'ctags', 'cscope', 'bookmark']
        t = Table(*fields)
        rows = []
        for src, data in sessions.items():
            proj = Project(src, data)
            if args.filter:
                lhs, rhs = args.filter, proj.src
                if args.ignore_case:
                    lhs, rhs = lhs.lower(), rhs.lower()
                if lhs not in rhs:
                    continue
            if not os.path.exists(src):
                src = f"[bold red]{src}[/]"
            timestamp = datetime.fromtimestamp(proj.timestamp)
            rows.append([
                src,
                timestamp,
                _num_lines(proj.f_list),
                _filesz(proj.f_tags),
                _filesz(proj.f_csdb),
                self._read_bookmark(proj.f_bookmark),
            ])
        idx = fields.index(args.sortby)
        for row in sorted(rows, key = lambda r: r[idx], reverse=True):
            t.add_row(*[str(col) for col in row])
        CONN.print(t)

    def do_open(self, args):
        sessions = self.sessions
        env = os.environ.copy()
        cmd = ['vim', '-R', '-M', '-n']
        if args.gui:
            cmd.append('-g')
        if args.tag:
            cmd.extend(['-t', args.tag])
        if args.file:
            cmd.append(args.file)
            fd = os.path.abspath(args.file)
            if os.path.isdir(fd):
                startpoint = fd
            else:
                startpoint = os.path.dirname(fd)
        else:
            startpoint = os.getcwd()
        proj = self.find_project(startpoint, sessions)
        if not proj:
            log("project not found:", startpoint)
            env['AVIM_SRC'] = os.getcwd()
        else:
            env['AVIM_SRC'] = proj.src
            env['AVIM_BOOKMARK'] = proj.f_bookmark
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
    p_add.add_argument('-t', dest='tag', action='store_true', help='create tag')
    p_add.add_argument('-c', dest='cscope', action='store_true', help='create cscope')
    p_add.add_argument('-f', dest='force', action='store_true', help='force overrite')
    p_add.add_argument('-e', dest='excludes', nargs='+', help='exclude pathes')

    p_rm = subparsers.add_parser('rm', help='remove audit session')
    p_rm.add_argument('-g', '--glob', action='store_true', help='enable glob match')
    p_rm.add_argument('src', nargs='*', default=['.'])

    p_info = subparsers.add_parser('info', help='list info of audit sessions',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p_info.add_argument("-i", dest="ignore_case", action="store_true", help="filter ignore case")
    p_info.add_argument("filter", nargs="?", help="filter projects by location")
    p_info.add_argument("-s", dest="sortby", choices=["location", "files", "timestamp"],
            default="timestamp", help="sort results by column")

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
            avim.do_rm(src, is_glob=args.glob)
    elif args.action == 'info':
        avim.do_info(args)
    elif args.action == 'open':
        avim.do_open(args)


if __name__ == '__main__':
    main()
