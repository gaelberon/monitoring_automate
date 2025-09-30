"""
daily_monitoring.py

To be scheduled daily, this script aims to:
  1. Pull the content from various sources (incl. papers from Hugging Face's papers page)
  2. Download their PDFs,
  3. Save their information in a JSON file.
"""

# Local resources imports
from websites_specific import extract_article_details_from_websites
from youtube_specific import extract_video_details_from_youtube_channels

def extract_daily_content() -> None:
    """
    Fetches daily content from various sources and sends notifications.
    
    This function performs the following tasks:
    
    1. Extracts articles and papers details from a some websites and sends notifications.
    2. Extracts videos details from some youtube channels and sends notifications.
    """
    extract_article_details_from_websites()
    
    extract_video_details_from_youtube_channels()
    # Add functionality to convert content to voice recorder (commented out for now)
    # convert_to_voice_recorder()  # Uncomment if implemented

if __name__ == "__main__":
    extract_daily_content()