"""
youtube_specific.py


"""

# Standard library imports
import os
# import time
from datetime import datetime
import json

# Third-party imports
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
# Import Youtube API libraries
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

# Local resources imports
from utils import config
# from utils import summarize_video_from_transcript
from utils import get_value2_on_key2_from_value1_on_key1_in_channels_list
# from utils import filter_unknown_items
# from utils import json_to_html
from utils import extract_node_values
# from utils import send_email
from utils import process_list_of_items

def get_youtube_client():
    """
    Retrieves a YouTube Data API client instance.

    This function handles authentication and token management.

    Returns:
        A YouTube API client instance.
    """
    
    creds = None
    # Check if token.json exists and load credentials from it
    if os.path.exists(config["youtube.api.service.token.file"]):
        try:
            print("Try to get the Youtube service credentials from the Youtube API credentials file, token.json.") # For Debug Only
            flow = InstalledAppFlow.from_client_secrets_file(
                config["youtube.api.service.credentials.file"],
                config["youtube.api.service.scopes"])
            # Load token from file
            creds = flow.run_local_server(port=0)  # This will open a browser window for authentication
            # Save the credentials for the next run
            with open(config["youtube.api.service.token.file"], 'w') as token:
                token.write(creds.to_json())
            print(f"Successfully loaded credentials from the Youtube API credentials file, token.json.")
        except Exception as e:
            print(f"Error loading Youtube service credentials from the Youtube API credentials file: {e}")
    
    # Handle the case where credentials are invalid or missing, try using service account json file if exists.
    if not creds or not creds.valid:
        print("Could not load Youtube service credentials from the Youtube API credentials file, try using service account json file if exists.") # For Debug Only
        # Check if a service account exists to retrieve Youtube Service
        if os.path.exists(config["google.service.account.key.json.file"]):
            try:
                print("Try to get the Youtube service credentials from service account json file.") # For Debug Only
                creds = Credentials.from_service_account_file(
                    config["google.service.account.key.json.file"],
                    scopes=config["youtube.api.service.scopes"])
            except Exception as e:
                print(f"Error loading service account credentials: {e}")
    
    # Handle the case where credentials are invalid or missing, let the user log in.
    if not creds or not creds.valid:
        print("Credentials are invalid or missing.") # For Debug Only
        if creds and creds.expired and creds.refresh_token:
            print("Credentials have expired, must refresh them.") # For Debug Only
            creds.refresh(Request())
        else:
            print("Load flow fromclient secrets file.") # For Debug Only
            flow = InstalledAppFlow.from_client_secrets_file(
                config["youtube.api.service.credentials.file"],
                config["youtube.api.service.scopes"])
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(config["youtube.api.service.token.file"], 'w') as token:
            token.write(creds.to_json())
    # Proceed with using the YouTube API
    else:
        print("Credentials are valid!")
        
    # Create a YouTube API client instance using the obtained credentials
    youtube = build(config["youtube.api.service.name"],
                    config["youtube.api.service.version"],
                    credentials=creds)

    return youtube

def extract_youtube_transcript(video_id:str) -> str:
    """
    Extracts the transcript from a YouTube video using web scraping.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        str: The extracted transcript, or None if no transcript is found.
    """

    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the transcript element (this may vary depending on YouTube's HTML structure)
    transcript_element = soup.find('div', class_='ytp-transcript-text')

    if transcript_element:
        transcript = transcript_element.get_text(separator='\n')
        return transcript
    else:
        return None

def pull_new_videos_from_channel(youtube_service: str,
                                 channel_id: str,
                                 channel_name: str,
                                 data_file_path: str) -> List[Dict]:
    """
    
    **Args:**
        youtube_service (str): A YouTube API client instance.
        channel_id (str): The ID of the channel to retrieve videos from.
        channel_name (str): The name of the Youtube channel.
        data_file_path (str): Path including the file name for json data file.
        
    **Returns:**
        A list of dictionaries. Each dictionary is a video that contains the following attributes:
            * `channelName (str)`: The name of the Youtube channel where the video was published,
            * `title (str)`: The title of the video,
            * `description (str)`: The description of the video,
            * `date (str)`: The date of the video,
            * `thumbnailUrl (str)`: The URL of the thumbnail of the video,
            * `id (str)`: The ID of the video,
            * `link (str)`: The URL of the video,
            * `transcript (str)`: The transcript of the video (if exists).
    """
    
    # Get the channel's "uploads" playlist ID
    # Channel ID for radionova
    # channel_id = config["youtuve.api.radionova.channel.id"]
    # 
    # request = youtube_service.search().list(
    #     part="snippet",
    #     channelId=channel_id,
    #     maxResults=500,
    #     order="date"
    #     )
    # response = request.execute()
    # for item in response['items']:
    #     title = item['snippet']['title']
    #     description = item['snippet']['description']
    #     publish_date = item['snippet']['publishedAt']
    #     print(f"Title: {title}")
    #     print(f"Description: {description}")
    #     print(f"Published at: {publish_date}\n")
    
    # First, get the channel's "uploads" playlist ID
    try:
        channel_response = youtube_service.channels().list(
            part = "contentDetails",
            id = channel_id
        ).execute()
    
    except Exception as e:
        print(f"🚨 An error occurred while processing an article!")
        print(f"Error details: {e}")
        # Optional: print the HTML snippet that caused the error to inspect it
        # print(f"Problematic HTML: {insurance_times_uk_article_div}") 
        return # Skip to the next article

    if channel_response and "items" in channel_response:
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    else:
        return
    
    # Initialize local variables
    playlist_response = None
    # channel_videos: A list of dictionaries, each representing a video with the following details to store:
    #         - channelName: The name of the Youtube channel where the video was published.
    #         - title: The video's title.
    #         - description: The video's description.
    #         - date: The video's publication date (from field 'publishedAt').
    #         - thumbnailUrl: The URL of the video's thumbnail.
    #         - id: The ID of the video.
    #         - link: The URL of the video (from field 'url').
    #         - transcript: The video's transcript (if available).
    #         - summary: The video's summary (if available).
    channel_videos: List[Dict[str, str, str, str, str, str, str, str, str]] = []
    seen_video_ids = set() # Set to track previously seen Youtube channel's videos IDs
    # original_known_ids = set() # Track originally known video IDs for comparison
    # length_seen_video_ids = 0 # Set to compare the new videos with the already known
    
    # Check if an existing json data file exists and load previously seen videos (if any)
    # print(f"data_file_path: {data_file_path}") # For Debug Only
    if os.path.isfile(data_file_path) is True:
        # Read JSON file and load the list of videos already treated
        with open(data_file_path) as fp:
            # Extract the list of IDs for the videos already treated
            seen_video_ids = extract_node_values(json.load(fp), config["key.json.id"]) # Set to track seen videos IDs
        # print(f"Already seen IDs: {', '.join(seen_ids)}") # For Debug Only
        # original_known_ids = seen_video_ids.copy()
        # print(f"Already known IDs: {', '.join(original_known_ids)}") # For Debug Only
        # Calculate the number of videos already treated
        # length_seen_video_ids = len(seen_video_ids)
        # Print the list of IDs for the videos already treated
        # print(f"List of videos already treated: {seen_ids}") # For Debug Only
    
    # Download the list of videos from the channel's "uploads" playlist
    try:
        playlist_response = youtube_service.playlistItems().list(
            playlistId = uploads_playlist_id,
            part = "snippet,contentDetails",
            maxResults = 50
        ).execute()
    except Exception as e:
        print(f"Failed to download the list of video from channel {channel_name}")
        print(f"With error {e}")
        raise(e)
    
    # Process videos in reverse order (latest first)
    # iter_video = 1 # For Debug Only
    # Start from the end of the list of videos
    # for current_video_index in range(len(playlist_response['items']) - 1, -1, -1):
    #     curr_video = playlist_response['items'][current_video_index]
    for current_video_index in range(len(playlist_response['items'])):
        # print(f"Length of the list of videos: {len(playlist_response['items'])}") # For Debug Only
        # print(f"Current index: {len(playlist_response['items'])-1-current_div_index}") # For Debug Only
        # print(f"Dealing with video of index #{len(playlist_response['items'])-1-current_div_index}") # For Debug Only
        curr_video = playlist_response['items'][len(playlist_response['items'])-1-current_video_index]
        
        # Extract video ID and URL
        video_id = curr_video["snippet"]["resourceId"].get("videoId")
        if not video_id:
            print(f"Video ID not found for a video in {channel_name} channel")
            continue
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        
        # video_id = ""
        # video_url = ""
        # if curr_video["snippet"]["resourceId"]["videoId"]:
        #     video_id = curr_video["snippet"]["resourceId"]["videoId"]
        #     video_url = f'https://www.youtube.com/watch?v={curr_video["snippet"]["resourceId"]["videoId"]}'
        # else:
        #     print(f"Video ID not found for a video in {channel_name} channel")
        #     continue
        # print(f"=> Video ID: {video_id}") # For Debug Only
        # print(f"=> Video URL: {video_url}") # For Debug Only
        
        # Skip duplicates based on video ID
        if video_id in seen_video_ids:
            # print(f"Duplicate video detected with ID {video_id}, skipping.") # For Debug Only
            continue
        seen_video_ids.add(video_id) # Add ID to set of seen IDs
        
        # For Debug Only
        # if video_id != "UUHIBA9FurU":
        #     break
        
        # Extract video details
        video_title = curr_video['snippet'].get('title')
        if not video_title:
            print(f"Title not found for a video in {channel_name} channel")
        video_description = curr_video["snippet"].get("description")
        if not video_description:
            print(f"Video description not found for a video in {channel_name} channel")
        video_date = curr_video["snippet"].get("publishedAt")
        if not video_date:
            print(f"Video date not found for a video in {channel_name} channel")
        video_thumbnailUrl = curr_video['snippet']['thumbnails'].get('default', {}).get('url')
        if not video_thumbnailUrl:
            print(f"Video thumbnail URL not found for a video in {channel_name} channel")
        
        # Create a dictionary to store video information
        video = {
            config["key.json.channel.name"]: channel_name,
            config["key.json.title"]: video_title,
            config["key.json.description"]: video_description,
            config["key.json.date"]: video_date,
            config["key.json.thumbnail.url"]: video_thumbnailUrl,
            config["key.json.id"]: video_id,
            config["key.json.link"]: video_url
        }
        
        # Try to get the transcript
        try:
            # DOESN'T WORK AS THE TRANSCRIPT IS NOT POPULATED THROUGH THE YOUTUBE API
            # transcript_response = youtube_service.captions().list(
            #     videoId=video['id'],
            #     part='snippet').execute()
            # 
            # if transcript_response['items']:
            #     video[config["key.json.transcript"]] = transcript_response['items'][0]['snippet']['text']
            # else:
            #     video[config["key.json.transcript"]] = None  # Indicate that no transcript is available
            video[config["key.json.transcript"]] = extract_youtube_transcript(video['id'])
        except Exception as e:
            print(f"Error getting transcript for video {video['id']}: {e}")
            video[config["key.json.transcript"]] = None
        
        # Add the current video details to the output list of videos information
        channel_videos.insert(0, video)
    
        # if iter_video > 1: # For Debug Only
        #     break # For Debug Only
        # iter_video += 1 # For Debug Only
        
    # Returns the built list of videos (dictionaries)
    return channel_videos
    
def process_videos_from_channel(youtube_service: str,
                                channel_id: str,
                                channel_name: str,
                                recipients: list,
                                smtp_server_details: Dict,
                                # sender: str,
                                # sender_password: str,
                                # smtp_server: str,
                                # smtp_port: str,
                                data_file_path: str,
                                summarize_it: bool = True) -> None:
    """
    Retrieves and processes a list of videos from a YouTube channel.

    This function retrieves videos from a YouTube channel, extracts relevant information,
    and potentially generates summaries. It also handles storing video data and sending email notifications.

    **Args:**
        youtube_service (str): A YouTube API client instance.
        channel_id (str): The ID of the channel to retrieve videos from.
        channel_name (str): The name of the Youtube channel.
        recipients (list): A list of email addresses to send notifications to.
        smtp_server_details (Dict): Details of the SMTP server in order to send email notification.
        data_file_path (str): Path including the file name for json data file.
        summarize_it (bool): Whether the summarizing function leveragin GenAI must be called or not.
    """
    
    # Retrieve Youtube channel's videos
    try:
        channel_videos = pull_new_videos_from_channel(
            youtube_service = youtube_service,
            channel_id = channel_id,
            channel_name = channel_name,
            data_file_path = data_file_path)
    
    except Exception as e:
        print(f"🚨 An error occurred while processing an article!")
        print(f"Error details: {e}")
        # Optional: print the HTML snippet that caused the error to inspect it
        # print(f"Problematic HTML: {insurance_times_uk_article_div}") 
        return # Skip to the next article
    
    if channel_videos:
        print(f"""
        {datetime.now().strftime("%Y-%m-%d")} - {len(channel_videos)} new videos for Youtube channel '{channel_name}':""") # For Debug Only
        print(f"""{''.join(f"""
            => Video ID: {curr_video[config['key.json.id']]}
               Title: {curr_video[config['key.json.title']]}""" for curr_video in channel_videos)}""") # For Debug Only
    else:
        print(f"Channel '{channel_name}' has no video or doesn't exist. Please verify its id ('{channel_id}')")
        return
    
    # Create email subject
    email_subject = f"{
        get_value2_on_key2_from_value1_on_key1_in_channels_list(
            key1 = "name",
            value1 = channel_name,
            key2 = "monitoring.category",
            channels = config["youtube.api.list.channels"])} {channel_name}"
    # Initialize email details
    email_details = {
        config["key.json.email.detail.recipients"]: recipients,
        config["key.json.email.detail.subject"]: email_subject
    }
    
    # Ignore key 'content' from the HTML to generate
    keys_to_ignore = [config["key.json.id"],
                      config["key.json.transcript"],
                      config["key.json.link"]]
    
    process_list_of_items(source_name = f"{config["key.json.youtube.source.name"]} - {channel_name}",
                          source_format = config["key.json.source.format.youtube.video"],
                          data_file_path = data_file_path,
                          known_items_json_key = config["key.json.id"],
                          new_items = channel_videos,
                          smtp_server_details = smtp_server_details,
                          email_details = email_details,
                          keys_to_ignore = keys_to_ignore,
                          summarize_it = summarize_it)

def extract_video_details_from_youtube_channels() -> None:
    """
    Fetches daily content from various youtube channels and sends notifications.
    
    This function performs the following tasks:
    
    1. Extracts Youtube videos for each channel in a configured list and sends notifications.
    """
    # Extract Youtube videos for a list of channels
    list_youtube_channels = config["youtube.api.list.channels"]
    
    # Retrieve Youtube authenticated service
    youtube_service = get_youtube_client()
    # iter_channel = 1 # For Debug Only
    for channel in list_youtube_channels:
        # Skip this channel for debugging (uncomment for testing specific channel)
        # if channel["name"] != "your_channel_name":
        #     continue
        # break # For Debug Only
        print(f"Looking at Youtube channel {channel["name"]}")
        process_videos_from_channel(
            youtube_service = youtube_service,
            channel_id = channel["id"],
            channel_name = channel["name"],
            recipients = channel["recipients"],
            smtp_server_details = channel["smtp.server.details"],
            # sender = channel["sender"],
            # sender_password = channel["sender.password"],
            # smtp_server = channel["smtp.server"],
            # smtp_port = channel["smtp.port"],
            # Data file path for storing video information
            data_file_path = os.path.join(config["json.key.data.dir"],
                                          f"EVER_{channel["name"].replace(' ', '_')}_videos.json"),
            summarize_it = channel["summarize.it"]
        )
        # if iter_channel > 2: # For Debug Only
        #     break # For Debug Only
        # iter_channel += 1 # For Debug Only
