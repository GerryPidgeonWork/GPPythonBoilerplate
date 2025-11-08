# ====================================================================================================
# SP1_launch_and_show_paths.py
# ----------------------------------------------------------------------------------------------------
# Test harness to:
#   1. Launch the real initial GUI (P05a)
#   2. Let the user pick the drive / method
#   3. When "Finish & Launch App" is clicked, show ALL paths from P01
#      in both a GUI window AND the console.
#
# IMPORTANT:
#   P05a imports DWHOrdersToCashGUI directly, so we must patch p05a.DWHOrdersToCashGUI,
#   not just the original module.
# ----------------------------------------------------------------------------------------------------
# ====================================================================================================

import sys
from pathlib import Path

# make sure we can import from /processes
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.dont_write_bytecode = True

from processes.P00_set_packages import *
from processes import P01_set_file_paths as p01
from processes import P05a_gui_elements_setup as p05a
from implementation import I02_gui_elements_main as p05b  # original main GUI (we'll still import it)


# ----------------------------------------------------------------------------------------------------
# 1. Path Viewer (replaces main GUI just for this test)
# ----------------------------------------------------------------------------------------------------
class PathViewerGUI(tk.Toplevel):
    def __init__(self, parent, snowflake_conn=None, gdrive_service=None,
                 upload_method=None, local_path=None):
        super().__init__(parent)
        self.title("Path Viewer (P01)")
        self.geometry("900x600")
        self.configure(bg="#f7f7f7")

        ttk.Label(self, text="✅ P01 Provider Paths", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(
            self,
            text=f"Upload method: {upload_method} | Local path: {local_path}",
            font=("Arial", 9, "italic")
        ).pack(pady=5)

        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        text = tk.Text(frame, wrap="none", height=30, bg="#ffffff")
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = ttk.Scrollbar(frame, command=text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scroll.set)

        # ---------- ACTUAL DUMP ----------
        print("\n================ P01 PATH DUMP ================")
        print(f"PROJECT_ROOT:      {p01.PROJECT_ROOT}")
        print(f"SHARED_DRIVE_ROOT: {p01.SHARED_DRIVE_ROOT}\n")

        text.insert(tk.END, "=== P01 Current State ===\n")
        text.insert(tk.END, f"PROJECT_ROOT:      {p01.PROJECT_ROOT}\n")
        text.insert(tk.END, f"SHARED_DRIVE_ROOT: {p01.SHARED_DRIVE_ROOT}\n\n")

        if not p01.ALL_PROVIDER_PATHS:
            msg = (
                "⚠️  ALL_PROVIDER_PATHS is empty.\n"
                "This means P05a may not have called initialise_provider_paths(...)\n"
                "or no local path was selected.\n"
            )
            text.insert(tk.END, msg)
            print(msg)
        else:
            for provider_name, paths_dict in p01.ALL_PROVIDER_PATHS.items():
                header = f"--- {provider_name.upper()} ---"
                text.insert(tk.END, header + "\n")
                print(header)
                for key, path_val in paths_dict.items():
                    line = f"{key:<35}: {path_val}"
                    text.insert(tk.END, line + "\n")
                    print(line)
                text.insert(tk.END, "\n")
                print()

        print("================ END P01 PATH DUMP ================\n")

        ttk.Button(self, text="Close Application", command=self._close_all).pack(pady=10)

    def _close_all(self):
        # kill the hidden launcher too
        self.master.destroy()


# ----------------------------------------------------------------------------------------------------
# 2. PATCH THE RIGHT REFERENCE
# ----------------------------------------------------------------------------------------------------
# P05a did: from processes.P05b_gui_elements_main import DWHOrdersToCashGUI
# so we must replace THAT name:
p05a.DWHOrdersToCashGUI = PathViewerGUI   # <- this is the key line


# ----------------------------------------------------------------------------------------------------
# 3. Run the real launcher (P05a)
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    print("SP1: Launching Initial Connection Launcher (P05a)...")
    app = p05a.ConnectionLauncher()
    app.mainloop()
    print("SP1: Application closed.")
