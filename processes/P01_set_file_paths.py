# ====================================================================================================
# P01_set_file_paths.py
# ----------------------------------------------------------------------------------------------------
# Centralises all key file and directory paths for the project.
#
# Purpose:
#   - Define a single source of truth for the project's root directory.
#   - Build paths for data, credentials, and other key resources.
#   - Allow other modules to import paths without hardcoding.
#
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
from processes.P00_set_packages import * # Imports all packages from P00_set_packages.py


# ====================================================================================================
# 3. PROJECT ROOT
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
# 4. CORE DIRECTORIES
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
# 5. GOOGLE DRIVE API FILES
# ----------------------------------------------------------------------------------------------------
# Paths for the Google Drive API credentials.
# P09_gdrive_api.py will look for these files here.
# ====================================================================================================
GDRIVE_CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
GDRIVE_TOKEN_FILE = CREDENTIALS_DIR / "token.json"

# ====================================================================================================
# 6. PROVIDER FOLDER STRUCTURE & REGISTRY
# ----------------------------------------------------------------------------------------------------
# Centralises all provider-level folder paths used across the project.
#
# Each provider has the same internal layout:
#
# ├── 01 CSVs
# │   ├── 01 To Process
# │   ├── 02 Processed
# │   └── 03 Reference
# ├── 02 PDFs
# │   ├── 01 To Process
# │   └── 02 Processed
# ├── 03 DWH
# └── 04 Consolidated Output
#     └── 01 Refund Data
#
# The Initial GUI (P05a) sets the `SHARED_DRIVE_ROOT` dynamically, ensuring all
# paths adapt automatically to the user's mapped Google Drive or local folder.
# ====================================================================================================

# --- 6a. Company Shared Root (fixed structure beyond drive letter) ---
PROJECT_SHARED_ROOT_DIR = (
    Path("Shared drives") / "Automation Projects" / "Accounting" / "Orders to Cash"
)

# --- 6b. Provider Registry (master list) ---
# Defines all supported providers and their numbered subfolders.
PROVIDER_SUBPATHS = {
    "braintree": "01 Braintree",
    "paypal":    "02 Paypal",
    "uber":      "03 Uber Eats",
    "deliveroo": "04 Deliveroo",
    "justeat":   "05 Just Eat",
    "amazon":    "06 Amazon",
}

# --- 6c. Standard Internal Folder Layout ---
PROVIDER_STRUCTURE = {
    "01 CSVs": [
        "01 To Process",
        "02 Processed",
        "03 Reference"
    ],
    "02 PDFs": [
        "01 To Process",
        "02 Processed"
    ],
    "03 DWH": [],
    "04 Consolidated Output": [
        "01 Refund Data"
    ],
}

# --- 6d. Root Path Placeholder (set dynamically by GUI) ---
SHARED_DRIVE_ROOT: Path | None = None


# --- 6e. Folder Builder Function ---
def build_provider_paths(shared_root: Path, provider_key: str) -> Dict[str, Path]:
    """
    Builds and returns a complete folder dictionary for a specific provider.

    Parameters:
        shared_root (Path): Base shared drive path (e.g., 'H:\\').
        provider_key (str): Short provider key (e.g., 'deliveroo').

    Returns:
        Dict[str, Path]: Dictionary mapping logical names to Path objects.
    """
    if provider_key not in PROVIDER_SUBPATHS:
        raise ValueError(f"Unknown provider key: {provider_key}")

    provider_root = shared_root / PROJECT_SHARED_ROOT_DIR / PROVIDER_SUBPATHS[provider_key]
    all_paths = {"root": provider_root}

    # Build full subfolder tree dynamically
    for top_folder, subfolders in PROVIDER_STRUCTURE.items():
        top_path = provider_root / top_folder
        key_base = top_folder.lower().replace(" ", "_")
        all_paths[key_base] = top_path

        for sub in subfolders:
            sub_path = top_path / sub
            sub_key = f"{key_base}_{sub.lower().replace(' ', '_')}"
            all_paths[sub_key] = sub_path

    return all_paths

# --- 6f. Master Dictionary for All Providers ---
# This dictionary will be rebuilt dynamically once the GUI sets SHARED_DRIVE_ROOT.
ALL_PROVIDER_PATHS: Dict[str, Dict[str, Path]] = {}

# --- 6g. Named Shortcuts (initialized empty; populated after GUI) ---
braintree_paths: Dict[str, Path] = {}
paypal_paths: Dict[str, Path]    = {}
uber_paths: Dict[str, Path]      = {}
deliveroo_paths: Dict[str, Path] = {}
justeat_paths: Dict[str, Path]   = {}
amazon_paths: Dict[str, Path]    = {}


# --- 6h. Initialisation Helper ---
def initialise_provider_paths(selected_root: str | Path | None = None) -> Dict[str, Dict[str, Path]]:
    """
    Initializes all provider folder dictionaries.

    Parameters:
        selected_root (str | Path | None): The base shared drive root (e.g. 'H:/')

    Returns:
        Dict[str, Dict[str, Path]]: Master dictionary containing all provider path maps.
    """
    global SHARED_DRIVE_ROOT, ALL_PROVIDER_PATHS
    global braintree_paths, paypal_paths, uber_paths, deliveroo_paths, justeat_paths, amazon_paths

    if not selected_root:
        SHARED_DRIVE_ROOT = Path("<Drive not yet selected>")
        print("⚠️  No drive selected — paths will show placeholder text until GUI sets the drive.")
    else:
        selected_path = Path(selected_root).resolve()

        # ✅ Normalise if user selected 'H:\\Shared drives' or deeper
        if selected_path.parts[-1].lower() == "shared drives":
            shared_drive_root = selected_path.drive + "\\"
        elif any(p.lower() == "shared drives" for p in selected_path.parts):
            shared_drive_root = selected_path.drive + "\\"
        else:
            shared_drive_root = str(selected_path)

        SHARED_DRIVE_ROOT = Path(shared_drive_root)
        if not SHARED_DRIVE_ROOT.exists():
            print(f"⚠️  Warning: {shared_drive_root} does not exist. Using placeholder paths.")
        else:
            print(f"✅ Normalized shared drive root: {SHARED_DRIVE_ROOT}")

    # --- Build full provider dictionary ---
    ALL_PROVIDER_PATHS = {
        key: build_provider_paths(SHARED_DRIVE_ROOT, key)
        for key in PROVIDER_SUBPATHS.keys()
    }

    # --- Create shorthand references (legacy compatibility) ---
    braintree_paths = ALL_PROVIDER_PATHS.get("braintree", {})
    paypal_paths    = ALL_PROVIDER_PATHS.get("paypal", {})
    uber_paths      = ALL_PROVIDER_PATHS.get("uber", {})
    deliveroo_paths = ALL_PROVIDER_PATHS.get("deliveroo", {})
    justeat_paths   = ALL_PROVIDER_PATHS.get("justeat", {})
    amazon_paths    = ALL_PROVIDER_PATHS.get("amazon", {})

    # ✅ Return for functional usage
    return ALL_PROVIDER_PATHS


# ====================================================================================================
# 7. HELPER FUNCTIONS
# ----------------------------------------------------------------------------------------------------
def get_provider_paths(provider_key: str) -> Dict[str, Path]:
    """
    Returns the full folder dictionary for a single provider.

    Example:
        >>> get_provider_paths("justeat")["02_pdfs_01_to_process"]
    """
    if provider_key not in ALL_PROVIDER_PATHS:
        raise KeyError(f"Provider '{provider_key}' not initialized.")
    return ALL_PROVIDER_PATHS[provider_key]


def get_folder_across_providers(folder_key: str) -> Dict[str, Path]:
    """
    Returns a dictionary of the same folder (e.g., '03_dwh') across all providers.

    Example:
        >>> get_folder_across_providers("03_dwh")
        {
            'braintree': Path('H:/.../01 Braintree/03 DWH'),
            'paypal':    Path('H:/.../02 Paypal/03 DWH'),
            ...
        }
    """
    if not ALL_PROVIDER_PATHS:
        raise RuntimeError("Provider paths not initialized. Call initialise_provider_paths() first.")

    results = {}
    for provider, paths in ALL_PROVIDER_PATHS.items():
        if folder_key in paths:
            results[provider] = paths[folder_key]
    return results

# ====================================================================================================
# 8. MAIN EXECUTION (STANDALONE TEST)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"Project Root: {PROJECT_ROOT}")
    print("\n--- Dynamic Path Test (H:/) ---")

    all_paths = initialise_provider_paths("H:/")

    print("\n✅ Available providers:", list(all_paths.keys()))
    print("\nSample provider map (Deliveroo):")
    for key, path in all_paths["deliveroo"].items():
        print(f"{key.ljust(35)} : {path}")

    print("\nSample cross-provider folder (03 DWH):")
    for prov, path in get_folder_across_providers("03_dwh").items():
        print(f"{prov.ljust(15)} : {path}")
