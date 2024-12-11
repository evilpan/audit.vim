" light-weight code audit tools

function! VisualSelectedText()
  let l:vm = visualmode()
  let l:bak = @@
  if l:vm ==# 'v'
    normal! `<v`>y
  elseif l:vm ==# 'char'
    normal! `[v`]y
  endif
  let l:text = @@
  let @@ = l:bak
  return l:text
endfunction

function! DoExecute(prefix, text, escape)
  let l:text = a:text
  if a:escape == 1
    " quote with ''
    let l:text = shellescape(a:text)
  elseif a:escape == 2
    " regex escape
    let l:text = escape(a:text, '^$()[]{}.*?\')
  elseif a:escape == 3
    " both
    let l:text = escape(a:text, '^$()[]{}.*?\')
    let l:text = shellescape(l:text)
  endif
  execute a:prefix . " " . l:text
endfunction

" commom options --- {{{
nnoremap [[ [{
nnoremap ]] ]}

" ReadOnly Mode
if $AVIM_SRC != ""
  augroup smartchdir
      " disable smart directory changing
      autocmd!
      set noautochdir
  augroup END
  " remap JK to navigate quickfix
  nnoremap J :cnext<cr>
  nnoremap K :cprev<cr>
  nnoremap H :colder<cr>
  nnoremap L :cnewer<cr>

  " remap movement shortcuts
  nnoremap i 5k
  nnoremap o 5j
  nnoremap O <Nop>
  nnoremap u 5<c-y>
  nnoremap d 5<c-e>
  nnoremap <silent><expr> c (&hls && v:hlsearch ? ':nohlsearch' : ':set hlsearch').'<cr>'
  nnoremap x <Nop>
  nnoremap p <Nop>
  nnoremap a :bprev<CR>
  nnoremap s :bnext<CR>
  nnoremap S <Nop>
  nnoremap B :Buffers<CR>

  let g:asyncrun_root = $AVIM_SRC
  lcd $AVIM_SRC
endif

if $AVIM_BOOKMARK != ""
  let g:bookmark_auto_save_file = $AVIM_BOOKMARK
endif

" augroup vimrc
"     " open quickfix window if updated
"     autocmd QuickFixCmdPost * botright copen 12
" augroup END
" }}}

" asyncrun.vim shortcuts --- {{{
nnoremap <leader>q :call asyncrun#quickfix_toggle(12)<CR>
command! -nargs=+ -complete=tag Grep AsyncRun -cwd=<root> rg "-n" <args>
if has('win32') || has('win64')
  nnoremap <silent><F2> :AsyncRun! -cwd=<root> findstr /n /s /C:"<C-R><C-W>"
        \ "\%CD\%\*.h" "\%CD\%\*.c*" <cr>
else
  " noremap <silent><F2> :AsyncRun! -cwd=<root> grep -n -s -R <C-R><C-W>
  "         \ --include='*.h' --include='*.c*' '<root>' <cr>
  " omit search path
  nnoremap <silent><F2> :AsyncRun! -errorformat=\%f:\%l:\%c:\%m -cwd=<root> rg --vimgrep -w <C-R><C-W> <cr>
  vnoremap <silent><F2> :call DoExecute("AsyncRun! -errorformat=\\%f:\\%l:\\%c:\\%m -cwd=<root> rg --vimgrep -w", VisualSelectedText(), 3)<cr>

  " search for method definition
  nnoremap <silent><F3> :AsyncRun! -errorformat=\%f:\%l:\%c:\%m -cwd=<root> rg --vimgrep " <C-R><C-W>\(.*\) .*\{" <cr>
endif
""" }}}

" ctags/taglist.vim shortcuts --- {{{
if $AVIM_TAGS != ""
  set tags=$AVIM_TAGS
else
  set tags=.tags; " upward search for ctags file
endif
" let Tlist_File_Fold_Auto_Close = 1
let Tlist_Show_One_File = 1
let Tlist_Exit_OnlyWindow = 1
nnoremap <leader>o :TlistToggle<CR>
" }}}

" cscope shortcuts --- {{{
if has("cscope")
  set cscopetag           " use cscope tag
  set cscopetagorder=1    " cstag search ctags first
  set cscopeverbose       " verbose output
  " set cscoperelative
  set cscopequickfix=s-,c-,d-,i-,t-,e-,a-,g-
  set cspc=3
endif

function CScopeFind(key, val)
  try
    execute "cscope find " . a:key . " " . a:val
  catch
    echo "Not Found: " . a:key . " " . a:val
    return 1
  endtry
  " jump back
  if len(getqflist()) > 1
    execute "normal! \<c-o>"
  endif
  call asyncrun#quickfix_toggle(12, 1)
endfunction

if $AVIM_CSDB != ""
  silent cs add $AVIM_CSDB
  " The following maps all invoke one of the following cscope search types:
  "
  "   's'   symbol: find all references to the token under cursor
  "   'g'   global: find global definition(s) of the token under cursor
  "   'c'   calls:  find all calls to the function name under cursor
  "   't'   text:   find all instances of the text under cursor
  "   'e'   egrep:  egrep search for the word under cursor
  "   'f'   file:   open the filename under cursor
  "   'i'   includes: find files that include the filename under cursor
  "   'd'   called: find functions that function under cursor calls
  " nnoremap <leader>fs :cscope find s <C-R>=expand("<cword>")<CR><CR>
  " nnoremap <leader>fg :cscope find g <C-R>=expand("<cword>")<CR><CR>
  " nnoremap <leader>fc :cscope find c <C-R>=expand("<cword>")<CR><CR>
  " nnoremap <leader>ft :cscope find t <C-R>=expand("<cword>")<CR><CR>
  " nnoremap <leader>fe :cscope find e <C-R>=expand("<cword>")<CR><CR>
  " nnoremap <leader>ff :cscope find f <C-R>=expand("<cfile>")<CR><CR>
  " nnoremap <leader>fi :cscope find i ^<C-R>=expand("<cfile>")<CR>$<CR>
  " nnoremap <leader>fd :cscope find d <C-R>=expand("<cword>")<CR><CR>
  nnoremap <leader>fs :call CScopeFind("s", expand("<cword>"))<CR>
  nnoremap <leader>fg :call CScopeFind("g", expand("<cword>"))<CR>
  nnoremap <leader>fc :call CScopeFind("c", expand("<cword>"))<CR>
  if $AVIM_TAGS != ""
    nnoremap <leader>ft :cstag <c-r>=expand('<cword>')<CR><CR>
  else
    nnoremap <leader>ft :call CScopeFind("t", expand("<cword>"))<CR>
  endif
  nnoremap <leader>fe :call CScopeFind("e", expand("<cword>"))<CR>
  " nnoremap <leader>ff :call CScopeFind("f", expand("<cfile>"))<CR>
  nnoremap <leader>fd :call CScopeFind("d", expand("<cword>"))<CR>
endif

" }}}

" fzf.vim shortcuts --- {{{
nnoremap <leader>ff :call DoExecute("FZF -1 -q", expand("<cword>"), 0)<cr>
vnoremap <leader>ff :call DoExecute("FZF -1 -q", VisualSelectedText(), 0)<cr>
nnoremap <leader>r :call DoExecute("RG", expand("<cword>"), 0)<cr>
vnoremap <leader>r :call DoExecute("RG", VisualSelectedText(), 2)<cr>
""" }}}
