#!/usr/bin/env python3
"""
Project management script for coordinating multiple projects and their port assignments.
"""

import json
import os
import subprocess
import sys
from typing import Dict, List, Optional
import time

def load_project_config() -> Dict:
    """Load project configuration."""
    config_file = "project_ports.json"
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    return {}

def get_project_status() -> Dict[str, Dict]:
    """Get status of all configured projects."""
    config = load_project_config()
    projects = config.get("project_ports", {})
    status = {}
    
    for project_name, project_config in projects.items():
        preferred_port = project_config.get("preferred_port", 8000)
        status[project_name] = {
            "preferred_port": preferred_port,
            "description": project_config.get("description", ""),
            "status": "unknown"
        }
    
    return status

def check_port_usage(port: int) -> bool:
    """Check if a port is in use."""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result == 0  # Port is in use if connection succeeds
    except Exception:
        return False

def display_project_status():
    """Display current status of all projects."""
    print("🏗️  Multi-Project Status")
    print("=" * 50)
    
    status = get_project_status()
    
    for project_name, project_info in status.items():
        port = project_info["preferred_port"]
        description = project_info["description"]
        in_use = check_port_usage(port)
        
        status_icon = "🟢" if not in_use else "🔴"
        status_text = "Available" if not in_use else "In Use"
        
        print(f"{status_icon} {project_name}")
        print(f"   Port: {port}")
        print(f"   Status: {status_text}")
        print(f"   Description: {description}")
        print()

def suggest_port_assignments():
    """Suggest optimal port assignments for all projects."""
    print("💡 Suggested Port Assignments")
    print("=" * 50)
    
    status = get_project_status()
    used_ports = []
    suggestions = {}
    
    for project_name, project_info in status.items():
        preferred_port = project_info["preferred_port"]
        
        # Check if preferred port is available
        if preferred_port not in used_ports and not check_port_usage(preferred_port):
            suggestions[project_name] = preferred_port
            used_ports.append(preferred_port)
        else:
            # Find next available port
            next_port = preferred_port
            while next_port in used_ports or check_port_usage(next_port):
                next_port += 1
            suggestions[project_name] = next_port
            used_ports.append(next_port)
    
    for project_name, port in suggestions.items():
        print(f"📋 {project_name}: Port {port}")
    
    return suggestions

def start_project(project_name: str, port: Optional[int] = None):
    """Start a specific project."""
    print(f"🚀 Starting {project_name}...")
    
    # Set environment variables
    env = os.environ.copy()
    if port:
        env["PORT"] = str(port)
    
    # Try to run the project
    try:
        # Look for common startup files
        startup_files = ["run.py", "main.py", "app.py", "server.py"]
        
        for file in startup_files:
            if os.path.exists(file):
                print(f"   Running {file}...")
                subprocess.run([sys.executable, file], env=env)
                return
        
        print(f"❌ No startup file found for {project_name}")
        print("   Looked for: " + ", ".join(startup_files))
        
    except KeyboardInterrupt:
        print(f"\n🛑 Stopped {project_name}")
    except Exception as e:
        print(f"❌ Error starting {project_name}: {e}")

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("🔧 Multi-Project Manager")
        print("=" * 30)
        print("Usage:")
        print("  py manage_projects.py status     - Show project status")
        print("  py manage_projects.py suggest    - Suggest port assignments")
        print("  py manage_projects.py start <project> [port] - Start a project")
        print()
        print("Available commands:")
        print("  status   - Display current project status")
        print("  suggest  - Suggest optimal port assignments")
        print("  start    - Start a specific project")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        display_project_status()
    
    elif command == "suggest":
        suggestions = suggest_port_assignments()
        print(f"\n💡 These assignments will avoid conflicts")
    
    elif command == "start":
        if len(sys.argv) < 3:
            print("❌ Please specify a project name")
            print("   Example: py manage_projects.py start MultiSportsBettingPlatform")
            return
        
        project_name = sys.argv[2]
        port = int(sys.argv[3]) if len(sys.argv) > 3 else None
        
        start_project(project_name, port)
    
    else:
        print(f"❌ Unknown command: {command}")
        print("   Use 'status', 'suggest', or 'start'")

if __name__ == "__main__":
    main() 