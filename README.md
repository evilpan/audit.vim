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
- junegunn/fzf
- junegunn/fzf.vim

External command-line tools:

- [ctags](https://github.com/universal-ctags/ctags) - Universal Ctags；
- [cscope](https://cscope.sourceforge.net/) - search for symbol, definition, etc.
- [ripgrep](https://github.com/BurntSushi/ripgrep) - rg tool to perform fast search
- [fzf](https://github.com/junegunn/fzf) - used for fuzzy search

## macOS

```sh
brew install universal-ctags cscope
```

## Linux

```sh
sudo apt install -y universal-ctags cscope
```

# VIM Tips

Shortcuts defined in audit.vim:

```
<leader>fs - find symbol
<leader>fg - find global
<leader>ft - find tag
<leader>fc - find what calling this function
<leader>fd - find what called by this function
<leader>fe - find expr
<leader>ff - find find, which is rarelly used

<leader>o - toggle taglist (left)
<leader>q - toggle quickfix list (bottom)

F2 - search with rg
i/o - move up/down
u/d - page up/down

r/R - create fold for current block
```

> Note: the `<leader>` is config by user, which is `,` for me.

## Mark

```
m{a-zA-Z}		    Set mark {a-zA-Z} at cursor position.
'{a-z}  `{a-z}		Jump to the mark {a-z} in the current buffer.
:marks              List all current marks.
```

## Folding

```
za      toggle open/close fold
zd      delete fold
zf      create fold
zfa}    create fold for current block
```
