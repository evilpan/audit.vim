#!/usr/bin/env python3
import os
import json
import argparse
import subprocess as sb
from prettytable import PrettyTable

class Constants:
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    INDEX_FILE = os.path.expanduser("~/.audit.json")
    PATTN_FILE = os.path.join(BASE_DIR, "patterns.txt")
    OUT_LIST = ".project"
    OUT_TAGS = ".tags"
    OUT_CSDB = ".cscope"

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

def _find_best_session(startpoint, sessions):
    if startpoint == '':
        return None
    p = os.path.abspath(startpoint)
    if p in sessions:
        return p
    parent = os.path.dirname(p)
    if parent == p:
        # recursive?
        return None
    return _find_best_session(parent, sessions)

def create_filelist(src, out):
    log("collecting files ...")
    cmd = ["find", src, "-type", "f"]
    flist = set()
    with open(Constants.PATTN_FILE, 'r') as f:
        for line in f:
            flist.add(line.strip())
    cmd.extend(['-and', '(', '-name', 'Makefile'])
    for ext in flist:
        cmd.extend(['-o', '-name', ext])
    cmd.append(')')
    data = sb.check_output(cmd)
    with open(out, 'wb') as f:
        f.write(data)
    log("collected {} files: {}".format(
        _num_lines(out), out))

def create_tags(flist, out):
    log("adding ctags ...")
    sb.call(['rm', '-f', out])
    cmd = ['ctags', '--fields=+l', '--links=no', '-L', flist, '-f', out]
    sb.call(cmd)

def create_cscope(flist, out, kernel=False):
    log("adding cscope ...")
    sb.call(['rm', '-f', out])
    cmd = ['cscope', '-b', '-i', flist, '-f', out]
    if kernel:
        cmd.append('-k')
    sb.call(cmd)

def get_sessions():
    if not os.path.exists(Constants.INDEX_FILE):
        return []
    with open(Constants.INDEX_FILE, "r") as f:
        return json.load(f)

def update_sessions(sessions):
    with open(Constants.INDEX_FILE, "w") as f:
        json.dump(sessions, f)

def do_make(src, force=False, kernel=False):
    src = os.path.abspath(src)
    sessions = get_sessions()
    if src in sessions:
        log("session existed:", src)
        if not force:
            return
    f_list = os.path.join(src, Constants.OUT_LIST)
    f_tags = os.path.join(src, Constants.OUT_TAGS)
    f_csdb = os.path.join(src, Constants.OUT_CSDB)
    create_filelist(src, f_list)
    create_tags(f_list, f_tags)
    create_cscope(f_list, f_csdb, kernel)
    if src not in sessions:
        sessions.append(src)
        update_sessions(sessions)

def do_clean(src):
    src = os.path.abspath(src)
    sessions = get_sessions()
    if src in sessions:
        sessions.remove(src)
        log("update session:", src)
        update_sessions(sessions)
    else:
        log("session not exist")
    f_list = os.path.join(src, Constants.OUT_LIST)
    f_tags = os.path.join(src, Constants.OUT_TAGS)
    f_csdb = os.path.join(src, Constants.OUT_CSDB)
    for dat in [f_csdb, f_tags, f_list]:
        if os.path.exists(dat):
            log("remove", dat)
            os.remove(dat)

def do_info():
    sessions = get_sessions()
    fields = ['name', 'files', 'tags', 'cscope']
    t = PrettyTable(field_names=fields)
    t.align = "l"
    for src in sessions:
        f_list = os.path.join(src, Constants.OUT_LIST)
        f_tags = os.path.join(src, Constants.OUT_TAGS)
        f_csdb = os.path.join(src, Constants.OUT_CSDB)
        row = [src, _num_lines(f_list), _filesz(f_tags), _filesz(f_csdb)]
        t.add_row(row)
    print(t)

def do_open(args):
    sessions = get_sessions()
    vim = 'vim'
    if args.gui:
        vim = 'gvim'
    cmd = [vim, '-R']
    if args.tag:
        cmd.extend(['-t', args.tag])
    startpoint = '.'
    if args.file:
        startpoint = os.path.dirname(args.file)
    root = _find_best_session(startpoint, sessions)
    if root:
        f_csdb = os.path.join(root, Constants.OUT_CSDB)
        # f_list = os.path.join(root, Constants.OUT_LIST)
        cmd.extend([
            '-c',
            "silent cs add %s" % f_csdb,
        ])
    if args.file:
        cmd.append(args.file)
    env = os.environ.copy()
    env['AUDIT_VIM'] = '1'
    sb.call(cmd, env=env)

def main():
    parser = argparse.ArgumentParser(description='lightweight code audit system with vim')
    subparsers = parser.add_subparsers(dest='action', help='sub actions')

    p_add = subparsers.add_parser('make', help='create new audit session from current directory')
    p_add.add_argument('src', nargs='?', default='.', help='project root direcotry to make')
    p_add.add_argument('-k', dest='kernel', action='store_true', help='kernel mode')
    p_add.add_argument('-f', dest='force', action='store_true', help='force overrite')

    p_clean = subparsers.add_parser('clean', help='remove audit session')
    p_clean.add_argument('src', nargs='?', default='.')

    p_info = subparsers.add_parser('info', help='show info of audit sessions')

    p_open = subparsers.add_parser('open', help='vim wrapper to open files')
    p_open.add_argument('file', nargs="?", help='filename to open')
    p_open.add_argument('-t', dest='tag', help='open tag')
    p_open.add_argument('-g', dest='gui', action='store_true', help='use gvim instead of vim')

    args = parser.parse_args()
    if args.action == 'make':
        do_make(args.src, args.force, args.kernel)
    elif args.action == 'clean':
        do_clean(args.src)
    elif args.action == 'info':
        do_info()
    elif args.action == 'open':
        do_open(args)


if __name__ == '__main__':
    main()
