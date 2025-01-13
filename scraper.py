import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import logging
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pyperclip

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    filename='logs/scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

########################################
# PROGRESS TRACKING FUNCTIONS
########################################
def read_progress(progress_file="progress.txt"):
    """
    Reads the last processed video index from a file.
    If file doesn't exist or is empty, return 0 (start from the beginning).
    """
    if not os.path.exists(progress_file):
        return 0
    try:
        with open(progress_file, 'r') as f:
            content = f.read().strip()
            return int(content) if content else 0
    except:
        return 0

def write_progress(index, progress_file="progress.txt"):
    """
    Writes the current video index to the file.
    """
    with open(progress_file, 'w') as f:
        f.write(str(index))

########################################
# LOOM LOGIN
########################################
def login_to_loom(page, email, password):
    """Handle Loom login process"""
    try:
        # Navigate to login page
        page.goto('https://www.loom.com/login')
        logging.info("Navigated to Loom login page")
        
        # Wait for and fill email field
        email_field = page.wait_for_selector('input[type="email"]')
        email_field.fill(email)
        email_field.press('Tab')
        
        # Wait briefly for password field to appear
        time.sleep(2)
        
        # Handle password field
        password_field = page.wait_for_selector('input[type="password"]')
        password_field.fill(password)
        
        # Submit the form
        password_field.press('Enter')
        
        # Wait for login to complete
        page.wait_for_load_state('networkidle')
        logging.info("Successfully logged into Loom")
        
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        raise

########################################
# GET VIDEO TITLE
########################################
def get_video_title(page):
    """Extract both human-readable title and video ID"""
    title_info = {}
    try:
        page.wait_for_load_state('networkidle')
        time.sleep(2)  # Wait for content to load

        # Try direct text extraction from <h1> or another known element
        try:
            title_element = page.wait_for_selector('h1', timeout=5000)  # Adjust selector if needed
            readable_title = title_element.inner_text().strip()
            if not readable_title:
                raise ValueError("Empty title text")
            title_info['readable_title'] = readable_title
            logging.info(f"Extracted readable title: {readable_title}")
        except Exception as e:
            logging.warning(f"Direct heading extraction failed: {str(e)}")

            # Fallback: Use the <title> from the browser’s tab
            page_title = page.title()
            if '– Loom' in page_title:
                readable_title = page_title.split('– Loom')[0].strip()
            elif '- Loom' in page_title:
                readable_title = page_title.split('- Loom')[0].strip()
            else:
                readable_title = page_title.strip()

            if not readable_title:
                readable_title = "Untitled Video"
            title_info['readable_title'] = readable_title
        
    except Exception as e:
        logging.warning(f"Failed to get readable title: {str(e)}")
        title_info['readable_title'] = "Untitled Video"

    # Grab the video ID from the URL
    try:
        video_url = page.url
        video_id = video_url.split('/')[-1]
        title_info['video_id'] = video_id
        logging.info(f"Extracted video ID: {video_id}")
    except Exception as e:
        logging.error(f"Failed to get video ID: {str(e)}")
        title_info['video_id'] = "unknown-id"
    
    return title_info

########################################
# GOOGLE DOCS SETUP
########################################
def init_google_docs():
    """Initialize Google Docs API client"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_CREDENTIALS_PATH'),
            scopes=['https://www.googleapis.com/auth/documents']
        )
        return build('docs', 'v1', credentials=credentials)
    except Exception as e:
        logging.error(f"Failed to initialize Google Docs: {str(e)}")
        raise

########################################
# APPEND CONTENT TO GOOGLE DOC
########################################
def append_to_google_doc(service, doc_id, title_info, transcript):
    """Append content to the specified Google Doc."""
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_content = (
            f"\n=== Video Title: {title_info['readable_title']} ===\n"
            f"Video ID: {title_info['video_id']}\n"
            f"Extracted on: {timestamp}\n\n"
            f"Transcript:\n{transcript}\n\n"
            f"---\n\n"
        )
        
        requests = [
            {
                'insertText': {
                    'location': {'index': 1},
                    'text': formatted_content
                }
            }
        ]
        
        service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        logging.info(f"Added title/transcript for: {title_info['readable_title']} ({title_info['video_id']})")
    except Exception as e:
        logging.error(f"Failed to update Google Doc: {str(e)}")
        raise

########################################
# DETERMINE WHICH DOC TO USE
########################################
def get_doc_id_for_video(video_index):
    """
    Splits videos among three docs.
    For example:
      - 0..143  go to doc #1
      - 144..287 go to doc #2
      - 288..431 go to doc #3
    """
    doc_id_1 = os.getenv('GOOGLE_DOC_ID_1')
    doc_id_2 = os.getenv('GOOGLE_DOC_ID_2')
    doc_id_3 = os.getenv('GOOGLE_DOC_ID_3')
    
    if video_index < 144:
        return doc_id_1
    elif video_index < 288:
        return doc_id_2
    else:
        return doc_id_3

########################################
# SCROLL UNTIL VIDEO APPEARS
########################################
def scroll_until_video_appears(page, target_video_index, max_scrolls=140):
    """
    Scrolls the page multiple times so that more Loom videos can load.
    target_video_index = zero-based index (e.g., 60 for video #61)
    max_scrolls = how many times to scroll before giving up.
    """
    for scroll_count in range(max_scrolls):
        video_links = page.query_selector_all('a[href*="/share/"]')
        if len(video_links) > target_video_index:
            return True
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        logging.info(f"Scrolling attempt #{scroll_count + 1}")
        time.sleep(3)
    return False

########################################
# MAIN LOGIC
########################################
def main():
    email = os.getenv('LOOM_EMAIL')
    password = os.getenv('LOOM_PASSWORD')
    
    logging.info("Starting Loom transcript scraper with skip-if-no-transcript logic")
    
    # Initialize Google Docs service
    docs_service = init_google_docs()

    # Total videos (adjust if needed)
    total_videos = 432  # or 431, or however many you have

    # Read last processed index from progress.txt
    last_processed_index = read_progress()
    logging.info(f"Resuming from video index #{last_processed_index}")

    try:
        with sync_playwright() as p:
            # Launch Chromium in non-headless mode
            browser = p.chromium.launch(headless=False)
            
            # If you'd like a custom user agent, do something like:
            # context = browser.new_context(
            #     user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ..."
            # )
            # page = context.new_page()

            page = browser.new_page()
            
            # Login to Loom
            login_to_loom(page, email, password)
            
            # Wait a bit to ensure login is stable
            time.sleep(5)
            
            # Loop from 'last_processed_index' to 'total_videos'
            for video_num in range(last_processed_index, total_videos):
                # Navigate to the Loom videos page
                page.goto('https://www.loom.com/looms/videos')
                page.wait_for_load_state('networkidle')
                time.sleep(5)  # Give page time to load
                
                # Attempt to scroll until the needed video is in the DOM
                if not scroll_until_video_appears(page, video_num, max_scrolls=140):
                    logging.error(f"Video #{video_num + 1} not found even after scrolling.")
                    continue

                # Now we should have enough links in the DOM
                video_links = page.query_selector_all('a[href*="/share/"]')
                if video_num < len(video_links):
                    current_video = video_links[video_num]
                    current_video.click()
                    logging.info(f"Clicked video #{video_num + 1}")
                    time.sleep(3)  # Wait for the video page to load

                    # Extract video title info
                    title_info = get_video_title(page)

                    # 1) Find and click Transcript tab
                    try:
                        transcript_tab = page.wait_for_selector('text=Transcript', timeout=5000)
                        transcript_tab.click()
                        logging.info("Clicked transcript tab")
                        time.sleep(2)  # Wait for transcript to load
                    except:
                        logging.warning("Transcript tab not found. Skipping this video.")
                        # go to next video
                        continue

                    # 2) Find and click Copy button
                    try:
                        copy_button = page.wait_for_selector('button:has-text("Copy")', timeout=5000)
                        copy_button.click()
                        logging.info("Clicked copy button")
                        time.sleep(2)  # Wait for copy to complete
                    except:
                        logging.warning("Copy button not found. Skipping this video.")
                        continue
                    
                    # 3) Get transcript from clipboard
                    transcript = pyperclip.paste().strip()
                    if not transcript:
                        logging.warning(f"Transcript is empty for video #{video_num + 1}. Skipping this video.")
                        continue

                    # Determine which Doc ID to use
                    target_doc_id = get_doc_id_for_video(video_num)

                    # Append to the correct Google Doc
                    append_to_google_doc(docs_service, target_doc_id, title_info, transcript)

                    # Mark progress: we finished this video
                    write_progress(video_num + 1)
                    logging.info(f"Progress saved. Just finished video #{video_num + 1}.")
                    
                    # Optional short delay
                    time.sleep(3)
                else:
                    logging.error(f"Index {video_num} out of range in video_links. Found only {len(video_links)} links.")
            
            logging.info("Completed processing videos (or ended early).")
            time.sleep(3)
            browser.close()

    except Exception as e:
        logging.error(f"An error occurred in main: {str(e)}")
        raise


if __name__ == "__main__":
    main()


