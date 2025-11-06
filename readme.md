🚀 Python GUI Boilerplate (Snowflake & Google Drive)

This project provides a robust, reusable boilerplate for building Python GUI applications that require authentication and connection management for Snowflake (via Okta SSO) and Google Drive (via API or local mapped drive).

It uses a Launcher pattern to handle all authentication up-front, passing live connection objects to the main application for immediate use.

Key Features

Authentication & Connections

Snowflake Connector (P08):

Connects using Okta SSO (externalbrowser).

Automatically finds and sets the best available Role/Warehouse for the user based on a priority list.

Google Drive Connector (P09):

Provides two methods for file operations, selectable in the GUI:

Local Mapped Drive: (Default) Lets the user browse and select their local shared folder (e.g., H:\).

API Method: Connects directly to the Google Drive API.

Launcher GUI (P05):

Dynamically builds email radio buttons from the configuration file (P10).

Uses background threading to ensure the GUI never freezes during network operations.

Configurable (P10):

User-friendly setup: A new user just edits processes/P10_user_config.py to add their team's emails.

Project Structure

GPPythonBoilerplate/
│
├── .venv/                  # Python Virtual Environment
│
├── credentials/            # Google API/OAuth Files
│   └── credentials.json    # Google API Key (Must be added manually)
│
├── main/
│   └── M00_run_setup.gui.py # *** MAIN ENTRY POINT ***
│
└── processes/
    ├── P00_set_packages.py        # Central place for all module imports
    ├── P05_gui_elements.py        # The "Launcher" GUI window
    ├── P06_class_items.py         # The "Main App" window (Placeholder)
    ├── P08_snowflake_connector.py # Snowflake/Okta connection logic
    ├── P09_gdrive_api.py          # Google Drive API connection logic
    └── P10_user_config.py       # User-editable email list


1. Setup & Configuration

Step 1: Install Python Packages

If a requirements.txt file exists, use it:

pip install -r requirements.txt


If not, manually create the list:

pip install pandas snowflake-connector-python google-api-python-client google-auth-httplib2 google-auth-oauthlib


Step 2: Configure User Emails

Open processes/P10_user_config.py.

Fill in your team's common emails in the EMAIL_SLOT variables. Any slot left blank will be ignored by the GUI.

# processes/P10_user_config.py

# --- REQUIRED: Fill in your team's common emails ---
EMAIL_SLOT_1 = "gerry.pidgeon@gopuff.com"
EMAIL_SLOT_2 = "dimitrios.kakkavas@gopuff.com"
# ...


Step 3: (Optional) Google Drive API Credentials

If you plan to use the API method, you need your credentials.

Go to the Google Cloud Console.

Enable the "Google Drive API".

Create an OAuth client ID of type "Desktop app".

Download the JSON file, rename it to credentials.json, and place it in the project's credentials/ folder.

2. How to Run

Navigate to the project's root folder (e.g., GPPythonBoilerplate/).

Activate your virtual environment (e.g., .\.venv\Scripts\Activate.ps1).

Run the main entry point:

python main/M00_run_setup.gui.py


Use the launcher window to set your connections.

3. Building an Executable (.exe)

To create a single executable file for Windows users, use PyInstaller.

Ensure PyInstaller is installed (pip install pyinstaller).

Run the following command from the root directory:

pyinstaller --onefile --name "GopuffApp" --add-data "credentials;credentials" main/M00_run_setup.gui.py


Your final GopuffApp.exe file will be in the new dist/ folder.
