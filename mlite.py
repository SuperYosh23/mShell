#!/usr/bin/env python3
"""
mLite - A lightweight version of mShell with simplified features
CLI configuration only, no TUI/GUI interfaces, no easter eggs, Unicode-only icons
"""

import os
import sys
import subprocess
import shlex
import signal
import readline
import atexit
import json
from pathlib import Path

# ANSI color codes for styling
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

# Global color references
class DefaultColors:
    def get_color(self, color_name):
        """Get default color by name"""
        color_map = {
            'prompt_dir': Colors.DIM,
            'prompt_arrow': Colors.GREEN,
            'error': Colors.RED,
            'warning': Colors.YELLOW,
            'info': Colors.CYAN,
            'success': Colors.GREEN,
            'title': Colors.BOLD + Colors.CYAN,
            'command': Colors.WHITE,
            'description': Colors.DIM,
            'separator': Colors.DIM,
            'help_title': Colors.BOLD,
            'help_command': Colors.GREEN,
            'help_external': Colors.BLUE,
            'help_feature': Colors.BLUE,
        }
        return color_map.get(color_name, '')

# Global color instance
default_colors = DefaultColors()

# Unicode-only icons (no Font Awesome)
class Icons:
    def __init__(self):
        pass
    
    def __getattr__(self, name):
        """Get icon attribute, using Unicode only"""
        unicode_icons = {
            'SHELL': '❯',
            'FOLDER': '🗀',
            'HOME': '⏏',
            'FILE': '🗎',
            'GEAR': '⚙',
            'ROCKET': '🚀',
            'SPARKLE': '✨',
            'ARROW_RIGHT': '❯',
            'ARROW_LEFT': '❮',
            'CHECK': '✓',
            'CROSS': '✗',
            'WARNING': '⚠',
            'INFO': 'ℹ',
            'LIGHTNING': '⚡',
            'FIRE': '🔥',
            'STAR': '★',
            'CROWN': '♛',
            'DOT': '•',
            'SEPARATOR': '│',
            'BRANCH': '├─',
            'END': '└─'
        }
        
        if name in unicode_icons:
            return unicode_icons[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# Global icon instance
icons = Icons()

class mLite:
    def __init__(self, startup_command=None):
        self.running = True
        self.current_dir = os.getcwd()
        self.history_file = Path.home() / ".mlite_history"
        self.config_file = Path.home() / ".mlite_config.json"
        self.startup_command = startup_command
        self.full_path_prompt = False
        
        # Set shell environment variable
        os.environ['SHELL'] = 'mlite'
        
        # Set terminal info
        actual_terminal = os.environ.get('TERM', 'unknown')
        if 'TERM_PROGRAM' in os.environ:
            actual_terminal = os.environ['TERM_PROGRAM']
        elif 'COLORTERM' in os.environ:
            actual_terminal = os.environ['COLORTERM']
        elif 'TERMINAL_EMULATOR' in os.environ:
            actual_terminal = os.environ['TERMINAL_EMULATOR']
        
        os.environ['TERM_PROGRAM'] = actual_terminal
        os.environ['TERM'] = os.environ.get('TERM', 'xterm-256color')
        os.environ['_'] = 'mlite'
        
        # Clear other shell versions
        if 'BASH_VERSION' in os.environ:
            del os.environ['BASH_VERSION']
        if 'ZSH_VERSION' in os.environ:
            del os.environ['ZSH_VERSION']
        
        # Handle restart directory
        if 'MLITE_RESTART_DIR' in os.environ:
            restart_dir = os.environ['MLITE_RESTART_DIR']
            try:
                os.chdir(restart_dir)
                del os.environ['MLITE_RESTART_DIR']
            except (FileNotFoundError, PermissionError):
                pass
        
        # Restore terminal info if coming from a restart
        if 'MLITE_TERM_PROGRAM' in os.environ:
            os.environ['TERM_PROGRAM'] = os.environ['MLITE_TERM_PROGRAM']
            del os.environ['MLITE_TERM_PROGRAM']
        if 'MLITE_TERM' in os.environ:
            os.environ['TERM'] = os.environ['MLITE_TERM']
            del os.environ['MLITE_TERM']
        
        # Load configuration
        self.load_config()
        
        # Initialize prompt
        self.update_prompt()
        
        # Setup readline
        self.setup_readline()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_sigint)
        signal.signal(signal.SIGTSTP, self.handle_sigtstp)
    
    def load_config(self):
        """Load configuration from config file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                if not self.startup_command and config.get('startup_command'):
                    self.startup_command = config['startup_command']
                
                self.full_path_prompt = config.get('full_path_prompt', False)
                    
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            pass
    
    def save_config(self, config):
        """Save configuration to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except (PermissionError, OSError):
            print(f"{Colors.RED}{icons.CROSS} Could not save config file{Colors.RESET}")
    
    def setup_readline(self):
        """Setup readline for command history and tab completion"""
        try:
            readline.read_history_file(self.history_file)
        except FileNotFoundError:
            pass
        
        readline.set_history_length(1000)
        atexit.register(self.save_history)
        
        readline.set_completer(self.tab_completer)
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims(' \t\n;')
        
        readline.parse_and_bind('set completion-ignore-case on')
        readline.parse_and_bind('set show-all-if-ambiguous on')
        readline.parse_and_bind('set visible-stats on')
    
    def tab_completer(self, text, state):
        """Tab completion function"""
        try:
            line = readline.get_line_buffer()
            cursor_pos = readline.get_endidx()
            words = line[:cursor_pos].split()
            
            if not words or (len(words) == 1 and not line.endswith(' ')):
                matches = self.get_command_matches(text)
            else:
                matches = self.get_file_matches(text)
            
            if not matches:
                return None
            
            if state < len(matches):
                return matches[state]
            else:
                return None
                
        except Exception as e:
            print(f"Completion error: {e}")
            return None
    
    def get_command_matches(self, text):
        """Get all command matches for the given text"""
        builtin_commands = ['cd', 'pwd', 'echo', 'help', 'clear', 'exit', 'config']
        
        all_commands = builtin_commands.copy()
        
        try:
            path_dirs = os.environ.get('PATH', '').split(':')
            common_commands = set()
            
            for path_dir in path_dirs:
                if os.path.isdir(path_dir):
                    try:
                        files = os.listdir(path_dir)[:50]
                        for file in files:
                            if file.startswith(text) and os.access(os.path.join(path_dir, file), os.X_OK):
                                common_commands.add(file)
                    except (PermissionError, OSError):
                        continue
            
            all_commands.extend(sorted(common_commands))
        except Exception:
            pass
        
        matches = [cmd for cmd in all_commands if cmd.startswith(text)]
        return matches
    
    def get_file_matches(self, text):
        """Get all file/directory matches for the given text"""
        try:
            original_text = text
            if text.startswith('~'):
                text = os.path.expanduser(text)
            
            if '/' in text:
                directory = os.path.dirname(text) or '.'
                filename = os.path.basename(text)
            else:
                directory = '.'
                filename = text
            
            if not os.path.isabs(directory):
                directory = os.path.abspath(directory)
            
            try:
                files = os.listdir(directory)
            except (PermissionError, OSError):
                return []
            
            matches = []
            for file in files:
                if file.startswith(filename):
                    full_path = os.path.join(directory, file)
                    
                    if os.path.isdir(full_path):
                        file += '/'
                    
                    if '/' in original_text:
                        rel_path = os.path.join(os.path.dirname(original_text), file)
                    else:
                        rel_path = file
                    
                    matches.append(rel_path)
            
            matches.sort(key=lambda x: (not x.endswith('/'), x.lower()))
            return matches
                
        except Exception:
            return []
    
    def save_history(self):
        """Save command history to file"""
        try:
            readline.write_history_file(self.history_file)
        except:
            pass
    
    def handle_sigint(self, signum, frame):
        """Handle Ctrl+C"""
        print(f"\n{default_colors.get_color('warning')}{icons.WARNING} Interrupted{Colors.RESET}")
        print(f"{default_colors.get_color('description')}Use 'exit' to quit{Colors.RESET}")
        print(self.prompt, end='', flush=True)
    
    def handle_sigtstp(self, signum, frame):
        """Handle Ctrl+Z"""
        print(f"\n{default_colors.get_color('warning')}{icons.WARNING} Suspended{Colors.RESET}")
        print(f"{default_colors.get_color('description')}Use 'exit' to quit{Colors.RESET}")
        print(self.prompt, end='', flush=True)
    
    def update_prompt(self):
        """Update the shell prompt"""
        self.current_dir = os.getcwd()
        home_dir = str(Path.home())
        
        if self.full_path_prompt:
            display_dir = self.current_dir
        else:
            if self.current_dir.startswith(home_dir):
                relative_path = self.current_dir[len(home_dir):].lstrip('/')
                if relative_path:
                    display_dir = f"{icons.HOME} /{relative_path}"
                else:
                    display_dir = icons.HOME
            else:
                display_dir = f"{icons.FOLDER} {self.current_dir}"
            
            if len(display_dir) > 23:
                current_dir_name = os.path.basename(self.current_dir)
                if self.current_dir == home_dir:
                    display_dir = icons.HOME
                else:
                    display_dir = f"{icons.FOLDER} {current_dir_name}"
        
        self.prompt = f"{default_colors.get_color('prompt_dir')}{display_dir}{Colors.RESET} "
        self.prompt += f"{default_colors.get_color('prompt_arrow')}{icons.ARROW_RIGHT}{Colors.RESET} "
    
    def parse_command(self, command_line):
        """Parse command line into tokens, handling pipes and redirections"""
        if not command_line.strip():
            return None
        
        pipe_commands = []
        current_command = ""
        in_quotes = False
        quote_char = None
        
        for char in command_line:
            if char in ['"', "'"] and not in_quotes:
                in_quotes = True
                quote_char = char
                current_command += char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current_command += char
            elif char == '|' and not in_quotes:
                pipe_commands.append(current_command.strip())
                current_command = ""
            else:
                current_command += char
        
        if current_command.strip():
            pipe_commands.append(current_command.strip())
        
        parsed_commands = []
        for cmd in pipe_commands:
            parsed_cmd = self.parse_redirections(cmd)
            parsed_commands.append(parsed_cmd)
        
        return parsed_commands
    
    def parse_redirections(self, command):
        """Parse a single command for input/output redirections"""
        parts = shlex.split(command)
        
        cmd_info = {
            'command': [],
            'input': None,
            'output': None,
            'append': False
        }
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            if part == '<':
                if i + 1 < len(parts):
                    cmd_info['input'] = parts[i + 1]
                    i += 2
                else:
                    print(f"{Colors.RED}{icons.CROSS} Missing input file after '<'{Colors.RESET}")
                    i += 1
            elif part == '>':
                if i + 1 < len(parts):
                    cmd_info['output'] = parts[i + 1]
                    cmd_info['append'] = False
                    i += 2
                else:
                    print(f"{Colors.RED}{icons.CROSS} Missing output file after '>'{Colors.RESET}")
                    i += 1
            elif part == '>>':
                if i + 1 < len(parts):
                    cmd_info['output'] = parts[i + 1]
                    cmd_info['append'] = True
                    i += 2
                else:
                    print(f"{Colors.RED}{icons.CROSS} Missing output file after '>>'{Colors.RESET}")
                    i += 1
            else:
                cmd_info['command'].append(part)
                i += 1
        
        return cmd_info
    
    def execute_builtin(self, cmd_info):
        """Execute built-in commands"""
        command = cmd_info['command']
        
        if not command:
            return True
        
        cmd = command[0].lower()
        
        if cmd == 'exit':
            self.running = False
            return True
        elif cmd == 'cd':
            return self.builtin_cd(command[1:])
        elif cmd == 'pwd':
            return self.builtin_pwd()
        elif cmd == 'echo':
            return self.builtin_echo(command[1:])
        elif cmd == 'help':
            return self.builtin_help()
        elif cmd == 'clear':
            return self.builtin_clear()
        elif cmd == 'config':
            return self.builtin_config()
        else:
            return False
    
    def builtin_cd(self, args):
        """Change directory built-in command"""
        if not args:
            target = Path.home()
        elif len(args) == 1:
            target = args[0]
        else:
            print("cd: too many arguments")
            return True
        
        try:
            if target == '~':
                target = Path.home()
            elif target == '-':
                target = os.environ.get('OLDPWD', os.getcwd())
            
            os.chdir(target)
            os.environ['OLDPWD'] = os.getcwd()
            self.update_prompt()
            return True
        except FileNotFoundError:
            print(f"{default_colors.get_color('error')}{icons.CROSS} {target}: No such directory{Colors.RESET}")
        except NotADirectoryError:
            print(f"{default_colors.get_color('error')}{icons.CROSS} {target}: Not a directory{Colors.RESET}")
        except PermissionError:
            print(f"{default_colors.get_color('error')}{icons.CROSS} {target}: Permission denied{Colors.RESET}")
        
        return True
    
    def builtin_pwd(self):
        """Print working directory built-in command"""
        print(os.getcwd())
        return True
    
    def builtin_echo(self, args):
        """Echo built-in command"""
        if args:
            print(' '.join(args))
        else:
            print()
        return True
    
    def builtin_config(self):
        """CLI configuration interface"""
        print(f"\n{default_colors.get_color('title')}{icons.GEAR} mLite Configuration{Colors.RESET}")
        print(f"{default_colors.get_color('separator')}{'─' * 40}{Colors.RESET}\n")
        
        config_file = self.config_file
        config = {}
        
        # Load existing config
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
        except:
            config = {}
        
        while True:
            print(f"{default_colors.get_color('help_title')}Current configuration:{Colors.RESET}")
            for key, value in config.items():
                print(f"  {default_colors.get_color('command')}{key}:{Colors.RESET} {value}")
            
            if not config:
                print(f"  {default_colors.get_color('description')}No configuration set{Colors.RESET}")
            
            print(f"\n{default_colors.get_color('help_title')}Options:{Colors.RESET}")
            print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}1{Colors.RESET} - {default_colors.get_color('description')}Set startup command{Colors.RESET}")
            print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}2{Colors.RESET} - {default_colors.get_color('description')}Toggle full path prompt{Colors.RESET}")
            print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}3{Colors.RESET} - {default_colors.get_color('description')}Save and exit{Colors.RESET}")
            print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}4{Colors.RESET} - {default_colors.get_color('description')}Exit without saving{Colors.RESET}")
            
            try:
                choice = input(f"\n{default_colors.get_color('info')}{icons.ARROW_RIGHT}{Colors.RESET} ").strip()
                
                if choice == '1':
                    startup_cmd = input("Enter startup command: ").strip()
                    if startup_cmd:
                        config['startup_command'] = startup_cmd
                        print(f"{default_colors.get_color('success')}{icons.CHECK} Startup command updated{Colors.RESET}")
                    else:
                        if 'startup_command' in config:
                            del config['startup_command']
                        print(f"{default_colors.get_color('info')}{icons.INFO} Startup command cleared{Colors.RESET}")
                elif choice == '2':
                    current_value = config.get('full_path_prompt', False)
                    new_value = not current_value
                    config['full_path_prompt'] = new_value
                    self.full_path_prompt = new_value
                    self.update_prompt()
                    print(f"{default_colors.get_color('success')}{icons.CHECK} Full path prompt: {'ON' if new_value else 'OFF'}{Colors.RESET}")
                elif choice == '3':
                    try:
                        with open(config_file, 'w') as f:
                            json.dump(config, f, indent=2)
                        print(f"{default_colors.get_color('success')}{icons.CHECK} Configuration saved{Colors.RESET}")
                    except Exception as e:
                        print(f"{default_colors.get_color('error')}{icons.CROSS} Failed to save configuration: {e}{Colors.RESET}")
                    break
                elif choice == '4':
                    print(f"{default_colors.get_color('info')}{icons.INFO} Exiting without saving{Colors.RESET}")
                    break
                else:
                    print(f"{default_colors.get_color('error')}{icons.CROSS} Invalid choice{Colors.RESET}")
                    
            except (EOFError, KeyboardInterrupt):
                print(f"\n{default_colors.get_color('info')}{icons.INFO} Exiting configuration{Colors.RESET}")
                break
        
        return True
    
    def builtin_help(self):
        """Help built-in command"""
        print(f"\n{default_colors.get_color('title')}{icons.CROWN} mLite{Colors.RESET}")
        print(f"{default_colors.get_color('separator')}{'─' * 40}{Colors.RESET}\n")
        
        print(f"{default_colors.get_color('help_title')}Commands:{Colors.RESET}")
        commands = [
            ("cd [dir]", "Change directory"),
            ("pwd", "Print working directory"),
            ("echo [args]", "Print arguments"),
            ("clear", "Clear screen"),
            ("config", "Configure mLite settings"),
            ("help", "Show this help"),
            ("exit", "Exit shell")
        ]
        
        for cmd, desc in commands:
            print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}{cmd:<15}{Colors.RESET} {default_colors.get_color('description')}{desc}{Colors.RESET}")
        
        print(f"\n{default_colors.get_color('help_title')}External Commands:{Colors.RESET}")
        external = [
            ("mlite config", "Open configuration interface"),
            ("mlite restart", "Restart mLite"),
        ]
        
        for cmd, desc in external:
            print(f"  {default_colors.get_color('help_external')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}{cmd:<25}{Colors.RESET} {default_colors.get_color('description')}{desc}{Colors.RESET}")
        
        print(f"\n{default_colors.get_color('help_title')}Features:{Colors.RESET}")
        features = [
            "Command history",
            "Tab completion", 
            "Pipes: cmd1 | cmd2",
            "Redirection: > >> <"
        ]
        
        for feature in features:
            print(f"  {default_colors.get_color('help_feature')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}{feature}{Colors.RESET}")
        
        print(f"\n{default_colors.get_color('separator')}{'─' * 40}{Colors.RESET}\n")
        return True
    
    def builtin_clear(self):
        """Clear screen built-in command"""
        os.system('clear' if os.name == 'posix' else 'cls')
        return True
    
    def execute_external_command(self, cmd_info):
        """Execute external command with subprocess"""
        command = cmd_info['command']
        
        if not command:
            return True
        
        # Special handling for 'mlite config' command
        if len(command) >= 2 and command[0] == 'mlite' and command[1] == 'config':
            return self.builtin_config()
        
        # Special handling for 'mlite' command
        if len(command) == 1 and command[0] == 'mlite':
            print(f"{default_colors.get_color('info')}{icons.INFO} You are already in mLite!{Colors.RESET}")
            print(f"{default_colors.get_color('description')}To restart mLite, run \"mlite restart\"{Colors.RESET}")
            return True
        
        # Special handling for 'mlite restart' command
        if len(command) == 2 and command[0] == 'mlite' and command[1] == 'restart':
            print(f"{default_colors.get_color('info')}{icons.LIGHTNING} Restarting mLite...{Colors.RESET}")
            os.environ['MLITE_RESTART_DIR'] = os.getcwd()
            os.environ['MLITE_TERM_PROGRAM'] = os.environ.get('TERM_PROGRAM', 'unknown')
            os.environ['MLITE_TERM'] = os.environ.get('TERM', 'xterm-256color')
            
            try:
                script_path = sys.argv[0] if sys.argv else 'mlite.py'
                startup_cmd = self.startup_command or os.environ.get('MLITE_STARTUP')
                
                restart_args = [sys.executable, script_path]
                if startup_cmd:
                    restart_args.extend(['--startup', startup_cmd])
                
                os.execv(sys.executable, restart_args)
            except Exception as e:
                print(f"{Colors.RED}{icons.CROSS} Failed to restart: {e}{Colors.RESET}")
            return True
        
        try:
            stdin = None
            stdout = None
            stderr = None
            
            if cmd_info['input']:
                stdin = open(cmd_info['input'], 'r')
            
            if cmd_info['output']:
                mode = 'a' if cmd_info['append'] else 'w'
                stdout = open(cmd_info['output'], mode)
            
            process = subprocess.Popen(
                command,
                stdin=stdin,
                stdout=stdout or sys.stdout,
                stderr=stderr or sys.stderr,
                cwd=os.getcwd(),
                env=os.environ
            )
            
            process.wait()
            
            if stdin:
                stdin.close()
            if stdout:
                stdout.close()
            
            return True
            
        except FileNotFoundError:
            print(f"{default_colors.get_color('error')}{icons.CROSS} {command[0]}: command not found{Colors.RESET}")
        except PermissionError:
            print(f"{default_colors.get_color('error')}{icons.CROSS} {command[0]}: permission denied{Colors.RESET}")
        except Exception as e:
            print(f"{default_colors.get_color('error')}{icons.CROSS} {e}{Colors.RESET}")
        
        return True
    
    def execute_pipeline(self, commands):
        """Execute a pipeline of commands"""
        if not commands:
            return
        
        if len(commands) == 1:
            cmd_info = commands[0]
            if not self.execute_builtin(cmd_info):
                self.execute_external_command(cmd_info)
            return
        
        processes = []
        
        try:
            for i, cmd_info in enumerate(commands):
                command = cmd_info['command']
                
                if i == 0:
                    stdin = None
                    if cmd_info['input']:
                        stdin = open(cmd_info['input'], 'r')
                else:
                    stdin = processes[i-1].stdout
                
                if i == len(commands) - 1:
                    stdout = None
                    if cmd_info['output']:
                        mode = 'a' if cmd_info['append'] else 'w'
                        stdout = open(cmd_info['output'], mode)
                else:
                    stdout = subprocess.PIPE
                
                if self.execute_builtin(cmd_info):
                    if i > 0 and processes[i-1].stdout:
                        processes[i-1].stdout.close()
                    continue
                
                process = subprocess.Popen(
                    command,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=sys.stderr,
                    cwd=os.getcwd(),
                    env=os.environ
                )
                
                processes.append(process)
                
                if isinstance(stdin, file):
                    stdin.close()
                
                if i > 0 and processes[i-1].stdout:
                    processes[i-1].stdout.close()
            
            for process in processes:
                process.wait()
                
        except Exception as e:
            print(f"{default_colors.get_color('error')}{icons.CROSS} Pipeline error: {e}{Colors.RESET}")
    
    def execute_startup_command(self):
        """Execute the startup command"""
        if not self.startup_command:
            return
        
        try:
            commands = self.parse_command(self.startup_command)
            if commands:
                self.execute_pipeline(commands)
                print()
        except Exception as e:
            print(f"{default_colors.get_color('error')}{icons.CROSS} Startup command error: {e}{Colors.RESET}\n")
    
    def run(self):
        """Main shell loop"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        self.execute_startup_command()
        
        if not self.startup_command:
            print(f"{default_colors.get_color('title')}{icons.SHELL} mLite{Colors.RESET}")
            print(f"{default_colors.get_color('description')}A lightweight Python shell{Colors.RESET}\n")
        
        while self.running:
            try:
                command_line = input(self.prompt)
                
                if not command_line.strip():
                    continue
                
                commands = self.parse_command(command_line)
                if commands:
                    self.execute_pipeline(commands)
                    
            except EOFError:
                print(f"\n{default_colors.get_color('info')}{icons.INFO} Goodbye{Colors.RESET}")
                self.running = False
            except KeyboardInterrupt:
                print(f"\n{default_colors.get_color('warning')}{icons.WARNING} Interrupted{Colors.RESET}")
                print(f"{default_colors.get_color('description')}Use 'exit' to quit{Colors.RESET}")
            except Exception as e:
                print(f"{default_colors.get_color('error')}{icons.CROSS} {e}{Colors.RESET}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='mLite - A lightweight Python shell')
    parser.add_argument('--startup', '-s', 
                       help='Command to run when shell starts',
                       default=None)
    
    args = parser.parse_args()
    
    startup_command = args.startup or os.environ.get('MLITE_STARTUP')
    
    shell = mLite(startup_command=startup_command)
    shell.run()

if __name__ == "__main__":
    main()
