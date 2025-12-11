#!/usr/bin/env python3
"""
Create Kendo React Project - YOLO MODE! (Fixed Encoding)
========================================================
Generate complete React project structure with Kendo UI components
"""

import os
import json
from kendo_react_ui_system import KendoReactUISystem

def create_project_structure():
    """Create complete React project structure"""
    print("🚀 Creating Kendo React Project Structure - YOLO MODE!")
    print("=" * 70)
    
    # Initialize Kendo system
    kendo_system = KendoReactUISystem()
    
    # Create project directory
    project_dir = "sports-betting-kendo-react"
    
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
        print(f"✅ Created project directory: {project_dir}")
    
    # Create subdirectories
    dirs_to_create = [
        f"{project_dir}/src",
        f"{project_dir}/src/components",
        f"{project_dir}/src/styles",
        f"{project_dir}/public"
    ]
    
    for dir_path in dirs_to_create:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✅ Created directory: {dir_path}")
    
    # Generate package.json
    print(f"\n📦 Generating package.json...")
    package_json = kendo_system.generate_package_json()
    with open(f"{project_dir}/package.json", "w", encoding='utf-8') as f:
        f.write(package_json)
    print(f"✅ Generated package.json")
    
    # Generate main App component
    print(f"\n⚛️ Generating App.js...")
    app_component = kendo_system.generate_main_app_component()
    with open(f"{project_dir}/src/App.js", "w", encoding='utf-8') as f:
        f.write(app_component)
    print(f"✅ Generated App.js")
    
    # Generate custom CSS
    print(f"\n🎨 Generating App.css...")
    custom_css = kendo_system.generate_custom_css()
    with open(f"{project_dir}/src/App.css", "w", encoding='utf-8') as f:
        f.write(custom_css)
    print(f"✅ Generated App.css")
    
    # Generate index.js
    print(f"\n🎯 Generating index.js...")
    index_js = """
import React from 'react';
import ReactDOM from 'react-dom/client';
import './App.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
    with open(f"{project_dir}/src/index.js", "w", encoding='utf-8') as f:
        f.write(index_js.strip())
    print(f"✅ Generated index.js")
    
    # Generate individual components
    print(f"\n🧩 Generating individual components...")
    
    # Portfolio Chart Component
    portfolio_chart = kendo_system.components.get("portfolio_chart")
    if portfolio_chart:
        with open(f"{project_dir}/src/components/PortfolioPerformanceChart.js", "w", encoding='utf-8') as f:
            f.write(portfolio_chart['code'])
        print(f"✅ Generated PortfolioPerformanceChart.js")
    
    # Betting Grid Component
    betting_grid = kendo_system.components.get("betting_grid")
    if betting_grid:
        with open(f"{project_dir}/src/components/BettingOpportunitiesGrid.js", "w", encoding='utf-8') as f:
            f.write(betting_grid['code'])
        print(f"✅ Generated BettingOpportunitiesGrid.js")
    
    # Analytics Dashboard Component
    analytics_dashboard = kendo_system.components.get("analytics_dashboard")
    if analytics_dashboard:
        with open(f"{project_dir}/src/components/AnalyticsDashboard.js", "w", encoding='utf-8') as f:
            f.write(analytics_dashboard['code'])
        print(f"✅ Generated AnalyticsDashboard.js")
    
    # Notification System Component
    notification_system = kendo_system.components.get("notification_system")
    if notification_system:
        with open(f"{project_dir}/src/components/NotificationSystem.js", "w", encoding='utf-8') as f:
            f.write(notification_system['code'])
        print(f"✅ Generated NotificationSystem.js")
    
    # User Management Component
    user_management = kendo_system.components.get("user_management")
    if user_management:
        with open(f"{project_dir}/src/components/UserManagement.js", "w", encoding='utf-8') as f:
            f.write(user_management['code'])
        print(f"✅ Generated UserManagement.js")
    
    # Generate public/index.html
    print(f"\n🌐 Generating index.html...")
    index_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Professional Sports Betting Platform with Kendo React UI" />
    <title>SportsBet Pro - Kendo React UI</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>"""
    
    with open(f"{project_dir}/public/index.html", "w", encoding='utf-8') as f:
        f.write(index_html)
    print(f"✅ Generated index.html")
    
    # Generate README.md
    print(f"\n📖 Generating README.md...")
    setup_instructions = kendo_system.get_setup_instructions()
    
    readme_content = f"""# SportsBet Pro - Kendo React UI

Professional Sports Betting Platform built with **Kendo React UI** components.

## 🚀 Features

{chr(10).join([f"- {feature}" for feature in setup_instructions['features']])}

## 📋 Requirements

- Node.js >= 16.0.0
- React >= 18.0.0
- Kendo UI License (30-day free trial available)

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start development server:**
   ```bash
   npm start
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## 📦 Kendo UI Packages

{chr(10).join([f"- {package}" for package in setup_instructions['kendo_packages']])}

## 🎨 Available Themes

{chr(10).join([f"- {theme}" for theme in setup_instructions['available_themes']])}

## 🧩 Components

{chr(10).join([f"- **{component}**: {kendo_system.components[component]['type']}" for component in setup_instructions['generated_components']])}

## 📊 Charts

{chr(10).join([f"- **{chart.title}**: {chart.chart_type.title()} chart with {len(chart.data)} data points" for chart in kendo_system.charts.values()])}

## 📋 Grids

{chr(10).join([f"- **{grid.grid_id}**: {len(grid.columns)} columns, {len(grid.data)} rows" for grid in kendo_system.grids.values()])}

## 🔧 Usage

The application includes several main sections:

1. **Dashboard** - Portfolio performance and key metrics
2. **Live Betting** - Real-time betting opportunities
3. **Analytics** - Sports performance analysis
4. **User Management** - Admin interface for user management

### Theme Switching

Use the theme dropdown in the app bar to switch between:
- Material Design
- Bootstrap  
- Default Dark
- Fluent Design

## 🎯 Project Structure

```
src/
├── App.js                 # Main application component
├── App.css               # Custom styles
├── index.js              # Entry point
└── components/
    ├── PortfolioPerformanceChart.js
    ├── BettingOpportunitiesGrid.js
    ├── AnalyticsDashboard.js
    ├── NotificationSystem.js
    └── UserManagement.js
```

## 📈 Getting Started

1. Open the application in your browser (http://localhost:3000)
2. Explore the different sections using the navigation
3. Switch themes using the dropdown in the top bar
4. Test the interactive components and data visualization

## 🎉 Built With

- **React 18** - Frontend framework
- **Kendo React UI** - Professional UI components
- **Material Design** - Default theme
- **Chart.js Integration** - Advanced data visualization

## 📄 License

This project uses Kendo UI for React. Please ensure you have a valid license.

---

**Powered by Kendo React UI** 🚀"""
    
    with open(f"{project_dir}/README.md", "w", encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ Generated README.md")
    
    # Generate setup scripts
    print(f"\n⚙️ Generating setup scripts...")
    
    # Windows setup script (no emojis to avoid encoding issues)
    setup_bat = """@echo off
echo Setting up SportsBet Pro with Kendo React UI
echo ==============================================

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed. Please install Node.js >= 16.0.0
    pause
    exit /b 1
)

echo Node.js check passed

:: Install dependencies
echo Installing dependencies...
call npm install

if %errorlevel% equ 0 (
    echo Dependencies installed successfully
) else (
    echo Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo To start the development server:
echo   npm start
echo.
echo To build for production:
echo   npm run build
echo.
echo Happy coding!
pause"""
    
    with open(f"{project_dir}/setup.bat", "w", encoding='utf-8') as f:
        f.write(setup_bat)
    print(f"✅ Generated setup.bat")
    
    # Summary
    print(f"\n" + "=" * 70)
    print(f"🎉 Kendo React Project Created Successfully!")
    print(f"=" * 70)
    print(f"📁 Project location: {project_dir}")
    
    # Count files safely
    try:
        total_files = 0
        for root, dirs, files in os.walk(project_dir):
            total_files += len(files)
        print(f"📦 Files generated: {total_files}")
    except:
        print(f"📦 Files generated: Multiple files created")
    
    print(f"🧩 Components: {len(setup_instructions['generated_components'])}")
    print(f"🎨 Themes: {len(setup_instructions['available_themes'])}")
    print(f"📊 Charts: {len(kendo_system.charts)}")
    print(f"📋 Grids: {len(kendo_system.grids)}")
    print(f"")
    print(f"🚀 Next steps:")
    print(f"1. cd {project_dir}")
    print(f"2. npm install")
    print(f"3. npm start")
    print(f"")
    print(f"🎯 Open http://localhost:3000 to view your professional sports betting platform!")

if __name__ == "__main__":
    create_project_structure() 