# VIM Audit

Light-weight Code Audit with VIM

which contains:

- A shell script wrapper
- A vim plugin

# Reference

- https://github.com/chazy/cscope_maps/blob/master/plugin/cscope_maps.vim
- cscope.vim

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

Note the `<leader>` is `,`

# TODO

[x] move .tags/.files/.cscope to global directory avoiding project pollution
