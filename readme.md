# 🚀 Python GUI Boilerplate (Snowflake & Google Drive)

A **modern, reusable Python GUI boilerplate** for applications that require authentication and connection management for **Snowflake** (via Okta SSO) and **Google Drive** (via API or local mapped drive).

This framework uses a **Launcher pattern** to handle authentication up-front, passing live connection objects to the main app for immediate use — making it ideal for data, finance, or automation tools.

---

## 🌟 Key Features

### 🔐 Authentication & Connections

**Snowflake Connector (P08)**

* Connects securely using **Okta SSO (externalbrowser)**.
* Automatically selects the best Role/Warehouse based on a configurable priority list.

**Google Drive Connector (P09)**

* Two file access modes available:

  * **Local Mapped Drive (Default):** Browse your shared folder (e.g., `H:\`).
  * **API Method:** Directly connects via the Google Drive API.

**Launcher GUI (P05)**

* Dynamically builds email selection radio buttons from config.
* Uses **threading** to prevent GUI freezing during authentication.

**Configurable (P10)**

* Simple onboarding — just edit `processes/P10_user_config.py` to add your team’s emails.

---

## 🧩 Project Structure

```
GPPythonBoilerplate/
│
├── .venv/                        # Python Virtual Environment
│
├── credentials/                  # Google API / OAuth Credentials
│   └── credentials.json          # (User-supplied API key)
│
├── main/
│   └── M00_run_setup.gui.py      # 🚀 MAIN ENTRY POINT
│
└── processes/
    ├── P00_set_packages.py        # Central import hub (all modules)
    ├── P05_gui_elements.py        # Launcher GUI window
    ├── P06_class_items.py         # Main App window (placeholder)
    ├── P08_snowflake_connector.py # Snowflake / Okta connection logic
    ├── P09_gdrive_api.py          # Google Drive API connection logic
    └── P10_user_config.py         # User-editable email configuration
```

---

## ⚙️ Setup & Configuration

### 🧰 Step 1 – Install Python Packages

If a `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas snowflake-connector-python google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

### 📧 Step 2 – Configure User Emails

Edit the config file `processes/P10_user_config.py` and add your team’s common emails:

```python
# --- REQUIRED: Fill in your team's common emails ---
EMAIL_SLOT_1 = "firstname.lastname@gopuff.com"
EMAIL_SLOT_2 = ""
# ...
```

Any blank slot will be ignored by the launcher.

---

### 🔑 Step 3 – (Optional) Google Drive API Credentials

To use the **API method** instead of a mapped drive:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Google Drive API**
3. Create an **OAuth client ID** (type: *Desktop app*)
4. Download the credentials JSON file
5. Rename it to `credentials.json` and place it in the `credentials/` folder

---

## ▶️ How to Run

1. Open a terminal in the project root (e.g., `GPPythonBoilerplate/`)
2. Activate your virtual environment:

   ```bash
   .\.venv\Scripts\Activate.ps1
   ```
3. Launch the main app:

   ```bash
   python main/M00_run_setup.gui.py
   ```

The **Launcher Window** will open — use it to authenticate to Snowflake and/or Google Drive.

---

## 🏗️ Building a Windows Executable (.exe)

To distribute the app as a single `.exe` file:

1. Install PyInstaller:

   ```bash
   pip install pyinstaller
   ```
2. Run the build command:

   ```bash
   pyinstaller --onefile --name "GopuffApp" --add-data "credentials;credentials" main/M00_run_setup.gui.py
   ```

Your compiled app will be created in the `/dist` folder as `GopuffApp.exe`.

---

## 👤 Author

**Gerry Pidgeon**
Created: November 2025
Project: *Python GUI Boilerplate (Snowflake & Google Drive)*
