"""
Development utilities untuk EcoReport Application
"""

import os
import sys
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask
import subprocess

class LiveReloadHandler(FileSystemEventHandler):
    """Handle file changes for live reload"""
    
    def __init__(self, app):
        self.app = app
        self.last_reload = 0
        
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only reload for Python and template files
        if not (event.src_path.endswith('.py') or event.src_path.endswith('.html')):
            return
        
        # Debounce reloads
        current_time = time.time()
        if current_time - self.last_reload < 1:
            return
        
        self.last_reload = current_time
        print(f"🔄 File changed: {event.src_path}")
        print("♻️  Restarting application...")

class DevelopmentServer:
    """Enhanced development server dengan live reload"""
    
    def __init__(self, app):
        self.app = app
        self.observer = None
        
    def start_file_watcher(self):
        """Start file watcher for live reload"""
        event_handler = LiveReloadHandler(self.app)
        self.observer = Observer()
        
        # Watch directories
        directories_to_watch = ['.', 'templates', 'static']
        for directory in directories_to_watch:
            if os.path.exists(directory):
                self.observer.schedule(event_handler, directory, recursive=True)
        
        self.observer.start()
        print("📁 File watcher started")
        
    def stop_file_watcher(self):
        """Stop file watcher"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            print("📁 File watcher stopped")
    
    def run(self, host='127.0.0.1', port=5000, debug=True):
        """Run development server dengan enhancements"""
        if debug:
            self.start_file_watcher()
        
        try:
            print(f"🚀 Starting development server on http://{host}:{port}")
            print("💡 Tips:")
            print("   • Ctrl+C untuk stop server")
            print("   • File changes akan auto-reload")
            print("   • Gunakan /api/docs untuk API documentation")
            
            self.app.run(host=host, port=port, debug=debug)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping development server...")
        finally:
            if debug:
                self.stop_file_watcher()

def run_linting():
    """Run code linting"""
    print("🔍 Running code linting...")
    
    commands = [
        ['flake8', '.', '--max-line-length=88', '--exclude=venv'],
        ['black', '--check', '--diff', '.']
    ]
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ {' '.join(cmd)} failed:")
                print(result.stdout)
                print(result.stderr)
            else:
                print(f"✅ {' '.join(cmd)} passed")
        except FileNotFoundError:
            print(f"⚠️  {cmd[0]} not installed, skipping...")

def format_code():
    """Format code dengan black"""
    print("✨ Formatting code...")
    
    try:
        subprocess.run(['black', '.'], check=True)
        print("✅ Code formatted successfully")
    except FileNotFoundError:
        print("⚠️  black not installed")
    except subprocess.CalledProcessError:
        print("❌ Code formatting failed")

def check_security():
    """Basic security checks"""
    print("🔒 Running security checks...")
    
    checks = []
    
    # Check .env file
    if os.path.exists('.env'):
        checks.append("✅ .env file exists")
        
        with open('.env', 'r') as f:
            content = f.read()
            
        if 'your-very-secret-key-here' in content:
            checks.append("❌ Default secret key detected!")
        else:
            checks.append("✅ Secret key is customized")
            
        if 'DEBUG=True' in content:
            checks.append("⚠️  Debug mode enabled")
        else:
            checks.append("✅ Debug mode configuration OK")
    else:
        checks.append("❌ .env file missing!")
    
    # Check .gitignore
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            gitignore_content = f.read()
            
        if '.env' in gitignore_content:
            checks.append("✅ .env is in .gitignore")
        else:
            checks.append("❌ .env not in .gitignore!")
    else:
        checks.append("⚠️  .gitignore file missing")
    
    for check in checks:
        print(f"   {check}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'lint':
            run_linting()
        elif command == 'format':
            format_code()
        elif command == 'security':
            check_security()
        else:
            print("Available commands: lint, format, security")
    else:
        print("Usage: python development.py [lint|format|security]")