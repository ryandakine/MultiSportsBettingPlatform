#!/usr/bin/env python3
"""
Parse PRD to Taskmaster Tasks
==============================
Extracts tasks from PRD document and creates task-master tasks.
"""

import sys
import re
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def parse_prd(prd_path: Path) -> list:
    """Parse PRD markdown file and extract tasks."""
    tasks = []
    
    with open(prd_path, 'r') as f:
        content = f.read()
    
    # Find Phase sections
    phases = re.findall(r'### Phase (\d+):([^\n]+)\n(.*?)(?=\n### Phase |\Z)', content, re.DOTALL)
    
    for phase_num, phase_title, phase_content in phases:
        phase_title = phase_title.strip()
        
        # Find requirement sections with checkboxes or lists
        # Look for sections like "#### 2.1 Review Existing Backtesting Data"
        sections = re.findall(r'#### ([\d.]+)\s+(.+?)\n(.*?)(?=\n#### |\Z)', phase_content, re.DOTALL)
        
        for section_num, section_title, section_content in sections:
            # Extract Requirements list items
            requirements = re.findall(r'^- (.+)$', section_content, re.MULTILINE)
            
            # Extract Deliverables
            deliverables = re.findall(r'\*\*Deliverables:\*\*\n((?:- .+\n?)+)', section_content, re.MULTILINE)
            
            # Create task for each major section
            task_title = f"Phase {phase_num} - {section_title.strip()}"
            task_description = f"Phase {phase_num}: {phase_title}\n\nSection: {section_title.strip()}\n\n"
            
            if requirements:
                task_description += "Requirements:\n" + "\n".join(f"- {req}" for req in requirements[:5]) + "\n\n"
            
            if deliverables:
                task_description += "Deliverables:\n" + deliverables[0] + "\n"
            
            tasks.append({
                'phase': phase_num,
                'section': section_num,
                'title': task_title,
                'description': task_description.strip()
            })
    
    return tasks


def add_task_to_taskmaster(title: str, description: str, project_root: Path) -> bool:
    """Add a task to task-master."""
    try:
        # Try using task-master CLI (installed version)
        # Format: task-master add-task --prompt "..." --project-root .
        prompt = f"{title}\n\n{description}"
        cmd = [
            'task-master', 'add-task',
            '--prompt', prompt,
            '--project-root', str(project_root)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(project_root))
        
        if result.returncode == 0:
            print(f"✅ Added task: {title}")
            if result.stdout:
                print(f"   {result.stdout.strip()}")
            return True
        else:
            # Try alternative: npx task-master-ai
            print(f"⚠️  task-master CLI failed, trying npx...")
            cmd = [
                'npx', '-y', 'task-master-ai', 'add-task',
                '--prompt', prompt,
                '--project-root', str(project_root)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, cwd=str(project_root))
            
            if result.returncode == 0:
                print(f"✅ Added task: {title} (via npx)")
                return True
            else:
                print(f"⚠️  Failed to add task '{title}'")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}")
                return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout adding task '{title}'")
        return False
    except FileNotFoundError:
        print(f"⚠️  task-master not found. Task saved for manual addition:")
        print(f"   Title: {title}")
        return False
    except Exception as e:
        print(f"❌ Error adding task '{title}': {e}")
        return False


def main():
    """Main function."""
    prd_path = project_root / "PRD_PLAYOFF_BETTING_STRATEGY.md"
    
    if not prd_path.exists():
        print(f"❌ PRD file not found: {prd_path}")
        return 1
    
    print("=" * 60)
    print("📋 PARSING PRD TO TASKMASTER TASKS")
    print("=" * 60)
    print()
    print(f"Reading PRD: {prd_path}")
    print()
    
    # Parse PRD
    tasks = parse_prd(prd_path)
    
    print(f"📊 Found {len(tasks)} tasks in PRD")
    print()
    
    # Show tasks that will be created
    print("Tasks to be created:")
    print("-" * 60)
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task['title']}")
        print(f"   Phase {task['phase']}, Section {task['section']}")
    print()
    
    # Add tasks automatically (non-interactive mode)
    print()
    print("Creating tasks in task-master...")
    print("-" * 60)
    
    created = 0
    for task in tasks:
        if add_task_to_taskmaster(task['title'], task['description'], project_root):
            created += 1
    
    print()
    print("=" * 60)
    print(f"✅ Created {created}/{len(tasks)} tasks")
    print("=" * 60)
    
    if created < len(tasks):
        print()
        print("⚠️  Some tasks failed to create. You may need to:")
        print("   1. Install task-master-ai: npm install -g task-master-ai")
        print("   2. Or add tasks manually using the task-master CLI")
        print("   3. Or review the PRD and extract tasks manually")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

