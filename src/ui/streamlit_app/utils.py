"""
Utility functions for Streamlit app
"""
import os
import sys
from pathlib import Path

def setup_project_path():
    """Setup project path and load environment variables"""
    # Find project root by looking for .env file or requirements.txt
    # This function can be called from different locations (main.py, pages/, etc.)
    current_file = Path(__file__).resolve()
    
    # Try different parent levels to find project root
    project_root = None
    for level in range(1, 7):
        candidate = current_file.parents[level]
        # Check for project root markers
        if (candidate / ".env").exists() or (candidate / "requirements.txt").exists():
            project_root = candidate
            break
        # Also check for src/ and Data/ directories
        if (candidate / "src").exists() and (candidate / "Data").exists():
            project_root = candidate
            break
    
    # Fallback: use current working directory
    if project_root is None:
        cwd = Path.cwd()
        if (cwd / ".env").exists() or (cwd / "requirements.txt").exists():
            project_root = cwd
        elif (cwd / "src").exists():
            project_root = cwd
        else:
            # Last resort: calculate from current file location
            # utils.py is in src/ui/streamlit_app/, so go up 3 levels
            project_root = current_file.parents[3]
    
    # Add to sys.path if not already there
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(project_root / ".env")
    except ImportError:
        pass  # dotenv not available, skip
    
    return project_root

