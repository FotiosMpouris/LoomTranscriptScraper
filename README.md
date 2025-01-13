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

## Configuration

1. Create a `.env` file with the following content:
```
LOOM_EMAIL="your-email"
LOOM_PASSWORD="your-password"
GOOGLE_DOC_ID="your-google-doc-id"
GOOGLE_CREDENTIALS_PATH="credentials/google-credentials.json"
```

2. Place your Google Cloud credentials JSON file in the `credentials` folder

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

## Error Handling

- The script includes comprehensive error handling for network issues
- Progress is saved after each video
- Detailed logging for troubleshooting
- Automatic retries for common failures

## Logging

- All operations are logged to `logs/scraper.log`
- Includes timestamps and detailed error information
- Helps track progress and debug issues

## Known Limitations

- Requires Chrome browser
- Must have valid Loom login credentials
- Network-dependent operation
- Rate limiting may apply for large numbers of videos

## Troubleshooting

1. If login fails:
   - Check your Loom credentials in `.env`
   - Ensure stable internet connection
   - Verify Chrome browser installation

2. If Google Docs saving fails:
   - Check Google credentials
   - Verify document ID
   - Ensure API access is enabled

## Contributing

[Add your contribution guidelines here]

## License

[Add your chosen license here]# LoomTranscriptScraper
