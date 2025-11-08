# ====================================================================================================
# I02_gui_elements_main.py
# ----------------------------------------------------------------------------------------------------
# Generic project-specific GUI placeholder.
#
# Purpose:
#   - Provides the initial project GUI template.
#   - Inherits from the locked BaseMainGUI (P05b).
#   - Receives active Snowflake connection and Google Drive path/service.
#   - Intended to be replaced or extended by project developers.
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-07
# Project:      GP Boilerplate
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True  # Prevents __pycache__ folders from being created


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from processes.P00_set_packages import *
from processes.P05b_gui_elements_main import BaseMainGUI


# ====================================================================================================
# 3. MAIN PROJECT GUI CLASS
# ----------------------------------------------------------------------------------------------------
class MainProjectGUI(BaseMainGUI):
    """
    Generic placeholder for the project's main GUI window.
    Inherit from this class or replace it with a custom implementation.
    """

    def build_gui(self):
        """Override of BaseMainGUI.build_gui(). Creates a placeholder interface."""
        ttk.Label(
            self.main_frame,
            text="✅ Setup Complete",
            font=("Arial", 14, "bold")
        ).pack(pady=10)

        ttk.Label(
            self.main_frame,
            text="This is the placeholder project GUI.",
            font=("Arial", 10, "italic")
        ).pack(pady=5)

        ttk.Label(
            self.main_frame,
            text=f"Upload Method: {self.upload_method}",
            font=("Arial", 10)
        ).pack(pady=2)

        ttk.Label(
            self.main_frame,
            text=f"Local Path: {self.local_path}",
            font=("Arial", 9, "italic")
        ).pack(pady=2)

        # --- Connection status ---
        sf_status = "Connected" if self.snowflake_conn else "Not Connected"
        gdrive_status = "Connected" if self.gdrive_service else "Not Connected"

        ttk.Label(
            self.main_frame,
            text=f"Snowflake: {sf_status}",
            foreground=("green" if self.snowflake_conn else "red")
        ).pack(pady=2)

        ttk.Label(
            self.main_frame,
            text=f"Google Drive: {gdrive_status}",
            foreground=("green" if self.gdrive_service else "red")
        ).pack(pady=2)


# ====================================================================================================
# END OF FILE — SAFE TO EXTEND OR REPLACE (PROJECT-SPECIFIC)
# ====================================================================================================
