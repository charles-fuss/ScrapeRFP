# RFP Scraper

This Python script is designed to scrape Request for Proposal (RFP) data from two websites, RFPMart and Bidnet, for different keywords related to software systems, such as CMMS, UAMS, UCIMS, and Utility Billing. The script uses Selenium WebDriver to automate the browsing and extraction of data from the websites and saves the results to text files. It then sends the results in an email to specified recipients.

## Features

- Scrape RFP data for various software systems
- Save results to text files
- Deduplicate results based on prior searches
- Send an email with the results in HTML format

## Requirements

- Python 3.x
- Selenium WebDriver
- Google Chrome or other compatible browser

## Installation

1. Clone the repository or download the code snippets provided.
2. Combine the two code snippets into a single Python file, e.g., `rfp_scraper.py`.
3. Install the required Python libraries by running the following command:

```bash
pip install selenium
