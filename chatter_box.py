import mysql.connector
import os
import datetime

# ---------------- DATABASE SETUP ----------------

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1111"
)
cursor = db.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS psb1")
cursor.execute("USE psb1")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Customer_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shop_no INT NOT NULL,
    customer_name VARCHAR(255) NOT NULL,

    product_name VARCHAR(255) NOT NULL,
    product_qty INT NOT NULL,

    product_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) AS (product_qty * product_price) STORED,

    payment_mode VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'Paid',

    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

db.commit()
cursor.close()
db.close()


# ---------------- RECONNECT DATABASE ----------------

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1111",
    database="psb1"
)
cursor = db.cursor()

# ---------------- PREDEFINED DATA ----------------

PRODUCTS = {
    1: ("Coffee", 20),
    2: ("Tea", 10),
    3: ("Burger", 60),
    4: ("Pizza", 120),
    5: ("Sandwich", 60),
    6: ("Cold Drink", 30)
}

PAYMENT_MODES = ["Cash", "Card", "Online"]

# ---------------- MAIN MENU ----------------

while True:
    print("\n===== ☕ CHATTER BOX CAFE ☕ =====")
    print("1. Add Customer Data")
    print("2. View All Customer Data")
    print("3. Search Customer Data by Name")
    print("4. Check Sales Shop Wise by Date")
    print("5. Shop Summary")
    print("6. Exit")

    choice = input("Enter your choice: ")

    # -------- ADD DATA --------
    if choice == '1':
        try:
            shop_no = int(input("Enter Shop No (1-6): "))

            if shop_no < 1 or shop_no > 6:
                print("Invalid Shop Number! Only 1 to 6 allowed.")
                continue
            customer_name = input("Enter Customer Name: ")

            print("\n📋 Available Products")
            print("ID | Product | Price")
            for pid, (pname, price) in PRODUCTS.items():
                print(f"{pid}  | {pname} | ₹{price}")

            product_id = int(input("Select Product ID: "))
            if product_id not in PRODUCTS:
                print("Invalid product")
                continue

            product_name, product_price = PRODUCTS[product_id]

            product_qty = int(input("Enter Quantity: "))
            if product_qty <= 0:
                print("Quantity must be greater than 0")
                continue

            print("\n💳 Payment Modes")
            for i, mode in enumerate(PAYMENT_MODES, 1):
                print(f"{i}. {mode}")

            pay_choice = int(input("Select Payment Mode: "))
            if pay_choice < 1 or pay_choice > len(PAYMENT_MODES):
                print("Invalid payment mode")
                continue

            payment_mode = PAYMENT_MODES[pay_choice - 1]
            payment_status = input("Payment Status (Paid/Pending) [Default Paid]: ") or "Paid"

            # ---------- DB INSERT ----------
            cursor.execute("""
            INSERT INTO Customer_data
            (shop_no, customer_name, product_name, product_qty, product_price, payment_mode, payment_status)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (shop_no, customer_name, product_name, product_qty,
                product_price, payment_mode, payment_status))

            db.commit()

            # ---------- TXT FILE SAVE ----------
            if not os.path.exists("data"):
                os.makedirs("data")

            file_name = "data/custoredata.txt"

            if not os.path.isfile(file_name):
                with open(file_name, "w", encoding="utf-8") as f:
                    f.write(
                        f"{'Shop No':<8} | {'Customer Name':<20} | {'Product':<12} | "
                        f"{'Qty':<3} | {'Price':<10} | {'Total':<10} | "
                        f"{'Payment Mode':<12} | {'Status':<7} | {'Order Date':<19}\n"
                    )
                    f.write("-" * 120 + "\n")

            data_str = (
                f"{shop_no:<8} | {customer_name:<20} | {product_name:<12} | "
                f"{product_qty:<3} | ₹{product_price:<8} | "
                f"₹{product_price * product_qty:<8} | {payment_mode:<12} | "
                f"{payment_status:<7} | "
                f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            with open(file_name, "a", encoding="utf-8") as f:
                f.write(data_str)

            print("✅ Customer data added successfully and saved to TXT")

        except ValueError:
            print("Invalid input")
            continue   # 🔥 MOST IMPORTANT LINE


            # -------- VIEW ALL --------
    elif choice == '2':
        cursor.execute("SELECT * FROM Customer_data")
        rows = cursor.fetchall()
        for row in rows:
           print(f"Name: {row[2]}, Product: {row[3]}, Qty: {row[4]}, Price: {row[5]:.2f}, Total: {row[6]:.2f}, Payment Mode: {row[7]}, Status: {row[8]}, Date: {row[9].date()}")

    # -------- SEARCH --------
    elif choice == '3':
        name = input("Enter customer name: ")
        cursor.execute(
            "SELECT * FROM Customer_data WHERE customer_name LIKE %s",
            (f"%{name}%",)
        )
        rows = cursor.fetchall()
        for row in rows:
            print(f"Name: {row[2]}, Product: {row[3]}, Qty: {row[4]}, Price: {row[5]:.2f}, Total: {row[6]:.2f}, Payment Mode: {row[7]}, Status: {row[8]}, Date: {row[9].date()}")
    # -------- DATE WISE SALES --------
    elif choice == '4':
        shop_no = int(input("Enter Shop No: "))
        date = input("Enter Date (YYYY-MM-DD): ")
        cursor.execute("""
        SELECT * FROM Customer_data
        WHERE shop_no=%s AND DATE(order_date)=%s
        """, (shop_no, date))
        rows = cursor.fetchall()
        if not rows:  
            print(f"No sales found for Shop No {shop_no} on {date}")
        else:
            for row in rows:
                print(f"Name: {row[2]}, Product: {row[3]}, Qty: {row[4]}, Price: {row[5]:.2f}, Total: {row[6]:.2f}, Payment Mode: {row[7]}, Status: {row[8]}, Date: {row[9].date()}")

    # -------- SHOP SUMMARY --------
    elif choice == '5':
        cursor.execute("""
        SELECT shop_no,
               COUNT(*) AS total_orders,
               SUM(total_price) AS total_sales
        FROM Customer_data
        GROUP BY shop_no
        """)
        rows = cursor.fetchall()
        for row in rows:
            print(f"Shop No: {row[0]} | Orders: {row[1]} | Sales: ₹{row[2]}")

    # -------- EXIT --------
    elif choice == '6':
        print("👋 Thank you! Exiting...")
        break

    else:
        print("Invalid choice")

cursor.close()
db.close()
