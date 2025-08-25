#!/usr/bin/env python3
"""
Legacy E-commerce Data Pipeline

This is a real-world example of a legacy data pipeline that processes
e-commerce transactions, customer data, and inventory updates.

Issues that need modernization:
1. Monolithic structure with everything in one function
2. Synchronous processing causing bottlenecks
3. No error handling or retry logic
4. Memory-intensive operations on large datasets
5. No monitoring or observability
6. Direct database connections without connection pooling
7. Hard-coded configuration values
8. No proper logging structure
9. Single point of failure design
10. Inefficient data processing patterns
"""

import json
import smtplib
import sqlite3
import time
from datetime import datetime
from email.mime.text import MIMEText

import pandas as pd
import requests

# Hard-coded configuration (should be externalized)
DATABASE_PATH = "ecommerce.db"
API_BASE_URL = "https://api.payment-processor.com"
API_KEY = "hardcoded-api-key-not-secure"
EMAIL_SERVER = "smtp.company.com"
EMAIL_USER = "pipeline@company.com"
EMAIL_PASS = "hardcoded-password"


def process_daily_ecommerce_pipeline():
    """
    Main pipeline function that processes daily e-commerce data.

    This monolithic function handles:
    - Customer data updates
    - Order processing
    - Payment verification
    - Inventory updates
    - Sales reporting
    - Customer notifications

    Problems:
    - Single massive function (complexity score: 9/10)
    - No separation of concerns
    - Synchronous API calls
    - No error recovery
    - Memory issues with large datasets
    """

    start_time = time.time()
    print(f"Starting e-commerce pipeline at {datetime.now()}")

    # Connect to database (no connection pooling)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Step 1: Load customer data (memory intensive for large datasets)
    print("Loading customer data...")
    customer_query = """
    SELECT customer_id, email, last_purchase_date, total_spent, loyalty_tier
    FROM customers
    WHERE last_updated >= datetime('now', '-1 day')
    """
    customers_df = pd.read_sql(customer_query, conn)
    print(f"Loaded {len(customers_df)} customers")

    # Step 2: Load orders (no pagination, loads everything into memory)
    print("Loading order data...")
    orders_query = """
    SELECT order_id, customer_id, product_id, quantity, price, order_date, status
    FROM orders
    WHERE order_date >= datetime('now', '-1 day')
    """
    orders_df = pd.read_sql(orders_query, conn)
    print(f"Loaded {len(orders_df)} orders")

    # Step 3: Process payments (synchronous API calls - very slow)
    print("Processing payments...")
    payment_results = []
    failed_payments = []

    for index, order in orders_df.iterrows():
        if order["status"] == "pending_payment":
            try:
                # Synchronous API call (no async, no connection pooling)
                payment_response = requests.post(
                    f"{API_BASE_URL}/process-payment",
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json={
                        "order_id": order["order_id"],
                        "amount": order["price"] * order["quantity"],
                        "customer_id": order["customer_id"],
                    },
                    timeout=30,
                )

                if payment_response.status_code == 200:
                    payment_data = payment_response.json()
                    payment_results.append(
                        {
                            "order_id": order["order_id"],
                            "status": "completed",
                            "transaction_id": payment_data.get("transaction_id"),
                            "processed_at": datetime.now().isoformat(),
                        }
                    )

                    # Update order status in database immediately (inefficient)
                    cursor.execute(
                        "UPDATE orders SET status = 'paid', payment_processed_at = ? WHERE order_id = ?",
                        (datetime.now(), order["order_id"]),
                    )
                    conn.commit()

                else:
                    failed_payments.append(order["order_id"])
                    print(
                        f"Payment failed for order {order['order_id']}: {payment_response.status_code}"
                    )

            except Exception as e:
                failed_payments.append(order["order_id"])
                print(f"Payment error for order {order['order_id']}: {e}")
                # No proper error handling or retry logic

            # Rate limiting (inefficient approach)
            time.sleep(0.5)

    print(f"Processed {len(payment_results)} payments, {len(failed_payments)} failed")

    # Step 4: Update inventory (inefficient batch processing)
    print("Updating inventory...")
    inventory_updates = {}

    # Group orders by product (inefficient pandas operations)
    for index, order in orders_df[
        orders_df["status"].isin(["paid", "completed"])
    ].iterrows():
        product_id = order["product_id"]
        quantity = order["quantity"]

        if product_id not in inventory_updates:
            inventory_updates[product_id] = 0
        inventory_updates[product_id] += quantity

    # Update inventory one by one (should be batch operation)
    for product_id, total_sold in inventory_updates.items():
        try:
            cursor.execute(
                "UPDATE inventory SET quantity = quantity - ?, last_updated = ? WHERE product_id = ?",
                (total_sold, datetime.now(), product_id),
            )

            # Check for low stock (inefficient query in loop)
            cursor.execute(
                "SELECT quantity, reorder_threshold FROM inventory WHERE product_id = ?",
                (product_id,),
            )
            result = cursor.fetchone()

            if result and result[0] <= result[1]:
                print(
                    f"Low stock alert for product {product_id}: {result[0]} remaining"
                )
                # Should trigger reorder process but doesn't

        except Exception as e:
            print(f"Inventory update failed for product {product_id}: {e}")
            # No proper error handling

    conn.commit()

    # Step 5: Calculate customer loyalty updates (complex calculations in memory)
    print("Calculating loyalty updates...")
    loyalty_updates = []

    for index, customer in customers_df.iterrows():
        customer_orders = orders_df[orders_df["customer_id"] == customer["customer_id"]]

        if len(customer_orders) > 0:
            # Calculate total spent today
            daily_spent = (customer_orders["price"] * customer_orders["quantity"]).sum()
            new_total_spent = customer["total_spent"] + daily_spent

            # Determine new loyalty tier (hard-coded business logic)
            if new_total_spent >= 10000:
                new_tier = "platinum"
            elif new_total_spent >= 5000:
                new_tier = "gold"
            elif new_total_spent >= 1000:
                new_tier = "silver"
            else:
                new_tier = "bronze"

            if new_tier != customer["loyalty_tier"]:
                loyalty_updates.append(
                    {
                        "customer_id": customer["customer_id"],
                        "old_tier": customer["loyalty_tier"],
                        "new_tier": new_tier,
                        "total_spent": new_total_spent,
                    }
                )

                # Update database immediately (inefficient)
                cursor.execute(
                    "UPDATE customers SET loyalty_tier = ?, total_spent = ?, last_updated = ? WHERE customer_id = ?",
                    (
                        new_tier,
                        new_total_spent,
                        datetime.now(),
                        customer["customer_id"],
                    ),
                )

    conn.commit()
    print(f"Updated loyalty for {len(loyalty_updates)} customers")

    # Step 6: Generate sales report (memory intensive aggregations)
    print("Generating sales report...")

    # Complex pandas operations that could be done in SQL
    daily_sales = (
        orders_df[orders_df["status"] == "paid"]
        .groupby("product_id")
        .agg({"quantity": "sum", "price": "mean"})
        .reset_index()
    )

    daily_sales["total_revenue"] = daily_sales["quantity"] * daily_sales["price"]
    total_revenue = daily_sales["total_revenue"].sum()
    total_orders = len(orders_df[orders_df["status"] == "paid"])

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "total_revenue": float(total_revenue),
        "total_orders": int(total_orders),
        "avg_order_value": float(total_revenue / total_orders)
        if total_orders > 0
        else 0,
        "top_products": daily_sales.nlargest(10, "total_revenue").to_dict("records"),
        "failed_payments": len(failed_payments),
        "loyalty_upgrades": len(loyalty_updates),
    }

    # Save report to file (should be stored in proper location)
    report_filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_filename, "w") as f:
        json.dump(report, f, indent=2)

    # Step 7: Send notification emails (blocking, synchronous)
    print("Sending notification emails...")

    try:
        # Send report to management (no error handling for email)
        server = smtplib.SMTP(EMAIL_SERVER, 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)

        # Management report
        msg = MIMEText(
            f"""
Daily E-commerce Report - {report['date']}

Total Revenue: ${report['total_revenue']:,.2f}
Total Orders: {report['total_orders']}
Average Order Value: ${report['avg_order_value']:.2f}
Failed Payments: {report['failed_payments']}
Loyalty Upgrades: {report['loyalty_upgrades']}

Pipeline completed in {time.time() - start_time:.2f} seconds.
        """
        )
        msg["Subject"] = f"Daily E-commerce Report - {report['date']}"
        msg["From"] = EMAIL_USER
        msg["To"] = "management@company.com"

        server.send_message(msg)

        # Customer loyalty upgrade emails (sends one by one, very slow)
        for update in loyalty_updates:
            customer_email = customers_df[
                customers_df["customer_id"] == update["customer_id"]
            ]["email"].iloc[0]

            loyalty_msg = MIMEText(
                f"""
Congratulations! Your loyalty tier has been upgraded from {update['old_tier']} to {update['new_tier']}.
Your total lifetime spending is now ${update['total_spent']:,.2f}.

Thank you for your continued business!
            """
            )
            loyalty_msg[
                "Subject"
            ] = f"Loyalty Tier Upgrade - Welcome to {update['new_tier'].title()}!"
            loyalty_msg["From"] = EMAIL_USER
            loyalty_msg["To"] = customer_email

            server.send_message(loyalty_msg)
            time.sleep(1)  # Rate limiting for email server

        server.quit()
        print("All notification emails sent")

    except Exception as e:
        print(f"Email notification failed: {e}")
        # No proper error handling or retry logic

    # Close database connection
    conn.close()

    # Final summary
    end_time = time.time()
    processing_time = end_time - start_time

    summary = {
        "pipeline_completed_at": datetime.now().isoformat(),
        "processing_time_seconds": processing_time,
        "customers_processed": len(customers_df),
        "orders_processed": len(orders_df),
        "payments_completed": len(payment_results),
        "payments_failed": len(failed_payments),
        "inventory_updates": len(inventory_updates),
        "loyalty_upgrades": len(loyalty_updates),
        "total_revenue": total_revenue,
    }

    print("\n=== PIPELINE COMPLETED ===")
    print(f"Processing time: {processing_time:.2f} seconds")
    print(f"Customers: {len(customers_df)}")
    print(f"Orders: {len(orders_df)}")
    print(f"Revenue: ${total_revenue:,.2f}")
    print(
        f"Success rate: {(len(payment_results) / len(orders_df) * 100):.1f}%"
        if len(orders_df) > 0
        else "N/A"
    )

    return summary


def setup_test_database():
    """Create test database with sample data for pipeline testing."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        email TEXT,
        last_purchase_date TEXT,
        total_spent REAL,
        loyalty_tier TEXT,
        last_updated TEXT
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        price REAL,
        order_date TEXT,
        status TEXT,
        payment_processed_at TEXT
    )
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS inventory (
        product_id INTEGER PRIMARY KEY,
        quantity INTEGER,
        reorder_threshold INTEGER,
        last_updated TEXT
    )
    """
    )

    # Insert sample data
    customers_data = [
        (1, "john@example.com", "2024-01-15", 2500.0, "silver", "2024-01-15"),
        (2, "jane@example.com", "2024-01-14", 8500.0, "gold", "2024-01-14"),
        (3, "bob@example.com", "2024-01-13", 500.0, "bronze", "2024-01-13"),
    ]

    cursor.executemany(
        """
    INSERT OR REPLACE INTO customers
    (customer_id, email, last_purchase_date, total_spent, loyalty_tier, last_updated)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
        customers_data,
    )

    orders_data = [
        (1, 1, 101, 2, 25.99, datetime.now().isoformat(), "pending_payment", None),
        (2, 2, 102, 1, 199.99, datetime.now().isoformat(), "pending_payment", None),
        (3, 3, 103, 3, 15.50, datetime.now().isoformat(), "pending_payment", None),
        (4, 1, 104, 1, 89.99, datetime.now().isoformat(), "pending_payment", None),
    ]

    cursor.executemany(
        """
    INSERT OR REPLACE INTO orders
    (order_id, customer_id, product_id, quantity, price, order_date, status, payment_processed_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        orders_data,
    )

    inventory_data = [
        (101, 100, 20, "2024-01-01"),
        (102, 50, 10, "2024-01-01"),
        (103, 200, 50, "2024-01-01"),
        (104, 25, 5, "2024-01-01"),
    ]

    cursor.executemany(
        """
    INSERT OR REPLACE INTO inventory
    (product_id, quantity, reorder_threshold, last_updated)
    VALUES (?, ?, ?, ?)
    """,
        inventory_data,
    )

    conn.commit()
    conn.close()
    print("Test database setup completed")


if __name__ == "__main__":
    print("Setting up test environment...")
    setup_test_database()

    print("\nRunning legacy e-commerce pipeline...")
    print("This will demonstrate performance issues and areas for modernization.")

    try:
        result = process_daily_ecommerce_pipeline()
        print("\n✅ Pipeline completed successfully (but with many issues)")
        print("👆 This legacy pipeline needs modernization!")

    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        print("This demonstrates the brittleness of legacy pipelines")
