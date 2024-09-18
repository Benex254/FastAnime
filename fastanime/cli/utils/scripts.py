fzf_preview = r"""
#
# Adapted from the preview script in the fzf repo
#
# Dependencies:
# - https://github.com/hpjansson/chafa
# - https://iterm2.com/utilities/imgcat
#
fzf-preview() {
	file=${1/#\~\//$HOME/}
	dim=${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}
	if [[ $dim = x ]]; then
		dim=$(stty size </dev/tty | awk '{print $2 "x" $1}')
	elif ! [[ $KITTY_WINDOW_ID ]] && ((FZF_PREVIEW_TOP + FZF_PREVIEW_LINES == $(stty size </dev/tty | awk '{print $1}'))); then
		# Avoid scrolling issue when the Sixel image touches the bottom of the screen
		# * https://github.com/junegunn/fzf/issues/2544
		dim=${FZF_PREVIEW_COLUMNS}x$((FZF_PREVIEW_LINES - 1))
	fi

	# 1. Use kitty icat on kitty terminal
	if [[ $KITTY_WINDOW_ID ]]; then
		# 1. 'memory' is the fastest option but if you want the image to be scrollable,
		#    you have to use 'stream'.
		#
		# 2. The last line of the output is the ANSI reset code without newline.
		#    This confuses fzf and makes it render scroll offset indicator.
		#    So we remove the last line and append the reset code to its previous line.
		kitty icat --clear --transfer-mode=memory --unicode-placeholder --stdin=no --place="$dim@0x0" "$file" | sed '$d' | sed $'$s/$/\e[m/'

    # 2. Use chafa with Sixel output
	elif command -v chafa >/dev/null; then
        case "$(uname -a)" in
            # termux does not support sixel graphics
            # and produces weird output
            *ndroid*) chafa -s "$dim" "$file";;
            *) chafa -f sixel -s "$dim" "$file";;
        esac
		# Add a new line character so that fzf can display multiple images in the preview window
		echo

    # 3. If chafa is not found but imgcat is available, use it on iTerm2
	elif command -v imgcat >/dev/null; then
		# NOTE: We should use https://iterm2.com/utilities/it2check to check if the
		# user is running iTerm2. But for the sake of simplicity, we just assume
		# that's the case here.
		imgcat -W "${dim%%x*}" -H "${dim##*x}" "$file"

    # 4. Cannot find any suitable method to preview the image
	else
        echo install chafa or imgcat or install kitty terminal so you can enjoy image previews
	fi
}
"""
