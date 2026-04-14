# mShell Full Path Oh-My-Zsh Theme
# Replicates mShell's "full_path_prompt" setting - shows raw system path
# No icons, no abbreviation, just the full path

# Colors
MSHELL_DIR_COLOR="%F{240}"      # Dim gray (color 240)
MSHELL_ARROW_COLOR="%F{82}"     # Green (color 82)
MSHELL_RESET="%f"               # Reset color

# Unicode arrow only (no directory icons)
MSHELL_ARROW="❯"

# Build the prompt with full path (absolute path, no ~ abbreviation, no icons)
# %/ = full working directory path, %~ = path with ~ for home
PROMPT='${MSHELL_DIR_COLOR}%/${MSHELL_RESET} ${MSHELL_ARROW_COLOR}${MSHELL_ARROW}${MSHELL_RESET} '

# Right prompt (optional)
# RPROMPT=''

# Set prompt substitution so functions get evaluated
setopt promptsubst
