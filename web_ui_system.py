#!/usr/bin/env python3
"""
Web UI System - YOLO MODE!
==========================
HTML templates, CSS styling, and JavaScript for interactive dashboard components
for ultra-modern sports betting platform interface
"""

import asyncio
import json
import time
import math
import random
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import defaultdict, deque
import uuid
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WebPage:
    """Web page configuration"""
    page_id: str
    title: str
    template: str
    css_files: List[str]
    js_files: List[str]
    data_endpoints: List[str]
    requires_auth: bool = True

@dataclass
class UIComponent:
    """UI component configuration"""
    component_id: str
    component_type: str  # 'chart', 'table', 'form', 'card', 'modal'
    template: str
    css_class: str
    js_handlers: List[str]
    data_bindings: Dict[str, str]

class WebUISystem:
    """Web UI system with templates and components"""
    
    def __init__(self):
        self.pages = {}
        self.components = {}
        self.templates = {}
        self.static_files = {}
        
        # Initialize default pages and components
        self._initialize_default_pages()
        self._initialize_default_components()
        self._initialize_templates()
        
        logger.info("🚀 Web UI System initialized - YOLO MODE!")
    
    def _initialize_default_pages(self):
        """Initialize default web pages"""
        self.pages = {
            "dashboard": WebPage(
                page_id="dashboard",
                title="Sports Betting Dashboard",
                template="dashboard.html",
                css_files=["main.css", "dashboard.css", "charts.css"],
                js_files=["main.js", "dashboard.js", "charts.js"],
                data_endpoints=["/api/dashboard", "/api/portfolio", "/api/opportunities"],
                requires_auth=True
            ),
            "login": WebPage(
                page_id="login",
                title="Login - Sports Betting Platform",
                template="login.html",
                css_files=["main.css", "auth.css"],
                js_files=["auth.js"],
                data_endpoints=["/api/auth/login"],
                requires_auth=False
            ),
            "register": WebPage(
                page_id="register",
                title="Register - Sports Betting Platform",
                template="register.html",
                css_files=["main.css", "auth.css"],
                js_files=["auth.js"],
                data_endpoints=["/api/auth/register"],
                requires_auth=False
            ),
            "profile": WebPage(
                page_id="profile",
                title="User Profile",
                template="profile.html",
                css_files=["main.css", "profile.css"],
                js_files=["profile.js"],
                data_endpoints=["/api/users/profile", "/api/users/preferences"],
                requires_auth=True
            ),
            "admin": WebPage(
                page_id="admin",
                title="Admin Panel",
                template="admin.html",
                css_files=["main.css", "admin.css"],
                js_files=["admin.js"],
                data_endpoints=["/api/admin/users", "/api/admin/security-logs"],
                requires_auth=True
            )
        }
    
    def _initialize_default_components(self):
        """Initialize default UI components"""
        self.components = {
            "portfolio_card": UIComponent(
                component_id="portfolio_card",
                component_type="card",
                template="portfolio_card.html",
                css_class="portfolio-card",
                js_handlers=["updatePortfolio", "refreshData"],
                data_bindings={"total_value": "portfolio.total_value", "roi": "portfolio.roi_percentage"}
            ),
            "chart_widget": UIComponent(
                component_id="chart_widget",
                component_type="chart",
                template="chart_widget.html",
                css_class="chart-widget",
                js_handlers=["initChart", "updateChart", "resizeChart"],
                data_bindings={"chart_data": "charts.portfolio_chart", "chart_type": "charts.portfolio_chart.chart_type"}
            ),
            "opportunities_table": UIComponent(
                component_id="opportunities_table",
                component_type="table",
                template="opportunities_table.html",
                css_class="opportunities-table",
                js_handlers=["loadOpportunities", "placeBet", "refreshTable"],
                data_bindings={"opportunities": "live_opportunities"}
            ),
            "alerts_panel": UIComponent(
                component_id="alerts_panel",
                component_type="panel",
                template="alerts_panel.html",
                css_class="alerts-panel",
                js_handlers=["loadAlerts", "markRead", "dismissAlert"],
                data_bindings={"alerts": "alerts"}
            )
        }
    
    def _initialize_templates(self):
        """Initialize HTML templates"""
        self.templates = {
            "dashboard.html": self._get_dashboard_template(),
            "login.html": self._get_login_template(),
            "register.html": self._get_register_template(),
            "profile.html": self._get_profile_template(),
            "admin.html": self._get_admin_template(),
            "portfolio_card.html": self._get_portfolio_card_template(),
            "chart_widget.html": self._get_chart_widget_template(),
            "opportunities_table.html": self._get_opportunities_table_template(),
            "alerts_panel.html": self._get_alerts_panel_template()
        }
    
    def _get_dashboard_template(self) -> str:
        """Get dashboard HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/dashboard.css">
    <link rel="stylesheet" href="/static/css/charts.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body class="dashboard-body">
    <header class="dashboard-header">
        <div class="header-content">
            <h1 class="logo">🏈 SportsBet Pro</h1>
            <nav class="main-nav">
                <a href="/dashboard" class="nav-link active">Dashboard</a>
                <a href="/opportunities" class="nav-link">Opportunities</a>
                <a href="/portfolio" class="nav-link">Portfolio</a>
                <a href="/profile" class="nav-link">Profile</a>
                <a href="/admin" class="nav-link admin-only">Admin</a>
            </nav>
            <div class="user-menu">
                <span class="username">{{ user.username }}</span>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
        </div>
    </header>

    <main class="dashboard-main">
        <div class="dashboard-grid">
            <!-- Portfolio Overview Card -->
            <div class="widget portfolio-overview" data-widget="portfolio_card">
                <div class="widget-header">
                    <h3>Portfolio Overview</h3>
                    <button class="refresh-btn" onclick="refreshPortfolio()">🔄</button>
                </div>
                <div class="widget-content">
                    <div class="metric-row">
                        <div class="metric">
                            <span class="metric-label">Total Value</span>
                            <span class="metric-value" id="total-value">${{ portfolio.total_value | format_currency }}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Total Profit</span>
                            <span class="metric-value {{ 'positive' if portfolio.total_profit > 0 else 'negative' }}" id="total-profit">
                                {{ portfolio.total_profit | format_currency }}
                            </span>
                        </div>
                    </div>
                    <div class="metric-row">
                        <div class="metric">
                            <span class="metric-label">ROI</span>
                            <span class="metric-value {{ 'positive' if portfolio.roi_percentage > 0 else 'negative' }}" id="roi">
                                {{ portfolio.roi_percentage | format_percentage }}
                            </span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Win Rate</span>
                            <span class="metric-value" id="win-rate">{{ portfolio.win_rate | format_percentage }}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Portfolio Performance Chart -->
            <div class="widget chart-widget" data-widget="chart_widget">
                <div class="widget-header">
                    <h3>Portfolio Performance</h3>
                    <div class="chart-controls">
                        <button class="chart-btn" onclick="changeChartPeriod('7d')">7D</button>
                        <button class="chart-btn active" onclick="changeChartPeriod('30d')">30D</button>
                        <button class="chart-btn" onclick="changeChartPeriod('90d')">90D</button>
                    </div>
                </div>
                <div class="widget-content">
                    <canvas id="portfolio-chart" width="400" height="200"></canvas>
                </div>
            </div>

            <!-- Live Opportunities Table -->
            <div class="widget opportunities-widget" data-widget="opportunities_table">
                <div class="widget-header">
                    <h3>Live Betting Opportunities</h3>
                    <div class="filter-controls">
                        <select id="sport-filter" onchange="filterOpportunities()">
                            <option value="all">All Sports</option>
                            <option value="basketball">Basketball</option>
                            <option value="football">Football</option>
                            <option value="hockey">Hockey</option>
                            <option value="baseball">Baseball</option>
                        </select>
                    </div>
                </div>
                <div class="widget-content">
                    <table class="opportunities-table">
                        <thead>
                            <tr>
                                <th>Match</th>
                                <th>Sport</th>
                                <th>Prediction</th>
                                <th>Confidence</th>
                                <th>Expected ROI</th>
                                <th>Risk</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="opportunities-tbody">
                            {% for opp in live_opportunities %}
                            <tr class="opportunity-row" data-sport="{{ opp.sport }}">
                                <td>{{ opp.home_team }} vs {{ opp.away_team }}</td>
                                <td>{{ opp.sport | title }}</td>
                                <td>{{ opp.prediction | title }}</td>
                                <td>{{ opp.confidence | format_percentage }}</td>
                                <td class="{{ 'positive' if opp.expected_roi > 0 else 'negative' }}">
                                    {{ opp.expected_roi | format_percentage }}
                                </td>
                                <td><span class="risk-badge risk-{{ opp.risk_level }}">{{ opp.risk_level | title }}</span></td>
                                <td>
                                    <button class="bet-btn" onclick="placeBet('{{ opp.opportunity_id }}')">Place Bet</button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Alerts Panel -->
            <div class="widget alerts-widget" data-widget="alerts_panel">
                <div class="widget-header">
                    <h3>Alerts & Notifications</h3>
                    <button class="clear-all-btn" onclick="clearAllAlerts()">Clear All</button>
                </div>
                <div class="widget-content">
                    <div id="alerts-container">
                        {% for alert in alerts %}
                        <div class="alert alert-{{ alert.alert_type }}" data-alert-id="{{ alert.alert_id }}">
                            <div class="alert-header">
                                <span class="alert-title">{{ alert.title }}</span>
                                <button class="dismiss-btn" onclick="dismissAlert('{{ alert.alert_id }}')">×</button>
                            </div>
                            <div class="alert-message">{{ alert.message }}</div>
                            <div class="alert-timestamp">{{ alert.timestamp | format_time }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script src="/static/js/main.js"></script>
    <script src="/static/js/dashboard.js"></script>
    <script src="/static/js/charts.js"></script>
    <script>
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initializeDashboard();
            startAutoRefresh();
        });
    </script>
</body>
</html>
        """
    
    def _get_login_template(self) -> str:
        """Get login HTML template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/auth.css">
</head>
<body class="auth-body">
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1 class="logo">🏈 SportsBet Pro</h1>
                <p class="auth-subtitle">Login to your account</p>
            </div>
            
            <form class="auth-form" id="login-form">
                <div class="form-group">
                    <label for="username">Username or Email</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <div class="form-group" id="totp-group" style="display: none;">
                    <label for="totp-code">Two-Factor Code</label>
                    <input type="text" id="totp-code" name="totp_code" placeholder="Enter 6-digit code">
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Login</button>
                    <a href="/register" class="btn btn-secondary">Create Account</a>
                </div>
            </form>
            
            <div class="auth-footer">
                <a href="/forgot-password">Forgot Password?</a>
            </div>
        </div>
    </div>

    <script src="/static/js/auth.js"></script>
</body>
</html>
        """
    
    def _get_portfolio_card_template(self) -> str:
        """Get portfolio card template"""
        return """
<div class="portfolio-card">
    <div class="card-header">
        <h3>{{ title }}</h3>
        <div class="card-actions">
            <button class="refresh-btn" onclick="refreshPortfolio()">🔄</button>
        </div>
    </div>
    <div class="card-content">
        <div class="metrics-grid">
            <div class="metric">
                <span class="metric-label">Total Value</span>
                <span class="metric-value">{{ total_value | format_currency }}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Profit</span>
                <span class="metric-value {{ 'positive' if total_profit > 0 else 'negative' }}">
                    {{ total_profit | format_currency }}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">ROI</span>
                <span class="metric-value {{ 'positive' if roi_percentage > 0 else 'negative' }}">
                    {{ roi_percentage | format_percentage }}
                </span>
            </div>
            <div class="metric">
                <span class="metric-label">Win Rate</span>
                <span class="metric-value">{{ win_rate | format_percentage }}</span>
            </div>
        </div>
    </div>
</div>
        """
    
    def _get_chart_widget_template(self) -> str:
        """Get chart widget template"""
        return """
<div class="chart-widget">
    <div class="widget-header">
        <h3>{{ title }}</h3>
        <div class="chart-controls">
            <button class="chart-btn" onclick="changeChartType('line')">Line</button>
            <button class="chart-btn" onclick="changeChartType('bar')">Bar</button>
            <button class="chart-btn" onclick="changeChartType('area')">Area</button>
        </div>
    </div>
    <div class="widget-content">
        <canvas id="{{ chart_id }}" width="400" height="200"></canvas>
    </div>
</div>
        """
    
    def _get_opportunities_table_template(self) -> str:
        """Get opportunities table template"""
        return """
<div class="opportunities-table">
    <div class="table-header">
        <h3>{{ title }}</h3>
        <div class="table-controls">
            <select id="sport-filter" onchange="filterOpportunities()">
                <option value="all">All Sports</option>
                <option value="basketball">Basketball</option>
                <option value="football">Football</option>
                <option value="hockey">Hockey</option>
                <option value="baseball">Baseball</option>
            </select>
        </div>
    </div>
    <div class="table-content">
        <table>
            <thead>
                <tr>
                    <th>Match</th>
                    <th>Sport</th>
                    <th>Prediction</th>
                    <th>Confidence</th>
                    <th>Expected ROI</th>
                    <th>Risk</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for opp in opportunities %}
                <tr class="opportunity-row" data-sport="{{ opp.sport }}">
                    <td>{{ opp.home_team }} vs {{ opp.away_team }}</td>
                    <td>{{ opp.sport | title }}</td>
                    <td>{{ opp.prediction | title }}</td>
                    <td>{{ opp.confidence | format_percentage }}</td>
                    <td class="{{ 'positive' if opp.expected_roi > 0 else 'negative' }}">
                        {{ opp.expected_roi | format_percentage }}
                    </td>
                    <td><span class="risk-badge risk-{{ opp.risk_level }}">{{ opp.risk_level | title }}</span></td>
                    <td>
                        <button class="bet-btn" onclick="placeBet('{{ opp.opportunity_id }}')">Place Bet</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
        """
    
    def _get_alerts_panel_template(self) -> str:
        """Get alerts panel template"""
        return """
<div class="alerts-panel">
    <div class="panel-header">
        <h3>{{ title }}</h3>
        <button class="clear-all-btn" onclick="clearAllAlerts()">Clear All</button>
    </div>
    <div class="panel-content">
        <div id="alerts-container">
            {% for alert in alerts %}
            <div class="alert alert-{{ alert.alert_type }}" data-alert-id="{{ alert.alert_id }}">
                <div class="alert-header">
                    <span class="alert-title">{{ alert.title }}</span>
                    <button class="dismiss-btn" onclick="dismissAlert('{{ alert.alert_id }}')">×</button>
                </div>
                <div class="alert-message">{{ alert.message }}</div>
                <div class="alert-timestamp">{{ alert.timestamp | format_time }}</div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
        """
    
    def _get_register_template(self) -> str:
        """Get register template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/auth.css">
</head>
<body class="auth-body">
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1 class="logo">🏈 SportsBet Pro</h1>
                <p class="auth-subtitle">Create your account</p>
            </div>
            
            <form class="auth-form" id="register-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input type="text" id="username" name="username" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">Password</label>
                    <input type="password" id="password" name="password" required>
                    <div class="password-strength" id="password-strength"></div>
                </div>
                
                <div class="form-group">
                    <label for="confirm-password">Confirm Password</label>
                    <input type="password" id="confirm-password" name="confirm_password" required>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Create Account</button>
                    <a href="/login" class="btn btn-secondary">Already have an account?</a>
                </div>
            </form>
        </div>
    </div>

    <script src="/static/js/auth.js"></script>
</body>
</html>
        """
    
    def _get_profile_template(self) -> str:
        """Get profile template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/profile.css">
</head>
<body class="profile-body">
    <header class="profile-header">
        <h1>User Profile</h1>
        <a href="/dashboard" class="back-btn">← Back to Dashboard</a>
    </header>
    
    <main class="profile-main">
        <div class="profile-grid">
            <div class="profile-card">
                <h3>Account Information</h3>
                <form id="profile-form">
                    <div class="form-group">
                        <label for="username">Username</label>
                        <input type="text" id="username" value="{{ user.username }}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" value="{{ user.email }}" readonly>
                    </div>
                    <div class="form-group">
                        <label for="role">Account Type</label>
                        <input type="text" id="role" value="{{ user.role | title }}" readonly>
                    </div>
                </form>
            </div>
            
            <div class="profile-card">
                <h3>Preferences</h3>
                <form id="preferences-form">
                    <div class="form-group">
                        <label for="theme">Theme</label>
                        <select id="theme">
                            <option value="light" {{ 'selected' if preferences.theme == 'light' }}>Light</option>
                            <option value="dark" {{ 'selected' if preferences.theme == 'dark' }}>Dark</option>
                            <option value="auto" {{ 'selected' if preferences.theme == 'auto' }}>Auto</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="default-sport">Default Sport</label>
                        <select id="default-sport">
                            <option value="all" {{ 'selected' if preferences.default_sport == 'all' }}>All Sports</option>
                            <option value="basketball" {{ 'selected' if preferences.default_sport == 'basketball' }}>Basketball</option>
                            <option value="football" {{ 'selected' if preferences.default_sport == 'football' }}>Football</option>
                            <option value="hockey" {{ 'selected' if preferences.default_sport == 'hockey' }}>Hockey</option>
                            <option value="baseball" {{ 'selected' if preferences.default_sport == 'baseball' }}>Baseball</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="notifications" {{ 'checked' if preferences.notifications_enabled }}>
                            Enable Notifications
                        </label>
                    </div>
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="auto-refresh" {{ 'checked' if preferences.auto_refresh }}>
                            Auto Refresh Dashboard
                        </label>
                    </div>
                    <button type="submit" class="btn btn-primary">Save Preferences</button>
                </form>
            </div>
        </div>
    </main>

    <script src="/static/js/profile.js"></script>
</body>
</html>
        """
    
    def _get_admin_template(self) -> str:
        """Get admin template"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/admin.css">
</head>
<body class="admin-body">
    <header class="admin-header">
        <h1>Admin Panel</h1>
        <nav class="admin-nav">
            <a href="#users" class="nav-link active">Users</a>
            <a href="#security" class="nav-link">Security</a>
            <a href="#system" class="nav-link">System</a>
        </nav>
    </header>
    
    <main class="admin-main">
        <div class="admin-content">
            <div id="users-section" class="admin-section active">
                <h2>User Management</h2>
                <div class="admin-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="users-tbody">
                            {% for user in users %}
                            <tr>
                                <td>{{ user.username }}</td>
                                <td>{{ user.email }}</td>
                                <td>{{ user.role | title }}</td>
                                <td>
                                    <span class="status-badge status-{{ 'active' if user.is_active else 'inactive' }}">
                                        {{ 'Active' if user.is_active else 'Inactive' }}
                                    </span>
                                </td>
                                <td>
                                    <button class="btn btn-small" onclick="editUser('{{ user.user_id }}')">Edit</button>
                                    <button class="btn btn-small btn-danger" onclick="blockUser('{{ user.user_id }}')">Block</button>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div id="security-section" class="admin-section">
                <h2>Security Logs</h2>
                <div class="security-logs">
                    <div id="security-events">
                        {% for event in security_events %}
                        <div class="security-event event-{{ event.severity }}">
                            <div class="event-header">
                                <span class="event-type">{{ event.event_type | title }}</span>
                                <span class="event-time">{{ event.timestamp | format_time }}</span>
                            </div>
                            <div class="event-description">{{ event.description }}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </main>

    <script src="/static/js/admin.js"></script>
</body>
</html>
        """
    
    def get_page_template(self, page_id: str) -> Optional[str]:
        """Get page template by ID"""
        if page_id in self.pages:
            page = self.pages[page_id]
            return self.templates.get(page.template)
        return None
    
    def get_component_template(self, component_id: str) -> Optional[str]:
        """Get component template by ID"""
        if component_id in self.components:
            component = self.components[component_id]
            return self.templates.get(component.template)
        return None
    
    def render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Render template with data (simplified template engine)"""
        # Simple template rendering (in production, use a proper template engine)
        rendered = template
        
        # Replace variables
        for key, value in data.items():
            placeholder = f"{{{{ {key} }}}}"
            if isinstance(value, (int, float)):
                rendered = rendered.replace(placeholder, str(value))
            elif isinstance(value, str):
                rendered = rendered.replace(placeholder, value)
            elif isinstance(value, dict):
                # Handle nested dictionaries
                for sub_key, sub_value in value.items():
                    sub_placeholder = f"{{{{ {key}.{sub_key} }}}}"
                    rendered = rendered.replace(sub_placeholder, str(sub_value))
        
        # Handle loops (simplified)
        if "{% for opp in live_opportunities %}" in rendered:
            opportunities = data.get('live_opportunities', [])
            loop_start = "{% for opp in live_opportunities %}"
            loop_end = "{% endfor %}"
            
            start_idx = rendered.find(loop_start)
            end_idx = rendered.find(loop_end)
            
            if start_idx != -1 and end_idx != -1:
                loop_template = rendered[start_idx + len(loop_start):end_idx]
                loop_content = ""
                
                for opp in opportunities:
                    opp_content = loop_template
                    for key, value in opp.items():
                        opp_content = opp_content.replace(f"{{{{ opp.{key} }}}}", str(value))
                    loop_content += opp_content
                
                rendered = rendered[:start_idx] + loop_content + rendered[end_idx + len(loop_end):]
        
        return rendered
    
    def generate_css(self) -> str:
        """Generate CSS styles"""
        return """
/* Main CSS Styles */
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --background-color: #0f172a;
    --surface-color: #1e293b;
    --text-color: #f8fafc;
    --border-color: #334155;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: var(--background-color);
    color: var(--text-color);
    line-height: 1.6;
}

/* Dashboard Styles */
.dashboard-header {
    background-color: var(--surface-color);
    border-bottom: 1px solid var(--border-color);
    padding: 1rem 0;
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1rem;
}

.logo {
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--primary-color);
}

.main-nav {
    display: flex;
    gap: 2rem;
}

.nav-link {
    color: var(--text-color);
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    transition: background-color 0.2s;
}

.nav-link:hover,
.nav-link.active {
    background-color: var(--primary-color);
}

.dashboard-main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 1.5rem;
}

.widget {
    background-color: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: 0.75rem;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.widget-header h3 {
    font-size: 1.125rem;
    font-weight: 600;
}

.portfolio-overview {
    grid-column: span 4;
    grid-row: span 2;
}

.chart-widget {
    grid-column: span 8;
    grid-row: span 4;
}

.opportunities-widget {
    grid-column: span 6;
    grid-row: span 4;
}

.alerts-widget {
    grid-column: span 6;
    grid-row: span 4;
}

/* Metrics */
.metric-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.metric {
    text-align: center;
}

.metric-label {
    display: block;
    font-size: 0.875rem;
    color: var(--secondary-color);
    margin-bottom: 0.25rem;
}

.metric-value {
    display: block;
    font-size: 1.5rem;
    font-weight: bold;
}

.metric-value.positive {
    color: var(--success-color);
}

.metric-value.negative {
    color: var(--error-color);
}

/* Tables */
.opportunities-table {
    width: 100%;
    border-collapse: collapse;
}

.opportunities-table th,
.opportunities-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
}

.opportunities-table th {
    font-weight: 600;
    color: var(--secondary-color);
    font-size: 0.875rem;
}

.risk-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
}

.risk-low {
    background-color: var(--success-color);
    color: white;
}

.risk-medium {
    background-color: var(--warning-color);
    color: white;
}

.risk-high {
    background-color: var(--error-color);
    color: white;
}

.bet-btn {
    background-color: var(--primary-color);
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    cursor: pointer;
    font-size: 0.875rem;
    transition: background-color 0.2s;
}

.bet-btn:hover {
    background-color: #1d4ed8;
}

/* Alerts */
.alert {
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid;
}

.alert-info {
    background-color: rgba(59, 130, 246, 0.1);
    border-left-color: #3b82f6;
}

.alert-success {
    background-color: rgba(16, 185, 129, 0.1);
    border-left-color: #10b981;
}

.alert-warning {
    background-color: rgba(245, 158, 11, 0.1);
    border-left-color: #f59e0b;
}

.alert-error {
    background-color: rgba(239, 68, 68, 0.1);
    border-left-color: #ef4444;
}

.alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.alert-title {
    font-weight: 600;
}

.dismiss-btn {
    background: none;
    border: none;
    color: var(--secondary-color);
    cursor: pointer;
    font-size: 1.25rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .dashboard-grid {
        grid-template-columns: 1fr;
    }
    
    .portfolio-overview,
    .chart-widget,
    .opportunities-widget,
    .alerts-widget {
        grid-column: span 1;
    }
    
    .header-content {
        flex-direction: column;
        gap: 1rem;
    }
    
    .main-nav {
        gap: 1rem;
    }
}
        """

async def main():
    """Test the web UI system"""
    print("🚀 Testing Web UI System - YOLO MODE!")
    print("=" * 70)
    
    # Initialize web UI system
    web_ui = WebUISystem()
    
    try:
        # Test page templates
        print("\n📄 Testing Page Templates:")
        print("-" * 40)
        
        for page_id, page in web_ui.pages.items():
            template = web_ui.get_page_template(page_id)
            if template:
                print(f"✅ {page_id}: Template loaded ({len(template)} characters)")
            else:
                print(f"❌ {page_id}: Template not found")
        
        # Test component templates
        print("\n🧩 Testing Component Templates:")
        print("-" * 40)
        
        for component_id, component in web_ui.components.items():
            template = web_ui.get_component_template(component_id)
            if template:
                print(f"✅ {component_id}: Template loaded ({len(template)} characters)")
            else:
                print(f"❌ {component_id}: Template not found")
        
        # Test template rendering
        print("\n🎨 Testing Template Rendering:")
        print("-" * 40)
        
        sample_data = {
            "title": "Sports Betting Dashboard",
            "user": {"username": "testuser", "role": "premium"},
            "portfolio": {
                "total_value": 1059.05,
                "total_profit": 34.05,
                "roi_percentage": 3.3,
                "win_rate": 62.5
            },
            "live_opportunities": [
                {
                    "opportunity_id": "opp_001",
                    "sport": "basketball",
                    "home_team": "Lakers",
                    "away_team": "Celtics",
                    "prediction": "home",
                    "confidence": 0.75,
                    "expected_roi": 12.5,
                    "risk_level": "medium"
                }
            ],
            "alerts": [
                {
                    "alert_id": "alert_001",
                    "alert_type": "warning",
                    "title": "Low ROI Alert",
                    "message": "Your portfolio ROI is below 5%",
                    "timestamp": "2024-01-10T15:30:00"
                }
            ]
        }
        
        dashboard_template = web_ui.get_page_template("dashboard")
        if dashboard_template:
            rendered = web_ui.render_template(dashboard_template, sample_data)
            print(f"✅ Dashboard template rendered ({len(rendered)} characters)")
            print(f"   Contains 'SportsBet Pro': {'✅' if 'SportsBet Pro' in rendered else '❌'}")
            print(f"   Contains 'Lakers vs Celtics': {'✅' if 'Lakers vs Celtics' in rendered else '❌'}")
            print(f"   Contains 'Low ROI Alert': {'✅' if 'Low ROI Alert' in rendered else '❌'}")
        
        # Test CSS generation
        print("\n🎨 Testing CSS Generation:")
        print("-" * 40)
        
        css = web_ui.generate_css()
        print(f"✅ CSS generated ({len(css)} characters)")
        print(f"   Contains CSS variables: {'✅' if '--primary-color' in css else '❌'}")
        print(f"   Contains responsive design: {'✅' if '@media' in css else '❌'}")
        print(f"   Contains dashboard styles: {'✅' if '.dashboard-grid' in css else '❌'}")
        
        # Show page statistics
        print("\n📊 Web UI Statistics:")
        print("-" * 40)
        print(f"✅ Total Pages: {len(web_ui.pages)}")
        print(f"✅ Total Components: {len(web_ui.components)}")
        print(f"✅ Total Templates: {len(web_ui.templates)}")
        
        # List all pages
        print(f"\n📄 Available Pages:")
        for page_id, page in web_ui.pages.items():
            print(f"   - {page_id}: {page.title}")
        
        # List all components
        print(f"\n🧩 Available Components:")
        for component_id, component in web_ui.components.items():
            print(f"   - {component_id}: {component.component_type}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("🎉 Web UI System Test Completed!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main()) 