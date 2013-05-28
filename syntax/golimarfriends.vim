" Golimarfriends (For friends list)

hi OFFLINE ctermfg=darkgray
hi ONLINE ctermfg=green
hi AWAY ctermfg=yellow
hi DND ctermfg=red

syn match golimarfriendsOffline "(OFFLINE)"
syn match golimarfriendsOnline "(ONLINE)"
syn match golimarfriendsAway "(AWAY)"
syn match golimarfriendsDnd "(DND)"

hi def link golimarfriendsOffline OFFLINE
hi def link golimarfriendsOnline ONLINE
hi def link golimarfriendsAway AWAY
hi def link golimarfriendsDnd DND
