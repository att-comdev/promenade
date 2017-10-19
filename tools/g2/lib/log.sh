C_CLEAR="\e[0m"
C_ERROR="\e[38;5;160m"
C_HEADER="\e[38;5;164m"
C_HILIGHT="\e[38;5;27m"
C_MUTE="\e[38;5;238m"
C_SUCCESS="\e[38;5;46m"

function log {
    echo -e ${C_MUTE}$(date --utc)${C_CLEAR} $* 1>&2
}

if [[ "x${PROMENADE_DEBUG}" = "x1" ]]; then
    export LOG_FILE=/dev/stderr
else
    export LOG_FILE=/dev/null
fi
