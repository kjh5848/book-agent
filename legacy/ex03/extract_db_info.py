import sys
import os
import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://metacoding:metacoding1234@localhost:5432/metacoding_db"
engine = create_engine(DATABASE_URL)

def export_table(table_name):
    df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
    print(f"\n### Table: {table_name}")
    print(df.to_markdown(index=False))

try:
    export_table("employees")
    export_table("leave_balance")
    export_table("sales")
except Exception as e:
    print(f"Error: {e}")
