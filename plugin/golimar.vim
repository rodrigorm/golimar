if !has('python')
    finish
endif

" Load golimar.py either from the runtime directory (usually
" /usr/local/share/vim/vim71/plugin/ if you're running Vim 7.1) or from the
" home vim directory (usually ~/.vim/plugin/).
if filereadable($VIMRUNTIME."/plugin/python/golimar.py")
    pyfile $VIMRUNTIME/plugin/golimar.py
elseif filereadable($HOME."/.vim/plugin/python/golimar.py")
    pyfile $HOME/.vim/plugin/python/golimar.py
else
    " when we use pathogen for instance
    let $CUR_DIRECTORY=expand("<sfile>:p:h")

    if filereadable($CUR_DIRECTORY."/python/golimar.py")
        pyfile $CUR_DIRECTORY/python/golimar.py
    else
        call confirm('golimar.vim: Unable to find golimar.py. Place it in either your home vim directory or in the Vim runtime directory.', 'OK')
    endif
endif

python golimar = Golimar()

command! Golimar python golimar.open()
command! -nargs=1 GolimarChatWith python golimar.chatWith('<args>')
command! -nargs=1 GolimarSearchChat python golimar.searchChat('<args>')
command! -nargs=0 GolimarRender python golimar.render()

augroup Golimar
    autocmd!

    autocmd BufWriteCmd Compose :python golimar.send()
augroup END
