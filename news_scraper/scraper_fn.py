import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pandas as pd
import logging
import os
import time
from datetime import datetime

class scrap_data(object):

    # Validate date format
    def get_date(self, date, concurrency, output):
        self.date = date
        self.concurrency = concurrency
        self.output = output

        try:
            self.date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


        # Get the current time in h-m-s format for the filename
        self.current_time = time.strftime("%H-%M-%S")

        # Create directories if they do not exist
        log_dir = f"log/{date}"
        os.makedirs(log_dir, exist_ok=True)

        data_dir = f"data/{date}"
        os.makedirs(data_dir, exist_ok=True)

        # Set paths for log and output files with timestamp
        log_filename = f"{log_dir}/{date}_logs.log"

        self.output_filename = f"{data_dir}/{date}_articles.{self.output}"

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Target URLs
        self.base_url = "https://www.newagebd.net"
        self.archive_url = f"{self.base_url}/archive?date={date}"


    # Fetch function with retries
    async def fetch(self,session, url, retries=3, timeout=10):
        for attempt in range(retries):
            try:
                async with session.get(url, timeout=timeout) as response:
                    if response.status == 200:
                        return await response.text()
                    self.logger.warning(f"Attempt {attempt + 1} failed with status {response.status} for URL: {url}")
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for URL: {url}, error: {e}")
        self.logger.error(f"Failed to fetch {url} after {retries} attempts")
        return None


    # Function to fetch article links from archive page
    async def fetch_article_links(self,url, session):
        articles_data = []
        page_content = await self.fetch(session, url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            articles = soup.select('div.block-area article.card.card-full.hover-a.mb-module')

            for article in articles:
                link_element = article.select_one('h2.card-title a')
                if link_element and link_element.get('href'):
                    link = link_element['href']
                    full_link = link if 'http' in link else f"{self.base_url}{link}"
                    articles_data.append({'title': None, 'content': None, 'link': full_link})
                    self.logger.info(f"Found article link: {full_link}")
        return articles_data


    # Function to fetch individual article content
    async def fetch_article_content(self,article, session):

        url = article['link']
        self.fetch_status = "Feching started.."
        page_content = await self.fetch(session, url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            title_element = soup.select_one('h1.entry-title')
            article['title'] = title_element.get_text(strip=True) if title_element else "No title found"

            content_elements = soup.select('div.post-content p')
            article['content'] = ' '.join(
                [p.get_text(strip=True) for p in content_elements]) if content_elements else "No content found"
            self.logger.info(f"Fetched content for article: {article['title'][:50]}")
            self.fetch_status = "Fetch completed for article :: " + url
        else:
            article['title'] = "Failed to fetch title"
            article['content'] = "Content not available"


    # Main async function
    async def main(self,a):
        start_time = time.time()
        async with aiohttp.ClientSession() as session:

            articles_data = await self.fetch_article_links(self.archive_url, session)

            # Fetch article content concurrently with limited tasks
            semaphore = asyncio.Semaphore(self.concurrency)  # Limit concurrent fetches

            async def sem_fetch(article):
                async with semaphore:
                    await self.fetch_article_content(article, session)

            await asyncio.gather(*(sem_fetch(article) for article in articles_data))

            df = pd.DataFrame(articles_data)
            if self.output == 'csv':
                df.to_csv(self.output_filename, index=False)
            elif self.output == 'xlsx':
                df.to_excel(self.output_filename, index=False, engine='openpyxl')
            elif self.output == 'txt':
                df.to_csv(self.output_filename, index=False, sep='\t')

        self.logger.info(f"Data scraping completed in {time.time() - start_time:.2f} seconds.")
        self.fetch_status = "FT_COMP"


# Run main function
# my_scraper = scrap_data()
# my_scraper.get_date(date='2024-12-07', concurrency=20, output='csv')
# asyncio.run(my_scraper.main(1))