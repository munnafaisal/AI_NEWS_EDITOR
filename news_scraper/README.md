# New Age Archive Article Scraper

This Python script allows you to scrape articles from the New Age Bangladesh website archive. It fetches article links for a specified date (defaulting to today’s date) and retrieves the content of each article, saving the data in a user-defined file format (`CSV`, `XLSX`, or `TXT`).

## [New Age Archive Link](https://www.newagebd.net/archive?)

## Features
- Scrape articles from the New Age archive for a specific date (defaults to today's date).
- Retrieve article titles and content.
- Handle concurrent requests efficiently with a configurable concurrency limit.
- Save the output in multiple formats: `CSV`, `XLSX`, or `TXT`.
- Log scraping details for debugging and monitoring.

## Requirements

Make sure you have the following Python dependencies installed:

- Python 3.7+
- `aiohttp`: For asynchronous HTTP requests
- `beautifulsoup4`: For HTML parsing and extracting article data
- `pandas`: For saving data to various file formats
- `openpyxl` (optional, only if `XLSX` format is chosen for output)

### Install Dependencies

To install the required dependencies, use the following `pip` command:

```bash
pip install aiohttp beautifulsoup4 pandas openpyxl
```

## Installation

1. Clone this repository to your local machine or download the script:

   ```bash
   git clone https://github.com/SalmanSamiKhan/news_scraper.git
   cd news_scraper
   ```

2. Install the required Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have Python 3.7+ installed on your machine.

## Usage

To run the script, use the following command in your terminal:

```bash
python scraper.py <date> [options]
```

Where `<date>` is the target date in the `YYYY-MM-DD` format. If no date is provided, today's date will be used by default.

### Arguments

- `date` (optional): The date to scrape articles from, in `YYYY-MM-DD` format. For example: `2024-10-20`. If not provided, today's date will be used.
- `-c, --concurrency` (optional): Specify the maximum number of concurrent requests. Default is `20`. Example: `-c 10` limits the concurrency to 10 requests.
- `-o, --output` (optional): Choose the output file format. Valid options are `csv`, `xlsx`, or `txt`. Default is `csv`. Example: `-o xlsx` saves the data as an Excel file.

### Examples

1. **Scrape articles for today's date and save as CSV (default behavior):**

   ```bash
   python scraper.py
   ```

2. **Scrape articles for a specific date with a concurrency limit of 10 and save as an Excel file:**

   ```bash
   python scraper.py 2024-08-05 -c 10 -o xlsx
   ```

3. **Scrape articles for a specific date and save as a tab-separated text file:**

   ```bash
   python scraper.py 2024-08-05 -o txt
   ```

### Output

The script generates two directories:

- **Data Directory**: Contains the scraped articles saved in the chosen format.
- **Log Directory**: Contains logs of the scraping process, useful for debugging and monitoring.

#### File Structure:

```
data/
    <date>/
        <date>_articles.<output_extension>
log/
    <date>/
        <date>_logs.log
```

Where:


- `<date>` is the specified date or today's date.
- `<output_extension>` is the chosen output file format (e.g., `csv`, `xlsx`, `txt`).


## Script Flow

1. The script fetches article links from the New Age archive page for the specified date.
2. It then fetches the content of each article concurrently.
3. Finally, the scraped data is saved into a file in the desired format.

## Error Handling

- The script will retry fetching each URL up to 3 times if the request fails.
- Any issues will be logged in the `log/<date>/<date>_logs.log` file.