import feedparser
import pandas as pd
import os
import requests
from io import BytesIO
from datetime import datetime


WATCHLIST = [
    "jardiance", "empagliflozin", "survodutide", 
    "semaglutide", "wegovy", "ozempic", "mounjaro", 
    "obesity", "approval", "launch",
    "ckd", "kidney", "renal", "heart failure"   
]

SOURCE_URLS = [
    "https://news.google.com/rss/search?q=diabetes+weight+loss+drug+pharma&hl=en-GB&gl=GB&ceid=GB:en",
    "https://www.fda.gov/feeds/press-releases.xml",
    "https://www.gov.uk/government/organisations/medicines-and-healthcare-products-regulatory-agency.atom",
    "https://www.sciencedaily.com/rss/health_medicine.xml",
    "https://www.nice.org.uk/consultations/rss"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def scan_feeds():
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
                title = getattr(entry, 'title', "")
                description = getattr(entry, 'description', "")
                link = getattr(entry, 'link', "No Link")
                
                content_to_check = (title + " " + description).lower()
                
                if any(keyword in content_to_check for keyword in WATCHLIST):
                    found_articles.append({
                        'Source': source_name,
                        'Title': title,
                        'Link': link,
                        'Found_Date': datetime.now().strftime("%Y-%m-%d")
                    })
                    
        except Exception as e:
            print(f"  > Error reading source: {e}")

    return found_articles

def save_database(new_data):
    filename = "BI_Market_Intel_Final.csv"
    
    # for when no articles are found
    if not new_data:
        pass 
        
    new_df = pd.DataFrame(new_data)
    
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

if __name__ == "__main__":
    articles = scan_feeds()
    # Only try to save if we actually found something
    if len(articles) > 0:
        save_database(articles)
