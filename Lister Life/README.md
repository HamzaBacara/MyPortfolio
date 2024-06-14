# Lister Life

Lister Life is a project that transfers Spotify playlists to YouTube. It authenticates with both Spotify and YouTube APIs to fetch playlist data from Spotify and create corresponding playlists on YouTube. Other platforms will be implemented in the future.

## Features

- Authenticate with Spotify and YouTube
- Fetch playlists from Spotify
- Create playlists on YouTube
- Transfer tracks from Spotify to YouTube

## Prerequisites

- Python 3.x
- Flask
- Requests
- google-auth
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- cachetools
- A Spotify Developer account
- A YouTube Developer account

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/Lister-Life.git
    cd Lister-Life
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up your environment variables for Spotify credentials:

    ```bash
    export SPOTIFY_CLIENT_ID='your_spotify_client_id'
    export SPOTIFY_CLIENT_SECRET='your_spotify_client_secret'
    ```

5. Ensure you have the `client_secrets.json` file for YouTube API authentication in the root directory.

## Usage

1. Run the Flask server:

    ```bash
    python app.py
    ```

2. Use the provided endpoints to authenticate and transfer playlists.

## Endpoints

- **GET /**: Check if the server is running.
- **POST /transfer**: Transfer a Spotify playlist to YouTube.
- **GET /get_youtube_playlists**: Get user's YouTube playlists.
- **GET /get_spotify_playlists**: Get user's Spotify playlists.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
