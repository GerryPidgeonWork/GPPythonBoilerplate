# ====================================================================================================
# P01_set_file_paths.py
# ----------------------------------------------------------------------------------------------------
# Centralises all key file and directory paths for the project.
#
# Purpose:
#   - Define a single source of truth for the project's root directory (static paths).
#   - Build paths for data, credentials, and other key resources.
#   - **NEW**: Provide a function to dynamically generate export paths based on user input.
#
# Usage:
#   from processes.P01_set_file_paths import PROJECT_ROOT, get_provider_paths
#
# Example:
#   >>> paths = get_provider_paths("/Users/Shared/Orders to Cash")
#   >>> print(paths['braintree'])
#   /Users/Shared/Orders to Cash/01 Braintree/03 DWH
#
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-05
# Project:      Just Eat Orders-to-Cash Reconciliation
# ====================================================================================================


# ====================================================================================================
# 1. SYSTEM IMPORTS
# ----------------------------------------------------------------------------------------------------
# Add parent directory to sys.path so this module can import other "processes" packages.
# ====================================================================================================
import sys
from pathlib import Path
from typing import Dict # Explicitly imported for the function type hint

# --- Standard block for all modules ---
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True  # Prevents __pycache__ folders from being created


# ====================================================================================================
# 2. PROJECT IMPORTS
# ----------------------------------------------------------------------------------------------------
# Bring in standard libraries and settings from the central import hub.
# ====================================================================================================
from processes.P00_set_packages import * # Imports all packages from P00_set_packages.py


# ====================================================================================================
# 3. PROJECT ROOT (Static, Internal Paths)
# ----------------------------------------------------------------------------------------------------
# This block defines the 'PROJECT_ROOT' variable for this module and for
# any other module that needs to import it (e.g., P02, P09).
# ====================================================================================================
try:
    # .parent is /.../Just-Eat-Project/processes/
    # .parent.parent is /.../Just-Eat-Project/
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
except NameError:
    # Fallback for interactive environments where __file__ isn't defined
    PROJECT_ROOT = Path.cwd()


# ====================================================================================================
# 4. CORE DIRECTORIES (Static, Internal Paths)
# ----------------------------------------------------------------------------------------------------
PROCESSES_DIR = PROJECT_ROOT / "processes"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
CREDENTIALS_DIR = PROJECT_ROOT / "credentials"  # A dedicated folder is safer

# --- Ensure key directories exist ---
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)

# ====================================================================================================
# 5. GOOGLE DRIVE API FILES (Static, Internal Paths)
# ----------------------------------------------------------------------------------------------------
# Paths for the Google Drive API credentials.
# P09_gdrive_api.py will look for these files here.
# ====================================================================================================
GDRIVE_CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
GDRIVE_TOKEN_FILE = CREDENTIALS_DIR / "token.json"


# ====================================================================================================
# 6. DYNAMIC EXPORT PATH GENERATOR (New Logic)
# ----------------------------------------------------------------------------------------------------

# This dictionary defines the fixed sub-structure for the DWH exports.
# The `get_provider_paths` function will prepend the user's root path to these.
PROVIDER_SUBPATHS = {
    'braintree': Path('01 Braintree') / '03 DWH',
    'paypal':    Path('02 Paypal')    / '03 DWH',
    'uber':      Path('03 Uber Eats') / '03 DWH',
    'deliveroo': Path('04 Deliveroo') / '03 DWH',
    'justeat':   Path('05 Just Eat')  / '03 DWH',
    'amazon':    Path('06 Amazon')    / '03 DWH',
}

def get_provider_paths(root_path_str: str) -> Dict[str, Path]:
    """
    Constructs the absolute file path objects for each provider's DWH export folder.
    
    This function is used when the user selects the 'Local Mapped Drive' method 
    in the GUI.

    Args:
        root_path_str (str): The string path to the base 'Orders to Cash' folder,
                             provided by the user via the GUI (e.g., 'H:/Shared drives/...')

    Returns:
        Dict[str, Path]: A dictionary where keys are provider names (lowercase) 
                         and values are pathlib.Path objects pointing to the 
                         provider's final export directory.
    """
    # Convert the user-provided string path (from GUI) into a pathlib.Path object.
    root_path = Path(root_path_str)

    # Derive the full path for each provider using the fixed sub-structure.
    provider_paths = {
        name: root_path / subpath
        for name, subpath in PROVIDER_SUBPATHS.items()
    }

    return provider_paths


# ====================================================================================================
# 7. MAIN EXECUTION (STANDALONE TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Processes Dir: {PROCESSES_DIR}")
    print(f"Data Dir: {DATA_DIR}")
    print(f"Logs Dir: {LOGS_DIR}")
    print(f"Credentials Dir: {CREDENTIALS_DIR}")
    print(f"G-Drive Credentials: {GDRIVE_CREDENTIALS_FILE}")
    print(f"G-Drive Token: {GDRIVE_TOKEN_FILE}")
    
    # Test the new dynamic function with a dummy path
    dummy_path = r"C:\Temp\Orders to Cash"
    test_paths = get_provider_paths(dummy_path)
    print("\n--- Dynamic Path Test ---")
    print(f"Braintree Path: {test_paths['braintree']}")
    print(f"Deliveroo Path: {test_paths['deliveroo']}")