#!/usr/bin/env python3
"""
Legacy Data Pipeline - Example for Modernization

This is a typical legacy pipeline that processes CSV data,
calls external APIs, and stores results. It has several issues:
- Monolithic structure
- No error handling
- Synchronous processing
- No retry logic
- Poor observability
"""

import sqlite3
import time
from datetime import datetime

import pandas as pd
import requests


def process_pipeline(input_file: str, output_db: str):
    """Main pipeline function - processes everything in sequence."""
    print(f"Starting pipeline at {datetime.now()}")

    # Step 1: Read CSV file (no error handling)
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df)} records")

    # Step 2: Transform data (inefficient operations)
    df["processed_date"] = datetime.now().strftime("%Y-%m-%d")
    df["status"] = "processing"

    # Step 3: Call external API for each record (synchronous, slow)
    api_results = []
    for index, row in df.iterrows():
        try:
            # Simulate API call
            response = requests.get(f"https://api.example.com/enrich/{row['id']}")
            if response.status_code == 200:
                api_results.append(response.json())
            else:
                api_results.append({"error": "API call failed"})
        except Exception as e:
            api_results.append({"error": str(e)})

        # Add delay (no retry logic)
        time.sleep(0.1)

    # Step 4: Save to database (no transaction management)
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()

    cursor.execute(
        """ CREATE TABLE IF NOT EXISTS results
                     (id INTEGER, processed_date TEXT, status TEXT, api_result TEXT)"""
    )

    for i, (index, row) in enumerate(df.iterrows()):
        cursor.execute(
            "INSERT INTO results VALUES (?, ?, ?, ?)",
            (
                row["id"],
                row["processed_date"],
                row["status"],
                str(api_results[i]) if i < len(api_results) else "{}",
            ),
        )

    conn.commit()
    conn.close()

    return len(df)


def create_sample_data(filename: str, num_records: int):
    """Create sample CSV data for testing."""
    import random

    data = []
    for i in range(num_records):
        data.append(
            {
                "id": i + 1,
                "name": f"Item_{i+1}",
                "category": random.choice(["A", "B", "C"]),
                "value": random.randint(1, 100),
                "priority": random.choice(["high", "medium", "low"]),
            }
        )

    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)


if __name__ == "__main__":
    # Create sample data
    create_sample_data("sample_input.csv", 500)

    # Run the pipeline
    result = process_pipeline("sample_input.csv", "results.db")
    print(f"Processed {result} records")
