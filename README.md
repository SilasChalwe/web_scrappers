# Italian Supreme Court (Corte di Cassazione) Document Scraper

## Project Overview

A Python-based web scraper that automatically collects legal documents from the Italian Supreme Court (Corte di Cassazione) website. The tool extracts metadata, downloads PDF documents, and stores everything in an organized SQLite database.

## Features

* Automated Scraping: Uses Selenium for browser automation to navigate through court documents
* Metadata Extraction: Captures comprehensive document information including ECLI numbers, dates, case numbers, judges, and more
* PDF Download: Automatically downloads full PDF documents with proper URL construction
* Database Storage: SQLite backend with structured schema for easy querying
* Robust Error Handling: Gracefully handles network issues and missing data
* Headless Operation: Can run in background without GUI

## Architecture

```
scrapper/
├── pcdb.py              # Main scraping engine
├── db_reader.py         # Database query utility
├── scraper_data.db      # SQLite database (auto-generated)
├── downloads/           # PDF storage directory
├── venv/                # Python virtual environment
└── .gitignore           # Version control exclusions
```

## Technical Stack

* Python 3 with BeautifulSoup4 for HTML parsing
* Selenium WebDriver with Firefox for browser automation
* SQLite3 for lightweight data storage
* Requests for HTTP operations
* urllib3 with SSL warning suppression

## Database Schema

```sql
CREATE TABLE documents (
    id TEXT PRIMARY KEY,          -- Unique document identifier
    category TEXT,                -- Civil/Criminal classification
    section TEXT,                 -- Court section (Prima, Seconda, etc.)
    kind TEXT,                    -- Document kind
    type TEXT,                    -- Document type (Ordinanza, Sentenza)
    number TEXT,                  -- Case number
    date TEXT,                    -- Decision date
    ecli TEXT,                    -- European Case Law Identifier
    president TEXT,               -- Presiding judge
    relator TEXT,                 -- Reporting judge
    pdf_path TEXT                 -- Local PDF file path
)
```

## Installation & Setup

### 1. Prerequisites

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3 python3-pip firefox-geckodriver

# Or for Termux:
pkg install python python-pip firefox-geckodriver
```

### 2. Clone and Setup

```bash
# Clone repository
git clone git@github.com:SilasChalwe/web_scrappers.git
cd web_scrapper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install selenium beautifulsoup4 requests
```

### 3. Configuration

```bash
# Set your Git identity
git config --global user.name "Silas Chalwe"
git config --global user.email "silaschalwe@outlook.com"

# Configure Geckodriver path if needed
# Update in pcdb.py: service = Service(executable_path="/your/path/to/geckodriver")
```

## Usage

### Basic Operation

```bash
# Run the scraper (default: 5 pages)
python3 pcdb.py

# Run with custom page limit
python3 pcdb.py  # Edit max_pages parameter in run_scraper() function
```

### Database Operations

```bash
# View database contents
python3 db_reader.py

# Query specific documents
python3 -c "
import sqlite3
conn = sqlite3.connect('scraper_data.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM documents LIMIT 5;')
print(cursor.fetchall())
conn.close()
"
```

## Output Structure

```
downloads/
├── CIV_2023_00123.pdf
├── CIV_2023_00124.pdf
└── ...

scraper_data.db
├── documents table with metadata
└── Full-text search capabilities
```

## URL Construction Logic

The scraper intelligently builds PDF URLs using this pattern:

```
https://www.italgiure.giustizia.it/xway/application/nif/clean/hc.dll?
verbo=attach&
db={db}&
id=./{YYYYMMDD}/{db}@{section_code}@a{year}@n{number}@t{type_code}.clean.pdf
```

Section Mapping:

* PRIMA → s10, SECONDA → s20, TERZA → s30
* QUARTA → s40, QUINTA → s50, SESTA → s60
* SETTIMA → s70, UNITE → su0

## Important Notes

### Legal & Ethical Considerations

* Respect robots.txt: Check website's terms of service
* Rate limiting: Built-in delays to avoid overloading servers
* Data usage: Only for personal/research purposes
* Copyright: Some documents may have usage restrictions

### Technical Limitations

* Website structure changes may break scraping logic
* SSL certificate validation disabled for compatibility
* Requires stable internet connection
* Firefox/Geckodriver must be properly installed

## Maintenance

### Regular Updates

```bash
# Update dependencies
pip install --upgrade selenium beautifulsoup4 requests

# Backup database
cp scraper_data.db scraper_data_backup_$(date +%Y%m%d).db

# Clear old downloads (optional)
rm -rf downloads/*.pdf
```

### Troubleshooting

1. "Geckodriver not found": Install geckodriver and update path in pcdb.py
2. SSL warnings: Already suppressed, but ensure network connectivity
3. Empty results: Check if website structure has changed
4. Permission errors: Ensure write access to downloads/ directory

## Future Enhancements

* Multi-threading for faster downloads
* Support for Criminal (Penale) section
* Export to CSV/JSON formats
* Web interface for querying
* Automated daily scraping with cron
* Docker containerization

## License

Educational/Research Use Only - Not for Commercial Distribution

## Author

Silas Chalwe - [silaschalwe@outlook.com](mailto:silaschalwe@outlook.com)

## Acknowledgments

* Italian Ministry of Justice for public access to case law
* Selenium and BeautifulSoup communities
* Open-source Python ecosystem

---

This tool is designed for legal research and educational purposes. Always verify official sources for authoritative legal documents.
