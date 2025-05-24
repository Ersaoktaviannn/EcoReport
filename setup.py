#!/usr/bin/env python3
"""
EcoReport Application Setup Script
Automated setup untuk development environment
"""

import os
import sys
import subprocess
import secrets
import platform
from pathlib import Path

def print_step(message):
    """Print step dengan formatting"""
    print(f"\n🔧 {message}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def check_python_version():
    """Check Python version"""
    print_step("Checking Python version...")
    
    if sys.version_info < (3, 8):
        print_error("Python 3.8 atau lebih baru diperlukan!")
        print(f"Versi saat ini: {sys.version}")
        sys.exit(1)
    
    print_success(f"Python {sys.version.split()[0]} - OK")

def check_pip():
    """Check if pip is available"""
    print_step("Checking pip...")
    
    try:
        subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                      check=True, capture_output=True)
        print_success("pip - OK")
    except subprocess.CalledProcessError:
        print_error("pip tidak ditemukan!")
        sys.exit(1)

def create_virtual_environment():
    """Create virtual environment"""
    print_step("Creating virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_warning("Virtual environment sudah ada")
        return
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print_success("Virtual environment dibuat")
    except subprocess.CalledProcessError as e:
        print_error(f"Gagal membuat virtual environment: {e}")
        sys.exit(1)

def get_activation_command():
    """Get virtual environment activation command"""
    system = platform.system().lower()
    
    if system == "windows":
        return "venv\\Scripts\\activate"
    else:
        return "source venv/bin/activate"

def install_dependencies():
    """Install Python dependencies"""
    print_step("Installing dependencies...")
    
    # Determine Python executable in venv
    system = platform.system().lower()
    if system == "windows":
        python_exe = "venv\\Scripts\\python.exe"
        pip_exe = "venv\\Scripts\\pip.exe"
    else:
        python_exe = "venv/bin/python"
        pip_exe = "venv/bin/pip"
    
    try:
        # Upgrade pip first
        subprocess.run([pip_exe, 'install', '--upgrade', 'pip'], check=True)
        
        # Install requirements
        subprocess.run([pip_exe, 'install', '-r', 'requirements.txt'], check=True)
        print_success("Dependencies installed")
    except subprocess.CalledProcessError as e:
        print_error(f"Gagal install dependencies: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file from template"""
    print_step("Creating environment file...")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print_warning(".env file sudah ada")
        return
    
    if not env_example.exists():
        print_error(".env.example tidak ditemukan!")
        return
    
    # Generate secret key
    secret_key = secrets.token_urlsafe(32)
    jwt_secret = secrets.token_urlsafe(32)
    
    # Read template and replace values
    with open(env_example, 'r') as f:
        content = f.read()
    
    content = content.replace('your-very-secret-key-here-change-this-in-production', secret_key)
    content = content.replace('your-jwt-secret-key-here', jwt_secret)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print_success(".env file dibuat dengan secret keys yang aman")

def create_directories():
    """Create necessary directories"""
    print_step("Creating directories...")
    
    directories = [
        'static/uploads',
        'static/css',
        'static/js',
        'static/images',
        'static/icons',
        'logs',
        'backups'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Create .gitkeep files
    for directory in ['static/uploads', 'logs', 'backups']:
        gitkeep = Path(directory) / '.gitkeep'
        gitkeep.touch()
    
    print_success("Directories created")

def initialize_database():
    """Initialize database with sample data"""
    print_step("Initializing database...")
    
    system = platform.system().lower()
    if system == "windows":
        python_exe = "venv\\Scripts\\python.exe"
    else:
        python_exe = "venv/bin/python"
    
    try:
        subprocess.run([python_exe, 'db_utils.py', 'init'], check=True)
        print_success("Database initialized with sample data")
    except subprocess.CalledProcessError as e:
        print_warning(f"Database initialization failed: {e}")
        print("You can run it manually later with: python db_utils.py init")

def run_tests():
    """Run basic tests"""
    print_step("Running basic tests...")
    
    system = platform.system().lower()
    if system == "windows":
        python_exe = "venv\\Scripts\\python.exe"
    else:
        python_exe = "venv/bin/python"
    
    try:
        subprocess.run([python_exe, '-m', 'pytest', 'test_app.py', '-v'], 
                      check=True, capture_output=True)
        print_success("All tests passed")
    except subprocess.CalledProcessError:
        print_warning("Some tests failed, but setup continues")
    except FileNotFoundError:
        print_warning("pytest not found, skipping tests")

def print_final_instructions():
    """Print final setup instructions"""
    activation_cmd = get_activation_command()
    
    print("\n" + "="*60)
    print("🎉 SETUP BERHASIL SELESAI!")
    print("="*60)
    
    print(f"""
📋 Langkah selanjutnya:

1. Aktivasi virtual environment:
   {activation_cmd}

2. Jalankan aplikasi:
   python app.py

3. Buka browser ke:
   http://localhost:5000

4. Login sebagai admin:
   Username: admin
   Password: admin123

📁 File penting:
   • .env          - Environment variables (JANGAN commit ke git!)
   • app.py        - Main application
   • requirements.txt - Python dependencies
   • templates/    - HTML templates
   • static/       - CSS, JS, images

🔧 Commands berguna:
   • python db_utils.py backup  - Backup database
   • python db_utils.py reset   - Reset database
   • python run_tests.py        - Run all tests
   • python deploy.py docker    - Deploy dengan Docker

💡 Tips:
   • Edit .env untuk konfigurasi custom
   • Lihat README.md untuk dokumentasi lengkap
   • Gunakan db_utils.py untuk manajemen database
    """)
    
    print("="*60)

def main():
    """Main setup function"""
    print("🌿 EcoReport Application Setup")
    print("="*40)
    
    # Run setup steps
    check_python_version()
    check_pip()
    create_virtual_environment()
    install_dependencies()
    create_env_file()
    create_directories()
    initialize_database()
    run_tests()
    
    print_final_instructions()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Setup dibatalkan oleh user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        sys.exit(1)