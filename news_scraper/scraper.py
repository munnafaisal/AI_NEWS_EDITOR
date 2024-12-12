import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os
import time
import argparse
from datetime import datetime

# Argument parsing for date input
parser = argparse.ArgumentParser(description="Scrape articles from New Age archive.")
# parser.add_argument('date', type=str, help="Date to scrape in YYYY-MM-DD format")
parser.add_argument(
    'date', 
    type=str, 
    nargs='?',  # Make the date argument optional
    default=datetime.today().strftime("%Y-%m-%d"),  # Default to today's date
    help="Date to scrape in YYYY-MM-DD format (default is today's date)"
)
parser.add_argument('--concurrency', type=int, default=20, help="Maximum number of concurrent requests")
parser.add_argument('--output', type=str, choices=['csv', 'xlsx', 'txt'], default='csv', help="Output file type (csv, xlsx, txt)")
args = parser.parse_args()

# Validate date format
try:
    date = datetime.strptime(args.date, "%Y-%m-%d").strftime("%Y-%m-%d")
except ValueError:
    raise ValueError("Date must be in YYYY-MM-DD format")

# Get the current time in h-m-s format for the filename
current_time = time.strftime("%H-%M-%S")

# Create directories if they do not exist
log_dir = f"log/{date}"
os.makedirs(log_dir, exist_ok=True)

data_dir = f"data/{date}"
os.makedirs(data_dir, exist_ok=True)

# Set paths for log and output files with timestamp
log_filename = f"{log_dir}/{date}_logs.log"

output_filename = f"{data_dir}/{date}_articles.{args.output}"


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Target URLs
base_url = "https://www.newagebd.net"
archive_url = f"{base_url}/archive?date={date}"

# Fetch function with retries
async def fetch(session, url, retries=3, timeout=10):
    for attempt in range(retries):
        try:
            async with session.get(url, timeout=timeout) as response:
                if response.status == 200:
                    return await response.text()
                logger.warning(f"Attempt {attempt + 1} failed with status {response.status} for URL: {url}")
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed for URL: {url}, error: {e}")
    logger.error(f"Failed to fetch {url} after {retries} attempts")
    return None

# Function to fetch article links from archive page
async def fetch_article_links(url, session):
    articles_data = []
    page_content = await fetch(session, url)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        articles = soup.select('div.block-area article.card.card-full.hover-a.mb-module')
        
        for article in articles:
            link_element = article.select_one('h2.card-title a')
            if link_element and link_element.get('href'):
                link = link_element['href']
                full_link = link if 'http' in link else f"{base_url}{link}"
                articles_data.append({'title': None, 'content': None, 'link': full_link})
                logger.info(f"Found article link: {full_link}")
    return articles_data

# Function to fetch individual article content
async def fetch_article_content(article, session):
    url = article['link']
    page_content = await fetch(session, url)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        title_element = soup.select_one('h1.entry-title')
        article['title'] = title_element.get_text(strip=True) if title_element else "No title found"
        
        content_elements = soup.select('div.post-content p')
        article['content'] = ' '.join([p.get_text(strip=True) for p in content_elements]) if content_elements else "No content found"
        logger.info(f"Fetched content for article: {article['title'][:50]}")
    else:
        article['title'] = "Failed to fetch title"
        article['content'] = "Content not available"
        
# Main async function
async def main():
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        
        articles_data = await fetch_article_links(archive_url, session)
        
        # Fetch article content concurrently with limited tasks
        semaphore = asyncio.Semaphore(args.concurrency)  # Limit concurrent fetches
        async def sem_fetch(article):
            async with semaphore:
                await fetch_article_content(article, session)
        
        await asyncio.gather(*(sem_fetch(article) for article in articles_data))
        
        
        df = pd.DataFrame(articles_data)
        if args.output == 'csv':
            df.to_csv(output_filename, index=False)
        elif args.output == 'xlsx':
            df.to_excel(output_filename, index=False, engine='openpyxl')
        elif args.output == 'txt':
            df.to_csv(output_filename, index=False, sep='\t')
    
    logger.info(f"Data scraping completed in {time.time() - start_time:.2f} seconds.")

# Run main function
if __name__ == "__main__":
    asyncio.run(main())
