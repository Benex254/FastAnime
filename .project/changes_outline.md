# Changes

-# # only load trailers when needed

- change how media card loader class works
- create function to get a trailer url and cache it for 360 secs
- refactor the codebase to reflect proposed changes

-# # # change how media card loader class works

- remove unnecesarry code
- make the media card function to still work so it doesn't cause a break in existing functionality- add a get trailer function which takes a callback

# - # Use one media popup for all the media cards

# 9 june

# # search screen

change the search results layout to be a recycle grid layout

change the trending bar to be a recyle box layout

AFFECTED:

- search results
- trendig bar

# # anime screen

# # # Features

- video player
- controls
  - next button + previous button
  - auto next
  - refresh button
  - play in mpv button
- episodes bar
- servers bar

NOTE:
  the affected:
    anime screen model, view, controller
