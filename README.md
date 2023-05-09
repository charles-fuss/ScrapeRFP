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
pip install -m requirements.txt
```

## Customization
You can customize the script by modifying the keywords, search functions, or output formatting as needed. Be sure to update the email subject and recipients as well. Also, you must change the file tree for the logs to upload to to whatever you've named your root folder.

## Disclaimer
Please note that web scraping may be against the terms of service for some websites. This script is provided for educational purposes only. Use at your own risk and ensure you have permission to access and scrape the websites in question.

## Problems I have yet to address

 - .txt log files are essentially hardcoded to the current searches. Isn't hard to change for new searches, but still works.
 - The script doesn't omit duplicates from the past search. 
 - The file tree is custom to my file system. Sorry :(
