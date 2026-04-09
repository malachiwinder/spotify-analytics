import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template_string

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

# --- Fetch Data ---
top_artists = sp.current_user_top_artists(limit=10, time_range="medium_term")
artists = [{"name": a.get("name", "Unknown"), "image": a["images"][0]["url"] if a.get("images") else None} for a in top_artists["items"]]

top_tracks = sp.current_user_top_tracks(limit=10, time_range="medium_term")
tracks = [{"name": t.get("name", "Unknown"), "artist": t["artists"][0].get("name", "Unknown"), "image": t["album"]["images"][0]["url"] if t["album"].get("images") else None} for t in top_tracks["items"]]

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>My Spotify Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --green: #1DB954;
            --green-dim: #158a3e;
            --black: #080808;
            --surface: #111111;
            --surface2: #1a1a1a;
            --border: #2a2a2a;
            --text: #f0f0f0;
            --muted: #888;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            background: var(--black);
            color: var(--text);
            font-family: 'DM Sans', sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Ambient background blobs */
        body::before {
            content: '';
            position: fixed;
            top: -200px;
            left: -200px;
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(29,185,84,0.08) 0%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        }
        body::after {
            content: '';
            position: fixed;
            bottom: -200px;
            right: -200px;
            width: 500px;
            height: 500px;
            background: radial-gradient(circle, rgba(29,185,84,0.05) 0%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 60px 40px;
            position: relative;
            z-index: 1;
        }

        /* Header */
        header {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            margin-bottom: 64px;
            padding-bottom: 32px;
            border-bottom: 1px solid var(--border);
        }

        .logo-area {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .eyebrow {
            font-size: 0.7em;
            letter-spacing: 0.25em;
            text-transform: uppercase;
            color: var(--green);
            font-weight: 500;
        }

        h1 {
            font-family: 'Bebas Neue', sans-serif;
            font-size: clamp(3em, 6vw, 5.5em);
            line-height: 0.9;
            letter-spacing: 0.02em;
            color: var(--text);
        }

        h1 span {
            color: var(--green);
        }

        .period-badge {
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 8px 18px;
            font-size: 0.78em;
            color: var(--muted);
            letter-spacing: 0.05em;
            align-self: flex-end;
        }

        /* Section */
        .section {
            margin-bottom: 72px;
        }

        .section-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 28px;
        }

        .section-num {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3.5em;
            color: var(--border);
            line-height: 1;
            letter-spacing: 0.02em;
        }

        h2 {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.8em;
            letter-spacing: 0.08em;
            color: var(--text);
        }

        .section-line {
            flex: 1;
            height: 1px;
            background: var(--border);
        }

        /* Artist Grid */
        .artists-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
        }

        .artist-card {
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            aspect-ratio: 1;
            cursor: pointer;
            background: var(--surface2);
        }

        .artist-card:first-child {
            grid-column: span 2;
            grid-row: span 2;
            border-radius: 16px;
        }

        .artist-card img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.5s ease;
        }

        .artist-card:hover img {
            transform: scale(1.06);
        }

        .artist-card .overlay {
            position: absolute;
            inset: 0;
            background: linear-gradient(to top, rgba(0,0,0,0.85) 0%, transparent 55%);
            display: flex;
            flex-direction: column;
            justify-content: flex-end;
            padding: 14px;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .artist-card:first-child .overlay {
            opacity: 1;
            padding: 22px;
        }

        .artist-card:hover .overlay {
            opacity: 1;
        }

        .artist-rank {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 0.85em;
            color: var(--green);
            letter-spacing: 0.12em;
            margin-bottom: 2px;
        }

        .artist-card:first-child .artist-rank {
            font-size: 1.1em;
        }

        .artist-name {
            font-size: 0.88em;
            font-weight: 600;
            line-height: 1.2;
            color: #fff;
        }

        .artist-card:first-child .artist-name {
            font-size: 1.3em;
        }

        .no-img {
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5em;
            background: var(--surface2);
        }

        /* Tracks List */
        .tracks-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .track-row {
            display: grid;
            grid-template-columns: 40px 56px 1fr auto;
            align-items: center;
            gap: 16px;
            padding: 10px 16px 10px 12px;
            border-radius: 10px;
            background: var(--surface);
            border: 1px solid transparent;
            transition: all 0.2s ease;
            animation: slideIn 0.4s ease both;
        }

        .track-row:hover {
            background: var(--surface2);
            border-color: var(--border);
            transform: translateX(4px);
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .track-num {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.3em;
            color: var(--border);
            text-align: center;
            letter-spacing: 0.05em;
            transition: color 0.2s;
        }

        .track-row:hover .track-num {
            color: var(--green);
        }

        .track-art {
            width: 56px;
            height: 56px;
            border-radius: 6px;
            object-fit: cover;
            background: var(--surface2);
        }

        .track-art-placeholder {
            width: 56px;
            height: 56px;
            border-radius: 6px;
            background: var(--surface2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4em;
        }

        .track-info {
            min-width: 0;
        }

        .track-name {
            font-size: 0.95em;
            font-weight: 600;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 3px;
        }

        .track-artist {
            font-size: 0.8em;
            color: var(--muted);
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .track-pill {
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 0.7em;
            color: var(--muted);
            letter-spacing: 0.08em;
            white-space: nowrap;
        }

        /* Footer */
        footer {
            margin-top: 80px;
            padding-top: 32px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        footer p {
            font-size: 0.75em;
            color: var(--muted);
            letter-spacing: 0.05em;
        }

        footer .dot {
            width: 6px;
            height: 6px;
            background: var(--green);
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }

        /* Staggered animation delays for tracks */
        .track-row:nth-child(1) { animation-delay: 0.05s; }
        .track-row:nth-child(2) { animation-delay: 0.1s; }
        .track-row:nth-child(3) { animation-delay: 0.15s; }
        .track-row:nth-child(4) { animation-delay: 0.2s; }
        .track-row:nth-child(5) { animation-delay: 0.25s; }
        .track-row:nth-child(6) { animation-delay: 0.3s; }
        .track-row:nth-child(7) { animation-delay: 0.35s; }
        .track-row:nth-child(8) { animation-delay: 0.4s; }
        .track-row:nth-child(9) { animation-delay: 0.45s; }
        .track-row:nth-child(10) { animation-delay: 0.5s; }
    </style>
</head>
<body>
<div class="container">

    <header>
        <div class="logo-area">
            <span class="eyebrow">Listening Stats</span>
            <h1>MY <span>SPOTIFY</span><br>WRAPPED</h1>
        </div>
        <span class="period-badge">LAST 6 MONTHS</span>
    </header>

    <!-- TOP ARTISTS -->
    <div class="section">
        <div class="section-header">
            <span class="section-num">01</span>
            <h2>TOP ARTISTS</h2>
            <div class="section-line"></div>
        </div>

        <div class="artists-grid">
            {% for a in artists %}
            <div class="artist-card">
                {% if a.image %}
                <img src="{{ a.image }}" alt="{{ a.name }}">
                {% else %}
                <div class="no-img">🎤</div>
                {% endif %}
                <div class="overlay">
                    <div class="artist-rank">#{{ loop.index }} ARTIST</div>
                    <div class="artist-name">{{ a.name }}</div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- TOP TRACKS -->
    <div class="section">
        <div class="section-header">
            <span class="section-num">02</span>
            <h2>TOP TRACKS</h2>
            <div class="section-line"></div>
        </div>

        <div class="tracks-list">
            {% for t in tracks %}
            <div class="track-row">
                <span class="track-num">{{ loop.index }}</span>
                {% if t.image %}
                <img class="track-art" src="{{ t.image }}" alt="{{ t.name }}">
                {% else %}
                <div class="track-art-placeholder">🎵</div>
                {% endif %}
                <div class="track-info">
                    <div class="track-name">{{ t.name }}</div>
                    <div class="track-artist">{{ t.artist }}</div>
                </div>
                <span class="track-pill">TOP {{ loop.index * 10 }}%</span>
            </div>
            {% endfor %}
        </div>
    </div>

    <footer>
        <p><span class="dot"></span>Live data via Spotify Web API</p>
        <p>Built with Python & Flask</p>
    </footer>

</div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML, artists=artists, tracks=tracks)

if __name__ == "__main__":
    print("Dashboard running at http://127.0.0.1:5000")
    app.run(debug=True)