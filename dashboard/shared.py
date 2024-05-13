from pathlib import Path
import sqlite3

import pandas as pd
import faicons as fa


def categorize_education(edu_str):
    if "BS" in edu_str or "Bachelor" in edu_str:
        return "Bachelor's"
    elif "MS" in edu_str or "Master" in edu_str:
        return "Master's"
    elif "PhD" in edu_str:
        return "PhD"
    elif "BE" in edu_str:
        return "BE"
    else:
        return "Other"


def load_data_to_sqlite(db_name, table_name, csv_file):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';"
    )
    table_exists = cursor.fetchone() is not None
    if not table_exists:
        df = pd.read_csv(csv_file)
        df.to_sql(table_name, conn, if_exists="replace", index=False)

    return conn


app_dir = Path(__file__).parent
applicants = pd.read_csv(app_dir / "applicants.csv")

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "briefcase": fa.icon_svg("briefcase"),
    "graduation-cap": fa.icon_svg("graduation-cap"),
    "ellipsis": fa.icon_svg("ellipsis"),
}
