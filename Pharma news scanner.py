import feedparser
import pandas as pd
import os  
import requests
from io import BytesIO
from datetime import datetime

WATCHLIST = [
    "jardiance", "empagliflozin", "survodutide",
    "semaglutide", "wegovy", "ozempic", "mounjaro", 
    "obesity", "approval",
]

SOURCE_URLS = [
    "https://news.google.com/rss/search?q=diabetes+weight+loss+drug+pharma&hl=en-GB&gl=GB&ceid=GB:en",
    "https://www.fda.gov/feeds/press-releases.xml",
    "https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency.atom",
    "https://www.sciencedaily.com/rss/health_medicine.xml"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

found_articles = [] 

print("--- Starting Market Access Scan ---")

for url in SOURCE_URLS:
    print(f"Checking source... {url[:40]}...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        feed = feedparser.parse(BytesIO(response.content))
        
        
        source_name = feed.feed.get('title', url)
        
        print(f"  > Connected to: {source_name}")
        print(f"  > Downloaded {len(feed.entries)} articles.") 
        
        for entry in feed.entries:
            headline = entry.title.lower()
            
            if any(keyword in headline for keyword in WATCHLIST):
                found_articles.append({
                    'Source': source_name,  
                    'Title': entry.title,
                    'Link': entry.link,
                    'Found_Date': datetime.now().strftime("%Y-%m-%d")
                })
    except Exception as e:
        print(f"  > Error reading source: {e}")

if len(found_articles) > 0:
    new_df = pd.DataFrame(found_articles)
    
    filename = "BI_Market_Intel_Final.csv"
    
    if os.path.exists(filename):
        print("Found existing database. Appending new data...")
        
        existing_df = pd.read_csv(filename)
    
        combined_df = pd.concat([existing_df, new_df])
        
        final_df = combined_df.drop_duplicates(subset=['Title'], keep='first')
        
        new_items_count = len(final_df) - len(existing_df)
        print(f"  > Added {new_items_count} completely new articles.")
        
    else:
        print("Creating new database...")
        final_df = new_df
        print(f"  > Started database with {len(final_df)} articles.")

    final_df.to_csv(filename, index=False)
    print("Updated successfully.")
