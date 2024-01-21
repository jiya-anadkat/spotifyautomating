# import necessary modules
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect
from datetime import datetime
import os

os.environ['SPOTIPY_CLIENT_ID'] = 'MY CLIENT ID'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'MY CLIENT SECRET'
os.environ['SPOTIPY_REDIRECT_URI'] = 'MY REDIRECT URI'

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

app.secret_key = 'MY SECRET KEY'

TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('save_discover_weekly',_external=True))

@app.route('/saveDiscoverWeekly')
def save_discover_weekly():
    try: 
        token_info = get_token()
    except:
        print('User not logged in')
        return redirect("/")

    sp = spotipy.Spotify(auth=token_info['access_token'])

    current_playlists =  sp.current_user_playlists()['items']
    # print("Current Playlists:", current_playlists)
    discover_weekly_playlist_id = None
    saved_weekly_playlist_id = None

    for playlist in current_playlists:
        #print(playlist['name'])
        if(playlist['name'] == 'Discover Weekly'):
            discover_weekly_playlist_id = playlist['id']
        if(playlist['name'] == 'Saved Weekly'):
            saved_weekly_playlist_id = playlist['id']
    
    if not discover_weekly_playlist_id:
        return 'Discover Weekly not found.'
    
    discover_weekly_playlist = sp.playlist_items(discover_weekly_playlist_id)
    song_uris = []
    for song in discover_weekly_playlist['items']:
        #print(song['track']['name'])
        song_uri= song['track']['uri']
        song_uris.append(song_uri)
    
    # print(sp.user('lpl4p0073h8dfratp36ewouf8'))
    sp.user_playlist_add_tracks('lpl4p0073h8dfratp36ewouf8', saved_weekly_playlist_id, song_uris, None)
    

    return ('Discover Weekly songs added successfully')

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        return redirect(url_for('login', _external=False))

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if is_expired:
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = 'MY CLIENT ID',
        client_secret = 'MY CLIENT SECRET',
        redirect_uri = url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

app.run(debug=True)
