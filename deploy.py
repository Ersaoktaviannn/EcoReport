import os
import sys
import subprocess
import shutil
from pathlib import Path

class Deployer:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / 'build'
        
    def clean_build(self):
        """Clean previous build"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir()
        print("✓ Build directory cleaned")
    
    def copy_files(self):
        """Copy necessary files for deployment"""
        files_to_copy = [
            'app.py',
            'requirements.txt',
            'Procfile',
            'runtime.txt',
            'config.py',
            'api.py',
            'db_utils.py'
        ]
        
        for file in files_to_copy:
            if (self.project_root / file).exists():
                shutil.copy2(self.project_root / file, self.build_dir / file)
                print(f"✓ Copied {file}")
        
        # Copy directories
        dirs_to_copy = ['templates', 'static']
        for dir_name in dirs_to_copy:
            src_dir = self.project_root / dir_name
            if src_dir.exists():
                shutil.copytree(src_dir, self.build_dir / dir_name)
                print(f"✓ Copied {dir_name}/")
    
    def minify_static_files(self):
        """Minify CSS and JS files"""
        try:
            # This would require additional tools like cssmin, jsmin
            print("⚠ Minification skipped (requires additional tools)")
        except Exception as e:
            print(f"⚠ Minification failed: {e}")
    
    def generate_requirements(self):
        """Generate frozen requirements"""
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'freeze'
            ], capture_output=True, text=True)
            
            with open(self.build_dir / 'requirements.txt', 'w') as f:
                f.write(result.stdout)
            print("✓ Requirements frozen")
        except Exception as e:
            print(f"⚠ Failed to freeze requirements: {e}")
    
    def create_docker_files(self):
        """Create Docker-related files"""
        dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --shell /bin/bash ecoreport
RUN chown -R ecoreport:ecoreport /app
USER ecoreport

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:5000/ || exit 1

CMD ["python", "app.py"]
'''
        
        with open(self.build_dir / 'Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        
        dockerignore_content = '''__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.DS_Store
.vscode/
.idea/
'''
        
        with open(self.build_dir / '.dockerignore', 'w') as f:
            f.write(dockerignore_content)
        
        print("✓ Docker files created")
    
    def create_deploy_scripts(self):
        """Create deployment scripts"""
        deploy_sh = '''#!/bin/bash
echo "🚀 Deploying EcoReport Application..."

# Build Docker image
docker build -t ecoreport:latest .

# Stop existing container
docker stop ecoreport-app 2>/dev/null || true
docker rm ecoreport-app 2>/dev/null || true

# Run new container
docker run -d \\
    --name ecoreport-app \\
    -p 80:5000 \\
    -e SECRET_KEY="${SECRET_KEY:-production-secret-key}" \\
    -e DATABASE_URL="${DATABASE_URL:-sqlite:///environmental_reports.db}" \\
    ecoreport:latest

echo "✅ Deployment completed!"
echo "Application available at: http://localhost"
'''
        
        with open(self.build_dir / 'deploy.sh', 'w') as f:
            f.write(deploy_sh)
        
        os.chmod(self.build_dir / 'deploy.sh', 0o755)
        print("✓ Deployment scripts created")
    
    def deploy(self, target='local'):
        """Main deployment function"""
        print(f"🚀 Starting deployment for {target}...")
        
        self.clean_build()
        self.copy_files()
        self.minify_static_files()
        
        if target in ['docker', 'production']:
            self.generate_requirements()
            self.create_docker_files()
            self.create_deploy_scripts()
        
        print(f"✅ Deployment build ready in {self.build_dir}")
        
        if target == 'heroku':
            self.deploy_heroku()
        elif target == 'docker':
            self.deploy_docker()
    
    def deploy_heroku(self):
        """Deploy to Heroku"""
        try:
            os.chdir(self.build_dir)
            
            # Initialize git if not exists
            if not (self.build_dir / '.git').exists():
                subprocess.run(['git', 'init'])
                subprocess.run(['git', 'add', '.'])
                subprocess.run(['git', 'commit', '-m', 'Initial commit'])
            
            # Create Heroku app (if needed)
            app_name = input("Enter Heroku app name (or press Enter to auto-generate): ")
            if app_name:
                subprocess.run(['heroku', 'create', app_name])
            else:
                subprocess.run(['heroku', 'create'])
            
            # Set environment variables
            subprocess.run(['heroku', 'config:set', 'FLASK_ENV=production'])
            
            # Deploy
            subprocess.run(['git', 'push', 'heroku', 'master'])
            
            print("✅ Deployed to Heroku successfully!")
            
        except Exception as e:
            print(f"❌ Heroku deployment failed: {e}")
    
    def deploy_docker(self):
        """Deploy using Docker"""
        try:
            os.chdir(self.build_dir)
            subprocess.run(['./deploy.sh'])
        except Exception as e:
            print(f"❌ Docker deployment failed: {e}")

if __name__ == '__main__':
    deployer = Deployer()
    
    target = sys.argv[1] if len(sys.argv) > 1 else 'local'
    
    if target not in ['local', 'heroku', 'docker', 'production']:
        print("Usage: python deploy.py [local|heroku|docker|production]")
        sys.exit(1)
    
    deployer.deploy(target)