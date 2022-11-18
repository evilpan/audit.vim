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
brew install universal-ctags
brew install cscope
make install
```

Extra tools and plugins:

- [asyncrun.vim](https://github.com/skywind3000/asyncrun.vim) -- run shell command async in vim.
- [ripgrep](https://github.com/BurntSushi/ripgrep) -- rg tool to perform fast search.
- [fzf](https://github.com/junegunn/fzf) -- fuzzy search path, not used yet.

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
```

> Note: the `<leader>` is config by user, which is `,` for me.
