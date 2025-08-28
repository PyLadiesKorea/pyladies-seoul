#!/usr/bin/env python
"""
Development setup script for PyLadies Seoul website.
Run this after initial project setup to ensure homepage is configured.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_development():
    """Set up development environment"""
    print("🐍 Setting up PyLadies Seoul development environment...")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    django.setup()
    
    # Run migrations 
    print("📦 Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Set up homepage
    print("🏠 Setting up homepage...")
    execute_from_command_line(['manage.py', 'setup_homepage'])
    
    # Collect static files
    print("📁 Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
    
    print("✅ Development setup complete!")
    print("🚀 Run 'uv run python manage.py runserver' to start the development server")

if __name__ == '__main__':
    setup_development()