import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Your Spotify credentials
CLIENT_ID = "863bcafa651a46ae9f529e226350fd69"
CLIENT_SECRET = "5dc548afbdcd4c289618af1806fb18d3"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

# Connect to Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope="user-top-read"
))

# --- Fetch Top Artists ---
top_artists = sp.current_user_top_artists(limit=10, time_range="medium_term")
artists_data = []
for artist in top_artists["items"]:
    artists_data.append({
        "name": artist.get("name", "Unknown"),
        "genres": ", ".join(artist.get("genres", ["Unknown"])),
        "popularity": artist.get("popularity", 0)
    })
artists_df = pd.DataFrame(artists_data)

# --- Fetch Top Tracks ---
top_tracks = sp.current_user_top_tracks(limit=10, time_range="medium_term")
tracks_data = []
for track in top_tracks["items"]:
    tracks_data.append({
        "name": track.get("name", "Unknown"),
        "artist": track["artists"][0].get("name", "Unknown"),
        "popularity": track.get("popularity", 0)
    })
tracks_df = pd.DataFrame(tracks_data)

# Preview the data
print("=== Top Artists ===")
print(artists_df)
print("\n=== Top Tracks ===")
print(tracks_df)