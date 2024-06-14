import requests
from requests.auth import HTTPBasicAuth
import os
import json
from youtube_auth import youtube_authenticate
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from cache_utils import cache_response, get_cached_response
import re
import logging
import cachetools.func
youtube_search_cache = {}  


client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

if not client_id or not client_secret:
    print("Spotify credentials not found")

def get_spotify_token():
    """
    Authenticate with Spotify and get an access token.
    """
    try:
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_response = requests.post(auth_url, auth=HTTPBasicAuth(client_id, client_secret), data={'grant_type': 'client_credentials'})
        if auth_response.status_code != 200:
            raise Exception(f"Spotify authentication failed: {auth_response.json()}")

        access_token = auth_response.json().get('access_token')
        return access_token
    except Exception as e:
        logging.error(f"Error in get_spotify_token: {str(e)}")
        return None

def get_spotify_playlist(playlist_id, access_token):
    base_url = 'https://api.spotify.com/v1/playlists/'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(base_url + playlist_id, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching playlist: {response.json()}")
        return None
    
    spotify_playlist = response.json()
    return spotify_playlist

def process_spotify_playlist(playlist_id, playlist_choice, new_playlist_title):
    try:
        youtube_creds = youtube_authenticate()
        youtube_service = build('youtube', 'v3', credentials=youtube_creds)
        
        if playlist_choice == 'new_playlist':
            youtube_playlist_id = create_youtube_playlist(youtube_service, new_playlist_title, "Playlist created from Spotify")
        else:
            youtube_playlist_id = playlist_choice

        token = get_spotify_token()
        if not token:
            raise Exception("Failed to get Spotify token")

        spotify_playlist = get_spotify_playlist(playlist_id, token)
        if spotify_playlist is None or 'tracks' not in spotify_playlist:
            raise Exception("Failed to fetch Spotify playlist or no tracks found")

        for item in spotify_playlist['tracks']['items']:
            track = item['track']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            spotify_track_info = {'name': track_name, 'artists': track['artists']}

            video_id = find_youtube_video_id(youtube_service, track_name, artist_name, spotify_track_info)
            if video_id:
                add_video_to_playlist(youtube_service, youtube_playlist_id, video_id)
            else:
                print(f"Failed to find a matching YouTube video for track: {track_name} by {artist_name}")

        return youtube_playlist_id

    except Exception as e:
        print(f"Error in process_spotify_playlist: {str(e)}")
        return None
    
def find_youtube_video_id(youtube_service, track_name, artist_name, spotify_track_info, additional_metadata=None):
    query = f"{track_name} {artist_name}"
    if additional_metadata:
        query += f" {additional_metadata}"

        cached_video_id = get_cached_response(query)
        if cached_video_id:
            
            return cached_video_id

    search_response = youtube_service.search().list(
        part='snippet',
        maxResults=5,  # Fetch more results to find the best match
        q=query,
        type='video'
    ).execute()

    best_match_video_id = None
    highest_relevance_score = 0  # Implement a scoring system for best match

    for item in search_response.get('items', []):
        video_title = item['snippet']['title']
        video_description = item['snippet']['description']
        video_id = item['id']['videoId']

      
        relevance_score = calculate_relevance_score(video_title, video_description, spotify_track_info, video_id, youtube_service)

        if relevance_score > highest_relevance_score:
            best_match_video_id = video_id
            highest_relevance_score = relevance_score

    cache_response(query, best_match_video_id)
    return best_match_video_id

def calculate_relevance_score(video_title, video_description, spotify_track_info, video_id, youtube_service):
    score = 0
    
    video_title_lower = video_title.lower()
    video_description_lower = video_description.lower()
    track_name_lower = spotify_track_info['name'].lower()
    artist_name_lower = spotify_track_info['artists'][0]['name'].lower()  # Assuming the first artist

    
    
    if track_name_lower in video_title_lower and artist_name_lower in video_title_lower:
        score += 50

   
    if 'album' in spotify_track_info and spotify_track_info['album']['name'].lower() in video_title_lower:
        score += 20

    spotify_duration = spotify_track_info.get('duration_ms', 0) / 1000  # Convert to seconds
    youtube_duration = get_youtube_video_duration(youtube_service, video_id)

    if youtube_duration is not None:
        if abs(spotify_duration - youtube_duration) < 30:  # 30 seconds tolerance
            score += 20


    
    non_original_keywords = ['cover', 'live', 'remix', 'karaoke']
    for keyword in non_original_keywords:
        if keyword in video_title_lower or keyword in video_description_lower:
            score -= 20

    return score

def get_youtube_video_duration(youtube_service, video_id):
    
    """
    Fetches and returns the duration of a YouTube video in seconds.

    Args:
        youtube_service: Authenticated YouTube API service instance.
        video_id (str): ID of the YouTube video.

    Returns:
        int: Duration of the video in seconds, or None if unable to fetch.
    """
    try:
        
        if video_id in duration_cache:
            print(f"Cache hit for video ID {video_id}")
            return duration_cache[video_id]

       
        response = youtube_service.videos().list(
            part="contentDetails",
            id=video_id
        ).execute()
        if 'items' not in response or not response['items']:
            print(f"No content details found for video ID {video_id}")
            return None

        
        duration_iso8601 = response['items'][0]['contentDetails']['duration']

        
        duration_seconds = iso8601_duration_to_seconds(duration_iso8601)

        
        duration_cache[video_id] = duration_seconds

        return duration_seconds

    except Exception as e:
        print(f"An error occurred while fetching duration for video ID {video_id}: {e}")
        return None

def iso8601_duration_to_seconds(duration):
    """
    Converts ISO 8601 duration format to seconds.

    Args:
        duration (str): ISO 8601 duration string.

    Returns:
        int: Duration in seconds.
    """
    match = re.match('PT(\d+H)?(\d+M)?(\d+S)?', duration)
    hours = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    seconds = int(match.group(3)[:-1]) if match.group(3) else 0
    return hours * 3600 + minutes * 60 + seconds

duration_cache = cachetools.func.ttl_cache(maxsize=100, ttl=3600)
def create_youtube_playlist(youtube_service, title, description):
    """
    Create a new YouTube playlist.

    Args:
        youtube_service: Authenticated YouTube API service instance.
        title (str): Title of the playlist.
        description (str): Description of the playlist.

    Returns:
        str: The ID of the created playlist.
    """
    try:
        request = youtube_service.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description
                },
                "status": {
                    "privacyStatus": "private" 
                }
            }
        )
        response = request.execute()
        return response["id"]
    except HttpError as error:
        print(f"An HTTP error occurred: {error.resp.status} {error.content}")
        return None

def add_tracks_to_youtube_playlist(youtube_service, youtube_playlist_id, spotify_playlist):
    for item in spotify_playlist['tracks']['items']:
        track = item['track']
        track_name = track['name']
        artist_name = track['artists'][0]['name']

        
        search_response = youtube_service.search().list(
            part='snippet',
            maxResults=5,
            q=f"{track_name} {artist_name}",
            type='video'
        ).execute()

        if search_response['items']:
            video_id = search_response['items'][0]['id']['videoId']
            add_video_to_playlist(youtube_service, youtube_playlist_id, video_id)

def add_video_to_playlist(youtube_service, playlist_id, video_id):
    add_video_request = youtube_service.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    )
    add_video_request.execute()

def get_user_youtube_playlists(youtube_service):
    playlists = []
    request = youtube_service.playlists().list(
        part="snippet",
        mine=True,
        maxResults=10  # Adjust as needed
    )
    response = request.execute()

    for item in response['items']:
        playlists.append({
            'id': item['id'],
            'title': item['snippet']['title']
        })
    
    return playlists
