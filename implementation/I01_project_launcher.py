# ====================================================================================================
# I01_project_launcher.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   Acts as the project-level bridge between the locked boilerplate (P05a / M01)
#   and the project-specific logic (e.g. GUI, ETL, data processing, etc.).
#
# How it fits:
#   - Called by M01_load_project_config.launch_project_main()
#   - You can override this file per project without ever touching the core boilerplate.
#
# Typical use cases:
#   - Launching a project-specific GUI (e.g., I02_gui_elements_main.MainProjectGUI)
#   - Running a standalone ETL or processing pipeline
#   - Switching dynamically between multiple app entry points
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-07
# Project:      GP Boilerplate (Generic Project Launcher)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True  # Prevents __pycache__ creation


# ====================================================================================================
# 2. MAIN LAUNCH FUNCTION
# ----------------------------------------------------------------------------------------------------
def launch_main_app(parent, snowflake_conn, gdrive_service, upload_method, local_path):
    """
    Called automatically by M01_load_project_config after all connections and
    file paths are ready.

    Parameters:
        parent          (tk.Tk)     : The launcher window instance (P05a)
        snowflake_conn  (object)    : Active Snowflake connection (or None)
        gdrive_service  (object)    : Google Drive API service (or None)
        upload_method   (str)       : 'local' or 'api'
        local_path      (str | Path): Selected Google Drive root or mapped folder

    Returns:
        main_app (object): The project’s main GUI or controller instance.
    """
    # =====================================================================
    # Import the project-specific GUI entry point
    # =====================================================================
    try:
        from implementation.I02_gui_elements_main import MainProjectGUI
    except ImportError as e:
        raise ImportError(
            "❌ Could not import project GUI (I02_gui_elements_main.py).\n"
            "Ensure your project defines a MainProjectGUI class."
        ) from e

    # =====================================================================
    # Instantiate and launch the project GUI
    # =====================================================================
    main_app = MainProjectGUI(
        parent=parent,
        snowflake_conn=snowflake_conn,
        gdrive_service=gdrive_service,
        upload_method=upload_method,
        local_path=local_path,
    )

    print("✅ [I01] Project main GUI launched successfully.")
    return main_app


# ====================================================================================================
# END OF FILE — SAFE TO EDIT (PROJECT-SPECIFIC)
# ====================================================================================================
