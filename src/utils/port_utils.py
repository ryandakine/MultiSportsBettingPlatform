#!/usr/bin/env python3
"""
Port utility functions for MultiSportsBettingPlatform
"""

import socket
import os
import json
from typing import Optional, Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def load_port_config(config_file: str = "project_ports.json") -> Dict[str, Any]:
    """
    Load port configuration from JSON file.
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Configuration dictionary or empty dict if file not found
    """
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            logger.warning(f"Port configuration file {config_file} not found")
            return {}
    except Exception as e:
        logger.error(f"Error loading port configuration: {e}")
        return {}

def get_project_port_config(project_name: str = "MultiSportsBettingPlatform") -> Dict[str, Any]:
    """
    Get port configuration for a specific project.
    
    Args:
        project_name: Name of the project
        
    Returns:
        Project port configuration
    """
    config = load_port_config()
    project_configs = config.get("project_ports", {})
    return project_configs.get(project_name, {})

def is_port_available(port: int, host: str = "localhost") -> bool:
    """
    Check if a port is available for binding.
    
    Args:
        port: Port number to check
        host: Host to check (default: localhost)
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except Exception as e:
        logger.warning(f"Error checking port {port}: {e}")
        return False

def find_available_port(
    start_port: int = 8000, 
    max_attempts: int = 100, 
    host: str = "localhost",
    exclude_ports: Optional[List[int]] = None
) -> Optional[int]:
    """
    Find an available port starting from start_port.
    
    Args:
        start_port: Starting port number
        max_attempts: Maximum number of ports to try
        host: Host to check
        exclude_ports: List of ports to exclude from search
        
    Returns:
        Available port number or None if none found
    """
    if exclude_ports is None:
        exclude_ports = []
    
    # Load reserved ports from config
    config = load_port_config()
    reserved_ports = config.get("reserved_ports", [])
    exclude_ports.extend(reserved_ports)
    
    for port in range(start_port, start_port + max_attempts):
        if port in exclude_ports:
            continue
        if is_port_available(port, host):
            return port
    
    return None

def get_port_range(start_port: int = 8000, count: int = 10) -> List[int]:
    """
    Get a range of available ports.
    
    Args:
        start_port: Starting port number
        count: Number of ports to find
        
    Returns:
        List of available port numbers
    """
    ports = []
    current_port = start_port
    
    while len(ports) < count:
        available_port = find_available_port(current_port, max_attempts=50)
        if available_port is None:
            break
        ports.append(available_port)
        current_port = available_port + 1
    
    return ports

def validate_port_config(host: str, port: int) -> Tuple[bool, str]:
    """
    Validate host and port configuration.
    
    Args:
        host: Host address
        port: Port number
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not (1 <= port <= 65535):
        return False, f"Port {port} is out of valid range (1-65535)"
    
    if host not in ["0.0.0.0", "localhost", "127.0.0.1"]:
        # For now, only allow common localhost variants
        return False, f"Host {host} is not in allowed list"
    
    return True, ""

def get_server_config(
    project_name: str = "MultiSportsBettingPlatform",
    default_host: str = "0.0.0.0",
    default_port: int = 8000,
    env_host_key: str = "HOST",
    env_port_key: str = "PORT"
) -> Tuple[Optional[str], Optional[int]]:
    """
    Get server configuration with dynamic port finding.
    
    Args:
        project_name: Name of the project for configuration lookup
        default_host: Default host if not specified in environment
        default_port: Default port if not specified in environment
        env_host_key: Environment variable key for host
        env_port_key: Environment variable key for port
        
    Returns:
        Tuple of (host, port) or (None, None) if configuration failed
    """
    host = os.getenv(env_host_key, default_host)
    preferred_port = int(os.getenv(env_port_key, str(default_port)))
    
    # Try to get project-specific configuration
    project_config = get_project_port_config(project_name)
    if project_config:
        preferred_port = project_config.get("preferred_port", preferred_port)
        logger.info(f"Using project configuration for {project_name}")
    
    # Validate configuration
    is_valid, error_msg = validate_port_config(host, preferred_port)
    if not is_valid:
        logger.error(f"Invalid configuration: {error_msg}")
        return None, None
    
    # Check if preferred port is available
    if is_port_available(preferred_port, "localhost"):
        port = preferred_port
        logger.info(f"Using preferred port {port}")
    else:
        logger.warning(f"Port {preferred_port} is in use, searching for available port...")
        
        # Use project-specific fallback range if available
        fallback_range = project_config.get("fallback_range", [preferred_port + 1, preferred_port + 100])
        start_port = fallback_range[0] if isinstance(fallback_range, list) else preferred_port + 1
        
        port = find_available_port(start_port)
        
        if port is None:
            logger.error(f"Could not find available port in range {start_port}-{start_port + 100}")
            return None, None
        else:
            logger.info(f"Found available port: {port}")
    
    return host, port

def check_service_health(host: str, port: int, timeout: int = 5) -> bool:
    """
    Check if a service is healthy by attempting to connect.
    
    Args:
        host: Service host
        port: Service port
        timeout: Connection timeout in seconds
        
    Returns:
        True if service is healthy, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            return result == 0  # Service is healthy if connection succeeds
    except Exception as e:
        logger.warning(f"Health check failed for {host}:{port}: {e}")
        return False

def get_multi_project_ports(project_names: List[str]) -> Dict[str, int]:
    """
    Get available ports for multiple projects.
    
    Args:
        project_names: List of project names
        
    Returns:
        Dictionary mapping project names to available ports
    """
    project_ports = {}
    used_ports = []
    
    for project_name in project_names:
        project_config = get_project_port_config(project_name)
        preferred_port = project_config.get("preferred_port", 8000)
        
        # Find available port for this project
        available_port = find_available_port(preferred_port, exclude_ports=used_ports)
        if available_port:
            project_ports[project_name] = available_port
            used_ports.append(available_port)
            logger.info(f"Assigned port {available_port} to {project_name}")
        else:
            logger.error(f"Could not find available port for {project_name}")
    
    return project_ports 