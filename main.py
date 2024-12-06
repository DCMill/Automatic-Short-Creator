import random
import praw
import ffmpeg
from vosk import Model, KaldiRecognizer
import wave
import json
import os
import subprocess
from tiktok_voice import tts, Voice
from test_srt import *
from upload import *
import datetime

REDDIT_CLIENT_ID = "<YOUR_REDDIT_CLIENT_ID_HERE>"
REDDIT_CLIENT_SECRET = "<YOUR_REDDIT_CLIENT_SECRET>"
REDDIT_USER_AGENT = "linux:random.reddit.bot:v1.0 (by /u/Stupid123234)"
TIK_TOK_SESSION_ID = "<YOUR_TIKTOK_SESSIONID>"
SUBSCRIPT_MODEL_PATH = "./vosk-model-small-en-us-0.15"
SUBSCRIPT_FILE_PATH = "subscript.srt"
MINECRAFT_PARKOUR_PATH = "minecraft_parkour.mp4"

subreddits = [
    "nosleep", "pettyrevenge",
    "confession", "AITA", "creepyencounters", 
    "relationship_advice", "UnresolvedMysteries", "AmItheAsshole", "AITA", "AITA", "AITA"
]
reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )
subreddit = reddit.subreddit(random.choice(subreddits))
posts = list(subreddit.hot(limit=1000))
def format_timestamp(seconds):
    """Convert seconds to SRT timestamp format (HH:MM:SS,MS)."""
    td = datetime.timedelta(seconds=seconds)
    return str(td)[:-3].replace('.', ',')

def get_reddit_post():
    random_post = random.choice(posts)
    print(subreddit.display_name)
    print(random_post.selftext)
    return random_post.title, random_post.selftext

def get_random_video(duration):
    probe = ffmpeg.probe(MINECRAFT_PARKOUR_PATH)
    video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    video_duration = float(video_info['duration'])

    max_start_time = video_duration - duration
    if max_start_time <= 0:
        raise ValueError("Clip duration is longer than the video length.")
    
    start_time = random.uniform(0, max_start_time)
    
    aspect_ratio = (9, 16)
    width = 720
    height = int(width * aspect_ratio[1] / aspect_ratio[0])

    (
        ffmpeg
        .input(MINECRAFT_PARKOUR_PATH, ss=start_time, t=duration)
        .output("output.mp4", vf='crop=ih*(9/16):ih,scale=1080:1920', loglevel="quiet")
        .run(overwrite_output=True)
    )

def get_audio(text_content):
    tts(text_content, Voice.MALE_DEADPOOL, "audio.mp3")
    ffmpeg.input('audio.mp3').output('audio.wav', loglevel="quiet").run(overwrite_output=True)

def apply_audio(title, video, audio):
    transcribe_to_srt(audio, SUBSCRIPT_FILE_PATH)

    if not os.path.exists(SUBSCRIPT_FILE_PATH):
        print(f"Error: SRT file '{SUBSCRIPT_FILE_PATH}' not found.")
        return
    
    inputs = {
        'video': ffmpeg.input(video).filter("subtitles", SUBSCRIPT_FILE_PATH),
        'audio': ffmpeg.input(audio),
    }

    ffmpeg.concat(inputs['video'], inputs['audio'], v=1, a=1).output(
        "videos/" + f'{"".join(title[:10].split(" "))}.mp4', loglevel="quiet"
    ).run(overwrite_output=True)

def get_audio_duration(audio_file):
    probe = ffmpeg.probe(audio_file)
    duration = float(probe['format']['duration'])
    return duration

def make_video():
    audio_duration = 61
    while audio_duration >= 60:
        title, text = get_reddit_post()

        success = False
        while not success:
            try:
                get_audio(text)
                success = True
            except ValueError as e:
                print(f"Error encountered: {e}. Trying a new Reddit post...")
                title, text = get_reddit_post()

        audio_duration = get_audio_duration('audio.mp3')

    get_random_video(audio_duration)
    apply_audio(title, "output.mp4", "audio.wav")
    os.remove("output.mp4")
    os.remove("audio.wav")
    os.remove("audio.mp3")
    video_status = upload_video(video_title=title, description=text, tags="reddit", video_file="videos/" + f'{"".join(title[:10].split(" "))}.mp4')
    if video_status is False:
        make_video()
    print("video uploaded?")

videos = 6
for i in range(videos):
    make_video()
