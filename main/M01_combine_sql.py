# ====================================================================================================
# M01_combine_sql.py
# ----------------------------------------------------------------------------------------------------
# Executes both SQL queries to produce consolidated DWH export files for all delivery providers.
# ----------------------------------------------------------------------------------------------------
# Process Summary:
#   • S01_order_level.sql → Produces the order-level data (core financial + operational metrics)
#   • S02_item_level.sql  → Produces the item-level data (line-item + VAT breakdown)
#   • Exports provider-specific CSVs to their respective local directories.
# ----------------------------------------------------------------------------------------------------
# Integration:
#   This main() function is called directly by the GUI (P05b_gui_elements_main.py) in a background thread.
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
from processes.P00_set_packages import * # --- Project-specific configuration and helpers ---
import processes.P07_module_configs as cfg # Used to read REPORTING_START_DATE, etc.
from processes.P08_snowflake_connector import connect_to_snowflake
from processes.P03_shared_functions import normalize_columns, read_sql_clean # Assuming these exist
from processes.P04_static_lists import FINAL_DF_ORDER # Assuming this exists
from processes.P01_set_file_paths import (
    braintree_path, paypal_path, uber_path, deliveroo_path, justeat_path, amazon_path # Assuming these exist
)


# ====================================================================================================
# 3. HELPER FUNCTION: get_sql_path()
# ----------------------------------------------------------------------------------------------------
def get_sql_path(filename: str) -> Path:
    """
    Returns the absolute path to an SQL file, compatible with both Python and PyInstaller builds.
    (Assumes SQL files are located in the project's 'sql/' directory.)
    """
    # PyInstaller resolves bundled files to sys._MEIPASS
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)

    # Note: If your 'sql' folder is in the project root, adjust the path here
    sql_path = Path(base_path) / "sql" / filename

    if not sql_path.exists():
        raise FileNotFoundError(f"❌ SQL file not found: {sql_path}")

    return sql_path


# ====================================================================================================
# 4. QUERY FUNCTIONS
# ----------------------------------------------------------------------------------------------------

def run_order_level_query(conn):
    """
    Executes the order-level SQL query (S01_order_level.sql) against Snowflake.
    """
    # --- STEP 1 - Get the reporting period from the GUI-set config ---
    start_date = cfg.REPORTING_START_DATE
    end_date = cfg.REPORTING_END_DATE

    sql_path = get_sql_path("S01_order_level.sql")

    # Load SQL and inject date placeholders
    sql_query = (
        sql_path.read_text(encoding="utf-8")
        .replace("{{start_date}}", start_date)
        .replace("{{end_date}}", end_date)
    )

    # --- STEP 2 - Execute SQL query ---
    print(f"⏳ Executing order-level query for {start_date} → {end_date} ...", end="", flush=True)
    t0 = time.time()

    df_orders = read_sql_clean(conn, sql_query)

    print(f"\r✅ Order-level query complete in {time.time() - t0:,.1f}s — {len(df_orders):,} rows.")
    return df_orders


def run_item_level_query(conn, df_orders):
    """
    Executes the item-level SQL query (S02_item_level.sql) using gp_order_id values from df_orders.
    """
    # --- STEP 1 - Validate input ---
    gp_order_ids = df_orders["gp_order_id"].dropna().unique().tolist()
    if not gp_order_ids:
        raise ValueError("❌ No valid gp_order_id values found in the order-level data.")

    # --- STEP 2 - Upload order IDs to a temporary Snowflake table ---
    print(f"⏳ Uploading {len(gp_order_ids):,} order IDs to Snowflake ...", end="", flush=True)
    cur = conn.cursor()
    cur.execute("CREATE OR REPLACE TEMP TABLE temp_order_ids (gp_order_id STRING);")

    chunk_size = 25000
    start_time = time.time()

    for i in range(0, len(gp_order_ids), chunk_size):
        chunk = [(oid,) for oid in gp_order_ids[i:i + chunk_size]]
        cur.executemany("INSERT INTO temp_order_ids (gp_order_id) VALUES (%s);", chunk)
        done = min(i + chunk_size, len(gp_order_ids))
        pct = (done / len(gp_order_ids)) * 100
        print(f"\r   ⏳ Inserted {done:,}/{len(gp_order_ids):,} IDs ({pct:,.1f}%)", end="", flush=True)

    elapsed = time.time() - start_time
    print(f"\r✅ Uploaded {len(gp_order_ids):,} order IDs via chunked insert in {elapsed:,.1f}s. Running item-level query ...", end="", flush=True)

    cur.close()

    # --- STEP 3 - Load item-level SQL and substitute order_id list ---
    sql_path = get_sql_path("S02_item_level.sql")
    sql_query = sql_path.read_text(encoding="utf-8")
    sql_query = sql_query.replace("{{order_id_list}}", "SELECT gp_order_id FROM temp_order_ids")

    # --- STEP 4 - Execute SQL ---
    t0 = time.time()
    df_items = read_sql_clean(conn, sql_query)

    print(f"\n✅ Item-level query complete in {time.time() - t0:,.1f}s — {len(df_items):,} rows.")
    return df_items

# ====================================================================================================
# 5. TRANSFORMATION LOGIC
# ----------------------------------------------------------------------------------------------------

def transform_item_data(df_orders, df_items):
    """
    Merges item-level data into order-level dataset and pivots VAT band data.
    """
    print("⏳ Starting data transformation and pivot...")
    
    # Normalize VAT band codes to simpler labels
    df_items["vat_band"] = df_items["vat_band"].replace({
        "0% VAT Band": "0",
        "5% VAT Band": "5",
        "20% VAT Band": "20",
        "Other / Unknown VAT Band": "other"
    })

    # Pivot VAT band rows into columns (aggregating by gp_order_id)
    df_pivot = (
        df_items.pivot_table(
            index="gp_order_id",
            columns="vat_band",
            values=["item_quantity_count", "total_price_inc_vat", "total_price_exc_vat"],
            aggfunc="sum",
            fill_value=0
        )
    )

    # Flatten multi-level column index (metric_band)
    df_pivot.columns = [f"{metric}_{band}" for metric, band in df_pivot.columns]

    # Calculate total number of products per order (sum across all VAT bands)
    df_pivot["total_products"] = df_pivot.filter(like="item_quantity_count_").sum(axis=1)

    # Merge back into main order-level data
    df_final = df_orders.merge(df_pivot, how="left", left_on="gp_order_id", right_index=True)

    # Clear duplicated item metrics for multi-transaction orders
    item_cols = [c for c in df_final.columns if any(x in c for x in [
        "item_quantity_count", "total_price_inc_vat", "total_price_exc_vat", "total_products"
    ])]
    # Assuming 'braintree_tx_index' exists in df_orders
    mask = (df_final["braintree_tx_index"].notna()) & (df_final["braintree_tx_index"] >= 2)
    df_final.loc[mask, item_cols] = np.nan

    # Sort and align columns
    df_final = df_final.sort_values(by=["gp_order_id", "braintree_tx_index"], ascending=True)
    df_final = df_final[FINAL_DF_ORDER]

    print(f"✅ Combined order + item data: {len(df_final):,} rows, {len(df_final.columns):,} columns.")
    return df_final


# ====================================================================================================
# 6. MAIN ORCHESTRATION FUNCTION
# ----------------------------------------------------------------------------------------------------
def main():
    """
    Main function to orchestrate the DWH export workflow.
    This function is called by the GUI (P05b_gui_elements_main.py).
    """
    # 1. Connect to Snowflake using the user saved in the environment by the GUI
    conn = connect_to_snowflake() 
    if not conn:
        # P08 handles printing the error, we just raise to stop the thread
        raise Exception("Snowflake connection failed. Check console for Okta authentication errors.")
    
    # 2. Set context (Role/Warehouse) - This happens internally in connect_to_snowflake()
    
    # 3. Run SQL queries
    df_orders = run_order_level_query(conn)
    df_items = run_item_level_query(conn, df_orders)

    # 4. Combine and finalize
    df_final = transform_item_data(df_orders, df_items)

    # 5. Cleanly close connection
    conn.close()
    print("\n🔒 Connection closed cleanly.\n")

    # 6. EXPORT TO PROVIDER CSVs
    start_date = cfg.REPORTING_START_DATE
    period_label = pd.to_datetime(start_date).strftime("%y.%m")

    # Define subsets by provider type
    df_braintree = df_final.loc[(df_final["vendor_group"].str.lower() == "dtc") & (df_final["payment_system"].str.lower() != "paypal")]
    df_paypal = df_final.loc[(df_final["vendor_group"].str.lower() == "dtc") & (df_final["payment_system"].str.lower() == "paypal")]
    df_uber = df_final.loc[df_final["order_vendor"].str.lower() == "uber"]
    df_deliveroo = df_final.loc[df_final["order_vendor"].str.lower() == "deliveroo"]
    df_justeat = df_final.loc[df_final["order_vendor"].str.lower().isin(["just eat", "justeat"])]
    df_amazon = df_final.loc[df_final["order_vendor"].str.lower() == "amazon uk"]

    # Map providers to their output folders and filtered DataFrames
    provider_map = {
        "Braintree": (braintree_path, df_braintree),
        "PayPal": (paypal_path, df_paypal),
        "Uber": (uber_path, df_uber),
        "Deliveroo": (deliveroo_path, df_deliveroo),
        "Just Eat": (justeat_path, df_justeat),
        "Amazon": (amazon_path, df_amazon),
    }

    # Iterate over each provider and save its subset to CSV
    for provider, (path, df_subset) in provider_map.items():
        if df_subset.empty:
            print(f"⚠️ No rows found for {provider}, skipping.")
            continue

        path.mkdir(parents=True, exist_ok=True)
        # Note: Added the run notes/label to the filename for better tracking
        notes_tag = f" ({cfg.NOTES.replace(' ', '_')})" if cfg.NOTES else ""
        filename = f"{period_label} - {provider} DWH data{notes_tag}.csv"
        file_path = path / filename

        df_subset.to_csv(file_path, index=False)
        print(f"💾 Saved {len(df_subset):,} rows for {provider} → {file_path}")

    # The main process does not need to return df_final, as the job is complete.
    # return df_final


# ====================================================================================================
# 7. STANDALONE EXECUTION
# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Allows running this module independently (not just imported by GUI or orchestrator)
    # NOTE: You must set config variables in P07 if running standalone.
    
    # Example to run standalone:
    # cfg.REPORTING_START_DATE = "2025-10-01"
    # cfg.REPORTING_END_DATE = "2025-10-31"
    # os.environ["SNOWFLAKE_USER"] = "gerry.pidgeon@gopuff.com"
    # main()
    print("This module is designed to be called by P05b_gui_elements_main.py.")
    print("To run standalone, manually set P07 config variables and OS environment variable.")