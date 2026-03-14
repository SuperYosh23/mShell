#!/usr/bin/env python3
"""
mShell - A modern Linux shell with Unicode icons and styling
Supports built-in commands, external commands, pipes, and redirections
"""

import os
import sys
import subprocess
import shlex
import signal
import readline
import atexit
import json
import curses
import glob
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

# ANSI color codes for styling
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    
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
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

# Global color references - using default theme only
class DefaultColors:
    # Simplified color mappings using default theme
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
            'terminal_bg': None,
            'terminal_text': None
        }
        return color_map.get(color_name, '')

# Global color instance
default_colors = DefaultColors()

# Font Awesome icons with Unicode fallbacks
class Icons:
    def __init__(self, use_unicode=False):
        self.use_unicode = use_unicode
        
        # Font Awesome icon mappings (using Unicode equivalents as fallbacks)
        self.icons = {
            'SHELL': {
                'font_awesome': '\uf120',  # fa-terminal
                'unicode': '❯'
            },
            'FOLDER': {
                'font_awesome': '\uf07b',  # fa-folder
                'unicode': '🗀'
            },
            'HOME': {
                'font_awesome': '\uf015',  # fa-home
                'unicode': '⏏'
            },
            'FILE': {
                'font_awesome': '\uf15b',  # fa-file
                'unicode': '🗎'
            },
            'GEAR': {
                'font_awesome': '\uf013',  # fa-cog
                'unicode': '⚙'
            },
            'ROCKET': {
                'font_awesome': '\uf135',  # fa-rocket
                'unicode': '🚀'
            },
            'SPARKLE': {
                'font_awesome': '\uf0e7',  # fa-bolt (closest to sparkle)
                'unicode': '✨'
            },
            'ARROW_RIGHT': {
                'font_awesome': '\uf061',  # fa-arrow-right
                'unicode': '❯'
            },
            'ARROW_LEFT': {
                'font_awesome': '\uf060',  # fa-arrow-left
                'unicode': '❮'
            },
            'CHECK': {
                'font_awesome': '\uf00c',  # fa-check
                'unicode': '✓'
            },
            'CROSS': {
                'font_awesome': '\uf00d',  # fa-times
                'unicode': '✗'
            },
            'WARNING': {
                'font_awesome': '\uf071',  # fa-exclamation-triangle
                'unicode': '⚠'
            },
            'INFO': {
                'font_awesome': '\uf05a',  # fa-info-circle
                'unicode': 'ℹ'
            },
            'LIGHTNING': {
                'font_awesome': '\uf0e7',  # fa-bolt
                'unicode': '⚡'
            },
            'FIRE': {
                'font_awesome': '\uf06d',  # fa-fire
                'unicode': '🔥'
            },
            'STAR': {
                'font_awesome': '\uf005',  # fa-star
                'unicode': '★'
            },
            'CROWN': {
                'font_awesome': '\uf521',  # fa-crown
                'unicode': '♛'
            },
            'DOT': {
                'font_awesome': '\uf111',  # fa-circle
                'unicode': '•'
            },
            'SEPARATOR': {
                'font_awesome': '\uf7d9',  # fa-grip-lines-vertical
                'unicode': '│'
            },
            'BRANCH': {
                'font_awesome': '\uf126',  # fa-code-branch
                'unicode': '├─'
            },
            'END': {
                'font_awesome': '\uf0da',  # fa-caret-right (closest to tree end)
                'unicode': '└─'
            }
        }
    
    def __getattr__(self, name):
        """Get icon attribute, choosing Font Awesome or Unicode based on config"""
        if name in self.icons:
            icon_set = self.icons[name]
            
            # Always use Unicode for these specific icons
            always_unicode = ['SHELL', 'ARROW_RIGHT', 'ARROW_LEFT', 'DOT', 'CROWN', 
                          'SEPARATOR', 'BRANCH', 'END', 'CHECK', 'CROSS']
            
            if name in always_unicode:
                return icon_set['unicode']
            elif self.use_unicode:
                return icon_set['unicode']
            else:
                return icon_set['font_awesome']
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

# Global icon instance - will be updated with config
icons = Icons(use_unicode=False)

class mShell:
    def __init__(self, startup_command=None):
        self.running = True
        self.current_dir = os.getcwd()
        self.history_file = Path.home() / ".mshell_history"
        self.config_file = Path.home() / ".mshell_config.json"
        self.startup_command = startup_command
        self.full_path_prompt = False  # Default: show abbreviated path
        self.use_unicode_icons = False  # Default: use Font Awesome icons
        
        # ASCII art for "bred" command
        self.bred_ascii_art = """⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⢿⠿⠷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠛⠉⠀⠀⠀⠐⠒⠒⠒⠺⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⡰⠃⠄⠀⠀⠀⠀⠆⠀⠀⢢⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⣐⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠈⠂⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠉⢉⡄⢱⣿⣿⣿⣾⣿⣿⣷⣦⡀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⢸⡇⠸⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⠂⣀⡜⠁⠀⠂⠀⢹⣯⠉⠉⠛⠻⠏⠀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⠀⢻⡇⢸⣿⣷⣆⣸⣿⣷⣶⣶⣿⠀⠼⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⢸⡇⣸⣿⠟⣀⣠⣈⣿⣻⣿⡿⠀⢰⣭⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠶⠾⠁⣿⣥⣅⣉⣛⣛⠛⣩⠗⢁⣀⣼⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡃⠠⡌⠻⣿⣿⣷⣿⣿⡏⢰⣿⣿⣿⣟⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⣦⣍⣀⣈⣉⣡⣊⡅⠈⢴⣶⣭⣛⣿⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢃⡄⡄⢿⣿⣿⣿⣿⣿⡿⢁⡇⠀⠙⠿⣿⣷⡽⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡿⠿⠘⢰⣿⡇⠓⠚⠻⢿⣿⠿⢋⣴⣿⠁⠀⠀⠀⠀⠀⠈⠑⠛⠛⠻⠿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⡿⢟⡫⠉⠉⠀⠀⠀⣿⣿⣼⣿⣯⠁⠘⢁⣴⢿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⠋⠁⠒⠉⠀⠀⠀⠀⠀⢳⣿⠿⡟⣿⣿⠘⢰⣷⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⡇⣿⣿⠠⠤⢬⣉⣉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣿⠃⠘⠒⠲⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡷⢠⢉⣈⡓⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣿⣿⣿⣿⣿⣿⣿⣿⣿
⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣺⣿⡇⠤⢤⣭⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⣿
⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⡇⠒⠶⠖⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣿⣿⣿⣿
⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⢉⣉⣉⠁⠀⠀⠀⠀⠐⠒⠶⣶⣶⣶⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣿⣿
⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢼⣿⠠⠤⣌⠀⠀⠀⠀⠀⠰⠉⣴⣶⣶⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿
⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠺⣸⠐⠲⠄⠀⠀⠀⠀⠀⠀⠈⣿⠛⠛⣛⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿
⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣹⣿⠈⠒⠂⠀⠀⠀⠀⠀⠀⠀⠘⠚⠛⠻⠿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢼⣽⠀⢉⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⠏⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸
⠄⠀⠀⠀⣠⣤⠶⠿⢿⣻⣄⠀⠀⡼⣿⠀⠤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸
⣾⠀⠀⠜⠁⢼⣶⣯⣤⣤⡴⠀⠀⢹⡟⠐⠒⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⣀⣀⣀⣀⣴⣿⣿
⣿⡄⠀⠀⠀⠀⢿⣦⣤⠤⠒⠀⠀⣸⡏⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣶⣄⡀⠀⠘⠒⠖⠒⠀⠀⠀⢹⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣦⣄⣀⡀⠀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⣤⣼⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀⣿⣿⢿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿"""
        
        # Set shell environment variable so external programs recognize mShell
        os.environ['SHELL'] = 'mshell'
        
        # Set terminal info for neofetch and other tools
        # Get the actual terminal being used
        actual_terminal = os.environ.get('TERM', 'unknown')
        if 'TERM_PROGRAM' in os.environ:
            # macOS Terminal.app, iTerm2, etc.
            actual_terminal = os.environ['TERM_PROGRAM']
        elif 'COLORTERM' in os.environ:
            # Modern terminals with color support
            actual_terminal = os.environ['COLORTERM']
        elif 'TERMINAL_EMULATOR' in os.environ:
            # Some Linux terminals set this
            actual_terminal = os.environ['TERMINAL_EMULATOR']
        
        # Set environment variables that neofetch and other tools check
        os.environ['TERM_PROGRAM'] = actual_terminal
        os.environ['TERM'] = os.environ.get('TERM', 'xterm-256color')  # Ensure TERM is set
        
        # Override shell detection to show mShell instead of python3
        os.environ['_'] = 'mshell'  # Some tools check this for the current shell
        # Clear other shell versions by removing them if they exist
        if 'BASH_VERSION' in os.environ:
            del os.environ['BASH_VERSION']
        if 'ZSH_VERSION' in os.environ:
            del os.environ['ZSH_VERSION']
        
        # Handle restart directory if coming from a restart
        if 'MSHELL_RESTART_DIR' in os.environ:
            restart_dir = os.environ['MSHELL_RESTART_DIR']
            try:
                os.chdir(restart_dir)
                del os.environ['MSHELL_RESTART_DIR']
            except (FileNotFoundError, PermissionError):
                pass  # If we can't change to the restart dir, just continue
        
        # Restore terminal info if coming from a restart
        if 'MSHELL_TERM_PROGRAM' in os.environ:
            os.environ['TERM_PROGRAM'] = os.environ['MSHELL_TERM_PROGRAM']
            del os.environ['MSHELL_TERM_PROGRAM']
        if 'MSHELL_TERM' in os.environ:
            os.environ['TERM'] = os.environ['MSHELL_TERM']
            del os.environ['MSHELL_TERM']
        
        # Load configuration
        self.load_config()
        
        # Initialize the sleek prompt
        self.update_prompt()
        
        # Setup readline for history and tab completion
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
                    
                # Apply startup command from config if not already set
                if not self.startup_command and config.get('startup_command'):
                    self.startup_command = config['startup_command']
                
                # Apply full path prompt setting
                self.full_path_prompt = config.get('full_path_prompt', False)
                
                # Apply unicode icons setting
                self.use_unicode_icons = config.get('use_unicode_icons', False)
                
                # Update global icons instance with new setting
                global icons
                icons = Icons(use_unicode=self.use_unicode_icons)
                    
                # Clean theme-related data from config if it exists
                if 'theme' in config or 'custom_themes' in config:
                    clean_config = {}
                    for key, value in config.items():
                        if key not in ['theme', 'custom_themes']:
                            clean_config[key] = value
                    
                    # Save cleaned config back to file
                    try:
                        with open(self.config_file, 'w') as f:
                            json.dump(clean_config, f, indent=2)
                    except:
                        pass  # Silently fail if we can't clean the file
                    
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            # Config file doesn't exist or is invalid, use defaults
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
        
        # Setup tab completion with bash-style behavior
        readline.set_completer(self.tab_completer)
        readline.parse_and_bind('tab: complete')
        readline.set_completer_delims(' \t\n;')
        
        # Configure readline for bash-style completion
        readline.parse_and_bind('set completion-ignore-case on')
        readline.parse_and_bind('set show-all-if-ambiguous on')
        readline.parse_and_bind('set visible-stats on')
    
    def tab_completer(self, text, state):
        """Tab completion function that behaves like bash"""
        try:
            # Get the current line being typed
            line = readline.get_line_buffer()
            cursor_pos = readline.get_endidx()
            
            # Split the line into words to understand context
            words = line[:cursor_pos].split()
            
            # Get all possible matches
            if not words or (len(words) == 1 and not line.endswith(' ')):
                matches = self.get_command_matches(text)
            else:
                matches = self.get_file_matches(text)
            
            if not matches:
                return None
            
            # Return matches in sequence for readline to handle
            if state < len(matches):
                return matches[state]
            else:
                return None
                
        except Exception as e:
            print(f"Completion error: {e}")
            return None
    
    def get_command_matches(self, text):
        """Get all command matches for the given text"""
        # Built-in commands
        builtin_commands = ['cd', 'pwd', 'echo', 'help', 'clear', 'exit', 'bred']
        
        # Combine built-in commands with system commands in PATH
        all_commands = builtin_commands.copy()
        
        # Get common system commands (limited to avoid performance issues)
        try:
            path_dirs = os.environ.get('PATH', '').split(':')
            common_commands = set()
            
            for path_dir in path_dirs:
                if os.path.isdir(path_dir):
                    try:
                        files = os.listdir(path_dir)[:50]  # Limit to first 50 files per dir
                        for file in files:
                            if file.startswith(text) and os.access(os.path.join(path_dir, file), os.X_OK):
                                common_commands.add(file)
                    except (PermissionError, OSError):
                        continue
            
            all_commands.extend(sorted(common_commands))
        except Exception:
            pass
        
        # Filter commands that start with the text
        matches = [cmd for cmd in all_commands if cmd.startswith(text)]
        return matches
    
    def get_file_matches(self, text):
        """Get all file/directory matches for the given text"""
        try:
            # Handle tilde expansion
            original_text = text
            if text.startswith('~'):
                text = os.path.expanduser(text)
            
            # Get directory and filename parts
            if '/' in text:
                directory = os.path.dirname(text) or '.'
                filename = os.path.basename(text)
            else:
                directory = '.'
                filename = text
            
            # Expand directory if it's a relative path
            if not os.path.isabs(directory):
                directory = os.path.abspath(directory)
            
            # Get all files/directories in the directory
            try:
                files = os.listdir(directory)
            except (PermissionError, OSError):
                return []
            
            # Filter matches that start with the filename
            matches = []
            for file in files:
                if file.startswith(filename):
                    full_path = os.path.join(directory, file)
                    
                    # Add trailing slash for directories
                    if os.path.isdir(full_path):
                        file += '/'
                    
                    # Reconstruct the relative path
                    if '/' in original_text:
                        # Preserve the original directory structure
                        rel_path = os.path.join(os.path.dirname(original_text), file)
                    else:
                        rel_path = file
                    
                    matches.append(rel_path)
            
            # Sort matches (directories first, then files)
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
        """Handle Ctrl+C with sleek styling"""
        print(f"\n{default_colors.get_color('warning')}{icons.WARNING} Interrupted{Colors.RESET}")
        print(f"{default_colors.get_color('description')}Use 'exit' to quit{Colors.RESET}")
        print(self.prompt, end='', flush=True)
    
    def handle_sigtstp(self, signum, frame):
        """Handle Ctrl+Z with sleek styling"""
        print(f"\n{default_colors.get_color('warning')}{icons.WARNING} Suspended{Colors.RESET}")
        print(f"{default_colors.get_color('description')}Use 'exit' to quit{Colors.RESET}")
        print(self.prompt, end='', flush=True)
    
    def update_prompt(self):
        """Update the shell prompt with current directory and sleek styling"""
        self.current_dir = os.getcwd()
        home_dir = str(Path.home())
        
        # Create path display based on full_path_prompt setting
        if self.full_path_prompt:
            # Show raw system path without icons or abbreviations
            display_dir = self.current_dir
        else:
            # Show abbreviated path with icons (original behavior)
            if self.current_dir.startswith(home_dir):
                relative_path = self.current_dir[len(home_dir):].lstrip('/')
                if relative_path:
                    display_dir = f"{icons.HOME} /{relative_path}"
                else:
                    display_dir = icons.HOME
            else:
                display_dir = f"{icons.FOLDER} {self.current_dir}"
            
            # If path is too long (>23 chars), show just current directory name
            if len(display_dir) > 23:
                current_dir_name = os.path.basename(self.current_dir)
                if self.current_dir == home_dir:
                    display_dir = icons.HOME  # Keep home icon for home directory
                else:
                    display_dir = f"{icons.FOLDER} {current_dir_name}"
        
        # Create a sleek, minimal prompt with default colors
        self.prompt = f"{default_colors.get_color('prompt_dir')}{display_dir}{Colors.RESET} "
        self.prompt += f"{default_colors.get_color('prompt_arrow')}{icons.ARROW_RIGHT}{Colors.RESET} "
    
    def show_bred_art(self):
        """Display the ASCII art when 'bred' command is run"""
        print(f"\n{Colors.BRIGHT_CYAN}{self.bred_ascii_art}{Colors.RESET}")
        print(f"{Colors.BRIGHT_YELLOW}never gonna give you up, never gonna let you down{Colors.RESET}\n")
    
    def parse_command(self, command_line):
        """Parse command line into tokens, handling pipes and redirections"""
        if not command_line.strip():
            return None
        
        # Split by pipes first
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
        
        # Parse each command for redirections
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
        elif cmd == 'bred':
            return self.builtin_bred()
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
        """Launch configuration interface selector"""
        try:
            interface_selector = ConfigInterfaceSelector(self.config_file, self)
            interface_selector.run()
            # Reload config after interface closes
            self.load_config()
            # Update prompt to apply full_path_prompt setting
            self.update_prompt()
        except Exception as e:
            print(f"{Colors.RED}{icons.CROSS} Config selector error: {e}{Colors.RESET}")
        return True
    
    def builtin_help(self):
        """Help built-in command with sleek styling"""
        print(f"\n{default_colors.get_color('title')}{icons.CROWN} mShell{Colors.RESET}")
        print(f"{default_colors.get_color('separator')}{'─' * 40}{Colors.RESET}\n")
        
        print(f"{default_colors.get_color('help_title')}Commands:{Colors.RESET}")
        commands = [
            ("cd [dir]", "Change directory"),
            ("pwd", "Print working directory"),
            ("echo [args]", "Print arguments"),
            ("clear", "Clear screen"),
            ("help", "Show this help"),
            ("exit", "Exit shell")
        ]
        
        for cmd, desc in commands:
            print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}{cmd:<15}{Colors.RESET} {default_colors.get_color('description')}{desc}{Colors.RESET}")
        
        print(f"\n{default_colors.get_color('help_title')}External Commands:{Colors.RESET}")
        external = [
            ("mshell config", "Open configuration interface selector"),
            ("mshell config --file", "Open config file in nano editor"),
            ("mshell restart", "Restart mShell"),
        ]
        
        for cmd, desc in external:
            print(f"  {default_colors.get_color('help_external')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}{cmd:<35}{Colors.RESET} {default_colors.get_color('description')}{desc}{Colors.RESET}")
        
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
    
    def builtin_bred(self):
        """Display ASCII art built-in command"""
        self.show_bred_art()
        return True
    
    def execute_external_command(self, cmd_info):
        """Execute external command with subprocess"""
        command = cmd_info['command']
        
        if not command:
            return True
        
        # Special handling for 'mshell config' command
        if len(command) >= 2 and command[0] == 'mshell' and command[1] == 'config':
            # Handle 'mshell config --file' to open config in nano
            if len(command) >= 3 and command[2] == '--file':
                try:
                    subprocess.run(['nano', str(self.config_file)], check=True)
                except FileNotFoundError:
                    print(f"{Colors.RED}{icons.CROSS} nano: command not found. Please install nano or use a different editor{Colors.RESET}")
                except subprocess.CalledProcessError as e:
                    print(f"{Colors.RED}{icons.CROSS} Failed to open config file: {e}{Colors.RESET}")
                except Exception as e:
                    print(f"{Colors.RED}{icons.CROSS} Error opening config file: {e}{Colors.RESET}")
                return True
            else:
                # Original config interface selector
                try:
                    interface_selector = ConfigInterfaceSelector(self.config_file, self)
                    interface_selector.run()
                    # Reload config after interface closes
                    self.load_config()
                except Exception as e:
                    print(f"{Colors.RED}{icons.CROSS} Config selector error: {e}{Colors.RESET}")
                return True
        
        # Special handling for 'mshell' command (already in shell)
        if len(command) == 1 and command[0] == 'mshell':
            print(f"{default_colors.get_color('info')}{icons.INFO} You are already in mShell, silly!{Colors.RESET}")
            print(f"{default_colors.get_color('description')}To restart mShell, run \"mshell restart\"{Colors.RESET}")
            return True
        
        # Special handling for 'mshell restart' command
        if len(command) == 2 and command[0] == 'mshell' and command[1] == 'restart':
            print(f"{default_colors.get_color('info')}{icons.LIGHTNING} Restarting mShell...{Colors.RESET}")
            # Save current working directory to pass to new instance
            os.environ['MSHELL_RESTART_DIR'] = os.getcwd()
            # Save terminal and shell info for restart
            os.environ['MSHELL_TERM_PROGRAM'] = os.environ.get('TERM_PROGRAM', 'unknown')
            os.environ['MSHELL_TERM'] = os.environ.get('TERM', 'xterm-256color')
            # Restart by replacing current process with new mShell instance
            try:
                # Get the path to the current script
                script_path = sys.argv[0] if sys.argv else 'mshell.py'
                # Get any original startup command
                startup_cmd = self.startup_command or os.environ.get('MSHELL_STARTUP')
                
                # Build restart command
                restart_args = [sys.executable, script_path]
                if startup_cmd:
                    restart_args.extend(['--startup', startup_cmd])
                
                # Replace current process
                os.execv(sys.executable, restart_args)
            except Exception as e:
                print(f"{Colors.RED}{icons.CROSS} Failed to restart: {e}{Colors.RESET}")
            return True
        
        
        try:
            # Setup stdin/stdout/stderr based on redirections
            stdin = None
            stdout = None
            stderr = None
            
            if cmd_info['input']:
                stdin = open(cmd_info['input'], 'r')
            
            if cmd_info['output']:
                mode = 'a' if cmd_info['append'] else 'w'
                stdout = open(cmd_info['output'], mode)
            
            # Execute the command
            process = subprocess.Popen(
                command,
                stdin=stdin,
                stdout=stdout or sys.stdout,
                stderr=stderr or sys.stderr,
                cwd=os.getcwd(),
                env=os.environ  # Ensure child processes inherit mShell environment
            )
            
            # Wait for completion
            process.wait()
            
            # Close file descriptors if we opened them
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
            # Single command, no piping needed
            cmd_info = commands[0]
            if not self.execute_builtin(cmd_info):
                self.execute_external_command(cmd_info)
            return
        
        # Multiple commands, create pipeline
        processes = []
        
        try:
            for i, cmd_info in enumerate(commands):
                command = cmd_info['command']
                
                if i == 0:
                    # First command
                    stdin = None
                    if cmd_info['input']:
                        stdin = open(cmd_info['input'], 'r')
                else:
                    # Middle commands - pipe from previous
                    stdin = processes[i-1].stdout
                
                if i == len(commands) - 1:
                    # Last command
                    stdout = None
                    if cmd_info['output']:
                        mode = 'a' if cmd_info['append'] else 'w'
                        stdout = open(cmd_info['output'], mode)
                else:
                    # Middle commands - pipe to next
                    stdout = subprocess.PIPE
                
                if self.execute_builtin(cmd_info):
                    # Built-in command executed, handle differently
                    if i > 0 and processes[i-1].stdout:
                        processes[i-1].stdout.close()
                    continue
                
                process = subprocess.Popen(
                    command,
                    stdin=stdin,
                    stdout=stdout,
                    stderr=sys.stderr,
                    cwd=os.getcwd(),
                    env=os.environ  # Ensure child processes inherit mShell environment
                )
                
                processes.append(process)
                
                # Close stdin if we opened it
                if isinstance(stdin, file):
                    stdin.close()
                
                # Close stdout of previous process in pipeline
                if i > 0 and processes[i-1].stdout:
                    processes[i-1].stdout.close()
            
            # Wait for all processes to complete
            for process in processes:
                process.wait()
                
        except Exception as e:
            print(f"{default_colors.get_color('error')}{icons.CROSS} Pipeline error: {e}{Colors.RESET}")
    
    def execute_startup_command(self):
        """Execute the startup command and display its output"""
        if not self.startup_command:
            return
        
        try:
            # Parse the startup command
            commands = self.parse_command(self.startup_command)
            if commands:
                # Execute the command without the "Running startup command" message
                self.execute_pipeline(commands)
                print()  # Add spacing after command output
        except Exception as e:
            print(f"{default_colors.get_color('error')}{icons.CROSS} Startup command error: {e}{Colors.RESET}\n")
    
    def run(self):
        """Main shell loop with sleek startup"""
        # Clear screen for clean start
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Execute startup command if configured
        self.execute_startup_command()
        
        # Show prompt if no startup command was run
        if not self.startup_command:
            print(f"{default_colors.get_color('title')}{icons.SHELL} mShell{Colors.RESET}")
            print(f"{default_colors.get_color('description')}A sleek Python shell{Colors.RESET}\n")
        
        while self.running:
            try:
                command_line = input(self.prompt)
                
                # Skip empty lines
                if not command_line.strip():
                    continue
                
                # Parse and execute command
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

    def manage_config(self, action=None, key=None, value=None):
        """Manage configuration from command line"""
        config_file = Path.home() / ".mshell_config.json"
        
        try:
            # Load existing config
            config = {}
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
            
            if action == 'show':
                print(f"{Colors.BOLD}mShell Configuration:{Colors.RESET}")
                print(f"Config file: {config_file}")
                
                if config:
                    print(f"\n{Colors.YELLOW}Current settings:{Colors.RESET}")
                    for k, v in config.items():
                        print(f"  {Colors.GREEN}{k}:{Colors.RESET} {v}")
                else:
                    print(f"{Colors.DIM}No configuration set{Colors.RESET}")
                    
            elif action == 'set' and key and value:
                config[key] = value
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                print(f"{Colors.GREEN}{icons.CHECK} Set {key} = {value}{Colors.RESET}")
                
            elif action == 'unset' and key:
                if key in config:
                    del config[key]
                    with open(config_file, 'w') as f:
                        json.dump(config, f, indent=2)
                    print(f"{Colors.GREEN}{icons.CHECK} Unset {key}{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}{icons.WARNING} {key} not found in config{Colors.RESET}")
                    
            else:
                print(f"{Colors.DIM}Usage:{Colors.RESET}")
                print(f"  {Colors.WHITE}mshell --config show{Colors.RESET}                              - Show current config")
                print(f"  {Colors.WHITE}mshell --config set <key> <value>{Colors.RESET}           - Set a config value")
                print(f"  {Colors.WHITE}mshell --config unset <key>{Colors.RESET}                  - Remove a config value")
                print(f"\n{Colors.DIM}Example:{Colors.RESET}")
                print(f"  {Colors.WHITE}mshell --config set startup_command 'neofetch'{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}{icons.CROSS} Config error: {e}{Colors.RESET}")

class ConfigTUI:
    def __init__(self, config_file, mshell_instance=None):
        self.config_file = config_file
        self.mshell = mshell_instance  # Reference to mShell for theme loading
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
        except:
            self.config = {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except:
            return False
    
    def save_config_with_data(self, config_data):
        """Save specific configuration data to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            return True
        except:
            return False
    
    def run(self):
        """Run the TUI configuration interface"""
        try:
            # Set locale to avoid Unicode issues
            import locale
            locale.setlocale(locale.LC_ALL, 'C')
            curses.wrapper(self.main_loop)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            # Fallback to CLI configuration if TUI fails
            print(f"TUI failed: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            print("Falling back to command-line configuration...")
            self.fallback_cli_config()
    
    def main_loop(self, stdscr):
        """Main TUI loop"""
        # Initialize curses
        curses.curs_set(0)  # Hide cursor
        stdscr.timeout(100)  # Non-blocking input
        
        # Colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)
        
        current_selection = 0
        menu_items = [
            ("startup_command", "Command to run when shell starts"),
            ("full_path_prompt", "Always show full path in prompt"),
            ("use_unicode_icons", "Use Unicode icons instead of Font Awesome"),
        ]
        
        # Use ASCII alternatives for icons in TUI
        arrow = ">"
        current_marker = "*"
        
        while True:
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            
            # Title
            title = "mShell Configuration"
            title_x = (w - len(title)) // 2
            # Only display title if it fits within window width
            if title_x >= 0 and len(title) <= w:
                stdscr.addstr(2, title_x, title, curses.color_pair(1) | curses.A_BOLD)
                stdscr.addstr(3, title_x, "-" * len(title), curses.color_pair(1))
            
            # Menu items
            start_y = 8
            for i, (key, description) in enumerate(menu_items):
                y = start_y + i * 3
                
                # Check if we have enough vertical space
                if y + 1 >= h:
                    break
                
                # Highlight current selection
                if i == current_selection:
                    stdscr.addstr(y, 4, arrow, curses.color_pair(2))
                    stdscr.addstr(y, 6, f"{key}:", curses.color_pair(4) | curses.A_BOLD)
                else:
                    stdscr.addstr(y, 6, f"{key}:", curses.color_pair(1))
                
                # Show current value
                value = self.config.get(key, "(not set)")
                if isinstance(value, bool):
                    # Handle boolean values
                    display_value = "ON" if value else "OFF"
                else:
                    # Handle string values
                    display_value = str(value)
                    if len(display_value) > 40:
                        display_value = display_value[:37] + "..."
                
                # Check if value fits within window width
                if 8 + len(display_value) <= w:
                    stdscr.addstr(y + 1, 8, display_value, curses.color_pair(3))
                    # Check if description fits
                    desc_text = f" - {description}"
                    if 8 + len(display_value) + len(desc_text) <= w:
                        stdscr.addstr(y + 1, 8 + len(display_value), desc_text, curses.A_DIM)
            
            # Instructions
            instructions = [
                "Up/Down: Navigate",
                "Enter: Edit",
                "d: Delete",
                "s: Save",
                "q: Quit"
            ]
            
            # Only show instructions if we have enough vertical space
            if h > 6:
                inst_y = h - 4
                inst_x = 4
                for instruction in instructions:
                    # Check if instruction fits within window width
                    if inst_x + len(instruction) <= w:
                        stdscr.addstr(inst_y, inst_x, instruction, curses.color_pair(1))
                        inst_x += len(instruction) + 4
                    else:
                        break  # Stop if we run out of horizontal space
            
            # Handle input
            key = stdscr.getch()
            
            if key == curses.KEY_UP and current_selection > 0:
                current_selection -= 1
            elif key == curses.KEY_DOWN and current_selection < len(menu_items) - 1:
                current_selection += 1
            elif key == ord('q') or key == ord('Q'):
                break
            elif key == ord('s') or key == ord('S'):
                self.save_and_exit(stdscr)
                break
            elif key == ord('d') or key == ord('D'):
                self.delete_option(stdscr, menu_items[current_selection][0])
            elif key == curses.KEY_ENTER or key in [10, 13]:
                self.edit_option(stdscr, menu_items[current_selection][0])
            
            stdscr.refresh()
    
    def fallback_cli_config(self):
        """Fallback CLI configuration when TUI fails"""
        print("\nmShell Configuration (CLI mode)")
        print("=" * 30)
        
        while True:
            print("\nCurrent configuration:")
            # Only show non-theme configuration
            for key, value in self.config.items():
                if key not in ['theme', 'custom_themes']:
                    print(f"  {key}: {value}")
            
            print("\nOptions:")
            print("  1. Set startup command")
            print("  2. Toggle full path prompt")
            print("  3. Toggle Unicode icons")
            print("  4. Save and exit")
            print("  5. Exit without saving")
            
            try:
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == '1':
                    startup_cmd = input("Enter startup command: ").strip()
                    if startup_cmd:
                        self.config['startup_command'] = startup_cmd
                        print("Startup command updated.")
                    else:
                        # Remove startup command if empty
                        if 'startup_command' in self.config:
                            del self.config['startup_command']
                        print("Startup command cleared.")
                elif choice == '2':
                    current_value = self.config.get('full_path_prompt', False)
                    new_value = not current_value
                    self.config['full_path_prompt'] = new_value
                    print(f"Full path prompt: {'ON' if new_value else 'OFF'}")
                elif choice == '3':
                    current_value = self.config.get('use_unicode_icons', False)
                    new_value = not current_value
                    self.config['use_unicode_icons'] = new_value
                    print(f"Unicode icons: {'ON' if new_value else 'OFF'}")
                elif choice == '4':
                    # Clean config by removing theme-related data
                    clean_config = {}
                    for key, value in self.config.items():
                        if key not in ['theme', 'custom_themes']:
                            clean_config[key] = value
                    
                    if self.save_config_with_data(clean_config):
                        print("Configuration saved successfully.")
                        # Update self.config to reflect cleaned state
                        self.config = clean_config
                    else:
                        print("Failed to save configuration.")
                    break
                elif choice == '5':
                    print("Exiting without saving.")
                    break
                else:
                    print("Invalid choice.")
                    
            except (EOFError, KeyboardInterrupt):
                print("\nExiting configuration.")
                break
    
    def edit_option(self, stdscr, key):
        """Edit a configuration option"""
        if key in ['full_path_prompt', 'use_unicode_icons']:
            # Handle boolean options
            current_value = self.config.get(key, False)
            new_value = not current_value
            self.config[key] = new_value
            
            # Show feedback
            h, w = stdscr.getmaxyx()
            if key == 'full_path_prompt':
                status_text = f"Full path prompt: {'ON' if new_value else 'OFF'}"
            else:
                status_text = f"Unicode icons: {'ON' if new_value else 'OFF'}"
            stdscr.addstr(h // 2, (w - len(status_text)) // 2, status_text, curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()
            curses.napms(1500)  # Show for 1.5 seconds
        else:
            # Handle text option (startup_command)
            curses.curs_set(1)  # Show cursor
            
            # Create edit window
            h, w = stdscr.getmaxyx()
            edit_win = curses.newwin(5, w - 10, h // 2 - 2, 5)
            edit_win.box()
            edit_win.addstr(1, 2, f"Edit {key}:", curses.color_pair(1) | curses.A_BOLD)
            
            current_value = self.config.get(key, "")
            edit_win.addstr(2, 2, "Value: " + " " * (w - 20), curses.color_pair(3))
            edit_win.addstr(2, 9, current_value, curses.color_pair(3))
            
            edit_win.refresh()
            
            # Enable input
            curses.echo()
            edit_win.move(2, 9 + len(current_value))
            
            input_str = edit_win.getstr(2, 9, w - 30).decode('utf-8')
            
            curses.noecho()
            curses.curs_set(0)  # Hide cursor
            
            if input_str:
                self.config[key] = input_str
    
    def delete_option(self, stdscr, key):
        """Delete a configuration option"""
        if key in self.config:
            del self.config[key]
    
    def save_and_exit(self, stdscr):
        """Save configuration and show confirmation"""
        if self.save_config():
            h, w = stdscr.getmaxyx()
            stdscr.addstr(h // 2, (w - 20) // 2, "Configuration saved!", curses.color_pair(2) | curses.A_BOLD)
            stdscr.refresh()
            curses.napms(1500)

class ConfigInterfaceSelector:
    """Interface selector for configuration options"""
    
    def __init__(self, config_file, mshell_instance=None):
        self.config_file = config_file
        self.mshell = mshell_instance
        
    def run(self):
        """Run the interface selection menu"""
        print(f"\n{default_colors.get_color('title')}{icons.GEAR} mShell Configuration{Colors.RESET}")
        print(f"{default_colors.get_color('separator')}{'─' * 40}{Colors.RESET}\n")
        
        print(f"{default_colors.get_color('help_title')}Choose configuration interface:{Colors.RESET}")
        print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}1{Colors.RESET} - {default_colors.get_color('description')}TUI Interface (Terminal UI){Colors.RESET}")
        print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}2{Colors.RESET} - {default_colors.get_color('description')}CLI Interface (Command Line){Colors.RESET}")
        print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}3{Colors.RESET} - {default_colors.get_color('description')}GUI Interface (Graphical){Colors.RESET}")
        print(f"  {default_colors.get_color('help_command')}{icons.DOT}{Colors.RESET} {default_colors.get_color('command')}q{Colors.RESET} - {default_colors.get_color('description')}Quit{Colors.RESET}")
        print()
        
        while True:
            try:
                choice = input(f"{default_colors.get_color('info')}{icons.ARROW_RIGHT}{Colors.RESET} ").strip().lower()
                
                if choice == '1':
                    self.launch_tui()
                    break
                elif choice == '2':
                    self.launch_cli()
                    break
                elif choice == '3':
                    self.launch_gui()
                    break
                elif choice in ['q', 'quit', 'exit']:
                    print(f"{default_colors.get_color('info')}{icons.INFO} Cancelled{Colors.RESET}")
                    break
                else:
                    print(f"{default_colors.get_color('error')}{icons.CROSS} Invalid choice. Please enter 1, 2, 3, or q{Colors.RESET}")
                    
            except (EOFError, KeyboardInterrupt):
                print(f"\n{default_colors.get_color('info')}{icons.INFO} Cancelled{Colors.RESET}")
                break
    
    def launch_tui(self):
        """Launch TUI configuration interface"""
        try:
            config_tui = ConfigTUI(self.config_file, self.mshell)
            config_tui.run()
        except Exception as e:
            print(f"{Colors.RED}{icons.CROSS} TUI error: {e}{Colors.RESET}")
            print("Falling back to CLI interface...")
            self.launch_cli()
    
    def launch_cli(self):
        """Launch CLI configuration interface"""
        try:
            config_tui = ConfigTUI(self.config_file, self.mshell)
            config_tui.fallback_cli_config()
        except Exception as e:
            print(f"{Colors.RED}{icons.CROSS} CLI error: {e}{Colors.RESET}")
    
    def launch_gui(self):
        """Launch GUI configuration interface"""
        try:
            config_gui = ConfigGUI(self.config_file, self.mshell)
            config_gui.run()
        except Exception as e:
            print(f"{Colors.RED}{icons.CROSS} GUI error: {e}{Colors.RESET}")
            print("Falling back to TUI interface...")
            self.launch_tui()

class ConfigGUI:
    """Graphical configuration interface using tkinter"""
    
    def __init__(self, config_file, mshell_instance=None):
        self.config_file = config_file
        self.mshell = mshell_instance
        self.config = {}
        self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {}
        except:
            self.config = {}
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except:
            return False
    
    def run(self):
        """Run the GUI configuration interface"""
        self.root = tk.Tk()
        self.root.title("mShell Configuration")
        self.root.geometry("400x200")
        self.root.resizable(True, True)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="mShell Configuration", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuration options
        row = 1
        
        # Startup command
        ttk.Label(main_frame, text="Startup Command:").grid(row=row, column=0, sticky=tk.W, pady=10)
        self.startup_var = tk.StringVar(value=self.config.get('startup_command', ''))
        startup_entry = ttk.Entry(main_frame, textvariable=self.startup_var, width=40)
        startup_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Full path prompt option
        self.full_path_var = tk.BooleanVar(value=self.config.get('full_path_prompt', False))
        full_path_check = ttk.Checkbutton(main_frame, text="Always show full path in prompt", 
                                         variable=self.full_path_var)
        full_path_check.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Unicode icons option
        self.unicode_icons_var = tk.BooleanVar(value=self.config.get('use_unicode_icons', False))
        unicode_icons_check = ttk.Checkbutton(main_frame, text="Use Unicode icons instead of Font Awesome", 
                                             variable=self.unicode_icons_var)
        unicode_icons_check.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=5)
        row += 1
        
        # Description
        desc_label = ttk.Label(main_frame, text="Configure shell startup and prompt behavior", 
                              font=('TkDefaultFont', 9), foreground='gray')
        desc_label.grid(row=row, column=0, columnspan=2, pady=(10, 20))
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_and_close).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.root.destroy).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=row+1, column=0, columnspan=2, pady=(5, 0))
        
        # Start the GUI
        self.root.mainloop()
    
    def save_and_close(self):
        """Save configuration and close window"""
        # Update config
        self.config['startup_command'] = self.startup_var.get()
        self.config['full_path_prompt'] = self.full_path_var.get()
        self.config['use_unicode_icons'] = self.unicode_icons_var.get()
        
        # Save and close
        if self.save_config():
            self.status_var.set("Configuration saved successfully!")
            self.root.destroy()
        else:
            messagebox.showerror("Error", "Failed to save configuration!")

def main():
    """Main entry point"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='mShell - A sleek Python shell')
    parser.add_argument('--startup', '-s', 
                       help='Command to run when shell starts',
                       default=None)
    parser.add_argument('--config', '-c',
                       help='Manage configuration',
                       nargs='+',
                       metavar='ACTION [KEY] [VALUE]')
    
    args = parser.parse_args()
    
    # Handle config management
    if args.config:
        shell = mShell()  # Create shell instance for config management
        action = args.config[0] if args.config else None
        key = args.config[1] if len(args.config) > 1 else None
        value = ' '.join(args.config[2:]) if len(args.config) > 2 else None
        shell.manage_config(action, key, value)
        return
    
    # Handle 'mshell config' command when called from within shell
    if len(sys.argv) == 3 and sys.argv[1] == 'mshell' and sys.argv[2] == 'config':
        shell = mShell()  # Create shell instance for config TUI
        try:
            config_tui = ConfigTUI(shell.config_file)
            config_tui.run()
        except Exception as e:
            print(f"{Colors.RED}{icons.CROSS} Config TUI error: {e}{Colors.RESET}")
        return
    
    # Check for environment variable as fallback
    startup_command = args.startup or os.environ.get('MSHELL_STARTUP')
    
    shell = mShell(startup_command=startup_command)
    shell.run()

if __name__ == "__main__":
    main()
