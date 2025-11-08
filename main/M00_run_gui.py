# ====================================================================================================
# M00_run_setup.gui.py
# ----------------------------------------------------------------------------------------------------
# *** MAIN APPLICATION ENTRY POINT ***
#
# Purpose:
#   - Entry point for the whole application.
#   - Adds the project root to sys.path so locked /processes modules can be imported.
#   - Starts the universal launcher (P05a) and provides it with a project callback.
#   - The launcher (P05a) handles connections, then automatically triggers the
#     project launch chain:
#         P05a → M01_load_project_config → implementation/I01_project_launcher → I02_gui...
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-06
# Project:      Python Boilerplate
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

# Add project root (…/project/) to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from processes.P00_set_packages import *                      # Common imports (tkinter, ttk, etc.)
from processes.P05a_gui_elements_setup import ConnectionLauncher
from main.M01_load_project_config import launch_project_main   # <- Passed as callback into P05a


# ====================================================================================================
# 3. MAIN EXECUTION
# ----------------------------------------------------------------------------------------------------
def main():
    """Main entry function for launching the universal setup GUI."""
    print("✅ Starting application...")

    # 1️⃣ Create and show the launcher, passing the project callback
    #     When the user clicks "Finish & Launch App", the launcher will call:
    #     → launch_project_main(parent, snowflake_conn, gdrive_service, upload_method, local_path)
    launcher = ConnectionLauncher(on_launch_callback=launch_project_main)
    launcher.mainloop()

    # 2️⃣ After main window closes
    print("🟡 Application closed.")


if __name__ == "__main__":
    main()
