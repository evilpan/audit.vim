" light-weight code audit tools

" commom options --- {{{
if $AUDIT_VIM != ""
    augroup smartchdir
        " disable smart directory changing
        autocmd!
    augroup END
    " remap JK to navigate quickfix
    nnoremap J :cnext<cr>
    nnoremap K :cprev<cr>
    let g:asyncrun_root = $AUDIT_VIM
    lcd $AUDIT_VIM
    echom "Project: " . $AUDIT_VIM
endif

" augroup vimrc
"     " open quickfix window if updated
"     autocmd QuickFixCmdPost * botright copen 12
" augroup END
" }}}

" asyncrun.vim shortcuts --- {{{
nnoremap <leader>q :call asyncrun#quickfix_toggle(12)<CR>
command! -nargs=+ -complete=tag Grep AsyncRun -cwd=<root> rg "-n" <args>
function! GrepOperator(type)
    " copy the selected word
    let l:saved_unnamed_register = @@
    if a:type ==# 'v'
        normal! `<v`>y
    elseif a:type ==# 'char'
        normal! `[v`]y
    else
        return
    endif
    " escape regex special characters
    let l:regex = escape(@@, '()[].*?')
    execute "AsyncRun! -cwd=<root> rg -n " . shellescape(l:regex)
    let @@ = l:saved_unnamed_register
endfunction

if has('win32') || has('win64')
    nnoremap <silent><F2> :AsyncRun! -cwd=<root> findstr /n /s /C:"<C-R><C-W>"
            \ "\%CD\%\*.h" "\%CD\%\*.c*" <cr>
else
    " noremap <silent><F2> :AsyncRun! -cwd=<root> grep -n -s -R <C-R><C-W>
    "         \ --include='*.h' --include='*.c*' '<root>' <cr>
    " omit search path
    nnoremap <silent><F2> :AsyncRun! -cwd=<root> rg -n -w <C-R><C-W> <cr>
    vnoremap <silent><F2> :<c-u>call GrepOperator(visualmode())<cr>
endif
""" }}}

" ctags/taglist.vim shortcuts --- {{{
set tags=.tags; " upward search for ctags file
" let Tlist_File_Fold_Auto_Close = 1
let Tlist_Show_One_File = 1
let Tlist_Exit_OnlyWindow = 1
nnoremap <leader>o :TlistToggle<CR>
" }}}

" cscope shortcuts --- {{{

function CScopeFind(key, val)
    try
        execute "cscope find " . a:key . " " . a:val
    catch
        echo "Not Found: " . a:key . " " . a:val
        return 1
    endtry
    " jump back
    execute "normal! \<c-o>"
    call asyncrun#quickfix_toggle(12, 1)
endfunction

" set efm for cscope shell command output
" remote/proto/EdrMessage.pb.cc MergeFrom 7401 mutable_process_info()->::oneagent_proto
" set errorformat+=%f\ %o\ %l\ %m

if has("cscope")
    set cscopetag           " use cscope tag
    set cscopetagorder=1    " but search ctags first since it's more accurate
    set cscopeverbose       " verbose output
    " set cscoperelative
    set cscopequickfix=s-,c-,d-,i-,t-,e-,a-,g-
    set cspc=3
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
    nnoremap <leader>fg :cstag <c-r>=expand('<cword>')<CR><CR>
    nnoremap <leader>fc :call CScopeFind("c", expand("<cword>"))<CR>
    nnoremap <leader>ft :call CScopeFind("t", expand("<cword>"))<CR>
    nnoremap <leader>fe :call CScopeFind("e", expand("<cword>"))<CR>
    nnoremap <leader>fd :call CScopeFind("d", expand("<cword>"))<CR>
endif
" }}}
