# ====================================================================================================
# P06_class_items.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   This is the MAIN APPLICATION window.
#   It is launched by the 'P05' Connection Launcher after successful setup.
#   It receives the live connection objects (Snowflake, GDrive) and
#   contains the actual logic for the project-specific application.
#
#   Each project can modify or extend this file with its own widgets and logic.
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-07
# Project:      GP Boilerplate
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# Add parent directory to sys.path so this module can import other "processes" packages.
# ====================================================================================================
import sys
from pathlib import Path

# --- Standard block for all modules ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True  # Prevents __pycache__ folders from being created


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in standard libraries and settings from the central import hub.
# ====================================================================================================
from processes.P00_set_packages import *  # Imports all packages from P00_set_packages.py