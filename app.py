import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, redirect, request, session, url_for

app = Flask(__name__)

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
REDIRECT_URI = os.environ.get("REDIRECT_URI")
app.secret_key = os.environ.get("SECRET_KEY")

SCOPE = "user-top-read"

def get_spotify_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    auth_url = get_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = get_spotify_oauth().get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    token_info = session.get("token_info")
    if not token_info:
        return redirect(url_for("index"))

    sp = spotipy.Spotify(auth=token_info["access_token"])

    # Fetch top artists
    top_artists = sp.current_user_top_artists(limit=10, time_range="medium_term")
    artists = [{"name": a.get("name", "Unknown"), "image": a["images"][0]["url"] if a.get("images") else None} for a in top_artists["items"]]

    # Fetch top tracks
    top_tracks = sp.current_user_top_tracks(limit=10, time_range="medium_term")
    tracks = [{"name": t.get("name", "Unknown"), "artist": t["artists"][0].get("name", "Unknown"), "image": t["album"]["images"][0]["url"] if t["album"].get("images") else None} for t in top_tracks["items"]]

    # Fetch user profile
    user = sp.current_user()
    username = user.get("display_name", "Listener")

    return render_template("dashboard.html", artists=artists, tracks=tracks, username=username)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)