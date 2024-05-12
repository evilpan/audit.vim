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

Useful plugins:

- [junegunn/fzf][fzf] - for the `:FZF` to search and jump across files
- [junegunn/fzf.vim][fzf.vim] - for the `:RG`, `:Files`, `:Buffers` and other commands
- [MattesGroeger/vim-bookmarks][bookmark] - bookmark with comments

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
usage: avim.py make [-h] [-t] [-c] [-f] [-e EXCLUDES [EXCLUDES ...]] [src]

positional arguments:
  src                   project root direcotry to make

options:
  -h, --help            show this help message and exit
  -t                    create tag
  -c                    create cscope
  -f                    force overrite
  -e EXCLUDES [EXCLUDES ...]
                        exclude pathes
```

for example:
```sh
$ avim.py make -tc /path/to/linux-1.11
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
# or start with GUI(gvim)
$ avim.py open -g /src/project
```

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
a/s - go to previous/next buffer
J/K - move up/down for quickfix matching
```

> Note: the `<leader>` is config by user, which is `,` for me.

## Mark

```
m{a-zA-Z}         Set mark {a-zA-Z} at cursor position.
'{a-z} `{a-z}     Jump to the mark {a-z} in the current buffer.
:marks            List all current marks.
:Marks            List marks with fzf search.
```

You can also use [vim-bookmarks][vim-bookmarks] plugin for better bookmarks support.

| Action                                          | Shortcut    | Command                      |
|-------------------------------------------------|-------------|------------------------------|
| Add/remove bookmark at current line             | `mm`        | `:BookmarkToggle`            |
| Add/edit/remove annotation at current line      | `mi`        | `:BookmarkAnnotate <TEXT>`   |
| Show all bookmarks (toggle)                     | `ma`        | `:BookmarkShowAll`           |
| Save all bookmarks to a file                    |             | `:BookmarkSave <FILE_PATH>`  |
| Load bookmarks from a file                      |             | `:BookmarkLoad <FILE_PATH>`  |

## Folding

```
za      toggle open/close fold
zd      delete fold
zf      create fold
zfi}    create fold inside `{}` (excluding)
zfa}    create fold inside `{}` (including)
```


[fzf]: https://github.com/junegunn/fzf
[fzf.vim]: https://github.com/junegunn/fzf.vim
[bookmark]: https://github.com/MattesGroeger/vim-bookmarks
[modes]: https://gist.github.com/kennypete/1fae2e48f5b0577f9b7b10712cec3212