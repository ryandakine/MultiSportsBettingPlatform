# Create a clean repository without sensitive data
Write-Host "Creating clean repository..." -ForegroundColor Green

# Remove existing Git repository
if (Test-Path ".git") {
    Remove-Item -Recurse -Force ".git"
    Write-Host "Removed existing Git repository" -ForegroundColor Yellow
}

# Initialize new repository
git init
Write-Host "Initialized new Git repository" -ForegroundColor Yellow

# Configure Git
git config user.name "ryandakine"
git config user.email "himselfjesus710@gmail.com"

# Add only safe files (excluding sensitive ones)
Write-Host "Adding safe files..." -ForegroundColor Yellow

# Core files
git add README.md
git add .gitignore
git add requirements.txt
git add requirements_minimal.txt

# Main Python files (excluding config with API keys)
git add advanced_ai_features_v4.py
git add advanced_ai_features_v3.py
git add advanced_ml_system.py
git add advanced_analytics_system.py
git add advanced_analytics_system_v2.py
git add advanced_analytics_v3.py
git add advanced_security_authentication_system.py
git add advanced_user_dashboard_system.py

# Integration files
git add integrated_head_agent.py
git add integrated_gold_standard_platform.py
git add integrated_parlay_system.py
git add gold_standard_platform_with_parlays.py

# Sports integration files
git add baseball_script_integration.py
git add football_script_integration.py
git add clean_football_integration.py
git add enhanced_baseball_integration.py
git add enhanced_football_integration.py
git add mlb_integration_connector.py
git add simple_football_integration.py

# System files
git add performance_tracking_system.py
git add portfolio_management_system.py
git add user_dashboard_system.py
git add real_time_odds_integration.py

# Test files
git add test_parlay_system.py
git add test_performance_optimization.py
git add test_production_infrastructure.py
git add test_social_features.py

# Demo files
git add demo_advanced_ai_features_v4.py
git add demo_advanced_analytics_v3.py
git add demo_advanced_ai_features_v3.py
git add demo_advanced_analytics_v2.py
git add demo_ai_ml_working.py
git add demo_ai_ml_simple.py
git add demo_advanced_ai_ml_integration.py
git add demo_advanced_analytics_integration.py
git add demo_complete_real_sports_integration.py
git add demo_docker_deployment.py
git add demo_production_deployment.py

# Infrastructure files
git add docker-compose.yml
git add Dockerfile
git add Dockerfile.demo

# Documentation
git add CLAUDE_AI_INTEGRATION.md
git add DEBUG_REPORT.md
git add ENHANCED_AI_SYSTEM.md
git add EXECUTIVE_SUMMARY.md
git add FASTAPI_INSTALLATION_GUIDE.md
git add FOOTBALL_INTEGRATION_STATUS.md
git add FOOTBALL_INTEGRATION_TEST_RESULTS.md
git add MANUAL_INSTALL.md
git add MULTI_PROJECT_CONTEXT.md
git add PERFORMANCE_TRACKING_DEMO.md
git add PERFORMANCE_TRACKING_DEMONSTRATION.md
git add PERFORMANCE_TRACKING_IMPLEMENTATION.md
git add PROJECT_SUMMARY_AND_END_GOAL.md
git add QUICK_CONTEXT_GUIDE.md
git add QUICK_SETUP.md
git add QUICK_START_NEW_CHAT.md
git add SUB_AGENT_FASTAPI_FIX_README.md
git add SUB_AGENT_INTEGRATION_PLAN.md
git add SUB_AGENT_SYSTEM.md
git add SYSTEM_IMPROVEMENTS_IMPLEMENTATION.md
git add SYSTEM_STATUS_REPORT.md
git add TASKMASTER_SETUP.md
git add UNIFIED_PLATFORM_CAPABILITIES_REPORT.md
git add YOLO_MODE_STATUS_REPORT.md
git add YOLO_MODE_TASKMASTER_COMPLETION.md

# Add src directory (excluding config.py with API keys)
git add src/agents/
git add src/api/
git add src/services/
git add src/utils/
git add src/main.py

# Add other directories
git add k8s/
git add nginx/
git add monitoring/
git add scripts/
git add sports-betting-kendo-react/
git add sub-agents/
git add tests/

# Commit
Write-Host "Committing clean repository..." -ForegroundColor Yellow
git commit -m "Initial commit: MultiSportsBettingPlatform with Advanced AI Features V4"

# Add remote
Write-Host "Adding GitHub remote..." -ForegroundColor Yellow
git remote add origin https://github.com/ryandakine/MultiSportsBettingPlatform.git

# Push
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git push -u origin master

Write-Host "Clean repository created successfully!" -ForegroundColor Green
Write-Host "Visit: https://github.com/ryandakine/MultiSportsBettingPlatform" -ForegroundColor Cyan 