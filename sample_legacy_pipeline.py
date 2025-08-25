#!/usr/bin/env python3
"""
Sample Legacy Pipeline - Demonstrates common patterns that need modernization
"""

import pandas as pd
import requests
import json
import time
from typing import List, Dict

def scrape_financial_data():
    """Legacy monolithic pipeline for financial data scraping"""
    
    # Configuration (hardcoded - not great!)
    base_url = "https://api.financial-data.com"
    pages_to_scrape = 500
    output_file = "financial_data.csv"
    
    all_data = []
    
    # Sequential processing (very slow!)
    for page in range(1, pages_to_scrape + 1):
        print(f"Processing page {page}/{pages_to_scrape}")
        
        try:
            # Fetch data
            url = f"{base_url}/data?page={page}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse response  
            raw_data = response.json()
            
            # Transform data (basic processing)
            for item in raw_data.get('items', []):
                processed_item = {
                    'company': item.get('company_name', ''),
                    'price': float(item.get('stock_price', 0)),
                    'volume': int(item.get('trading_volume', 0)),
                    'timestamp': item.get('timestamp', ''),
                    'market_cap': item.get('market_cap', 0)
                }
                all_data.append(processed_item)
                
        except Exception as e:
            print(f"Error processing page {page}: {e}")
            time.sleep(1)  # Simple retry
            continue
    
    # Save data
    df = pd.DataFrame(all_data)
    df.to_csv(output_file, index=False)
    
    print(f"Scraped {len(all_data)} records to {output_file}")
    return len(all_data)

if __name__ == "__main__":
    scrape_financial_data()