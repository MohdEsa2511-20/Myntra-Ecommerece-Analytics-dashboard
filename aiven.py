import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

# Read CSV
df = pd.read_csv("ecommerce_data.csv", sep=";")

# Create table with PRIMARY KEY
with engine.begin() as conn:
    conn.execute(text("DROP TABLE IF EXISTS ecommerce_data"))

    conn.execute(text("""
    CREATE TABLE ecommerce_data (
        id INT AUTO_INCREMENT PRIMARY KEY
    )
    """))

# Add all CSV columns
for col in df.columns:
    with engine.begin() as conn:
        conn.execute(
            text(f"ALTER TABLE ecommerce_data ADD COLUMN `{col}` TEXT")
        )

# Upload data
df.to_sql(
    "ecommerce_data",
    engine,
    if_exists="append",
    index=False
)

print("Upload Successful!")