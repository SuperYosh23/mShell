# mShell Oh-My-Zsh Theme
# Based on mShell's sleek, minimal prompt styling
# Features: dim directory, green arrow, Unicode icons

# Colors
MSHELL_DIR_COLOR="%F{240}"      # Dim gray (color 240)
MSHELL_ARROW_COLOR="%F{82}"     # Green (color 82)
MSHELL_RESET="%f"               # Reset color

# Font Awesome Icons (requires Font Awesome font in terminal)
# Using $'...' syntax to properly escape unicode characters
MSHELL_HOME_ICON=$'\uf015'      # fa-home
MSHELL_FOLDER_ICON=$'\uf07b'    # fa-folder
MSHELL_ARROW="❯"                  # Unicode arrow (keep this as Unicode)

# Function to get abbreviated directory display
mshell_dir_display() {
    local current_dir="$PWD"
    local home_dir="$HOME"
    local display_dir
    local max_len=23

    # Check if in home directory
    if [[ "$current_dir" == "$home_dir" ]]; then
        display_dir="$MSHELL_HOME_ICON"
    elif [[ "$current_dir" == "$home_dir"/* ]]; then
        # In subdirectory of home
        local rel_path="${current_dir#$home_dir/}"
        display_dir="$MSHELL_HOME_ICON /$rel_path"
    else
        # Outside home
        display_dir="$MSHELL_FOLDER_ICON $current_dir"
    fi

    # Truncate if too long (>23 chars)
    if [[ ${#display_dir} -gt $max_len ]]; then
        local dir_name="${current_dir##*/}"
        if [[ "$current_dir" == "$home_dir" ]]; then
            display_dir="$MSHELL_HOME_ICON"
        else
            display_dir="$MSHELL_FOLDER_ICON $dir_name"
        fi
    fi

    echo "$display_dir"
}

# Build the prompt
PROMPT='${MSHELL_DIR_COLOR}$(mshell_dir_display)${MSHELL_RESET} ${MSHELL_ARROW_COLOR}${MSHELL_ARROW}${MSHELL_RESET} '

# Right prompt (optional - can show git info, time, etc.)
# RPROMPT=''

# Set prompt substitution so functions get evaluated
setopt promptsubst
