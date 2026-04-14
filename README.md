
<h3 style="text-align:center;">IMPORTANT: mShell IS VERY BUGGY AND UNSTABLE.</p>
<h3 style="text-align:center;"> If you want the same look, it is recommended to use the <a href="https://ohmyz.sh/">Oh-My-Zsh</a> themes included in this repo thet almost perfectly replicate the look of mShell, without the bugs and instability.</p>

<h4 style="text-align:center;">The <a href="https://github.com/kovidgoyal/kitty">kitty</a> terminal emulator is reccomended for both the Oh-My-Zsh themes and the original version of mShell.</p>

<br><br><br>




<div align="center">
  <img src="https://github.com/SuperYosh23/mShell/blob/main/Untitled%20drawing(10).png?raw=true" alt="Centered image">
</div>


<h3 style="text-align:center;">mShell is a beautifully styled, fully functional Linux shell implemented in Python that features modern Unicode icons, colorful output, and an attractive interface. It supports common shell features including built-in commands, external command execution, pipes, and I/O redirection.</p>

## Features

### Core Functionality
- **Interactive shell** with beautiful colored prompt showing current directory
- **Built-in commands**: `cd`, `pwd`, `echo`, `help`, `clear`, `exit`
- **External command execution** using subprocess
- **Command history** with arrow key navigation
- **Signal handling** for Ctrl+C and Ctrl+Z

### Visual Features 
- **Modern Unicode icons** throughout the interface (❯ 📁 🏠 ⚙ ✨)
- **Colorful terminal output** with ANSI color codes
- **Styled prompt** with directory display and path abbreviations
- **Beautiful startup screen** with welcome message
- **Enhanced error messages** with visual indicators
- **Professional help display** with organized sections

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
python3 mshell.py --config set startup_command "neofetch"  # Save to config file
```

## Installation

### Manual Installation
1. **Make the script executable:**
```bash
chmod +x mshell.py
```

2. **Copy mShell to system directory:**
```bash
mkdir -p ~/.local/bin
cp mshell.py ~/.local/bin/mshell
chmod +x ~/.local/bin/mshell
```

3. **Add to PATH:**
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, or ~/.profile)
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

4. **Verify installation:**
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
- `exit` - Exit the shell

### External Commands
- `mshell config` - Open configuration interface selector (within mShell)

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
- `full_path_prompt` - Always show full path in prompt (true/false)

### Priority Order
Configuration values are loaded in this priority order:
1. Command line argument (`--startup`)
2. Environment variable (`MSHELL_STARTUP`)
3. Configuration file (`~/.mshell_config.json`)

## Configuration Interfaces

mShell provides multiple configuration interfaces to suit different preferences:

### TUI Interface (Terminal UI)
A curses-based terminal interface with keyboard navigation:
- Up/Down arrows to navigate options
- Enter to edit values
- d to delete options
- s to save and exit
- q to quit

### CLI Interface (Command Line)
A simple command-line interface for quick configuration changes.

### GUI Interface (Graphical)
A tkinter-based graphical interface for desktop environments.

### Accessing Configuration
```bash
# From within mShell
mshell config

# From command line
python3 mshell.py --config show
python3 mshell.py --config set startup_command "neofetch"
python3 mshell.py --config set full_path_prompt true
```

## Implementation Details

### Architecture
- **MShell class**: Main shell controller
- **Command parsing**: Handles pipes, redirections, and quoting
- **Process management**: Uses subprocess for external commands
- **Signal handling**: Graceful handling of interrupts
- **Configuration system**: JSON-based configuration with multiple interfaces

### Key Components
1. **Command Parser**: Parses complex command lines with pipes and redirections
2. **Built-in Handler**: Executes shell built-in commands
3. **External Executor**: Runs external programs via subprocess
4. **Pipeline Manager**: Handles command pipelines with proper I/O redirection
5. **Configuration Manager**: TUI, CLI, and GUI interfaces for settings management

### File Structure
```
mshell.py          # Main shell implementation
README.md          # This documentation
```

## Requirements

- Python 3.6+
- Linux/Unix-like operating system
- Standard Python libraries: `os`, `sys`, `subprocess`, `shlex`, `signal`, `readline`, `pathlib`, `json`, `curses`, `tkinter`

## Security Considerations

This shell is designed for educational purposes and development environments. While it implements proper command parsing and signal handling, it should not be used in production security-sensitive environments without additional hardening.

## Contributing

Feel free to extend the shell with additional features:
- More built-in commands
- Job control and background processes
- Environment variable management
- Enhanced configuration options
- Custom prompt formatting

## DISCLAIMER

This is project is almost entirely AI genarated, including the majority of this readme.
