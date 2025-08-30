import requests
import pandas as pd
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import time

class WikipediaScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_page_content(self, url):
        # Fetch the content of a Wikipedia page
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_tables(self, soup, save_prefix="wikipedia_table"):
        # Extract all tables from the page and save as CSV
        tables = soup.find_all('table', class_='wikitable')
        
        if not tables:
            print("No tables found on this page.")
            return []
        
        saved_files = []
        
        for i, table in enumerate(tables):
            try:
                # Extract table data
                rows = []
                headers = []
                
                # Get headers
                header_row = table.find('tr')
                if header_row:
                    for th in header_row.find_all(['th', 'td']):
                        headers.append(th.get_text().strip())
                
                # Get data rows
                for row in table.find_all('tr')[1:]:  # Skip header row
                    row_data = []
                    for cell in row.find_all(['td', 'th']):
                        # Clean cell text
                        text = cell.get_text().strip()
                        text = re.sub(r'\[\d+\]', '', text)  # Remove reference numbers
                        text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
                        row_data.append(text)
                    
                    if row_data:  # Only add non-empty rows
                        rows.append(row_data)
                
                if rows and headers:
                    # Create DataFrame
                    df = pd.DataFrame(rows, columns=headers[:len(rows[0])] if len(headers) >= len(rows[0]) else headers + [f'Col_{j}' for j in range(len(headers), len(rows[0]))])
                    
                    # Save to CSV
                    filename = f"{save_prefix}{i+1}.csv"
                    df.to_csv(filename, index=False, encoding='utf-8')
                    saved_files.append(filename)
                    print(f"Table {i+1} saved as {filename} ({df.shape[0]} rows, {df.shape[1]} columns)")
                    
                    # Show preview
                    print(f"\nPreview of Table {i+1}:")
                    print(df.head(3))
                    print("-" * 50)
                    
            except Exception as e:
                print(f"Error processing table {i+1}: {e}")
        
        return saved_files
    
    def extract_text_content(self, soup, save_as="wikipedia_content.txt"):
        # Find the main content div
        content_div = soup.find('div', id='mw-content-text')
        
        if not content_div:
            print("Could not find main content.")
            return None
        
        # Extract paragraphs
        paragraphs = content_div.find_all('p')
        
        content = []
        for p in paragraphs:
            text = p.get_text().strip()
            if text:  # Only add non-empty paragraphs
                # Clean the text
                text = re.sub(r'\[\d+\]', '', text)  # Remove reference numbers
                text = re.sub(r'\s+', ' ', text)     # Normalize whitespace
                content.append(text)
        
        if content:
            with open(save_as, 'w', encoding='utf-8') as f:
                f.write('\n\n'.join(content))
            print(f"Text content saved as {save_as} ({len(content)} paragraphs)")
            return save_as
        
        return None    
    
    def scrape_page(self, url):
        print(f"Scraping Wikipedia page: {url}")
        
        # Validate URL
        parsed_url = urlparse(url)
        if 'wikipedia.org' not in parsed_url.netloc:
            print("Please provide a Wikipedia URL.")
            return
        
        soup = self.get_page_content(url)
        if not soup:
            return
        
        # Extract page title
        title = soup.find('h1', id='firstHeading')
        page_title = title.get_text().strip() if title else "wikipedia_page"
        page_title = re.sub(r'[^\w\s-]', '', page_title)  # Remove special characters
        page_title = re.sub(r'\s+', '_', page_title)      # Replace spaces with underscores
        
        print(f"Page title: {page_title}")
        
        saved_files = []
        
        # Extract tables
        table_files = self.extract_tables(soup, "table")
        saved_files.extend(table_files)
        
        # Extract text content
        content_file = self.extract_text_content(soup, "content.txt")
        if content_file:
            saved_files.append(content_file)
        
        print(f"\nScraping completed. Files saved: {saved_files}")
        return saved_files

def main():
    scraper = WikipediaScraper()
    
    while True:
        url = input("\nEnter Wikipedia URL (or 'quit' to exit): ").strip()
        
        if url.lower() == 'quit':
            break
        
        if not url:
            continue
        
        try:
            scraper.scrape_page(url)
        except Exception as e:
            print(f"Error during scraping: {e}")
        
        # Small delay to be respectful to Wikipedia's servers
        time.sleep(1)

if __name__ == "__main__":
    main()
