# Audit.VIM

light weight code audit (code review) tool based on VIM.

![audit.vim](https://img-blog.csdnimg.cn/direct/10717e760e96410b93c1cf02269f8c56.png)

which contains:

- A shell script wrapper
- A vim plugin

# Install

```sh
python3 -m pip install -U rich
make install
```

Required plugins:

- [vim-scripts/taglist.vim](https://www.vim.org/scripts/script.php?script_id=273) - left side taglist
- [skywind3000/asyncrun.vim](https://github.com/skywind3000/asyncrun.vim) - run shell command async in vim
- [junegunn/fzf][fzf] - use the `:FZF` to search and jump across files
- [junegunn/fzf.vim][fzf.vim] - use the `:RG`, `:Files`, `:Buffers` and other commands

External command-line tools:

- [ctags](https://github.com/universal-ctags/ctags) - Universal Ctags；
- [cscope](https://cscope.sourceforge.net/) - search for symbol, definition, etc.
- [ripgrep](https://github.com/BurntSushi/ripgrep) - rg tool to perform fast search
- [fzf][fzf] - used for fuzzy search

## macOS

```sh
brew install universal-ctags cscope
```

## Linux

```sh
sudo apt install -y universal-ctags cscope
```

# Run

index a project:
```sh
$ avim.py make -h
usage: avim.py make [-h] [-k] [-e EXCLUDES [EXCLUDES ...]] [-f] [src]

positional arguments:
  src                   project root direcotry to make

options:
  -h, --help            show this help message and exit
  -k                    kernel mode
  -e EXCLUDES [EXCLUDES ...]
                        exclude pathes
  -f                    force overrite
```

for example:
```sh
$ avim.py make /path/to/linux-1.11
```

list indexed projects:
```sh
$ avim.py info
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━┓
┃ source             ┃ files ┃ tags    ┃ cscope ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━┩
│ /data/src/project1 │ 2429  │ 10.7MB  │ 14.0MB │
│ /data/src/project2 │ 17013 │ 103.7MB │ 84.8MB │
└────────────────────┴───────┴─────────┴────────┘
```

remove an index:
```sh
$ avim.py rm /path/to/linux-1.11
```

open vim/gvim of with indexed tags/cscopes:
```sh
$ avim.py open .
# or start with gvim
$ avim.py -g open .
```

open vim without index file(livegrep), use fzf.vim for searching and jumping.
```sh
usage: avim.py lv [-h] [-r RG] [root] [extra_args ...]

positional arguments:
  root
  extra_args  extra arguments that pass to vim

options:
  -h, --help  show this help message and exit
  -r RG       init pattern to search with ripgrep

```

Some useful commands are `:FZF`, `:Files`, `:RG`, `:Marks`, `:Buffers`, see [fzf.vim][fzf.vim].

# VIM Tips

Shortcuts defined in audit.vim:

```
<leader>fs - find symbol
<leader>fg - find global
<leader>ft - find tag (based on ctags)
<leader>fc - find what calling this function
<leader>fd - find what called by this function
<leader>fe - find expr
<leader>ff - find file (based on fzf)

<leader>o - toggle taglist (left)
<leader>q - toggle quickfix list (bottom)

F2 - search current word or selected word with ripgrep
i/o - move up/down
u/d - page up/down

r/R - create fold for current block
```

> Note: the `<leader>` is config by user, which is `,` for me.

## Mark

```
m{a-zA-Z}         Set mark {a-zA-Z} at cursor position.
'{a-z} `{a-z}     Jump to the mark {a-z} in the current buffer.
:marks            List all current marks.
```

## Folding

```
za      toggle open/close fold
zd      delete fold
zf      create fold
zfa}    create fold for current block
```


[fzf]: https://github.com/junegunn/fzf
[fzf.vim]: https://github.com/junegunn/fzf.vim
