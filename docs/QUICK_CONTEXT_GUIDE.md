# Quick Context Switching Guide

## **🎯 Multi-Project Sports Betting Platform**

### **Current Projects:**
1. **Head Agent:** `C:\Users\himse\MultiSportsBettingPlatform` (Ready - 85%)
2. **CFL/NFL Gold:** `C:\Users\himse\cfl_nfl_gold` (In Progress - 85%)
3. **Baseball System:** `C:\Users\himse\[baseball_path]` (In Progress - 90%)
4. **Basketball System:** `C:\Users\himse\[basketball_path]` (Planned)
5. **Hockey System:** `C:\Users\himse\[hockey_path]` (Planned)

## **🔄 Quick Context Switching**

### **Using the Context Manager:**
```bash
# List all projects
python project_context_manager.py list

# Switch to Head Agent (current)
python project_context_manager.py switch head_agent

# Switch to CFL/NFL Gold System
python project_context_manager.py switch cfl_nfl_gold

# Switch to Baseball System
python project_context_manager.py switch baseball

# Check current project status
python project_context_manager.py status

# Update project status
python project_context_manager.py update head_agent ready 85

# Run Task Master command
python project_context_manager.py task-master "get-tasks"
```

### **Manual Context Switching:**
```bash
# Head Agent (Current)
cd C:\Users\himse\MultiSportsBettingPlatform
task-master get-tasks --project-root .

# CFL/NFL Gold System
cd C:\Users\himse\cfl_nfl_gold
task-master get-tasks --project-root .

# Baseball System
cd C:\Users\himse\[baseball_path]
task-master get-tasks --project-root .
```

## **📋 Current Focus: Head Agent (MultiSportsBettingPlatform)**

### **Status:** Ready (85% Complete)
### **Current Issues:** Pydantic compatibility, port conflicts
### **Priority:** High - Need to complete sub-agent integration

### **Current Features:**
- ✅ YOLO Mode Implementation - Fully operational with verbose logging
- ✅ MLB System Integration - Connected and operational (port 8000)
- ✅ Verbose Logging System - Comprehensive logging with emoji indicators
- ✅ Dynamic Port Management - Advanced port utilities working
- ✅ Specialized System Integration - Logic implemented and tested
- ✅ Cross-System Prediction - Aggregating predictions from multiple systems

### **Current Issues:**
- ❌ Pydantic Configuration Error - FastAPI imports failing due to version conflicts
- ❌ Port Conflicts - Multiple processes trying to use same ports
- ❌ CFL/NFL System Integration - System not running (port 8010)

## **🎯 Task Master AI Commands**

### **For Head Agent (Current):**
```bash
# Get current tasks
task-master get-tasks --project-root .

# Get next task to work on
task-master next-task --project-root .

# Add new task
task-master add-task --prompt "Fix Pydantic compatibility issues" --project-root .

# Test sub-agent integration
task-master add-task --prompt "Test CFL/NFL Gold sub-agent integration" --project-root .

# Monitor all sub-agents
task-master add-task --prompt "Monitor sub-agent health and performance" --project-root .
```

### **For CFL/NFL Gold System:**
```bash
# Get current tasks
task-master get-tasks --project-root .

# Get next task to work on
task-master next-task --project-root .

# Set task status
task-master set-status --id 1.5 --status in-progress --project-root .

# Expand task into subtasks
task-master expand-task --id 1.5 --project-root .
```

## **🏗️ Architecture Context**

```
Multi-Sport Betting Platform (Head Agent) ← Current Focus
├── CFL/NFL Gold System (Sub-Agent) 
├── Baseball System (Sub-Agent) 
├── Basketball System (Sub-Agent) ← Next to Create
└── Hockey System (Sub-Agent) ← Next to Create
```

### **Communication Flow:**
1. **Sub-Agents** → Register with Head Agent
2. **Sub-Agents** → Send predictions and data
3. **Head Agent** → Aggregates data from all sub-agents
4. **Head Agent** → Provides unified user interface
5. **Head Agent** → Manages cross-sport learning

## **📊 Project Priorities**

### **Immediate (This Week):**
1. **Fix Pydantic Issues** - Resolve FastAPI import problems
2. **Test YOLO Server** - Verify HTTP server works on clean port
3. **Start CFL/NFL System** - Enable full integration testing

### **Short Term (Next 2 Weeks):**
1. **Complete CFL/NFL Integration** - Fix sub-agent communication
2. **Test Baseball Integration** - Verify existing connection
3. **Cross-Project Testing** - Test all sub-agents together

### **Long Term (Next Month):**
1. **Unified Dashboard** - Multi-sport user interface
2. **Global Learning** - Cross-sport pattern recognition
3. **Multi-Sport Parlays** - Cross-sport betting combinations

## **🔧 Development Workflow**

### **Daily Routine:**
1. **Morning:** Check all project statuses
2. **Focus:** Work on one sub-agent at a time
3. **Integration:** Test with head agent
4. **Evening:** Update progress and plan next day

### **Context Switching Checklist:**
- [ ] Save current work and commit changes
- [ ] Update project status
- [ ] Switch to target project
- [ ] Load Task Master context
- [ ] Review current tasks
- [ ] Begin focused work

## **📞 Quick Reference**

### **Current Project:** Head Agent (MultiSportsBettingPlatform)
### **Current Directory:** `C:\Users\himse\MultiSportsBettingPlatform`
### **Current Issues:** Pydantic compatibility, port conflicts
### **Next Goal:** Fix Pydantic issues and start CFL/NFL system

### **Key Files:**
- `MULTI_PROJECT_CONTEXT.md` - Full project context
- `project_context_manager.py` - Context switching tool
- `DEBUG_REPORT.md` - Current status and issues
- `.cursorrules` - Verbose logging requirements
- `run.py` - YOLO mode with verbose logging

### **Current Status:**
- ✅ YOLO Mode: Fully operational
- ✅ Verbose Logging: Implemented with emoji indicators
- ✅ MLB Integration: Connected and working
- ❌ FastAPI: Pydantic import issues
- ❌ CFL/NFL System: Not running
- ❌ Port Conflicts: Multiple processes

---

**Last Updated:** July 29, 2025  
**Context Manager:** Task Master AI  
**Status:** Active Development - YOLO Mode Operational 