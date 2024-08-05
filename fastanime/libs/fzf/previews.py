preview_anime_search = 'hght=$(($FZF_PREVIEW_COLUMNS/2 +2));\
  i=$(echo {}|sed "s/\\t.*$//g");\
  echo $i>$HOME/.cache/magic-tape/search/channels/index.txt;\
  TITLE="$(cat $HOME/.cache/magic-tape/search/channels/titles.txt|head -$i|tail +$i)";\
  if [[ "$IMAGE_SUPPORT" != "none" ]]&&[[ "$IMAGE_SUPPORT" != "chafa" ]];then ll=0;while [ $ll -le $(($hght/2 - 2)) ];do echo "";((ll++));done;fi;\
  ll=1; echo -ne "\x1b[38;5;241m"; while [ $ll -le $FZF_PREVIEW_COLUMNS ];do echo -n -e "─";((ll++));done;echo -n -e "$normal";\
  if [[ "$TITLE" == "Previous Page" ]];then draw_preview $(($hght/3)) 1 $(($FZF_PREVIEW_COLUMNS/2)) $(($FZF_PREVIEW_COLUMNS/2)) $HOME/.cache/magic-tape/png/previous.png;\
  elif [[ "$TITLE" == "Next Page" ]];then draw_preview $(($hght/3)) 1 $(($FZF_PREVIEW_COLUMNS/2)) $(($FZF_PREVIEW_COLUMNS/2)) $HOME/.cache/magic-tape/png/next.png;\
  elif [[ "$TITLE" == "Abort Selection" ]];then draw_preview $(($hght/3)) 1 $(($FZF_PREVIEW_COLUMNS/2)) $(($FZF_PREVIEW_COLUMNS/2)) $HOME/.cache/magic-tape/png/abort.png;\
  else draw_preview $(($hght/3)) 1 $(($FZF_PREVIEW_COLUMNS/2)) $(($FZF_PREVIEW_COLUMNS/2)) $HOME/.cache/magic-tape/jpg/"$(cat $HOME/.cache/magic-tape/search/channels/ids.txt|head -$i|tail +$i)".jpg;fi;\
  echo -e "\n""$Yellow""$TITLE""$normal"|fold -w $FZF_PREVIEW_COLUMNS -s;\
  ll=1; echo -ne "\x1b[38;5;241m"; while [ $ll -le $FZF_PREVIEW_COLUMNS ];do echo -n -e "─";((ll++));done;echo -n -e "$normal";\
   if [[ $TITLE != "Abort Selection" ]]&&[[ $TITLE != "Next Page" ]]&&[[ $TITLE != "Previous Page" ]];\
   then SUBS="$(cat $HOME/.cache/magic-tape/search/channels/subscribers.txt|head -$i|tail +$i)";\
  echo -e "\n"$Green"Subscribers: ""$Cyan""$SUBS""$normal";\
  ll=1; echo -ne "\x1b[38;5;241m"; while [ $ll -le $FZF_PREVIEW_COLUMNS ];do echo -n -e "─";((ll++));done;echo -n -e "$normal";\
  DESCRIPTION="$(cat $HOME/.cache/magic-tape/search/channels/descriptions.txt|head -$i|tail +$i)";\
  echo -e "\n\x1b[38;5;250m$DESCRIPTION"$normal""|fold -w $FZF_PREVIEW_COLUMNS -s; \
  fi;'
