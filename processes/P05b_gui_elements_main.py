# ====================================================================================================
# P05b_gui_elements_main.py
# ----------------------------------------------------------------------------------------------------
# Purpose:
#   This is the MAIN APPLICATION window.
#   It is launched by the 'P05a' Connection Launcher.
#   It receives the live connection objects and contains the core application logic (Query/Export).
# ----------------------------------------------------------------------------------------------------
# Author:       Gerry Pidgeon
# Created:      2025-11-06
# Project:      Python Boilerplate
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

# --- Import specific project functions ---
from processes.P09_gdrive_api import upload_dataframe_as_csv


# ====================================================================================================
# 3. MAIN APPLICATION WINDOW CLASS
# ----------------------------------------------------------------------------------------------------
class MainApplicationWindow(tk.Toplevel):
    """
    This is the main application window where the user interacts with data.
    It receives live connection objects from the ConnectionLauncher (P05a).
    """
    def __init__(self, parent, snowflake_conn, gdrive_service, upload_method, local_path):
        super().__init__(parent)
        
        print("MainApplicationWindow: __init__ started.")
        
        # --- Store the connection objects and settings ---
        self.parent = parent
        self.sf_conn = snowflake_conn
        self.gdrive_service = gdrive_service
        self.upload_method = upload_method
        self.local_path = local_path
        self.report_df = None # Stores the result of the last query

        # --- Window Setup ---
        self.title("Snowflake Data Exporter")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # --- Styling ---
        style = ttk.Style(self)
        style.configure("Query.TLabel", font=("Arial", 11, "bold"))
        style.configure("Title.TLabel", font=("Arial", 16, "bold"))
        style.configure("Status.TLabel", font=("Arial", 9, "italic"))
        style.configure("Export.TButton", font=("Arial", 10, "bold"), padding=10)

        # --- Layout ---
        self.main_frame = ttk.Frame(self, padding="15")
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        self.main_frame.columnconfigure(0, weight=1)

        # --- Status Header (Row 0) ---
        self.status_label = ttk.Label(self.main_frame, text="Connections Initialized.", style="Title.TLabel")
        self.status_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        self.sub_status = ttk.Label(self.main_frame, text=self._get_connection_summary(), style="Status.TLabel", foreground="blue")
        self.sub_status.grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Separator(self.main_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

        # --- 2. Query Input (Row 3) ---
        ttk.Label(self.main_frame, text="2. SQL Query", style="Query.TLabel").grid(row=3, column=0, sticky=tk.W, pady=(10, 5))

        self.query_text = tk.Text(self.main_frame, height=12, width=80)
        self.query_text.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=5)
        self.query_text.insert(tk.END, "SELECT \n  CURRENT_USER() AS USER_NAME,\n  CURRENT_TIMESTAMP() AS QUERY_TIME,\n  'Test Data' AS SAMPLE_COLUMN\nLIMIT 10;")
        
        self.main_frame.rowconfigure(4, weight=1) 
        
        # --- 3. Action Buttons (Row 5) ---
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(15, 0))

        # --- Run Query Button ---
        self.run_button = ttk.Button(
            button_frame, text="RUN QUERY (Step 3)",
            command=self.run_query,
            state=tk.NORMAL if self.sf_conn else tk.DISABLED
        )
        self.run_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # --- Export Button ---
        self.export_button = ttk.Button(
            button_frame, text="EXPORT TO DRIVE (Step 4)",
            command=self.export_report,
            state=tk.DISABLED,
            style="Export.TButton"
        )
        self.export_button.pack(side=tk.LEFT)

        # --- Query Status (Row 6) ---
        self.query_status = ttk.Label(self.main_frame, text="Ready to run query.", foreground="black")
        self.query_status.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))

        self.check_for_thread_results()


    # ====================================================================================================
    # 4. HELPER FUNCTIONS
    # ====================================================================================================

    def _get_connection_summary(self) -> str:
        """Returns a string summarizing the connection state."""
        sf_state = "✅ CONNECTED" if self.sf_conn else "❌ NOT CONNECTED"
        if self.upload_method == 'api':
            gd_state = "✅ API READY" if self.gdrive_service else "❌ API BLOCKED"
            gd_detail = "Method: Google API"
        else:
            gd_state = "✅ LOCAL PATH SET"
            gd_detail = f"Method: Local (Path: {self.local_path})"
        
        return f"Snowflake: {sf_state} | GDrive: {gd_state} ({gd_detail})"

    def on_close(self):
        """Called when the user clicks the 'X' on this window."""
        print("MainApplicationWindow: Closing...")
        
        if self.sf_conn:
            try:
                self.sf_conn.close()
                print("Snowflake connection closed.")
            except Exception as e:
                print(f"Error closing Snowflake connection: {e}")
        
        self.parent.destroy()


    # ====================================================================================================
    # 5. CORE LOGIC: QUERY AND EXPORT
    # ====================================================================================================
    
    def run_query(self):
        """Initiates the Snowflake query process in a separate thread."""
        if not self.sf_conn:
            messagebox.showerror("Connection Error", "Cannot run query: Snowflake is not connected.")
            return

        sql_query = self.query_text.get("1.0", tk.END).strip()
        if not sql_query:
            messagebox.showwarning("Input Error", "Please enter a SQL query.")
            return

        self.run_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)
        self.query_status.config(text="Status: Running query... Please wait.", foreground="orange")

        threading.Thread(target=self.threaded_run_query, args=(sql_query,)).start()

    def threaded_run_query(self, sql_query):
        """The actual blocking function that fetches data from Snowflake."""
        try:
            df = pd.read_sql(sql_query, self.sf_conn)
            self.parent.thread_queue.put({"source": "main_app", "action": "query_success", "data": df})
        except Exception as e:
            self.parent.thread_queue.put({"source": "main_app", "action": "query_failure", "error": str(e)})


    # --- EXPORT HANDLERS ---
    
    def export_report(self):
        """Handles the Export button click and directs to the correct export method."""
        if self.report_df is None or self.report_df.empty:
            messagebox.showwarning("Export Error", "No data to export. Run a query first.")
            return

        self.export_button.config(state=tk.DISABLED)
        self.query_status.config(text="Status: Preparing report for export...", foreground="orange")
        
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"snowflake_report_{timestamp}.csv"

        if self.upload_method == 'api':
            threading.Thread(target=self._export_api_csv, args=(self.report_df, filename)).start()
        else: # 'local'
            threading.Thread(target=self._export_local_csv, args=(self.report_df, filename)).start()

    def _export_local_csv(self, df: pd.DataFrame, filename: str):
        """Exports DataFrame to the local mapped drive path."""
        try:
            full_path = Path(self.local_path) / filename
            full_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(full_path, index=False)
            
            self.parent.thread_queue.put({
                "source": "main_app", 
                "action": "export_success", 
                "method": "Local Drive",
                "path": str(full_path)
            })
            
        except Exception as e:
            self.parent.thread_queue.put({
                "source": "main_app", 
                "action": "export_failure", 
                "method": "Local Drive",
                "error": str(e)
            })

    def _export_api_csv(self, df: pd.DataFrame, filename: str):
        """Exports DataFrame to Google Drive using the API."""
        if not self.gdrive_service:
            self.parent.thread_queue.put({
                "source": "main_app", 
                "action": "export_failure", 
                "method": "API",
                "error": "Google Drive API Service is not connected."
            })
            return

        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            file_id = upload_dataframe_as_csv(
                self.gdrive_service,
                csv_buffer,
                filename
            )

            if file_id:
                 self.parent.thread_queue.put({
                    "source": "main_app", 
                    "action": "export_success", 
                    "method": "API",
                    "path": f"File ID: {file_id}"
                })
            else:
                raise Exception("API upload failed to return a file ID.")

        except Exception as e:
            self.parent.thread_queue.put({
                "source": "main_app", 
                "action": "export_failure", 
                "method": "API",
                "error": str(e)
            })


    # ====================================================================================================
    # 6. THREADING & STATUS UPDATES (RUNS IN MAIN GUI THREAD)
    # ====================================================================================================
    
    def check_for_thread_results(self):
        """Continuously checks the queue for results from background threads."""
        try:
            message = self.parent.thread_queue.get(block=False)
            
            action = message.get("action")
            data = message.get("data")
            error = message.get("error")
            method = message.get("method")
            path = message.get("path")
            
            if action == "query_success":
                self.report_df = data
                self.query_status.config(
                    text=f"Status: ✅ Query successful. Fetched {len(self.report_df)} rows.", 
                    foreground="green"
                )
                self.run_button.config(state=tk.NORMAL)
                self.export_button.config(state=tk.NORMAL)
            
            elif action == "query_failure":
                self.report_df = None
                self.query_status.config(
                    text=f"Status: ❌ Query Failed. Error: {error}", 
                    foreground="red"
                )
                self.run_button.config(state=tk.NORMAL)
                self.export_button.config(state=tk.DISABLED)
                messagebox.showerror("SQL Error", f"Query failed:\n\n{error}")

            elif action == "export_success":
                self.query_status.config(
                    text=f"Status: ✅ Export Successful via {method}. File saved: {path}", 
                    foreground="green"
                )
                self.run_button.config(state=tk.NORMAL)
                self.export_button.config(state=tk.NORMAL)

            elif action == "export_failure":
                self.query_status.config(
                    text=f"Status: ❌ Export Failed via {method}. Error: {error}", 
                    foreground="red"
                )
                self.run_button.config(state=tk.NORMAL)
                self.export_button.config(state=tk.NORMAL)
                messagebox.showerror("Export Error", f"Export failed:\n\nMethod: {method}\nError: {error}")

        except queue.Empty:
            pass

        self.after(100, self.check_for_thread_results)


# ====================================================================================================
# 7. MAIN EXECUTION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    This script is not intended to be run directly.
    """
    print("This is the main application module (P05b_gui_elements_main.py).")
    print("Please run 'main/M00_run_setup.gui.py' to start the application.")