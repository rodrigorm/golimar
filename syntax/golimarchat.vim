" Golimarfriends (For friends list)

hi DATETIME ctermfg=darkgray
hi USERNAME ctermfg=blue

syn match golimarchatDatetime "^\[.\{-}\]"
syn match golimarchatUsername "\s\s.\{-}:"

hi def link golimarchatDatetime DATETIME
hi def link golimarchatUsername USERNAME
