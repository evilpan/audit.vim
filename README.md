# VIM Audit

Light-weight code audit with VIM

which contains:

- A shell script wrapper
- A vim plugin

# Reference

- https://github.com/universal-ctags/ctags
- https://github.com/chazy/cscope_maps/blob/master/plugin/cscope_maps.vim
- cscope.vim

# Install
```sh
python3 -m pip install -U rich
make install
```

Extra tools and plugins:

- [taglist.vim](https://www.vim.org/scripts/script.php?script_id=273) -- left side taglist
- [asyncrun.vim](https://github.com/skywind3000/asyncrun.vim) -- run shell command async in vim.
- [ripgrep](https://github.com/BurntSushi/ripgrep) -- rg tool to perform fast search.
- [fzf](https://github.com/junegunn/fzf) -- fuzzy search path.

## macOS

```sh
brew install universal-ctags
brew install cscope
```

## Linux

```sh
sudo apt install -y exuberant-ctags cscope
```

# Quick Start

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

# VIM Tips


## Fold

- za - toggle open/close fold
- zd - delete fold
- zf - create fold
- zfa} - create fold for current block
