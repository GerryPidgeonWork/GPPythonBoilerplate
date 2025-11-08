# ====================================================================================================
# M01_load_project_config.py
# ----------------------------------------------------------------------------------------------------
# Loads project-specific runtime configuration.
#   - Selects active provider (e.g., 'justeat', 'uber', etc.)
#   - Defines shared drive root (e.g., H:\)
#   - Initializes provider folder dictionaries from P01
#
# Each new project can have its own version of this file — or override
# just the relevant constants and imports.
# ----------------------------------------------------------------------------------------------------
# Author:         Gerry Pidgeon
# Created:        2025-11-07
# Project:        GP Boilerplate (Generic Project Config Loader)
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
from processes.P00_set_packages import *          # (tkinter, ttk, threading, etc.)
from processes.P01_set_file_paths import initialise_provider_paths, ALL_PROVIDER_PATHS


# ====================================================================================================
# 3. PROJECT SELECTION
# ----------------------------------------------------------------------------------------------------
# Define which project and provider are currently active.
# Each project can update these two constants.
# ----------------------------------------------------------------------------------------------------
ACTIVE_PROJECT = "Generic Orders-to-Cash Project"
ACTIVE_PROVIDER_KEY = "justeat"   # 🔧 Change this per project


# ====================================================================================================
# 4. DRIVE / ROOT SELECTION
# ----------------------------------------------------------------------------------------------------
# Default shared drive root (this may be overridden by P05a GUI at runtime)
# ----------------------------------------------------------------------------------------------------
SHARED_DRIVE_ROOT = Path("H:/")

# Initialize all provider paths using the shared root
all_paths = initialise_provider_paths(SHARED_DRIVE_ROOT)
provider_paths = all_paths[ACTIVE_PROVIDER_KEY]


# ====================================================================================================
# 5. PROVIDER PATH COMBINATIONS (REFERENCE)
# ----------------------------------------------------------------------------------------------------
# Each provider (Just Eat, Uber, Deliveroo, etc.) uses the same internal structure:
#
#   Provider Root (e.g. "05 Just Eat")
#   ├── 01 CSVs
#   │   ├── 01 To Process
#   │   ├── 02 Processed
#   │   └── 03 Reference
#   ├── 02 PDFs
#   │   ├── 01 To Process
#   │   └── 02 Processed
#   ├── 03 DWH
#   └── 04 Consolidated Output
#       └── 01 Refund Data
# ----------------------------------------------------------------------------------------------------


# ====================================================================================================
# 6. PROJECT-SPECIFIC SHORTCUTS
# ----------------------------------------------------------------------------------------------------
RAW_PDF_FOLDER       = provider_paths["02_pdfs_01_to_process"]
PROCESSED_PDF_FOLDER = provider_paths["02_pdfs_02_processed"]
RAW_CSV_FOLDER       = provider_paths["01_csvs_01_to_process"]
PROCESSED_CSV_FOLDER = provider_paths["01_csvs_02_processed"]
REFERENCE_CSV_FOLDER = provider_paths["01_csvs_03_reference"]
DWH_FOLDER           = provider_paths["03_dwh"]
OUTPUT_FOLDER        = provider_paths["04_consolidated_output"]
REFUND_DATA_FOLDER   = provider_paths["04_consolidated_output_01_refund_data"]


# ====================================================================================================
# 7. DEBUG / VALIDATION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Loaded project:   {ACTIVE_PROJECT}")
    print(f"Active provider:  {ACTIVE_PROVIDER_KEY}")
    print(f"Shared root:      {SHARED_DRIVE_ROOT}")
    print("\n✅ Available providers:", list(all_paths.keys()))

    print("\nResolved folder map for this provider:\n")
    for k, v in provider_paths.items():
        print(f"{k.ljust(40)} : {v}")

    # Optional: show all DWH folders across all providers
    from processes.P01_set_file_paths import get_folder_across_providers
    print("\nCross-provider check (03_dwh):")
    for prov, path in get_folder_across_providers("03_dwh").items():
        print(f"{prov.ljust(15)} : {path}")


# ====================================================================================================
# 8. PROJECT INITIALISER (CALLED BY P05a)
# ----------------------------------------------------------------------------------------------------
def initialise_project_paths(selected_drive: str | Path):
    """
    Called by P05a (the launcher GUI) after user selects the shared drive.
    Returns the provider_paths dictionary for the active project.
    """
    all_paths = initialise_provider_paths(selected_drive)
    provider_paths = all_paths[ACTIVE_PROVIDER_KEY]
    return provider_paths


# ====================================================================================================
# 9. PROJECT MAIN LAUNCHER (CALLED BY P05a)
# ----------------------------------------------------------------------------------------------------
def launch_project_main(parent, snowflake_conn, gdrive_service, upload_method, local_path):
    """
    Called by P05a after all connections and paths are ready.
    Delegates to the project-level launcher (I01_project_launcher.py),
    which decides how to start the main application or process.
    """
    from implementation.I01_project_launcher import launch_main_app

    main_app = launch_main_app(
        parent=parent,
        snowflake_conn=snowflake_conn,
        gdrive_service=gdrive_service,
        upload_method=upload_method,
        local_path=local_path
    )

    print(f"✅ [M01] Project main launched successfully for provider: {ACTIVE_PROVIDER_KEY}")
    return main_app


# ====================================================================================================
# END OF FILE — SAFE TO EDIT (PROJECT-SPECIFIC)
# ====================================================================================================