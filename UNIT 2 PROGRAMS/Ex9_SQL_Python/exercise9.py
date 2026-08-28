import sqlite3
from pathlib import Path


# ============================================================
# 1. DATABASE SETUP
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "sales.db"


def create_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]

    if count == 0:
        sales_data = [
            ("Laptop", "Electronics", 5, 55000),
            ("Mobile Phone", "Electronics", 10, 25000),
            ("Keyboard", "Accessories", 15, 1200),
            ("Mouse", "Accessories", 20, 800),
            ("Monitor", "Electronics", 8, 15000),
            ("Headphones", "Accessories", 12, 2500),
            ("Printer", "Electronics", 4, 18000),
            ("USB Cable", "Accessories", 30, 400),
            ("Tablet", "Electronics", 6, 22000),
            ("Webcam", "Accessories", 9, 3500),
        ]

        cursor.executemany("""
            INSERT INTO sales
            (product, category, quantity, price)
            VALUES (?, ?, ?, ?)
        """, sales_data)

    connection.commit()
    connection.close()


# ============================================================
# 2. DISPLAY ALL SALES
# ============================================================

def display_sales():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, product, category, quantity, price,
               quantity * price AS total
        FROM sales
    """)

    rows = cursor.fetchall()

    print("\n" + "=" * 80)
    print("SALES DATA")
    print("=" * 80)

    print(
        f"{'ID':<5}"
        f"{'Product':<20}"
        f"{'Category':<15}"
        f"{'Qty':<8}"
        f"{'Price':<12}"
        f"{'Total':<12}"
    )

    print("-" * 80)

    for row in rows:
        print(
            f"{row[0]:<5}"
            f"{row[1]:<20}"
            f"{row[2]:<15}"
            f"{row[3]:<8}"
            f"{row[4]:<12.2f}"
            f"{row[5]:<12.2f}"
        )

    connection.close()


# ============================================================
# 3. TOTAL SALES
# ============================================================

def calculate_total_sales():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT SUM(quantity * price)
        FROM sales
    """)

    total = cursor.fetchone()[0]

    connection.close()

    return total


# ============================================================
# 4. CATEGORY-WISE SALES
# ============================================================

def category_sales():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            category,
            SUM(quantity) AS total_quantity,
            SUM(quantity * price) AS total_sales
        FROM sales
        GROUP BY category
        ORDER BY total_sales DESC
    """)

    rows = cursor.fetchall()

    print("\n" + "=" * 60)
    print("CATEGORY-WISE SALES")
    print("=" * 60)

    print(
        f"{'Category':<20}"
        f"{'Quantity':<15}"
        f"{'Sales':<15}"
    )

    print("-" * 60)

    for row in rows:
        print(
            f"{row[0]:<20}"
            f"{row[1]:<15}"
            f"{row[2]:<15.2f}"
        )

    connection.close()


# ============================================================
# 5. TOP SELLING PRODUCT
# ============================================================

def top_product():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            product,
            quantity,
            quantity * price AS total_sales
        FROM sales
        ORDER BY total_sales DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    return row


# ============================================================
# 6. MAIN PROGRAM
# ============================================================

def main():

    print("=" * 70)
    print("SQL + PYTHON SALES ANALYSIS")
    print("=" * 70)

    create_database()

    display_sales()

    total = calculate_total_sales()

    print("\n" + "=" * 60)
    print("TOTAL SALES")
    print("=" * 60)
    print(f"Total Sales: ₹{total:,.2f}")

    category_sales()

    product = top_product()

    print("\n" + "=" * 60)
    print("TOP SELLING PRODUCT BY REVENUE")
    print("=" * 60)

    print(f"Product: {product[0]}")
    print(f"Quantity: {product[1]}")
    print(f"Revenue: ₹{product[2]:,.2f}")

    print("\n" + "=" * 70)
    print("EXERCISE 9 DATABASE CREATED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()