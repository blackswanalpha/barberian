#!/usr/bin/env python
"""
A simple script to run the Django development server with some default settings.
"""

import os
import sys
import subprocess
import webbrowser
from time import sleep

def main():
    """Run the Django development server."""
    print("Starting Barberian Development Server...")
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Virtual environment not detected. It's recommended to run this in a virtual environment.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
    
    # Check if Django is installed
    try:
        import django
        print(f"Django version: {django.get_version()}")
    except ImportError:
        print("Django is not installed. Please install it with 'pip install django'.")
        sys.exit(1)
    
    # Check for database migrations
    print("Checking for database migrations...")
    subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
    subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    
    # Collect static files
    print("Collecting static files...")
    subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput"], check=True)
    
    # Start the development server
    port = 8000
    host = "127.0.0.1"
    url = f"http://{host}:{port}"
    
    print(f"\nStarting development server at {url}")
    print("Quit the server with CONTROL-C.\n")
    
    # Open the browser after a short delay
    def open_browser():
        sleep(2)
        webbrowser.open(url)
    
    from threading import Thread
    browser_thread = Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run the server
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "barberian.settings")
    subprocess.run([sys.executable, "manage.py", "runserver", f"{host}:{port}"])

if __name__ == "__main__":
    main()
