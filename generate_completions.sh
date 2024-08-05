#!/usr/bin/env bash
APP_DIR="$(
  cd -- "$(dirname "$0")" >/dev/null 2>&1
  pwd -P
)"

# fish shell completions
_FASTANIME_COMPLETE=fish_source fastanime >"$APP_DIR/completions/fastanime.fish"

# zsh completions
_FASTANIME_COMPLETE=zsh_source fastanime >"$APP_DIR/completions/fastanime.zsh"

# bash completions
_FASTANIME_COMPLETE=bash_source fastanime >"$APP_DIR/completions/fastanime.bash"
