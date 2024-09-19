import click


@click.command(
    help="Helper command to get shell completions",
    epilog="""
\b
\b\bExamples:
    # try to detect your shell and print completions
    fastanime completions
\b
    # print fish completions
    fastanime completions --fish
\b
    # print bash completions
    fastanime completions --bash
\b
    # print zsh completions
    fastanime completions --zsh
""",
)
@click.option("--fish", is_flag=True, help="print fish completions")
@click.option("--zsh", is_flag=True, help="print zsh completions")
@click.option("--bash", is_flag=True, help="print bash completions")
def completions(fish, zsh, bash):
    if not fish or not zsh or not bash:
        import os

        shell_env = os.environ.get("SHELL", "")
        if "fish" in shell_env:
            current_shell = "fish"
        elif "zsh" in shell_env:
            current_shell = "zsh"
        elif "bash" in shell_env:
            current_shell = "bash"
        else:
            current_shell = None
    else:
        current_shell = None
    if fish or current_shell == "fish" and not zsh and not bash:
        print(
            """
function _fastanime_completion;
    set -l response (env _FASTANIME_COMPLETE=fish_complete COMP_WORDS=(commandline -cp) COMP_CWORD=(commandline -t) fastanime);

    for completion in $response;
        set -l metadata (string split "," $completion);

        if test $metadata[1] = "dir";
            __fish_complete_directories $metadata[2];
        else if test $metadata[1] = "file";
            __fish_complete_path $metadata[2];
        else if test $metadata[1] = "plain";
            echo $metadata[2];
        end;
    end;
end;

complete --no-files --command fastanime --arguments "(_fastanime_completion)";
        """
        )
    elif zsh or current_shell == "zsh" and not bash:
        print(
            """
#compdef fastanime

_fastanime_completion() {
    local -a completions
    local -a completions_with_descriptions
    local -a response
    (( ! $+commands[fastanime] )) && return 1

    response=("${(@f)$(env COMP_WORDS="${words[*]}" COMP_CWORD=$((CURRENT-1)) _FASTANIME_COMPLETE=zsh_complete fastanime)}")

    for type key descr in ${response}; do
        if [[ "$type" == "plain" ]]; then
            if [[ "$descr" == "_" ]]; then
                completions+=("$key")
            else
                completions_with_descriptions+=("$key":"$descr")
            fi
        elif [[ "$type" == "dir" ]]; then
            _path_files -/
        elif [[ "$type" == "file" ]]; then
            _path_files -f
        fi
    done

    if [ -n "$completions_with_descriptions" ]; then
        _describe -V unsorted completions_with_descriptions -U
    fi

    if [ -n "$completions" ]; then
        compadd -U -V unsorted -a completions
    fi
}

if [[ $zsh_eval_context[-1] == loadautofunc ]]; then
    # autoload from fpath, call function directly
    _fastanime_completion "$@"
else
    # eval/source/. command, register function for later
    compdef _fastanime_completion fastanime
fi
        """
        )
    elif bash or current_shell == "bash":
        print(
            """
_fastanime_completion() {
    local IFS=$'\n'
    local response

    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _FASTANIME_COMPLETE=bash_complete $1)

    for completion in $response; do
        IFS=',' read type value <<< "$completion"

        if [[ $type == 'dir' ]]; then
            COMPREPLY=()
            compopt -o dirnames
        elif [[ $type == 'file' ]]; then
            COMPREPLY=()
            compopt -o default
        elif [[ $type == 'plain' ]]; then
            COMPREPLY+=($value)
        fi
    done

    return 0
}

_fastanime_completion_setup() {
    complete -o nosort -F _fastanime_completion fastanime
}

_fastanime_completion_setup;
        """
        )
    else:
        print("Could not detect shell")
