#!/usr/bin/env python3
"""
Simple Data Pipeline Example

This is a basic data processing pipeline with fewer complexity issues
for testing the modernization system.
"""

import requests


def prepare_data():
    """Prepare the data for processing."""
    print("Preparing data...")
    return {"source": "api", "format": "json"}


def fetch_data(config):
    """Fetch data from external source."""
    print("Fetching data...")
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    return response.json()


def transform_data(raw_data):
    """Transform the fetched data."""
    print("Transforming data...")
    return [{"id": item["id"], "title": item["title"]} for item in raw_data[:10]]


def save_data(processed_data):
    """Save the processed data."""
    print("Saving data...")
    with open("output.json", "w") as f:
        import json

        json.dump(processed_data, f)
    return {"saved": len(processed_data)}


def run_pipeline():
    """Main pipeline orchestrator."""
    config = prepare_data()
    raw_data = fetch_data(config)
    processed_data = transform_data(raw_data)
    result = save_data(processed_data)
    return result


if __name__ == "__main__":
    result = run_pipeline()
    print(f"Pipeline completed: {result}")
