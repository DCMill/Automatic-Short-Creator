import os
import google.auth
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# YouTube API v3 scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def authenticate_youtube_api():
    """Authenticates and returns the YouTube API service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = google.auth.load_credentials_from_file('token.json')[0]
    
    # If there are no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the YouTube API service object
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def video_exists(youtube, video_title):
    """Checks if a video with the given title exists."""
    # Retrieve the channel's uploads playlist
    request = youtube.channels().list(part="contentDetails", mine=True)
    response = request.execute()
    
    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # Retrieve videos from the uploads playlist
    next_page_token = None
    while True:
        playlist_request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        playlist_response = playlist_request.execute()

        # Check if any video matches the title
        for item in playlist_response["items"]:
            if item["snippet"]["title"].lower() == video_title.lower():
                print(f"Video found: {item['snippet']['title']}")
                return True

        # Check if there are more pages of results
        next_page_token = playlist_response.get("nextPageToken")
        if not next_page_token:
            break

    print("Video not found")
    return False
