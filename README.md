# mShell - A Modern Linux Shell in Python

mShell is a beautifully styled, fully functional Linux shell implemented in Python that features modern Unicode icons, colorful output, and an attractive interface. It supports common shell features including built-in commands, external command execution, pipes, and I/O redirection.

## Features

### Core Functionality
- **Interactive shell** with beautiful colored prompt showing current directory
- **Built-in commands**: `cd`, `pwd`, `echo`, `help`, `clear`, `exit`
- **External command execution** using subprocess
- **Command history** with arrow key navigation
- **Signal handling** for Ctrl+C and Ctrl+Z

### Visual Features 🎨
- **Modern Unicode icons** throughout the interface (🐚 📁 🏠 ⚡ ✨)
- **Colorful terminal output** with ANSI color codes
- **Styled prompt** with user@hostname and directory icons
- **Beautiful startup screen** with animated welcome message
- **Enhanced error messages** with visual indicators
- **Professional help display** with organized sections
- **Theme system** with multiple color schemes (default, dark, light, cyberpunk, minimal)

### Advanced Features
- **Startup commands**: Run any command when shell starts
- **Pipes**: Chain commands with `|` (e.g., `ls -la | grep .py`)
- **Input redirection**: Read from files with `<` (e.g., `sort < data.txt`)
- **Output redirection**: Write to files with `>` (e.g., `ls > files.txt`)
- **Append redirection**: Append to files with `>>` (e.g., `echo "line" >> log.txt`)
- **Tab completion** for file and directory names
- **Persistent command history** saved to `~/.mshell_history`

## Usage

### Running the Shell
```bash
python3 mshell.py
# or
./mshell.py

# With startup command
python3 mshell.py --startup "neofetch"
python3 mshell.py -s "neofetch"
python3 mshell.py --startup "ls -la && echo 'Welcome!'"

# Using environment variable
export MSHELL_STARTUP="neofetch"
python3 mshell.py

# Configuration file (persistent settings)
mshell --config set startup_command "neofetch"  # Save to config file
```

## Installation

### Easy Installation (Recommended)
```bash
# Run the installation script
./install.sh
```

### Manual Installation
1. **Copy mShell to system directory:**
```bash
mkdir -p ~/.local/bin
cp mshell.py ~/.local/bin/mshell
chmod +x ~/.local/bin/mshell
```

2. **Add to PATH:**
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, or ~/.profile)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

3. **Verify installation:**
```bash
which mshell
# Should show: ~/.local/bin/mshell
```

### Usage After Installation
```bash
# Start mShell from anywhere
mshell

# With startup command
mshell --startup "neofetch"

# Configure settings
mshell --config set startup_command "neofetch"
```

### Built-in Commands
- `cd [directory]` - Change directory (defaults to home directory)
- `pwd` - Print current working directory
- `echo [text]` - Print text to stdout
- `help` - Display help information
- `clear` - Clear the terminal screen
- `theme` - Manage color themes
- `exit` - Exit the shell

### Examples
```bash
# Basic commands
ls -la
pwd
echo "Hello World"

# Pipes
ls -la | grep ".py"
ps aux | grep python

# Redirection
ls > files.txt
echo "Log entry" >> log.txt
sort < unsorted.txt > sorted.txt

# Combined features
cat data.txt | grep "error" | wc -l > error_count.txt
```

## Configuration

mShell supports persistent configuration through a JSON config file located at `~/.mshell_config.json`.

### Config Commands
```bash
# View current configuration
mshell --config show

# Set a configuration value
mshell --config set startup_command "neofetch"
mshell --config set startup_command "ls -la && echo 'Welcome!'"

# Remove a configuration value
mshell --config unset startup_command
```

### Configuration Options
- `startup_command` - Command to run when shell starts
- `theme` - Color theme to use (default, dark, light, cyberpunk, minimal)

### Priority Order
Configuration values are loaded in this priority order:
1. Command line argument (`--startup`)
2. Environment variable (`MSHELL_STARTUP`)
3. Configuration file (`~/.mshell_config.json`)

## Theming

mShell includes a powerful theming system that allows you to customize the appearance of the shell.

### Available Themes
- **default** - The original mShell color scheme, no terminal changes
- **dark** - Black background with bright white text, enhanced colors
- **light** - White background with black text, optimized for light terminals
- **cyberpunk** - Black background with cyan text, vibrant magenta/cyan accents
- **minimal** - No terminal changes, minimal mShell colors only

### Theme Commands
```bash
# List available themes
theme list

# Set a theme
theme set dark
theme set cyberpunk

# Show current theme
theme current

# Reset to default theme
theme reset

# Show theme help
theme
```

### Theme Configuration
You can also set themes through the configuration system:

```bash
# Set theme via config
mshell --config set theme dark

# Or use the TUI
mshell config
```

### Custom Themes
Advanced users can create custom themes by adding them to the configuration file:

```json
{
  "theme": "my_custom",
  "custom_themes": {
    "my_custom": {
      "prompt_dir": "\033[90m",
      "prompt_arrow": "\033[92m",
      "error": "\033[91m",
      "warning": "\033[93m",
      "info": "\033[96m",
      "success": "\033[92m",
      "terminal_bg": "\033[40m",
      "terminal_text": "\033[97m"
    }
  }
}
```

#### Terminal Color Options:
- `terminal_bg` - Background color (use `Colors.BG_*` constants)
- `terminal_text` - Default text color (use `Colors.*` constants)
- Set to `null`/`None` to leave unchanged

## Implementation Details

### Architecture
- **MShell class**: Main shell controller
- **Command parsing**: Handles pipes, redirections, and quoting
- **Process management**: Uses subprocess for external commands
- **Signal handling**: Graceful handling of interrupts

### Key Components
1. **Command Parser**: Parses complex command lines with pipes and redirections
2. **Built-in Handler**: Executes shell built-in commands
3. **External Executor**: Runs external programs via subprocess
4. **Pipeline Manager**: Handles command pipelines with proper I/O redirection

### File Structure
```
mshell.py          # Main shell implementation
README.md          # This documentation
```

## Requirements

- Python 3.6+
- Linux/Unix-like operating system
- Standard Python libraries: `os`, `sys`, `subprocess`, `shlex`, `signal`, `readline`, `pathlib`

## Security Considerations

This shell is designed for educational purposes and development environments. While it implements proper command parsing and signal handling, it should not be used in production security-sensitive environments without additional hardening.

## Contributing

Feel free to extend the shell with additional features:
- More built-in commands
- Job control and background processes
- Environment variable management
- Configuration file support
- Custom prompt formatting

## License

This project is open source and available under the MIT License.
