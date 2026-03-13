#!/bin/bash

# mShell Auto-Install Script
# Clones mShell from GitHub and sets up PATH shortcut

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Icons
CHECK='✓'
CROSS='✗'
GEAR='⚙'
ROCKET='🚀'

# Configuration
REPO_URL="https://github.com/SuperYosh23/mShell.git"
INSTALL_DIR="$HOME/mshell"
SCRIPT_NAME="mshell"

echo -e "${CYAN}${ROCKET} mShell Auto-Install Script${NC}"
echo "=================================="

# Function to print status messages
print_status() {
    echo -e "${BLUE}${GEAR} $1${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install python3 first."
    exit 1
fi

print_status "Checking for existing installation..."

# Remove existing installation if it exists
if [ -d "$INSTALL_DIR" ]; then
    print_warning "Existing mShell installation found at $INSTALL_DIR"
    read -p "Do you want to remove it and reinstall? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Removing existing installation..."
        rm -rf "$INSTALL_DIR"
        print_success "Existing installation removed"
    else
        print_error "Installation cancelled."
        exit 0
    fi
fi

print_status "Cloning mShell from GitHub..."

# Clone the repository
if git clone "$REPO_URL" "$INSTALL_DIR"; then
    print_success "Repository cloned successfully"
else
    print_error "Failed to clone repository"
    exit 1
fi

print_status "Setting up executable permissions..."

# Make mshell.py executable
chmod +x "$INSTALL_DIR/mshell.py"
print_success "Made mshell.py executable"

print_status "Creating PATH shortcut..."

# Determine shell configuration file
SHELL_RC=""
if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

# Create the mshell wrapper script
WRAPPER_SCRIPT="$HOME/.local/bin/mshell"
mkdir -p "$(dirname "$WRAPPER_SCRIPT")"

cat > "$WRAPPER_SCRIPT" << EOF
#!/bin/bash
python3 "$INSTALL_DIR/mshell.py" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"

print_success "Created wrapper script at $WRAPPER_SCRIPT"

# Add ~/.local/bin to PATH if not already present
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    print_status "Adding ~/.local/bin to PATH in $SHELL_RC..."
    
    echo '' >> "$SHELL_RC"
    echo '# mShell PATH configuration' >> "$SHELL_RC"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    
    print_success "Added ~/.local/bin to PATH"
else
    print_success "~/.local/bin is already in PATH"
fi

# Test the installation
print_status "Testing installation..."

if command -v mshell &> /dev/null; then
    print_success "mShell command is available!"
else
    print_warning "mShell command not found in current session"
    print_status "You may need to restart your terminal or run:"
    echo "  source $SHELL_RC"
fi

# Display installation summary
echo ""
echo -e "${GREEN}${CHECK} Installation Complete!${NC}"
echo "=================================="
echo -e "${CYAN}Installation Details:${NC}"
echo "  • Repository: $REPO_URL"
echo "  • Install directory: $INSTALL_DIR"
echo "  • Wrapper script: $WRAPPER_SCRIPT"
echo "  • Shell config: $SHELL_RC"
echo ""
echo -e "${CYAN}Usage:${NC}"
echo "  • Start mShell: ${YELLOW}mshell${NC}"
echo "  • With startup command: ${YELLOW}mshell --startup \"neofetch\"${NC}"
echo "  • Configure: ${YELLOW}mshell --config show${NC}"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "  • If 'mshell' command is not found, restart your terminal or run:"
echo "    ${BLUE}source $SHELL_RC${NC}"
echo "  • To uninstall, simply remove: $INSTALL_DIR"
echo ""
echo -e "${GREEN}Enjoy using mShell!${NC}"
