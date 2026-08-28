import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "sales.db"

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

cursor.execute("""
    SELECT category,
           SUM(quantity) AS total_quantity,
           SUM(quantity * price) AS total_sales
    FROM sales
    GROUP BY category
    ORDER BY total_sales DESC
""")

rows = cursor.fetchall()

print("\n" + "=" * 60)
print("SALES REPORT")
print("=" * 60)

for category, quantity, total_sales in rows:
    print(f"Category      : {category}")
    print(f"Quantity Sold : {quantity}")
    print(f"Total Sales   : ₹{total_sales:,.2f}")
    print("-" * 60)

cursor.execute("""
    SELECT SUM(quantity * price)
    FROM sales
""")

grand_total = cursor.fetchone()[0]

print(f"GRAND TOTAL SALES: ₹{grand_total:,.2f}")
print("=" * 60)

connection.close()