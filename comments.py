import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pytube import extract
from dotenv import load_dotenv

load_dotenv()

api_server_name = st.secrets["API_SERVICE_NAME"]
api_version = st.secrets['API_VERSION']
youtube_api_key = st.secrets['YOUTUBE_API_KEY']

def start_youtube_service():
    return build(api_server_name, api_version, developerKey=youtube_api_key)

def extract_video_id_from_link(url):
    return extract.video_id(url)

def get_comments_thread(youtube, video_id, next_page_token):
    results = youtube.commentThreads().list(
        part="snippet,replies",                     
        videoId=video_id,
        textFormat='plainText',
        maxResults=100,
    ).execute()
    return results

def load_comments_in_format(comments):
    all_comments_string = ""
    for thread in comments["items"]:
        comment_content = thread['snippet']['topLevelComment']['snippet']['textOriginal']
        all_comments_string += comment_content + "\n"
        if 'replies' in thread:
            for reply in thread['replies']['comments']:
                reply_text = reply['snippet']['textOriginal']
                all_comments_string += reply_text + "\n"
    return all_comments_string

def fetch_comments(url):
    youtube = start_youtube_service()
    video_id = extract_video_id_from_link(url)
    next_page_token = ''
    
    try:
        data = get_comments_thread(youtube, video_id, next_page_token)
        all_comments = load_comments_in_format(data)
        return all_comments
    except HttpError as e:
        error_message = str(e)
        if "commentsDisabled" in error_message:
            st.error("The video has disabled comments. Please try with another video.")
        else:
            st.error(f"An error occurred: {error_message}")
        return None