from flask import Flask, request, render_template, jsonify
from Lister import process_spotify_playlist, youtube_authenticate, get_user_youtube_playlists
from googleapiclient.discovery import build
from flask_cors import CORS
import requests
import logging
import os

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)
@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Flask server is running"})

@app.route('/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    spotify_url = data.get('spotify_url')
    playlist_choice = request.form.get('playlist_choice')
    new_playlist_title = data.get('new_playlist_title')

    try:
        playlist_id = extract_playlist_id(spotify_url)
        if not playlist_id:
            raise ValueError("Invalid Spotify URL")

        youtube_playlist_id = process_spotify_playlist(playlist_id, playlist_choice, new_playlist_title)
        if not youtube_playlist_id:
            raise ValueError("Error Code: {response.status_code}, Error Details: {response.text}")

        playlist_url = f"https://www.youtube.com/playlist?list={youtube_playlist_id}"
        return render_template('index.html', playlist_url=playlist_url, user_playlists=[])

    except Exception as e:
        return f"Transfer failed: {str(e)}"

    return jsonify({"success": True, "playlist_url": playlist_url})
    

@app.route('/get_youtube_playlists', methods=['GET'])
def get_youtube_playlists():
    try:
        youtube_creds = youtube_authenticate()
        if not youtube_creds:
            raise Exception('Failed to authenticate with YouTube')

        youtube_service = build('youtube', 'v3', credentials=youtube_creds)
        user_playlists = get_user_youtube_playlists(youtube_service)
        if user_playlists is None:
            raise Exception('Failed to fetch playlists')

        return jsonify({'playlists': user_playlists})
    except Exception as e:
        logging.error("Error in get_youtube_playlists: {}".format(e))
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_spotify_playlists', methods=['GET'])
def get_spotify_playlists():
    access_token = get_spotify_token()
    if not access_token:
        return jsonify({'error': 'Failed to authenticate with Spotify'}), 401

    playlists = fetch_spotify_user_playlists(access_token)
    if playlists is None:
        return jsonify({'error': 'Failed to fetch playlists'}), 500

    return jsonify({'playlists': playlists})



def get_spotify_token():
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

    # Log the client_id and client_secret for debugging (remove this in production)
    logging.info(f"Client ID: {client_id}, Client Secret: {client_secret}")

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(
        auth_url, 
        auth=(client_id, client_secret), 
        data={'grant_type': 'client_credentials'}
    )

    # Log the response status code and text
    logging.info(f"Auth Response Status Code: {auth_response.status_code}")
    logging.info(f"Auth Response Body: {auth_response.text}")

    if auth_response.status_code != 200:
        logging.error("Failed to get the access token from Spotify.")
        return None

    auth_response_data = auth_response.json()
    access_token = auth_response_data.get('access_token')

    return access_token

def fetch_spotify_user_playlists(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    endpoint = 'https://api.spotify.com/v1/me/playlists'  # URL to fetch user's playlists
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        playlists = response.json().get('items', [])
        return playlists
    else:
        return None
    
def extract_playlist_id(spotify_url):
    try:
        playlist_id = spotify_url.split('/playlist/')[1].split('?')[0]
        return playlist_id
    except IndexError:
        return None

if __name__ == '__main__':
    app.run(debug=True)
 