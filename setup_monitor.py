"""
Configure system-level progress monitoring tasks
"""

import json
import subprocess
import sys

# Fix encoding for Windows
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Load the monitor
with open('progress_monitor.py', 'r', encoding='utf-8') as f:
    exec(f.read())

# Create monitor instance
monitor = ProgressMonitor()

# Clear existing tasks
monitor.config['tasks'] = {}

print("=" * 50)
print("  Configure System-Level Progress Monitor")
print("=" * 50)
print()

# Task 1: Docker Desktop
monitor.add_task(
    task_name='Docker Desktop',
    process_name='Docker Desktop'
)

# Task 2: Docker Backend
monitor.add_task(
    task_name='Docker Backend',
    process_name='com.docker.backend.exe'
)

# Task 3: WSL Ubuntu
monitor.add_task(
    task_name='WSL Ubuntu',
    process_name=None,  # WSL via wsl command check
    check_command='wsl -l -v'
)

# Task 4: Sunlogin (SunloginClient)
monitor.add_task(
    task_name='Sunlogin (SunloginClient)',
    process_name='SunloginClient.exe'
)

# Task 5: Docker CLI test
monitor.add_task(
    task_name='Docker CLI',
    process_name=None,
    check_command='docker ps'
)

print("Tasks added:")
print()
print("1. Docker Desktop - Monitor process status")
print("2. Docker Backend - Monitor backend service")
print("3. WSL Ubuntu - Monitor Linux distro status")
print("4. Sunlogin (SunloginClient) - Monitor remote tool")
print("5. Docker CLI - Monitor command line tool")
print()
print("=" * 50)
print()
print("Configuration saved! Now you can setup scheduled tasks...")
print()

# Run initial monitoring
reports = monitor.monitor()

print("Initial check complete!")
print()
