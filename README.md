# Loom Transcript Scraper

An automated tool to extract transcripts and titles from Loom videos and save them to Google Docs.

## Features

- Automated login to Loom
- Batch processing of multiple videos
- Transcript extraction
- Title extraction
- Automatic saving to Google Docs
- Progress tracking
- Detailed logging

## Prerequisites

- Python 3.x
- Google Cloud Platform account with Google Docs API enabled
- Loom account
- Chrome browser

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd loom-scraper
```

2. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/MacOS
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure
```
loom-scraper/
├── scraper.py
├── requirements.txt
├── .env
├── .gitignore
├── logs/
└── credentials/
    └── google-credentials.json
```

## Security & Configuration

### Important Security Notes
- Never commit your `.env` file or Google credentials to GitHub
- Keep your Google Cloud credentials secure and private
- Regularly rotate your credentials for better security
- Add both `.env` and `credentials/` to your `.gitignore` file

### Configuration Steps
1. Create a `.env` file with the following structure:
```
# This is just a template - do not commit the actual .env file!
LOOM_EMAIL="your-email"
LOOM_PASSWORD="your-password"
GOOGLE_DOC_ID="your-google-doc-id"
GOOGLE_CREDENTIALS_PATH="credentials/google-credentials.json"
```

2. Set up your .gitignore:
```
# Add to .gitignore
.env
credentials/
logs/
__pycache__/
*.pyc
```

3. Create a `credentials` folder and place your Google Cloud credentials JSON file there
   - Keep this file secure and private
   - Never share or commit this file
   - Consider using environment variables in production

## Usage

1. Activate the virtual environment:
```bash
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/MacOS
```

2. Run the script:
```bash
python scraper.py
```

3. Check the logs:
```bash
notepad logs\scraper.log
```

## Output Format

The script saves transcripts to Google Docs in the following format:
```
=== Video Title: [Video Title] ===
Video ID: [Video ID]
Extracted on: [Timestamp]

Transcript:
[Transcript content]

---
```

## Browser Configuration

### Playwright Browser Options
- Default: Chrome/Chromium browser in non-headless mode
- Configurable user agent strings to prevent automation detection
- Support for multiple browser types:
  ```python
  # Chrome/Chromium (default)
  browser = p.chromium.launch(headless=False)
  
  # Firefox
  browser = p.firefox.launch(headless=False)
  
  # Webkit (Safari)
  browser = p.webkit.launch(headless=False)
  ```

### User Agent Configuration
- Custom user agents can be configured to avoid scraping detection
- Supports multiple browser identities
- Example configuration:
  ```python
  context = browser.new_context(
      user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  )
  page = context.new_page()
  ```

This flexibility helps prevent automation detection while maintaining stable operation.

## Logging

- All operations are logged to `logs/scraper.log`
- Includes timestamps and detailed error information
- Helps track progress and debug issues

## Advanced Features

## Progress Tracking
- Automatic progress saving after each video
- Resume capability from last processed video
- Progress stored in `progress.txt`
- Error recovery and restart support

## Multi-Document Support
- Automatic distribution across multiple Google Docs
- Configurable document rotation (default: every 144 videos)
- Separate document IDs for different video ranges
- Prevents single document size limitations

## Scroll Management
- Dynamic video loading through automatic scrolling
- Configurable maximum scroll attempts
- Handles Loom's infinite scroll interface
- Ensures all videos are accessible

## Environmental Variables
```bash
# Required .env configurations
LOOM_EMAIL="your-email"
LOOM_PASSWORD="your-password"
GOOGLE_DOC_ID_1="first-doc-id"
GOOGLE_DOC_ID_2="second-doc-id"
GOOGLE_DOC_ID_3="third-doc-id"
GOOGLE_CREDENTIALS_PATH="credentials/google-credentials.json"
```

## Troubleshooting

1. If login fails:
   - Check your Loom credentials in `.env`
   - Ensure stable internet connection
   - Verify Chrome browser installation

2. If Google Docs saving fails:
   - Check Google credentials
   - Verify document ID
   - Ensure API access is enabled

# Technical Implementation

## Playwright Integration
- Utilizes Playwright for robust browser automation
- Handles dynamic content loading and interactions
- Manages element selection and state management
- Provides reliable automation across browser sessions

Key Playwright features used:
```python
# Browser initialization
browser = p.chromium.launch(headless=False)
page = browser.new_page()

# Element selection and interaction
page.wait_for_selector('input[type="email"]')
page.wait_for_load_state('networkidle')

# Dynamic content handling
page.query_selector_all('a[href*="/share/"]')
page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
```

## Additional Technologies
- Python for core functionality
- Google Docs API for content storage
- Logging for operation tracking
- Environment variables for configuration
