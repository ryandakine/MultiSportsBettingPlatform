#!/usr/bin/env python3
"""
Multi-Project Context Manager for Sports Betting Platform
Manages context switching between different sub-agent projects
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

class ProjectContextManager:
    """
    Manages context switching between different sports betting projects.
    """
    
    def __init__(self):
        self.projects = {
            "head_agent": {
                "name": "Multi-Sport Betting Platform",
                "path": r"C:\Users\himse\MultiSportsBettingPlatform",
                "type": "head_agent",
                "status": "ready",
                "description": "Main coordinator for all sub-agents"
            },
            "cfl_nfl_gold": {
                "name": "CFL/NFL Gold System",
                "path": r"C:\Users\himse\cfl_nfl_gold",
                "type": "sub_agent",
                "sport": "football",
                "status": "in_progress",
                "completion": 85,
                "description": "Football betting sub-agent"
            },
            "baseball": {
                "name": "Baseball System",
                "path": r"C:\Users\himse\[baseball_path]",  # Update with actual path
                "type": "sub_agent",
                "sport": "baseball",
                "status": "in_progress",
                "completion": 90,
                "description": "Baseball betting sub-agent"
            },
            "basketball": {
                "name": "Basketball System",
                "path": r"C:\Users\himse\[basketball_path]",  # Update with actual path
                "type": "sub_agent",
                "sport": "basketball",
                "status": "planned",
                "completion": 0,
                "description": "Basketball betting sub-agent"
            },
            "hockey": {
                "name": "Hockey System",
                "path": r"C:\Users\himse\[hockey_path]",  # Update with actual path
                "type": "sub_agent",
                "sport": "hockey",
                "status": "planned",
                "completion": 0,
                "description": "Hockey betting sub-agent"
            }
        }
        
        self.current_project = "head_agent"  # Default to head agent
        self.context_file = "project_context.json"
        
    def save_context(self):
        """Save current context to file."""
        context = {
            "current_project": self.current_project,
            "projects": self.projects,
            "last_updated": str(Path.cwd())
        }
        
        with open(self.context_file, 'w') as f:
            json.dump(context, f, indent=2)
            
        print(f"✅ Context saved to {self.context_file}")
    
    def load_context(self):
        """Load context from file."""
        if Path(self.context_file).exists():
            with open(self.context_file, 'r') as f:
                context = json.load(f)
                self.current_project = context.get("current_project", "head_agent")
                self.projects.update(context.get("projects", {}))
            print(f"✅ Context loaded from {self.context_file}")
        else:
            print("ℹ️ No context file found, using defaults")
    
    def list_projects(self):
        """List all projects with their status."""
        print("\n🏈 Multi-Sport Betting Platform - Project Status")
        print("=" * 60)
        
        for project_id, project in self.projects.items():
            status_emoji = {
                "ready": "✅",
                "in_progress": "🚧",
                "planned": "📋",
                "completed": "🎉"
            }.get(project['status'], "❓")
            
            current_marker = " ← CURRENT" if project_id == self.current_project else ""
            
            print(f"{status_emoji} {project['name']} ({project_id}){current_marker}")
            print(f"   Type: {project['type']}")
            if 'sport' in project:
                print(f"   Sport: {project['sport']}")
            print(f"   Status: {project['status']}")
            if 'completion' in project:
                print(f"   Completion: {project['completion']}%")
            print(f"   Path: {project['path']}")
            print(f"   Description: {project['description']}")
            print()
    
    def switch_project(self, project_id: str):
        """Switch to a different project context."""
        if project_id not in self.projects:
            print(f"❌ Project '{project_id}' not found")
            return False
        
        project = self.projects[project_id]
        project_path = Path(project['path'])
        
        if not project_path.exists():
            print(f"❌ Project path does not exist: {project_path}")
            return False
        
        # Save current context
        self.save_context()
        
        # Update current project
        self.current_project = project_id
        
        print(f"🔄 Switching to {project['name']} ({project_id})")
        print(f"📁 Path: {project_path}")
        print(f"🎯 Type: {project['type']}")
        
        if project['type'] == 'sub_agent':
            print(f"🏈 Sport: {project['sport']}")
        
        # Change directory
        try:
            os.chdir(project_path)
            print(f"✅ Changed to project directory: {project_path}")
            
            # Check if Task Master is available
            if self.check_task_master():
                print("✅ Task Master AI available in this project")
                self.show_task_master_commands(project_id)
            else:
                print("⚠️ Task Master AI not found in this project")
                
        except Exception as e:
            print(f"❌ Error switching to project: {e}")
            return False
        
        return True
    
    def check_task_master(self) -> bool:
        """Check if Task Master AI is available in current project."""
        try:
            result = subprocess.run(
                ["task-master", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def show_task_master_commands(self, project_id: str):
        """Show relevant Task Master commands for the project."""
        print("\n📋 Task Master AI Commands for this project:")
        print("-" * 40)
        
        if project_id == "cfl_nfl_gold":
            print("🏈 CFL/NFL Gold System Commands:")
            print("  task-master get-tasks --project-root .")
            print("  task-master next-task --project-root .")
            print("  task-master set-status --id 1.5 --status in-progress --project-root .")
            print("  task-master expand-task --id 1.5 --project-root .")
            
        elif project_id == "head_agent":
            print("🎯 Head Agent Commands:")
            print("  task-master get-tasks --project-root .")
            print("  task-master add-task --prompt 'Test sub-agent integration' --project-root .")
            
        else:
            print("📋 General Commands:")
            print("  task-master get-tasks --project-root .")
            print("  task-master add-task --prompt 'Your task description' --project-root .")
    
    def get_current_project_info(self):
        """Get information about the current project."""
        project = self.projects[self.current_project]
        
        print(f"\n🎯 Current Project: {project['name']} ({self.current_project})")
        print(f"📁 Path: {Path.cwd()}")
        print(f"🎯 Type: {project['type']}")
        print(f"📊 Status: {project['status']}")
        
        if 'sport' in project:
            print(f"🏈 Sport: {project['sport']}")
        
        if 'completion' in project:
            print(f"📈 Completion: {project['completion']}%")
        
        print(f"📝 Description: {project['description']}")
    
    def update_project_status(self, project_id: str, status: str, completion: Optional[int] = None):
        """Update project status."""
        if project_id not in self.projects:
            print(f"❌ Project '{project_id}' not found")
            return
        
        self.projects[project_id]['status'] = status
        if completion is not None:
            self.projects[project_id]['completion'] = completion
        
        print(f"✅ Updated {self.projects[project_id]['name']} status to: {status}")
        if completion is not None:
            print(f"✅ Updated completion to: {completion}%")
        
        self.save_context()
    
    def show_architecture_overview(self):
        """Show the overall architecture."""
        print("\n🏗️ Multi-Sport Betting Platform Architecture")
        print("=" * 50)
        
        # Head Agent
        head_agent = self.projects["head_agent"]
        print(f"🎯 {head_agent['name']} (Head Agent)")
        print(f"   Status: {head_agent['status']}")
        print(f"   Role: Coordinates all sub-agents")
        print()
        
        # Sub-Agents
        print("🏈 Sub-Agents:")
        for project_id, project in self.projects.items():
            if project['type'] == 'sub_agent':
                status_emoji = {
                    "ready": "✅",
                    "in_progress": "🚧",
                    "planned": "📋"
                }.get(project.status, "❓")
                
                print(f"   {status_emoji} {project['name']} ({project['sport']})")
                print(f"      Status: {project['status']}")
                if 'completion' in project:
                    print(f"      Completion: {project['completion']}%")
                print()
    
    def run_task_master_command(self, command: str):
        """Run a Task Master command in the current project."""
        try:
            full_command = f"task-master {command} --project-root ."
            print(f"🚀 Running: {full_command}")
            
            result = subprocess.run(
                full_command,
                shell=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Task Master command completed successfully")
                print(result.stdout)
            else:
                print("❌ Task Master command failed")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Error running Task Master command: {e}")

def main():
    """Main function for the context manager."""
    manager = ProjectContextManager()
    manager.load_context()
    
    if len(sys.argv) < 2:
        print("🏈 Multi-Project Context Manager")
        print("=" * 40)
        print("Usage:")
        print("  python project_context_manager.py list")
        print("  python project_context_manager.py switch <project_id>")
        print("  python project_context_manager.py status")
        print("  python project_context_manager.py architecture")
        print("  python project_context_manager.py update <project_id> <status> [completion]")
        print("  python project_context_manager.py task-master <command>")
        print()
        print("Available projects:")
        for project_id, project in manager.projects.items():
            print(f"  {project_id}: {project['name']}")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        manager.list_projects()
        
    elif command == "switch" and len(sys.argv) >= 3:
        project_id = sys.argv[2]
        manager.switch_project(project_id)
        
    elif command == "status":
        manager.get_current_project_info()
        
    elif command == "architecture":
        manager.show_architecture_overview()
        
    elif command == "update" and len(sys.argv) >= 4:
        project_id = sys.argv[2]
        status = sys.argv[3]
        completion = int(sys.argv[4]) if len(sys.argv) >= 5 else None
        manager.update_project_status(project_id, status, completion)
        
    elif command == "task-master" and len(sys.argv) >= 3:
        task_command = " ".join(sys.argv[2:])
        manager.run_task_master_command(task_command)
        
    else:
        print("❌ Invalid command or missing arguments")

if __name__ == "__main__":
    main() 