import sqlite3
import pandas as pd
from datetime import datetime

def view_attendance(date=None):
    conn = sqlite3.connect("attendance.db")

    if date:
        query = f"SELECT * FROM attendance WHERE date='{date}' ORDER BY time DESC"
    else:
        query = "SELECT * FROM attendance ORDER BY date DESC, time DESC"

    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        print("[INFO] No attendance records found.")
    else:
        print("\n" + "="*50)
        print("        ATTENDANCE RECORDS")
        print("="*50)
        print(df.to_string(index=False))
        print("="*50)
        print(f"Total Records: {len(df)}")

# View all records
view_attendance()

# View today only
today = datetime.now().strftime("%Y-%m-%d")
print(f"\n--- Today ({today}) ---")
view_attendance(date=today)