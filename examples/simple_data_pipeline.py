#!/usr/bin/env python3
"""
Simple Data Processing Pipeline - Example for Architecture Optimization

This pipeline demonstrates common bottlenecks:
- API calls that can be parallelized
- Data transformation that's CPU intensive
- Database operations that can be optimized
"""

import time
from datetime import datetime

import pandas as pd
import requests


def process_data(data_file):
    """Simple pipeline with clear bottlenecks for optimization."""

    # Prepare: Load data
    print("Loading data...")
    df = pd.read_csv(data_file)

    # Fetch: API calls (synchronous bottleneck)
    results = []
    for _, row in df.iterrows():
        response = requests.get(f"https://api.example.com/enrich/{row['id']}")
        results.append(response.json() if response.status_code == 200 else {})
        time.sleep(0.1)  # Rate limiting

    # Transform: Data processing (CPU intensive)
    processed_data = []
    for i, result in enumerate(results):
        processed_item = {
            "id": result.get("id", df.iloc[i]["id"]),
            "value": result.get("value", 0) * 2,
            "category": result.get("category", "unknown").upper(),
            "processed_at": datetime.now().isoformat(),
        }
        processed_data.append(processed_item)

    # Save: Write results
    output_df = pd.DataFrame(processed_data)
    output_df.to_csv("output.csv", index=False)

    return len(processed_data)


if __name__ == "__main__":
    result = process_data("input.csv")
    print(f"Processed {result} records")
