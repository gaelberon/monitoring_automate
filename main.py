# -*- coding: utf-8 -*-

import os
import pandas as pd
import requests
import arxiv
import vertexai
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
# File Paths
CLIENT_SECRET_FILE = 'client_secret_413915175774-jdf1o37s414ifkr4dulc8erhnjlinn89.apps.googleusercontent.com.json'
TOKEN_FILE = 'token.json'
SERVICE_ACCOUNT_FILE = 'healthy-fuze-437202-j9-e32d9ee30852.json'
TEMPLATES_DIR = 'templates'
OUTPUT_HTML_FILE = 'monitoring_report.html'

# Google Cloud & Vertex AI
GCP_PROJECT_ID = 'healthy-fuze-437202-j9'
GCP_LOCATION = 'us-central1'
PRIMARY_MODEL_NAME = 'gemini-1.5-pro-preview-0409'
SECONDARY_MODEL_NAME = 'gemini-1.0-pro'

# YouTube API
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
YOUTUBE_SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# --- SOURCES CONFIGURATION ---
# Add YouTube channel IDs with their type ('techno', 'debate', 'entertainment')
YOUTUBE_SOURCES = {
    # 'UC_3_j_MWdGjK_v9E2e5M-ag': 'techno', # Example: Add a tech channel ID
    # 'UC-3jI4T0gG3I-qC-iF4i4sw': 'debate', # Example: Add a debate channel ID
}
ARXIV_QUERY = 'cat:cs.AI OR cat:cs.LG'
# This is an example URL, change it to the page you want to scrape
ACTUIA_URL = 'https://www.actuia.com/tag/intelligence-artificielle/'


# --- AUTHENTICATION & INITIALIZATION ---

def get_youtube_credentials():
    """Handles OAuth 2.0 for YouTube API. Will trigger browser auth on first run."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, YOUTUBE_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, YOUTUBE_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds

def initialize_vertex_ai():
    """Initializes Vertex AI client."""
    credentials = ServiceAccountCredentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION, credentials=credentials)
    primary_model = GenerativeModel(PRIMARY_MODEL_NAME)
    secondary_model = GenerativeModel(SECONDARY_MODEL_NAME)
    print(f"Vertex AI initialized. Primary model: {PRIMARY_MODEL_NAME}, Secondary model: {SECONDARY_MODEL_NAME}")
    return primary_model, secondary_model


# --- CONTENT FETCHING ---

def fetch_youtube_videos(youtube_client, channel_id, channel_type, max_results=2):
    """Fetches the latest videos from a YouTube channel."""
    request = youtube_client.search().list(
        part="snippet",
        channelId=channel_id,
        maxResults=max_results,
        order="date",
        type="video"
    )
    response = request.execute()
    
    videos = []
    for item in response.get('items', []):
        video_id = item['id']['videoId']
        video_info = {
            'source': 'YouTube',
            'type': channel_type,
            'title': item['snippet']['title'],
            'url': f'https://www.youtube.com/watch?v={video_id}',
            'date': item['snippet']['publishedAt'].split('T')[0],
            'channelName': item['snippet']['channelTitle'],
            'description': item['snippet']['description'],
            'transcript': 'N/A' # Placeholder; a dedicated library like youtube-transcript-api would be needed for actual transcripts.
        }
        videos.append(video_info)
    print(f"Fetched {len(videos)} videos from YouTube channel {item['snippet']['channelTitle']}.")
    return videos

def fetch_arxiv_papers(query, max_results=5):
    """Fetches recent papers from arXiv."""
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    papers = []
    for result in search.results():
        papers.append({
            'source': 'arXiv',
            'type': 'paper',
            'title': result.title,
            'url': result.pdf_url,
            'authors': [str(author) for author in result.authors],
            'summary_original': result.summary.replace('\n', ' '), # This is the abstract
            'date': result.published.strftime('%Y-%m-%d')
        })
    print(f"Fetched {len(papers)} papers from arXiv.")
    return papers

def fetch_actuia_articles(url, max_articles=3):
    """Fetches article summaries from a listings page on ActuIA."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = []
        # NOTE: These selectors are based on ActuIA's structure as of late 2024 and may break if the site is updated.
        for article_element in soup.select('div.item-details')[:max_articles]:
            title_element = article_element.select_one('h3.entry-title a')
            content_element = article_element.select_one('div.td-excerpt')
            
            if title_element and content_element:
                articles.append({
                    'source': 'ActuIA',
                    'type': 'article',
                    'title': title_element.text.strip(),
                    'url': title_element['href'],
                    'content': content_element.text.strip(),
                    'author': 'N/A', # Author is not easily available on listing page
                    'date': 'N/A',   # Date is not easily available on listing page
                })
        print(f"Fetched {len(articles)} articles from ActuIA.")
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching ActuIA articles: {e}")
        return []

# --- SUMMARIZATION ---

def get_prompt_for_item(item):
    """Selects the correct prompt template and formats it with item data."""
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    
    if item['source'] == 'YouTube':
        if item['type'] == 'techno':
            template = env.get_template('prompt_summarize_techno_youtube_chanel.md')
        elif item['type'] == 'debate':
            template = env.get_template('prompt_summarize_debate_youtube_chanel.md')
        elif item['type'] == 'entertainment':
            template = env.get_template('prompt_summarize_entertainment_youtube_chanel.md')
        else:
            return None
        return template.render(
            channelName=item['channelName'],
            title=item['title'],
            description=item['description'],
            date=item['date'],
            transcript=item['transcript'],
            url=item['url']
        )

    elif item['source'] == 'arXiv':
        template = env.get_template('prompt_summarize_HF_paper_template.md')
        # The original template is missing a placeholder for the content.
        # We will dynamically add the paper's abstract to the prompt text.
        prompt_text = template.render(
            title=item['title'],
            authors=", ".join(item['authors'])
        )
        prompt_text += f"\n\nAbstract: {item['summary_original']}"
        return prompt_text
        
    elif item['source'] == 'ActuIA':
        template = env.get_template('prompt_summarize_ActuIA_articles_template.md')
        return template.render(
            title=item['title'],
            author=item.get('author', 'N/A'),
            date=item.get('date', 'N/A'),
            content=item['content']
        )
        
    return None

def summarize_item(item, primary_model, secondary_model):
    """
    Summarizes a single content item using a primary and secondary LLM.
    If both fail, returns a specific failure message.
    """
    prompt = get_prompt_for_item(item)
    if not prompt:
        print(f"No prompt template found for item: {item['title']}")
        return "SUMMARIZATION_FAILED: No suitable prompt template found."

    summary = None
    
    # Try Primary Model
    try:
        print(f"  -> Summarizing with primary model ({PRIMARY_MODEL_NAME})...")
        response = primary_model.generate_content(prompt)
        summary = response.text.strip()
    except Exception as e:
        print(f"  -> Primary model failed for '{item['title']}': {e}")
        summary = None

    # If primary failed or returned empty, try secondary model
    if not summary:
        try:
            print(f"  -> Summarizing with secondary model ({SECONDARY_MODEL_NAME})...")
            response = secondary_model.generate_content(prompt)
            summary = response.text.strip()
        except Exception as e2:
            print(f"  -> Secondary model also failed for '{item['title']}': {e2}")
            summary = None

    # THE CORE CHANGE: If both failed, set an error message
    if not summary:
        print(f"  -> Summarization failed for '{item['title']}'.")
        return "SUMMARIZATION_FAILED: Both LLM models failed to generate a summary for this item."
    
    print(f"  -> Summarization successful for '{item['title']}'.")
    return summary


# --- REPORT GENERATION ---

def generate_html_report(processed_items, output_path):
    """Generates an HTML report from the list of processed items."""
    if not processed_items:
        print("No items to report.")
        return

    df = pd.DataFrame(processed_items)
    
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("email_template_monitoring_content.html")
    
    header_html = "".join(f'<th style="border: 1px solid #ddd; padding: 8px; text-align: left; background-color: #f2f2f2;">{col}</th>' for col in df.columns)
    
    body_html = ""
    for _, row in df.iterrows():
        body_html += '<tr style="background-color: #ffffff;">'
        for item in row:
            safe_item = str(item).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
            body_html += f'<td style="border: 1px solid #ddd; padding: 8px; vertical-align: top;">{safe_item}</td>'
        body_html += "</tr>"

    html_content = template.render(htmlTableHeader=header_html, htmlTableBody=body_html)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"\nReport generated successfully: {output_path}")

# --- MAIN WORKFLOW ---

def main():
    """Main function to run the entire monitoring and summarization pipeline."""
    print("--- Starting Automated Technology Monitoring ---")

    # 1. Initialize services
    youtube = None
    if YOUTUBE_SOURCES:
        try:
            youtube_creds = get_youtube_credentials()
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=youtube_creds)
            print("YouTube API client initialized.")
        except Exception as e:
            print(f"Could not initialize YouTube API client. Skipping YouTube sources. Error: {e}")
            
    primary_model, secondary_model = initialize_vertex_ai()
    
    all_content = []
    
    # 2. Fetch content from all configured sources
    print("\n--- Fetching Content ---")
    if youtube:
        for channel_id, channel_type in YOUTUBE_SOURCES.items():
            try:
                all_content.extend(fetch_youtube_videos(youtube, channel_id, channel_type))
            except Exception as e:
                print(f"Failed to fetch from YouTube channel {channel_id}: {e}")

    try:
        all_content.extend(fetch_arxiv_papers(ARXIV_QUERY))
    except Exception as e:
        print(f"Failed to fetch from arXiv: {e}")

    try:
        all_content.extend(fetch_actuia_articles(ACTUIA_URL))
    except Exception as e:
        print(f"Failed to fetch from ActuIA: {e}")

    if not all_content:
        print("\nNo content fetched from any source. Exiting.")
        return

    print(f"\nTotal items fetched: {len(all_content)}")

    # 3. Summarize each piece of content
    print("\n--- Summarizing Content ---")
    processed_items = []
    for item in all_content:
        print(f"Processing item: {item['title']}")
        summary = summarize_item(item, primary_model, secondary_model)
        
        report_item = {
            'Source': item['source'],
            'Title': f"<a href='{item['url']}' target='_blank'>{item['title']}</a>",
            'Date': item.get('date', 'N/A'),
            'Summary': summary
        }
        processed_items.append(report_item)

    # 4. Generate the final HTML report
    print("\n--- Generating Report ---")
    generate_html_report(processed_items, OUTPUT_HTML_FILE)
    
    print("\n--- Monitoring process finished. ---")


if __name__ == "__main__":
    # Note on YouTube Authentication:
    # If you add YouTube channels to the configuration, the first time you run this script,
    # it will open a browser window for you to log in and authorize access to your YouTube account.
    # This will create a 'token.json' file to be used for subsequent runs.
    main()