# 🚀 GP Python Boilerplate (Universal GUI Framework)

A **modular, locked-core Python GUI boilerplate** designed for projects that require **Snowflake authentication (Okta SSO)** and **Google Drive integration (API or local mapped drive)**.
It provides a fully reusable launcher workflow and structured layering — separating *locked shared components* from *project-specific logic*.

This framework lets you spin up new finance, analytics, or automation tools rapidly — each with its own GUI — all built on the same stable foundation.

---

## 🌟 Key Features

### 🔐 Authentication & Connections

**Snowflake Connector (P08)**

* Securely connects using **Okta SSO (externalbrowser)**.
* Automatically sets the best role/warehouse based on a configurable priority list.
* Reuses authenticated sessions when possible.

**Google Drive Connector (P09)**

* Supports **two methods**:

  * 🖥️ **Local mapped drive** (default): Choose your local `H:\` or equivalent shared path.
  * ☁️ **API mode:** Uses Google Drive API with OAuth credentials for direct access.

**Universal Launcher (P05a)**

* Thread-safe, responsive GUI for connection setup.
* Dynamically loads user emails from `P10_user_config.py`.
* Passes live connection objects (Snowflake + Drive) into the project’s GUI.

**Locked Core (P05b)**

* Provides consistent GUI layout, styling, and lifecycle management for all projects.
* Ensures unified window structure and “Close Application” handling.

---

## 🧩 Folder & Module Structure

```
GPPythonBoilerplate/
│
├── main/
│   ├── M00_run_gui.py               # 🚀 Main entry point (starts universal launcher)
│   └── M01_load_project_config.py   # Loads provider setup & routes to project launcher
│
├── implementation/
│   ├── I01_project_launcher.py      # Project bridge — imports and launches GUI
│   └── I02_gui_elements_main.py     # Project-specific GUI (inherits from BaseMainGUI)
│
├── processes/                       # 🔒 Locked, reusable core modules
│   ├── P00_set_packages.py          # Central import hub (tkinter, pandas, etc.)
│   ├── P01_set_file_paths.py        # Provider path initialisation (shared drive / GDrive)
│   ├── P02_system_processes.py      # OS detection, path helpers
│   ├── P05a_gui_elements_setup.py   # Universal connection launcher GUI
│   ├── P05b_gui_elements_main.py    # Locked base GUI (structure, styling, lifecycle)
│   ├── P08_snowflake_connector.py   # Handles Snowflake Okta login + role assignment
│   ├── P09_gdrive_api.py            # Google Drive API service builder
│   └── P10_user_config.py           # User-editable file (email slots, defaults)
│
├── credentials/                     # (Optional) Google API OAuth credentials
│   └── credentials.json
│
└── .venv/                           # Local virtual environment
```

---

## ⚙️ Setup & Configuration

### 🧰 Step 1 – Install Dependencies

If a `requirements.txt` is provided:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install pandas snowflake-connector-python google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

---

### 📧 Step 2 – Configure User Emails

Edit the config file `processes/P10_user_config.py` and add your team’s emails:

```python
EMAIL_SLOT_1 = "firstname.lastname@gopuff.com"
EMAIL_SLOT_2 = ""
```

Any blank or placeholder entry will be ignored.

---

### 🔑 Step 3 – (Optional) Google Drive API Setup

If using the **API method** instead of a mapped drive:

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Google Drive API**
3. Create an **OAuth client ID** (type: Desktop App)
4. Download and rename credentials as `credentials.json`
5. Place it in the `/credentials/` folder

---

## ▶️ Running the Application

1. Open the terminal in your project root:

   ```bash
   cd GPPythonBoilerplate
   ```
2. Activate your virtual environment:

   ```bash
   .\.venv\Scripts\Activate.ps1
   ```
3. Launch the app:

   ```bash
   python main/M00_run_gui.py
   ```

🪟 The **Launcher Window** opens. Use it to:

* Authenticate to **Snowflake** (Okta browser flow)
* Connect to **Google Drive** (via API or mapped path)
* Launch your project GUI automatically

---

## 🧠 Building New Projects

You can clone this boilerplate to create new, independent applications while reusing the same locked core.

### 🪄 Step-by-Step

1. **Duplicate this repository** and rename it (e.g., `InvoiceProcessor`, `FinanceReconciler`)
2. Inside `/implementation/`, replace the placeholder files:

   * `I01_project_launcher.py` → import your own GUI or workflow
   * `I02_gui_elements_main.py` → define your own subclass of `BaseMainGUI`
3. (Optional) Update metadata in `main/M01_load_project_config.py`
4. Run your new project via `M00_run_gui.py`

### Example

```python
# In I02_gui_elements_main.py
from processes.P05b_gui_elements_main import BaseMainGUI

class MyNewAppGUI(BaseMainGUI):
    def build_gui(self):
        ttk.Label(self.main_frame, text="Welcome to My Custom App", font=("Arial", 14, "bold")).pack(pady=20)
        ttk.Button(self.main_frame, text="Run Report", command=self.run_report).pack(pady=10)

    def run_report(self):
        print("Running my project-specific logic...")
```

Now your app uses the same secure launcher, styling, and environment setup — but with your own GUI logic.

---

## 🏗️ Building a Windows Executable (.exe)

To distribute the app as a single binary:

```bash
pip install pyinstaller
pyinstaller --onefile --name "MyApp" --add-data "credentials;credentials" main/M00_run_gui.py
```

Your executable will appear in `/dist/MyApp.exe`.

---

## 🧭 Architecture Overview

```
M00_run_gui.py
  └── starts → P05a_gui_elements_setup.ConnectionLauncher
        └── after setup calls → M01_load_project_config.launch_project_main()
              └── imports → implementation/I01_project_launcher.launch_main_app()
                    └── instantiates → implementation/I02_gui_elements_main.MainProjectGUI()
```

* 🔒 **P05a / P05b:** Universal locked core
* 🧩 **I01 / I02:** Project layer (safe to edit)
* 🚀 **M00 / M01:** Entry points + runtime config

---

## 👤 Author

**Gerry Pidgeon**
Created: November 2025
Project: *GP Python Boilerplate (Snowflake & Google Drive)*
