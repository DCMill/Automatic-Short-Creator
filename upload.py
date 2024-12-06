import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
import datetime
from google.oauth2.credentials import Credentials
from video_exists import video_exists
# Define the scope and API service information
SCOPES = ['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.readonly',"https://www.googleapis.com/auth/youtube"]
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def authenticate():
    """Authenticate to the YouTube API using OAuth 2.0"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json', SCOPES)
        creds = flow.run_local_server(port=8080)
    print(True if creds else False) 
    # Save the credentials for future use
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    return creds

def upload_video(video_title, video_file, description="", tags=None, category_id="22", privacy_status="public"):
    """Uploads a video to YouTube"""
    
    # Authenticate and create the YouTube client
    credentials = authenticate()
    youtube = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    if video_exists(youtube,video_title):
        return False
    # Define the video metadata
    body = {
        'snippet': {
            'title': video_title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status
        }
    }

    # Upload the video file
    media = googleapiclient.http.MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype='video/*')

    # Make the request to the YouTube API
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = request.execute()
    print(f"Video uploaded. Video ID: {response['id']}")
    return True


